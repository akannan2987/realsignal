-- Every raw table belongs to a source in the register, and everything
-- scripts/load_raw.py loaded is listed in sources/tables.csv (or is one of the
-- three tables in sources/ themselves). Returns anything unaccounted for.

select tables.table_name, tables.source_id, 'source not in sources/register.csv' as problem
from {{ ref('stg_register__tables') }} as tables
where tables.source_id not in (select source_id from {{ ref('stg_register__sources') }})
union all
select log.table_name, log.source_id, 'loaded, but not in sources/tables.csv'
from {{ source('raw', 'load_log') }} as log
where log.source_id <> 'register'
  and log.table_name not in (select table_name from {{ ref('stg_register__tables') }})
