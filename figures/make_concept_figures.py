"""
figures/make_concept_figures.py: the pictures that explain RealSignal's ideas.

These figures teach concepts, so they need no data and can be drawn on any
computer, before anything is downloaded. Each one is used by a guide:

    figures/combinations.png      why you can't test every community     (README, Handbook Stage 0)
    figures/screening_design.png  the screen, explained as a 5-a-side league (README, Phase 1 guide)
    figures/three_way.png         paper, original R code, Python rebuild   (README, Roadmap Phase 6)
    figures/data_layers.png       five layers of data, one strain key      (README, Roadmap, architecture)
    figures/fetch_pipeline.png    the six steps of Phase 1                 (Phase 1 guide, Handbook Stage 3)
    figures/log_scale.png         why bacterial counts use a log scale     (Phase 1 guide, Glossary)

and one interactive page, which works offline in any browser:

    docs/interactive/combinations.html   change the pool size, the team size and the
                                         yearly testing rate, and see the arithmetic

The screening picture is an illustration with made-up teams; every other
number in these figures is either arithmetic or comes from the published paper.

Run from the project folder, with the virtual environment active:
    python figures/make_concept_figures.py
"""

import math
import random
from pathlib import Path

import matplotlib

matplotlib.use("Agg")          # draw straight to files; no window needed
import matplotlib.pyplot as plt                      # noqa: E402
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Rectangle  # noqa: E402

OUT = Path(__file__).resolve().parent

# The same colours as the logo and the journey map, so the pictures look like
# one family. Colour marks identity only; every label is written in dark ink.
BLUE, GREEN, GOLD, PURPLE, RED, GREY = "#5B8DEF", "#4CAF7D", "#C9A227", "#9C6ADE", "#D9634C", "#8A94A6"
INK, SOFT, LINE, SURFACE = "#1F2933", "#5F6B7A", "#D5DCE6", "#FBFCFE"
PALE = {BLUE: "#EAF1FD", GREEN: "#E6F4EA", GOLD: "#FFF3CD", PURPLE: "#F2EAFB", RED: "#FBEAE6", GREY: "#F1F3F6"}

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11, "text.color": INK,
                     "figure.facecolor": SURFACE, "savefig.facecolor": SURFACE})


def canvas(width, height):
    """A blank figure whose coordinates run from 0 to width and 0 to height."""
    fig = plt.figure(figsize=(width / 100, height / 100), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, width)
    ax.set_ylim(0, height)
    ax.axis("off")
    return fig, ax


def box(ax, x, y, w, h, colour, title, body="", title_size=13, body_size=10.5):
    """A rounded card with a coloured edge, a bold title and a few lines of text."""
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=14",
                                linewidth=2.2, edgecolor=colour, facecolor=PALE.get(colour, "white")))
    ax.text(x + w / 2, y + h - 22, title, ha="center", va="top", fontsize=title_size, fontweight="bold")
    if body:
        ax.text(x + w / 2, y + h - 50, body, ha="center", va="top", fontsize=body_size, color=SOFT,
                linespacing=1.35)


def arrow(ax, start, end, colour=GREY, width=2.2, style="-|>", rad=0.0):
    ax.add_patch(FancyArrowPatch(start, end, arrowstyle=style, mutation_scale=18, linewidth=width,
                                 color=colour, connectionstyle=f"arc3,rad={rad}"))


def save(fig, name):
    fig.savefig(OUT / name, dpi=100)
    plt.close(fig)
    print(f"  drew figures/{name}")


# ---------------------------------------------------------------------------
# 1. Why nobody tests every community
# ---------------------------------------------------------------------------

