-- fct_gene_cluster: every predicted gene cluster, one per row, with the length
-- of the contig it sits on where the genome is part of Layer 2.

with contigs as (
    select strain_id, genbank_accession, length_bp
    from {{ ref('stg_genomes__contigs') }}
)

select
    clusters.strain_id || '_' || clusters.cluster_number   as gene_cluster_id,
    clusters.strain_id,
    clusters.cluster_number,
    clusters.contig_accession,
    clusters.bgc_type,
    clusters.potentially_inhibitory,
    clusters.named_compound,
    clusters.start_position,
    clusters.end_position,
    clusters.gene_count,
    contigs.length_bp                                       as contig_length_bp
from {{ ref('stg_helfrich__gene_clusters') }} as clusters
left join contigs
    on contigs.strain_id = clusters.strain_id
   and contigs.genbank_accession = clusters.contig_accession
