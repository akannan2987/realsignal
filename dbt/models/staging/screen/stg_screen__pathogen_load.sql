-- stg_screen__pathogen_load: the pathogen on every infected plant.
-- CFU (colony-forming units) per gram of fresh leaf, as counted, and the same
-- number on a log10 scale. The third column is the authors' normalised value,
-- kept as published; how it was normalised is a question for Phase 6.

select
    trim("Uid")                              as plant_id,
    cast("CFUgFW" as double)                 as cfu_per_g,
    cast("LogCFUgFW" as double)              as log10_cfu_per_g,
    cast("NormLogCFUgFW" as double)          as log10_cfu_per_g_normalised,
    _row                                     as source_row
from {{ source('raw', 'screen_pathogen_load') }}
