-- stg_helfrich__inhibitor_panel: the strains tested as inhibitors
-- (Helfrich et al. 2018, Supplementary Table 4, first column). The rest of
-- the sheet, results on six media against ten strains, isn't needed here.

select
    {{ strain_id('"Inhibitor"') }}       as strain_id,
    _row                                 as source_row
from {{ source('raw', 'helfrich_inhibitor_panel') }}
where {{ looks_like_strain('"Inhibitor"') }}
