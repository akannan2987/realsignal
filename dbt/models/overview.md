{% docs __overview__ %}
# RealSignal: the harmonised data

These pages describe every table in the RealSignal warehouse: what it holds,
where each column comes from, and the tests that check it. Click **Lineage**
(the blue button at the bottom right) to see how each table is built from the
others, from the raw files on the left to the marts on the right.

The layers, in the order data flows through them:

- **raw**: the source tables, unchanged (loaded by `scripts/load_raw.py`)
- **staging**: one model per raw table, renamed and typed, with one spelling for every strain
- **intermediate**: where sources meet, and where the three Layer 1 choices are applied
- **marts**: the tables later phases read: `dim_strain`, `dim_community`, `community_member`, `fct_plant`, `fct_plant_measurement`, `fct_strain_interaction`, `fct_gene_cluster` and `model_plants`
- **reference**: `known_source_differences`, the places where two sources disagree

The guide that builds all of this is `docs/04-phase-3-harmonisation.md` in the repository.
{% enddocs %}
