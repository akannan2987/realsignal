-- Table S9 checked against itself, twice:
--   * each strain's Total column equals the sum of its class columns;
--   * the Total row at the bottom equals the sum of every strain's Total.
-- Both hold (the three extra clusters are in the class columns too), so the
-- difference from Table S11 is between the two tables, not inside Table S9.

with classes as (
    select strain_id, sum(cluster_count) as summed
    from {{ ref('stg_helfrich__bgc_counts') }}
    group by strain_id
),

per_strain as (
    select totals.strain_id, totals.reported_total, classes.summed
    from {{ ref('stg_helfrich__bgc_totals') }} as totals
    join classes on classes.strain_id = totals.strain_id
    where totals.reported_total <> classes.summed
),

total_row as (
    select cast("Total" as integer) as reported_total
    from {{ source('raw', 'helfrich_bgc_counts') }}
    where trim("Strain") = 'Total'
)

select strain_id, reported_total, summed
from per_strain
union all
select 'Total row', total_row.reported_total,
       (select sum(reported_total) from {{ ref('stg_helfrich__bgc_totals') }})
from total_row
where total_row.reported_total <> (select sum(reported_total) from {{ ref('stg_helfrich__bgc_totals') }})
