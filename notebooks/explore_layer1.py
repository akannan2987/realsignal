"""
notebooks/explore_layer1.py: what Layer 1's tables say, before any code relies on them.

Phase 1 listed the files in the published archive. This script opens the
ones that describe the community screen and answers, from the data alone:

  * how many communities there are, and how many strains each holds;
  * how many plants each round of the experiment had, and what became of them;
  * which communities were used for training and which for testing;
  * what the machine-learning input tables contain.

It reads only data files. The authors' R code stays closed until Phase 6, so
the Python rebuild in Phase 5 is written from the paper alone.

Run from the project folder, with the virtual environment active, after
scripts/fetch_data.py:

    python notebooks/explore_layer1.py

Explained in docs/03-phase-2-more-sources.md, section 5.
"""

import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA = PROJECT_ROOT / "data" / "raw" / "extracted" / "Data"

# The four files this script reads, by their real names (from data/raw/manifest.csv).
DESIGN = DATA / "MetaData" / "Mini5SynComScreen" / "20200828_Mixes.txt"
REASONS = DATA / "MetaData" / "Mini5SynComScreen" / "20201130_Comments.txt"
PLANTS = DATA / "CleanData" / "2023-01-16Mini5SynComScreen_CommentsFile.txt"
ML_FOLDER = DATA / "EditedData" / "ML_DataInput"
ML_INPUT = ML_FOLDER / "MLData_DF_Ind_TRUE_CommPresence.txt"     # one of them, looked at in detail


def show(path: Path) -> str:
    """A file's path from inside the archive, as the guide names it."""
    return path.relative_to(DATA.parent).as_posix()


def statuses(column: pd.Series) -> pd.Series:
    """TRUE, FALSE or TBD as text. A column holding only TRUE and FALSE is read
    as true/false values, so turn it back into the same three words."""
    return column.astype(str).str.upper()


def mix_names(names) -> str:
    """'Mix69, Mix70' in numeric order, not text order (Mix100 after Mix99)."""
    return ", ".join(sorted(names, key=lambda m: int(m[3:]) if m[3:].isdigit() else -1))


