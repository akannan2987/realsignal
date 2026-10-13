-- fct_plant: one row per plant, with where it grew, what it received, its
-- marks, and whether later phases use it (see int_plants for the rules).

select
    plant_id,
    box_id,
    position,
    round_id,
    community_id,
    pathogen,
    inclusion_mark,
    inclusion_mark_2020,
    set_aside_reason,
    split,
    use_for_modelling,
    not_used_because,
    notes
from {{ ref('int_plants') }}
