-- stg_helfrich__interactions: every inhibition seen in the strain-against-strain
-- screen (Helfrich et al. 2018, Supplementary Table 1), one row per pair.
--
-- strength is "strong", "weak" or, for one pair, "weak; strong" (the
-- replicates disagreed). media lists where it was seen, separated by "; ".
-- Both are kept as the table writes them. The taxonomy columns of the sheet
-- aren't kept: taxonomy comes from the strain tables.

select
    {{ strain_id('"Inhibitor"') }}       as inhibitor_strain_id,
    {{ strain_id('"Sensitive"') }}       as sensitive_strain_id,
    lower(trim("Interaction"))           as strength,
    trim("Medium")                       as media,
    _row                                 as source_row
from {{ source('raw', 'helfrich_interactions') }}
where {{ looks_like_strain('"Inhibitor"') }}
