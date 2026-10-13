-- Layer 2 against the two strain lists, for every strain of the screen:
--   * sources/files.csv lists a genome exactly when Vogel et al. 2021 (ST12)
--     gives an accession, and the two accessions are the same;
--   * that's also exactly when the Layer 1 archive says the genome was
--     published in Bai et al. 2015;
--   * every genome in sources/files.csv was loaded.
-- Leaf21 passes: none of the three sources has a genome for it.

with library as (
    select distinct strain_id from {{ ref('stg_screen__design') }}
),

files as (
    select strain_id, assembly_accession, file_name
    from {{ ref('stg_register__files') }}
    where kind = 'ncbi_assembly'
),

checked as (
    select
        library.strain_id,
        files.assembly_accession                 as in_files_csv,
        vogel.assembly_accession                 as in_st12,
        collection.genome_in_bai2015
    from library
    left join files on files.strain_id = library.strain_id
    left join {{ ref('stg_vogel__strains') }} as vogel on vogel.strain_id = library.strain_id
    left join {{ ref('stg_collection__strains') }} as collection on collection.strain_id = library.strain_id
)

select strain_id, 'accessions differ' as problem
from checked
where in_files_csv is distinct from in_st12
union all
select strain_id, 'genome listed, but the archive says not published (or the reverse)'
from checked
where (in_files_csv is not null) is distinct from genome_in_bai2015
union all
select strain_id, 'genome file not loaded'
from files
where file_name not in (select file_name from {{ ref('stg_genomes__contigs') }})
