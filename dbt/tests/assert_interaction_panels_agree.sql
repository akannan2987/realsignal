-- The interaction screen tested the same strains as inhibitors (Table S4) and
-- as sensitive strains (Table S24), and every strain in Table S1 is one of
-- them. That's what makes "no row in Table S1" mean zero for a strain on the
-- panels. Returns every strain that breaks it.

with inhibitors as (select strain_id from {{ ref('stg_helfrich__inhibitor_panel') }}),
sensitive as (select strain_id from {{ ref('stg_helfrich__sensitive_panel') }}),
in_table_s1 as (
    select inhibitor_strain_id as strain_id from {{ ref('stg_helfrich__interactions') }}
    union
    select sensitive_strain_id from {{ ref('stg_helfrich__interactions') }}
)

select strain_id, 'inhibitor panel only' as problem
from (select * from inhibitors except select * from sensitive)
union all
select strain_id, 'sensitive panel only'
from (select * from sensitive except select * from inhibitors)
union all
select strain_id, 'in Table S1 but on neither panel'
from (select * from in_table_s1 except select * from inhibitors)
