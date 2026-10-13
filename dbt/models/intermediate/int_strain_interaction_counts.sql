-- int_strain_interaction_counts: for every strain in the interaction screen,
-- how many strains it held back and how many held it back.
--
-- Supplementary Table 1 lists only the inhibitions that were seen. A strain
-- that took part in the screen (it's on the inhibitor panel or the sensitive
-- panel) and has no row there had no inhibition seen: zero, not unknown. The
-- left joins and coalesce(..., 0) below write that zero. A strain that wasn't
-- in the screen at all gets no row here, so its counts stay unknown (NULL)
-- in dim_strain.
-- "strongly" counts pairs whose strength mentions strong, the one
-- "weak; strong" pair included.

with screened as (
    select strain_id from {{ ref('stg_helfrich__inhibitor_panel') }}
    union
    select strain_id from {{ ref('stg_helfrich__sensitive_panel') }}
),

interactions as (
    select * from {{ ref('stg_helfrich__interactions') }}
),

as_inhibitor as (
    select inhibitor_strain_id as strain_id,
           count(*) as inhibits,
           count(*) filter (where strength like '%strong%') as inhibits_strongly
    from interactions
    group by 1
),

as_sensitive as (
    select sensitive_strain_id as strain_id,
           count(*) as inhibited_by,
           count(*) filter (where strength like '%strong%') as inhibited_strongly_by
    from interactions
    group by 1
)

select
    screened.strain_id,
    coalesce(as_inhibitor.inhibits, 0)                as inhibits,
    coalesce(as_inhibitor.inhibits_strongly, 0)       as inhibits_strongly,
    coalesce(as_sensitive.inhibited_by, 0)            as inhibited_by,
    coalesce(as_sensitive.inhibited_strongly_by, 0)   as inhibited_strongly_by
from screened
left join as_inhibitor on as_inhibitor.strain_id = screened.strain_id
left join as_sensitive on as_sensitive.strain_id = screened.strain_id
