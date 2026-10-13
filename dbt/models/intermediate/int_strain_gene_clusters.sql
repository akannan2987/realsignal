-- int_strain_gene_clusters: how many gene clusters each analysed strain has,
-- counted two ways.
--
--   clusters_reported  the Total column of Supplementary Table 9
--   clusters_listed    the rows of Supplementary Table 11, one per cluster
--
-- A strain is "analysed" when Table 9 has a row for it. Table 11 then lists
-- its clusters, and a strain it doesn't mention has none listed (0). The two
-- counts differ for three strains; a test compares the differences with
-- seeds/known_source_differences.csv.

with listed as (
    select strain_id,
           count(*) as clusters_listed,
           count(*) filter (where potentially_inhibitory) as potentially_inhibitory_clusters
    from {{ ref('stg_helfrich__gene_clusters') }}
    group by strain_id
)

select
    totals.strain_id,
    totals.reported_total                                 as clusters_reported,
    coalesce(listed.clusters_listed, 0)                   as clusters_listed,
    coalesce(listed.potentially_inhibitory_clusters, 0)   as potentially_inhibitory_clusters
from {{ ref('stg_helfrich__bgc_totals') }} as totals
left join listed on listed.strain_id = totals.strain_id
