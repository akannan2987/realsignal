-- Between the 2020 notes and the 2023 plant file, a plant's mark may stay the
-- same or move from TBD to FALSE (a decision made later). Any other change,
-- TRUE to FALSE or FALSE to TRUE, would need an explanation the files don't
-- give. Returns every such plant.

select plant_id, inclusion_mark_2020, inclusion_mark
from {{ ref('fct_plant') }}
where inclusion_mark is distinct from inclusion_mark_2020
  and not (inclusion_mark_2020 = 'TBD' and inclusion_mark = 'FALSE')
