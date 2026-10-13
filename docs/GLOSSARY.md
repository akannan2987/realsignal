[Handbook](HANDBOOK.md) · [README](../README.md) · [Architecture](00-architecture.md) · [Roadmap](ROADMAP.md)

# Glossary: every term, in plain language

Every biological and technical term used anywhere in RealSignal is defined here in everyday words, with a familiar comparison where one helps. If you meet a word in a guide, a code comment or an app screen that isn't here, that's a documentation bug worth reporting.

Terms are grouped by subject. Within a group, earlier entries don't depend on later ones, so a group reads from top to bottom. Terms for phases not built yet are marked *(Phase N)*.

## Contents

- [Group 1: The biology](#group-1-the-biology)
- [Group 2: The experiment](#group-2-the-experiment)
- [Group 3: Your computer and the command line](#group-3-your-computer-and-the-command-line)
- [Group 4: Python and packages](#group-4-python-and-packages)
- [Group 5: Git and GitHub](#group-5-git-and-github)
- [Group 6: Data, files and downloads](#group-6-data-files-and-downloads)
- [Group 7: Databases and data engineering](#group-7-databases-and-data-engineering)
- [Group 8: Machine learning](#group-8-machine-learning)
- [Group 9: Evaluation](#group-9-evaluation)
- [Group 10: Science and reproducibility](#group-10-science-and-reproducibility)
- [Group 11: Applications and containers](#group-11-applications-and-containers)
- [Group 12: Graphs and the AI features](#group-12-graphs-and-the-ai-features)
- [Group 13: R and the three-way comparison](#group-13-r-and-the-three-way-comparison)
- [Group 14: The documentation and releases](#group-14-the-documentation-and-releases)

---

## Group 1: The biology

- **Bacterium** (plural **bacteria**): a living thing made of a single cell, about a thousandth of a millimetre across. They live everywhere (soil, water, skin, leaves); most are harmless or useful, and a minority cause disease.
- **Microbe**: any living thing too small to see, including bacteria and fungi. All the microbes in this project are bacteria.
- **Strain**: one particular, named kind of bacterium, kept alive in a laboratory and identified down to its genes. These ones have names like `Leaf15` and `Leaf76` because they were isolated from leaves and numbered.
- **Genus**: the first part of a bacterium's scientific name, written in italics. *Pseudomonas* Leaf15 is the strain numbered Leaf15, in the genus *Pseudomonas*, much as a surname groups relatives.
- **Taxonomy**, **phylum**, **class**, **order**, **family**: the system that names living things and groups them, from the broadest group to the narrowest: phylum, class, order, family, genus, then species and strain. Names change as more is learned, so two strain lists made years apart can put the same strain in groups with different names. Phase 3 found two lists that agree on every phylum and class and differ on 7 families and 10 genera.
- **Microbiome**: the whole community of microbes living on or in something: a leaf, a gut, a patch of soil. The town's whole population, as opposed to one resident.
- **Microbiota**: used to mean the same as microbiome in most writing, including the source paper. Strictly, the microbiota is the organisms and the microbiome includes their genes and surroundings; this project treats them as one.
- **Commensal**: a microbe that lives on a host without harming it (from the Latin for "sharing a table"). All 35 strains in the study are commensals.
- **Pathogen**: a microbe that causes disease. The study's is *Pseudomonas syringae* pv. *tomato* DC3000, shortened to **Pst**, which infects leaves and multiplies inside them.
- **Inoculation**: putting the harmless strains onto the plants, before the pathogen arrives.
- **Infection**: putting the pathogen onto the plants, here by spraying a measured dose. The source paper keeps the two words apart and so does this project.
- **Colonisation**: how much of a microbe has settled on a plant; this is what gets measured. High pathogen colonisation means the pathogen thrived and the plant wasn't protected.
- **Biocontrol**: protecting plants from disease with living organisms instead of chemicals, the way a gardener releases ladybirds to eat aphids instead of spraying.
- **Protective strain** (the paper's **pathogen-reducing** or **PR strain**): a strain whose presence measurably lowers pathogen colonisation. The study found three: *Pseudomonas* Leaf15, *Rhizobium* Leaf68 and *Acidovorax* Leaf76.
- ***Arabidopsis thaliana*** (thale cress, often just *Arabidopsis*): a small, fast-growing weed that plant scientists use as their standard plant, much as medical researchers use mice.
- **Phyllosphere**: the parts of a plant above ground, leaves above all, seen as a home for microbes.
- ***At*-LSPHERE**: a collection of bacteria isolated from the leaves of wild *Arabidopsis* plants. Every data layer in this project describes strains from it, which is why they can be joined.
- **Axenic**: completely free of microbes. An axenic plant is sterile, the blank to compare everything else against. In the screen's files, `axenic` marks plants given none of the 35 strains; most of them still received the pathogen, to show an unprotected infection.
- **Gnotobiotic**: a system in which every organism present is known and was put there on purpose. Not sterile, but with a known cast list, like a stage play instead of a crowd scene filmed in a real street.
- **Genome**: the complete set of a strain's DNA, its full instruction book. *(Layer 2)*
- **DNA sequence**: DNA written down as a string of four letters, A, C, G and T, one for each of its four building blocks.
- **Genome assembly**: a genome put back together by a computer from the short fragments a sequencing machine reads. Each published assembly gets its own accession (Group 6).
- **Contig**: one continuous stretch of an assembled genome. A genome in 40 contigs holds the whole sequence, in 40 pieces whose order isn't known.
- **GC content**: the share of the letters G and C in a DNA sequence, given as a percentage. Each kind of bacterium has a typical value, so an odd one is worth a second look.
- **Gene cluster**, or **biosynthetic gene cluster (BGC)**: a group of neighbouring genes that together make one chemical, often an antibiotic or another **natural product** (a compound made by a living thing). *(Layer 3)*
- **Inhibition**: one strain holding back another's growth, for example by releasing a chemical. The **inhibition network** records which strain holds back which. *(Layer 4)*
- **Multi-omics**: combining several kinds of biological measurement (genomes, chemistry, behaviour) about the same organisms. The "-omics" ending means "all of one kind", as in genomics, all the genes. *(Phase 8)*

---

## Group 2: The experiment

- **SynCom** (synthetic community): a group of known strains combined and applied together on purpose. *Synthetic* means "assembled by people from known parts", not fake.
- **Mini5SynCom**: the source paper's name for one community of exactly five strains.
- **Strain pool**: the 35 strains the communities were drawn from. The number was worked out, not guessed: with 136 communities of five, 35 strains lets each strain appear in about 20 communities, enough repeats for the statistics to mean something.
- **Prevalence** (of a strain): how many communities it appears in. In the 136 training communities each strain appears 13 to 24 times, 19.4 on average, close to the 20 the design aimed for.
- **CFU** (colony-forming unit): the standard way to count live bacteria. Spread a diluted sample on a nutrient jelly, let each living bacterium grow into a visible dot (a **colony**), count the dots, and scale back up by the dilution. One CFU is roughly one living bacterium that could grow.
- **CFU per gram of fresh weight**: the count divided by the plant's weight, so a big plant isn't counted as worse off just for offering more surface. Crime figures per 100,000 residents work the same way, so a city isn't automatically "worse" than a village.
- **Order of magnitude**: a factor of ten. Two orders of magnitude larger means a hundred times larger.
- **Log scale**, **log10**: replacing a number by roughly how many zeros it has: 1,000 becomes 3 and 1,000,000 becomes 6. Pathogen counts here run from a few thousand to a few billion per gram of leaf, so on an ordinary scale the large values would squash everything else flat. On a log scale each step means ten times more, which is how biologists think about these numbers ([`figures/log_scale.png`](../figures/log_scale.png)).
- **dpi** (days post infection): days since the pathogen was applied. The study measured at 14 dpi.
- **Replicate**: a repeat of the same condition, to see how much of the variation is noise. Several plants received each community.
- **Control**: a condition included only to compare against: here, sterile plants without the pathogen (what does a healthy plant look like?), sterile plants with it (what does an unprotected infection look like?), all 35 strains at once, and two reference communities grown in every round.
- **Experiments 1, 2 and 3**, **rounds**: the study's three rounds, `Exp1`, `Exp2` and `Exp3` in the files. Experiments 1 and 2 hold the 136 training communities. Experiment 3, run separately, holds 68 new communities which, with the two reference communities, make the 70 used only to test the finished models.
- **Box**: a sealed, sterile container of four plants, all given the same community. Each round had 80 boxes.
- **Reference community**: a community grown in every round, so the rounds can be compared with each other: here `Mix69` and `Mix70`, labelled `SynCom-High` and `SynCom-Low` in the plant file.
- **Between-round reference plants**: Phase 3's name for the 16 plants of `Mix69` and `Mix70` grown in rounds 1 and 2. Their communities are test communities, so these plants never train a model; they're kept for comparing the rounds.
- **TRUE, FALSE and TBD**: the marks in the `IncludedAnalysis` column of the plant files: kept, left out, or "to be decided". The 144 `TBD` plants sat in boxes that were dropped and recovered; the authors' per-plant machine-learning tables keep 120 of them. *(Phase 2 guide, section 5)*
- **Screen** (or screening): testing many candidates in the same way to find the few worth a closer look.

---

## Group 3: Your computer and the command line

- **Operating system** (OS): the software a computer runs on: Windows, macOS or Linux. This project works on all three, and the guides show each version where a command differs.
- **RHEL** (Red Hat Enterprise Linux): a version of Linux common on company servers; **RHEL 8** is one release. **Rocky Linux** and **AlmaLinux** are free rebuilds of it, and everything said about RHEL 8 applies to them.
- **Virtual machine** (VM): a whole computer simulated inside another one.
- **Terminal** (macOS and Linux) or **PowerShell** (Windows): a window where you type commands instead of clicking. Slower to learn and far more precise afterwards, and every instruction can be written down exactly, which is why the guides use it.
- **Git Bash**: a small terminal that comes with Git for Windows and understands macOS and Linux commands. Windows users run the safety gate in it.
- **Command**: one instruction typed into the terminal, such as `python --version`.
- **Prompt**: the text the terminal shows before the cursor while it waits for you. The guides show commands without it, so a whole line can be copied.
- **Shell**: the program inside the terminal that reads commands. **bash** and **zsh** are the usual ones on Linux and macOS.
- **Directory**: a folder. Command lines say directory; the two words mean the same.
- **Path**: the address of a file or folder. `docs/01-setup.md` is a **relative path**, starting from the project folder; `/Users/<you>/projects/realsignal/docs/01-setup.md` is an **absolute path**, starting from the top of the disk. Windows separates folders with `\`, macOS and Linux with `/`. The guides always name files by their path from the project folder.
- **Project folder**: the folder that holds `README.md`. Every command in the guides is run from there.
- **Working directory**: the folder the terminal is currently in; commands act relative to it. `cd` changes it, and `pwd` (macOS and Linux) or `Get-Location` (Windows) prints it.
- **Environment variable**: a named setting the computer holds in memory for programs to read, used for things such as passwords that must never be written into files.
- **PATH**: the environment variable listing the folders searched when you type a command name. "Command not found" after installing something usually means its folder isn't on the PATH.
- **sudo**: "run this as administrator" on macOS and Linux. It asks for your password.
- **chmod +x**: marks a file as runnable on macOS and Linux. A file can be readable without being runnable, which is why `./check-public-safe.sh` can say `Permission denied`.
- **Look-alike characters**: characters that resemble keyboard ones but aren't: a long dash for `-`, curly quotes for `"`. Word processors and web pages insert them, and they break commands pasted into a terminal ([`docs/01-setup.md` section 14](01-setup.md#14-copy-commands-safely)).

---

## Group 4: Python and packages

- **Python**: the main language of this project, readable and the standard for data work and machine learning.
- **Script**: a file of Python instructions ending in `.py`, run from top to bottom.
- **Function**: a named, reusable piece of code that takes inputs and gives back a result, such as `compute_md5(path)`.
- **Module, package, library**: code someone else wrote that your code can use. A module is one file, a package a folder of modules, and library is the everyday word for either.
- **Import**: making a module's code available in yours (`import pandas`).
- **`sys.path`**: the list of folders Python searches when it meets an `import`. The scripts add `src/` to it, so `from realsignal import helpers` finds `src/realsignal/helpers.py`.
- **pip**: Python's package installer. `python -m pip` makes sure it's the pip that belongs to the Python you're using.
- **PyPI** (the Python Package Index): the public warehouse pip downloads from.
- **Virtual environment** (`.venv`): a private copy of Python and its packages for one project only, so two projects needing different versions of the same package can't break each other. Like a pencil case per subject instead of one shared drawer.
- **Activate** (a virtual environment): telling the terminal to use this project's environment for the session. `(.venv)` at the start of the prompt shows it's active. Every new terminal needs it again.
- **`requirements.txt`**: the list of packages the project needs, with version ranges. `python -m pip install -r requirements.txt` rebuilds the environment from it.
- **`requirements.lock.txt`**, **lock file**: the exact versions installed on a computer where everything worked, written by `python -m pip freeze`. The ranges make an install possible on every system; the lock file records what a working one looked like.
- **Version range**: `pandas>=2.2,<4.0` means any version from 2.2 up to, but not including, 4.0.
- **pandas**: the Python library for tables of data, a spreadsheet driven by typed instructions so every step is recorded and repeatable.
- **DataFrame**: pandas' word for one table, with rows and named columns.
- **NumPy**: the library under pandas that does fast arithmetic on large blocks of numbers.
- **requests**: the library that downloads files over the internet.
- **hashlib**: Python's built-in library for checksums such as MD5.
- **pathlib**: Python's built-in library for file paths. It writes `\` or `/` to suit the operating system, so the same code runs on all three.
- **Matplotlib**: the library that draws the figures as image files.
- **scikit-learn** (`sklearn` in code): the standard Python machine-learning library, with models and the tools to measure them. *(Phase 5)*
- **pytest**: the tool that runs the automated tests (`pytest -q`).
- **Test**: a small program that checks another program does what it should, and fails loudly if not. A **unit test** checks one small piece on its own.
- **`pytest.ini`**: pytest's settings file; here it tells pytest to look only in `tests/`.
- **Stand-in** (tests): a small fake version of something big or slow, such as the tiny archive `tests/test_fetch_data.py` builds instead of downloading 239 MB, or the small web server `tests/test_fetch_sources.py` runs on your own computer in place of NCBI. Programmers also call these *mocks* or *fixtures*.
- **Editor**, **VS Code**: a program for writing code comfortably, with colours and error highlighting. VS Code is free and the same on all three systems.

---

## Group 5: Git and GitHub

- **Version control**: recording every change to your files, so you can see what changed, when and why, and go back.
- **Git**: the version-control program on your computer ([`docs/GIT_WORKFLOW.md`](GIT_WORKFLOW.md) explains it from zero).
- **GitHub**: the website that keeps an online copy of a Git project, for backup, sharing and a public home.
- **Repository** (repo): one project tracked by Git, its files plus their whole history.
- **Local, remote, `origin`**: local is the copy on your computer, remote the copy on GitHub; `origin` is the usual nickname for the remote.
- **Clone**: making a local copy of a remote repository, history included.
- **Working tree**, **staging area**, **history**: the three places a change passes through: your files, the changes picked for the next commit, and the permanent record ([`docs/GIT_WORKFLOW.md` section 2](GIT_WORKFLOW.md#2-the-three-places-a-change-can-be)).
- **Stage** (`git add`): picking changes for the next commit.
- **Commit**: one permanent, dated, labelled save point. Its message should say why.
- **Push**, **pull**: sending your commits to GitHub; bringing GitHub's commits to your computer.
- **Branch**: an independent line of work. This project has three: `develop` (where work happens), `beta` (a checkpoint copy) and `master` (the published state).
- **`git switch`**: moving between branches. (Older guides use `git checkout`.)
- **Fast-forward**, **`--ff-only`**: moving a branch forward to a newer commit when nothing has gone a different way. `--ff-only` means "only if it's that simple; otherwise stop and tell me".
- **Tracked, new and ignored files**: tracked files are already in Git; new (untracked) files are in the folder but not yet in Git, and `git add -A` will add them; ignored files are listed in `.gitignore`, and Git never adds them. The safety gate checks the first two.
- **`.gitignore`**: the list of files and folders Git must never record: the virtual environment, downloaded data, secrets, private notes, operating-system clutter.
- **`git rm --cached`**: takes a file out of Git while leaving it on your disk.
- **`.gitkeep`**: an empty file whose only job is to make Git keep an otherwise empty folder.
- **Tag**: a permanent name pinned to one commit, such as `v0.1.0`. Unlike a branch, it never moves.
- **Safety gate** (`check-public-safe.sh`): the script run before every push. It refuses the all-clear if a secret, downloaded data, a private note, a database file, a path from one particular computer or operating-system clutter would be published ([`docs/01-setup.md` section 13](01-setup.md#13-the-safety-gate)). `.gitignore` is the lock on the door; the gate is the check at the exit.
- **Credential**, **secret**, **API key**: a private password-like string that lets a program use a service. It must never be committed; one that reaches a public repository has to be replaced.
- **Hidden records in pictures** (metadata): information stored inside an image file that doesn't show on screen, such as the GPS position where a photo was taken (**EXIF**) or a record from the program that last edited or exported it (**content credentials**, or **C2PA**). The safety gate refuses pictures that carry them.
- **`.DS_Store`**: a hidden file macOS writes into folders to remember how they're displayed. Harmless, but clutter in a repository, so `.gitignore` excludes it. **Thumbs.db** and **desktop.ini** are the Windows equivalents.

---

## Group 6: Data, files and downloads

- **CSV** (comma-separated values): the simplest table file: plain text, one row per line, columns separated by commas. **TSV** uses tabs instead.
- **Excel file** (`.xlsx`): a spreadsheet file, with sheets, formatting and formulas; common for published scientific data.
- **JSON**: a plain-text format for structured information, readable by people and programs. `data/raw/fetch_log.json` is one.
- **Archive** (`.zip`): many files packed, usually compressed, into one.
- **Extract**, **unzip**: unpacking an archive into its files.
- **Zip slip**: a trick where an archive contains a name like `../../somefile`, so unpacking it carelessly writes outside the intended folder. `scripts/fetch_data.py` refuses such entries.
- **`__MACOSX`**: a folder of hidden extra files that macOS adds to zip files made on a Mac. The download script skips it.
- **Checksum**, **hash**, **MD5**: a short code calculated from every byte of a file; change one byte and it changes completely. MD5 is the method Zenodo and NCBI publish. A matching checksum proves you hold exactly the published file; it says nothing about whether its contents are right.
- **SHA-256**: a newer checksum method, 64 characters long. MD5 still catches accidental damage, but two different files with the same MD5 can be made on purpose; no such weakness is known for SHA-256, so the project uses it for its own pins.
- **Pinning**, **trust on first use**: when a publisher gives no checksum, recording the checksum of the first download and checking every later download against it. The pins live in the `pinned_sha256` column of `sources/files.csv`.
- **File signature**: the first few bytes every file of one kind starts with. Every `.xlsx` workbook starts with `PK`, every `.gz` file with the bytes `1f 8b`. A download that starts differently isn't the file it claims to be (often a web page).
- **HTTPS**, **certificate**: an address starting `https://` means the connection is encrypted and the website proves who it is with a certificate, a statement signed by an issuer that browsers and programs trust. Python checks the signature against a list of trusted issuers; **certifi** is a package holding such a list. `CERTIFICATE_VERIFY_FAILED` means the check couldn't be made, often because that list is missing ([`docs/01-setup.md` section 17](01-setup.md#17-troubleshooting)).
- **DOI** (digital object identifier): a permanent address for a published paper or dataset that keeps working when websites are reorganised. `10.5281/zenodo.10118600` is the dataset's.
- **Zenodo**: a free, permanent public archive for research data and code, run by CERN. The study's data and code are deposited there.
- **HTTP**, **HEAD request**: HTTP is how browsers and programs talk to websites. A HEAD request asks for a file's details (size, type) without its contents, which is what the download script's `--probe` does.
- **Streaming** (a download): reading a large file a piece at a time instead of loading it all into memory at once.
- **`.part` file**: where the download script writes until the download is complete, then renames it. A connection that drops leaves an obviously unfinished `.part` file, never something that looks complete.
- **Idempotent**: safe to run again and again with the same result. The download script checks an existing archive instead of downloading it twice.
- **Raw data**: the downloaded files exactly as received. Read-only, kept in `data/raw/`, because everything else is rebuilt from them.
- **Processed data**: anything your own code derives from raw data. It can always be rebuilt, so it's never edited by hand either.
- **Manifest**: a list of every file in a collection. `data/raw/manifest.csv` lists every file in the archive with its folder, type and size.
- **Provenance**: the written history of a piece of data: where it came from, when, and what's been done to it since. `data/raw/fetch_log.json` records it for the download.
- **Supplementary data**, **supplementary information**, **Source Data**: files published alongside a paper on its web page: the data behind it, and (Source Data) the numbers behind each figure. The publisher of the *Nature* journals calls them *electronic supplementary material* (ESM), hence file names such as `41564_2021_997_MOESM3_ESM.xlsx`.
- **Data availability statement**: the paragraph in a paper saying where its data can be found and on what terms.
- **Source register**: a table recording, for every data source, its terms, how to get it, when it was checked and whether it could be obtained, including sources that couldn't be. This project's is `sources/register.csv`.
- **NCBI** (National Center for Biotechnology Information): the US centre that keeps one of the world's main public collections of DNA sequences and genomes, free to search and download.
- **RefSeq**: NCBI's curated collection, with one reference record for each genome assembly. Its accessions start with `GCF_`; the records as originally submitted start with `GCA_`.
- **Accession**: the permanent ID of a record in a database, such as `GCF_001422065.1`. The number after the dot is the version: a corrected record gets a new one, and the old one stays available.
- **BioProject**: an NCBI record that groups all the data from one research project, so a project's genomes can be found together.
- **FASTA** (`.fna`, `.fasta`): a plain-text format for DNA sequences. A line starting with `>` names a sequence; the lines after it hold its letters.
- **gzip** (`.gz`): a common way of compressing one file. Python reads `.gz` files directly with its `gzip` module, without unpacking them first.
- **Mirror**: a second address for the same file, tried when the first fails. `sources/files.csv` lists them separated by ` | `.
- **Rate limit**: the most requests a website accepts from one program in a given time. `scripts/fetch_sources.py` pauses after every request to NCBI to stay inside it.

---

## Group 7: Databases and data engineering

- **Database**: an organised store of tables built to answer questions quickly.
- **SQL**: the common language for asking databases questions: `SELECT ... FROM ... WHERE ...`.
- **Schema**: two related meanings. The declared structure of a database (its tables, their columns and the type of each), and, in DuckDB and dbt, a named group of tables inside one database, like a folder: the warehouse has the schemas `raw`, `staging`, `intermediate`, `marts` and `reference`.
- **Wide and long format**: two shapes for the same table. Wide has one column per strain (the design file's 35 columns of 1s and 0s); long has one row per community-and-strain pair (`marts.community_member`). Different tools want different shapes, and a long table doesn't change shape when the library grows.
- **UNPIVOT**: the SQL command that turns a wide table into a long one: each column becomes rows. `dbt/models/staging/screen/stg_screen__design.sql` uses it on the design.
- **Presence/absence matrix**: a wide table of 1s and 0s saying which strains are in which community.
- **Harmonisation**: making several sources agree: one name for each thing, one shape, and written rules for disagreements.
- **ETL**, **ELT**: extract, transform, load (reshape the data before storing it) and extract, load, transform (store it first, reshape it inside the database). dbt works the ELT way.
- **dbt** (data build tool): a tool that turns a folder of SQL files into a pipeline with an order, tests and documentation. **dbt Core** is the free, open-source command-line version this project uses.
- **Model** (in dbt): one SQL file that builds one table from others. Not the same as a machine-learning model (Group 8).
- **Staging, intermediate, marts**: dbt's usual layers: tidy each source on its own, combine them, then build the final tables people use.
- **`ref()`, `source()`**: how a dbt model names the tables it reads, `{{ ref('stg_screen__plants') }}` for another model and `{{ source('raw', 'screen_plants') }}` for a raw table. dbt fills in the real names and learns the order to build things in.
- **Jinja**, **macro**: Jinja is the template language in the `{{ }}` and `{% %}` parts of a dbt file, filled in before the SQL runs. A macro is a reusable piece of it, such as `strain_id()`, which gives every strain one spelling.
- **View**, **table**: a view is a saved query that runs again each time something reads it; a table stores its rows.
- **Materialisation** (dbt): how a model is stored: as a view, as a table, or otherwise. Set per layer in `dbt/dbt_project.yml`.
- **Seed** (dbt): a small CSV table written by hand, committed with the project, and loaded by dbt like any other table. Not the same as a random seed (Group 8).
- **Var** (dbt): a setting in `dbt/dbt_project.yml` that models read with `var('...')`, such as `keep_undecided_plants`. It can be changed for one run: `dbt build --vars "{keep_undecided_plants: false}"`.
- **Adapter** (dbt): the part of dbt that talks to one kind of database; `dbt-duckdb` is the one for DuckDB.
- **Profile** (dbt): a connection, saying which database to use and where: `dbt/profiles.yml`.
- **Dimension**, **fact**, **bridge table**: a dimension has one row per thing (a strain, a community); a fact has one row per event or measurement (a plant, a weight, an inhibition) and points at the dimensions; a bridge links two dimensions that relate many to many (`community_member`: a community holds several strains, and a strain is in many communities).
- **Key**: the column that names each row once and only once (`strain_id` in `dim_strain`). A column in another table that holds those names points at that table.
- **Join**: a query that combines two tables on a column they share, such as plants and communities on `community_id`.
- **Data test**: an automatic check on the data itself, such as "every strain name is unique" or "no outcome is missing". In dbt it's a query that returns the rows breaking the rule, and it passes when there are none.
- **Generic test**, **singular test** (dbt): a generic test is written as one line next to a column (`unique`, `not_null`, `accepted_values`, `relationships`, which checks that every name a column points with exists in the table it points at, and this project's `accepted_range`); a singular test is a SQL file of its own in `dbt/tests/`, for a rule that spans several tables.
- **`dbt build`**, **`dbt show`**, **`dbt docs`**: build loads the seeds, builds every model and runs every test, in order; show runs a query and prints the result; docs generate and docs serve make and open the documentation pages.
- **Manifest**, **catalog** (dbt): two files dbt writes in `dbt/target/`. The manifest records every model, what it reads and every test; the catalog records what the database itself says about each table (columns, types, size). `figures/make_phase3_figures.py` draws the lineage from the manifest.
- **Graph operators** (dbt): the `+` in `--select int_plants+` (this model and everything after it) or `--select +model_plants` (this model and everything it needs).
- **Lineage**: where every table and column came from, drawn as a diagram.
- **DuckDB**: a complete analytical database in a single file, with no server and no setup.
- **Transaction**: a group of changes a database applies all together or not at all. `scripts/load_raw.py` loads every raw table in one, so a failed load leaves nothing half done.
- **Lock** (on a database file): DuckDB lets one program at a time write to a file. A second program trying to write gets `Could not set lock on file` until the first lets go.
- **PostgreSQL** (Postgres): a database built for applications, with many people reading and writing at once. *(Phase 10)*
- **OLAP**, **OLTP**: analytical processing (a few large questions over whole columns, DuckDB's job) and transaction processing (many small reads and writes, PostgreSQL's job).
- **Data warehouse**: a database for analysis that brings all the data together, often rented in the cloud. This project's is a DuckDB file, `data/warehouse/realsignal.duckdb` (Phase 3). **Snowflake** and **Databricks** are well-known cloud ones; this project keeps them as an optional exercise.
- **Spark**: a system that spreads computation over many machines when data won't fit on one. Not used here: the data is small.
- **Pipeline**: a fixed sequence of steps, each doing one job and passing its result on.
- **Orchestration**: running a pipeline's steps in the right order, on a schedule, with retries and a record of what happened. *(Phase 12)*
- **cron**: the traditional scheduler on macOS and Linux: "run this command at this time". It knows nothing about steps depending on each other.
- **Airflow**: an orchestrator: an alarm clock crossed with a checklist that knows which tasks depend on which. **Prefect** is a similar, simpler one. *(Phase 12)*
- **DAG** (directed acyclic graph): Airflow's name for a pipeline: tasks joined by arrows showing which must finish first, with no loops.
- **Retraining**: training the models again when new results arrive, so predictions use everything known so far. *(Phase 12)*

---

## Group 8: Machine learning

- **Machine learning** (ML): getting a computer to learn a pattern from examples instead of following rules written by hand.
- **Model** (ML): the learned pattern, in a form that can make predictions about new cases.
- **Training**: showing the model examples with known answers so it can learn.
- **Feature**: one input the model gets about each example, such as "is Leaf76 in this community?".
- **Label**, **target**, **outcome**: what the model is trying to predict, here the pathogen level or whether the plant was protected.
- **Supervised learning**: learning from examples with known answers. Everything modelled here is supervised. **Unsupervised learning** finds structure without answers (grouping similar things).
- **Classification**, **class**: predicting a category, such as protected or not; each category is a class.
- **Regression**: predicting a number, such as how much pathogen grew.
- **Class imbalance**: when one category is much rarer than the other, so a model that always guesses the common one looks good.
- **Decision tree**: a model that asks a chain of yes-or-no questions ("is Leaf76 present? is Leaf15?") to reach a prediction.
- **Random forest**: hundreds of decision trees, each trained on a slightly different sample, voting together; individual mistakes tend to cancel. *(Phase 5)*
- **Elastic net** (the paper's **GLMNet**): a straight-line model with a penalty that pushes the weights of unhelpful features to zero, leaving a short, readable list of what matters. *(Phase 5)*
- **Regularisation**: any penalty that keeps a model simple, so it doesn't fit noise.
- **Hyperparameter**, **tuning**: a setting chosen before training (how many trees, how strong the penalty), and the search for good settings.
- **Feature importance**, **permutation importance**: how much each feature matters to the model's predictions. Permutation importance measures it by shuffling one feature and seeing how much worse the model gets.
- **Seed**: the starting number for a computer's random choices. The same seed gives the same "random" results, which makes runs repeatable.
- **Multi-omics integration**: adding features from several biological layers (here, genomes, gene clusters and the inhibition network) to see whether they predict better together. *(Phase 8)*
- **MLflow**: a tool that records every training run's settings, scores and model. *(Phase 5)*
- **Deep learning**, **neural network**: large layered models that need far more examples than 136 communities. Not used here.

---

## Group 9: Evaluation

- **Training set**, **test set**: the examples a model learns from, and the ones kept aside to judge it. Here the test set is the 70 communities from a separate experiment.
- **Overfitting**: a model memorising its training examples, noise included, instead of learning the pattern; it scores well on what it has seen and badly on anything new. **Underfitting** is the opposite: too simple to catch the pattern.
- **Cross-validation**, **k-fold**: splitting the training data into k parts (say five), training on four and testing on the fifth, then rotating, so every part is used for testing once.
- **Data leakage**: information from the test side slipping into training, which makes a model look better than it is. Here, plants of one community on both sides of a split would leak.
- **Grouped split**: a split that keeps everything belonging together (all plants of one community) on the same side.
- **Accuracy**: the share of predictions that are right.
- **Precision**, **recall**, **specificity**: of the communities predicted protective, how many were (precision); of the protective ones, how many were found (recall); of the unprotective ones, how many were correctly called unprotective (specificity).
- **Confusion matrix**: a small table of right and wrong predictions, by category.
- **RMSE** (root mean squared error): the typical size of a regression model's mistakes, in the outcome's own units.
- **Baseline**: what a trivial strategy scores (always guessing the commonest answer, say). A score means little without one beside it.
- **Confidence interval**: a range that shows how uncertain a number is. Seventy test communities isn't many, so intervals matter.
- **Bootstrapping**: estimating that uncertainty by recomputing a score on many random resamples of the data.
- **Exploratory data analysis** (EDA): describing data with a few summary numbers and pictures before any model touches it, to find problems while they're cheap to fix. Phase 4 is this project's.
- **Distribution**: how the values of a measurement are spread: where most of them sit, how far they reach, and whether they bunch in one place or several.
- **Histogram**: a bar chart of a distribution. The range is cut into equal steps, with one bar per step, as tall as the number of values that fall in it. A **kernel density estimate** is a smoothed histogram: each value becomes a small bell curve and the curves are added up, so the shape doesn't depend on where the bars start.
- **Median**, **quartiles**, **interquartile range** (IQR): sort the values. The median is the one in the middle, the quartiles cut the sorted list into quarters, and the IQR is the distance from the first quartile to the third, where the **middle half** of the values sit. None of them moves much when a few values are extreme.
- **Mean**, **standard deviation**: the ordinary average, and the typical distance of a value from it. Both are pulled about by extreme values, which is one reason bacterial counts are averaged on a log scale.
- **Bimodal distribution**: values that cluster around two peaks (humps) instead of one, like the pathogen counts (well protected plants low, less protected ones high).
- **Outlier**: a value far from the others it should resemble. Worth checking, not deleting on sight: Phase 4 lists them by a stated rule and keeps them.
- **Batch effect**: a difference caused by when or how a batch of samples was handled rather than by what was being studied. Here each round of the experiment is a batch, and the controls grown in every round show the difference.
- **Normalisation**: rescaling a measurement against a reference, such as subtracting the median of the round's plants with no strains. Phase 4 works out from the numbers how the authors normalised theirs.
- **Sealed test set**: a test set whose results nobody looks at until the final score, so that no choice made before it can have been shaped by it. In Phase 4 the test plants are counted, and no value measured on one is read.
- **Shuffle test**, **permutation test**: checking whether a difference could come from chance alone, by handing the outcomes out at random many times and seeing how large the difference gets when nothing real is going on.
- **Multiple comparisons**: looking at many things at once (35 strains, say) makes it likely that one of them looks impressive by luck. Comparing with the largest of all the shuffled differences, as Phase 4 does, allows for it.
- **Confounding**: two things that go together, so that the effect of one is mistaken for the other's. Strains that often share a community confound each other's one-at-a-time differences.
- **Intraclass correlation**: the share of the variation that lies between groups (communities) rather than within them (the plants of one community): 1 if plants of a community always agree, 0 if the community makes no difference. It sets a rough ceiling for a model that only knows the group.
- **Rank correlation** (Spearman's): how well two rankings agree, from 1 (same order) through 0 (unrelated) to -1 (reversed). Phase 4 uses it to compare strain properties with protection.
- **External validation**: checking a conclusion against data from a separate experiment that played no part in building it. *(Phase 9)*
- **Learning curve**, **data-efficiency curve**: how a result changes as a model gets more training examples; here, how many communities were needed before the conclusion stopped changing. *(Phase 9)*
- **Hit rate**: the share of recommended communities that turn out to protect, compared with communities chosen at random.

---

## Group 10: Science and reproducibility

- **Peer review**: checking of a paper by other scientists before a journal publishes it.
- **Open access**: free to read. Not the same as an **open licence**, which makes something free to reuse.
- **Publisher's terms**: the conditions a publisher sets for material it hosts when no open licence comes with it. Files under publisher's terms are downloaded from the publisher by the scripts and never stored in this repository.
- **Preprint**: a paper shared publicly before peer review.
- **Reproduction**: same data, same question, analysis rebuilt. What this project does first.
- **Replication**: new data from a new experiment, same question. Out of scope here: it needs a laboratory.
- **Extension**: same data, questions the original didn't ask. What this project does second.
- **Reproducibility crisis**: the repeated finding, across many fields, that a large share of published results are hard to reproduce or replicate.
- **Hindsight fitting**: adjusting an analysis until it gives an answer you already know, then presenting it as if found independently. Committing the rebuild before looking at the authors' code (Phase 5, then Phase 6) guards against it.
- **Attribution**: crediting the people whose work you use.
- **CC-BY 4.0**: an open licence allowing anyone to reuse and adapt a work, commercially too, as long as the creators are credited. The study's data uses it.
- **MIT licence**: a short open licence for software: do what you like, keep the copyright notice. This project's code and documents use it.

---

## Group 11: Applications and containers

- **Frontend**, **backend**: the part people see and click, and the part that does the work out of sight ([`docs/00-architecture.md` section 9](00-architecture.md#9-box-7-serving-it-and-three-words-explained)).
- **Streamlit**: a library that turns a Python script into a web app with buttons and sliders, with no web development. **Streamlit Community Cloud** puts such an app online from a GitHub repository. *(Phase 7)*
- **API** (application programming interface): a defined set of addresses other programs can call to ask a system for something.
- **REST**, **endpoint**: REST is the common style for web APIs, where each address (an endpoint, such as `/predict`) does one job.
- **FastAPI**: the Python framework for building the API; it checks every request and documents itself. *(Phase 10)*
- **JavaScript**, **TypeScript**: the language web pages run in, and the same language with types added, which catch whole kinds of mistakes in the editor. *(Phase 11)*
- **React**: a JavaScript library for building web apps out of reusable pieces called **components**. *(Phase 11)*
- **Node.js**, **npm**: a way to run JavaScript outside a browser, and its package installer, used to build the React app. *(Phase 11)*
- **Accessibility**: making an app usable by everyone, including people using screen readers, keyboards only or high contrast. *(Phase 18)*
- **Container**: a program packed with everything it needs to run (language, libraries, code, start-up instructions) so it behaves the same on any computer ([`docs/CONTAINERS.md`](CONTAINERS.md)). *(Phases 10 and 17)*
- **Image**: the read-only template a container starts from.
- **Dockerfile**, **Containerfile**: the text file describing how to build an image.
- **Registry**: a website storing images for download, such as Docker Hub or quay.io.
- **Volume**: storage that outlives the containers using it; databases keep their data in volumes.
- **Bind mount**: a folder on your computer made visible inside a container.
- **Port**, **port mapping**: a numbered door a program listens on; mapping connects a door on your computer to one inside a container (`-p 8000:8000`).
- **localhost**: your own computer, used as an address: `http://localhost:8080` is a page served by a program on your machine to your machine (`dbt docs serve` in Phase 3).
- **Docker**, **Podman**: the two common container engines. Podman runs without a background service and as an ordinary user, and it's the engine Red Hat supports on RHEL 8.
- **Daemon**: a program that runs in the background all the time; Docker's engine is one.
- **Rootless**: running containers as your ordinary user instead of as administrator.
- **OCI** (Open Container Initiative): the open standard both engines follow, which is why an image built by one runs under the other.
- **Compose**, **`compose.yaml`**: a file describing several containers that run together, and the command that starts them all. *(Phase 17)*
- **Multi-stage build**: an image built in two steps, one with all the build tools and a slim final one without them.
- **Layer** (images): one step of an image's build, cached so later builds reuse it.
- **SELinux**: RHEL's security system that labels every file and decides which programs may use which labels; `:Z` on a mount relabels a folder for a container.
- **Linger** (`loginctl enable-linger`): keeps a user's containers running after logout on Linux.
- **EPEL** (Extra Packages for Enterprise Linux): an extra package collection for RHEL and its rebuilds, where `podman-compose` comes from.
- **WSL2** (Windows Subsystem for Linux): a real Linux kernel running inside Windows, which both engines use there.
- **Podman machine**: the small hidden Linux virtual machine Podman runs on macOS and Windows.
- **Kubernetes**: a system for running containers across a fleet of machines. Not needed here.
- **CI/CD** (continuous integration and delivery): tests and builds that run automatically on every push. **GitHub Actions** is GitHub's built-in way to do it. *(Phase 18)*

---

## Group 12: Graphs and the AI features

- **Graph**: things (nodes) joined by relationships (edges): strains joined by "inhibits", for example.
- **Ontology**: an agreed vocabulary for a domain: which kinds of thing exist and how they may relate ("a strain CARRIES a gene cluster"). *(Phase 13)*
- **Knowledge graph**: data stored in the shape the ontology describes, so questions can follow chains of relationships. *(Phase 13)*
- **Neo4j**, **Cypher**: a graph database, and its query language. *(Phase 13)*
- **NetworkX**: a Python library for graphs in memory, with no database; used to show the idea before Neo4j.
- **LLM** (large language model): a program trained on vast amounts of text to write text. **Local model**: one that runs on your own computer, so nothing leaves it.
- **Hallucination**: an LLM stating something fluent and false.
- **RAG** (retrieval-augmented generation): looking things up in your own data first, then letting a language model write an answer from what was found. *(Phase 14)*
- **GraphRAG**: RAG where the lookup walks a knowledge graph, so answers can follow relationships. *(Phase 14)*
- **Embedding**: a list of numbers representing a piece of text so that similar meanings get similar numbers, which makes searching by meaning possible.
- **Grounding**, **citation**: tying every statement in an answer to the source it came from, so it can be checked.
- **MCP** (Model Context Protocol): a shared standard for plugging tools and data into AI assistant apps. An **MCP server** offers a project's tools that way. *(Phase 15)*
- **Agent**: a program that uses a language model to decide which tools to call, looks at the results and decides the next step, until a task is done. *(Phase 16)*
- **Guardrails**: limits on what an agent may do: a fixed set of read-only tools, a maximum number of steps, a full log.
- **Active learning**: choosing the next experiments to teach a model as much as possible, then retraining on their results. A later product feature ([`docs/PRODUCT_ROADMAP.md`](PRODUCT_ROADMAP.md#a3-closing-the-loop-new-results-in-better-suggestions-out)).

---

## Group 13: R and the three-way comparison

- **R**: a programming language built by statisticians for statistics, and the language of the original analysis. *(Phase 6)*
- **RStudio**: an editor made for R, with a console, a list of everything in memory and a plot viewer. It sits happily alongside VS Code. **Positron** is a newer editor from the same company that handles both R and Python.
- **`.Rproj`**: an RStudio project file. Opening `realsignal.Rproj` starts RStudio in the project folder. *(Phase 6)*
- **CRAN**: the main public warehouse of R packages, R's equivalent of PyPI.
- **renv**, **`renv.lock`**: R's version of the virtual environment and the lock file: a private package library per project, and the exact versions in it. *(Phase 6)*
- **`Rscript`**: the command that runs an R script from the terminal, the way `python` runs a Python one.
- **tidyverse**, **dplyr**: a family of R packages for working with data, and its member for filtering, grouping and summarising tables.
- **caret**, **randomForest**, **glmnet**, **lme4**: widely used R packages for training and evaluating models, random forests, elastic nets and mixed models. Phase 6 records which ones the authors' scripts load.
- **Mixed model**: a statistical model that allows for measurements coming in groups (several plants per community, several boxes per experiment).
- **`.rds`**, **`.RData`**: R's own files for saving objects. They can run code when loaded, so the safety gate keeps them out of Git.
- **R Markdown**: a file mixing text and R code that produces a report.
- **Three-way comparison**: putting the paper's numbers, the authors' code run here, and the Python rebuild side by side, so a difference can be traced to its cause ([`figures/three_way.png`](../figures/three_way.png)). *(Phase 6)*
- **Same task, different language**: a short section in some guides doing one small job in two or three languages, to show what each is good at.

---

## Group 14: The documentation and releases

- **Handbook** ([`docs/HANDBOOK.md`](HANDBOOK.md)): the guide to read first: every stage from day 0 to the finished product, with links to the detail.
- **Stage**, **phase**: a phase is one piece of building work (18 of them); a stage is one step of the Handbook's journey. Stage N+2 is Phase N.
- **Checkpoint**: the list at the end of a stage or guide that says how you know it worked.
- **Markdown** (`.md`): plain text with light marks for headings, lists and links, which GitHub displays as formatted pages. Every guide is Markdown.
- **Mermaid**: diagrams written as text inside Markdown, which GitHub draws as pictures.
- **PNG**, **SVG**: two image formats. PNG stores pixels; SVG stores shapes, so it stays sharp at any size.
- **Interactive page**: an HTML file in `docs/interactive/` that opens in a browser and responds to clicks and sliders, with nothing to install.
- **GitHub Pages**, **`.nojekyll`**: GitHub's free way to publish a folder of a repository as a small website, and the empty file that tells it to publish the folder as it is.
- **Changelog** ([`CHANGELOG.md`](../CHANGELOG.md)): the record of what changed in each version.
- **Semantic versioning**: version numbers of the form MAJOR.MINOR.PATCH; here a new MINOR marks a milestone, a PATCH a fix, and 1.0.0 the first complete release ([`docs/GIT_WORKFLOW.md` section 7](GIT_WORKFLOW.md#7-tags-and-version-numbers)).
- **Milestone**: a planned stopping point where the project is complete in itself, marked by a version tag.
- **Release**: a version published for others to use. *(Phase 18)*
- **`CITATION.cff`**, **`CONTRIBUTING.md`**, **issue template**: a file telling others how to cite the project, a guide to contributing, and a form for reporting a problem on GitHub. *(Phase 18)*
- **Notes from the build**: a section in each phase guide recording things that went wrong or changed while the phase was built.
