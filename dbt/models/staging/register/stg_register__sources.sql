-- stg_register__sources: sources/register.csv, one row per data source.
-- Typed and renamed; nothing else changes.

select
    trim(source_id)              as source_id,
    trim(layer)                  as layers,          -- text: one source can provide two layers ("3, 4")
    trim(layer_name)             as layer_name,
    citation,
    doi,
    terms,
    trim(status)                 as status,
    cast(checked_on as date)     as checked_on,
    notes
from {{ source('raw', 'source_register') }}
