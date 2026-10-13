-- A strain can only be counted on a plant whose community holds it. Returns
-- every count of a strain that isn't a member of the plant's community.

select measurements.plant_id, measurements.strain_id, plants.community_id
from {{ ref('fct_plant_measurement') }} as measurements
join {{ ref('fct_plant') }} as plants on plants.plant_id = measurements.plant_id
left join {{ ref('community_member') }} as members
    on members.community_id = plants.community_id
   and members.strain_id = measurements.strain_id
where measurements.strain_id is not null
  and members.strain_id is null
