-- The two strain lists (the Layer 1 archive's and Vogel et al. 2021's) must
-- agree on phylum and class for every strain both list, and may disagree on
-- family or genus only where seeds/known_source_differences.csv says so.

with pairs as (
    select
        archive.strain_id,
        archive.phylum           as archive_phylum,   vogel.phylum           as vogel_phylum,
        archive.taxonomic_class  as archive_class,    vogel.taxonomic_class  as vogel_class,
        archive.family           as archive_family,   vogel.family           as vogel_family,
        archive.genus            as archive_genus,    vogel.genus            as vogel_genus
    from {{ ref('stg_collection__strains') }} as archive
    join {{ ref('stg_vogel__strains') }} as vogel on vogel.strain_id = archive.strain_id
),

found as (
    select 'phylum' as what_differs, strain_id, archive_phylum as first_value, vogel_phylum as second_value
    from pairs where archive_phylum is distinct from vogel_phylum
    union all
    select 'class', strain_id, archive_class, vogel_class
    from pairs where archive_class is distinct from vogel_class
    union all
    select 'family', strain_id, archive_family, vogel_family
    from pairs where archive_family is distinct from vogel_family
    union all
    select 'genus', strain_id, archive_genus, vogel_genus
    from pairs where archive_genus is distinct from vogel_genus
),

known as (
    select what_differs, strain_id, first_value, second_value
    from {{ ref('known_source_differences') }}
    where what_differs in ('family', 'genus')
)

select *, 'found, but not on the list' as problem
from (select * from found except select * from known)
union all
select *, 'on the list, but not found' as problem
from (select * from known except select * from found)
