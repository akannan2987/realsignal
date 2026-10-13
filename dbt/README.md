# dbt/: the harmonisation models

This folder is a dbt project. It turns the raw tables in the warehouse (`data/warehouse/realsignal.duckdb`, filled by `scripts/load_raw.py`) into tested tables in which all five data layers meet on one strain name and one community name. The guide that builds it, step by step, is [`docs/04-phase-3-harmonisation.md`](../docs/04-phase-3-harmonisation.md).

Run every dbt command from inside this folder, because that's where dbt finds `profiles.yml`. From the project folder:

```bash
cd dbt
dbt build            # every model, the seed and every test, in order
dbt docs generate    # the documentation pages
dbt docs serve       # open them in a browser (Ctrl+C to stop)
cd ..
```

| Path | What it holds |
|---|---|
| `dbt_project.yml` | the settings: how each layer is stored, and the choices (`vars`) with their reasons |
| `profiles.yml` | where the database is (a file, so no password) |
| `models/staging/` | one model per raw table (two for Table S9), in a folder per source: renamed, typed, one spelling for every strain |
| `models/intermediate/` | where the sources meet, and where the three Layer 1 choices are applied |
| `models/marts/` | the tables later phases read: `dim_strain`, `dim_community`, `community_member`, `fct_plant`, `fct_plant_measurement`, `fct_strain_interaction`, `fct_gene_cluster`, `model_plants` |
| `models/overview.md` | the front page of the documentation pages |
| `macros/` | `strain_id()` and `looks_like_strain()`, `in_list()`, and the schema names |
| `seeds/known_source_differences.csv` | every place two sources disagree, written down; two tests compare the data with it |
| `tests/` | 17 tests, each a rule too big for one line in a `.yml` file (most of them across tables), and `generic/accepted_range.sql` |

`target/` and `logs/` appear when dbt runs. dbt makes them again every time, so Git ignores them.
