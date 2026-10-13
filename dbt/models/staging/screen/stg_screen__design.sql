-- stg_screen__design: the design, turned from wide to long.
--
-- The file has one column per strain, so its shape depends on the size of the
-- strain library. UNPIVOT turns every column except Mix into rows of
-- (community, strain, cell), whatever the number of strain columns is. That's
-- how nothing downstream needs to know there are 35 strains.

with design as (
    select * exclude (_row) from {{ source('raw', 'screen_design') }}
),

long as (
    unpivot design
    on columns(* exclude ("Mix"))
    into name strain_column value cell
)

select
    trim("Mix")                          as community_id,
    {{ strain_id('strain_column') }}     as strain_id,
    -- 1 means in the community, 0 means not. Anything else becomes NULL,
    -- which the not_null test on this column catches.
    case trim(cell) when '1' then true when '0' then false end as is_member
from long
