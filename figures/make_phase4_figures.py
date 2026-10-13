"""
figures/make_phase4_figures.py: the pictures for Phase 4, the first ones drawn
from measured values.

    figures/outcome_shape.png         the training outcome on an ordinary and a
                                      log scale, with its two humps
    figures/rounds_compared.png       the plants grown with the same treatment
                                      in more than one round
    figures/strain_frequency.png      how many training and test communities
                                      hold each strain
    figures/missing_values.png        which plants have which measurement
    figures/one_strain_at_a_time.png  communities with each strain against the
                                      rest, and what chance alone gives

Every number comes from src/realsignal/exploration.py, the functions the
explorer and the data-quality report use. Test plants are counted (figures 3
and 4), but their values are never read: no test value is drawn.

Run from the project folder, with the virtual environment active, after
scripts/load_raw.py and dbt build (run inside dbt/):

    python figures/make_phase4_figures.py

Explained in docs/05-phase-4-exploration.md.
"""

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")                              # draw to files, never open a window
import matplotlib.pyplot as plt                     # noqa: E402
import numpy as np                                  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from realsignal import exploration as ex            # noqa: E402

OUT = ROOT / "figures"

# The project's colours (as in the other figure scripts). The three rounds
# use blue, gold and green in that order, a set that passes a colour-blindness
# check; every series also has a label, so colour is never the only clue.
BLUE, GREEN, GOLD, PURPLE, RED, GREY = "#5B8DEF", "#4CAF7D", "#C9A227", "#9C6ADE", "#D9634C", "#8A94A6"
INK, SOFT, LINE, SURFACE = "#1F2933", "#5F6B7A", "#D5DCE6", "#FBFCFE"
PALE = {BLUE: "#EAF1FD", GREEN: "#E6F4EA", GOLD: "#FFF3CD", GREY: "#F1F3F6", RED: "#FBEAE6"}
ROUND_COLOURS = [BLUE, GOLD, GREEN, PURPLE]

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11, "text.color": INK,
                     "axes.labelcolor": INK, "xtick.color": SOFT, "ytick.color": SOFT,
                     "axes.edgecolor": LINE, "axes.facecolor": SURFACE,
                     "figure.facecolor": SURFACE, "savefig.facecolor": SURFACE})


def tidy(ax):
    """Recessive axes: no box, a light grid behind the data."""
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.grid(True, color=LINE, linewidth=0.8, alpha=0.7)
    ax.set_axisbelow(True)


def titles(fig, title, subtitle):
    """A bold title and a grey line under it, the same distance from the top in
    every picture whatever its height."""
    height = fig.get_size_inches()[1]
    fig.text(0.03, 1 - 0.22 / height, title, fontsize=17, weight="bold", va="top")
    fig.text(0.03, 1 - 0.62 / height, subtitle, fontsize=11.5, color=SOFT, va="top")


def save(fig, name):
    path = OUT / name
    fig.savefig(path, dpi=100)
    plt.close(fig)
    print(f"  drew {path.relative_to(ROOT).as_posix()}")


# ---------------------------------------------------------------------------
# 1. The shape of the outcome
# ---------------------------------------------------------------------------

def outcome_shape_figure(con):
    s = ex.outcome_shape(con)
    base = ex.class_balance(con, s)["baselines"]
    y = s["values"]
    fig = plt.figure(figsize=(14, 5.8), dpi=100)
    titles(fig, f"The outcome, {s['plants']} training plants: the same numbers on two scales",
           f"{s['measurement']}: the pathogen counted per gram of leaf. "
           "Test plants are sealed and not drawn.")
    left = fig.add_axes([0.06, 0.13, 0.4, 0.66])
    right = fig.add_axes([0.55, 0.13, 0.42, 0.66])

    if s["linear"]:
        counts = 10 ** y
        left.hist(counts / 1e9, bins=40, color=GREY, edgecolor=SURFACE, linewidth=1)
        lin = s["linear"]
        top = left.get_ylim()[1]
        for value, text, colour, height in (
                (lin["median"], f"median: {lin['median'] / 1e6:.1f} million", BLUE, 0.88),
                (lin["mean"], f"mean: {lin['mean'] / 1e6:.0f} million", RED, 0.72)):
            left.axvline(value / 1e9, color=colour, linewidth=2)
            left.annotate(text, (value / 1e9, top * height), xytext=(counts.max() / 1e9 * 0.25, top * height),
                          va="center", fontsize=10.5,
                          arrowprops={"arrowstyle": "-", "color": colour, "linewidth": 1})
        left.set_xlabel("pathogen per gram of leaf, in billions")
        left.set_title("An ordinary scale: most plants in the first bar",
                       loc="left", fontsize=12, color=INK)
    left.set_ylabel("plants")
    tidy(left)

    bins = np.arange(np.floor(y.min() * 4) / 4, np.ceil(y.max() * 4) / 4 + 0.25, 0.25)
    right.hist(y, bins=bins, color=PALE[BLUE], edgecolor=BLUE, linewidth=1)
    scale = len(y) * 0.25                        # density times plants times bar width = plants
    right.plot(s["grid"], s["density"] * scale, color=BLUE, linewidth=2)
    top = right.get_ylim()[1] * 1.25              # room above the bars for the labels
    right.set_ylim(0, top)
    for peak in s["peaks"]:
        right.annotate(f"hump near {peak:.2f}", (peak, np.interp(peak, s["grid"], s["density"]) * scale),
                       xytext=(peak, top * 0.93), ha="center", va="center", fontsize=10.5,
                       arrowprops={"arrowstyle": "-", "color": BLUE, "linewidth": 1})
    if s["dip"] is not None:
        right.axvline(s["dip"], color=GOLD, linewidth=2, linestyle="--")
        right.text(s["dip"] + 0.08, top * 0.8, f"dip: {s['dip']:.2f}", fontsize=10.5)
    rounds = [base[r] for r in s["rounds"] if r in base]
    if rounds:
        right.axvspan(min(rounds) - 0.03, max(rounds) + 0.03, facecolor=PALE[RED], edgecolor=RED,
                      linewidth=1, zorder=0)
        right.text(max(rounds) + 0.12, top * 0.62, "plants with\nno strains\n(round medians)",
                   fontsize=10, color=INK, va="top")
    right.set_xlabel("log10 of the pathogen per gram (each step is ten times more)")
    right.set_title("A log scale: two humps appear", loc="left", fontsize=12, color=INK)
    right.set_ylabel("plants")
    tidy(right)
    save(fig, "outcome_shape.png")


