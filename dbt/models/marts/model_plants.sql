-- model_plants: the plants later phases train and test on, one row per plant,
-- with the outcome to predict.
--
-- Which plants: fct_plant.use_for_modelling (the three Layer 1 choices).
-- Which outcome: var outcome_measurement in dbt/dbt_project.yml, by its name
-- in fct_plant_measurement. Changing that setting changes the outcome without
-- touching this file. The community's strains come from community_member;
-- Phase 5 turns them into one column per strain.

select
    plants.plant_id,
    plants.community_id,
    plants.round_id,
    plants.split,
    plants.inclusion_mark,
    '{{ var("outcome_measurement") }}'     as outcome_measurement,
    outcome.value                          as outcome
from {{ ref('fct_plant') }} as plants
left join {{ ref('fct_plant_measurement') }} as outcome
    on outcome.plant_id = plants.plant_id
   and outcome.measurement = '{{ var("outcome_measurement") }}'
   and outcome.strain_id is null
where plants.use_for_modelling
