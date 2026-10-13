-- int_communities: one row per community in the design, with its size, kind
-- and role.
--
-- Nothing here knows how many strains the library has or how many go into a
-- community. Both are counted from the design:
--   community_size  how many strains the community holds
--   kind            'no strains' (size 0), 'whole library' (every strain),
--                   otherwise 'community'
--   role            'control' for the two other kinds; 'test' for a community
--                   grown in a test round (var test_rounds); 'training' for
--                   the rest
-- A community grown in the test round and in earlier rounds as well (the two
-- reference communities) is therefore a test community. Its earlier plants
-- are handled in int_plants.

with members as (
    select community_id, count(*) filter (where is_member) as community_size
    from {{ ref('stg_screen__design') }}
    group by community_id
),

library as (
    select count(distinct strain_id) as library_size
    from {{ ref('stg_screen__design') }}
),

grown as (
    select
        community_id,
        string_agg(distinct round_id, ', ' order by round_id)              as rounds_grown,
        bool_or(round_id in {{ in_list(var('test_rounds')) }})              as grown_in_test_round,
        count(*)                                                            as plants_grown,
        -- the name figures use (SynCom-High for Mix69), from infected plants where there are any
        coalesce(min(figure_label) filter (where infection_code <> '{{ var("no_pathogen_code") }}'),
                 min(figure_label))                                         as label
    from {{ ref('stg_screen__plants') }}
    group by community_id
),

sized as (
    select
        members.community_id,
        grown.label,
        members.community_size,
        case
            when members.community_size = 0 then 'no strains'
            when members.community_size = library.library_size then 'whole library'
            else 'community'
        end                                                      as kind,
        coalesce(grown.grown_in_test_round, false)               as grown_in_test_round,
        grown.rounds_grown,
        coalesce(grown.plants_grown, 0)                          as plants_grown
    from members
    cross join library
    left join grown on grown.community_id = members.community_id
)

select
    community_id,
    label,
    community_size,
    kind,
    case
        when kind <> 'community' then 'control'
        when grown_in_test_round then 'test'
        else 'training'
    end as role,
    rounds_grown,
    plants_grown
from sized
