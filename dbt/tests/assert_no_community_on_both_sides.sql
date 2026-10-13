-- No community may have plants for modelling on both sides, training and test.
--
-- If one did, a model would be scored on a community it had already learnt
-- from (data leakage, docs/00-architecture.md section 8). The two reference
-- communities grown in every round are where this could happen, and Choice 2
-- is what prevents it. Returns every community found on both sides.

select community_id, string_agg(distinct split, ', ') as splits
from {{ ref('model_plants') }}
group by community_id
having count(distinct split) > 1
