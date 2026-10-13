-- int_strain_genomes: one row per strain with a genome: its size in letters,
-- the number of pieces (contigs) it's in, and its GC content.

select
    strain_id,
    min(assembly_accession)                         as assembly_accession,
    count(*)                                        as contigs,
    sum(length_bp)                                  as genome_length_bp,
    100.0 * sum(gc_count) / sum(length_bp)          as gc_percent
from {{ ref('stg_genomes__contigs') }}
group by strain_id
