-- stg_screen__boxes: one row per box of four plants (20200828_Box.txt).

select
    cast("Box" as integer)         as box_id,
    trim("Mix")                    as community_id,
    trim("Infection")              as infection_code,
    cast("Replicate" as integer)   as replicate,
    trim("Experiment")             as round_id,
    "Comment_General"              as box_comment,
    _row                           as source_row
from {{ source('raw', 'screen_boxes') }}
