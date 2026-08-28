# 02 — Phase 1: getting the real data

**Prerequisites:** [`01-setup.md`](01-setup.md) completed, with
`python scripts/check_env.py` reporting **ALL CHECKS PASSED**. You
should be inside the project folder with `(.venv)` showing in your
prompt and on the `develop` branch.

**Learning goal:** after this phase you will understand what a permanent
research archive is and why it exists; what a checksum proves and what
it does not; why raw data is treated as read-only; what provenance
means and how to record it; and you will have the real, published,
peer-reviewed dataset on your machine, verified.

**Time:** 45–60 minutes, most of it the download running while you read.

**Data downloaded:** about 239 MB, once.

> Every term is defined in [`GLOSSARY.md`](GLOSSARY.md).

---

## Contents

- [1. Why this phase exists](#1-why-this-phase-exists)
- [2. Where the data comes from](#2-where-the-data-comes-from)
- [3. What is actually in the dataset (the science)](#3-what-is-actually-in-the-dataset-the-science)
- [4. Three ideas you need before running anything](#4-three-ideas-you-need-before-running-anything)
- [5. Create the download script](#5-create-the-download-script)
- [6. Run it — first look, then leap](#6-run-it--first-look-then-leap)
- [7. Look at what you got](#7-look-at-what-you-got)
- [8. Checkpoint](#8-checkpoint)
- [9. What could go wrong](#9-what-could-go-wrong)
- [10. Commit this phase](#10-commit-this-phase)

---

## 1. Why this phase exists

It is tempting to think of "getting the data" as a chore before the
real work. In practice it *is* real work, and it is where a
disproportionate share of projects quietly go wrong.

Consider what can happen without care:

- The download is interrupted at 94%, leaving a file that opens
  perfectly and is missing a fifth of the rows. Nothing errors. Every
  number you produce afterwards is wrong.
- You open a data file in Excel "just to look", it helpfully converts
  a strain identifier into a date, you save without thinking, and the
  original is gone.
- Six months later somebody asks where a number came from and the
  honest answer is "a spreadsheet on my old laptop".

Each of those is mundane, common, and fatal to trust. This phase
installs three habits that prevent all three:

1. **Verify what you downloaded** against a published checksum.
2. **Never edit raw data** — treat the downloaded copy as read-only.
3. **Write down where it came from**, automatically, at download time.

*Analogy for the whole phase:* a laboratory receiving a sample.
Somebody checks the seal is unbroken, logs the batch number and the
date, and stores it in the freezer. Only then does anyone start
pipetting. The logging feels bureaucratic right up until the day a
result looks strange and the log is the only way to find out why.

---

## 2. Where the data comes from

### The study

> Emmenegger, B., Massoni, J., Pestalozzi, C. M., Bortfeld-Miller, M.,
> Maier, B. A., & Vorholt, J. A. (2023). Identifying microbiota
> community patterns important for plant protection using synthetic
> communities and machine learning. *Nature Communications*, **14**,
> 7983. <https://doi.org/10.1038/s41467-023-43793-z>

Open access — you can read the whole thing for free, and it is worth
skimming the figures before you continue. The work was done at the
Institute of Microbiology, ETH Zurich.

### The data deposit

> <https://doi.org/10.5281/zenodo.10118600> — data and the original R
> code, licensed CC-BY 4.0.

**What Zenodo is.** A free, permanent public archive for research data
and software, run by CERN. Researchers deposit their files and receive
a **DOI** — a permanent identifier.

**Why a DOI rather than a link.** Ordinary web links rot.
Laboratories move, universities redesign their websites, hosting
lapses. A 2019 paper pointing at `somelab.uni.edu/data/final.zip` is,
today, quite often pointing at nothing at all. A DOI carries a promise:
it will keep resolving to the same object.

*Analogy:* an ISBN identifies a book regardless of which shop stocks
it. "Third shelf, corner shop" identifies a book only until someone
rearranges the shop.

**What the licence means.** CC-BY 4.0 permits anyone to reuse the work —
including commercially, including modified — **on condition that the
creators are credited**. This project credits them in the README, in
every document, in the code, and in the fetch log the script writes.
Reuse under CC-BY is not a favour being granted quietly; it is the
explicit purpose of the licence. Crediting properly is both the legal
requirement and simply the right thing.

**What we deliberately do not do:** we do not put a copy of their data
in our repository. The script downloads it from the original archive so
that everyone receives it from the source, with the licence and the
authors' names attached. That keeps the chain of attribution intact
rather than laundering it through us.

### A note on the study being reproduced

Reproducing someone's analysis is sometimes read as an accusation. It
should not be. These authors did the thing that makes reproduction
possible at all — they released their data and their code, publicly,
permanently, openly licensed. That is still not universal. **A study
you can check is a better study than one you cannot**, and engaging
with it closely is a form of respect.

---

## 3. What is actually in the dataset (the science)

You do not need a biology background. Here is the whole experiment.

### The question

Plant leaves are covered in harmless bacteria. Some of those bacteria
protect the plant against disease-causing ones. **Which ones?**

The difficulty is that bacteria do not act alone — they compete, they
inhibit one another, sometimes they help one another. So a strain that
looks protective by itself in a laboratory dish may do nothing on a
real leaf surrounded by others.

### The design

*Analogy.* You manage a 5-a-side football league and want to know which
individual players actually win matches. Testing a player alone against
a wall tells you nothing, because football is not played against a
wall. So instead: form many random 5-player teams, record every result,
then work backwards — *which players keep appearing in winning teams?*

That is the experiment, exactly:

| Element | In the experiment |
|---|---|
| The pool of players | **35 strains** of harmless leaf bacteria |
| A team | **5 strains** applied together (a "Mini5SynCom") |
| Matches played | **136 teams**, each on its own set of plants |
| The opponent | *Pseudomonas syringae* DC3000, a plant pathogen |
| The pitch | Sterile *Arabidopsis thaliana* plants in sealed boxes |
| The final score | How much pathogen grew, 14 days after infection |
| The rematch | **70 more teams** in a separate experiment, kept for testing |

Every plant was also weighed, and the harmless bacteria were counted
too — so the data records not just the score but the conditions.

### Some vocabulary, in plain words

- **Strain** — one specific, named type of bacterium kept in a
  laboratory freezer. Like one named breed rather than "dog" in
  general. Ours are called things like `Leaf15` and `Leaf76`, because
  they were isolated from real leaves and numbered.
- **SynCom** (synthetic community) — a team of known strains
  deliberately combined. "Synthetic" means *assembled from known parts
  by humans*, not artificial.
- **Pathogen** — a microbe that causes disease.
- **CFU** (colony-forming unit) — how live bacteria are counted. You
  spread a diluted sample on a nutrient jelly; each living bacterium
  grows into one visible dot; you count the dots and scale back up.
  *Analogy:* estimating fish in a lake by netting one measured bucket.
- **CFU per gram** — divided by the plant's weight, so a big plant is
  not unfairly counted as "more infected" simply for offering more
  surface. *Analogy:* crime per 100,000 residents rather than raw
  counts.

### One thing that will look strange in the numbers

Pathogen counts in this data range from roughly ten thousand to roughly
a billion. That is not an error — bacterial populations genuinely span
that range, and it is why biologists always work with these numbers on
a **log10 scale**, where a tenfold difference is the same visual
distance everywhere.

On a log10 scale, 10,000 becomes 4 and 1,000,000,000 becomes 9. So a
column of numbers between about 4 and 9 is what you are expecting to
see. Anything outside that is worth investigating.

### The answer they found

Three strains — *Pseudomonas* Leaf15, *Rhizobium* Leaf68 and
*Acidovorax* Leaf76 — genuinely reduced the pathogen, confirmed
afterwards by direct laboratory tests. One of them had never previously
been identified as protective.

**Our job is not to take their word for it.** In later phases we will
train our own models, in a different language, and see whether the same
three strains come out on top.

---

## 4. Three ideas you need before running anything

### Idea 1 — A checksum, and what it proves

A **checksum** is a short code calculated from a file's exact contents.
Change one single byte and the code changes completely and
unpredictably.

Zenodo publishes the checksum for this archive:
`f8061f230b621703f0f11be454c5167e`. Our script computes the checksum of
what we downloaded and compares.

**What a match proves:** you have exactly the file the authors
deposited — not truncated, not corrupted, not a different version.

**What it does not prove:** that the data is *correct*, or that the
science is right. *Analogy:* the tamper-evident seal on a medicine
bottle tells you nobody opened it in transit. It says nothing about
whether the medicine works.

That distinction matters, because a lot of technical checks get
oversold. Knowing precisely what a check does and does not tell you is
part of doing this well.

### Idea 2 — Raw data is read-only

Once downloaded, nothing ever edits `data/raw/`. Every other file in
the project can be regenerated by running code. The raw copy cannot.

*Analogy:* photographers keep the original negatives and edit prints.
Make a hundred prints, throw ninety-nine away, start again. You cannot
un-scribble on a negative.

**In practice this means:** do not open the extracted files in Excel
and save. If you want to look at one, look — and close it without
saving. Better, look at it with code, which cannot accidentally
overwrite anything.

### Idea 3 — Provenance

**Provenance** is the documented history of a piece of data: where it
came from, when, and what has been done to it since.

Our script writes a small `fetch_log.json` recording the source DOI,
the date, the checksum and the file count. It takes no effort and it is
the difference between a result and a rumour.

*Analogy:* an artwork with documented ownership history versus one that
"was in the attic". The painting may be identical. The value is not.

---

## 5. Create the download script

The full script is `scripts/fetch_data.py`, provided with this project.
**Read it before running it** — it is heavily commented, and every
design decision in it is explained in place. If you are typing it out
yourself rather than copying, that is excellent; you will remember more.

The script does six things:

| Step | What it does | Why |
|---|---|---|
| 1. Probe | Asks the server how big the file is, without downloading | A 239 MB download deserves a warning first |
| 2. Download | Streams the file to disk with a progress bar | Streaming means 1 MB of memory, not 239 MB |
| 3. Verify | Computes the checksum and compares | Catches truncation and corruption |
| 4. Extract | Unpacks the archive, safely | Zip files from anywhere are unpacked defensively |
| 5. Inventory | Lists every file inside, writes a manifest | We do not guess what is in there — we look |
| 6. Log | Writes the provenance record | So the source is written down, not remembered |

Three details in the code are worth pausing on, because each represents
a habit rather than a trick:

**Streaming.** `requests.get(..., stream=True)` reads the response a
megabyte at a time instead of loading all 239 MB into memory. The
pattern matters far beyond this project: any time you handle a file
bigger than comfortable, process it in pieces.

**The `.part` rename.** The file downloads under a temporary name and
is renamed only when complete. If your connection drops, you are left
with something obviously unfinished rather than something that looks
like a finished download. *Analogy:* not putting the label on the jar
until it is full.

**The zip-safety check.** A zip archive can contain entries with names
like `../../.bashrc`, which — unpacked naively — escape the folder you
intended and overwrite files elsewhere. It is called *zip slip*. This
archive is from a trusted scientific source and is certainly fine, but
"probably fine" is not a security model, and the check costs two lines.

---

## 6. Run it — first look, then leap

### Step 1 — Activate your environment

Confirm `(.venv)` is in your prompt. If not:

> **🪟 Windows:** `.\.venv\Scripts\Activate.ps1`
> **🍎 macOS / 🐧 Linux:** `source .venv/bin/activate`

### Step 2 — Probe first

```bash
python scripts/fetch_data.py --probe
```

**Expected output:**

```
======================================================================
PROBE — what would be downloaded
======================================================================
Source record : https://zenodo.org/records/10118600
File          : Mini5SynCom_Repository.zip
Published size: ~239.2 MB
Published MD5 : f8061f230b621703f0f11be454c5167e
Licence       : CC-BY 4.0 (reuse permitted with attribution)
Destination   : /home/you/projects/realsignal/data/raw/Mini5SynCom_Repository.zip

Server reports: 239.2 MB
Reachable     : yes

Nothing has been downloaded. To proceed:
    python scripts/fetch_data.py
```

**What just happened.** The script sent an HTTP `HEAD` request — "send
me the headers, not the body". The label on the parcel, not the parcel.
It costs a fraction of a second and almost no data.

**Why bother?** Because looking before leaping is a habit worth having
with any external source you do not control. It also catches the two
commonest failures — no internet, or the source having moved — in one
second instead of after a five-minute download.

> If this step fails, do not continue. §9 covers what to do.

### Step 3 — Download

```bash
python scripts/fetch_data.py
```

**Expected output** (this takes several minutes; the bar updates in
place):

```
======================================================================
DOWNLOAD
======================================================================
From: https://zenodo.org/records/10118600/files/Mini5SynCom_Repository.zip?download=1
To  : /home/you/projects/realsignal/data/raw/Mini5SynCom_Repository.zip
This is a large file. Expect several minutes on a typical connection.

  [########################################] 100.0%  239.2 MB / 239.2 MB
Download complete: 239.2 MB

======================================================================
VERIFY — is this exactly the file the authors deposited?
======================================================================
Computing checksum (this takes a few seconds)...
  Expected: f8061f230b621703f0f11be454c5167e
  Actual  : f8061f230b621703f0f11be454c5167e

MATCH. This is provably the published archive, byte for byte.

======================================================================
EXTRACT
======================================================================
Unpacking ... entries...
Extracted to: /home/you/projects/realsignal/data/raw/extracted

======================================================================
INVENTORY — what is actually inside
======================================================================
Total files: ...
...
```

🎉 **The `MATCH` line is the moment worth pausing on.** You have not
just downloaded a file — you have *proved* you have the same bytes the
authors deposited on 13 November 2023. That is a different and stronger
claim than "I downloaded it and it seemed fine", and it is the
foundation everything else in this project rests on.

### Step 4 — Confirm it is idempotent

Run exactly the same command again:

```bash
python scripts/fetch_data.py
```

```
Archive already present: .../data/raw/Mini5SynCom_Repository.zip
Verifying it rather than downloading again (use --force to re-download).
...
MATCH. This is provably the published archive, byte for byte.
Already extracted at .../data/raw/extracted — skipping.
```

**No second download.** A script that is safe to run repeatedly is
called **idempotent**, and it is a genuinely important property: it
means you can re-run a pipeline without fear, which in turn means you
will actually re-run it, which is how errors get caught.

*Analogy:* a light switch that is already on. Pressing it again does
not turn the light "more on", and it does not break anything.

---

## 7. Look at what you got

The inventory step printed a summary and wrote
`data/raw/manifest.csv`. Now explore it properly — this is genuine
analysis work, not a formality.

### Step 1 — Read the manifest

Create `notebooks/explore_raw.py` (a plain script, not a notebook — we
introduce notebooks in Phase 3):

```python
"""
explore_raw.py — a first look at what the archive actually contains.

WHY THIS EXISTS: never assume the shape of data you did not create.
Before writing a single line of analysis, find out what you have.
"""

import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST = PROJECT_ROOT / "data" / "raw" / "manifest.csv"

# Read the manifest the fetch script produced.
manifest = pd.read_csv(MANIFEST)

print(f"Total files in the archive: {len(manifest)}")
print()

# How is the archive made up? Grouping by file type is the fastest way
# to understand an unfamiliar folder.
print("Files by type:")
by_type = (
    manifest
    .groupby("extension")
    .agg(count=("relative_path", "size"),
         total_mb=("size_bytes", lambda s: round(s.sum() / 1024 / 1024, 1)))
    .sort_values("count", ascending=False)
)
print(by_type)
print()

# Which files are likely to hold the measurements we need?
# Spreadsheets and delimited text are the usual homes for tabular data.
data_like = manifest[manifest["extension"].isin(
    [".csv", ".tsv", ".txt", ".xlsx", ".xls"]
)]
print(f"Tabular data files: {len(data_like)}")
print(data_like[["size_human", "relative_path"]].to_string(index=False))
print()

# The archive also contains the authors' original R code. Reading it later
# is how we check our interpretation of their method against what they
# actually did — a resource most reproduction attempts do not have.
code_like = manifest[manifest["extension"].isin([".r", ".rmd"])]
print(f"R script files (the authors' original analysis): {len(code_like)}")
print(code_like[["size_human", "relative_path"]].head(20).to_string(index=False))
```

Run it:

```bash
python notebooks/explore_raw.py
```

### Step 2 — Actually read the output

Do not skim past this. Ask yourself, and write the answers in a plain
text file as you go:

1. **How many files, and of what types?** An archive that is mostly
   `.R` files is a code deposit with data attached; one that is mostly
   `.csv` is the reverse. Which is this?
2. **Which files plausibly hold the 136 teams and their outcomes?**
   Look at names and sizes. A file of a few hundred kilobytes is about
   right for a few hundred rows; a 40 MB file is something else.
3. **Is the authors' R code present?** If so, you have something rare:
   the ability to check your reading of the method against what they
   actually ran. Note where it is.
4. **Is anything conspicuously missing** compared with what the paper's
   Methods section describes?

**Why do this by hand rather than automate it?** Because the goal here
is understanding, and understanding does not come from a script. In
Phase 2 you will write code that reads specific files — and you can
only write that code once you know which files, which is what this step
establishes. Skipping it means guessing filenames, which is exactly how
scripts break silently on someone else's machine.

*Analogy:* unpacking a delivery of ingredients and reading the labels
before starting to cook, rather than tipping everything into the pan
and finding out.

### Step 3 — A note on the alternative source

The paper also publishes its **Source Data** — the numbers behind each
figure — as spreadsheet files on the article page itself
(<https://doi.org/10.1038/s41467-023-43793-z>, in the "Source data"
section). Those files are much smaller than the full archive.

If the Zenodo download is impractical on your connection, the Source
Data is a viable alternative route to the same measurements. If you use
it, **say so in your README** — the point of this project is that
choices are documented, not that one particular route is correct.

---

## 8. Checkpoint

You have finished Phase 1 when all of these are true:

- [ ] `python scripts/fetch_data.py --probe` reports the archive is
      reachable
- [ ] `data/raw/Mini5SynCom_Repository.zip` exists
- [ ] The verify step printed **MATCH**
- [ ] `data/raw/extracted/` contains the unpacked files
- [ ] `data/raw/manifest.csv` exists and lists every file
- [ ] `data/raw/fetch_log.json` exists and records the DOI and date
- [ ] Running the script a second time does **not** re-download
- [ ] `python notebooks/explore_raw.py` runs and prints a summary
- [ ] You have written down which files look like they hold the
      measurements
- [ ] `git status` does **not** list anything inside `data/`

**That last one matters most.** Confirm it explicitly:

```bash
git status
```

You should see `scripts/fetch_data.py` and `notebooks/explore_raw.py`
as new files, and **nothing** from `data/`. If `data/` appears,
`.gitignore` is not doing its job — go back to
[`01-setup.md`](01-setup.md) §11 before committing anything, because a
239 MB file committed once stays in the history forever.

### What you learned in this phase

- What a permanent research archive is, and why DOIs exist
- What a checksum proves — and, just as importantly, what it does not
- Why raw data is treated as read-only, and what goes wrong otherwise
- What provenance means and how little it costs to record
- Why streaming a large file matters, and what idempotence buys you
- How to approach unfamiliar data: look first, guess never

---

## 9. What could go wrong

### The probe fails: "Could not reach the archive"

- Check your internet connection (open any website).
- On a corporate network, a proxy may be blocking the request. Try from
  a different network to confirm, and speak to your IT team if so.
- Zenodo occasionally goes down for maintenance. Check
  <https://zenodo.org> in a browser; if the site is down, wait and
  retry.

### The download stops partway

Re-run the command. The partial file is named `...zip.part` and is
simply overwritten. If it fails repeatedly at the same point, your
connection is dropping — try a wired connection, or a different
network.

### `MISMATCH` on the checksum

Nearly always an incomplete download. Delete the archive and try again:

> **🪟 Windows:** `Remove-Item data\raw\Mini5SynCom_Repository.zip`
> **🍎 macOS / 🐧 Linux:** `rm data/raw/Mini5SynCom_Repository.zip`

```bash
python scripts/fetch_data.py
```

If a second clean download gives the same mismatch, the archive itself
may have been updated by its authors. Check the record page — the
current checksum is shown next to the file — and **note the discrepancy
in your README**. A changed source is a finding worth reporting, not a
nuisance to be worked around silently.

### `ModuleNotFoundError: No module named 'requests'`

The virtual environment is not active. Look for `(.venv)` in your
prompt, activate, and re-run. See [`01-setup.md`](01-setup.md) §15.

### "No space left on device"

You need roughly 700 MB free: 239 MB for the archive, plus its
extracted contents. Free some space and re-run — nothing is lost.

### The extraction is slow

239 MB of compressed files takes a little while to unpack, especially
on a network drive or an older disk. Let it finish. If it is
*extremely* slow, check you are not working inside a cloud-synced
folder (OneDrive, Dropbox) — see [`01-setup.md`](01-setup.md) §7.

### Windows: "The filename or extension is too long"

Windows has a historic 260-character path limit and deeply-nested
archives can exceed it. Two fixes: move the project closer to the drive
root (`C:\projects\realsignal`), or enable long paths — in PowerShell
**as administrator**:

```powershell
New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" `
  -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
```

Then restart, and re-run.

---

## 10. Commit this phase

You have added two scripts and a lot of understanding. Save the work.

```bash
# 1. Make sure you are on the working branch.
git switch develop

# 2. Check what will be committed — read this output.
git status

# 3. Stage everything.
git add -A

# 4. Commit with a message that explains what and why.
git commit -m "feat: add verified download of the published dataset

Fetches the Zenodo archive (DOI 10.5281/zenodo.10118600), verifies it
against the published MD5, extracts it safely, writes a file manifest
and a provenance log. Idempotent: a second run verifies rather than
re-downloads. Data itself stays out of Git by design."

# 5. Push develop, and update beta and master to match.
git push origin develop develop:beta develop:master

# 6. Bring local master in line with the master you just pushed.
git switch master
git pull --ff-only origin master

# 7. Return to the working branch, ready for Phase 2.
git switch develop
```

**Verify it worked:**

```bash
git log --oneline -3
```

```
c3d4e5f (HEAD -> develop, origin/master, origin/develop, origin/beta, master) feat: add verified download of the published dataset
b2c3d4e chore: verified environment setup on this machine
a1b2c3d chore: initial project structure, documentation and environment
```

The fact that `origin/master`, `origin/develop`, `origin/beta` and
`master` all appear on the same line means every branch is pointing at
the same commit — exactly what the push was meant to achieve.

Every command above is explained word by word in
[`GIT_WORKFLOW.md`](GIT_WORKFLOW.md) §6.

---

## What comes next

**Phase 2 — Building the analysis table.** Taking the files you have
just identified and reshaping them into the one tidy table the models
need: 136 rows (one per team), 35 columns of 1s and 0s (which strains
were on it), and the measured outcome. You will meet SQL and DuckDB,
write your first data-quality checks, and discover — as everyone does —
that turning real published data into a clean rectangle is most of the
work in any data project.

---

**Previous:** [`01-setup.md`](01-setup.md) ·
**Glossary:** [`GLOSSARY.md`](GLOSSARY.md) ·
**Architecture:** [`00-architecture.md`](00-architecture.md)
