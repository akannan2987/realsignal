# Roadmap — the full build plan

**What this document is.** The complete plan for RealSignal, from the
verified dataset that exists today to a working, industrialised data
product. It states what each phase builds, what it teaches, roughly how
long it takes, and — for the things deliberately left out — why.

**Why publish a roadmap at all.** Two reasons. It keeps the project
honest: a plan written down in advance cannot quietly shrink to match
whatever got finished. And it makes the *reasoning* visible, which is
the more interesting half of any engineering decision. Several tools
that could have been used here are deliberately not, and the
explanation of why is in §6.

**Current status: Phase 1 complete (v0.1.0).** Everything below Phase 1
is planned, and marked as such everywhere in this repository. Nothing
in this project is ever described as finished before it is.

---

## Contents

- [1. The shape of the plan](#1-the-shape-of-the-plan)
- [2. The data layers](#2-the-data-layers)
- [3. The phases, in build order](#3-the-phases-in-build-order)
- [4. Milestones and releases](#4-milestones-and-releases)
- [5. Effort and schedule, honestly](#5-effort-and-schedule-honestly)
- [6. Tools deliberately not used, and why](#6-tools-deliberately-not-used-and-why)
- [7. What could derail this](#7-what-could-derail-this)

---

## 1. The shape of the plan

The work splits into four tracks. Tracks A and B are built
**interleaved**, not sequentially — so that there is always something
working to show, and so that the science and the software grow
together rather than one waiting on the other.

| Track | Theme | What it proves |
|---|---|---|
| **A — Science** | Multi-source data, harmonisation, modelling, validation | That the analysis is real, rigorous and correctly evaluated |
| **B — Platform** | Database, API, frontend, orchestration | That the analysis becomes a usable system, not a folder of scripts |
| **C — AI** | Knowledge graph, retrieval, MCP, agent | That the domain is modelled properly and machine-queryable |
| **D — Industrialisation** | Testing, CI/CD, packaging, release | That it can be maintained by someone who is not its author |

**Why interleave A and B.** If you build all the science first, you
have nothing clickable for two months and no feedback on whether the
outputs are usable. If you build all the platform first, you have a
beautiful application serving nothing. Alternating means every few
weeks produces either a new finding or a new capability — and the two
keep correcting each other. It is also simply how products get built.

---

## 2. The data layers

The single most important change from the original plan: RealSignal is
now **multi-source**. One dataset answers one question; four linked
datasets answer questions none of them could answer alone.

All four describe the **same strain collection** — the *At*-LSPHERE, a
library of bacteria isolated from wild *Arabidopsis* leaves — which is
what makes joining them possible at all. The shared key is the strain
identifier (`Leaf15`, `Leaf76`, and so on).

| # | Layer | What it contains | Source | Status |
|---|---|---|---|---|
| 1 | **Community composition + outcome** | 136 five-strain communities and 70 test communities, with measured pathogen abundance per plant | Emmenegger *et al.* 2023, *Nat Commun* 14:7983 · [Zenodo](https://doi.org/10.5281/zenodo.10118600) · CC-BY 4.0 | ✅ verified, downloaded |
| 2 | **Strain genomes** | Draft genome sequences for the strain collection | Bai *et al.* 2015, *Nature* 528:364 · [at-sphere.com](https://www.at-sphere.com/) | ⏳ access to be confirmed |
| 3 | **Biosynthetic gene clusters** | >1,000 predicted natural-product gene clusters across 207 strains, classified by type (NRPS, PKS, RiPP, terpene, quorum-sensing and others) | Helfrich *et al.* 2018, *Nat Microbiol* · [doi:10.1038/s41564-018-0200-0](https://doi.org/10.1038/s41564-018-0200-0) | ⏳ supplementary access to be confirmed |
| 4 | **Strain–strain inhibition network** | ~50,000 pairwise growth-interference tests among 224 strains | Helfrich *et al.* 2018 (same paper) | ⏳ as above |
| 5 | **Individual protection scores** | 224 strains each tested *alone* for protection against the same pathogen | Vogel *et al.* 2021, *Nat Microbiol* · [doi:10.1038/s41564-021-00997-7](https://doi.org/10.1038/s41564-021-00997-7) | ⏳ as above |

> **Honesty note on access.** Layer 1 is confirmed: open access, open
> licence, downloaded, checksum verified. Layers 2–5 come from papers
> that may be behind subscriptions. Supplementary tables are usually
> freely downloadable even when the article is not, but that is *not*
> guaranteed and has not yet been checked. **Phase 2 begins by
> verifying access to each layer and recording the result** — including
> any layer that turns out to be unobtainable. A source that cannot be
> obtained is a finding to report, not a gap to paper over. The project
> is designed so that Layer 1 alone still supports a complete
> reproduction; every additional layer is an enhancement.

### Why these layers, and not others

Each one answers a question the others cannot:

- **Layer 1** asks *which communities protect?* — the prediction task.
- **Layers 2–3** ask *why?* Genes encode the chemistry a strain can
  produce. If the strains the model ranks highly turn out to carry more
  antibiotic-producing gene clusters, the statistical result acquires a
  mechanism. Genome → chemistry → phenotype is the multi-omics chain.
- **Layer 4** asks *how do they interact?* Bacteria inhibit one
  another. That is a network, and it is the natural home for
  network-based analysis and, later, the knowledge graph.
- **Layer 5** is the prize: **independent external validation.** Our
  model learns which strains matter *from communities only* — it never
  sees any strain tested alone. Layer 5 is a different laboratory
  study that measured exactly that. So we can ask: does the ranking
  produced from community data agree with individually-measured
  protection?

That last comparison is a stronger claim than reproducing the original
paper, because it tests the *conclusion* against evidence the model
never touched. Very few analyses of any kind get to do this.

---

## 3. The phases, in build order

Phases alternate between tracks. The "Ships" column is what exists at
the end of it that did not exist before.

### ✅ Phase 1 — Data acquisition · Track A · ~4 h · **complete**

Verified download of Layer 1: checksummed, extracted, inventoried,
provenance logged. Idempotent.

**Ships:** `scripts/fetch_data.py`, a verified 239 MB archive, a file
manifest, a fetch log.
**Teaches:** permanent archives, DOIs, checksums, read-only raw data,
provenance, streaming large files.
**Guide:** [`02-phase-1-data-acquisition.md`](02-phase-1-data-acquisition.md)

---

### Phase 2 — Multi-source ingestion · Track A · ~8 h

Confirm access to Layers 2–5, then fetch each one with the same
discipline as Layer 1: verified, logged, never edited. Record honestly
what is and is not obtainable.

**Ships:** one fetcher per source, a source register documenting
licence and access terms for each, a combined provenance log.
**Teaches:** working with heterogeneous sources; reading a paper's data
availability statement; the difference between "open access" and "open
licence" (they are not the same); recording what you could *not* get.
**New concepts:** supplementary data, data licensing, source registers.

---

### Phase 3 — Harmonisation with dbt · Track A · ~10 h

Four sources, four different spellings of the same strain, four
different table shapes. This phase joins them onto one strain key and
one community key, as a tested, documented transformation pipeline.

**What dbt is:** a tool that turns a folder of SQL files into a
transformation pipeline with dependencies, automated tests and
generated documentation. *Analogy:* your recipes were loose sheets of
paper; dbt turns them into a cookbook with a contents page, an index,
and a note on every page saying which other pages must be cooked first.

Free (dbt Core), running against DuckDB locally.

**One design rule, set here and cheap only if set here.** The schema
must not hard-code 35 strains, five members per community, one pathogen
or one readout. Treat the strain library, the community size and the
measured outcome as *data*, not as constants baked into column names or
logic. Hard-coding is marginally simpler today and makes the entire
pipeline single-use; the same tables should accept a library of 400
strains, communities of three, and a different assay without a rewrite.
Generality designed in at the schema stage costs nothing. Retrofitted
later, it is a rebuild.

**Ships:** a dbt project with staging → intermediate → mart models,
data tests (uniqueness, not-null, accepted ranges, referential
integrity), and auto-generated documentation with a lineage graph.
**Teaches:** ELT versus ETL; layered modelling; data testing;
lineage; why transformation belongs in version control.
**Why this matters:** harmonising heterogeneous measurement layers onto
a common key *is* the hard part of multi-source data work. Doing it in
dbt makes every step inspectable rather than buried in a script.

---

### Phase 4 — Exploration · Track A · ~6 h

The first proper look: distributions, the two-hump (bimodal) pattern in
pathogen abundance, strain prevalence, missingness, outliers, and the
relationships between layers.

**Ships:** an exploration notebook, the first real figures, a written
data-quality report.
**Teaches:** exploratory data analysis; log scales and why they suit
bacterial counts; class imbalance; spotting problems before modelling
rather than after.

---

### Phase 5 — Reproduction of the published models · Track A · ~12 h

Random forest and elastic net, classification and regression, repeated
cross-validation across multiple seeds, evaluated once on the
never-seen test communities. Then the comparison table: our numbers
beside the published ones, including any disagreement.

Experiment tracking with **MLflow** — a free tool that records every
training run's settings, metrics and resulting model. *Analogy:* a
laboratory notebook that fills itself in, so "which settings produced
that result?" always has an answer.

**Ships:** the modelling engine in `src/`, an MLflow experiment log,
the comparison table, unit tests including a leakage guard.
**Teaches:** supervised learning; cross-validation; grouping to prevent
leakage; baselines; reporting across seeds; experiment tracking; the
discipline of not tuning until you match a known answer.

**Lock your result before moving on.** Commit the Phase 5 numbers
before starting Phase 6. That commit is the timestamped evidence that
your reproduction was written independently, without having seen the
authors' code run.

---

### Phase 6 — The original R analysis, and the three-way comparison · Track A · ~8 h

**The phase that turns a reproduction into a proper one.**

The study this project rebuilds was written in **R** — a programming
language built by statisticians, for statistics. The authors used the
`caret`, `randomForest`, `glmnet` and `lme4` packages, and **their
actual analysis scripts are inside the archive downloaded in Phase 1.**

That is unusual and valuable. Most reproduction attempts have only the
paper and the data. Here we also have the code that produced the
published numbers — which means we can run it.

#### Why this matters: what a two-way comparison cannot tell you

Up to Phase 5, the project compares two things: the numbers printed in
the paper, and the numbers from the Python rebuild. Suppose they
disagree. What have you learned?

Almost nothing, because **at least three different things could have
caused it** and you cannot tell which:

1. The rebuild misread the method — a mistake in the new code.
2. The original code does not actually reproduce the published paper —
   a gap between what was written and what was run.
3. The finding is real but sensitive to the toolchain — different
   defaults in different libraries.

*Analogy.* A recipe from a magazine produces a flat cake in your
kitchen. Was it your baking, a misprint in the recipe, or your oven?
With only the magazine and your cake, you cannot say. But if you can
watch the original chef bake it in *their* kitchen, the ambiguity
collapses immediately.

Running the authors' own code is watching the chef bake.

#### The three comparisons

| Comparison | The question it answers |
|---|---|
| Published paper → **their R code, run by you** | Does the released code reproduce its own paper? |
| **Their R code** → your Python rebuild | Did you rebuild the method correctly? |
| Published paper → your Python rebuild | Does the finding survive a different toolchain? |

Each isolates one variable. Together they turn "our numbers differ" —
a shrug — into a specific, defensible statement about *where* the
difference comes from.

#### Why it comes after Phase 5, not before

Deliberately. You write your own reproduction **first**, from the
published method, without having seen their code run.

*Analogy.* Doing the exercise before turning to the answers at the back
of the book. If you look first, you cannot honestly claim you worked it
out — and worse, you will unconsciously steer your code toward the
number you already know is coming. That has a name — **hindsight
fitting** — and it is the specific way reproduction projects fool
themselves.

Locking the Python result before opening the R scripts is the whole
discipline of this phase, and the README will say so plainly.

#### What R is, and why it exists alongside Python

**R** is a programming language created by and for statisticians.
Python is a general-purpose language that grew excellent data tools;
R was built for data from the first line.

*Analogy.* Python is a well-equipped general workshop where you can
build furniture, fix a bicycle or wire a lamp. R is a joiner's bench —
narrower, and unbeatable at the thing it is for. Neither is better.
Knowing which to reach for is the skill, and **being able to read both
is what lets you work with anyone's code rather than only your own.**

R remains the default in academic statistics and much of biology, which
is precisely why the source study is written in it — and why reading it
is a genuinely useful thing to be able to do.

#### What gets built

- **R and RStudio installed** — RStudio is an editor built specifically
  for R, with a live console, a pane showing every variable currently
  in memory, and a built-in plot viewer. It sits alongside VS Code
  without conflict; they are two editors opening the same folder.
- **`renv`** — R's equivalent of the Python virtual environment: a
  sealed, per-project package library plus a lock file, so the exact
  environment can be rebuilt by anyone. Same idea, same reasons,
  different language.
- **The authors' scripts run**, read-only, writing their outputs to a
  separate folder so nothing in `data/raw/` is ever touched.
- **A three-way comparison table** with a written interpretation of
  every difference found.
- **One "same task, three languages" walkthrough** — the same small
  aggregation in Python/pandas, R/dplyr and SQL, side by side, with
  commentary on what each is best at. Small and self-contained: it
  teaches the trade-offs without doubling the workload.

**Ships:** an R environment with `renv`, a runner for the original
scripts, the three-way comparison table, the language comparison.
**Teaches:** R basics from zero; `renv`; reading someone else's code in
an unfamiliar language; the difference between "my code disagrees" and
"the original does not reproduce"; why polyglot fluency matters more
than language preference.

**Honest expectations.** Someone else's research code frequently does
not run unchanged: hard-coded paths, absent packages, versions long
since moved on. **That is a finding, not a failure**, and it is
precisely what reproducibility research reports. Every fix required to
make it run will be documented — and that log is often the most useful
artefact of the whole exercise.

**Guide:** `03-r-environment.md` — written when this phase is reached,
from zero, covering macOS, Windows and RHEL 8.

---

### Phase 7 — Streamlit prototype · Track B · ~8 h

The first clickable thing. Choose five strains, see the predicted
outcome and a plain-language explanation of which strains drove it.

Deliberately placed early: a working product at roughly the halfway
point of the science keeps the whole project grounded in "who would use
this, and for what?"

**Ships:** a running application; the first screenshots for the README.
**Teaches:** turning analysis into a tool; presenting uncertainty
honestly in a user interface; stating a model's limits on screen.

---

### Phase 8 — Multi-omics integration · Track A · ~12 h · **headline phase**

The centrepiece. Join the genomic and network layers to the community
data and ask whether they add predictive power beyond strain identity
alone:

- Community features from Layer 1 (which strains are present)
- Genomic features from Layers 2–3 (what chemistry those strains can
  make — counts of gene clusters by class)
- Network features from Layer 4 (how antagonistic the community is
  internally; how strongly its members inhibit the pathogen's
  relatives)

Then: does a model using all layers beat one using composition alone?
And does the answer survive honest evaluation?

**Ships:** integrated feature tables, layer-by-layer model comparison,
cross-layer correlation network, feature-importance analysis across
layers.
**Teaches:** multi-omics integration — harmonisation, feature
engineering across layers, network-based methods; and the discipline of
testing whether added complexity actually helps, rather than assuming
it does.
**Honest expectation:** the added layers may *not* improve prediction.
The original paper found strain identity alone was highly predictive.
If the extra layers add nothing, that is a real and publishable-style
result, and it will be reported as one. Reporting a negative result
correctly is a stronger signal than manufacturing a positive one.

---

### Phase 9 — External validation · Track A · ~8 h

Compare the model's strain ranking — learned only from communities —
against Layer 5's independently measured single-strain protection
scores. Rank correlation, agreement analysis, and an examination of
where they disagree, because the disagreements are the interesting
part: a strain that only works in company is a genuinely different
finding from one that works alone.

**Ships:** the validation analysis, a ranking-agreement figure, a
written interpretation.
**Teaches:** external validation; rank correlation; the difference
between reproduction, replication and validation; interpreting
disagreement rather than hiding it.

---

### Phase 10 — PostgreSQL + FastAPI · Track B · ~12 h

The serving layer. Postgres as the application database, FastAPI as the
backend, both running in Docker so the setup is identical on Windows,
macOS and Linux.

**Why two databases?** DuckDB and Postgres do different jobs, and using
each where it belongs is the point. DuckDB is an *analytics* engine —
built to scan whole columns fast, for one analyst at a time. Postgres
is a *transactional* database — built for many small reads and writes
from many users at once. *Analogy:* DuckDB is a research library where
you spread twenty books across a table; Postgres is a busy pharmacy
counter serving a queue. Same building trade, different buildings.

**What FastAPI is:** a Python framework for building an **API** — a
defined set of addresses another program can call to ask your system
for something. *Analogy:* the serving hatch between kitchen and dining
room. Orders in, plates out, and nobody wanders into the kitchen.

**First contact with containers.** Rather than making you install
PostgreSQL by hand on three operating systems, the database arrives as
a container — one command, identical everywhere. This is deliberately
where containers are introduced: one service, one obvious benefit,
before the full system in Phase 17. Works with **either Docker or
Podman**; on RHEL 8 it will be Podman, because Red Hat removed Docker
from RHEL 8 entirely. The full explanation, from zero, is in
[`CONTAINERS.md`](CONTAINERS.md).

**Ships:** a containerised Postgres, a FastAPI service with automatic
interactive documentation, API tests, the model behind an endpoint.
**Teaches:** OLTP versus OLAP; REST APIs; request validation; what a
container is and why; why applications and analytics keep separate
stores.

---

### Phase 11 — React + TypeScript frontend · Track B · ~16 h

The production-style interface, replacing Streamlit for external users
while Streamlit remains the internal tool.

**What TypeScript adds over JavaScript:** types. *Analogy:* seatbelts.
JavaScript will happily let you add a number to a sentence and find out
at three in the morning; TypeScript stops you in the editor.

**Ships:** a React/TypeScript application talking to the FastAPI
backend — consortium designer, prediction display, network
visualisation.
**Teaches:** frontend versus backend; component-based interfaces;
consuming an API; typed JavaScript; why companies separate the two
layers.

---

### Phase 12 — Airflow orchestration · Track B · ~10 h

Every step so far is a command someone types. This phase makes the
pipeline run itself, in the right order, on a schedule, with failures
visible.

**What Airflow is:** an alarm clock crossed with a checklist that knows
which tasks depend on which. *Analogy:* a kitchen pass that knows the
sauce must be ready before the plate goes out, starts the sauce at the
right time, and rings a bell loudly if it burns.

Built up gently — a plain Python runner first, so you understand what
Airflow is replacing before you meet it. Run locally via the Astro CLI,
free.

**Ships:** a DAG covering ingestion → dbt → modelling → publication,
with retries, alerting and a monitoring view.
**Teaches:** orchestration; dependencies; idempotent tasks; scheduling;
observability; why "I run it manually" stops working.

---

### Phase 13 — Knowledge graph and ontology · Track C · ~12 h

The domain modelled as entities and relationships, in Neo4j.

**What an ontology is:** an agreed vocabulary for a domain — what kinds
of thing exist and how they may relate. *Analogy:* a family tree for
concepts. It fixes that a *strain* CARRIES a *gene cluster*, a *gene
cluster* PRODUCES a *compound class*, a *strain* INHIBITS a *strain*, a
*community* CONTAINS *strains* and PROTECTS a *plant*.

**Why this is not decoration here:** the data already *is* a graph.
Layer 4 is 50,000 explicit strain-to-strain relationships. Forcing a
graph onto tabular data would be ornamental; this is the opposite —
flattening it into tables loses structure that matters.

**Ships:** a Neo4j graph, the ontology written down, graph queries
answering questions SQL handles awkwardly ("which strains inhibit the
pathogen's close relatives *and* carry NRPS clusters?").
**Teaches:** graph data modelling; ontologies; Cypher; when a graph
beats a table and when it does not.

---

### Phase 14 — GraphRAG chatbot · Track C · ~10 h

Ask questions in plain English; get answers grounded in the graph and
the source papers, with citations.

**What RAG is:** Retrieval-Augmented Generation — the model looks
things up in *your* data before answering, instead of relying on what
it happens to remember. *Analogy:* the difference between a colleague
answering from memory and one who checks the file first.

**GraphRAG** goes further: the retrieval step walks the knowledge graph
rather than just matching text, so relationship questions ("why might
Leaf76 work?") can actually be answered by following the chain.

**Ships:** a chat interface over graph and documents, with every answer
citing its source.
**Teaches:** RAG; embeddings; grounding; citation; why an ungrounded
model is unusable for scientific work.

---

### Phase 15 — MCP server · Track C · ~6 h

Wrap the model, database and graph as an MCP server so an AI assistant
can query the project directly.

**What MCP is:** the Model Context Protocol — a standard way to plug
tools and data into AI assistants. *Analogy:* USB. Before it, every
device needed its own connector; after it, one socket fits everything.

**Ships:** an MCP server exposing prediction, query and graph tools,
with documented safety limits (read-only, no destructive operations).
**Teaches:** MCP; tool design for AI consumers; safe scoping.
**Why it is small:** once Phase 10's API exists, this is mostly a thin,
well-designed wrapper. Good value for the effort.

---

### Phase 16 — Recommendation agent · Track C · ~8 h

An agent that plans: given a goal ("suggest three untested five-strain
communities most likely to protect"), it decides which queries to run,
runs them, evaluates candidates against the model and the graph, and
returns a shortlist with reasoning.

**Chatbot versus agent:** a chatbot answers; an agent *acts*. It
chooses tools, runs them, looks at results, and decides what to do
next. *Analogy:* asking a librarian a question, versus asking a
research assistant to go away and come back with a shortlist.

**Ships:** a scoped agent with a fixed toolset, a step limit, and a
full log of every action it took.
**Teaches:** agent loops; tool use; guardrails; why an unlogged agent
is unacceptable in any serious setting.

---

### Phase 17 — Containerise the whole system · Track D · ~12 h

Everything built so far becomes six containers that start together as
one system: PostgreSQL, Neo4j, the FastAPI backend, the Streamlit tool,
the React frontend and MLflow. One command, on any of the three
operating systems, with **no manual installation of any of them**.

Written to work identically with **Docker or Podman**. That is not a
stylistic choice: Red Hat removed the Docker engine from RHEL 8, where
Podman is the shipped and supported default. Both implement the same
OCI image standard, so one set of files serves both — the four
decisions that make this work are set out in
[`CONTAINERS.md`](CONTAINERS.md) §8.

**Ships:** a `Dockerfile` per service (multi-stage, non-root user),
`compose.yaml` with named volumes and health checks, and
`container.sh` / `container.ps1` wrappers that detect whichever engine
is installed.
**Teaches:** images versus containers; volumes and why data survives;
port mapping; one job per container; multi-stage builds; rootless
containers; and the RHEL 8 traps — SELinux volume labels, lingering
sessions, compose availability.
**Why it comes late:** containers package a working system. Building
the box before knowing what goes in it means rebuilding the box.
**Why it is worth the 12 hours:** it is the difference between a
project people admire and a project people actually try. Three commands
and a stranger has the whole system running.
**Guide:** [`CONTAINERS.md`](CONTAINERS.md) — written from zero, no
prior container knowledge assumed.

---

### Phase 18 — CI/CD and release · Track D · ~8 h

Continuous integration on GitHub Actions: tests run on every push, and
the container images build automatically so a broken build is caught by
the machine rather than by a user. Then release notes, a versioned tag,
and a final documentation pass.

**Ships:** a CI pipeline, `NEWS.md`, `v1.0.0`.
**Teaches:** CI/CD; automated image builds; semantic versioning;
what a release actually is.

---

## 4. Milestones and releases

Each is a genuine stopping point — the project is coherent and
presentable at every one, which matters because life interrupts
projects.

| Version | After | What exists |
|---|---|---|
| **v0.1.0** ✅ | Phase 1 | Documentation, verified dataset, reproducible setup |
| v0.2.0 | Phase 3 | All sources ingested and harmonised; a tested dbt pipeline |
| v0.5.0 | Phase 5 | The reproduction: our numbers beside the published ones |
| v0.6.0 | Phase 6 | The three-way comparison — paper, original R code, and the Python rebuild |
| v0.7.0 | Phase 7 | A working, clickable product |
| v0.8.0 | Phase 9 | Multi-omics integration and external validation — the science complete |
| v1.0.0 | Phase 12 | Full application: Postgres, API, React, orchestrated |
| v1.2.0 | Phase 16 | The AI layer: graph, retrieval, MCP, agent |
| v1.3.0 | Phase 17 | Fully containerised — one command, Docker or Podman |
| v1.4.0 | Phase 18 | Industrialised: CI/CD, released |

---

## 5. Effort and schedule, honestly

| Track | Phases | Hours |
|---|---|---|
| A — Science | 1, 2, 3, 4, 5, 6, 8, 9 | ~68 |
| B — Platform | 7, 10, 11, 12 | ~46 |
| C — AI | 13, 14, 15, 16 | ~36 |
| D — Industrialisation | 17, 18 | ~20 |
| **Total** | | **~170** |

At four to five hours a week, that is **roughly eight to eleven months**.

**This is deliberately stated rather than softened.** A plan that
claims a project like this fits into three weekends is either
describing something much smaller or is not being straight. Phase 1
alone — one download script and its documentation — took four hours
done properly.

**What this means in practice:**

- Every phase ends at a working, committed checkpoint. Stopping after
  any of them leaves something coherent, not a half-demolished kitchen.
- The **science is complete at v0.8.0** — roughly four months in. That
  is the natural point at which the project's central claim is fully
  supported.
- Tracks C and D are genuine enhancements, not padding, but the project
  stands without them.
- If time runs short, the honest response is to ship a smaller version
  well and mark the rest as planned — never to claim phases that were
  not built. This roadmap exists partly to make that easy: what is done
  and what is planned are visibly separate.

---

## 6. Tools deliberately not used, and why

Choosing not to use a tool is an engineering decision like any other,
and deserves a reason rather than silence.

**Databricks / Apache Spark — not used.** Spark exists to spread
computation across many machines when data will not fit on one. This
dataset is 136 rows by 35 columns. Running Spark on it would be
theatre: slower than pandas, more complex, and demonstrating poor
judgement rather than advanced skill. The one genuinely useful piece
from that ecosystem — **MLflow** for experiment tracking — is used, in
Phase 5, running locally and free. *Knowing when a tool is the wrong
size is part of using tools well.*

**Snowflake — optional, as a portability exercise only.** Same
objection: a cloud warehouse for a dataset this small is
disproportionate. But there is a real skill worth demonstrating —
**environment portability**. Phase 3's dbt models are written so the
same SQL runs against DuckDB locally *or* a cloud warehouse by
switching one configuration profile. That makes "could this run in the
cloud?" a documented one-line answer rather than a rewrite. If the
Snowflake path is built, it will be an optional module with exact
free-trial steps and explicit guidance on avoiding cost — and the
free-trial terms will be verified at the time of writing, because they
change.

**Deep learning — not used.** With 136 training examples, a neural
network would overfit badly and be impossible to interpret. The whole
scientific point is *which strains matter*, which requires an
interpretable model. Random forests and elastic nets are not the
simpler choice here; they are the correct one.

**Kubernetes — not used.** Compose runs the entire system on one
machine, which is what this project needs. Kubernetes coordinates
containers across a fleet of machines with automatic restarts, scaling
and rolling updates — real problems, none of which this project has.
*Analogy:* Compose organises one restaurant; Kubernetes runs a national
chain. Adopting the chain's management system for one restaurant is not
ambition, it is overhead. The containers built in Phase 17 are standard
OCI images, so if a fleet ever were needed, they would already be the
right input — which is the honest version of "future-proof".

**A separate feature store, a message queue, a data lake.** All
sensible at scale. All disproportionate here. Each would add setup and
teach nothing this project needs.

---

## 7. What could derail this

Stated in advance, so nothing looks like a surprise later.

**Layers 2–5 may not be freely obtainable.** The mitigation is built
in: Layer 1 alone supports a complete reproduction, and each additional
layer is an enhancement. Phase 2 begins by checking, and records the
answer either way.

**The multi-omics layers may not improve prediction.** Entirely
possible — the original found strain identity alone was highly
predictive. That would be a real negative result, reported as one.

**Joining sources may be harder than it looks.** Strain naming across
four papers will not be perfectly consistent. This is the ordinary
reality of multi-source data work, it is exactly the skill Phase 3
exists to demonstrate, and the effort estimate allows for it.

**Phases may take longer than estimated.** They usually do. The
estimates are honest guesses, not commitments, and this document will
be updated with actuals as phases complete — which will itself be a
more useful record than the estimates were.

---

**See also:** [`00-architecture.md`](00-architecture.md) for how the
finished system fits together · [`GLOSSARY.md`](GLOSSARY.md) for every
term in plain language · [`GIT_WORKFLOW.md`](GIT_WORKFLOW.md) for the
branch model used at the end of every phase.
