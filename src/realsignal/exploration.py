"""
src/realsignal/exploration.py: the questions Phase 4 asks of the warehouse.

Phase 3 left a harmonised, tested warehouse. Before any model is trained, this
module looks at what it holds, one question at a time:

  1. the shape of the outcome, and where its two humps are;
  2. how much the rounds differ, and what the authors' normalised values are;
  3. how the strains are spread over the communities (the design);
  4. missing values, the undecided plants and outliers;
  5. how much plants of one community differ from each other;
  6. one strain at a time;
  7. how the other data layers relate to that.

Three programs use it: notebooks/explore_marts.py prints the answers,
scripts/make_quality_report.py writes them into docs/reports/data-quality.md
and figures/make_phase4_figures.py draws them. They all call the functions
below, so a number can't differ between the terminal, the report and a
picture.

The test set stays sealed. Test plants are counted and their records checked,
but no value measured on a test plant is ever read here: every query that
reads a value leaves split = 'test' out in its SQL, before anything reaches
Python. Phase 5 scores its models once on those plants, and that score only
means something if no choice made before it was shaped by them.
tests/test_exploration.py checks this by changing every test value in a
made-up warehouse and confirming that no answer moves.

Explained in docs/05-phase-4-exploration.md.
"""

from __future__ import annotations

import hashlib
import itertools
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd
from scipy.stats import gaussian_kde

PROJECT_ROOT = Path(__file__).resolve().parents[2]
WAREHOUSE = PROJECT_ROOT / "data" / "warehouse" / "realsignal.duckdb"

# ---- Settings, each with its reason ------------------------------------------
# The shuffle tests below draw random numbers. A fixed seed makes every run
# draw the same ones, so the report comes out identical each time.
SEED = 2026
SHUFFLES = 1000
# A plant is listed as an outlier when it sits more than this many log10 units
# (2 = 100 times) from the median of the other plants of its community. Listed,
# never removed: whether to drop a plant is a modelling decision, with a reason.
OUTLIER_DISTANCE = 2.0
# "Protected" isn't defined yet (Phase 5 takes the published definition). These
# are the reductions, in log10 units below the round's plants with no strains,
# at which the class balance is counted: 1 = ten times fewer, 3 = a thousand.
REDUCTIONS = (1, 2, 3)

# Measurements this module looks for by name. The outcome itself is never
# named here: it's whatever marts.model_plants says (var outcome_measurement).
PATHOGEN_LOG10 = "pathogen_log10_cfu_per_g"
PATHOGEN_NORMALISED = "pathogen_log10_normalised"
FRESH_WEIGHT = "fresh_weight"
FRESH_WEIGHT_NORMALISED = "fresh_weight_normalised"
COMMENSAL_LOG10 = "commensal_log10_cfu_per_g"
STRAIN_LOG10 = "strain_log10_cfu_per_g"
MEASUREMENT_ORDER = [
    "pathogen_cfu_per_g", PATHOGEN_LOG10, PATHOGEN_NORMALISED,
    FRESH_WEIGHT, FRESH_WEIGHT_NORMALISED,
    "commensal_cfu_per_g", COMMENSAL_LOG10, "strain_cfu_per_g", STRAIN_LOG10]

# Strain properties from the other layers, compared with question 6.
STRAIN_FEATURES = {
    "genome_length_bp": "genome length (Layer 2)",
    "gc_percent": "GC content (Layer 2)",
    "clusters_listed": "gene clusters (Layer 3)",
    "potentially_inhibitory_clusters": "possibly inhibitory clusters (Layer 3)",
    "inhibits": "strains it held back (Layer 4)",
    "inhibited_by": "strains that held it back (Layer 4)",
}

# Every plant belongs to one of these groups. Controls are told apart by what
# their community is (no strains, or the whole library), not by its name.
GROUPS = ["training", "test", "between-round reference", "no strains, infected",
          "no strains, not infected", "whole library"]

