# Changelog

All notable changes to RealSignal are recorded here, newest first. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses [Semantic Versioning](https://semver.org/): version numbers look like `MAJOR.MINOR.PATCH`, a new MINOR version marks a milestone from [`docs/ROADMAP.md`](docs/ROADMAP.md#4-milestones-and-version-tags), a PATCH marks a fix, and 1.0.0 marks the first complete release.

Each step is explained in [`docs/HANDBOOK.md`](docs/HANDBOOK.md), the guide from day 0 to the finished product.

## [Unreleased]

Nothing yet.

## [0.2.0] - 2026-10-13

Phases 2 and 3: the other four data layers fetched and checked ([`docs/03-phase-2-more-sources.md`](docs/03-phase-2-more-sources.md)), and all five harmonised in one tested warehouse with dbt ([`docs/04-phase-3-harmonisation.md`](docs/04-phase-3-harmonisation.md)).

**Result, Phase 3.** Every raw table (20 tables, 13,908 rows) loads unchanged into the DuckDB warehouse `data/warehouse/realsignal.duckdb`, and a dbt project of 35 models builds from it the tables later phases read: 285 strains on one spelling, 208 communities with their roles, 960 plants, nine kinds of measurement, 725 inhibitions and 1,050 gene clusters. `dbt build` passes all 223 steps (1 seed, 35 models, 187 data tests). The three choices Phase 2 left are made: the 120 undecided (`TBD`) plants are kept, as the authors' tables keep them (leaving them out would empty 22 training and 12 test communities), with a setting to leave them out; `Mix69` and `Mix70` are test communities, their 16 plants from earlier rounds kept only for comparing rounds; `Mix54` and `Mix73` keep their rows with no plants (136 training communities designed, 134 with plants). The rebuilt choice of 808 plants is the authors', plant for plant. The tests located the three gene clusters on which Tables S9 and S11 disagree (one each for Leaf61, Leaf130 and Leaf182), found that the two strain lists differ on 7 families and 10 genera (agreeing on every phylum and class), record Leaf168, Leaf371 and Leaf454 as screened with no inhibition seen, and confirm that all 191 gene clusters of the 34 strains with a genome sit inside their contigs. A test runs the loader and the whole dbt project on a made-up screen of four strains in communities of two. 54 tests pass.

**Result, Phase 2.** Layer 1's files hold 206 five-strain communities: 136 for training (rounds 1 and 2), 68 new ones for testing (round 3), and `Mix69` and `Mix70`, grown in every round, which complete the 70 test communities. The authors' 12 per-plant machine-learning tables (808 plants from 204 communities) can be rebuilt exactly from the plant file, and they keep 120 undecided (`TBD`) plants from boxes that were dropped and recovered. All 36 files of Layers 2 to 5 download and check out (48.5 MB): 34 genomes match the MD5 that NCBI publishes (Leaf21, the 35th strain, has no genome listed), and the two journal workbooks are pinned by SHA-256. Layer 5's workbook differs in its bytes from the copy in the Phase 1 archive, which was saved again later, but every cell of its 14 sheets holds the same value. In the 2018 workbook, Table S9 counts 1,053 gene clusters and Table S11 lists 1,050, a difference left for Phase 3's data tests. 36 tests pass.

### Added

- `sources/tables.csv`: every raw table to load (17), with its source, file, sheet, heading row and what it holds.
- `scripts/load_raw.py`: `--list` prints the table list; the default run loads every table, and the three tables in `sources/`, into the schema `raw` of `data/warehouse/realsignal.duckdb`, every value as text with a `_row` column pointing back into the file, the genomes as one row per contig with their letters counted, in one transaction, with `raw.load_log` holding each file's SHA-256. It loads nothing when a file is missing, and says so in plain words when the warehouse is open in another program.
- `dbt/`: the dbt project. `dbt_project.yml` (layers, schemas, the settings `keep_undecided_plants`, `test_rounds`, `no_pathogen_code` and `outcome_measurement`, anonymous usage statistics switched off) and `profiles.yml` (the warehouse file); 21 staging models in six folders, one per source; 6 intermediate models, `int_plants` applying the three Layer 1 choices; 8 marts (`dim_strain`, `dim_community`, `community_member`, `fct_plant`, `fct_plant_measurement`, `fct_strain_interaction`, `fct_gene_cluster`, `model_plants`); the macros `strain_id()`, `looks_like_strain()`, `in_list()` and `generate_schema_name()`; the seed `known_source_differences.csv` (20 rows); 170 generic data tests (with the new `accepted_range`) and 17 singular ones; descriptions of every model and column, `models/overview.md` for the documentation pages, and `README.md`.
- `src/realsignal/helpers.py`: the helpers `scripts/fetch_data.py` and `scripts/fetch_sources.py` had each carried (sizes, paths, banners, checksums, reading and writing CSV tables), now shared with `scripts/load_raw.py`.
- `notebooks/explore_warehouse.py`: the strains, communities, plants, the modelling table, the measurements and the known differences, every number from a query on the marts.
- `figures/make_phase3_figures.py`, drawing `figures/lineage.png` and `figures/data_model.png` from dbt's manifest and `figures/plant_choices.png` from the warehouse.
- Tests, 18 more, 54 in all: `tests/test_helpers.py` (5), `tests/test_load_raw.py` (9: text kept as written, row numbers, workbook headings and footnotes, genomes counted, the load log, nothing loaded when a file is missing, a second run replaces, plain output within 80 columns for the real table list too) and `tests/test_warehouse.py` (4: the loader and the whole dbt project on a made-up screen, and the undecided plants left out by a setting).
- `docs/04-phase-3-harmonisation.md`: the Phase 3 guide, in 20 sections.
- `sources/register.csv`, the source register: one row per source with its layer, citation, DOI, where the files come from, terms, status and date; and `sources/files.csv`, one row per file with its address or NCBI accession, the name to save it under, its pinned checksum and, for Layer 5, the copy in the Phase 1 archive to compare with. Leaf21 has no genome accession in the strain table, which the register records.
- `scripts/fetch_sources.py`: `--list` prints the register; `--probe` checks every file can be reached and downloads nothing; the default run fetches each file once into `data/raw/sources/<source>/`, throws away a download that doesn't start like its kind of file (a web page sent instead of a workbook) and tries the next address, checks genomes against the MD5 that NCBI publishes and workbooks against a pinned SHA-256, compares Layer 5's workbook with the archive copy (byte for byte, then cell by cell), moves a mismatching file aside, and logs every file in `data/raw/sources/fetch_log.json`; `--pin` records first-download checksums in `sources/files.csv` and each source's status and date in `sources/register.csv`; `--force` and `--only` as their names say. There is a pause after every request to NCBI.
- `notebooks/explore_layer1.py`: Layer 1's design, its plants per round with their marks, the training and test communities, why plants were set aside, and the authors' 16 machine-learning input tables, one of them rebuilt from the plant file as a check.
- `notebooks/explore_sources.py`: the sheets of each fetched workbook, with how many of the screen's 35 strains each mentions and which strains a nearly complete sheet leaves out, and each genome's contigs, length and GC content.
- `figures/make_phase2_figures.py`, drawing `figures/three_checks.png` (three ways to trust a download), `figures/source_register.png` (drawn from the register) and `figures/layer1_rounds.png` (every box of the three rounds), and building `docs/interactive/communities.html` (pick strains, see which training and test communities held them).
- Tests, 17 more, 36 in all: `tests/test_fetch_sources.py` (12), the register as committed and the fetcher against a stand-in web server on your own computer (published MD5, mirrors, a web page refused, pinning and statuses, a second run that downloads nothing, a changed file moved aside, the cross-check, a workbook saved again told apart from one with different values, plain output); `tests/test_explore.py` (5), both explorers on tiny made-up tables and a two-sheet workbook.
- `docs/03-phase-2-more-sources.md`: the Phase 2 guide, in 18 sections.

### Changed

- `requirements.txt`: `dbt-core` and `dbt-duckdb`; `requirements.lock.txt` written again after installing them.
- `scripts/check_env.py`: checks twelve packages, shown under the name pip installs them by, with the version pip recorded.
- `scripts/fetch_data.py`, `scripts/fetch_sources.py`: their small helpers come from `src/realsignal/helpers.py`; what they do is unchanged.
- `pytest.ini`: `pythonpath = src`, so tests can import the package.
- `.gitignore`, and its copy in `docs/01-setup.md` section 11: `dbt/target/`, `dbt/logs/` and `dbt/dbt_packages/`.
- `tests/test_docs.py`: `.sql` and `.csv` files are checked for look-alike characters too.
- `docs/HANDBOOK.md`, revision 4: Stage 5 written out with its steps, real checkpoint numbers and save block with the v0.2.0 tag; Stage 6 next; the Phase 3 commands in the whole build; nine new troubleshooting rows; the new files in the file index.
- `figures/make_illustrations.py`: Stage 5 done, Stage 6 next.
- `README.md`: version v0.2.0, the Phase 3 result, the layers harmonised, the gene-cluster count as listed (1,050), the build status, the tutorial table, the repository map and the run commands.
- `docs/ROADMAP.md`: Phase 3 done, with what it built and taught; status line, checklist, tag table and risks updated.
- `docs/GLOSSARY.md`: new terms (taxonomy and its ranks, between-round reference plants, `sys.path`, UNPIVOT, `ref()` and `source()`, Jinja and macros, views and tables, materialisation, seed in dbt's sense, var, adapter, profile, dimension, fact and bridge table, key, join, generic and singular tests, `dbt build`, `dbt show` and `dbt docs`, manifest and catalog, graph operators, transaction, lock, localhost), and schema, wide and long format and data warehouse brought up to date.
- `docs/00-architecture.md`: Layers 2 to 5, the harmonised tables and DuckDB marked built in the diagram; Box 3 with the real disagreements and what Phase 3 built; the SQL example in Box 4 runs on the real warehouse; the run commands and the note on `src/` brought up to date.
- `docs/PRODUCT_ROADMAP.md`: the reuse test on a made-up screen, the list of known differences, and the cloud warehouse marked optional and not built.
- `docs/index.html`: the lineage and the plant choices.
- `docs/01-setup.md`: the two new packages in the requirements listing, twelve packages in the check (with the output from the Mac), and a pointer to `src/realsignal/helpers.py`.
- `docs/03-phase-2-more-sources.md`: its pointers to Phase 3 now say what Phase 3 did.
- `docs/GIT_WORKFLOW.md`: the v0.2.0 line in the table of tags.
- `src/realsignal/__init__.py`: its docstring names `helpers.py`.
- `docs/HANDBOOK.md`, revision 3: Stage 4 written out with its steps, real checkpoint numbers and save block; Stage 5 names the three choices Phase 2 left for Phase 3; the Phase 2 commands in the whole build; six new troubleshooting rows; nine new rows in the file index.
- `figures/make_concept_figures.py`: the layers picture reads each layer's status from `sources/register.csv`.
- `figures/make_illustrations.py`: Stage 4 done, Stage 5 next, so the journey map and `docs/interactive/journey.html` move on.
- `README.md`: layer statuses, version and build status, the Phase 2 result, the repository map with `sources/` and the new files, the tutorial table and the run commands.
- `docs/ROADMAP.md`: Phase 2 done, with what it built and taught; status line, checklist and risks updated.
- `docs/GLOSSARY.md`: new terms (DNA sequence, genome assembly, contig, GC content, box, reference community, the TRUE, FALSE and TBD marks, SHA-256, pinning, file signature, NCBI, RefSeq, accession, BioProject, FASTA, gzip, mirror, rate limit, publisher's terms), and prevalence, controls and the three rounds corrected with the real numbers.
- `docs/00-architecture.md`: the source register in Box 1, `data/raw/sources/` and the three kinds of check in Box 2, `sources/` in the folder map.
- `docs/PRODUCT_ROADMAP.md`: the terms of each layer, and what they mean for a product.
- `docs/index.html`: a card for the communities page, and two of the new pictures.
- `docs/02-phase-1-data-acquisition.md`: its pointers to Phase 2 now say what Phase 2 found, and a sentence about reading names from the manifest, which no longer described what the code does, is replaced.

### Fixed (found on the first run on a Mac)

- `pip install -r requirements.txt` stopped at `dbt-core-experimental-parser` with `CERTIFICATE_VERIFY_FAILED` on a Mac with Python from python.org: that package downloads its real file from GitHub during the install, and that Python trusts no certificate until its `Install Certificates.command` has run. `docs/01-setup.md` now has the step right after installing Python, and a troubleshooting entry; `docs/04-phase-3-harmonisation.md` has it in the mini-FAQ and the notes from the build; the Handbook has a row for it, and the Glossary explains certificates.
- `docs/04-phase-3-harmonisation.md`: the expected outputs of the environment check, `dbt debug`, `dbt build`, the failing test and `pytest` are now the ones from the Mac, with the partial-parsing line of a first build; `dbt docs serve` shows its real output, and what it prints when stopped with Ctrl+C.

## [0.1.0] - 2026-10-12

Phase 1: the verified download of the published dataset ([`docs/02-phase-1-data-acquisition.md`](docs/02-phase-1-data-acquisition.md)), and the documentation brought up to the standard the rest of the project will follow.

**Result.** The archive (239,154,876 bytes) downloads from Zenodo and matches its published MD5 checksum, `f8061f230b621703f0f11be454c5167e`. It unpacks into 342 files (368 entries, 26 of them folders; no macOS clutter, nothing unsafe): 53 data files the authors started from, 183 that their code wrote, 22 R scripts and 76 figure PDFs. 19 tests pass.

### Added

- `docs/HANDBOOK.md`: one document for the whole journey, from understanding the project (Stage 0) through the 18 phases (Stages 3 to 20) to the product (Stage 21). Each stage says what you do, why, which guide holds the detail, how you know it worked, and the commit message that saves it. Also: every command in order, what to do every session, a troubleshooting table, an index of every file and where it's explained, and the rules for keeping the Handbook up to date.
- `check-public-safe.sh`: the safety gate, run before every push. It checks the tracked files and the new ones `git add -A` would add, and refuses the all-clear for environments, downloaded data, private notes, `.env` files, secret and database file types, credential-shaped text, paths from one particular computer, operating-system clutter such as `.DS_Store`, and pictures carrying hidden records (GPS positions or content credentials). It also lists large files and occurrences of the author's name and handle for information.
- `notebooks/explore_raw.py`: a summary of the downloaded archive from `data/raw/manifest.csv` (files by type, files per folder, files that probably hold tables, the authors' R code).
- Tests, 19 in all, with `pytest.ini`:
  - `tests/test_fetch_data.py` (9): the download script, offline, against a tiny stand-in archive with two traps in it (an entry that would land outside its folder, and macOS clutter): sizes, the zip-slip guard, the checksum, unpacking, the inventory, a second run that checks instead of downloading, a wrong checksum stopping the run before anything is unpacked, and output free of home-folder paths and look-alike characters.
  - `tests/test_safety_gate.py` (7): the gate passes a clean repository and refuses a fake key, force-added data, a home-folder path, a tracked `.DS_Store` and a picture with a hidden record, while accepting `/Users/<you>/` placeholders. Skipped where bash or Git isn't available, and on Windows unless pytest is started from Git Bash.
  - `tests/test_docs.py` (3): every link and `#anchor` between the documents resolves, no file holds long dashes or curly quotes, and the Handbook's stage table agrees with the journey map.
- `figures/make_concept_figures.py`, drawing six pictures that explain ideas without needing the data: `figures/combinations.png` (every five-strain community from 35 strains, and the 206 tested), `figures/screening_design.png` (the experiment as a 5-a-side league), `figures/three_way.png` (the paper, the original R code and the rebuild), `figures/data_layers.png` (five layers from four sources), `figures/fetch_pipeline.png` (Phase 1 in six steps) and `figures/log_scale.png` (why bacterial counts are read on a log scale); and `docs/interactive/combinations.html`, the same arithmetic with sliders.
- `figures/make_illustrations.py`, drawing the logo, icon and wordmark (`docs/img/realsignal_logo.svg`, `docs/img/realsignal_icon.svg`, `docs/img/realsignal_wordmark.svg`), the journey map `docs/img/journey_map.svg`, and `docs/interactive/journey.html`, the Handbook's stages as a page to click, built from the Handbook itself.
- `docs/index.html` and `docs/.nojekyll`: the front page of an optional GitHub Pages site for the interactive pages.
- `docs/PRODUCT_ROADMAP.md`: what a larger RealSignal would add, with a verdict and a trigger for each technology, and what changes when the method is reused on another strain library.
- `CHANGELOG.md`: this file.

### Changed

- `scripts/fetch_data.py`: a `--probe` step that asks Zenodo about the file without downloading it; the download goes to a `.part` file renamed only when complete; a checksum mismatch stops the run before anything is unpacked; unpacking skips macOS clutter and refuses entries that would land outside their folder; a second run checks the archive instead of downloading it again; `data/raw/manifest.csv` lists every file and `data/raw/fetch_log.json` records where the data came from, keeping the download date (`downloaded_at_utc`) when a later run only checks (`last_verified_utc`). Sizes are in decimal megabytes, as on the Zenodo record page, so "239.2 MB" means the same in both places. Output uses plain characters and paths from the project folder, so it's the same on every computer and safe to quote.
- `scripts/check_env.py`: plain characters, the Python in use shown relative to the project folder, and a pointer to the Handbook at the end.
- `docs/01-setup.md`: rewritten in 17 sections, with the safety gate (section 13), copying commands safely (section 14) and setting up a second computer (section 16) added, every step for Windows, macOS and RHEL 8, and the expected output after every command. On a Mac using the zsh shell, a one-time setting (section 2) so the notes after `#` in pasted command blocks are skipped instead of read as commands; the bash shell needs nothing.
- The end-of-phase ritual, everywhere it appears: the tests and the safety gate are now a block of their own, run and read before the save block, because a pasted block carries on after a failing line.
- `docs/02-phase-1-data-acquisition.md`: rewritten in 17 sections to match the new script, with the science of the experiment, the tests, notes from the build, the same checksum in four tools, a mini-FAQ and the save block.
- `README.md`: the logo and journey map, a pointer to the Handbook, five data layers from four sources (the counts checked against the papers), the build status with every phase and its version tag, a results table that fills in phase by phase, and an annotated map of every file.
- `docs/ROADMAP.md`: the version tags now run from v0.1.0 at Phase 1 to v1.0.0 at Phase 18 (before, the phase list said v1.0.0 at Phase 18 while the milestone table ran to v1.4.0); a "What finished means" checklist; Phase 7 includes putting the app online; Phase 9 adds the data-efficiency curve; Phase 12 retrains on new results; Phase 18 lists the release work; the Phase 6 guide name fixed; effort 174 hours.
- `docs/00-architecture.md`, `docs/CONTAINERS.md`, `docs/GIT_WORKFLOW.md` and `docs/GLOSSARY.md`: rewritten in plain characters, checked against the new plan, with the Git workflow gaining a section on tags and version numbers.
- `.gitignore`: now the same, line for line, as the block in `docs/01-setup.md` section 11.
- `setup.sh` and `setup.ps1`: also look for Python 3.14, print plain characters, point to the Handbook when done; the Windows script writes the lock file as plain ASCII.
- `requirements.txt`: comments explain the version ranges and use `python -m pip`.
- `src/realsignal/__init__.py`: a docstring saying what the package is for.

### Fixed (found on the first real run, on a Mac)

- `check-public-safe.sh`: the check for credential-shaped text found nothing on macOS, where one of the tests failed. The pattern no longer uses `{20,}` or `^` inside a group, which regex engines treat differently from system to system; it writes the twenty characters out and lets Git test word boundaries (`git grep -w`). A test checks that a link anchor such as `#task-...` isn't taken for a key.
- `scripts/fetch_data.py`: a second run, which skips unpacking, wrote `null` over the macOS-clutter and unsafe-entry counts in `data/raw/fetch_log.json`; it now keeps the numbers from the run that unpacked. The lines under DONE are shorter, so an 80-character terminal no longer wraps them.
- `notebooks/explore_raw.py`: files per folder counts folders only (the R scripts no longer appear one by one), data files are split into what the authors started from (`Data/`) and what their code wrote (`Output/`), and the lists line up on the left.

### Removed

- `.DS_Store` and `src/.DS_Store` from Git. They reached the repository in its second commit, and the safety gate found them. They stay on disk, and `.gitignore` keeps them out from now on.

## Earlier history

Before this changelog existed, the project had three commits, all on 2026-08-28:

| Commit | What it did |
|---|---|
| `chore: initial project structure, documentation and environment` | the folder structure, the first README, architecture guide, Git workflow and glossary, the environment check, and the package lists |
| `docs: architecture overview and roadmap` | the architecture guide and roadmap rewritten; the setup guide, the Phase 1 guide and its download script, the containers guide, the setup scripts and the licence added (and, by accident, the two `.DS_Store` files) |
| `docs: add the R reproduction phase and the generalisable problem` | Phase 6 (the authors' R code and the three-way comparison) in the plan, the `R/` folder, and the README section on the part that generalises |
