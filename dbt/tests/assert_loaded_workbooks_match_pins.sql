-- The warehouse was built from exactly the files Phase 2 pinned.
--
-- scripts/load_raw.py records the SHA-256 of every file it reads in
-- raw.load_log; sources/files.csv holds the pins. Returns a pinned file whose
-- loaded copy has another checksum, or that wasn't loaded at all.

with pinned as (
    select file_name, pinned_sha256
    from {{ ref('stg_register__files') }}
    where pinned_sha256 is not null
),

loaded as (
    select distinct path, sha256
    from {{ source('raw', 'load_log') }}
)

select pinned.file_name, pinned.pinned_sha256, loaded.sha256 as loaded_sha256
from pinned
left join loaded on loaded.path like '%/' || pinned.file_name
where loaded.sha256 is distinct from pinned.pinned_sha256
