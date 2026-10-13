-- stg_helfrich__bgc_counts: gene clusters per strain and class
-- (Helfrich et al. 2018, Supplementary Table 9), turned from wide to long.
--
-- Every column except Strain, Genus and Total is a class of gene cluster, so
-- UNPIVOT takes them all without naming them. The Total row, the heading
-- repeated under it and the average below fail looks_like_strain().

with strains as (
    select * exclude (_row, "Genus", "Total")
    from {{ source('raw', 'helfrich_bgc_counts') }}
    where {{ looks_like_strain('"Strain"') }}
),

long as (
    unpivot strains
    on columns(* exclude ("Strain"))
    into name bgc_class value cell
)

select
    {{ strain_id('"Strain"') }}          as strain_id,
    bgc_class,
    cast(cell as integer)                as cluster_count
from long