# ---------------------------------------------------------------------------
# 2. Rounds compared
# ---------------------------------------------------------------------------

def rounds_figure(con):
    plants = ex.values(con, ex.outcome_name(con))
    plants = plants[(plants["plant_group"] != "training") & (plants["inclusion_mark"] != "FALSE")]
    groups = [("no strains, infected", "No strains", plants["plant_group"] == "no strains, infected"),
              ("whole library", "Whole library", plants["plant_group"] == "whole library")]
    references = (plants[plants["plant_group"] == "between-round reference"]
                  [["community_id", "label"]].drop_duplicates().itertuples(index=False))
    for community, label in references:
        groups.append((community, f"{community}\n({label})" if label != community else community,
                       (plants["plant_group"] == "between-round reference")
                       & (plants["community_id"] == community)))
    rounds = ex.round_order(plants["round_id"])
    rng = np.random.default_rng(ex.SEED)          # the sideways scatter is the same every time
    fig = plt.figure(figsize=(13, 6.2), dpi=100)
    titles(fig, "The same treatment in different rounds",
           "Each dot is a plant, each bar its round's median. "
           "Reference communities in the test round are test plants: sealed.")
    ax = fig.add_axes([0.07, 0.16, 0.78, 0.63])
    width = 0.8 / len(rounds)
    for g, (_, name, mask) in enumerate(groups):
        part = plants[mask]
        for r, round_id in enumerate(rounds):
            values = part.loc[part["round_id"] == round_id, "value"].to_numpy()
            if not len(values):
                continue
            x = g + (r - (len(rounds) - 1) / 2) * width
            ax.scatter(x + rng.uniform(-width / 4, width / 4, len(values)), values, s=46,
                       color=ROUND_COLOURS[r % len(ROUND_COLOURS)], edgecolor=SURFACE,
                       linewidth=1.2, zorder=3, label=round_id if g == 0 else None)
            ax.hlines(np.median(values), x - width / 2.6, x + width / 2.6, color=INK, linewidth=2.5, zorder=4)
    ax.set_xticks(range(len(groups)))
    ax.set_xticklabels([name for _, name, _ in groups])
    ax.set_ylabel(f"{ex.outcome_name(con)}")
    ax.legend(title="round", frameon=False, loc="upper left", bbox_to_anchor=(1.01, 1))
    tidy(ax)
    ax.grid(False, axis="x")
    save(fig, "rounds_compared.png")


# ---------------------------------------------------------------------------
# 3. How often each strain appears
# ---------------------------------------------------------------------------

def strain_frequency_figure(con):
    d = ex.design_balance(con)
    counts = d["counts"].sort_values(["training", "test"], ascending=False, kind="stable")
    fig = plt.figure(figsize=(14, 5.8), dpi=100)
    titles(fig, "How many communities hold each strain",
           f"{d['communities']['training']} training and {d['communities']['test']} test "
           f"communities with plants, {', '.join(str(x) for x in d['sizes'])} strains each. "
           "This counts membership only, so the test communities can be shown.")
    ax = fig.add_axes([0.05, 0.2, 0.78, 0.6])
    x = np.arange(len(counts))
    ax.bar(x - 0.2, counts["training"], width=0.38, color=BLUE, label="training communities")
    ax.bar(x + 0.2, counts["test"], width=0.38, color=GOLD, label="test communities")
    ax.set_xticks(x)
    ax.set_xticklabels(counts.index, rotation=60, ha="right", fontsize=9.5)
    ax.set_ylabel("communities")
    ax.legend(frameon=False, loc="upper left", bbox_to_anchor=(1.0, 1))
    tidy(ax)
    ax.grid(False, axis="x")
    save(fig, "strain_frequency.png")


