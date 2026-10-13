-- stg_helfrich__sensitive_panel: the strains tested as sensitive
-- (Helfrich et al. 2018, Supplementary Table 24). The three footnotes under
-- the table fail looks_like_strain() and are left out.

select
    {{ strain_id('"Strain"') }}          as strain_id,
    _row                                 as source_row
from {{ source('raw', 'helfrich_sensitive_panel') }}
where {{ looks_like_strain('"Strain"') }}
