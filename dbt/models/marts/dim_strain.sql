-- dim_strain: one row per strain any source names, with what each layer says
-- about it. The strain table every other table points to.
--
-- Taxonomy comes from the Layer 1 archive's strain list, the one the study
-- being reproduced used. Where Vogel et al. 2021 (Supplementary Table 12)
-- names a different family or genus, that's kept beside it (family_vogel2021,
-- genus_vogel2021); seeds/known_source_differences.csv lists every such case.
-- Columns from a layer stay NULL for a strain that layer doesn't cover.

with strains as (
    select distinct strain_id from {{ ref('int_strain_mentions') }}
),

library as (
    select distinct strain_id from {{ ref('stg_screen__design') }}
),

membership as (
    select
        design.strain_id,
        count(*) filter (where design.is_member and communities.kind = 'community') as communities_designed,
        count(*) filter (where design.is_member and communities.role = 'training') as training_communities,
        count(*) filter (where design.is_member and communities.role = 'test')     as test_communities
    from {{ ref('stg_screen__design') }} as design
    join {{ ref('int_communities') }} as communities
        on communities.community_id = design.community_id
    group by design.strain_id
),

collection as (select * from {{ ref('stg_collection__strains') }}),
vogel as (select * from {{ ref('stg_vogel__strains') }}),
genomes as (select * from {{ ref('int_strain_genomes') }}),
clusters as (select * from {{ ref('int_strain_gene_clusters') }}),
interactions as (select * from {{ ref('int_strain_interaction_counts') }})

select
    strains.strain_id,
    library.strain_id is not null                                as in_screen_library,
    coalesce(collection.collection_group, vogel.collection)      as collection_group,
    coalesce(collection.phylum, vogel.phylum)                    as phylum,
    coalesce(collection.taxonomic_class, vogel.taxonomic_class)  as taxonomic_class,
    coalesce(collection.family, vogel.family)                    as family,
    coalesce(collection.genus, vogel.genus)                      as genus,
    vogel.family                                                 as family_vogel2021,
    vogel.genus                                                  as genus_vogel2021,

    -- Layer 2: the genome
    genomes.strain_id is not null                                as has_genome,
    genomes.assembly_accession,
    genomes.contigs,
    genomes.genome_length_bp,
    genomes.gc_percent,

    -- Layer 3: gene clusters
    clusters.clusters_reported,
    clusters.clusters_listed,
    clusters.potentially_inhibitory_clusters,

    -- Layer 4: the interaction screen (zero means none seen; NULL, not screened)
    interactions.strain_id is not null                           as in_interaction_screen,
    interactions.inhibits,
    interactions.inhibits_strongly,
    interactions.inhibited_by,
    interactions.inhibited_strongly_by,

    -- Layer 1: how often the design used the strain
    membership.communities_designed,
    membership.training_communities,
    membership.test_communities
from strains
left join library on library.strain_id = strains.strain_id
left join membership on membership.strain_id = strains.strain_id
left join collection on collection.strain_id = strains.strain_id
left join vogel on vogel.strain_id = strains.strain_id
left join genomes on genomes.strain_id = strains.strain_id
left join clusters on clusters.strain_id = strains.strain_id
left join interactions on interactions.strain_id = strains.strain_id
