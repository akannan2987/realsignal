-- stg_screen__plant_notes: the 2020 notes on every plant (20201130_Comments.txt).
-- The file has no plant ID column, so it's built the way the plant file
-- builds it: box, underscore, position ("25_2").

select
    cast("Box" as integer) || '_' || cast("Plant" as integer)   as plant_id,
    upper(trim("IncludedAnalysis"))                            as inclusion_mark_2020,
    nullif(trim("ExclusionJustification"), '')                 as set_aside_reason,
    nullif(concat_ws('; ', "Comment_General", "Comment_Infection", "Comment_Weight",
                     "Comment_Harvest", "Comment_CommensalCount"), '') as notes,
    _row                                                       as source_row
from {{ source('raw', 'screen_plant_notes') }}
