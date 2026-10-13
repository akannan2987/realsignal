-- stg_screen__commensal_load: all the community's bacteria together, per gram
-- of fresh leaf, on every plant that received a community.

select
    trim("Uid")                              as plant_id,
    cast("CFUgFW" as double)                 as cfu_per_g,
    cast("LogCFUgFW" as double)              as log10_cfu_per_g,
    _row                                     as source_row
from {{ source('raw', 'screen_commensal_load') }}
