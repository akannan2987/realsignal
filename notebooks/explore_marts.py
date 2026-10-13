"""
notebooks/explore_marts.py: a first careful look at the harmonised data.

Phase 3 built the marts and tested that they hold what the sources say. This
script asks what the data looks like before anything is modelled: the shape of
the outcome, how much the rounds differ, how the design spreads the strains,
missing values and outliers, how noisy single plants are, one strain at a
time, and how the other layers relate. Seven questions, printed in order.

The training plants and the control plants are looked at in full. Test plants
are counted, but their values are never read: they stay sealed until Phase 5
scores its models on them once.

Every number comes from src/realsignal/exploration.py, the same functions
scripts/make_quality_report.py and figures/make_phase4_figures.py use.

Run from the project folder, with the virtual environment active, after
scripts/load_raw.py and dbt build:

    python notebooks/explore_marts.py

Explained in docs/05-phase-4-exploration.md, sections 3 to 10.
"""

import sys
import textwrap
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
from realsignal import exploration as ex  # noqa: E402


def big(x: float) -> str:
    """A count a person can read: 9420289 -> '9.4 million'."""
    for size, word in ((1e9, "billion"), (1e6, "million")):
        if x >= size:
            return f"{x / size:.1f} {word}"
    return f"{x:,.0f}"


def pct(share: float) -> str:
    return f"{100 * share:.0f} %"


def heading(text: str) -> None:
    print()
    print(text)


def wrap(text: str, indent: str = "  ") -> None:
    print(textwrap.fill(text, width=78, initial_indent=indent, subsequent_indent=indent + "  "))


