"""
scripts/make_quality_report.py: write the data-quality report.

Reads the warehouse (read-only), asks the seven questions of Phase 4 through
src/realsignal/exploration.py and writes every answer, with the full lists,
to docs/reports/data-quality.md.

The report holds no date or time, only what the data gives. Run it twice on
the same warehouse and the file comes out byte for byte the same, so
`git diff` shows a change in the report only when the data or a choice in
dbt/dbt_project.yml changed. Test plants are counted, but their values are
never read: they stay sealed until Phase 5.

Run from the project folder, with the virtual environment active, after
scripts/load_raw.py and dbt build:

    python scripts/make_quality_report.py

Explained in docs/05-phase-4-exploration.md, section 12.
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
from realsignal import exploration as ex  # noqa: E402
from realsignal import helpers  # noqa: E402

REPORT = PROJECT_ROOT / "docs" / "reports" / "data-quality.md"


def big(x: float) -> str:
    for size, word in ((1e9, "billion"), (1e6, "million")):
        if x >= size:
            return f"{x / size:.1f} {word}"
    return f"{x:,.0f}"


def pct(share: float) -> str:
    return f"{100 * share:.0f} %"


def table(header: list, rows: list) -> list[str]:
    """A Markdown table: the header, the line under it, then one line per row."""
    lines = ["| " + " | ".join(header) + " |", "|" + "|".join("---" for _ in header) + "|"]
    lines += ["| " + " | ".join(str(cell) for cell in row) + " |" for row in rows]
    return lines


def render(a: dict) -> str:
    """The whole report as text, from the answers of exploration.answers()."""
    c, s, b = a["counts"], a["shape"], a["balance"]
    out = ["[Phase 4 guide](../05-phase-4-exploration.md) · [Handbook](../HANDBOOK.md) · "
           "[Glossary](../GLOSSARY.md)", "",
           "# Data-quality report", "",
           "Written by `scripts/make_quality_report.py` from the warehouse. Don't edit it by "
           "hand: run the script again. Every number comes from a query on the marts, through "
           "`src/realsignal/exploration.py`, so a changed source or a changed choice in "
           "`dbt/dbt_project.yml` shows up here the next time the script runs. "
           "[`docs/05-phase-4-exploration.md`](../05-phase-4-exploration.md) explains each "
           "section and what it means for the models.", ""]
    out += table(["What", "Value"], [
        ["Warehouse", f"`data/warehouse/realsignal.duckdb`, {c['tables_loaded']} tables, "
                      f"{c['rows_loaded']:,} rows loaded"],
        ["Source files' fingerprint", f"`{c['fingerprint']}` (a checksum of the checksums "
                                      "the load log records for the archive's tables and the "
                                      "two journal workbooks)"],
        ["Outcome", f"`{s['measurement']}` (the dbt setting `outcome_measurement`)"],
        ["Undecided (TBD) plants in the modelling table", f"{c['undecided_in_model']}"],
        ["Test plants", "counted, values never read: sealed until Phase 5"]])

    # ---- The plants ----------------------------------------------------------------
    out += ["", "## The plants", ""]
    out += table(["Group", "Plants", "Used for modelling", "Communities used"],
                 [[("test (sealed)" if g == "test" else g), r["plants"], r["used"], r["communities"]]
                  for g, r in c["plants"].iterrows()])

    # ---- 1 ---------------------------------------------------------------------------
    out += ["", "## 1. The shape of the outcome", "",
            f"Training plants only: {s['plants']} plants in {s['communities']} communities, "
            f"rounds {' and '.join(s['rounds'])}. Picture: "
            "[`figures/outcome_shape.png`](../../figures/outcome_shape.png).", ""]
    out += table(["Statistic", "Value"], [
        ["Median", f"{s['median']:.2f}"],
        ["Middle half (first to third quartile)", f"{s['q1']:.2f} to {s['q3']:.2f}"],
        ["Spread of the middle half (IQR)", f"{s['iqr']:.2f}"],
        ["Lowest and highest", f"{s['min']:.2f} and {s['max']:.2f}"],
        ["Mean", f"{s['mean']:.2f}"],
        ["Standard deviation", f"{s['sd']:.2f}"]])
    if s["dip"] is not None:
        out += ["", f"A smoothed histogram (kernel density estimate) has two humps, near "
                    f"**{s['peaks'][0]:.2f}** and **{s['peaks'][1]:.2f}**, and its lowest point "
                    f"between them at **{s['dip']:.2f}**."]
    if s["linear"]:
        lin = s["linear"]
        out += ["", f"Back on the ordinary scale (pathogen per gram of leaf) the median plant "
                    f"holds {big(lin['median'])} and the mean is {big(lin['mean'])}: on the log "
                    f"scale that mean is {lin['log10_of_mean']:.2f}, higher than "
                    f"{pct((s['values'] < lin['log10_of_mean']).mean())} of the plants. The tenth "
                    f"of plants with the most pathogen hold {pct(lin['top_tenth_share'])} of all "
                    f"the pathogen counted. The counts run from {big(lin['min'])} to "
                    f"{big(lin['max'])} per gram."]
    out += ["", "**Class balance.** How many training plants have at least this much less "
                "pathogen than the median of their own round's infected plants with no strains "
                "(that median: " + ", ".join(f"{r} {v:.2f}" for r, v in b["baselines"].items()
                                             if r in s["rounds"]) + ").", ""]
    rounds = s["rounds"]
    out += table(["Reduction", "Plants", "Share"] + rounds,
                 [[f"{cut['reduction']} log10 ({cut['fold']:,} times fewer)", cut["plants"],
                   pct(cut["share"])] + [pct(cut["by_round"].get(r, 0)) for r in rounds]
                  for cut in b["cuts"]])
    if b["below_dip"] is not None:
        out += ["", f"Below the dip ({s['dip']:.2f}): {b['below_dip']} of {b['plants']} plants "
                    f"({pct(b['below_dip'] / b['plants'])})."]

    # ---- 2 ---------------------------------------------------------------------------
    out += ["", "## 2. How much the rounds differ", "",
            "The outcome per round for the plants that got the same treatment in more than one "
            "round. Controls and reference plants count unless marked FALSE. The reference "
            "communities' plants in the test round are test plants, so they stay sealed. The "
            "training rows are different communities in each round. Picture: "
            "[`figures/rounds_compared.png`](../../figures/rounds_compared.png).", ""]
    out += table(["Group", "Round", "Plants", "Median", "Middle half"],
                 [[r.group, r.round_id, r.n, ex.fixed(r.median), f"{ex.fixed(r.q1)} to {ex.fixed(r.q3)}"]
                  for r in a["rounds"].itertuples()])
    out += ["", "How far each median moved from the group's first round:", ""]
    out += table(["Group", "Rounds", "Change"],
                 [[r.group, f"{r.first_round} to {r.later_round}", ex.fixed(r.shift, signed=True)]
                  for r in a["shifts"].itertuples()])
    out += ["", "Fresh weight per round (mg):", ""]
    out += table(["Group", "Round", "Plants", "Median", "Middle half"],
                 [[r.group, r.round_id, r.n, f"{r.median:.1f}", f"{r.q1:.1f} to {r.q3:.1f}"]
                  for r in a["weights"].itertuples()])
    norm = a["normalisation"]
    out += ["", "**The authors' normalised values, worked out from the numbers.** "
                "Checked on every plant outside the test set; Phase 6 reads the authors' code "
                "and confirms or corrects this.", ""]
    if "pathogen" in norm:
        p = norm["pathogen"]
        out += [f"- `{ex.PATHOGEN_NORMALISED}` is the log10 count minus the median of the "
                f"round's infected plants with no strains (" +
                ", ".join(f"{r} {v:.2f}" for r, v in p["baselines"].items()) +
                f"): {p['matching']} of {p['plants']} plants match to the ninth decimal place."]
    if "weight" in norm:
        w = norm["weight"]
        if w["one_number"]:
            where = ", ".join(w["matching_rounds"]) or "no round"
            out += [f"- `{ex.FRESH_WEIGHT_NORMALISED}` is every plant's weight divided by one "
                    f"number, {w['divisor']:.2f} mg ({w['plants']} plants checked). That's the "
                    f"median weight of the plants with neither strains nor pathogen in {where}; "
                    "the same median in each round is " +
                    ", ".join(f"{r} {v:.2f}" for r, v in w["healthy_medians"].items()) +
                    " mg, so the weights aren't adjusted round by round the way the pathogen "
                    "counts are."]
        else:
            out += [f"- `{ex.FRESH_WEIGHT_NORMALISED}` isn't the weight divided by one number."]

    # ---- 3 ---------------------------------------------------------------------------
    d = a["design"]
    counts = d["counts"]
    out += ["", "## 3. The design", "",
            f"{d['library']} strains, communities of {', '.join(str(x) for x in d['sizes'])}, "
            f"{d['communities']['training']} training and {d['communities']['test']} test "
            "communities with plants for modelling. Counting which strains a community holds "
            "reads no measurement, so test communities are included. Picture: "
            "[`figures/strain_frequency.png`](../../figures/strain_frequency.png).", ""]
    for role in ("training", "test"):
        out += [f"- Each strain is in {counts[role].min()} to {counts[role].max()} {role} "
                f"communities (average {counts[role].mean():.1f})."]
    out += [f"- Pairs of strains that never share a training community: "
            f"{d['pairs_never_together']} of {d['pairs']}. The most training communities one "
            f"pair shares: {d['most_together']}.",
            "- Test communities by the most strains they share with any one training "
            "community: " + ", ".join(f"{n} share {k}" for k, n in d["test_overlap"].items()) + ".",
            ""]
    out += table(["Strain", "Training communities", "Test communities"],
                 [[strain, row["training"], row["test"]] for strain, row in counts.iterrows()])

    # ---- 4 ---------------------------------------------------------------------------
    m = a["missing"]
    out += ["", "## 4. Missing values, undecided plants and outliers", "",
            "Plants with each measurement, by group. Picture: "
            "[`figures/missing_values.png`](../../figures/missing_values.png).", ""]
    groups = list(m["present"].columns)
    out += table(["Measurement"] + [("test (sealed)" if g == "test" else g) for g in groups],
                 [["plants in the group"] + [m["plants"][g] for g in groups]]
                 + [[f"`{name}`"] + list(row) for name, row in m["present"].iterrows()])
    out += ["", f"Among the {m['used_plants']} plants used for modelling, missing values: "
                f"{int(m['used_missing'].sum())}. Plants with fewer strain counts than their "
                f"community has strains: {m['strain_counts_short']}. Strain counts that two "
                f"strains share (they couldn't be told apart on the plate), training plants: "
                f"{m['strain_rows_shared']:,} of {m['strain_rows']:,}."]
    out += ["", "**The undecided (TBD) plants**, from boxes that were dropped, against the rest "
                "of their round (median outcome, plants in brackets):", ""]
    rows = []
    for r in a["undecided"]:
        boxes = (f"{r['boxes']} boxes, medians {r['box_low']:.2f} to {r['box_high']:.2f}"
                 if "boxes" in r else "n/a")
        rows.append([r["round_id"], r["group"], f"{r['TRUE_median']:.2f} ({r['TRUE_n']})",
                     f"{r['TBD_median']:.2f} ({r['TBD_n']})", boxes])
    out += table(["Round", "Group", "TRUE", "TBD", "Box to box"], rows)
    o = a["outliers"]
    rule = o["column_rule"]
    out += ["", f"**Outliers.** Training plants more than {ex.OUTLIER_DISTANCE:g} log10 units "
                f"({10 ** ex.OUTLIER_DISTANCE:,.0f} times) from the median of the other plants "
                f"of their community: {len(o['listed'])}, in {o['communities']} communities. "
                "They're listed, not removed. By the usual rule for a whole column (beyond 1.5 "
                f"times the middle half, here {rule['low']:.2f} to {rule['high']:.2f}), "
                f"{rule['outside']} plants would count as outliers.", ""]
    out += table(["Plant", "Community", "Round", "Outcome", "Others' median", "Distance"],
                 [[r.plant_id, r.community_id, r.round_id, f"{r.outcome:.2f}",
                   f"{r.others_median:.2f}", f"{r.distance:.2f}"] for r in o["listed"].itertuples()])

    # ---- 5 ---------------------------------------------------------------------------
    n = a["noise"]
    out += ["", "## 5. How much plants of one community differ", ""]
    out += table(["Statistic", "Value"], [
        ["Standard deviation, all training plants", f"{n['sd_total']:.2f}"],
        ["Standard deviation within a community", f"{n['sd_within']:.2f}"],
        ["Share of the variation between communities (intraclass correlation)", f"{n['icc']:.2f}"],
        ["Plants per community", ", ".join(f"{k} plants: {v}" for k, v in
                                           sorted(n["plants_per_community"].items(), reverse=True))]])
    if n["split_by_dip"]:
        sp = n["split_by_dip"]
        out += ["", f"Communities with plants on both sides of the dip ({s['dip']:.2f}): "
                    f"{sp['both_sides']} of {n['communities']}. All plants below it: "
                    f"{sp['all_below']}; all above it: {sp['all_above']}."]

    # ---- 6 ---------------------------------------------------------------------------
    st = a["strains"]
    out += ["", "## 6. One strain at a time", "",
            f"For each strain, the mean outcome of the {st['communities']} training communities "
            "that hold it minus the mean of those that don't, community by community (each "
            "community's plants averaged first). Below zero: less pathogen where the strain "
            f"was. Shuffling the community means {ex.SHUFFLES:,} times (seed {ex.SEED}), the "
            f"largest difference of any strain reached **{st['threshold']:.2f}** in 95 % of the "
            "shuffles; a strain stands out only beyond that. A first look, not a model: strains "
            "share communities, so one strain's difference carries some of its partners'. "
            "Picture: [`figures/one_strain_at_a_time.png`](../../figures/one_strain_at_a_time.png).",
            ""]
    out += table(["Strain", "Communities with it", "Mean with it", "Difference", "Stands out"],
                 [[r.strain_id, r.communities_with, f"{r.mean_with:.2f}", ex.fixed(r.difference, signed=True),
                   "yes" if r.stands_out else ""] for r in st["table"].itertuples()])

    # ---- 7 ---------------------------------------------------------------------------
    lay = a["layers"]
    out += ["", "## 7. How the other layers relate", "",
            "Spearman's rank correlation between each strain property and the differences of "
            "section 6 (1: the two orders agree, -1: reversed, 0: no relation). Shuffling the "
            f"differences {ex.SHUFFLES:,} times, the largest correlation of any property reached "
            f"**{lay['threshold']:.2f}** in 95 % of the shuffles.", ""]
    out += table(["Property", "Strains", "Correlation", "Stands out"],
                 [[r.label, r.strains, ex.fixed(r.rho, signed=True), "yes" if r.stands_out else ""]
                  for r in lay["table"].itertuples()])
    if lay["commensal"]:
        cm = lay["commensal"]
        out += ["", f"Plant by plant, the total commensal load (all the community's bacteria, "
                    f"log10 per gram, median {cm['median']:.2f}, middle half {cm['q1']:.2f} to "
                    f"{cm['q3']:.2f}) against the outcome: rank correlation {ex.fixed(cm['rho'], signed=True)}, "
                    f"{cm['plants']} training plants."]
    out += [""]
    return "\n".join(out)


def main() -> int:
    try:
        con = ex.open_warehouse()
    except ex.WarehouseNotReady as problem:
        print(problem)
        return 1
    answers = ex.answers(con)
    con.close()
    text = render(answers)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    before = REPORT.read_bytes() if REPORT.exists() else None
    with open(REPORT, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
    status = ("unchanged" if before == text.encode("utf-8")
              else "new" if before is None else "changed")
    print(f"Wrote {helpers.rel(REPORT, PROJECT_ROOT)} ({text.count(chr(10))} lines, {status})")
    print(f"  source files' fingerprint: {answers['counts']['fingerprint']}")
    print(f"  outcome: {answers['shape']['measurement']}, "
          f"{answers['shape']['plants']} training plants; test plants sealed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