def combinations_figure():
    pool, size, per_square = 35, 5, 100
    total = math.comb(pool, size)                     # 324,632
    squares = math.ceil(total / per_square)           # 3,247
    screened = 136 + 70                               # the published screen: training + test communities
    fig, ax = canvas(1100, 640)
    ax.text(40, 612, f"Every {size}-strain community from {pool} strains: {total:,} of them",
            fontsize=19, fontweight="bold", va="top")
    ax.text(40, 578, f"Each small square stands for {per_square} communities, so there are {squares:,} squares. "
            f"At {per_square} communities a year, testing them all", fontsize=12, color=SOFT, va="top")
    ax.text(40, 558, f"would take {total / per_square:,.0f} years. The published screen tested {screened} "
            "communities: the two gold squares in the top left corner.", fontsize=12, color=SOFT, va="top")
    cols, cell, gap = 100, 8, 2
    left, top = 40, 492
    for i in range(squares):
        r, c = divmod(i, cols)
        colour = GOLD if i < round(screened / per_square) else "#C8D3E6"
        ax.add_patch(Rectangle((left + c * (cell + gap), top - r * (cell + gap) - cell), cell, cell,
                               facecolor=colour, edgecolor="none"))
    ax.annotate(f"{screened} communities tested (136 to learn from, 70 to test on)",
                xy=(left + cell + gap / 2, top + 1), xytext=(left + 70, top + 22),
                fontsize=11, fontweight="bold", va="center",
                arrowprops=dict(arrowstyle="-|>", color=INK, linewidth=1.4, connectionstyle="arc3,rad=0.0"))
    rows = math.ceil(squares / cols)
    bottom = top - rows * (cell + gap)
    ax.text(40, bottom - 22, "Even at 1,000 communities a year it would take over 300 years. That is why the "
            "study tested a random sample", fontsize=11.5, va="top")
    ax.text(40, bottom - 42, "and let a model learn which strains matter from it.", fontsize=11.5, va="top")
    ax.text(40, 20, "Arithmetic: 35 choose 5 = 324,632. The yearly rate is an assumption; change it in "
            "docs/interactive/combinations.html.", fontsize=9.5, color=SOFT)
    save(fig, "combinations.png")


# ---------------------------------------------------------------------------
# 2. The screen as a five-a-side league
# ---------------------------------------------------------------------------

def plant(ax, x, y, pathogen):
    """A small plant: a stem, two leaves, and red dots for the pathogen that grew."""
    ax.plot([x, x], [y, y + 46], color="#3E7D4F", linewidth=3, solid_capstyle="round")
    for dx, dy, angle in ((-13, 30, 35), (13, 22, -35)):
        leaf = matplotlib.patches.Ellipse((x + dx, y + dy), 26, 12, angle=angle, facecolor=GREEN,
                                          edgecolor="#3E7D4F", linewidth=1.2)
        ax.add_patch(leaf)
    rng = random.Random(int(x * 7 + y))
    for _ in range(pathogen):
        ax.add_patch(Circle((x + rng.uniform(-22, 22), y + rng.uniform(16, 40)), 2.4, color=RED))


