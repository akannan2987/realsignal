# Glossary — every term, in plain language

This is a contract. **Every term used anywhere in this repository is
defined here**, in ordinary words, with an everyday comparison wherever
one helps. If you meet a word in any document, any code comment or any
part of the application that is not explained here, that is a bug in
the documentation — please open an issue.

Terms are grouped by where you first meet them. Within each group they
are ordered so that earlier entries do not depend on later ones — you
can read a group top to bottom without ever hitting a word that hasn't
been introduced.

**Contents**

- [Group 1 — The biology](#group-1--the-biology)
- [Group 2 — The experiment](#group-2--the-experiment)
- [Group 3 — Your computer and the command line](#group-3--your-computer-and-the-command-line)
- [Group 4 — Python and packages](#group-4--python-and-packages)
- [Group 5 — Git and GitHub](#group-5--git-and-github)
- [Group 6 — Data, files and databases](#group-6--data-files-and-databases)
- [Group 7 — Machine learning](#group-7--machine-learning)
- [Group 8 — Evaluation and honesty](#group-8--evaluation-and-honesty)
- [Group 9 — Science and reproducibility](#group-9--science-and-reproducibility)

---

## Group 1 — The biology

**Bacterium** (plural: **bacteria**) — a single-celled living organism,
far too small to see. Roughly a thousandth of a millimetre across. They
are everywhere: soil, water, your skin, plant leaves. Most are harmless
or helpful; a minority cause disease.

**Microbe** — an umbrella word for any organism too small to see:
bacteria, fungi, and others. In this project, all our microbes are
bacteria.

**Strain** — one specific, named, genetically distinct type of
bacterium, maintained as a living culture in a laboratory. *Analogy:*
"dog" is a species; "the Labrador in kennel 15" is a strain. Our
strains have names like `Leaf15`, `Leaf68`, `Leaf76` — they were
isolated from real plant leaves and numbered as they were catalogued.

**Genus** — the family-name half of a bacterium's scientific name.
*Pseudomonas* Leaf15 means "the strain numbered Leaf15, which belongs
to the genus *Pseudomonas*". Written in italics by convention.
*Analogy:* the surname in "Smith, John".

**Microbiome** — the whole community of microbes living on or in
something. Your gut microbiome; a leaf's microbiome. *Analogy:* the
full population of a town, as opposed to one named resident.

**Microbiota** — used interchangeably with microbiome in most writing,
including in the source paper. Strictly, *microbiota* is the collection
of organisms and *microbiome* is that collection plus their genes and
surroundings. This project treats them as the same thing and says so.

**Commensal** — a microbe that lives on a host without harming it.
From the Latin for "sharing a table". All 35 strains in this project
are commensals. *Analogy:* a lodger who pays rent, breaks nothing, and
occasionally fixes the boiler.

**Pathogen** — a microbe that causes disease. The one used here is
*Pseudomonas syringae* pv. *tomato* DC3000, usually shortened to
**Pst**. It infects plant leaves and multiplies inside them.

**Infection** — deliberately applying the pathogen to the plants, in
this experiment by spraying a measured dose.

**Inoculation** — deliberately applying the *harmless* strains to the
plants, before infection. The distinction between inoculation
(commensals) and infection (pathogen) is the source paper's convention
and this project keeps it.

**Colonisation** — how much of a microbe has established itself on a
plant. This is the thing actually measured. High pathogen colonisation
= the pathogen thrived = the plant was not protected.

**Biocontrol** — protecting a plant from disease using living organisms
instead of chemicals. *Analogy:* introducing ladybirds to eat aphids,
rather than spraying insecticide.

**Protective strain / pathogen-reducing (PR) strain** — a strain whose
presence measurably lowers pathogen colonisation. The source paper
identified three: *Pseudomonas* Leaf15, *Rhizobium* Leaf68 and
*Acidovorax* Leaf76.

***Arabidopsis thaliana*** — thale cress, a small, fast-growing weed
that plant scientists use as their standard experimental plant, the way
medical researchers use mice. Small, quick, cheap, and enormously well
studied. Often shortened to *Arabidopsis*.

**Phyllosphere** — the above-ground surface of a plant (the leaves and
stems) considered as a habitat for microbes. *Analogy:* "the rooftops"
as an ecosystem for pigeons.

**Axenic** — completely free of any other organism. An axenic plant is
a sterile plant with no microbes on it at all — the blank control that
everything else is compared against. *Analogy:* a clean room before
anyone walks in.

**Gnotobiotic** — an experimental system in which *every* organism
present is known and deliberately put there. Not sterile, but with a
fully known cast list. *Analogy:* a stage play where you know every
actor by name, versus a crowd scene filmed on a real street.

---

## Group 2 — The experiment

**SynCom** (synthetic community) — a group of known strains
deliberately combined and applied together. "Synthetic" here means
*assembled by humans from known parts*, not artificial or fake.
*Analogy:* a chosen 5-a-side team, versus whoever happens to turn up at
the park.

**Mini5SynCom** — the source paper's name for one team of exactly five
strains. 136 of them formed the training set.

**Strain pool** — the 35 strains that teams were drawn from. Choosing
35 was a calculation, not a guess: with 136 teams of 5 drawn from 35
strains, each strain appears in roughly 20 teams, which is enough
repetition for the statistics to mean anything.

**Prevalence** (of a strain) — in how many of the teams that strain
appears. Roughly 20 here, by design.

**CFU** (colony-forming unit) — the standard way of counting live
bacteria. You spread a diluted sample on a jelly-like nutrient plate;
each living bacterium that can grow forms one visible dot, called a
colony; you count the dots and multiply back up by the dilution.
*Analogy:* estimating how many fish are in a lake by netting one
measured bucket and scaling up. One CFU ≈ one living bacterium that was
able to grow.

**CFU per gram of fresh weight** — CFU counted, divided by the weight
of the plant it came from. Necessary because a bigger plant offers more
surface to live on, so raw counts would unfairly favour big plants.
*Analogy:* comparing crime rates per 100,000 residents instead of raw
crime counts, so a city isn't automatically "worse" than a village.

**Orders of magnitude** — factors of ten. Something two orders of
magnitude larger is 100× larger. Bacterial counts span so many
factors of ten that we always work with them on a logarithmic scale
(below).

**Log10 transformation** — replacing a number by "how many zeros it
has", roughly. 1,000 becomes 3; 1,000,000 becomes 6. *Why:* our
pathogen counts range from about 10,000 to about 1,000,000,000. On a
plain scale, the huge values would swamp everything and any chart would
be a flat line with one spike. On a log scale, "a tenfold difference"
is the same visual distance everywhere, which is exactly how biologists
think about these numbers. This is not a trick to make data look nicer;
it is choosing the ruler that matches the quantity.

**dpi** (days post infection) — days since the pathogen was applied.
Measurements here were taken at 14 dpi.

**Replicate** — a repeat of the same condition, to see how much of the
variation is just noise. Here, several plants received each team.

**Control** — a condition included specifically so you have something
to compare against. This experiment's controls include axenic
non-infected plants (nothing applied — what does a healthy plant look
like?), axenic infected plants (pathogen only, no protectors — what
does an unprotected infection look like?), and a community of all 35
strains at once.

**Experiment 1 / 2 / 3** — the source study's three rounds.
Experiments 1 and 2 together produced the 136 training teams.
Experiment 3 was run separately and produced 70 further teams, none
matching a training team, used purely to test the finished models. That
separation is the single most important design decision in the whole
study, and Group 8 explains why.

---

## Group 3 — Your computer and the command line

**Operating system (OS)** — the software your whole computer runs on:
Windows, macOS, or Linux. This project works on all three; where a
command differs, the documents show all versions.

**RHEL** (Red Hat Enterprise Linux) — a version of Linux common on
company servers. **RHEL 8** is one release of it. If you are on a work
Linux machine, this is often what you are on.

**VM** (virtual machine) — a whole computer simulated inside another
computer. Common at work: your Windows laptop connects to a Linux VM
somewhere in a data centre. Everything in these documents works the
same either way.

**Terminal** (macOS/Linux) / **PowerShell** (Windows) — a window where
you type commands as text instead of clicking. *Analogy:* ordering at a
counter by saying exactly what you want, rather than pointing at
pictures on a menu. Slower to learn, far faster and far more precise
once learned, and — crucially — every instruction can be written down
exactly, which is why documentation uses it.

**Command** — one instruction typed into the terminal, e.g.
`python --version`.

**Prompt** — the text the terminal shows before your cursor, waiting
for input. In these documents commands are shown *without* the prompt,
so you can copy the whole line safely.

**Shell** — the program inside the terminal that reads your commands.
**bash** and **zsh** are the usual ones on Linux and macOS,
**PowerShell** on Windows.

**Directory** — a folder. The two words mean the same thing; command
lines say "directory".

**Path** — the address of a file or folder.
`docs/01-setup.md` is a **relative path** (starting from where you
are); `C:\Users\me\realsignal\docs\01-setup.md` or
`/home/me/realsignal/docs/01-setup.md` is an **absolute path**
(starting from the top of the disk). Windows separates folders with
`\`, macOS and Linux with `/`.

**Working directory** — the folder your terminal is currently "sitting
in". Commands act relative to it. `cd` changes it; `pwd` (macOS/Linux)
or `Get-Location` (Windows) prints it. *Analogy:* which room of the
house you are standing in — "fetch the towels" means something
different in the kitchen than in the bathroom.

**Environment variable** — a named setting your computer holds in
memory that programs can read. Used for things you must not write down
in files, like passwords. Not needed for this project's public data,
but defined here because it appears in the setup document's safety
notes.

**PATH** (the environment variable) — the list of folders your computer
searches when you type a command name. If you install Python but the
terminal says "command not found", nine times out of ten Python is
installed but its folder is not on your PATH. *Analogy:* the shop
exists, but it isn't on the map your driver is using.

---

## Group 4 — Python and packages

**Python** — the programming language this project is written in.
Widely used, readable, and the standard language for data work and
machine learning.

**Script** — a file of Python instructions, ending in `.py`, that runs
from top to bottom when you execute it. *Analogy:* a recipe card.

**Module / package / library** — reusable code somebody else wrote that
you can use in your own. Strictly: a *module* is one file, a *package*
is a folder of modules, a *library* is the informal word for either.
*Analogy:* rather than forging your own screwdriver, you buy one.

**pip** — Python's package installer: the command that fetches
libraries from the internet and puts them where Python can find them.
*Analogy:* the app store for Python code.

**PyPI** (the Python Package Index) — the public warehouse pip
downloads from. Pronounced "pie-pea-eye".

**Virtual environment** (**venv**) — a private, sealed copy of Python
and its packages, belonging to one project only. **Why this matters
more than it sounds:** project A may need pandas version 1, project B
pandas version 2. Install both system-wide and one of them breaks. A
virtual environment gives each project its own sealed toolbox, so they
cannot interfere. *Analogy:* a chef's knife roll for each restaurant,
rather than one shared drawer everybody rummages in. This project's
lives in a folder called `.venv`.

**Activate** (a virtual environment) — telling your terminal "for this
session, use *this* project's toolbox". Until you activate, `python`
means the system's Python, not the project's. You re-activate every
time you open a new terminal; forgetting to is the single most common
beginner confusion, and the setup guide gives you a way to check.

**requirements.txt** — a plain text file listing exactly which packages
and which versions this project needs. `pip install -r requirements.txt`
rebuilds the toolbox from it. *Analogy:* the parts list that comes with
flat-pack furniture — with it, anybody can assemble the same thing.

**Pinning** (a version) — writing `pandas==2.2.3` rather than `pandas`,
so everyone gets the identical version. Unpinned dependencies are one
of the top reasons old analyses stop working: the code didn't change,
the library underneath it did.

**pandas** — the Python library for working with tables of data.
*Analogy:* a spreadsheet you drive with typed instructions instead of a
mouse — so every step is recorded, repeatable and reviewable.

**DataFrame** — pandas' name for one table: rows, named columns, like a
spreadsheet sheet.

**NumPy** — the library underneath pandas that does fast arithmetic on
large blocks of numbers.

**scikit-learn** — the standard Python machine-learning library.
Provides both the models and, just as importantly, the tools to measure
them honestly. Written `sklearn` in code.

**Streamlit** — a library that turns a Python script into a web
application with buttons and sliders, without needing web development
skills. *Analogy:* your analysis, but with knobs anyone can turn.

**pytest** — the standard tool for writing **unit tests** (Group 6).

**IDE / editor / VS Code** — a program for writing code comfortably,
with colouring and error highlighting. **VS Code** (Visual Studio Code)
is free and works identically on all three operating systems. Optional
— everything here also works in any text editor — but recommended.

---

## Group 5 — Git and GitHub

**Version control** — a system that records every change to your files,
so you can see what changed, when, and go back.

**Git** — the version-control program itself, running on your machine.
*Analogy:* a save-game system for your work. You choose when to save,
each save is permanent and labelled, and you can load any earlier one.

**GitHub** — a website that stores copies of Git projects online, so
they are backed up, shareable and visible. Git is the tool; GitHub is
the place. *Analogy:* Git is the camera, GitHub is the photo album you
share.

**Repository** (**repo**) — one project tracked by Git: its files plus
its entire history.

**Local / remote** — *local* is the copy on your machine; *remote* is
the copy on GitHub. **`origin`** is the standard nickname for your
remote.

**Clone** — making a local copy of a remote repository, history and
all.

**Stage** (`git add`) — marking which changes you want in your next
save. *Analogy:* putting items on the checkout belt. Nothing is bought
yet.

**Commit** — one permanent, labelled save point. *Analogy:* paying, and
getting a receipt with a description of what you bought. A good commit
message says *why*, not just what.

**Push** — sending your commits to GitHub. **Pull** — bringing GitHub's
commits down to your machine.

**Branch** — an independent line of work. Your files can exist in
several versions at once, each on its own branch, and you switch
between them. *Analogy:* writing a document while keeping a clean copy
you can still show people — the messy draft and the presentable version
live side by side, and you decide when the draft becomes the version.
This project uses three: `develop` (where work happens), `beta` (a
checkpoint), `master` (the presentable state).

**`git switch`** — moving between branches. (Older tutorials use
`git checkout` for this; `switch` is the modern, clearer command and
this project uses it.)

**Fast-forward** (`--ff-only`) — updating a branch by simply moving it
forward when nothing has diverged. Adding `--ff-only` tells Git: *only
do this if it is a clean, no-surprises update; otherwise stop and tell
me.* A safety catch, not a restriction.

**`.gitignore`** — a file listing things Git must never record:
downloaded data, the virtual environment, secrets. *Analogy:* the "do
not photograph" list before a house tour.

**Tag** — a permanent name pinned to one commit, usually a version like
`v1.0.0`. *Analogy:* a bookmark in the history saying "this is the
edition we published".

Full explanations and the exact commands live in
[`GIT_WORKFLOW.md`](GIT_WORKFLOW.md).

---

## Group 6 — Data, files and databases

**CSV** (comma-separated values) — the simplest table file: plain text,
one row per line, columns separated by commas. Opens in anything.

**TSV** — the same, with tab characters instead of commas.

**Excel file** (`.xlsx`) — a spreadsheet file, which can hold several
sheets, formatting and formulas. Common in published scientific data.

**Archive** (`.zip`) — many files packed into one, usually compressed.
*Analogy:* a suitcase.

**Extract / unzip** — unpacking an archive back into its files.

**Checksum** (also **hash**, e.g. **MD5**) — a short code calculated
from a file's exact contents. Change one byte and the code changes
completely. Publishing a checksum lets anyone verify they downloaded
exactly the intended file, uncorrupted and unaltered. *Analogy:* a
tamper-evident seal on a medicine bottle. This project checks the MD5
of the downloaded archive before doing anything with it.

**DOI** (digital object identifier) — a permanent address for a
published thing. Unlike an ordinary web link, a DOI is guaranteed not
to rot: it keeps pointing at the same object even if the hosting
website is reorganised. *Analogy:* an ISBN for a book rather than "the
third shelf in the corner shop".

**Zenodo** — a free, permanent public archive for research data and
code, run by CERN. Scientists deposit datasets there and get a DOI.
This project's data lives there.

**Raw data** — the downloaded files exactly as received, never edited.
Sacred. Every project should have exactly one copy of these and treat
it as read-only, because it is the only thing you can always fall back
to. *Analogy:* the original negatives; you edit prints, never the
negative.

**Processed data** — anything derived from raw data by your own code.
Always disposable, because it can be regenerated.

**Database** — an organised store of tables designed to be questioned
efficiently. *Analogy:* a filing cabinet with a very good index, versus
a pile of paper.

**SQL** (Structured Query Language) — the near-universal language for
asking questions of a database. Reads almost like English:
`SELECT strain, COUNT(*) FROM teams GROUP BY strain`.

**DuckDB** — a complete analytics database that lives in a single file
on your laptop. No server to run, no account, no cost, and it is built
for exactly the kind of wide numeric tables this project produces.
*Analogy:* a filing cabinet you can carry, rather than one bolted into
a warehouse you must first rent.

**Schema** — the shape of a table: which columns exist and what type
each holds. Deciding the schema before loading data is what stops a
column of numbers quietly becoming a column of text.

**Wide vs long format** — the same data, two shapes. *Wide:* one row
per team, one column per strain. *Long:* one row per team-and-strain
combination. Machine learning wants wide; charting often wants long;
converting between them is routine and Phase 2 does it explicitly.

**Presence/absence matrix** — a table of 1s and 0s: was this strain on
this team, yes or no. This is the main input to our models. 136 rows
(teams) × 35 columns (strains).

**Data quality check** — an automated test that the data is as
expected: right number of rows, values in plausible ranges, no
unexplained gaps. Run *before* analysis, because an analysis of broken
data produces confident nonsense. *Analogy:* checking the scales are
zeroed before weighing anything.

**Unit test** — a small automated check that one piece of your code
does what you claim, run in a second, every time. *Analogy:* a smoke
alarm — cheap, boring, and the reason a small problem doesn't become a
large one.

**Idempotent** — safe to run more than once, with the same result.
Our download script is idempotent: run it twice and it notices the file
is already there and verified, rather than downloading 239 MB again.

---

## Group 7 — Machine learning

**Machine learning (ML)** — programs that find patterns in examples
rather than being told the rules explicitly. *Analogy:* you never
listed the rules for recognising your friend's handwriting; you saw
enough of it.

**Model** — the pattern the program has learned, in a form that can
make predictions about new cases.

**Training** — the process of showing the model examples so it can
learn.

**Feature** — one piece of information the model is given about a case;
one input column. Here: "was strain Leaf76 on this team?" — 35 features
in total.

**Label / target / outcome** — the thing being predicted. Here: how
much pathogen grew.

**Supervised learning** — learning from examples where the right answer
is already known. This project is entirely supervised. *Analogy:*
studying with a marked answer key.

**Unsupervised learning** — finding structure with no answer key. Not
used here; defined so the contrast is clear.

**Classification** — predicting which category something falls into.
Here: was this team **protective** or **not protective**?

**Regression** — predicting a number rather than a category. Here: *how
much* pathogen, on the log scale.

The source study did both, and so do we: classification answers "will
this team work?", regression answers "how well?".

**Class** — one of the categories in a classification. Ours are
"protected" and "non-protected".

**Class imbalance** — when one class is much rarer than the other. It
matters because a model can score well by ignoring the rare class
entirely, and accuracy alone will not notice. *Analogy:* a smoke alarm
that never goes off is right 99.9% of the time and still useless.

**Random forest** — a model made of many decision trees, each trained
on a slightly different slice of the data, whose votes are combined.
*Analogy:* asking a hundred reasonably informed people instead of one
expert; individual mistakes cancel out, and the crowd's average is
usually better than any one member. Robust, needs little tuning, and
tells you which features it relied on — which is exactly what this
project needs.

**Decision tree** — a flowchart of yes/no questions ending in an
answer. "Was Leaf76 present? If yes → ...". Easy to read, easy to
overfit, which is why we use a forest of them rather than one.

**Elastic net** (in code: `ElasticNet` / `LogisticRegression` with an
`elasticnet` penalty; in R: `glmnet`) — a linear model that
deliberately keeps itself simple, pushing the weights of unhelpful
features toward zero. *Analogy:* packing for a trip with a strict
weight limit — only genuinely useful items survive. Useful here because
it produces a short, readable list of the strains that matter.

**Regularisation** — the general name for that "keep it simple"
pressure. Without it, a flexible model will happily memorise noise.

**Hyperparameter** — a setting you choose *before* training, as opposed
to something the model learns. How many trees in the forest, how strong
the regularisation. *Analogy:* oven temperature — not part of the
recipe's ingredients, but it decides how they turn out.

**Tuning** — trying several hyperparameter values and keeping the best,
judged only on data that will not later be used to report results.

**Feature importance** — a ranking of how much each input contributed
to the model's predictions. This is the scientific payoff of the whole
project: it is how "which strains matter?" gets answered.

**Permutation importance** — a more trustworthy way of measuring
importance: shuffle one feature's values at random and see how much the
model's performance drops. A big drop means the model genuinely relied
on it. *Analogy:* to find out who matters on a team, have one player
play at random and see how much worse the results get. Slower than the
built-in measures, and harder to fool.

**Seed** (random seed) — a starting number for the computer's
random-number generator. Fixing the seed makes "random" choices repeat
identically, so your results are reproducible. *Analogy:* shuffling a
deck the same way every time so the trick works the same. Important
subtlety: because a seed changes results slightly, an honest project
reports across *several* seeds rather than picking the flattering one.

---

## Group 8 — Evaluation and honesty

This group exists because measuring a model dishonestly is easy and
common, and every term here is a defence against a specific way of
fooling yourself.

**Training set** — the examples the model learns from.

**Test set** (**held-out set**) — examples deliberately kept away from
the model during training, used once at the end to see how it performs
on things it has never encountered. *Analogy:* an exam containing
questions not in the revision pack. Testing a model on its training
data is like grading students on the questions you already gave them
the answers to — everyone scores brilliantly and it means nothing.

**Overfitting** — when a model learns the noise in the training data
rather than the real pattern, and so performs superbly on training data
and badly on anything new. *Analogy:* a student who memorised last
year's paper instead of learning the subject. This is the central
failure of machine learning and almost everything in this group exists
to detect it.

**Underfitting** — the opposite: the model is too simple to capture the
real pattern, and does poorly everywhere.

**Cross-validation** — splitting the training data into *k* parts,
training on *k*−1 and testing on the one left out, then rotating so
every part gets a turn. Gives a more reliable performance estimate than
a single split, and uses all the data. *Analogy:* five practice exams
covering different chapters, rather than one.

**k-fold** — the number of parts, e.g. **5-fold**. The source study
used 10 rounds of 5-fold cross-validation across 8 seeds — thorough,
and we match it.

**Data leakage** — when information from the test set sneaks into
training, making results look better than they are. Often subtle: it
happens if you scale your data using statistics computed over
everything before splitting, or if measurements from the same plant end
up on both sides of a split. The source study explicitly guarded
against the second case by keeping all plants of one team together; we
do the same, and Phase 4 tests for it. *Analogy:* a student who
glimpsed the exam paper — the marks are real, the knowledge isn't.

**Accuracy** — the fraction of predictions that were right. Simple, and
untrustworthy alone whenever classes are imbalanced.

**Precision** — of the cases the model *called* protective, what
fraction really were. Answers: "when it says yes, can I believe it?"

**Recall** (sensitivity) — of the cases that really *were* protective,
what fraction the model found. Answers: "how many did it miss?"

Precision and recall pull against each other, and which one you care
about depends entirely on the cost of each kind of mistake. For strain
screening, missing a genuinely protective strain (low recall) wastes a
discovery; wrongly flagging a useless one (low precision) wastes a
laboratory experiment. The source study achieved 94–100% recall at
72–82% precision — that is, it caught essentially every good team, at
the price of some false alarms, which is the right trade for a
screening tool.

**Specificity** — of the cases that were *not* protective, what
fraction the model correctly rejected.

**Confusion matrix** — the 2×2 table of right and wrong answers of each
kind, from which all of the above are calculated. Worth always looking
at, because it makes the trade-offs visible instead of hiding them
behind one number.

**RMSE** (root mean squared error) — for regression: the typical size
of the model's error, in the units of the thing being predicted. Lower
is better. Because our outcome is log10 pathogen abundance, an RMSE of
1.0 means "typically wrong by about a factor of ten". Sounds terrible,
is actually respectable for a quantity spanning six orders of
magnitude — which is exactly why the next term matters.

**Baseline** — the score you get from a trivial strategy: guessing at
random, or always predicting the average. **A model's performance is
meaningless without one.** The source paper reports both, which is a
mark of careful work: their regression RMSE of 0.79–1.06 only means
something next to the no-model baseline of 1.50.

**Confidence interval** — a range that expresses how uncertain a number
is. "84% accurate" from 70 test cases is not the same fact as "84%
accurate" from 70,000, and an interval is how you say so. Reporting
point estimates from small datasets without intervals is one of the
commonest ways portfolio analyses overclaim.

**Bimodal distribution** — a distribution with two humps rather than
one, suggesting two underlying groups. The pathogen measurements here
are bimodal — protected plants and unprotected plants — and that
observed structure is what justified splitting into two classes in the
first place. The authors checked it wasn't an accident by
**bootstrapping** (below) a thousand times.

**Bootstrapping** — re-sampling your data with replacement many times
to see how stable a finding is. If a pattern survives a thousand
re-samples, it is unlikely to be a fluke of which particular plants you
happened to measure. *Analogy:* re-running an election exit poll on a
thousand different random subsets of the same voters, and checking the
winner doesn't change.

**Outlier** — a measurement far from the rest. Sometimes a real
extreme, sometimes a mistake. The source study defined outliers by a
stated rule and excluded only those it could justify (contaminated
plants, a dropped box) — deciding the rule *before* looking is what
separates cleaning from cherry-picking.

---

## Group 9 — Science and reproducibility

**Peer review** — before publication, other scientists in the field
read a paper and can demand changes or reject it. A filter, not a
guarantee.

**Open access** — the paper is free to read for anyone. The source
study is.

**Preprint** — a paper posted publicly before peer review.

**Supplementary data / source data** — extra files published alongside
a paper: the underlying numbers behind each figure. Increasingly
expected, still not universal.

**Data availability statement** — the section of a paper stating where
its data can be obtained. The source study's points to Zenodo, with a
DOI. This is best practice, and it is the reason this project is
possible at all.

**Reproduction** — same data, rebuilt analysis, same question. What
this project does.

**Replication** — new data from a new experiment, same question. What
this project cannot do, and says so.

**Extension** — new questions asked of the same data. The second half
of what this project does.

**The reproducibility crisis** — the broad finding, across many
scientific fields, that a large share of published results are hard to
reproduce. Causes are mostly mundane rather than sinister: lost code,
undocumented manual steps, software that changed underneath, small
sample sizes, and selective reporting.

**Provenance** — the documented history of a piece of data: where it
came from, what was done to it, by which version of which code. A
result without provenance cannot really be checked. Every number this
project produces will be traceable to a script and a verified input
file.

**Attribution** — crediting whose work you built on. Required by the
CC-BY licence on this data, and right regardless.

**CC-BY 4.0** — a licence allowing anyone to reuse a work, including
commercially and in modified form, provided the original creators are
credited. The source data is under it.

**MIT licence** — a very permissive software licence: do what you like,
keep the copyright notice, no warranty. This project's own code and
documentation use it.

**Hindsight fitting** — adjusting your analysis until it agrees with an
answer you already knew, then presenting the agreement as
confirmation. The specific temptation in a reproduction project, and
the reason this project records its first honest attempt at each step
before any adjustment, and reports both.
