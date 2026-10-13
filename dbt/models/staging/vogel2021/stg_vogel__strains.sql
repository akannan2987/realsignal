-- stg_vogel__strains: the strain list of Vogel et al. 2021, Supplementary
-- Table 12. It names each strain twice, as Leaf73 and as the bare number 73;
-- both go through strain_id(), and a test checks they agree.
--
-- The footnote says a genus ends in * when it comes from Bai et al. 2015
-- instead of NCBI's taxonomy; the * is removed and kept as a flag.
-- The table also lists the positive control used in that paper, Fr1, which
-- isn't part of the At-LSPHERE collection (collection says so).

select
    {{ strain_id('"Strain"') }}                          as strain_id,
    {{ strain_id('"Strain_ID"') }}                       as strain_id_from_number,
    trim("Phylum")                                       as phylum,
    trim("Class")                                        as taxonomic_class,
    trim("Order")                                        as taxonomic_order,
    trim("Family")                                       as family,
    rtrim(trim("Genus1"), '*')                           as genus,
    ends_with(trim("Genus1"), '*')                       as genus_from_bai2015,
    nullif(trim("RefSeq_Assembly_Accession"), '')        as assembly_accession,
    trim("Comment")                                      as collection,
    _row                                                 as source_row
from {{ source('raw', 'vogel_strains') }}
where "Strain_ID" is not null
