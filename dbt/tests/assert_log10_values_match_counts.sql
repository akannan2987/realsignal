-- Each log10 column must be the log10 of the count beside it. Rounding in the
-- files allows a difference of at most a billionth. Returns any row where it's
-- larger, or where a count is zero or less (its log10 wouldn't exist).

with pairs as (
    select plant_id, 'pathogen' as measured, cfu_per_g, log10_cfu_per_g
    from {{ ref('stg_screen__pathogen_load') }}
    union all
    select plant_id, 'commensal', cfu_per_g, log10_cfu_per_g
    from {{ ref('stg_screen__commensal_load') }}
    union all
    select plant_id, 'strain ' || strain_id, cfu_per_g, log10_cfu_per_g
    from {{ ref('stg_screen__strain_colonisation') }}
)

select *
from pairs
where cfu_per_g <= 0
   or abs(log10(cfu_per_g) - log10_cfu_per_g) > 1e-9
