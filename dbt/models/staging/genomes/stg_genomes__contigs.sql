-- stg_genomes__contigs: one row per contig of every genome.
--
-- scripts/load_raw.py counted each contig's letters. The genome files are
-- named after their strain and accession, and sources/files.csv says which
-- file belongs to which strain, so the strain comes from there.
-- RefSeq writes a contig as NZ_LMJX01000002.1; GenBank, and Supplementary
-- Table 11, as LMJX01000002.1. genbank_accession is the second form.

select
    files.strain_id,
    files.assembly_accession,
    contigs.contig                                    as contig_accession,
    regexp_replace(contigs.contig, '^NZ_', '')        as genbank_accession,
    contigs.description,
    cast(contigs.length as bigint)                    as length_bp,
    cast(contigs.gc_count as bigint)                  as gc_count,
    contigs.file                                      as file_name
from {{ source('raw', 'genome_contigs') }} as contigs
left join {{ ref('stg_register__files') }} as files
    on files.file_name = contigs.file
