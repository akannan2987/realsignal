-- fct_plant_measurement: every measurement on every plant, one per row.
--
-- A long table: plant, what was measured, the value and its unit. A new kind
-- of measurement (another pathogen, a chemical readout) becomes more rows,
-- not new columns, so nothing downstream has to change to take it in.
-- strain_id is filled in for measurements of one community member only.
-- Values are as published, including the two weights of the missing plants
-- (an empty tube weighs about nothing, and one weighs slightly less than
-- nothing); both plants are marked FALSE.

with pathogen as (
    select plant_id, cfu_per_g, log10_cfu_per_g, log10_cfu_per_g_normalised
    from {{ ref('stg_screen__pathogen_load') }}
),

measurements as (
    select plant_id, 'pathogen_cfu_per_g' as measurement, null as strain_id,
           cfu_per_g as value, 'CFU per g fresh weight' as unit, null::boolean as is_ambiguous,
           'screen_pathogen_load' as source_table
    from pathogen
    union all
    select plant_id, 'pathogen_log10_cfu_per_g', null, log10_cfu_per_g,
           'log10 CFU per g fresh weight', null, 'screen_pathogen_load'
    from pathogen
    union all
    select plant_id, 'pathogen_log10_normalised', null, log10_cfu_per_g_normalised,
           'normalised by the authors', null, 'screen_pathogen_load'
    from pathogen
    union all
    select plant_id, 'fresh_weight', null, fresh_weight_mg, 'mg', null, 'screen_plant_weights'
    from {{ ref('stg_screen__plant_weights') }}
    union all
    select plant_id, 'fresh_weight_normalised', null, fresh_weight_normalised,
           'normalised by the authors', null, 'screen_plant_weights'
    from {{ ref('stg_screen__plant_weights') }}
    union all
    select plant_id, 'commensal_cfu_per_g', null, cfu_per_g,
           'CFU per g fresh weight', null, 'screen_commensal_load'
    from {{ ref('stg_screen__commensal_load') }}
    union all
    select plant_id, 'commensal_log10_cfu_per_g', null, log10_cfu_per_g,
           'log10 CFU per g fresh weight', null, 'screen_commensal_load'
    from {{ ref('stg_screen__commensal_load') }}
    union all
    select plant_id, 'strain_cfu_per_g', strain_id, cfu_per_g,
           'CFU per g fresh weight', is_ambiguous, 'screen_strain_colonisation'
    from {{ ref('stg_screen__strain_colonisation') }}
    union all
    select plant_id, 'strain_log10_cfu_per_g', strain_id, log10_cfu_per_g,
           'log10 CFU per g fresh weight', is_ambiguous, 'screen_strain_colonisation'
    from {{ ref('stg_screen__strain_colonisation') }}
)

select
    plant_id || '|' || measurement || coalesce('|' || strain_id, '')   as measurement_id,
    plant_id,
    measurement,
    strain_id,
    value,
    unit,
    is_ambiguous,
    source_table
from measurements
