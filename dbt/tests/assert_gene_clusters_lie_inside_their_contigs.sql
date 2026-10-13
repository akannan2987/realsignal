-- Layer 3 against Layer 2. For every strain whose genome is part of the
-- project, each gene cluster in Table S11 must sit on a contig of that genome
-- (matched by its GenBank accession) and end before the contig does.
-- Returns every cluster that doesn't.

select
    clusters.gene_cluster_id,
    clusters.contig_accession,
    clusters.start_position,
    clusters.end_position,
    clusters.contig_length_bp
from {{ ref('fct_gene_cluster') }} as clusters
join {{ ref('dim_strain') }} as strains on strains.strain_id = clusters.strain_id
where strains.has_genome
  and (clusters.contig_length_bp is null
       or clusters.start_position > clusters.end_position
       or clusters.end_position > clusters.contig_length_bp)
