-- stg_helfrich__bgc_totals: the Total column of Supplementary Table 9, the
-- number of gene clusters the table reports for each strain.

select
    {{ strain_id('"Strain"') }}          as strain_id,
    trim("Genus")                        as genus,
    cast("Total" as integer)             as reported_total,
    _row                                 as source_row
from {{ source('raw', 'helfrich_bgc_counts') }}
where {{ looks_like_strain('"Strain"') }}
