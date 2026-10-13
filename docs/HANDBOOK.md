[README](../README.md) · [Glossary](GLOSSARY.md) · [Architecture](00-architecture.md) · [Roadmap](ROADMAP.md) · [Product roadmap](PRODUCT_ROADMAP.md) · [Changelog](../CHANGELOG.md)

# The RealSignal Handbook: from day 0 to the finished product

**Handbook revision:** 5 · **Last updated:** 2026-10-13 · **Repository state it describes:** Stages 0 to 6 are done: the plan, the setup on a blank computer, the repository with its three branches and the safety gate, Phase 1 (the published dataset downloaded and verified, version v0.1.0), Phase 2 (Layer 1's tables read, and the other four layers fetched and checked, with a source register that records each one), Phase 3 (every source loaded into one DuckDB warehouse and harmonised with dbt, with the three Layer 1 choices made and 187 data tests, version v0.2.0) and Phase 4 (the harmonised data explored with the test set sealed: seven questions, five pictures and a data-quality report one script rebuilds). Stage 7, Phase 5, is next. 65 automated tests.

**Read this document first, and come back to it whenever you wonder what to do next.** It walks the whole journey in order: understanding the project, preparing a blank computer, building each of the 18 phases, releasing version 1.0, and what lies beyond. At every step it explains *why*, and it links to the guide that holds the detail. If you ever have to hunt through the repository to find your next step, the Handbook has a gap, and that counts as a bug.

**Who it's for.** Someone with no background in microbiology, statistics, programming, Git or the command line, who wants to end up able to build, run, explain and extend RealSignal. Every term used anywhere in the repository is defined in plain language in the [Glossary](GLOSSARY.md). Keep it open in a second browser tab.

**How to use it.** Stages are numbered and follow each other. Each one says what you'll do, why it exists, which guide to open, roughly how long it takes, how you know you're done (the *Checkpoint*) and the commit message that saves the work. **Don't move on until the checkpoint is met.** Every stage ends at a natural stopping point, with your work safely on GitHub.

**Paths.** Every file is named by its path from the project folder (the folder that holds `README.md`), for example `scripts/fetch_data.py` or `docs/01-setup.md`. Files that sit in the project folder itself (`README.md`, `CHANGELOG.md`, `check-public-safe.sh`) have no folder in front of them.

**Every stage has the same parts:** *What* (what you do, with the commands), *Why* (the reason it exists), a *Checkpoint* (how you know it worked, with real numbers once the stage is built) and the *commit message* that saves it. Stages that haven't been built yet say *planned* next to those words. The phase guides hold every step with its expected output; the Handbook is the thread that ties them together. [The whole build, command by command](#the-whole-build-command-by-command) lists every command in order on one page.

### Short on time?

Three things give you the project in twenty minutes, with nothing installed:

1. The README sections [What is a plant microbiome?](../README.md#what-is-a-plant-microbiome-start-here) and [The problem this project tackles](../README.md#the-problem-this-project-tackles).
2. The picture of the experiment, [`figures/screening_design.png`](../figures/screening_design.png), and of the plan, [`docs/img/journey_map.svg`](img/journey_map.svg).
3. The interactive page [`docs/interactive/combinations.html`](interactive/combinations.html), which shows why nobody tests every possible community. Download it and open it in a browser; it works offline. (Once GitHub Pages is switched on, Stage 3 step 6, the interactive pages also open from a link.)

![The screen: a pool of strains, random teams, plants and pathogen, then working backwards](../figures/screening_design.png)

---

## The journey at a glance

![The RealSignal journey, from a blank laptop to a finished product](img/journey_map.svg)

*Would you rather click? [`docs/interactive/journey.html`](interactive/journey.html) is the same journey as a page: pick any stage to read what you do, why, and how you know it worked. `figures/make_illustrations.py` builds it from this Handbook, so the two always say the same thing. Download it and open it in a browser; it works offline.*

```mermaid
flowchart TB
    subgraph FOUND["Foundations: once per machine"]
        direction LR
        S0["0 · Understand"] --> S1["1 · Set up"] --> S2["2 · Version control"]
    end
    subgraph DATA["Data: Phases 1 to 4"]
        direction LR
        S3["3 · Real data"] --> S4["4 · More sources"] --> S5["5 · Harmonise"] --> S6["6 · Explore"]
    end
    subgraph SCIENCE["Science: Phases 5 to 9"]
        direction LR
        S7["7 · Reproduce"] --> S8["8 · Original R code"] --> S9["9 · Prototype app"] --> S10["10 · Multi-omics"] --> S11["11 · Validate"]
    end
    subgraph PLATFORM["Platform: Phases 10 to 12"]
        direction LR
        S12["12 · Database + API"] --> S13["13 · React frontend"] --> S14["14 · Orchestrate"]
    end
    subgraph AI["AI layer: Phases 13 to 16"]
        direction LR
        S15["15 · Knowledge graph"] --> S16["16 · GraphRAG"] --> S17["17 · MCP server"] --> S18["18 · Agent"]
    end
    subgraph RELEASE["Release: Phases 17 and 18, and beyond"]
        direction LR
        S19["19 · Containers"] --> S20["20 · Release 1.0"] --> S21["21 · The product"]
    end
    FOUND --> DATA --> SCIENCE --> PLATFORM --> AI --> RELEASE

    classDef done fill:#E6F4EA,stroke:#4CAF7D,color:#0B3D2E;
    classDef next fill:#FFF3CD,stroke:#C9A227,color:#4A3B00;
    classDef later fill:#F5F5F5,stroke:#B0B0B0,color:#555555,stroke-dasharray:4 3;
    class S0,S1,S2,S3,S4,S5,S6 done
    class S7 next
    class S8,S9,S10,S11,S12,S13,S14,S15,S16,S17,S18,S19,S20,S21 later
```

*Green: built and tested. Gold: in progress. Dashed grey: planned.* The Prototype app (Stage 9) sits inside the science group on purpose: a first clickable version halfway through the science keeps asking "who would use this, and for what?" while there's still time to act on the answer.

| Stage | Area | What you do | Guide | Hands-on time | Status |
|---|---|---|---|---|---|
| 0 | Orientation | Understand what you are building and why | [README](../README.md), [Architecture](00-architecture.md), [Roadmap](ROADMAP.md) | 1-2 h reading | ✅ done |
| 1 | Setup | Set up your workshop (once per machine) | [`docs/01-setup.md`](01-setup.md) sections 1 to 11 | 60-90 min | ✅ done |
| 2 | Git | Version control, the three branches and the safety gate | [`docs/01-setup.md`](01-setup.md) sections 12 to 14, [`docs/GIT_WORKFLOW.md`](GIT_WORKFLOW.md) | 30-45 min | ✅ done |
| 3 | Data | Phase 1: get the real data, verified | [`docs/02-phase-1-data-acquisition.md`](02-phase-1-data-acquisition.md) | about 1 h | ✅ done |
| 4 | Data | Phase 2: the other four layers, or a record of why not | [`docs/03-phase-2-more-sources.md`](03-phase-2-more-sources.md) | about 1.5 h | ✅ done |
| 5 | Data | Phase 3: harmonise everything with dbt | [`docs/04-phase-3-harmonisation.md`](04-phase-3-harmonisation.md) | 2-3 h | ✅ done |
| 6 | Data | Phase 4: explore the data | [`docs/05-phase-4-exploration.md`](05-phase-4-exploration.md) | about 1.5 h | ✅ done |
| 7 | Science | Phase 5: reproduce the published models in Python | `docs/06-phase-5-reproduction.md` | ~12 h | ⏳ next |
| 8 | Science | Phase 6: run the authors' R code, the three-way comparison | `docs/07-phase-6-original-r-code.md` | ~8 h | ⬜ planned |
| 9 | Product | Phase 7: the prototype app, online | `docs/08-phase-7-prototype-app.md` | ~10 h | ⬜ planned |
| 10 | Science | Phase 8: multi-omics integration | `docs/09-phase-8-multi-omics.md` | ~12 h | ⬜ planned |
| 11 | Science | Phase 9: external validation and the data-efficiency curve | `docs/10-phase-9-validation.md` | ~10 h | ⬜ planned |
| 12 | Platform | Phase 10: PostgreSQL and FastAPI, the first container | `docs/11-phase-10-database-api.md` | ~12 h | ⬜ planned |
| 13 | Platform | Phase 11: the React and TypeScript frontend | `docs/12-phase-11-react-frontend.md` | ~16 h | ⬜ planned |
| 14 | Platform | Phase 12: orchestration with Airflow | `docs/13-phase-12-orchestration.md` | ~10 h | ⬜ planned |
| 15 | AI | Phase 13: the knowledge graph and its ontology | `docs/14-phase-13-knowledge-graph.md` | ~12 h | ⬜ planned |
| 16 | AI | Phase 14: GraphRAG, answers with sources | `docs/15-phase-14-graphrag.md` | ~10 h | ⬜ planned |
| 17 | AI | Phase 15: the MCP server | `docs/16-phase-15-mcp-server.md` | ~6 h | ⬜ planned |
| 18 | AI | Phase 16: the recommendation agent | `docs/17-phase-16-agent.md` | ~8 h | ⬜ planned |
| 19 | Release | Phase 17: the whole system in containers, Docker or Podman | `docs/18-phase-17-containers.md`, [`docs/CONTAINERS.md`](CONTAINERS.md) | ~12 h | ⬜ planned |
| 20 | Release | Phase 18: tests on three systems, release 1.0 | `docs/19-phase-18-release.md` | ~8 h | ⬜ planned |
| 21 | Product | Beyond the repository: the product | [`docs/PRODUCT_ROADMAP.md`](PRODUCT_ROADMAP.md) | reading | ⬜ planned |

Guide names in plain text (not links) are the files each phase will add; they don't exist yet. For built stages, the time is what following the guide takes; for planned stages it's my estimate for building and documenting the phase, which takes far longer than following it later. At four to five hours a week, the whole journey is eight to ten months of evenings and weekends, and [`docs/ROADMAP.md`](ROADMAP.md#5-effort-and-schedule) explains where that estimate comes from.

---

## Stage 0: Understand what you are building and why

**What.** Read, in this order:

1. The [README](../README.md), up to and including *How it works*. It explains, without any biology background, what a plant's microbiome is, why some bacteria protect plants, and why choosing which ones to test is a data problem.
2. [`docs/00-architecture.md`](00-architecture.md): every part of the finished system, what it does and why it exists, including the three words most software leans on (frontend, backend, database).
3. [`docs/ROADMAP.md`](ROADMAP.md): the 18 phases, the order they come in, and the tools left out on purpose.

**Why.** Everything you type later only makes sense if you can say in one sentence what RealSignal is for: *rebuilding a published machine-learning result about plant-protecting bacteria, checking it against evidence the model never saw, and turning it into a tool that helps choose which experiments are worth running.* With that sentence in mind, each command has a reason you can follow.

**Checkpoint.** Without notes, you can explain to a friend: what a strain is; what the 136 random five-strain communities were for (the [screening picture](../figures/screening_design.png) helps); the difference between reproducing and replicating a study; why the original R code gets run as well as rebuilt ([`figures/three_way.png`](../figures/three_way.png)); and why nobody tests every possible community ([`figures/combinations.png`](../figures/combinations.png)).

---

## Stage 1: Set up your workshop (once per machine)

**What.** Follow [`docs/01-setup.md`](01-setup.md) sections 1 to 11. Each step shows the exact command for Windows, macOS or RHEL 8 (and other Linux). **Do the one for your machine and skip the others.**

1. Open a terminal and learn the four commands that move you around (section 2).
2. Install Python 3.11 or newer, Git and VS Code (sections 3 to 5).
3. Create a GitHub account and an **empty** repository called `realsignal` (section 6).
4. Create the project folder, the virtual environment `.venv`, and install the packages from `requirements.txt` (sections 7 to 9).
5. Prove it works: `python scripts/check_env.py` (section 10).

On a Mac whose terminal prompt ends with `%` (the zsh shell), also switch on one setting so that notes after `#` in pasted commands are skipped (section 2, *macOS only*). A prompt ending with `$` (the bash shell) needs nothing.

**Why.** You install the language everything is written in (Python), the program that records every change (Git), a comfortable editor, an online home for the project (GitHub), and a sealed box of packages for this project only (the virtual environment). All of the setup sits at the front on purpose: after this stage, daily work is the same handful of short commands on every operating system.

**Platform promise.** The code builds every file path with Python's `pathlib`, so the same commands work on Windows, macOS and RHEL 8. Where an operating system really differs (installing Python, activating the environment, deleting a file), the guides show each version side by side.

**Checkpoint.** Your terminal prompt shows `(.venv)`, and `python scripts/check_env.py` ends with `ALL CHECKS PASSED. Your workshop is ready.` On the MacBook Pro this project was built on, that was Python 3.14 with pandas 3.0.5, scikit-learn 1.9.0 and DuckDB 1.5.5.

---

## Stage 2: Version control, the three branches and the safety gate

**What.** [`docs/01-setup.md`](01-setup.md) sections 12 to 14, with [`docs/GIT_WORKFLOW.md`](GIT_WORKFLOW.md) for the full explanation.

1. Turn the folder into a Git repository, connect it to GitHub, and create the branches `master`, `beta` and `develop` (section 12).
2. Meet the safety gate, `check-public-safe.sh`, which runs before every push (section 13).
3. Learn why commands must be typed with plain keyboard characters (section 14).

**Why.** Git records every change, so nothing is ever lost and every step can be looked at later. The three branches give the work a steady rhythm:

```mermaid
%%{init: {'gitGraph': {'mainBranchName': 'master'}}}%%
gitGraph
    commit id: "setup"
    branch beta
    branch develop
    checkout develop
    commit id: "phase work"
    commit id: "tests pass"
    checkout beta
    merge develop id: "same commit"
    checkout master
    merge develop id: "published"
```

(The picture draws the updates as merges. In practice one push moves `beta` and `master` forward to the very same commit as `develop`, which Git calls a *fast-forward*.) You only ever work on **`develop`**. One push line updates all three branches on GitHub, and then your own copy of `master` is brought in step. The safety gate runs before that, every time: it refuses to give the all-clear if a secret, downloaded data, a private note, a database file, a path from your own computer, a macOS `.DS_Store` file or a picture carrying hidden records is about to become public. It checks the files Git already tracks **and** the new files `git add -A` is about to add, so you can run it before staging.

> **Copy commands safely.** Every command, commit message and tag message in this repository uses plain keyboard characters. Look-alike characters from word processors and web pages (a long dash, curly quotes) can break a command when pasted into a terminal. [`docs/01-setup.md` section 14](01-setup.md#14-copy-commands-safely) has the details.

**The end-of-phase ritual**, used at the end of every stage from here on. Each stage names its own commit message. First check, and read the result; stop if either fails:

```bash
pytest -q                     # all tests pass
./check-public-safe.sh        # must end with: SAFE TO PUSH (Windows: bash check-public-safe.sh in Git Bash)
```

Then save:

```bash
git switch develop
git add -A
git commit -m "<the stage's commit message>"
git push origin develop develop:beta develop:master
## --tags is optional, only when required (the stage says when it earns a version tag)
## then switch back to local master and pull in the remote changes
git switch master
git pull --ff-only origin master
git switch develop
```

The checks are a block of their own because a pasted block runs every line even after one fails, so a failing test inside it wouldn't stop the push.

**Checkpoint.** `git branch -a` lists `master`, `beta` and `develop`, and the same three under `remotes/origin/`. `./check-public-safe.sh` ends with `SAFE TO PUSH`. Your README shows on the repository's page on GitHub.
**Commit messages used:** `chore: initial project structure, documentation and environment` · `docs: architecture overview and roadmap` · `docs: add the R reproduction phase and the generalisable problem`. (In this repository's own history the gate arrived with Stage 3's commit; if you're following along from scratch, you have it from the start.)

---

## Stage 3: Phase 1, get the real data, verified

**What.** Follow [`docs/02-phase-1-data-acquisition.md`](02-phase-1-data-acquisition.md).

1. Read the guide's sections 1 to 4 first: the study, the experiment, and three ideas (checksums, read-only raw data, provenance).
2. Look before you leap: `python scripts/fetch_data.py --probe` asks Zenodo about the file without downloading it.
3. Download, verify, unpack and list: `python scripts/fetch_data.py` (about 239 MB, several minutes).
4. Run the same command again and watch it check the copy instead of downloading it twice.
5. Look at what arrived: `python notebooks/explore_raw.py`, and write down which files hold the communities, the outcomes and the authors' R code.
6. Optional: switch on GitHub Pages so the interactive pages open from a link (the guide's section 9).

![Phase 1 in six steps](../figures/fetch_pipeline.png)

**Why.** Getting data is where many projects go quietly wrong: a download stops at 94 % and still opens, a spreadsheet gets "fixed" by hand and the original is lost, and a year later nobody knows where a number came from. Phase 1 builds three habits that prevent all three. It verifies the download against the checksum the authors published, so you hold exactly their bytes. It never edits the raw copy. And it writes down where the data came from, automatically. It also finds out what is actually in the archive before any code assumes it, because Phase 2 reads files by their real names.

**Checkpoint.** The probe reports `Server reports: 239.2 MB` and `Reachable     : yes`. The download ends with `MATCH. This is the published archive, byte for byte.` (the MD5 checksum is `f8061f230b621703f0f11be454c5167e`); the archive holds 368 entries, of which 342 are files, with no macOS clutter and nothing unsafe. A second run says `The archive is already here` and checks it again without downloading. `data/raw/manifest.csv` lists the 342 files and `data/raw/fetch_log.json` records the download (239,154,876 bytes). `python notebooks/explore_raw.py` finds 53 data files the authors started from (in `Data/`), 183 their code wrote (in `Output/`) and 22 R scripts (in `Rscripts/`). `pytest -q` passes 19 tests (run from Windows PowerShell, 12 pass and the 7 safety-gate tests are skipped, because they need Git Bash). `git status` shows nothing from `data/`.
**Save it.** This stage completes **v0.1.0**, the first version. Two one-off steps come first, because this is the commit that adds the safety gate: take the two `.DS_Store` files that reached an early commit out of Git (they stay on your disk), and record the gate and the setup script as runnable.

```bash
git switch develop
git rm --cached --ignore-unmatch .DS_Store src/.DS_Store
chmod +x check-public-safe.sh setup.sh   # Windows PowerShell: git update-index --chmod=+x check-public-safe.sh setup.sh
```

Then check, and stop if either fails:

```bash
pytest -q                                # 19 passed
./check-public-safe.sh                   # must end with: SAFE TO PUSH
```

Then save:

```bash
git switch develop
git add -A
git commit -m "feat: verified download of the published dataset, Handbook, safety gate and illustrations"
git push origin develop develop:beta develop:master
## --tags is optional, only when required: this stage completes v0.1.0
git tag -a v0.1.0 -m "v0.1.0: verified data, documentation and a reproducible setup"
git push origin develop develop:beta develop:master --tags
## then switch back to local master and pull in the remote changes
git switch master
git pull --ff-only origin master
git switch develop
```

---

## Stage 4: Phase 2, the other four layers (or a record of why not)

**What.** Follow [`docs/03-phase-2-more-sources.md`](03-phase-2-more-sources.md).

1. Read the guide's sections 1 to 4: the five layers and the papers behind them, the difference between free to read and free to reuse, and three ways to trust a download.
2. Open Layer 1's tables: `python notebooks/explore_layer1.py`. It answers the question Phase 1 left open (where the 70 test communities are) and shows which plants were set aside and why.
3. Read the source register: `python scripts/fetch_sources.py --list`.
4. Check every file can be reached, downloading nothing: `python scripts/fetch_sources.py --probe`.
5. Fetch and check everything: `python scripts/fetch_sources.py`. Run it a second time and watch it check instead of downloading.
6. See how the outcome is recorded: `python scripts/fetch_sources.py --pin`. The repository already holds the pins and statuses from the first run, so after a fetch without failures it finds nothing new to record.
7. Look at what arrived: `python notebooks/explore_sources.py`.
8. Draw the pictures and the interactive page: `python figures/make_phase2_figures.py`.

![Three ways to trust a download](../figures/three_checks.png)

**Why.** One dataset answers one question. The other layers add *why* (the chemistry a strain could make), *how* (which strains hold each other back) and an independent check (each strain measured alone), as [`figures/data_layers.png`](../figures/data_layers.png) shows. They come from three more papers, on two kinds of website, under different terms, and only some of them publish a checksum. So this stage keeps a register of every source, including any that can't be had, checks each download as well as its source allows, and stores no data file in the repository. It starts with Layer 1 because code can only be written against tables once you know what they hold.

**Checkpoint.** `python notebooks/explore_layer1.py` finds 136 training communities (rounds 1 and 2), 68 new test communities in round 3 plus `Mix69` and `Mix70`, grown in every round, and rebuilds the authors' per-plant machine-learning tables from the plant file: 808 plants, the same ones, including 120 undecided (`TBD`) plants. The probe reaches all 36 files. The fetch (48.5 MB) ends with `Match a published MD5  : 34`, `Match a pinned SHA-256 : 2` and `Failed or mismatched   : 0`: every genome matches the MD5 that NCBI publishes, and both journal workbooks match their pins. Layer 5's workbook isn't byte for byte the same as the copy in the Phase 1 archive, but every cell of its 14 sheets holds the same value. `--list` shows all four sources as `fetched`, and `--pin` finds nothing new to record. `python notebooks/explore_sources.py` describes the two workbooks (26 and 14 sheets) and the 34 genomes (2.94 to 6.85 million letters, GC content 33.4 to 74.2 %). `pytest -q` passes 36 tests (29 passed and 7 skipped from Windows PowerShell). `git status` shows nothing under `data/`.
**Save it.** No version tag this time: v0.2.0 comes with Phase 3. Check first, and stop if either fails:

```bash
pytest -q                                # 36 passed
./check-public-safe.sh                   # must end with: SAFE TO PUSH
```

Then save:

```bash
git switch develop
git add -A
git commit -m "feat: add the source register and fetchers for the remaining data layers"
git push origin develop develop:beta develop:master
## --tags is optional, only when required: not this time, v0.2.0 comes with Phase 3
## then switch back to local master and pull in the remote changes
git switch master
git pull --ff-only origin master
git switch develop
```

---

## Stage 5: Phase 3, harmonise everything with dbt

**What.** Follow [`docs/04-phase-3-harmonisation.md`](04-phase-3-harmonisation.md).

1. Read the guide's sections 1 to 4: what harmonising means and why the data is loaded before it's transformed (ELT), dbt from zero, one strain name and one community name, and the files.
2. Install dbt Core and its DuckDB adapter, and check the workshop: `python -m pip install -r requirements.txt`, then `python scripts/check_env.py`.
3. Load every raw table into the warehouse, unchanged: `python scripts/load_raw.py --list`, then `python scripts/load_raw.py`.
4. Go into `dbt/` (`cd dbt`), check the connection with `dbt debug`, read the three Layer 1 choices (the guide's section 8), then build and test everything: `dbt build`.
5. Write your first SQL query with `dbt show`, then from the project folder: `python notebooks/explore_warehouse.py`.
6. Draw the pictures (`python figures/make_phase3_figures.py`) and open dbt's own documentation pages (`dbt docs generate`, then `dbt docs serve`, inside `dbt/`).
7. Change a choice and break a test on purpose (the guide's section 12), then rebuild with a plain `dbt build`.

![Which plants the models will see](../figures/plant_choices.png)

**Why.** Sources written by different laboratories years apart spell the same strain differently and shape their tables differently. Making them agree is usually the biggest single job in multi-source work, and doing it in dbt keeps every decision visible and tested instead of buried in a script. The three choices Phase 2 left open (the undecided plants, the two communities grown in every round, the two communities with no plants left) are made here, each with its reason and a test, and the one a reader may want to change is a setting. One rule is set here because it's free now and expensive later: nothing hard-codes 35 strains, five per community, one pathogen or one measurement. A test runs the whole pipeline on a made-up screen of four strains in communities of two to show it.

**Checkpoint.** `python scripts/check_env.py` lists twelve packages, `dbt-core` and `dbt-duckdb` among them. `python scripts/load_raw.py` loads 20 tables (13,908 rows) into `data/warehouse/realsignal.duckdb`. Inside `dbt/`, `dbt debug` ends with `All checks passed!` and `dbt build` with `Done. PASS=223 WARN=0 ERROR=0` (35 models, 1 seed and 187 data tests). `python notebooks/explore_warehouse.py` reports 285 strains (35 in the screen, 34 of them with a genome), 136 training and 70 test communities (134 and 70 with plants for modelling), and 808 plants for modelling, 120 of them `TBD`: the same plants as the authors' table. The tests located the three gene clusters on which Tables S9 and S11 disagree (one each for Leaf61, Leaf130 and Leaf182), record Leaf168, Leaf371 and Leaf454 as screened with no inhibition seen, and confirm that all 191 gene clusters of the 34 strains with a genome sit inside their contigs. `python figures/make_phase3_figures.py` draws three pictures. `pytest -q` passes 54 tests (47 passed and 7 skipped from Windows PowerShell). `git status` shows nothing under `data/` or `dbt/target/`.
**Save it.** This stage completes **v0.2.0**, and the changelog's `[Unreleased]` entry for Phase 2 moves under `[0.2.0]` with it. The pictures first, then the checks; stop if either check fails:

```bash
python figures/make_phase3_figures.py    # the guides link to these pictures
pytest -q                                # 54 passed
./check-public-safe.sh                   # must end with: SAFE TO PUSH
```

Then save:

```bash
git switch develop
git add -A
git commit -m "feat: harmonise all sources with dbt models and data tests"
git push origin develop develop:beta develop:master
## --tags is optional, only when required: this stage completes v0.2.0
git tag -a v0.2.0 -m "v0.2.0: every source harmonised in a tested dbt project"
git push origin develop develop:beta develop:master --tags
## then switch back to local master and pull in the remote changes
git switch master
git pull --ff-only origin master
git switch develop
```

---

## Stage 6: Phase 4, explore the data

**What.** Follow [`docs/05-phase-4-exploration.md`](05-phase-4-exploration.md).

1. Read the guide's section 1: what exploring means, the seven questions, and why the test set stays sealed (test plants are counted, but their values are never read).
2. Run the explorer: `python notebooks/explore_marts.py`. Then read its answers with the guide's sections 4 to 10, one question at a time: the shape of the outcome, the rounds, the design, missing values and outliers, plant-to-plant noise, one strain at a time, and how the other layers relate.
3. Draw the pictures: `python figures/make_phase4_figures.py`.
4. Write the data-quality report, twice: `python scripts/make_quality_report.py`. The second run says `unchanged`.
5. Read what it all means for Phase 5 (the guide's section 13).
6. Try the two experiments of the guide's section 14: the authors' normalised outcome, and a broken seal the tests catch. Then a plain `dbt build` inside `dbt/`.

![The outcome on an ordinary scale and on a log scale](../figures/outcome_shape.png)

**Why.** Looking comes before modelling. A problem spotted in a histogram costs minutes; the same problem found after training a model costs days, because by then it looks like a modelling bug. This stage also shows why bacterial counts are read on a log scale ([`figures/log_scale.png`](../figures/log_scale.png)), how controls grown in every round reveal differences between rounds, and how a difference found by looking at 35 strains is checked against what chance alone gives. It keeps every test plant's values out of every choice, so the single score Phase 5 gets on the 70 test communities still means something.

**Checkpoint.** `python notebooks/explore_marts.py` describes 531 training plants in 134 communities, with two humps near 4.91 and 7.81 and the dip between them at 5.71; it finds the reference and whole-library plants about one log unit higher in round 2 than in round 1 while the plants with no strains stay near 9.0; it works out the authors' normalised pathogen value from the numbers alone (`655 of 655 plants match`); it reports no missing values among the 808 plants used for modelling, 22 outliers listed and kept, a share of 0.69 of the variation between communities, and `standing out: Leaf76, Leaf68, Leaf15`. `python figures/make_phase4_figures.py` draws five pictures. `python scripts/make_quality_report.py` writes `docs/reports/data-quality.md`, and a second run says `unchanged`. `pytest -q` passes 65 tests (58 passed and 7 skipped from Windows PowerShell).
**Save it.** No version tag this time: v0.3.0 comes with Phase 5. The pictures and the report first, then the checks; stop if either check fails:

```bash
python figures/make_phase4_figures.py    # the guides link to these pictures
python scripts/make_quality_report.py    # and to this report
pytest -q                                # 65 passed
./check-public-safe.sh                   # must end with: SAFE TO PUSH
```

Then save:

```bash
git switch develop
git add -A
git commit -m "feat: explore the harmonised data, first figures and a data-quality report"
git push origin develop develop:beta develop:master
## --tags is optional, only when required: not this time, v0.3.0 comes with Phase 5
## then switch back to local master and pull in the remote changes
git switch master
git pull --ff-only origin master
git switch develop
```

---

## Stage 7: Phase 5, reproduce the published models in Python

**What (planned).** `docs/06-phase-5-reproduction.md`. Random forests and elastic nets, for both classification (protected or not) and regression (how much pathogen), with repeated cross-validation over several random seeds, scored once on the 70 test communities the models never saw. Every run is recorded with MLflow. Then the comparison table: these numbers next to the published ones. It takes Phase 4's findings with it ([`docs/05-phase-4-exploration.md` section 13](05-phase-4-exploration.md#13-what-this-means-for-phase-5)): errors reported by round where possible, community means scored as well as single plants, and a check that no conclusion depends on the 22 plants listed as outliers.

**Why.** This is the reproduction itself, written from the paper alone. Its evaluation guards against the usual ways a model fools its maker: a held-out test set from a separate experiment, cross-validation that keeps all plants of one community together, a baseline for every score, and results across several seeds instead of the best one.

**Checkpoint (planned).** The comparison table lists each published metric beside the rebuilt one; `pytest -q` includes a test that fails if plants of one community ever land on both sides of a split.
**Commit message (planned):** `feat: reproduce the published models in Python, with MLflow tracking`, tagged **v0.3.0**. **Commit this before opening any of the authors' R code**: that commit is the timestamped record that the rebuild was written independently.

---

## Stage 8: Phase 6, run the authors' R code, the three-way comparison

**What (planned).** `docs/07-phase-6-original-r-code.md`. Install R and RStudio, give the project its own R package library with `renv`, run the authors' original scripts from the archive (reading `data/raw/`, writing elsewhere), and put three results side by side.

![Three results, three comparisons](../figures/three_way.png)

**Why.** If the rebuild and the paper disagree, three different things could explain it: a mistake in the rebuild, the released code not reproducing its own paper, or a result that depends on the software used. With only two numbers you can't tell which. Running the original code adds the third number and pins the difference down. Someone else's research code often needs small fixes to run on a new computer; every fix is logged, and that log is part of the result.

**Checkpoint (planned).** The three-way table has a written explanation for every difference; `renv.lock` records the exact R packages.
**Commit message (planned):** `feat: run the original R analysis and add the three-way comparison`, tagged **v0.4.0**.

---

## Stage 9: Phase 7, the prototype app, online

**What (planned).** `docs/08-phase-7-prototype-app.md`. A Streamlit app: choose a community, see the predicted outcome with its uncertainty and which strains drove it, in plain words, with the model's limits stated on screen. Then put it online on Streamlit Community Cloud and the interactive figures on GitHub Pages.

**Why.** Until now, only someone who can run Python can see a result. A working tool at this point keeps the rest of the science grounded in what someone would actually do with it.

**Checkpoint (planned).** The app runs locally with one command and online from a link; every number it shows matches the tables from Stages 7 and 8.
**Commit message (planned):** `feat: add the Streamlit prototype and put it online`, tagged **v0.5.0**.

---

## Stage 10: Phase 8, multi-omics integration

**What (planned).** `docs/09-phase-8-multi-omics.md`. Add features from the genome, gene-cluster and network layers to the community data, and test whether they improve prediction over which strains are present.

**Why.** This is where the data layers earn their place: do the strains the model ranks highly carry more antibiotic-producing gene clusters, or hold back the pathogen's relatives? The original study found that strain identity alone predicted well, so the extra layers may add nothing. That would be a real result, and it gets reported as one.

**Checkpoint (planned).** A table compares models with and without each layer, all scored the same way, with intervals.
**Commit message (planned):** `feat: integrate the genomic and network layers and compare models by layer`.

---

## Stage 11: Phase 9, external validation and the data-efficiency curve

**What (planned).** `docs/10-phase-9-validation.md`. Compare the strain ranking the model learned from communities with each strain's protection measured alone in a separate published experiment. Then retrain on smaller and smaller random subsets of the 136 communities to see how many were needed to reach the same conclusion.

**Why.** The first check tests the conclusion against evidence the model never touched. (It's a separate experiment and dataset from the same research group, and the guide says so.) The second answers the first question anyone planning a screen like this asks: *how many communities do I need to test?* Each one costs weeks of glasshouse time.

**Checkpoint (planned).** A rank-agreement figure with its interval, the disagreements discussed one by one, and a curve of result stability against the number of communities.
**Commit message (planned):** `feat: validate against single-strain results and add the data-efficiency curve`, tagged **v0.6.0** (the science is complete).

---

## Stage 12: Phase 10, PostgreSQL and FastAPI, the first container

**What (planned).** `docs/11-phase-10-database-api.md`. PostgreSQL as the application's database, started in a container with Docker or Podman, and a FastAPI backend that serves predictions and data with automatic documentation.

**Why.** Analysis and applications need different kinds of database (the architecture guide explains the difference), and an API is the clean doorway between the model and anything that wants to use it. Containers make PostgreSQL one command on all three operating systems; [`docs/CONTAINERS.md`](CONTAINERS.md) explains them from zero, and why RHEL 8 uses Podman.

**Checkpoint (planned).** The API's documentation page opens in a browser; its tests pass; the database container starts the same way on macOS, Windows and RHEL 8.
**Commit message (planned):** `feat: add the PostgreSQL store and the FastAPI backend`.

---

## Stage 13: Phase 11, the React and TypeScript frontend

**What (planned).** `docs/12-phase-11-react-frontend.md`. A React app written in TypeScript that talks to the API: a community designer, prediction views and a network view. Streamlit stays as the quick internal tool.

**Why.** This is how larger applications are built: a frontend and a backend that can change independently. TypeScript catches whole classes of mistakes before the code runs.

**Checkpoint (planned).** The frontend builds without type errors and shows the same numbers as the API for the same community.
**Commit message (planned):** `feat: add the React and TypeScript frontend`.

---

## Stage 14: Phase 12, orchestration with Airflow

**What (planned).** `docs/13-phase-12-orchestration.md`. First a plain Python runner that calls every step in order, then the same pipeline as an Airflow workflow (ingest, transform, model, publish) with retries and a monitoring view. The pipeline also takes new results: a new file of measured communities goes in and the models retrain.

**Why.** Up to here every step is a command someone remembers to type. Orchestration runs them in the right order, on a schedule, and makes failures visible. Starting with the plain runner shows exactly what Airflow takes over.

**Checkpoint (planned).** One command (or one Airflow run) rebuilds everything from the raw data, and the result matches the committed tables.
**Commit message (planned):** `feat: orchestrate the pipeline, plain runner first, then Airflow`, tagged **v0.7.0**.

---

## Stage 15: Phase 13, the knowledge graph and its ontology

**What (planned).** `docs/14-phase-13-knowledge-graph.md`. Write down the ontology (what kinds of thing exist: strains, gene clusters, compound classes, communities, plants, and how they may relate), then build the graph, first in memory with NetworkX to show the idea, then in Neo4j, and ask questions that follow chains of relationships.

**Why.** The interaction layer is already a network of measured strain-against-strain effects. Squeezing it into tables loses structure; a graph keeps it, and makes questions such as "which strains hold back the pathogen's relatives *and* carry antibiotic gene clusters?" natural to ask.

**Checkpoint (planned).** Every relationship in the graph is allowed by the written ontology (a test checks it), and a set of example graph queries returns the expected answers.
**Commit message (planned):** `feat: add the ontology and the Neo4j knowledge graph`.

---

## Stage 16: Phase 14, GraphRAG, answers with sources

**What (planned).** `docs/15-phase-14-graphrag.md`. A question-answering page that looks things up in the knowledge graph and the project's documents before a language model writes an answer, and cites where each statement came from.

**Why.** In science an answer without a source can't be checked. Retrieval keeps the model to what the project actually contains, and the citations let a reader verify every claim. It runs without any language model too (search only), and with a local model nothing leaves the computer.

**Checkpoint (planned).** A set of test questions with known answers scores as expected, and questions the project can't answer are refused instead of guessed.
**Commit message (planned):** `feat: add GraphRAG question answering with cited sources`.

---

## Stage 17: Phase 15, the MCP server

**What (planned).** `docs/16-phase-15-mcp-server.md`. A small server that offers the project's predictions, data queries and graph lookups as read-only tools through the Model Context Protocol, so an AI assistant app can use them.

**Why.** MCP is a shared standard for connecting tools to assistant apps. Once the API of Stage 12 exists, this is a thin, well-checked layer on top: read-only tools, checked inputs, and a log of every call.

**Checkpoint (planned).** The server lists its tools, refuses anything that would change data, and logs every call; its tests talk to it the way an assistant app does.
**Commit message (planned):** `feat: add the MCP server with read-only tools`.

---

## Stage 18: Phase 16, the recommendation agent

**What (planned).** `docs/17-phase-16-agent.md`. An agent that takes a goal ("suggest three untested communities most likely to protect"), decides which tools to call, checks the candidates against the model and the graph, and returns a shortlist with its reasons.

**Why.** A chatbot answers; an agent takes steps. Here the steps are narrow and safe: a fixed set of read-only tools, a limit on the number of steps, and a full log of every action, so anyone can see how a shortlist was reached.

**Checkpoint (planned).** The agent's shortlist beats random choice on the held-out communities, and its log replays every step.
**Commit message (planned):** `feat: add the recommendation agent with logged, read-only steps`, tagged **v0.8.0**.

---

## Stage 19: Phase 17, the whole system in containers, Docker or Podman

**What (planned).** `docs/18-phase-17-containers.md`, with [`docs/CONTAINERS.md`](CONTAINERS.md) for the concepts. Every service (database, graph, API, Streamlit, frontend, MLflow) in its own container, started together with one command by a small script that finds Docker or Podman, whichever is installed.

**Why.** It turns "install six programs and wire them together" into one command that behaves the same on Windows, macOS and RHEL 8. Red Hat doesn't ship Docker on RHEL 8 (Podman is its container engine), so the same files are written to work with both.

**Checkpoint (planned).** On each of the three systems, one command starts all services, and the app's numbers match the tests.
**Commit message (planned):** `feat: run the whole system in containers with Docker or Podman`, tagged **v0.9.0**.

---

## Stage 20: Phase 18, tests on three systems, release 1.0

**What (planned).** `docs/19-phase-18-release.md`. Automated tests on Windows, macOS and Linux at every push (GitHub Actions), container images built automatically, a licence check, a citation file, a contribution guide and issue templates, an uninstall guide, an accessibility check of the apps, the changelog brought to 1.0, and the **v1.0.0** tag.

**Why.** Tests that run on three operating systems at every push show the project works beyond the computer it was built on, and keep showing it after every change.

**Checkpoint (planned).** The test run is green on all three systems for the release commit, and a fresh clone on a new computer follows the README to a working system.
**Commit message (planned):** `chore: release 1.0`, tagged **v1.0.0**.

---

## Stage 21: Beyond the repository, the product

**What (planned).** Read [`docs/PRODUCT_ROADMAP.md`](PRODUCT_ROADMAP.md).

**Why.** It describes what a larger RealSignal would add (other strain libraries, other assays, many users, scheduled retraining as new results come in, running inside an organisation's own network) and gives each technology a verdict with the event that would change it. The design choices made along the way (an assay-agnostic schema, containers, read-only tools) mean that list can be built on top of what exists.

**Checkpoint (planned).** You can explain which parts of RealSignal are specific to this study and which would carry over unchanged to another strain library.

---

## The whole build, command by command

Every command from a set-up computer to today, in order, on one page. Run them from the project folder with `(.venv)` showing in your prompt. Stage 1, the setup itself, differs by operating system, so it stays in [`docs/01-setup.md`](01-setup.md). After each stage: `pytest -q`, `./check-public-safe.sh`, then the ritual of Stage 2.

```bash
# Stage 1: check the workshop                              (docs/01-setup.md section 10)
python scripts/check_env.py

# Stage 3, Phase 1: get the real data, verified            (docs/02-phase-1-data-acquisition.md)
python scripts/fetch_data.py --probe
python scripts/fetch_data.py
python scripts/fetch_data.py                               # again: checks, doesn't download twice
python notebooks/explore_raw.py
python figures/make_concept_figures.py                     # the concept pictures and combinations.html
python figures/make_illustrations.py                       # logo, journey map, journey.html

# Stage 4, Phase 2: the other four layers                  (docs/03-phase-2-more-sources.md)
python notebooks/explore_layer1.py                         # what Layer 1's tables hold
python scripts/fetch_sources.py --list                     # the source register
python scripts/fetch_sources.py --probe
python scripts/fetch_sources.py                            # fetch and check every file
python scripts/fetch_sources.py                            # again: checks, doesn't download twice
python scripts/fetch_sources.py --pin                      # record checksums and statuses
python notebooks/explore_sources.py                        # what arrived
python figures/make_phase2_figures.py                      # the Phase 2 pictures and communities.html
python figures/make_concept_figures.py                     # redraws the layers picture from the register

# Stage 5, Phase 3: harmonise everything with dbt          (docs/04-phase-3-harmonisation.md)
python -m pip install -r requirements.txt                  # adds dbt-core and dbt-duckdb
python scripts/check_env.py                                # twelve packages
python scripts/load_raw.py --list                          # what gets loaded
python scripts/load_raw.py                                 # every raw table into the warehouse, unchanged
cd dbt                                                     # dbt runs from inside dbt/
dbt debug                                                  # can dbt find its files and the warehouse?
dbt build                                                  # every model, the seed and every test
dbt docs generate                                          # the documentation pages (dbt docs serve opens them)
cd ..
python notebooks/explore_warehouse.py                      # what the warehouse holds
python figures/make_phase3_figures.py                      # lineage, data model, plant choices

# Stage 6, Phase 4: explore the data                       (docs/05-phase-4-exploration.md)
python notebooks/explore_marts.py                          # seven questions; test values stay sealed
python figures/make_phase4_figures.py                      # the five Phase 4 pictures
python scripts/make_quality_report.py                      # docs/reports/data-quality.md
python scripts/make_quality_report.py                      # again: unchanged, byte for byte

# Every stage ends with
pytest -q
./check-public-safe.sh                                     # Windows: bash check-public-safe.sh in Git Bash
```

Each new phase adds its block here, in order. The order matters, because each stage reads what the stage before it wrote. One-off clean-up steps that belong to this repository's own history (such as Stage 3's `git rm --cached`) stay in their stage's *Save it* block.

## Every session, after setup

```bash
cd ~/projects/realsignal                  # wherever your project folder is; Windows PowerShell: cd $HOME\projects\realsignal
source .venv/bin/activate                 # Windows PowerShell: .\.venv\Scripts\Activate.ps1
git switch develop
git pull --ff-only origin develop
pytest -q                                 # is everything still green?
# ... work on the current stage ...
```

Then the end-of-phase ritual (Stage 2) when the stage is complete.

## When something goes wrong

| Symptom | Look in |
|---|---|
| a command "is not recognized" or "not found" | is `(.venv)` in your prompt? [`docs/01-setup.md` section 17](01-setup.md#17-troubleshooting) |
| `ModuleNotFoundError: No module named ...` | the virtual environment isn't active, or the packages went elsewhere: activate it, then `python -m pip install -r requirements.txt` |
| `python scripts/check_env.py` says something needs attention | it names the fix on its last lines; the details are in [`docs/01-setup.md` section 17](01-setup.md#17-troubleshooting) |
| the probe says `Could not reach the archive` | the internet connection, a company network that blocks the request, or Zenodo down for maintenance ([Phase 1 mini-FAQ](02-phase-1-data-acquisition.md#15-what-could-go-wrong-mini-faq)) |
| the download stops halfway | run the same command again; a leftover `.part` file is replaced |
| `MISMATCH` after the download | delete the archive and download again; if it happens twice, the archive may have changed ([Phase 1 mini-FAQ](02-phase-1-data-acquisition.md#15-what-could-go-wrong-mini-faq)) |
| the Phase 2 probe says `NOT REACHED  HTTP 403` for a journal file, or the fetch says `the server sent something else` | download the workbook by hand from the article page and put it in `data/raw/sources/<source_id>/` under the name in `sources/files.csv` ([Phase 2 mini-FAQ](03-phase-2-more-sources.md#16-what-could-go-wrong-mini-faq)) |
| a genome line says `FAILED` | run `python scripts/fetch_sources.py` again; only the missing files are fetched |
| `MISMATCH with pinned SHA-256` | the workbook isn't the one that was pinned: never re-pin to silence it ([Phase 2 mini-FAQ](03-phase-2-more-sources.md#16-what-could-go-wrong-mini-faq)) |
| `pytest -q` says `missing file ../figures/...png` | a guide links to a picture not drawn on this computer yet: run the figure scripts (`python figures/make_concept_figures.py`, `python figures/make_illustrations.py`, `python figures/make_phase2_figures.py`, `python figures/make_phase3_figures.py`, `python figures/make_phase4_figures.py`), then the tests again |
| `pytest -q` says a file ending in `data-quality.md` is missing | the report hasn't been written on this computer yet: `python scripts/make_quality_report.py`, then the tests again |
| `notebooks/explore_marts.py` or the Phase 4 scripts say `No warehouse yet` or that the marts aren't built | `python scripts/load_raw.py`, then `dbt build` inside `dbt/` ([Phase 4 mini-FAQ](05-phase-4-exploration.md#20-what-could-go-wrong-mini-faq)) |
| the explorer shows `pathogen_log10_normalised`, or numbers that differ from the guide | a `--vars` experiment is still in the warehouse: a plain `dbt build` inside `dbt/` |
| the data-quality report says `changed` though nothing was changed | `git diff docs/reports/data-quality.md` shows which numbers moved; usually a var left over from an experiment ([Phase 4 mini-FAQ](05-phase-4-exploration.md#20-what-could-go-wrong-mini-faq)) |
| `Nothing fetched yet` from `notebooks/explore_sources.py` | run `python scripts/fetch_sources.py` first |
| `ModuleNotFoundError: No module named 'openpyxl'` | the packages aren't installed in the active environment: `python -m pip install -r requirements.txt` |
| `pip install` stops at `dbt-core-experimental-parser` with `CERTIFICATE_VERIFY_FAILED` (Mac, Python from python.org) | Python's certificates were never installed: `sh "/Applications/Python 3.14/Install Certificates.command"` once, then install again ([Phase 3 mini-FAQ](04-phase-3-harmonisation.md#18-what-could-go-wrong-mini-faq)) |
| `dbt: command not found`, or `dbt is not recognized` | the virtual environment isn't active, or dbt isn't installed in it: activate it, then `python -m pip install -r requirements.txt` |
| dbt says `Path '/Users/<you>/.dbt' does not exist` or `No dbt_project.yml found` | dbt was started from the project folder: `cd dbt` first ([Phase 3 mini-FAQ](04-phase-3-harmonisation.md#18-what-could-go-wrong-mini-faq)) |
| `Catalog Error: Table with name ... does not exist` during `dbt build` | the raw tables aren't loaded: `python scripts/load_raw.py` from the project folder, then `dbt build` again |
| `Could not set lock on file`, or `scripts/load_raw.py` says the warehouse is open in another program | close the other program holding `data/warehouse/realsignal.duckdb` (a Python session, a database viewer, a dbt command still running) |
| a dbt test fails | `dbt show --select <the test's name>` shows the rows it found; after an experiment with `--vars`, a plain `dbt build` first ([Phase 3 mini-FAQ](04-phase-3-harmonisation.md#18-what-could-go-wrong-mini-faq)) |
| `dbt docs serve` says the address is in use | another program uses port 8080: `dbt docs serve --port 8081` |
| `git status` lists `dbt/target/` or `dbt/logs/` | your `.gitignore` is older than Phase 3: compare it with [`docs/01-setup.md` section 11](01-setup.md#11-keep-things-out-of-git-with-gitignore) |
| Windows: `The filename or extension is too long` | move the project closer to `C:\`, or switch on long paths ([Phase 1 mini-FAQ](02-phase-1-data-acquisition.md#15-what-could-go-wrong-mini-faq)) |
| `git status` lists files under `data/` | stop: `.gitignore` isn't working ([`docs/01-setup.md` section 11](01-setup.md#11-keep-things-out-of-git-with-gitignore)) |
| the safety gate says NOT SAFE | read the line marked ✗; it names the file and the fix. Never weaken the check ([`docs/01-setup.md` section 13](01-setup.md#13-the-safety-gate)) |
| the gate lists `.DS_Store` | `git rm --cached <path>` for each file it names; they stay on your disk and `.gitignore` keeps them out from then on |
| the gate says a picture carries hidden records | redraw it: `python figures/make_concept_figures.py` and `python figures/make_illustrations.py` ([`docs/01-setup.md` section 13](01-setup.md#13-the-safety-gate)) |
| `permission denied: ./check-public-safe.sh` (the exact wording depends on the shell) | the file lost its "runnable" mark: `chmod +x check-public-safe.sh`, or run it as `bash check-public-safe.sh` |
| macOS: `zsh: command not found: #`, or pytest complains about arguments such as `all` | the zsh shell is reading the notes after `#` as commands: the one-time setting in [`docs/01-setup.md` section 2](01-setup.md#macos-only-let-the-terminal-skip-the-notes-in-commands) |
| a pasted command prints strange characters | a look-alike character (long dash, curly quote) came along; retype it ([`docs/01-setup.md` section 14](01-setup.md#14-copy-commands-safely)) |
| `git push` is rejected | GitHub has commits your computer doesn't; pull first ([`docs/GIT_WORKFLOW.md` section 8](GIT_WORKFLOW.md#8-five-situations-that-confuse-everyone-and-their-fixes)) |
| you edited files on the wrong branch | [`docs/GIT_WORKFLOW.md` section 8](GIT_WORKFLOW.md#8-five-situations-that-confuse-everyone-and-their-fixes) |
| a word you don't know | the [Glossary](GLOSSARY.md) |
| a figure looks wrong or is missing | run the script that draws it again: `python figures/make_concept_figures.py`, `python figures/make_illustrations.py`, `python figures/make_phase2_figures.py`, `python figures/make_phase3_figures.py` or `python figures/make_phase4_figures.py` |

## Every file in the repository, and where it is explained

Every file in the repository is listed here with the guide that explains it. Paths are relative to the project folder.

| Path | What it is | Explained in |
|---|---|---|
| `README.md` | the front page | n/a |
| `CHANGELOG.md` | what changed, version by version | this Handbook |
| `LICENSE` | the MIT licence for the code and documentation (the data keeps its own CC-BY licence) | [README, Credits and licence](../README.md#credits-and-licence) |
| `requirements.txt` | the Python packages, with version ranges | [`docs/01-setup.md`](01-setup.md) section 9 |
| `requirements.lock.txt` | the exact package versions installed on the computer the project was built on | [`docs/01-setup.md`](01-setup.md) section 9 |
| `setup.sh`, `setup.ps1` | one-command setup for macOS/Linux and for Windows PowerShell, once Python is installed | [`docs/01-setup.md`](01-setup.md) section 16 |
| `.gitignore` | what Git must never record | [`docs/01-setup.md`](01-setup.md) section 11 |
| `check-public-safe.sh` | the safety gate, run before every push | [`docs/01-setup.md`](01-setup.md) section 13 |
| `pytest.ini` | tells the tests where to look (only in `tests/`), and lets them import from `src/` | [`docs/02-phase-1-data-acquisition.md`](02-phase-1-data-acquisition.md) section 12, [`docs/04-phase-3-harmonisation.md`](04-phase-3-harmonisation.md) section 4 |
| `scripts/check_env.py` | proves the setup works: Python, the virtual environment and the twelve packages | [`docs/01-setup.md`](01-setup.md) section 10 |
| `scripts/fetch_data.py` | probe, download, verify, unpack, list and log the published archive | [`docs/02-phase-1-data-acquisition.md`](02-phase-1-data-acquisition.md) |
| `notebooks/explore_raw.py` | a first look at what the archive contains | [`docs/02-phase-1-data-acquisition.md`](02-phase-1-data-acquisition.md) section 8 |
| `sources/register.csv` | the source register: every data source, its terms, status and date | [`docs/03-phase-2-more-sources.md`](03-phase-2-more-sources.md) sections 2 and 4 |
| `sources/files.csv` | every file to download, with its address or accession and its pinned checksum | [`docs/03-phase-2-more-sources.md`](03-phase-2-more-sources.md) section 4 |
| `scripts/fetch_sources.py` | list, probe, fetch, check and log the other layers, and record the outcome | [`docs/03-phase-2-more-sources.md`](03-phase-2-more-sources.md) sections 6 to 8 |
| `notebooks/explore_layer1.py` | what Layer 1's tables hold: training and test communities, plants set aside, the machine-learning table | [`docs/03-phase-2-more-sources.md`](03-phase-2-more-sources.md) section 5 |
| `notebooks/explore_sources.py` | a first look at the fetched workbooks and genomes | [`docs/03-phase-2-more-sources.md`](03-phase-2-more-sources.md) section 9 |
| `sources/tables.csv` | every raw table to load into the warehouse: its source, file, sheet and heading row | [`docs/04-phase-3-harmonisation.md`](04-phase-3-harmonisation.md) section 4 |
| `scripts/load_raw.py` | list and load the raw tables into `data/warehouse/realsignal.duckdb`, unchanged, with a load log | [`docs/04-phase-3-harmonisation.md`](04-phase-3-harmonisation.md) section 6 |
| `dbt/dbt_project.yml`, `dbt/profiles.yml` | the dbt project's settings and choices (vars), and where the warehouse is | [`docs/04-phase-3-harmonisation.md`](04-phase-3-harmonisation.md) section 7 |
| `dbt/README.md` | a map of the dbt folder | [`docs/04-phase-3-harmonisation.md`](04-phase-3-harmonisation.md) section 4 |
| `dbt/models/staging/` | the raw tables' declaration (`_sources.yml`) and 21 staging models in six folders, each with a `.yml` of descriptions and tests | [`docs/04-phase-3-harmonisation.md`](04-phase-3-harmonisation.md) sections 2, 3 and 9 |
| `dbt/models/intermediate/` | six models where the sources meet; `int_plants.sql` applies the three Layer 1 choices | [`docs/04-phase-3-harmonisation.md`](04-phase-3-harmonisation.md) section 8 |
| `dbt/models/marts/` | the eight tables later phases read, and their `.yml` | [`docs/04-phase-3-harmonisation.md`](04-phase-3-harmonisation.md) sections 9 and 10 |
| `dbt/models/overview.md` | the front page of dbt's documentation pages | [`docs/04-phase-3-harmonisation.md`](04-phase-3-harmonisation.md) section 11 |
| `dbt/macros/` | `strain_id()` and `looks_like_strain()`, `in_list()`, and the schema names | [`docs/04-phase-3-harmonisation.md`](04-phase-3-harmonisation.md) sections 3 and 7 |
| `dbt/seeds/` | `known_source_differences.csv`, every place two sources disagree, and its `.yml` | [`docs/04-phase-3-harmonisation.md`](04-phase-3-harmonisation.md) section 9 |
| `dbt/tests/` | 17 singular data tests, and the generic test `generic/accepted_range.sql` | [`docs/04-phase-3-harmonisation.md`](04-phase-3-harmonisation.md) section 9 |
| `notebooks/explore_warehouse.py` | what the warehouse holds, from queries on the marts | [`docs/04-phase-3-harmonisation.md`](04-phase-3-harmonisation.md) section 10 |
| `src/realsignal/__init__.py` | marks the folder as a Python package | [`docs/00-architecture.md`](00-architecture.md) section 14 |
| `src/realsignal/helpers.py` | the small helpers three scripts share: sizes, paths, banners, checksums, CSV tables | [`docs/04-phase-3-harmonisation.md`](04-phase-3-harmonisation.md) section 4 |
| `src/realsignal/exploration.py` | the seven Phase 4 questions, one function each, with the test set sealed | [`docs/05-phase-4-exploration.md`](05-phase-4-exploration.md) sections 1 and 2 |
| `notebooks/explore_marts.py` | prints every Phase 4 answer in the terminal | [`docs/05-phase-4-exploration.md`](05-phase-4-exploration.md) sections 3 to 10 |
| `scripts/make_quality_report.py` | writes the data-quality report, the same bytes every time for the same data | [`docs/05-phase-4-exploration.md`](05-phase-4-exploration.md) section 12 |
| `docs/reports/data-quality.md` | the data-quality report: every Phase 4 answer with its full lists, written by the script above | [`docs/05-phase-4-exploration.md`](05-phase-4-exploration.md) section 12 |
| `tests/test_fetch_data.py` | checks the download script offline, with a tiny stand-in archive | [`docs/02-phase-1-data-acquisition.md`](02-phase-1-data-acquisition.md) section 12 |
| `tests/test_safety_gate.py` | checks that the safety gate refuses what it should | [`docs/01-setup.md`](01-setup.md) section 13 |
| `tests/test_docs.py` | every link between the documents works, no look-alike characters, the Handbook and the journey map agree | [`docs/02-phase-1-data-acquisition.md`](02-phase-1-data-acquisition.md) section 12 |
| `tests/test_fetch_sources.py` | checks the register, and the fetcher against a stand-in web server, offline | [`docs/03-phase-2-more-sources.md`](03-phase-2-more-sources.md) section 13 |
| `tests/test_explore.py` | checks both Phase 2 explorers on tiny made-up tables | [`docs/03-phase-2-more-sources.md`](03-phase-2-more-sources.md) section 13 |
| `tests/test_helpers.py` | checks the shared helpers | [`docs/04-phase-3-harmonisation.md`](04-phase-3-harmonisation.md) section 15 |
| `tests/test_load_raw.py` | checks the loader on a made-up project | [`docs/04-phase-3-harmonisation.md`](04-phase-3-harmonisation.md) section 15 |
| `tests/test_warehouse.py` | runs the loader and the whole dbt project on a made-up screen of four strains in communities of two | [`docs/04-phase-3-harmonisation.md`](04-phase-3-harmonisation.md) section 15 |
| `tests/test_exploration.py` | the Phase 4 questions on a made-up warehouse of six strains in pairs, and the seal on the test set | [`docs/05-phase-4-exploration.md`](05-phase-4-exploration.md) section 17 |
| `figures/make_concept_figures.py`, `figures/*.png` | the concept pictures and the combinations page; the layers picture reads its statuses from `sources/register.csv` | [`docs/02-phase-1-data-acquisition.md`](02-phase-1-data-acquisition.md) section 9 |
| `figures/make_illustrations.py` | the logo, icon, wordmark, journey map and the interactive journey | [How this Handbook is maintained](#how-this-handbook-is-maintained) |
| `figures/make_phase2_figures.py` | the three Phase 2 pictures (`three_checks.png`, `source_register.png`, `layer1_rounds.png`) and the communities page | [`docs/03-phase-2-more-sources.md`](03-phase-2-more-sources.md) section 10 |
| `figures/make_phase3_figures.py` | the three Phase 3 pictures: `lineage.png` and `data_model.png` from dbt's manifest, `plant_choices.png` from the warehouse | [`docs/04-phase-3-harmonisation.md`](04-phase-3-harmonisation.md) section 11 |
| `figures/make_phase4_figures.py` | the five Phase 4 pictures, drawn from measured values: `outcome_shape.png`, `rounds_compared.png`, `strain_frequency.png`, `missing_values.png`, `one_strain_at_a_time.png` | [`docs/05-phase-4-exploration.md`](05-phase-4-exploration.md) section 11 |
| `docs/*.md` | the guides, glossary, roadmaps and this Handbook | this table |
| `docs/img/*.svg` | the logo, icon, wordmark and journey map | `figures/make_illustrations.py` |
| `docs/interactive/journey.html` | this Handbook's journey as a page you can click, built from this file | `figures/make_illustrations.py` |
| `docs/interactive/combinations.html` | how many communities exist, and how long testing them all would take | `figures/make_concept_figures.py` |
| `docs/interactive/communities.html` | all 206 communities of the screen: pick strains, see which training and test communities hold them | `figures/make_phase2_figures.py` |
| `docs/index.html`, `docs/.nojekyll` | the front page of the optional GitHub Pages site, and the marker that publishes the folder as it is | [`docs/02-phase-1-data-acquisition.md`](02-phase-1-data-acquisition.md) section 9 |
| `R/`, `api/`, `app/`, `frontend/`, `airflow/`, `mcp/` | empty folders kept by a `.gitkeep` file, one for each phase that will fill it | [`docs/00-architecture.md`](00-architecture.md) section 14 |
| `data/` | the downloaded files and everything made from them: **never in Git**. `data/raw/` (the archive) is rebuilt by `scripts/fetch_data.py`, `data/raw/sources/` (the other layers) by `scripts/fetch_sources.py`, and `data/warehouse/realsignal.duckdb` by `scripts/load_raw.py` and `dbt build` | [`docs/02-phase-1-data-acquisition.md`](02-phase-1-data-acquisition.md), [`docs/03-phase-2-more-sources.md`](03-phase-2-more-sources.md), [`docs/04-phase-3-harmonisation.md`](04-phase-3-harmonisation.md) |
| `dbt/target/`, `dbt/logs/` | what dbt writes each time it runs (compiled SQL, results, the documentation pages, its log): **never in Git**, made again on every run | [`docs/04-phase-3-harmonisation.md`](04-phase-3-harmonisation.md) section 11 |

## How this Handbook is maintained

It's a living document, and the **first** one to update. At the end of every phase, in the same commit as the phase itself:

1. Change the stage's status in the table at the top, and write the real checkpoint numbers into the stage. (Stage headings carry no status marks, so their link addresses never change.)
2. Turn the planned guide name into a link to the guide that now exists.
3. Update the version, date and repository state at the top.
4. Make the same status change in [`docs/ROADMAP.md`](ROADMAP.md), the README's build status, and the `STAGES` list in `figures/make_illustrations.py`, then run `python figures/make_illustrations.py`. It redraws the journey map and rebuilds `docs/interactive/journey.html` from this Handbook. (`tests/test_docs.py` fails if the table and the list disagree.)
5. Add the stage's commands to [The whole build, command by command](#the-whole-build-command-by-command).
6. Add the change to `CHANGELOG.md`.

Small changes between phases (a fix, a renamed command, a new troubleshooting row) update the Handbook in the same commit too, as a "Stage N.1" when they deserve their own stage. **If the Handbook falls behind the code, treat it as a bug.**

**One house rule for every document in the repository:** whenever a document names a file, it gives the file's full path from the project folder (`scripts/fetch_data.py`, not `fetch_data.py`), so a reader always knows where it lives.
