-- The rebuilt choice of plants against the authors' own machine-learning table.
--
-- With keep_undecided_plants true (Choice 1), marts.model_plants must hold
-- exactly the plants of MLData_DF_Ind_TRUE_CommPresence.txt; with false, the
-- same plants minus those marked TBD. Returns every plant found on one side
-- only. It compares data files: the authors' code stays closed until Phase 6.

with ours as (
    select plant_id from {{ ref('model_plants') }}
),

theirs as (
    select plant_id from {{ ref('stg_screen__authors_model_plants') }}
    {% if not var('keep_undecided_plants') %}
    where inclusion_mark <> 'TBD'
    {% endif %}
)

select plant_id, 'rebuilt only' as found
from (select plant_id from ours except select plant_id from theirs)
union all
select plant_id, 'authors only' as found
from (select plant_id from theirs except select plant_id from ours)