PLANTS_SQL = """
    select p.plant_id, p.box_id, p.round_id, p.community_id, p.inclusion_mark,
           p.use_for_modelling, p.split, c.label, c.kind, c.community_size,
           case
               when p.split in ('training', 'test', 'between-round reference')
                   then p.split
               when c.kind = 'no strains' and p.pathogen is not null
                   then 'no strains, infected'
               when c.kind = 'no strains' then 'no strains, not infected'
               when c.kind = 'whole library' then 'whole library'
               else 'other'
           end as plant_group
    from marts.fct_plant as p
    join marts.dim_community as c using (community_id)
"""


class WarehouseNotReady(Exception):
    """The warehouse is missing, locked or not built yet. The message says what to do."""


def open_warehouse(path: Path | None = None) -> duckdb.DuckDBPyConnection:
    """The warehouse, opened read-only: nothing in Phase 4 changes it. Without a
    path, the project's own (WAREHOUSE, looked up when called, so a test can
    point it somewhere else)."""
    path = Path(path) if path else WAREHOUSE
    if not path.exists():
        raise WarehouseNotReady("No warehouse yet. Run:  python scripts/load_raw.py,\n"
                                "then from inside dbt/:  dbt build")
    try:
        con = duckdb.connect(str(path), read_only=True)
    except duckdb.IOException as error:
        raise WarehouseNotReady("The warehouse is open in another program (a running dbt\n"
                                "build or a Python session). Close it and try again.") from error
    built = con.execute("select count(*) from information_schema.tables "
                        "where table_schema = 'marts' and table_name = 'model_plants'").fetchone()[0]
    if not built:
        con.close()
        raise WarehouseNotReady("The raw tables are loaded, but dbt hasn't built the marts yet.\n"
                                "From inside dbt/:  dbt build")
    return con


# ---- Reading the warehouse -----------------------------------------------------

def outcome_name(con) -> str:
    """The measurement Phase 5 will predict, as marts.model_plants records it."""
    return con.execute("select any_value(outcome_measurement) from marts.model_plants").fetchone()[0]


def training_outcomes(con) -> pd.DataFrame:
    """The training plants of marts.model_plants with their outcome. Never the test ones."""
    return con.execute("""
        select plant_id, community_id, round_id, inclusion_mark, outcome
        from marts.model_plants
        where split = 'training'
        order by plant_id""").df()


def values(con, measurement: str) -> pd.DataFrame:
    """One measurement for every plant outside the test set, with its group.

    The where clause is the seal: test plants are dropped in SQL, so their
    values never reach Python."""
    return con.execute(f"""
        with plants as ({PLANTS_SQL})
        select plants.*, m.value
        from plants
        join marts.fct_plant_measurement as m
          on m.plant_id = plants.plant_id
         and m.measurement = ?
         and m.strain_id is null
        where plants.split <> 'test'
        order by plants.plant_id""", [measurement]).df()


def strain_order(strain: str) -> tuple:
    """Leaf15 before Leaf130: by the number, then by the name."""
    digits = "".join(c for c in strain if c.isdigit())
    return (strain.rstrip("0123456789"), int(digits) if digits else 0)


def round_order(rounds) -> list:
    return sorted(set(rounds), key=lambda r: (len(r), r))


def fixed(x: float, signed: bool = False) -> str:
    """Two decimals, '+0.31' style when signed, and never '-0.00' for a value
    that rounds to zero (a tiny negative number would otherwise print that way)."""
    text = f"{x:+.2f}" if signed else f"{x:.2f}"
    return text.replace("-0.00", "+0.00" if signed else "0.00")


def quartiles(series) -> dict:
    """Count, median and the middle half of a set of numbers."""
    q1, median, q3 = np.quantile(np.asarray(series, dtype=float), [0.25, 0.5, 0.75])
    return {"n": len(series), "median": median, "q1": q1, "q3": q3}


# ---- 1. The shape of the outcome --------------------------------------------------

