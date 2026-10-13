-- A plant's fresh weight must be above zero, unless the plant is marked FALSE.
-- The two missing plants are weighed as empty tubes (0.7 mg and -0.4 mg: a
-- scale drifts a little), and both are FALSE. Returns any other plant with a
-- weight of zero or less.

select weights.plant_id, weights.value as fresh_weight_mg, plants.inclusion_mark
from {{ ref('fct_plant_measurement') }} as weights
join {{ ref('fct_plant') }} as plants on plants.plant_id = weights.plant_id
where weights.measurement = 'fresh_weight'
  and weights.value <= 0
  and plants.inclusion_mark <> 'FALSE'