# ---------------------------------------------------------------------------
# 4. Missing values
# ---------------------------------------------------------------------------

def missing_values_figure(con):
    m = ex.missing_values(con)
    present, plants = m["present"], m["plants"]
    rows, cols = present.shape
    fig = plt.figure(figsize=(14, 6.6), dpi=100)
    titles(fig, "Which plants have which measurement",
           f"Each cell: plants with the measurement, of the plants in the group. Plants used "
           f"for modelling with a value missing: {int(m['used_missing'].sum())}.")
    ax = fig.add_axes([0.2, 0.1, 0.78, 0.68])
    fig.text(0.2, 0.03, "Green: every plant in the group has it.  Gold: some do.  Grey: none do.",
             fontsize=10.5, color=SOFT)
    ax.set_xlim(0, cols)
    ax.set_ylim(rows, 0)
    for i, measurement in enumerate(present.index):
        for j, group in enumerate(present.columns):
            have, total = present.iloc[i, j], plants[group]
            colour = GREEN if have == total else GREY if have == 0 else GOLD
            ax.add_patch(plt.Rectangle((j + 0.04, i + 0.06), 0.92, 0.88, facecolor=PALE[colour],
                                       edgecolor=colour, linewidth=1.2))
            ax.text(j + 0.5, i + 0.5, f"{have} of {total}" if have else "none", ha="center",
                    va="center", fontsize=10)
    ax.set_xticks(np.arange(cols) + 0.5)
    ax.set_xticklabels([("test\n(sealed)" if g == "test" else g.replace(", ", ",\n")) for g in present.columns],
                       fontsize=10)
    ax.xaxis.tick_top()
    ax.set_yticks(np.arange(rows) + 0.5)
    ax.set_yticklabels(present.index, fontsize=10)
    for side in ax.spines.values():
        side.set_visible(False)
    ax.tick_params(length=0)
    save(fig, "missing_values.png")


# ---------------------------------------------------------------------------
# 5. One strain at a time
# ---------------------------------------------------------------------------

def one_strain_figure(con):
    st = ex.one_strain_at_a_time(con)
    table = st["table"].iloc[::-1]               # the lowest difference ends up at the top
    fig = plt.figure(figsize=(12, 10.5), dpi=100)
    titles(fig, "One strain at a time: communities with it against the rest",
           f"Mean outcome of the {st['communities']} training communities holding the strain minus the "
           "rest, in log10. A first look, not a model.")
    ax = fig.add_axes([0.11, 0.07, 0.84, 0.82])
    y = np.arange(len(table))
    colours = [BLUE if out else GREY for out in table["stands_out"]]
    ax.axvspan(-st["threshold"], st["threshold"], color=PALE[GOLD], zorder=0)
    ax.barh(y, table["difference"], color=colours, height=0.7, zorder=2)
    ax.axvline(0, color=INK, linewidth=1)
    ax.set_yticks(y)
    ax.set_yticklabels(table["strain_id"], fontsize=9.5)
    ax.set_xlabel("difference in log10 units (below zero: less pathogen where the strain was)")
    ax.text(-st["threshold"] - 0.25, len(table) * 0.3,
            f"The shaded band is what chance\nalone gives: shuffled {ex.SHUFFLES:,} times,\n"
            f"the largest difference of any\nstrain stayed within {st['threshold']:.2f}\n"
            "in 95 % of the shuffles.", fontsize=10, va="center", ha="right")
    for row_y, (_, row) in zip(y, table.iterrows()):
        if row["stands_out"]:
            ax.text(row["difference"] - 0.04, row_y, f"{row['difference']:+.2f}", ha="right",
                    va="center", fontsize=10)
    lowest = table["difference"].min()
    ax.set_xlim(min(lowest - 0.45, -st["threshold"] - 1.6), max(table["difference"].max(), st["threshold"]) + 0.3)
    tidy(ax)
    ax.grid(False, axis="y")
    save(fig, "one_strain_at_a_time.png")


def main() -> int:
    try:
        con = ex.open_warehouse()
    except ex.WarehouseNotReady as problem:
        print(f"  skipped the Phase 4 pictures: {problem.args[0].splitlines()[0]}")
        return 1
    with con:
        outcome_shape_figure(con)
        rounds_figure(con)
        strain_frequency_figure(con)
        missing_values_figure(con)
        one_strain_figure(con)
    return 0


if __name__ == "__main__":
    sys.exit(main())
