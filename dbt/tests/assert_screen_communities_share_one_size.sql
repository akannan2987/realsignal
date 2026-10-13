-- Every community of the screen holds the same number of strains.
--
-- The number itself isn't written here or anywhere in the models: it comes
-- from the design. The test only checks that there is one. A future screen
-- that mixes community sizes would change this test, on purpose.

select community_size, count(*) as communities
from {{ ref('dim_community') }}
where kind = 'community'
group by community_size
having (select count(distinct community_size)
        from {{ ref('dim_community') }}
        where kind = 'community') > 1
