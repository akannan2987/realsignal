-- dim_community: one row per community in the design, controls included.
--
-- role says how the community is used (training, test or control) and
-- plants_for_modelling how many of its plants marts.model_plants keeps. A
-- community the design made whose plants were all left out stays here, with
-- plants_for_modelling = 0 (Choice 3, docs/04-phase-3-harmonisation.md).

with used as (
    select community_id, count(*) filter (where use_for_modelling) as plants_for_modelling
    from {{ ref('int_plants') }}
    group by community_id
)

select
    communities.community_id,
    communities.label,
    communities.community_size,
    communities.kind,
    communities.role,
    communities.rounds_grown,
    communities.plants_grown,
    coalesce(used.plants_for_modelling, 0)        as plants_for_modelling,
    coalesce(used.plants_for_modelling, 0) > 0    as has_plants_for_modelling
from {{ ref('int_communities') }} as communities
left join used on used.community_id = communities.community_id
