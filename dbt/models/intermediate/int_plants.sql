-- int_plants: every plant, with the three Layer 1 choices applied.
-- (docs/04-phase-3-harmonisation.md, section 8, gives the reasons.)
--
-- split says which part of the experiment a plant belongs to:
--   training                 its community is a training community
--   test                     its community is a test community, grown here in
--                            a test round
--   between-round reference  its community is a test community, but this plant
--                            grew in an earlier round (Choice 2: these plants
--                            compare rounds and never train a model, so no
--                            test community is seen during training)
--   control                  no strains, or the whole library
--
-- use_for_modelling is true for an infected training or test plant, unless the
-- plant file marks it FALSE, or marks it TBD while var keep_undecided_plants
-- is false (Choice 1). not_used_because says why, in words, when it's false.
-- A community whose plants are all FALSE keeps its row in dim_community and
-- has no plants for modelling (Choice 3).

{% set keep_undecided = 'true' if var('keep_undecided_plants') else 'false' %}

with plants as (
    select * from {{ ref('stg_screen__plants') }}
),

notes as (
    select plant_id, inclusion_mark_2020, set_aside_reason, notes
    from {{ ref('stg_screen__plant_notes') }}
),

communities as (
    select community_id, kind, role from {{ ref('int_communities') }}
),

placed as (
    select
        plants.plant_id,
        plants.box_id,
        plants.position,
        plants.round_id,
        plants.community_id,
        case when plants.infection_code = '{{ var("no_pathogen_code") }}' then null
             else plants.infection_code end                       as pathogen,
        plants.inclusion_mark,
        notes.inclusion_mark_2020,
        notes.set_aside_reason,
        notes.notes,
        case
            when communities.kind <> 'community' then 'control'
            when communities.role = 'training' then 'training'
            when plants.round_id in {{ in_list(var('test_rounds')) }} then 'test'
            else 'between-round reference'
        end                                                        as split
    from plants
    left join communities on communities.community_id = plants.community_id
    left join notes on notes.plant_id = plants.plant_id
)

select
    *,
    case
        when split not in ('training', 'test') then false
        when pathogen is null then false
        when inclusion_mark = 'FALSE' then false
        when inclusion_mark = 'TBD' and not {{ keep_undecided }} then false
        else true
    end as use_for_modelling,
    case
        when split = 'control' then 'control plant'
        when split = 'between-round reference' then 'grown before the test round; its community is a test community'
        when pathogen is null then 'not infected'
        when inclusion_mark = 'FALSE' then 'marked FALSE: ' || coalesce(set_aside_reason, 'no reason given')
        when inclusion_mark = 'TBD' and not {{ keep_undecided }} then 'marked TBD, and keep_undecided_plants is false'
    end as not_used_because
from placed
