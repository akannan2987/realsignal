# Changelog

All notable changes to RealSignal are recorded here, newest first. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses [Semantic Versioning](https://semver.org/): version numbers look like `MAJOR.MINOR.PATCH`, a new MINOR version marks a milestone from [`docs/ROADMAP.md`](docs/ROADMAP.md#4-milestones-and-version-tags), a PATCH marks a fix, and 1.0.0 marks the first complete release.

Each step is explained in [`docs/HANDBOOK.md`](docs/HANDBOOK.md), the guide from day 0 to the finished product.

## [Unreleased]

Nothing yet. Phase 2 is next.

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
