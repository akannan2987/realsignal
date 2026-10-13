-- The box file and the plant file describe the same boxes. Every plant must
-- sit in a box of the box file, with the same community, infection and round.
-- Returns every plant where they differ.

select
    plants.plant_id,
    plants.community_id   as plant_file_community,   boxes.community_id   as box_file_community,
    plants.infection_code as plant_file_infection,   boxes.infection_code as box_file_infection,
    plants.round_id       as plant_file_round,       boxes.round_id       as box_file_round
from {{ ref('stg_screen__plants') }} as plants
left join {{ ref('stg_screen__boxes') }} as boxes on boxes.box_id = plants.box_id
where boxes.box_id is null
   or plants.community_id   is distinct from boxes.community_id
   or plants.infection_code is distinct from boxes.infection_code
   or plants.round_id       is distinct from boxes.round_id