def main() -> int:
    try:
        con = ex.open_warehouse()
    except ex.WarehouseNotReady as problem:
        print(problem)
        return 1
    a = ex.answers(con)
    con.close()

    print("EXPLORING THE MARTS: data/warehouse/realsignal.duckdb")
    print("Test plants are counted, but their values are never read: sealed.")

    # ---- The plants ------------------------------------------------------------
    heading("The plants")
    print("  group                       plants  used for modelling  communities")
    for group, row in a["counts"]["plants"].iterrows():
        name = "test (sealed)" if group == "test" else group
        print(f"  {name:<26}{row['plants']:>7}{row['used']:>20}{row['communities']:>13}")

    # ---- 1. The outcome ----------------------------------------------------------
    s, b = a["shape"], a["balance"]
    heading(f"1. The outcome: {s['measurement']}, training plants only")
    print(f"  {s['plants']} plants in {s['communities']} communities, "
          f"rounds {' and '.join(s['rounds'])}")
    print(f"  median {s['median']:.2f}, middle half {s['q1']:.2f} to {s['q3']:.2f}, "
          f"range {s['min']:.2f} to {s['max']:.2f}")
    print(f"  mean {s['mean']:.2f}, standard deviation {s['sd']:.2f}")
    if s["dip"] is not None:
        print(f"  two humps, near {s['peaks'][0]:.2f} and {s['peaks'][1]:.2f}, "
              f"with the dip between them at {s['dip']:.2f}")
    if s["linear"]:
        lin = s["linear"]
        print(f"  on the ordinary scale (per gram): median {big(lin['median'])}, "
              f"mean {big(lin['mean'])}")
        wrap(f"that mean is {lin['log10_of_mean']:.2f} on the log scale, higher than "
             f"{pct((s['values'] < lin['log10_of_mean']).mean())} of the plants: the "
             f"tenth of plants with the most hold {pct(lin['top_tenth_share'])} of all "
             "the pathogen counted")
    print("  plants at least this far below their round's plants with no strains:")
    rounds = list(b["cuts"][0]["by_round"]) if b["cuts"] else []
    print("    reduction                    plants   share" + "".join(f"{r:>8}" for r in rounds))
    for cut in b["cuts"]:
        label = f"{cut['reduction']} log10 ({cut['fold']:,} times)"
        print(f"    {label:<27}{cut['plants']:>8}{pct(cut['share']):>8}"
              + "".join(f"{pct(v):>8}" for v in cut["by_round"].values()))
    if b["below_dip"] is not None:
        print(f"  below the dip ({s['dip']:.2f}): {b['below_dip']} of {b['plants']} "
              f"({pct(b['below_dip'] / b['plants'])})")

    # ---- 2. Rounds ------------------------------------------------------------------
    heading("2. How much the rounds differ (outcome per round)")
    print("  group                              round  plants  median  middle half")
    for row in a["rounds"].itertuples():
        print(f"  {row.group:<35}{row.round_id:<7}{row.n:>6}{ex.fixed(row.median):>8}  "
              f"{ex.fixed(row.q1)} to {ex.fixed(row.q3)}")
    print("  the reference communities' test-round plants are test plants: sealed")
    print("  how far each median moved from the first round")
    for row in a["shifts"].itertuples():
        print(f"    {row.group:<35}{row.first_round} to {row.later_round}  {ex.fixed(row.shift, signed=True)}")
    print("  fresh weight per round, median in mg")
    for group, part in a["weights"].groupby("group", sort=False):
        print(f"    {group:<28}" + "  ".join(f"{r} {m:.1f}" for r, m in zip(part["round_id"], part["median"])))
    norm = a["normalisation"]
    print("  the authors' normalised values, worked out from the numbers:")
    if "pathogen" in norm:
        p = norm["pathogen"]
        wrap(f"pathogen: the log10 count minus the median of the round's infected "
             f"plants with no strains; {p['matching']} of {p['plants']} plants match", "    ")
    if "weight" in norm:
        w = norm["weight"]
        if w["one_number"]:
            where = ", ".join(w["matching_rounds"]) or "no round"
            others = ", ".join(f"{r} {m:.2f}" for r, m in w["healthy_medians"].items()
                               if r not in w["matching_rounds"])
            wrap(f"weight: every weight divided by one number, {w['divisor']:.2f} mg, the "
                 f"median of the plants with neither strains nor pathogen in {where} "
                 f"(the other rounds: {others})", "    ")
        else:
            wrap("weight: not one number for every plant; Phase 6 reads how", "    ")

    # ---- 3. The design ---------------------------------------------------------------
    d = a["design"]
    counts = d["counts"]
    heading("3. The design: strains per community")
    print(f"  {d['library']} strains, communities of {', '.join(str(x) for x in d['sizes'])}; "
          f"{d['communities']['training']} training and {d['communities']['test']} test "
          "communities with plants")
    for role in ("training", "test"):
        low, high = counts[role].min(), counts[role].max()
        print(f"  each strain is in {low} to {high} {role} communities "
              f"(average {counts[role].mean():.1f})")
    print(f"  rarest in training: {', '.join(counts.index[counts['training'] == counts['training'].min()])}; "
          f"most common: {', '.join(counts.index[counts['training'] == counts['training'].max()])}")
    print(f"  pairs of strains never in one training community: "
          f"{d['pairs_never_together']} of {d['pairs']}")
    print(f"  the most training communities one pair shares: {d['most_together']}")
    overlap = ", ".join(f"{n} share {k}" for k, n in d["test_overlap"].items())
    wrap(f"test communities, by the most strains they share with any one training "
         f"community: {overlap}")

    # ---- 4. Missing values, undecided plants, outliers --------------------------------
    m = a["missing"]
    heading("4. Missing values (plants with each measurement)")
    short = {"training": "train", "test": "test", "between-round reference": "ref",
             "no strains, infected": "none+P", "no strains, not infected": "none",
             "whole library": "all35"}
    print("  " + " " * 26 + "".join(f"{short.get(g, g):>8}" for g in m["present"].columns))
    print("  " + "plants in the group".ljust(26) + "".join(f"{n:>8}" for n in m["plants"]))
    for measurement, row in m["present"].iterrows():
        print(f"  {measurement:<26}" + "".join(f"{v:>8}" for v in row))
    wrap("train, test: training and test plants; ref: between-round reference; "
         "none+P and none: no strains, with and without the pathogen; all35: the "
         "whole library")
    gaps = int(m["used_missing"].sum())
    print(f"  plants used for modelling: {m['used_plants']}, missing values among them: {gaps}")
    print(f"  ...with fewer strain counts than strains: {m['strain_counts_short']}")
    print(f"  strain counts shared by two strains (training): {m['strain_rows_shared']:,} "
          f"of {m['strain_rows']:,}")
    print("  the undecided (TBD) plants, from dropped boxes, against the rest:")
    for row in a["undecided"]:
        line = (f"    {row['round_id']} {row['group']:<22} TRUE {row['TRUE_median']:.2f} "
                f"({row['TRUE_n']})  TBD {row['TBD_median']:.2f} ({row['TBD_n']})")
        print(line)
        if "boxes" in row:
            print(f"      its {row['boxes']} boxes have medians from {row['box_low']:.2f} "
                  f"to {row['box_high']:.2f}")
    o = a["outliers"]
    print(f"  plants more than {ex.OUTLIER_DISTANCE:g} log10 from the others of their community: "
          f"{len(o['listed'])}")
    print(f"    in {o['communities']} communities (listed in the report, none removed)")
    c = o["column_rule"]
    print(f"  outside 1.5 times the middle half ({c['low']:.2f} to {c['high']:.2f}): "
          f"{c['outside']}")

    # ---- 5. Noise ------------------------------------------------------------------------
    n = a["noise"]
    heading("5. Plants of one community: how much they differ")
    print(f"  standard deviation, all training plants: {n['sd_total']:.2f}")
    print(f"  standard deviation within a community  : {n['sd_within']:.2f}")
    print(f"  share of the variation between communities: {n['icc']:.2f}")
    if n["split_by_dip"]:
        sp = n["split_by_dip"]
        print(f"  communities with plants on both sides of the dip: {sp['both_sides']} "
              f"of {n['communities']}")
        print(f"    all plants below it: {sp['all_below']}, all above it: {sp['all_above']}")

    # ---- 6. One strain at a time -----------------------------------------------------------
    st = a["strains"]
    table = st["table"]
    heading("6. One strain at a time (training communities, a first look)")
    print("  difference: mean of the communities with the strain minus the rest,")
    print("  in log10 units; below zero means less pathogen where the strain was")
    print(f"  chance alone (shuffled {ex.SHUFFLES:,} times) reaches {st['threshold']:.2f}")
    print("  strain     with  difference")
    shown = list(table.index[:5]) + list(table.index[-3:])
    for i in shown:
        row = table.loc[i]
        mark = "  stands out" if row["stands_out"] else ""
        print(f"  {row['strain_id']:<10}{row['communities_with']:>5}{ex.fixed(row['difference'], signed=True):>12}{mark}")
        if i == shown[4] and len(table) > 8:
            print(f"  ... {len(table) - 8} more in the report")
    print(f"  standing out: {', '.join(st['stands_out']) or 'none'}")

    # ---- 7. Layers -------------------------------------------------------------------------
    lay = a["layers"]
    heading("7. How the other layers relate (rank correlation with question 6)")
    print(f"  chance alone (shuffled {ex.SHUFFLES:,} times) reaches {lay['threshold']:.2f}")
    for row in lay["table"].itertuples():
        mark = "  stands out" if row.stands_out else ""
        print(f"  {row.label:<42}{row.strains:>4}{ex.fixed(row.rho, signed=True):>8}{mark}")
    if lay["commensal"]:
        cm = lay["commensal"]
        wrap(f"plant by plant, total commensal load against the outcome: "
             f"{ex.fixed(cm['rho'], signed=True)} ({cm['plants']} training plants)")
    print()
    print("All of it, with every list, in docs/reports/data-quality.md:")
    print("  python scripts/make_quality_report.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
