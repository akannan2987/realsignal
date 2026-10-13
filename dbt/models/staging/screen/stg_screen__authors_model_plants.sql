-- stg_screen__authors_model_plants: which plants the authors' machine-learning
-- table holds. Only the plant columns are kept: this model exists so that a
-- test can check the rebuilt selection (marts.model_plants) against it.
-- It's a data file; the authors' R code stays closed until Phase 6.

select
    trim("Uid")                          as plant_id,
    trim("Mix")                          as community_id,
    trim("Experiment")                   as round_id,
    upper(trim("IncludedAnalysis"))      as inclusion_mark
from {{ source('raw', 'screen_authors_model_input') }}
