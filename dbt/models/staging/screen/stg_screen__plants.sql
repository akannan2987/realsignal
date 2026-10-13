-- stg_screen__plants: one row per plant (2023-01-16..._CommentsFile.txt).
-- The file calls a round an "Experiment" (Exp1, Exp2, Exp3) and a plant's
-- position in its box "Plant"; here they're round_id and position.

select
    trim("Uid")                           as plant_id,
    cast("Box" as integer)                as box_id,
    cast("Plant" as integer)              as position,
    trim("Mix")                           as community_id,
    trim("Infection")                     as infection_code,
    trim("FigureLabel")                   as figure_label,
    upper(trim("IncludedAnalysis"))       as inclusion_mark,     -- TRUE, FALSE or TBD
    trim("Experiment")                    as round_id,
    _row                                  as source_row
from {{ source('raw', 'screen_plants') }}
