-- stg_helfrich__gene_clusters: every predicted gene cluster
-- (Helfrich et al. 2018, Supplementary Table 11), one per row.
--
-- A gene cluster (BGC) is a group of neighbouring genes that together make one
-- compound. Accession is the contig it sits on, as GenBank writes it
-- (LMJX01000002.1); Start and End are positions on that contig.
-- Potentially_inhibitory is "put_inhib", sometimes followed by a compound's
-- name in brackets.

select
    {{ strain_id('"Strain"') }}                                       as strain_id,
    cast("Cluster" as integer)                                        as cluster_number,
    trim("Accession")                                                 as contig_accession,
    lower(trim("AntiSMASH BGC_type"))                                 as bgc_type,
    coalesce(starts_with(trim("Potentially_inhibitory"), 'put_inhib'), false) as potentially_inhibitory,
    nullif(regexp_extract("Potentially_inhibitory", '\((.*)\)', 1), '') as named_compound,
    cast("Start" as bigint)                                           as start_position,
    cast("End" as bigint)                                             as end_position,
    len(string_split("Genes", ';'))                                   as gene_count,
    _row                                                              as source_row
from {{ source('raw', 'helfrich_gene_clusters') }}
where {{ looks_like_strain('"Strain"') }}
