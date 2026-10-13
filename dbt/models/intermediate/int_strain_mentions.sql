-- int_strain_mentions: every strain every source names, once per source.
--
-- After strain_id() each source spells a strain the same way, so the union
-- below is the full list of strains the project knows about, and where each
-- one is mentioned. marts.dim_strain has one row per strain in it.

{% set mentions = [
    ('stg_screen__design', 'strain_id'),
    ('stg_screen__strain_colonisation', 'strain_id'),
    ('stg_collection__strains', 'strain_id'),
    ('stg_helfrich__interactions', 'inhibitor_strain_id'),
    ('stg_helfrich__interactions', 'sensitive_strain_id'),
    ('stg_helfrich__inhibitor_panel', 'strain_id'),
    ('stg_helfrich__sensitive_panel', 'strain_id'),
    ('stg_helfrich__bgc_totals', 'strain_id'),
    ('stg_helfrich__gene_clusters', 'strain_id'),
    ('stg_vogel__strains', 'strain_id'),
    ('stg_genomes__contigs', 'strain_id'),
] %}

{% for model, column in mentions %}
select distinct {{ column }} as strain_id, '{{ model }}' as mentioned_in
from {{ ref(model) }}
where {{ column }} is not null
{% if not loop.last %}union{% endif %}
{% endfor %}
