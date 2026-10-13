-- fct_strain_interaction: every inhibition seen between two strains of the
-- collection, one row per pair (inhibitor holds back sensitive).
-- Pairs that were tested and showed nothing aren't rows: dim_strain counts
-- them as zero for every strain in the screen.

with library as (
    select distinct strain_id from {{ ref('stg_screen__design') }}
)

select
    interactions.inhibitor_strain_id || '->' || interactions.sensitive_strain_id as interaction_id,
    interactions.inhibitor_strain_id,
    interactions.sensitive_strain_id,
    interactions.strength,
    interactions.media,
    interactions.inhibitor_strain_id in (select strain_id from library)
        and interactions.sensitive_strain_id in (select strain_id from library) as both_in_screen_library
from {{ ref('stg_helfrich__interactions') }} as interactions