def main() -> int:
    missing = [p for p in (DESIGN, REASONS, PLANTS, ML_INPUT) if not p.exists()]
    if missing:
        print("Layer 1 isn't unpacked yet. Run:  python scripts/fetch_data.py")
        return 1

    # ---- 1. The design: which strains go into which community -----------------
    # One row per community ("Mix"), one column per strain: 1 = in, 0 = out.
    # The files are tab-separated text, so sep="\t".
    design = pd.read_csv(DESIGN, sep="\t").set_index("Mix")
    size = design.sum(axis=1)
    five = design[size == 5]
    print("LAYER 1: the community screen, as its files describe it")
    print()
    print("The design")
    print(f"  file: {show(DESIGN)}")
    print(f"  strains in the pool        : {design.shape[1]}")
    print(f"  five-strain communities    : {len(five)}")
    for n, label in ((design.shape[1], "all strains together"), (0, "no strains from the pool")):
        names = list(size[size == n].index)
        print(f"  {label:<27}: {len(names)} ({mix_names(names) if n else ', '.join(names)})")
    counts = five.sum()
    print(f"  communities per strain     : {counts.min()} to {counts.max()} "
          f"(average {counts.mean():.1f}) across all {len(five)}")
    print()

    # ---- 2. The plants: one row per plant, with its round and its status ------
    plants = pd.read_csv(PLANTS, sep="\t")
    plants["size"] = plants["Mix"].map(size)
    status = statuses(plants["IncludedAnalysis"])
    print("The plants")
    print(f"  file: {show(PLANTS)}")
    print("  round   plants  infected  five-strain     kept  undecided  left out")
    print("                            communities")
    for round_name, group in plants.groupby("Experiment"):
        infected = group[group["Infection"] == "Pst"]
        s = status[infected.index]
        n_five = group.loc[group["size"] == 5, "Mix"].nunique()
        print(f"  {round_name:<6}{len(group):>8}{len(infected):>10}{n_five:>13}"
              f"{(s == 'TRUE').sum():>9}{(s == 'TBD').sum():>11}{(s == 'FALSE').sum():>10}")
    print("  (kept = TRUE, undecided = TBD, left out = FALSE in the file's")
    print("   IncludedAnalysis column; counts for infected plants)")
    print()

    # ---- 3. Training and test --------------------------------------------------
    # The paper trains on rounds 1 and 2 and tests on round 3. A community
    # grown in more than one round needs a decision, so find any.
    infected_five = plants[(plants["size"] == 5) & (plants["Infection"] == "Pst")]
    rounds_of = infected_five.groupby("Mix")["Experiment"].apply(set)
    everywhere = sorted(m for m, r in rounds_of.items() if len(r) > 1)
    train = {m for m, r in rounds_of.items() if r <= {"Exp1", "Exp2"}}
    test = {m for m, r in rounds_of.items() if r == {"Exp3"}}
    print("Training and test")
    labels = plants.groupby("Mix")["FigureLabel"].first()
    print(f"  grown in more than one round : {mix_names(everywhere)}")
    print("  labelled in the plant file   : "
          + ", ".join(f"{m} {labels[m]}" for m in everywhere))
    print(f"  rounds 1 and 2 only          : {len(train)} communities (training)")
    print(f"  round 3 only                 : {len(test)} communities (testing)")
    print(f"  round 3 in all               : {len(test) + len(everywhere)} "
          f"({len(test)} new, plus {mix_names(everywhere)})")
    in_training = design.loc[sorted(train)].sum()
    print(f"  communities per strain, training only: {in_training.min()} to "
          f"{in_training.max()} (average {in_training.mean():.1f})")
    print()

    # ---- 4. Why plants were left out --------------------------------------------
    reasons = pd.read_csv(REASONS, sep="\t")
    print("Why plants were left out or undecided")
    print(f"  file: {show(REASONS)}")
    # The comments file is from 2020, the cleaned plant file from 2023: put
    # them side by side to see what each reason became.
    merged = plants.merge(reasons, on=["Box", "Plant"], suffixes=("", "_2020"))
    now = statuses(merged["IncludedAnalysis"])
    print("  reason                 plants   marked in the 2023 file:  TBD  FALSE")
    for reason, n in reasons["ExclusionJustification"].value_counts().items():
        mark = now[merged["ExclusionJustification"] == reason]
        print(f"  {reason:<22}{n:>7}{(mark == 'TBD').sum():>32}{(mark == 'FALSE').sum():>7}")
    changed = merged[statuses(merged["IncludedAnalysis"]) != statuses(merged["IncludedAnalysis_2020"])]
    print(f"  plants whose status differs between the two files: {len(changed)}")
    kept_per_mix = infected_five.assign(kept=status[infected_five.index] != "FALSE").groupby("Mix")["kept"].sum()
    lost = kept_per_mix[kept_per_mix == 0]
    lost_rounds = infected_five.groupby("Mix")["Experiment"].first()
    print("  communities with every plant left out: "
          + (", ".join(f"{m} ({lost_rounds[m]})" for m in sorted(lost.index, key=lambda m: int(m[3:])))
             or "none"))
    print()

    # ---- 5. The tables the authors' machine learning read -----------------------
    # The folder holds several versions of the input (per plant or per
    # community, with strains as presence, category or count). Which ones the
    # models used is a question for Phase 6, so here: are the per-plant ones
    # about the same plants? Then one of them, in detail.
    tables = sorted(ML_FOLDER.glob("MLData_*.txt"))
    per_plant = [t for t in tables if "_Ind_" in t.name]
    plant_sets = {frozenset(pd.read_csv(t, sep="\t", usecols=["Uid"])["Uid"]) for t in per_plant}
    print("The machine-learning input tables")
    print(f"  folder: {show(ML_FOLDER)}/")
    print(f"  tables: {len(tables)} ({len(per_plant)} with one row per plant, "
          f"{len(tables) - len(per_plant)} with one row per community)")
    print(f"  the per-plant tables all hold the same plants: {'yes' if len(plant_sets) == 1 else 'no'}")
    print()
    ml = pd.read_csv(ML_INPUT, sep="\t")
    per_round = ml.groupby("Experiment")
    print(f"  in detail: {ML_INPUT.name}")
    print(f"  plants      : {len(ml)} ("
          + ", ".join(f"{r} {len(g)}" for r, g in per_round) + ")")
    print(f"  communities : {ml['Mix'].nunique()} ("
          + ", ".join(f"{r} {g['Mix'].nunique()}" for r, g in per_round) + ")")
    shown = ml[ml["Mix"].isin(everywhere)].groupby("Mix")["Experiment"].apply(lambda e: ", ".join(sorted(set(e))))
    for mix, rounds in shown.items():
        print(f"  {mix} appears as : {rounds} only")
    print("  classes     : " + ", ".join(f"{c} {n}" for c, n in ml["Class"].value_counts().items()))
    print(f"  columns     : {', '.join(ml.columns[:6])},")
    print(f"                then one per strain ({ml.shape[1] - 6})")

    # Can this table be rebuilt from the plant file? Try the simplest rule
    # that fits the counts above, then compare plant by plant (Uid is the
    # plant's ID, box and position: "10_1"). This reads data files only;
    # the authors' R code stays closed until Phase 6.
    keep = (status[infected_five.index] != "FALSE") & (
        ~infected_five["Mix"].isin(everywhere) | (infected_five["Experiment"] == "Exp3"))
    rebuilt = set(infected_five.loc[keep, "Uid"])
    same = "yes" if rebuilt == set(ml["Uid"]) else "no"
    undecided = (statuses(ml["IncludedAnalysis"]) == "TBD").sum()
    print(f"  rebuilt from the plant file : {len(rebuilt)} plants, the same ones: {same}")
    print("    (infected plants in five-strain communities, minus those marked")
    print(f"     FALSE, with {mix_names(everywhere)} from round 3 only)")
    print(f"  undecided (TBD) plants in it: {undecided}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
