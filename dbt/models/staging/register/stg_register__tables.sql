-- stg_register__tables: sources/tables.csv, one row per raw table.

select
    trim(table_name)                    as table_name,
    trim(source_id)                     as source_id,
    trim(format)                        as format,
    path,
    sheet,
    cast(header_row as integer)         as header_row,
    what_it_holds
from {{ source('raw', 'source_tables') }}
