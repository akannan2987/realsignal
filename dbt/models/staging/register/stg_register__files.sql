-- stg_register__files: sources/files.csv, one row per file Phase 2 fetches.
-- For a genome, location holds its NCBI accession; for a workbook, its
-- addresses. strain is filled in for genomes only.

select
    trim(file_id)                                              as file_id,
    trim(source_id)                                            as source_id,
    trim(kind)                                                 as kind,
    trim(target)                                               as file_name,
    case when kind = 'ncbi_assembly' then trim(location) end   as assembly_accession,
    nullif(trim(pinned_sha256), '')                            as pinned_sha256,
    case when strain is not null then {{ strain_id('strain') }} end as strain_id
from {{ source('raw', 'source_files') }}