def humps(y) -> dict:
    """Where a smoothed histogram of y peaks, and the lowest point between the two
    highest peaks.

    The smoothing is a kernel density estimate: each value is replaced by a small
    bell curve and the curves are added up, which gives a histogram without the
    jagged edges that depend on where the bars start. The width of the bells is
    scipy's standard choice (Scott's rule), so it isn't tuned by hand."""
    y = np.asarray(y, dtype=float)
    grid = np.round(np.arange(np.floor(y.min()), np.ceil(y.max()) + 0.001, 0.01), 2)
    density = gaussian_kde(y)(grid)
    inside = np.arange(1, len(grid) - 1)
    peaks = inside[(density[inside] > density[inside - 1]) & (density[inside] > density[inside + 1])]
    top = sorted(peaks, key=lambda i: density[i], reverse=True)[:2]
    result = {"grid": grid, "density": density, "peaks": sorted(float(grid[i]) for i in top), "dip": None}
    if len(top) == 2:
        low, high = sorted(top)
        dip = low + int(np.argmin(density[low:high + 1]))
        result["dip"] = float(grid[dip])
    return result


def outcome_shape(con) -> dict:
    """Question 1: what the training outcome looks like, on its own scale and,
    for a log10 measurement, back on the ordinary scale."""
    plants = training_outcomes(con)
    y = plants["outcome"].to_numpy(dtype=float)
    shape = {"measurement": outcome_name(con), "plants": len(y),
             "communities": plants["community_id"].nunique(),
             "rounds": round_order(plants["round_id"]),
             "min": y.min(), "max": y.max(), "mean": y.mean(), "sd": y.std(ddof=1),
             **quartiles(y), "values": y}
    shape["iqr"] = shape["q3"] - shape["q1"]
    shape.update({k: v for k, v in humps(y).items()})
    # The ordinary-scale view only makes sense for a log10 count that also exists
    # unlogged (pathogen_log10_cfu_per_g and pathogen_cfu_per_g), not for a
    # normalised value, which is a difference from something else.
    shape["linear"] = None
    unlogged = shape["measurement"].replace("_log10", "")
    known = {r[0] for r in con.execute("select distinct measurement from marts.fct_plant_measurement").fetchall()}
    if "_log10" in shape["measurement"] and unlogged in known:
        counts = np.sort(10 ** y)[::-1]
        shape["linear"] = {"mean": counts.mean(), "median": float(np.median(counts)),
                           "min": counts.min(), "max": counts.max(),
                           "log10_of_mean": float(np.log10(counts.mean())),
                           "top_tenth_share": counts[:len(counts) // 10].sum() / counts.sum()}
    return shape


def baselines(con) -> pd.Series:
    """Per round, the median outcome of the infected plants that got no strains:
    what the pathogen does with nothing in its way."""
    plants = values(con, outcome_name(con))
    plants = plants[(plants["plant_group"] == "no strains, infected")
                    & (plants["inclusion_mark"] != "FALSE")]
    return plants.groupby("round_id")["value"].median()


def class_balance(con, shape: dict) -> dict:
    """How the training plants split at a few reductions below the baseline of
    their own round, and on either side of the dip between the humps."""
    plants = training_outcomes(con)
    base = baselines(con)
    reduction = plants["round_id"].map(base) - plants["outcome"]
    rows = []
    for cut in REDUCTIONS:
        hit = reduction >= cut
        rows.append({"reduction": cut, "fold": 10 ** cut, "plants": int(hit.sum()),
                     "share": hit.mean(),
                     "by_round": hit.groupby(plants["round_id"]).mean().to_dict()})
    below = None
    if shape["dip"] is not None:
        below = int((plants["outcome"] < shape["dip"]).sum())
    return {"baselines": base.to_dict(), "cuts": rows, "below_dip": below, "plants": len(plants)}


# ---- 2. Rounds, and the authors' normalised values -----------------------------

def rounds_compared(con) -> pd.DataFrame:
    """Question 2: the outcome per round for the plants grown in more than one
    round with the same treatment, and for the training plants.

    Controls and reference plants count unless marked FALSE; training plants are
    the ones marts.model_plants uses. Reference communities appear in the rounds
    before the test round only: their test-round plants are test plants."""
    plants = values(con, outcome_name(con))
    plants = plants[plants["plant_group"] != "training"]
    plants = plants[plants["inclusion_mark"] != "FALSE"]
    rows = []
    groups = [("no strains, infected", "no strains, infected"), ("whole library", "whole library")]
    for community, label in (plants[plants["plant_group"] == "between-round reference"]
                             [["community_id", "label"]].drop_duplicates().itertuples(index=False)):
        groups.append((f"community {community}", f"{community} ({label})" if label != community else community))
    for key, name in groups:
        if key.startswith("community "):
            part = plants[(plants["plant_group"] == "between-round reference")
                          & (plants["community_id"] == key.split(" ", 1)[1])]
        else:
            part = plants[plants["plant_group"] == key]
        for round_id in round_order(part["round_id"]):
            rows.append({"group": name, "round_id": round_id,
                         **quartiles(part.loc[part["round_id"] == round_id, "value"])})
    training = training_outcomes(con)
    for round_id in round_order(training["round_id"]):
        rows.append({"group": "training (different communities)", "round_id": round_id,
                     **quartiles(training.loc[training["round_id"] == round_id, "outcome"])})
    return pd.DataFrame(rows)


def round_shifts(table: pd.DataFrame) -> pd.DataFrame:
    """For each group, how far its median moved from its first round to each later one."""
    rows = []
    for group, part in table.groupby("group", sort=False):
        part = part.set_index("round_id")
        first = part.index[0]
        for later in part.index[1:]:
            rows.append({"group": group, "first_round": first, "later_round": later,
                         "shift": part.loc[later, "median"] - part.loc[first, "median"]})
    return pd.DataFrame(rows)


def weights_by_round(con) -> pd.DataFrame:
    """Median fresh weight per round for the plants with no strains, infected or not."""
    plants = values(con, FRESH_WEIGHT)
    plants = plants[plants["inclusion_mark"] != "FALSE"]
    rows = []
    for group in ("no strains, not infected", "no strains, infected"):
        part = plants[plants["plant_group"] == group]
        for round_id in round_order(part["round_id"]):
            rows.append({"group": group, "round_id": round_id,
                         **quartiles(part.loc[part["round_id"] == round_id, "value"])})
    return pd.DataFrame(rows)


def normalisation(con) -> dict:
    """What the two normalised measurements are, worked out from the numbers alone.

    Pathogen: is the normalised value the log10 count minus the median of the
    round's infected plants with no strains (every mark)? Weight: is it the
    weight divided by one number, and is that number a median of the plants
    with no strains and no pathogen? Checked on every plant outside the test
    set. Phase 6 reads the authors' code and confirms or corrects this."""
    found = {}
    pathogen = values(con, PATHOGEN_LOG10)
    published = values(con, PATHOGEN_NORMALISED)
    if len(pathogen) and len(published):
        base = (pathogen[pathogen["plant_group"] == "no strains, infected"]
                .groupby("round_id")["value"].median())
        both = pathogen.merge(published[["plant_id", "value"]], on="plant_id", suffixes=("", "_published"))
        rebuilt = both["value"] - both["round_id"].map(base)
        difference = (rebuilt - both["value_published"]).abs()
        found["pathogen"] = {"plants": len(both), "matching": int((difference < 1e-9).sum()),
                             "largest_difference": float(difference.max()),
                             "baselines": base.to_dict()}
    weight = values(con, FRESH_WEIGHT)
    weight_published = values(con, FRESH_WEIGHT_NORMALISED)
    if len(weight) and len(weight_published):
        both = weight.merge(weight_published[["plant_id", "value"]], on="plant_id",
                            suffixes=("", "_published"))
        both = both[both["value_published"] != 0]
        ratio = both["value"] / both["value_published"]
        healthy = (weight[(weight["plant_group"] == "no strains, not infected")]
                   .groupby("round_id")["value"].median())
        constant = float(ratio.median())
        one_number = float(ratio.max() - ratio.min()) < 1e-6
        found["weight"] = {"plants": len(both), "one_number": one_number,
                           "divisor": constant if one_number else None,
                           "healthy_medians": healthy.to_dict(),
                           "matching_rounds": [r for r, m in healthy.items()
                                               if one_number and abs(m - constant) < 1e-6]}
    return found


# ---- 3. The design -------------------------------------------------------------------

def design_balance(con) -> dict:
    """Question 3: how often each strain appears in the training and test
    communities that have plants for modelling, how many pairs of strains never
    share a training community, and how close each test community comes to a
    training one. Reads only which strains each community holds."""
    members = con.execute("""
        select m.community_id, m.strain_id, c.role
        from marts.community_member as m
        join marts.dim_community as c using (community_id)
        where c.kind = 'community' and c.role in ('training', 'test')
          and c.has_plants_for_modelling""").df()
    library = sorted(con.execute("select strain_id from marts.dim_strain where in_screen_library")
                     .df()["strain_id"], key=strain_order)
    counts = (members.groupby(["strain_id", "role"]).size().unstack(fill_value=0)
              .reindex(library, fill_value=0))
    for role in ("training", "test"):
        if role not in counts:
            counts[role] = 0
    counts = counts[["training", "test"]]
    teams = {role: members[members["role"] == role].groupby("community_id")["strain_id"].apply(frozenset)
             for role in ("training", "test")}
    together = {pair: 0 for pair in itertools.combinations(library, 2)}
    for team in teams["training"]:
        for pair in itertools.combinations(sorted(team, key=strain_order), 2):
            together[pair] += 1
    shared = [max((len(team & other) for other in teams["training"]), default=0)
              for team in teams["test"]]
    sizes = sorted(con.execute("select distinct community_size from marts.dim_community "
                               "where kind = 'community'").df()["community_size"])
    return {"counts": counts, "library": len(library), "sizes": sizes,
            "communities": {role: len(teams[role]) for role in teams},
            "pairs": len(together), "pairs_never_together": sum(1 for n in together.values() if n == 0),
            "most_together": max(together.values(), default=0),
            "test_overlap": pd.Series(shared, dtype=int).value_counts().sort_index().to_dict()}


# ---- 4. Missing values, undecided plants, outliers --------------------------------

def missing_values(con) -> dict:
    """Question 4a: for every plant group and measurement, how many plants have it.

    Test plants are counted here (whether a record exists), but their values
    aren't read: count(distinct plant_id) never looks at value."""
    table = con.execute(f"""
        with plants as ({PLANTS_SQL}),
        kinds as (select distinct measurement from marts.fct_plant_measurement)
        select plants.plant_group, kinds.measurement,
               count(distinct plants.plant_id) as plants,
               count(distinct m.plant_id) as present
        from plants
        cross join kinds
        left join marts.fct_plant_measurement as m
          on m.plant_id = plants.plant_id and m.measurement = kinds.measurement
        group by all""").df()
    order = MEASUREMENT_ORDER + sorted(set(table["measurement"]) - set(MEASUREMENT_ORDER))
    present = (table.pivot(index="measurement", columns="plant_group", values="present")
               .reindex([m for m in order if m in set(table["measurement"])])
               .reindex(columns=[g for g in GROUPS if g in set(table["plant_group"])]).fillna(0).astype(int))
    plants = table.groupby("plant_group")["plants"].first().reindex(present.columns)
    used = con.execute("""
        with used as (select p.plant_id, c.community_size
                      from marts.fct_plant as p join marts.dim_community as c using (community_id)
                      where p.use_for_modelling)
        select k.measurement, count(distinct used.plant_id) - count(distinct m.plant_id) as missing
        from used
        cross join (select distinct measurement from marts.fct_plant_measurement) as k
        left join marts.fct_plant_measurement as m
          on m.plant_id = used.plant_id and m.measurement = k.measurement
        group by k.measurement""").df().set_index("measurement")["missing"]
    used_plants = con.execute("select count(*) from marts.fct_plant where use_for_modelling").fetchone()[0]
    short = con.execute(f"""
        select count(*) from (
            select p.plant_id, any_value(c.community_size) as size, count(m.plant_id) as counted
            from marts.fct_plant as p
            join marts.dim_community as c using (community_id)
            left join marts.fct_plant_measurement as m
              on m.plant_id = p.plant_id and m.measurement = '{STRAIN_LOG10}'
            where p.use_for_modelling
            group by p.plant_id)
        where counted <> size""").fetchone()[0]
    shared = con.execute(f"""
        select count(*), count(*) filter (where m.is_ambiguous)
        from marts.fct_plant_measurement as m
        join marts.fct_plant as p using (plant_id)
        where m.measurement = '{STRAIN_LOG10}' and p.use_for_modelling and p.split <> 'test'
    """).fetchone()
    return {"present": present, "plants": plants, "used_plants": used_plants,
            "used_missing": used.reindex(present.index).fillna(0).astype(int),
            "strain_counts_short": short, "strain_rows": shared[0], "strain_rows_shared": shared[1]}


def undecided_plants(con) -> list[dict]:
    """Question 4b: do the undecided (TBD) plants, from dropped boxes, look
    different from the rest? Compared within a round, for the training plants
    and for the infected plants with no strains, where a dropped box can't be
    confused with a different community."""
    rows = []
    training = training_outcomes(con)
    controls = values(con, outcome_name(con))
    controls = controls[controls["plant_group"] == "no strains, infected"]
    for round_id in round_order(training.loc[training["inclusion_mark"] == "TBD", "round_id"]):
        for group, part, column in (("training", training, "outcome"),
                                    ("no strains, infected", controls, "value")):
            part = part[part["round_id"] == round_id]
            marks = {mark: part.loc[part["inclusion_mark"] == mark, column] for mark in ("TRUE", "TBD")}
            if min(len(v) for v in marks.values()) == 0:
                continue
            row = {"round_id": round_id, "group": group,
                   **{f"{mark}_n": len(v) for mark, v in marks.items()},
                   **{f"{mark}_median": float(np.median(v)) for mark, v in marks.items()}}
            if group == "no strains, infected":
                boxes = part.groupby("box_id")["value"].median()
                row.update({"boxes": len(boxes), "box_low": boxes.min(), "box_high": boxes.max()})
            rows.append(row)
    return rows


def outliers(con) -> dict:
    """Question 4c: training plants far from the other plants of their community.

    A plant is listed when it sits more than OUTLIER_DISTANCE log10 units from
    the median of the other plants that got the same community (communities
    with at least three plants, so that 'the others' are at least two). For
    comparison, the usual rule for a whole column (more than 1.5 times the
    middle half beyond the quartiles) is applied too."""
    plants = training_outcomes(con)
    rows = []
    for community, part in plants.groupby("community_id"):
        if len(part) < 3:
            continue
        for index, plant in part.iterrows():
            others = part.drop(index)["outcome"].median()
            distance = abs(plant["outcome"] - others)
            if distance > OUTLIER_DISTANCE:
                rows.append({"plant_id": plant["plant_id"], "community_id": community,
                             "round_id": plant["round_id"], "outcome": plant["outcome"],
                             "others_median": others, "distance": distance})
    listed = pd.DataFrame(rows, columns=["plant_id", "community_id", "round_id", "outcome",
                                         "others_median", "distance"])
    listed = listed.sort_values(["distance", "plant_id"], ascending=[False, True]).reset_index(drop=True)
    y = plants["outcome"]
    q1, q3 = np.quantile(y, [0.25, 0.75])
    low, high = q1 - 1.5 * (q3 - q1), q3 + 1.5 * (q3 - q1)
    return {"listed": listed, "communities": listed["community_id"].nunique(),
            "column_rule": {"low": low, "high": high, "outside": int(((y < low) | (y > high)).sum())}}


# ---- 5. Plant-to-plant noise --------------------------------------------------------------

def noise(con, dip: float | None) -> dict:
    """Question 5: how much of the variation between training plants lies between
    communities, and how much between plants that got the same community.

    The share between communities is the intraclass correlation, from a one-way
    analysis of variance: 1 would mean plants of one community always agree,
    0 that the community makes no difference. It's a rough ceiling for any
    model that only knows which strains a plant got."""
    plants = training_outcomes(con)
    groups = plants.groupby("community_id")["outcome"]
    y = plants["outcome"].to_numpy(dtype=float)
    n, k = len(y), groups.ngroups
    sizes = groups.size().to_numpy()
    within = float(((plants["outcome"] - groups.transform("mean")) ** 2).sum())
    between = float((sizes * (groups.mean().to_numpy() - y.mean()) ** 2).sum())
    ms_between, ms_within = between / (k - 1), within / (n - k)
    n0 = (n - (sizes ** 2).sum() / n) / (k - 1)
    icc = (ms_between - ms_within) / (ms_between + (n0 - 1) * ms_within)
    result = {"plants": n, "communities": k, "icc": icc, "sd_total": float(np.std(y, ddof=1)),
              "sd_within": float(np.sqrt(ms_within)), "plants_per_community": groups.size().value_counts().to_dict(),
              "split_by_dip": None}
    if dip is not None:
        low, high = groups.min(), groups.max()
        result["split_by_dip"] = {"both_sides": int(((low < dip) & (high > dip)).sum()),
                                  "all_below": int((high < dip).sum()), "all_above": int((low > dip).sum())}
    return result


# ---- 6. One strain at a time ------------------------------------------------------------

def community_means(con) -> tuple[pd.Series, pd.DataFrame]:
    """Each training community's mean outcome, and which strains it holds (one
    column per strain, True or False). Communities, not plants, are the unit:
    the four plants of a community share their strains, so counting them as
    four separate pieces of evidence would overstate what the data shows."""
    means = training_outcomes(con).groupby("community_id")["outcome"].mean()
    members = con.execute("select community_id, strain_id from marts.community_member").df()
    members = members[members["community_id"].isin(means.index)]
    holds = pd.crosstab(members["community_id"], members["strain_id"]).reindex(means.index).fillna(0) > 0
    holds = holds[sorted(holds.columns, key=strain_order)]
    return means, holds


def differences(means: np.ndarray, holds: np.ndarray) -> np.ndarray:
    """Per strain: mean of the communities holding it minus mean of the rest."""
    with_ = (holds * means[:, None]).sum(axis=0) / holds.sum(axis=0)
    without = (~holds * means[:, None]).sum(axis=0) / (~holds).sum(axis=0)
    return with_ - without


def one_strain_at_a_time(con) -> dict:
    """Question 6: for each strain, how the training communities holding it
    compare with those that don't.

    A shuffle test says how large a difference chance alone produces: the
    community means are handed out to the communities at random, SHUFFLES
    times, and each time the largest of all the strains' differences is noted.
    A strain stands out only if its difference is beyond what 95 % of the
    shuffles reached. Taking the largest over all strains each time accounts
    for looking at every strain at once."""
    means, holds = community_means(con)
    m, h = means.to_numpy(dtype=float), holds.to_numpy()
    observed = differences(m, h)
    rng = np.random.default_rng(SEED)
    largest = np.array([np.abs(differences(rng.permutation(m), h)).max() for _ in range(SHUFFLES)])
    threshold = float(np.quantile(largest, 0.95))
    table = pd.DataFrame({"strain_id": holds.columns, "communities_with": h.sum(axis=0),
                          "communities_without": (~h).sum(axis=0),
                          "mean_with": (h * m[:, None]).sum(axis=0) / h.sum(axis=0),
                          "difference": observed})
    table = table.sort_values(["difference", "strain_id"]).reset_index(drop=True)
    table["stands_out"] = table["difference"].abs() > threshold
    return {"table": table, "threshold": threshold, "communities": len(m),
            "stands_out": list(table.loc[table["stands_out"], "strain_id"])}


# ---- 7. How the layers relate -------------------------------------------------------------

def ranks(x: np.ndarray) -> np.ndarray:
    return pd.Series(x).rank().to_numpy()


def layers(con, strains: pd.DataFrame) -> dict:
    """Question 7: do the strains' properties from Layers 2 to 4 line up with
    question 6's differences? A rank correlation per property (Spearman's: 1
    means the two orders agree completely, -1 that they're reversed, 0 no
    relation), with a shuffle test over all properties at once, as in
    question 6. And, plant by plant, total commensal load against the outcome."""
    features = con.execute(f"""
        select strain_id, {', '.join(STRAIN_FEATURES)}
        from marts.dim_strain where in_screen_library""").df().set_index("strain_id")
    # A query without ORDER BY can hand rows back in any order, and the shuffles
    # below pair values by position, so the strains are put in one fixed order
    # first. Without this line the threshold changed between runs and computers.
    features = features.loc[sorted(features.index, key=strain_order)]
    joined = features.join(strains.set_index("strain_id")["difference"], how="inner")
    prepared = []
    for column, label in STRAIN_FEATURES.items():
        part = joined[[column, "difference"]].dropna()
        prepared.append((column, label, ranks(part[column].to_numpy(dtype=float)),
                         part["difference"].to_numpy(dtype=float)))

    def correlation(a, b):
        return float(np.corrcoef(a, ranks(b))[0, 1])

    rows = [{"feature": column, "label": label, "strains": len(d), "rho": correlation(r, d)}
            for column, label, r, d in prepared]
    rng = np.random.default_rng(SEED)
    largest = [max(abs(correlation(r, rng.permutation(d))) for _, _, r, d in prepared)
               for _ in range(SHUFFLES)]
    threshold = float(np.quantile(largest, 0.95))
    table = pd.DataFrame(rows)
    table["stands_out"] = table["rho"].abs() > threshold
    commensal = values(con, COMMENSAL_LOG10)
    pairs = training_outcomes(con).merge(commensal[["plant_id", "value"]], on="plant_id")
    load = None
    if len(pairs) > 2:
        load = {"plants": len(pairs),
                "rho": float(np.corrcoef(ranks(pairs["value"].to_numpy()),
                                         ranks(pairs["outcome"].to_numpy()))[0, 1]),
                "median": float(pairs["value"].median()),
                "q1": float(pairs["value"].quantile(0.25)), "q3": float(pairs["value"].quantile(0.75))}
    return {"table": table, "threshold": threshold, "commensal": load}


# ---- Everything at once --------------------------------------------------------------------

def counts(con) -> dict:
    """The plants and communities in each group: counted, no value read."""
    plants = con.execute(f"""
        with plants as ({PLANTS_SQL})
        select plant_group, count(*) as plants,
               count(*) filter (where use_for_modelling) as used,
               count(distinct community_id) filter (where use_for_modelling) as communities
        from plants group by 1""").df().set_index("plant_group").reindex(GROUPS).dropna().astype(int)
    # The fingerprint is a checksum of the checksums raw.load_log records for the
    # tables read from one file each: the archive's tables and the two journal
    # workbooks. The genomes (34 files read as one table) have no checksum there;
    # Phase 2 checked each against NCBI's. The registers in sources/ are left out
    # because Git may change their line endings on Windows.
    load = con.execute("""
        select count(*), sum(rows),
               string_agg(sha256, ',' order by table_name) filter (where source_id <> 'register')
        from raw.load_log""").fetchone()
    undecided = con.execute("select count(*) filter (where inclusion_mark = 'TBD') "
                            "from marts.model_plants").fetchone()[0]
    return {"plants": plants, "tables_loaded": load[0], "rows_loaded": int(load[1]),
            "undecided_in_model": undecided,
            "fingerprint": hashlib.sha256((load[2] or "").encode("utf-8")).hexdigest()[:12]}


def answers(con) -> dict:
    """Every question, answered once, for the report and the explorer."""
    shape = outcome_shape(con)
    strains = one_strain_at_a_time(con)
    rounds = rounds_compared(con)
    return {"counts": counts(con), "shape": shape, "balance": class_balance(con, shape),
            "rounds": rounds, "shifts": round_shifts(rounds), "weights": weights_by_round(con),
            "normalisation": normalisation(con), "design": design_balance(con),
            "missing": missing_values(con), "undecided": undecided_plants(con),
            "outliers": outliers(con), "noise": noise(con, shape["dip"]),
            "strains": strains, "layers": layers(con, strains["table"])}
