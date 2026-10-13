-- stg_screen__plant_weights: the fresh weight of every plant, in milligrams.
-- (The raw weighing file records tube weights of about 1,800, which only
-- makes sense in milligrams.) The normalised value is the authors', as published.

select
    trim("Uid")                              as plant_id,
    cast("PlantWeight" as double)            as fresh_weight_mg,
    cast("NormPlantWeight" as double)        as fresh_weight_normalised,
    _row                                     as source_row
from {{ source('raw', 'screen_plant_weights') }}
