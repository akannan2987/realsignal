-- Table S9 (clusters counted per strain) against Table S11 (clusters listed
-- one by one): they may differ only where seeds/known_source_differences.csv
-- says they do. Returns a difference that isn't on the list, or a listed one
-- that's no longer there.

with found as (
    select strain_id,
           cast(clusters_reported as varchar) as first_value,
           cast(clusters_listed as varchar)   as second_value
    from {{ ref('int_strain_gene_clusters') }}
    where clusters_reported <> clusters_listed
),

known as (
    select strain_id, first_value, second_value
    from {{ ref('known_source_differences') }}
    where what_differs = 'gene_cluster_count'
)

select *, 'found, but not on the list' as problem
from (select * from found except select * from known)
union all
select *, 'on the list, but not found' as problem
from (select * from known except select * from found)
