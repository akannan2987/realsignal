-- Supplementary Table 12 of Vogel et al. 2021 names each strain twice, as
-- Leaf73 and as 73. After strain_id() both must give the same name. Returns
-- every row where they don't.

select source_row, strain_id, strain_id_from_number
from {{ ref('stg_vogel__strains') }}
where strain_id is distinct from strain_id_from_number
