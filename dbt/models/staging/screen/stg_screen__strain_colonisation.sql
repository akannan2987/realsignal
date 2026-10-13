-- stg_screen__strain_colonisation: each community member, per gram of fresh leaf.
-- Where two strains in a community couldn't be told apart, the file gives
-- both the same count and marks them AmbiguousSingleStrains = TRUE.

select
    trim("Uid")                                          as plant_id,
    {{ strain_id('"Strain_ID"') }}                       as strain_id,
    upper(trim("AmbiguousSingleStrains")) = 'TRUE'       as is_ambiguous,
    cast("CFUgFW" as double)                             as cfu_per_g,
    cast("LogCFUgFW" as double)                          as log10_cfu_per_g,
    _row                                                 as source_row
from {{ source('raw', 'screen_strain_colonisation') }}