def screening_figure():
    rng = random.Random(7)
    fig, ax = canvas(1200, 650)
    ax.text(40, 622, "The screen in one picture: random teams, then work backwards", fontsize=19,
            fontweight="bold", va="top")
    ax.text(40, 588, "It works like finding the players who win matches in a 5-a-side league. Nobody plays "
            "alone, so you form many", fontsize=11.5, color=SOFT, va="top")
    ax.text(40, 568, "random teams, record every result, and look for the players who keep turning up in "
            "the winning teams.", fontsize=11.5, color=SOFT, va="top")

    # three strains (gold) stand for the ones the paper found protective
    stars = {7, 19, 28}
    top, height = 110, 400
    box(ax, 30, top, 230, height, BLUE, "1. The pool", "35 harmless leaf\nbacteria (strains)")
    for i in range(35):
        r, c = divmod(i, 5)
        ax.add_patch(Circle((80 + c * 33, 395 - r * 36), 11, facecolor=GOLD if i in stars else BLUE,
                            edgecolor="white", linewidth=1.5))

    box(ax, 300, top, 250, height, PURPLE, "2. Random teams", "136 teams of 5,\nsix of them shown")
    teams = []
    for t_ in range(6):
        team = rng.sample(sorted(set(range(35)) - stars), 5)
        if t_ in (1, 4):
            team[2] = sorted(stars)[t_ % 3]          # two teams happen to hold a protective strain
        teams.append(team)
        for k, s in enumerate(team):
            ax.add_patch(Circle((345 + k * 34, 395 - t_ * 46), 11, facecolor=GOLD if s in stars else BLUE,
                                edgecolor="white", linewidth=1.5))

    box(ax, 590, top, 260, height, GREEN, "3. Plants + pathogen",
        "each team goes on its own\nplants; the pathogen (red)\ngrows where nothing stops it")
    for t_, team in enumerate(teams):
        protected = any(s in stars for s in team)
        plant(ax, 650 + (t_ % 3) * 70, 255 - (t_ // 3) * 120, 3 if protected else 14)
        ax.text(650 + (t_ % 3) * 70, 237 - (t_ // 3) * 120, f"team {t_ + 1}", ha="center", fontsize=9, color=SOFT)

    box(ax, 885, top, 290, height, GOLD, "4. Work backwards",
        "count the pathogen for each team,\nthen ask which strains keep\nturning up in the low counts")
    for t_, team in enumerate(teams):
        protected = any(s in stars for s in team)
        y = 380 - t_ * 40
        for k, s in enumerate(team):
            ax.add_patch(Circle((912 + k * 16, y + 8), 6.5, facecolor=GOLD if s in stars else BLUE,
                                edgecolor="white", linewidth=1))
        length = 25 if protected else 110
        ax.add_patch(Rectangle((1000, y), length, 16, facecolor=RED, edgecolor="none"))
        ax.text(1000 + length + 7, y + 8, "low" if protected else "high", va="center", fontsize=10, color=SOFT)
    ax.text(1030, 122, "gold turns up where\nthe count is low", ha="center", va="bottom", fontsize=11.5,
            fontweight="bold", linespacing=1.3)

    for x0, x1 in ((262, 298), (552, 588), (852, 883)):
        arrow(ax, (x0, 310), (x1, 310), colour=INK)
    ax.text(40, 72, "Gold marks the strains the study found protective. The teams and plants here are an "
            "illustration, not the real data.", fontsize=10.5, color=SOFT)
    ax.text(40, 48, "The real screen: 136 teams in two rounds, and 70 more teams in a separate third round "
            "kept back for testing.", fontsize=10.5, color=SOFT)
    save(fig, "screening_design.png")


# ---------------------------------------------------------------------------
# 3. The three-way comparison
# ---------------------------------------------------------------------------

def three_way_figure():
    fig, ax = canvas(1100, 640)
    ax.text(550, 610, "Three results, three comparisons", ha="center", fontsize=19, fontweight="bold", va="top")
    ax.text(550, 578, "When two numbers disagree, a third one tells you where the difference comes from.",
            ha="center", fontsize=12, color=SOFT, va="top")
    corners = {"paper": (550, 430), "r": (230, 150), "py": (870, 150)}
    w, h = 270, 110
    box(ax, corners["paper"][0] - w / 2, corners["paper"][1] - h / 2, w, h, GOLD,
        "The published paper", "the numbers printed in it")
    box(ax, corners["r"][0] - w / 2, corners["r"][1] - h / 2, w, h, BLUE,
        "Their R code, run here", "the authors' scripts from\nthe archive (Phase 6)")
    box(ax, corners["py"][0] - w / 2, corners["py"][1] - h / 2, w, h, GREEN,
        "The Python rebuild", "written from the paper alone\n(Phase 5, locked first)")
    arrow(ax, (440, 385), (300, 210), INK, style="<|-|>")
    arrow(ax, (660, 385), (800, 210), INK, style="<|-|>")
    arrow(ax, (370, 150), (730, 150), INK, style="<|-|>")
    ax.text(350, 300, "Does the released code\nreproduce its own paper?", ha="right", fontsize=11.5,
            fontweight="bold")
    ax.text(750, 300, "Does the finding survive\na different toolchain?", ha="left", fontsize=11.5,
            fontweight="bold")
    ax.text(550, 112, "Did the rebuild get the method right?", ha="center", fontsize=11.5, fontweight="bold")
    ax.text(550, 40, "Only one side disagrees? Then you know which of the three to look at. "
            "With two results you could only say that they differ.", ha="center", fontsize=10.5, color=SOFT)
    save(fig, "three_way.png")


# ---------------------------------------------------------------------------
# 4. Five layers of data, one strain key
# ---------------------------------------------------------------------------

def data_layers_figure():
    fig, ax = canvas(1150, 700)
    ax.text(575, 672, "Five layers of data from four published sources, joined on one strain name",
            ha="center", fontsize=18, fontweight="bold", va="top")
    ax.text(575, 640, "Every layer describes strains from the same collection of leaf bacteria, so a name "
            "such as Leaf76 links them.", ha="center", fontsize=11.5, color=SOFT, va="top")
    cx, cy = 575, 330
    ax.add_patch(Circle((cx, cy), 78, facecolor="white", edgecolor=INK, linewidth=2.5))
    ax.text(cx, cy + 14, "strain name", ha="center", fontsize=12, color=SOFT)
    ax.text(cx, cy - 16, "Leaf76", ha="center", fontsize=17, fontweight="bold")
    layers = [
        ((70, 430), BLUE, "1. Communities + outcome", "which strains were in each\nteam, and how much pathogen\nEmmenegger 2023, Zenodo", "downloaded in Phase 1"),
        ((800, 430), GREEN, "2. Genomes", "each strain's DNA\nBai 2015", "access checked in Phase 2"),
        ((800, 120), PURPLE, "3. Gene clusters", "the chemistry each strain\ncould make (predicted)\nHelfrich 2018", "access checked in Phase 2"),
        ((435, 40), GOLD, "4. Inhibition network", "which strain holds back\nwhich, in pairs\nHelfrich 2018", "access checked in Phase 2"),
        ((70, 120), RED, "5. Single-strain protection", "each strain tested alone\nagainst the pathogen\nVogel 2021", "access checked in Phase 2"),
    ]
    w, h = 280, 160
    for (x, y), colour, title, body, status in layers:
        box(ax, x, y, w, h, colour, title, body, title_size=12.5, body_size=10.5)
        ax.text(x + w / 2, y + 16, status, ha="center", fontsize=10, fontweight="bold",
                color=INK if "downloaded" in status else SOFT)
        bx = x + w / 2
        by = y + h / 2
        dx, dy = cx - bx, cy - by
        dist = math.hypot(dx, dy)
        start = (bx + dx * (w * 0.55) / dist, by + dy * (h * 0.62) / dist)
        end = (cx - dx * 82 / dist, cy - dy * 82 / dist)
        ax.plot([start[0], end[0]], [start[1], end[1]], color=colour, linewidth=3, solid_capstyle="round")
    save(fig, "data_layers.png")


# ---------------------------------------------------------------------------
# 5. Phase 1 in six steps
# ---------------------------------------------------------------------------

def fetch_pipeline_figure():
    fig, ax = canvas(1200, 430)
    ax.text(40, 400, "Phase 1: six steps from a public archive to data you can trust", fontsize=19,
            fontweight="bold", va="top")
    ax.text(40, 368, "python scripts/fetch_data.py runs all six; --probe runs only the first.", fontsize=12,
            color=SOFT, va="top")
    steps = [
        (BLUE, "1. Probe", "ask how big the file\nis; nothing is fetched"),
        (BLUE, "2. Download", "stream it to disk\nunder a .part name"),
        (GOLD, "3. Verify", "compare its checksum\nwith Zenodo's"),
        (PURPLE, "4. Unpack", "skip unsafe entries\nand Mac clutter"),
        (GREEN, "5. Inventory", "list every file\nin manifest.csv"),
        (GREEN, "6. Log", "record the source,\ndate and checksum"),
    ]
    w, h, gap = 178, 150, 14
    for i, (colour, title, body) in enumerate(steps):
        x = 40 + i * (w + gap)
        box(ax, x, 150, w, h, colour, title, body, title_size=12.5, body_size=10.5)
        if i < len(steps) - 1:
            arrow(ax, (x + w + 1, 225), (x + w + gap - 1, 225), INK, width=1.8)
    # the read-only zone under steps 2 to 6
    ax.add_patch(FancyBboxPatch((232, 40), 950, 80, boxstyle="round,pad=0,rounding_size=12",
                                facecolor="#F1F3F6", edgecolor=GREY, linewidth=1.5, linestyle="--"))
    ax.text(707, 92, "data/raw/   the evidence: written only by this script, never edited, never committed to Git",
            ha="center", fontsize=11.5, fontweight="bold")
    ax.text(707, 62, "MISMATCH at step 3 stops the run before anything is unpacked.", ha="center",
            fontsize=10.5, color=SOFT)
    save(fig, "fetch_pipeline.png")


# ---------------------------------------------------------------------------
# 6. Why counts of bacteria use a log scale
# ---------------------------------------------------------------------------

def log_scale_figure():
    fig, ax = canvas(1100, 470)
    ax.text(40, 445, "Why counts of bacteria are drawn on a log scale", fontsize=19, fontweight="bold", va="top")
    ax.text(40, 413, "The pathogen counts in this study run from about 10,000 to about 1,000,000,000 per gram "
            "of leaf.", fontsize=12, color=SOFT, va="top")
    values = [10 ** k for k in range(4, 10)]
    names = ["10,000", "100,000", "1 million", "10 million", "100 million", "1 billion"]
    left, right = 70, 1030

    # ordinary (linear) scale: everything but the last value is squashed at the left
    y1 = 300
    ax.text(left, y1 + 42, "An ordinary ruler", fontsize=13, fontweight="bold")
    ax.plot([left, right], [y1, y1], color=INK, linewidth=2)
    for v, name in zip(values, names):
        x = left + (right - left) * v / values[-1]
        ax.add_patch(Circle((x, y1), 7, facecolor=RED, edgecolor="white", linewidth=1.5, zorder=3))
    ax.text(right, y1 - 30, "1 billion", ha="center", fontsize=10.5)
    ax.text(left - 30, y1 - 30, "10,000 to 10 million: four values crammed into this corner", fontsize=10.5,
            color=SOFT)
    ax.text(left + (right - left) * 0.1, y1 + 14, "100 million", ha="center", fontsize=10.5)

    # log10 scale: each step is "ten times more"
    y2 = 150
    ax.text(left, y2 + 42, "A log scale: every step to the right is ten times more", fontsize=13, fontweight="bold")
    ax.plot([left, right], [y2, y2], color=INK, linewidth=2)
    for k, (v, name) in enumerate(zip(values, names)):
        x = left + (right - left) * k / (len(values) - 1)
        ax.add_patch(Circle((x, y2), 7, facecolor=RED, edgecolor="white", linewidth=1.5, zorder=3))
        ax.text(x, y2 - 30, name, ha="center", fontsize=10.5)
        ax.text(x, y2 - 50, f"log10 = {k + 4}", ha="center", fontsize=9.5, color=SOFT)
    ax.text(40, 40, "On the log scale a value of 6 means a million and 7 means ten million: "
            "a difference of 1 is a factor of ten.", fontsize=11, va="center")
    save(fig, "log_scale.png")


# ---------------------------------------------------------------------------
# 7. The interactive version of figure 1
# ---------------------------------------------------------------------------

COMBINATIONS_PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>How many communities?</title>
<style>
  :root { --ink:#1F2933; --soft:#5F6B7A; --line:#D5DCE6; --bg:#FBFCFE; --card:#FFFFFF; --accent:#4CAF7D; --gold:#C9A227; }
  @media (prefers-color-scheme: dark) {
    :root { --ink:#E8ECF1; --soft:#A9B4C2; --line:#3A4350; --bg:#16191D; --card:#1E2228; }
  }
  * { box-sizing: border-box; }
  body { margin:0; font-family:"Segoe UI", Helvetica, Arial, sans-serif; color:var(--ink); background:var(--bg); }
  main { max-width:880px; margin:0 auto; padding:24px 16px 40px; }
  h1 { font-size:24px; margin:0 0 6px; }
  p { line-height:1.55; }
  .soft { color:var(--soft); }
  .controls { display:grid; gap:16px; background:var(--card); border:1px solid var(--line); border-radius:16px; padding:18px 20px; margin:18px 0; }
  label { display:flex; justify-content:space-between; font-weight:600; gap:12px; }
  label output { font-variant-numeric:tabular-nums; }
  input[type=range] { width:100%; accent-color:var(--accent); }
  .tiles { display:grid; grid-template-columns:repeat(auto-fit, minmax(220px, 1fr)); gap:12px; }
  .tile { background:var(--card); border:1px solid var(--line); border-radius:16px; padding:14px 16px; }
  .tile .big { font-size:28px; font-weight:700; font-variant-numeric:tabular-nums; overflow-wrap:anywhere; }
  .tile .what { color:var(--soft); font-size:14px; }
  .presets { display:flex; flex-wrap:wrap; gap:8px; }
  .presets button { border:1px solid var(--line); background:var(--card); color:var(--ink); border-radius:999px; padding:6px 14px; cursor:pointer; font:inherit; }
  .presets button:focus-visible, input:focus-visible { outline:3px solid #5B8DEF; outline-offset:2px; }
  code { background:rgba(127,127,127,.15); padding:1px 5px; border-radius:5px; }
</style></head>
<body><main>
  <h1>How many communities could you build?</h1>
  <p class="soft">Pick how many strains you have, how many go into each community, and how many communities
  a laboratory can test in a year. The page does the arithmetic: <code>n choose k</code>, the number of
  different ways to pick k strains out of n when the order doesn't matter.</p>

  <div class="presets" role="group" aria-label="Examples">
    <button data-n="35" data-k="5" data-r="100">The published screen (35 strains, teams of 5)</button>
    <button data-n="224" data-k="5" data-r="100">The whole leaf collection (224 strains)</button>
    <button data-n="35" data-k="3" data-r="100">Teams of 3 instead</button>
  </div>

  <section class="controls" aria-label="Settings">
    <div><label for="n">Strains in the pool <output id="nOut"></output></label>
      <input id="n" type="range" min="5" max="400" value="35"></div>
    <div><label for="k">Strains in each community <output id="kOut"></output></label>
      <input id="k" type="range" min="1" max="10" value="5"></div>
    <div><label for="r">Communities tested per year <output id="rOut"></output></label>
      <input id="r" type="range" min="0" max="30" value="10" aria-describedby="rHelp">
      <div id="rHelp" class="soft" style="font-size:13px">An assumption you choose: the slider moves in growing steps from
      10 to 10,000 a year. For scale, each round of the published screen fitted 80 sealed boxes into one growth
      chamber, and the plants grew for about five and a half weeks.</div></div>
  </section>

  <div class="tiles" aria-live="polite">
    <div class="tile"><div class="big" id="combos"></div><div class="what">different communities</div></div>
    <div class="tile"><div class="big" id="years"></div><div class="what">years to test every one</div></div>
    <div class="tile"><div class="big" id="share"></div><div class="what">of them tested in a year</div></div>
  </div>

  <p id="sentence"></p>
  <p class="soft">This is why the study tested a random sample of 136 communities and let a model work out which
  strains matter, instead of testing everything. Part of the RealSignal project; the same numbers appear in
  <code>figures/combinations.png</code>.</p>
</main>
<script>
function choose(n, k) {            // exact, with whole numbers of any size
  if (k > n) return 0n;
  k = Math.min(k, n - k);
  let result = 1n;
  for (let i = 1; i <= k; i++) result = result * BigInt(n - k + i) / BigInt(i);
  return result;
}
const rate = v => Math.round(10 * Math.pow(10, v / 10));          // 0..30 -> 10..10,000; 10 -> 100
const fmt = x => x.toLocaleString("en-US");
const n = document.getElementById("n"), k = document.getElementById("k"), r = document.getElementById("r");
function update() {
  const N = +n.value, K = +k.value, R = rate(+r.value);
  document.getElementById("nOut").textContent = N;
  document.getElementById("kOut").textContent = K;
  document.getElementById("rOut").textContent = fmt(R);
  const c = choose(N, K);
  const years = Number(c) / R;
  document.getElementById("combos").textContent = fmt(c);
  document.getElementById("years").textContent = years < 1 ? "under 1" : years > 1e12 ? years.toExponential(1) : fmt(Math.round(years));
  const share = R / Number(c) * 100;
  document.getElementById("share").textContent = share >= 100 ? "all" : share >= 0.01 ? share.toFixed(2) + " %" : "under 0.01 %";
  document.getElementById("sentence").textContent =
    `With ${N} strains and ${K} in each community there are ${fmt(c)} possible communities. ` +
    `Testing ${fmt(R)} a year, you would need ${years < 1 ? "less than a year" : "about " + fmt(Math.round(years)) + " years"} to try them all.`;
}
[n, k, r].forEach(el => el.addEventListener("input", update));
document.querySelectorAll(".presets button").forEach(b => b.addEventListener("click", () => {
  n.value = b.dataset.n; k.value = b.dataset.k;
  r.value = Math.round(10 * Math.log10(b.dataset.r / 10));
  update();
}));
update();
</script>
</body></html>
"""


def combinations_page():
    folder = OUT.parent / "docs" / "interactive"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "combinations.html").write_text(COMBINATIONS_PAGE, encoding="utf-8")
    print("  wrote docs/interactive/combinations.html")


if __name__ == "__main__":
    combinations_figure()
    screening_figure()
    three_way_figure()
    data_layers_figure()
    fetch_pipeline_figure()
    log_scale_figure()
    combinations_page()
