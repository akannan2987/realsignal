-- community_member: which strains each community holds, one row per pair.
-- A bridge table: it links dim_community and dim_strain, which have a
-- many-to-many relationship (a community holds several strains, and a strain
-- is in many communities).

select
    community_id,
    strain_id
from {{ ref('stg_screen__design') }}
where is_member
