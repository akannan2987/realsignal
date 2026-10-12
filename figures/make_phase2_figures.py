"""
figures/make_phase2_figures.py: the pictures for Phase 2.

    figures/three_checks.png          three ways to trust a download (no data needed)
    figures/source_register.png       the five layers, their terms and their status,
                                      read from sources/register.csv
    figures/layer1_rounds.png         the three rounds of the screen, box by box,
                                      read from the Layer 1 files (needs the Phase 1 download)
    docs/interactive/communities.html every community and its strains, to click through
                                      (needs the Phase 1 download)

Run from the project folder, with the virtual environment active:

    python figures/make_phase2_figures.py

Pictures that need data are skipped, with a note, when the data isn't there.
Explained in docs/03-phase-2-more-sources.md.
"""

import csv
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")                              # draw to files, never open a window
import matplotlib.pyplot as plt                     # noqa: E402
import pandas as pd                                 # noqa: E402
from matplotlib.patches import Circle, FancyBboxPatch  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "figures"
INTERACTIVE = ROOT / "docs" / "interactive"
DATA = ROOT / "data" / "raw" / "extracted" / "Data"
DESIGN = DATA / "MetaData" / "Mini5SynComScreen" / "20200828_Mixes.txt"
BOXES = DATA / "MetaData" / "Mini5SynComScreen" / "20200828_Box.txt"
PLANTS = DATA / "CleanData" / "2023-01-16Mini5SynComScreen_CommentsFile.txt"

# The project's colours (the same family as the logo and the Phase 1 pictures).
# Colour marks identity only; every label is written in dark ink.
BLUE, GREEN, GOLD, PURPLE, RED, GREY = "#5B8DEF", "#4CAF7D", "#C9A227", "#9C6ADE", "#D9634C", "#8A94A6"
INK, SOFT, LINE, SURFACE = "#1F2933", "#5F6B7A", "#D5DCE6", "#FBFCFE"
PALE = {BLUE: "#EAF1FD", GREEN: "#E6F4EA", GOLD: "#FFF3CD", PURPLE: "#F2EAFB", RED: "#FBEAE6", GREY: "#F1F3F6"}

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11, "text.color": INK,
                     "figure.facecolor": SURFACE, "savefig.facecolor": SURFACE})


def canvas(width, height):
    fig = plt.figure(figsize=(width / 100, height / 100), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, width)
    ax.set_ylim(0, height)
    ax.axis("off")
    return fig, ax


def card(ax, x, y, w, h, colour, radius=14, fill=None, dashed=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={radius}",
                                facecolor=fill or PALE[colour], edgecolor=colour, linewidth=2,
                                linestyle="--" if dashed else "-"))


def save(fig, name):
    path = OUT / name
    fig.savefig(path, dpi=100)
    plt.close(fig)
    print(f"  drew {path.relative_to(ROOT).as_posix()}")


# ---------------------------------------------------------------------------
# 1. Three ways to trust a download
# ---------------------------------------------------------------------------

def lock(ax, x, y, colour):
    """A padlock: a published checksum, set by whoever published the file."""
    ax.add_patch(FancyBboxPatch((x - 26, y - 30), 52, 40, boxstyle="round,pad=0,rounding_size=6",
                                facecolor=colour, edgecolor=INK, linewidth=1.5))
    ax.add_patch(matplotlib.patches.Arc((x, y + 10), 34, 44, theta1=0, theta2=180, color=INK, linewidth=4))
    ax.add_patch(Circle((x, y - 12), 5, facecolor=INK))


def pin(ax, x, y, colour):
    """A drawing pin: a checksum we record ourselves the first time."""
    ax.add_patch(Circle((x, y + 14), 18, facecolor=colour, edgecolor=INK, linewidth=1.5))
    ax.plot([x, x], [y - 4, y - 34], color=INK, linewidth=3, solid_capstyle="round")


def two_pages(ax, x, y, colour):
    """Two identical pages: the same file found in two places."""
    for dx, dy in ((-14, 8), (10, -8)):
        ax.add_patch(FancyBboxPatch((x + dx - 18, y + dy - 26), 36, 48, boxstyle="round,pad=0,rounding_size=4",
                                    facecolor="white", edgecolor=INK, linewidth=1.5))
        for k in range(3):
            ax.plot([x + dx - 10, x + dx + 10], [y + dy + 8 - k * 10] * 2, color=colour, linewidth=2.5)


def three_checks_figure():
    fig, ax = canvas(1200, 470)
    ax.text(40, 440, "Three ways to trust a download", fontsize=19, fontweight="bold", va="top")
    ax.text(40, 408, "A checksum is a file's fingerprint. Phase 2 uses whichever kind of reference "
            "each source allows.", fontsize=12, color=SOFT, va="top")
    columns = [
        (BLUE, lock, "1. A published checksum",
         "The publisher lists the fingerprint\nnext to the file. A match proves you\nhold exactly what they published.",
         "Zenodo (Layer 1),\nNCBI (Layer 2)"),
        (GOLD, pin, "2. Pinned on first use",
         "No fingerprint is published, so the\nfirst download's is recorded in\nsources/files.csv and committed.",
         "the journal supplements\n(Layers 3, 4 and 5)"),
        (PURPLE, two_pages, "3. A second copy",
         "The same file exists somewhere else.\nSame fingerprint: same file. If not,\nworkbooks are compared cell by cell.",
         "Layer 5: a copy is also\nin the Phase 1 archive"),
    ]
    w, h, gap = 360, 300, 30
    for i, (colour, icon, title, body, used) in enumerate(columns):
        x = 40 + i * (w + gap)
        card(ax, x, 50, w, h, colour)
        icon(ax, x + w / 2, 300, colour)
        ax.text(x + w / 2, 238, title, ha="center", fontsize=14, fontweight="bold")
        ax.text(x + w / 2, 212, body, ha="center", va="top", fontsize=11, color=INK, linespacing=1.45)
        ax.text(x + w / 2, 70, "used for: " + used, ha="center", fontsize=10.5, color=SOFT, linespacing=1.4)
    ax.text(40, 22, "None of them says whether the data inside is right; that is what the later phases look at.",
            fontsize=10.5, color=SOFT)
    save(fig, "three_checks.png")


# ---------------------------------------------------------------------------
# 2. The source register as a picture
# ---------------------------------------------------------------------------

LAYER_COLOURS = {"1": BLUE, "2": GREEN, "3": PURPLE, "4": GOLD, "5": RED}


def terms_kind(terms: str) -> str:
    if "CC-BY" in terms:
        return "open licence (CC-BY 4.0)"
    if "NCBI" in terms:
        return "public database"
    return "publisher's terms"


def checked_by(row: dict, files: list[dict]) -> str:
    mine = [f for f in files if f["source_id"] == row["source_id"]]
    if not mine:
        return "published MD5"
    if all(f["kind"] == "ncbi_assembly" for f in mine):
        return f"published MD5 ({len(mine)} files)"
    text = "pinned SHA-256"
    if any(f["same_as"] for f in mine):
        text += "\n+ a second copy"
    return text


def source_register_figure():
    with open(ROOT / "sources" / "register.csv", newline="", encoding="utf-8") as handle:
        register = list(csv.DictReader(handle))
    with open(ROOT / "sources" / "files.csv", newline="", encoding="utf-8") as handle:
        files = list(csv.DictReader(handle))
    fig, ax = canvas(1200, 140 + 92 * len(register))
    top = 140 + 92 * len(register)
    ax.text(40, top - 28, "The source register: where every layer comes from", fontsize=19,
            fontweight="bold", va="top")
    ax.text(40, top - 60, "Drawn from sources/register.csv, the table that records each source's "
            "terms and status, gaps included.", fontsize=12, color=SOFT, va="top")
    heads = [(48, "layer"), (350, "source"), (575, "terms"), (790, "checked by"), (1010, "status")]
    for x, label in heads:
        ax.text(x, top - 100, label, fontsize=10.5, color=SOFT, fontweight="bold")
    for i, row in enumerate(register):
        y = top - 190 - i * 92
        colour = LAYER_COLOURS[row["layer"].split(",")[0].strip()]
        card(ax, 30, y, 1140, 76, colour, radius=10)
        ax.text(48, y + 50, f"Layer {row['layer']}", fontsize=12, fontweight="bold")
        ax.text(48, y + 24, row["layer_name"], fontsize=10.5)
        journal = row["citation"].split(",", 1)[1].strip().rsplit(" ", 1)[0]
        ax.text(350, y + 50, row["citation"].split(",")[0], fontsize=11.5, fontweight="bold")
        ax.text(350, y + 24, journal, fontsize=10.5, color=SOFT)
        ax.text(575, y + 38, terms_kind(row["terms"]), fontsize=10.5, va="center")
        ax.text(790, y + 38, checked_by(row, files), fontsize=10.5, va="center", linespacing=1.3)
        mark = "\u2713" if row["status"] == "fetched" else "\u25cb"     # a tick, or an empty circle
        ax.text(1010, y + 38, f"{mark} {row['status']}", fontsize=11.5, fontweight="bold", va="center")
    save(fig, "source_register.png")


# ---------------------------------------------------------------------------
# 3. The three rounds, box by box (needs the Phase 1 download)
# ---------------------------------------------------------------------------

def load_layer1():
    design = pd.read_csv(DESIGN, sep="\t").set_index("Mix")
    boxes = pd.read_csv(BOXES, sep="\t")
    plants = pd.read_csv(PLANTS, sep="\t")
    size = design.sum(axis=1)
    infected = plants[(plants["Infection"] == "Pst") & (plants["Mix"].map(size) == 5)]
    rounds_of = infected.groupby("Mix")["Experiment"].apply(set)
    return design, boxes, plants, size, rounds_of


def role(mix, infection, size, rounds_of):
    if mix == "axenic":
        return "no strains"
    if size.get(mix) != 5:
        return "all 35"
    seen = rounds_of.get(mix, set())
    if len(seen) > 1:
        return "every round"
    return "training" if seen <= {"Exp1", "Exp2"} else "test"


ROLE_STYLE = {"training": BLUE, "test": GOLD, "every round": PURPLE, "all 35": GREEN, "no strains": GREY}


def layer1_rounds_figure():
    design, boxes, plants, size, rounds_of = load_layer1()
    status = plants.assign(s=plants["IncludedAnalysis"].astype(str).str.upper()).groupby("Box")["s"].apply(list)
    fig, ax = canvas(1200, 600)
    ax.text(40, 572, "Layer 1 in one picture: three rounds of 80 boxes", fontsize=19, fontweight="bold", va="top")
    ax.text(40, 540, "Each square is one sealed box of four plants, coloured by the community it held. "
            "Drawn from the published files.", fontsize=12, color=SOFT, va="top")
    cell, gap = 30, 5
    counts = {}
    for r, name in enumerate(("Exp1", "Exp2", "Exp3")):
        x0 = 40 + r * 385
        sub = boxes[boxes["Experiment"] == name].sort_values("Box")
        for k, (_, b) in enumerate(sub.iterrows()):
            rr, cc = divmod(k, 10)
            x, y = x0 + cc * (cell + gap), 470 - rr * (cell + gap) - cell
            what = role(b["Mix"], b["Infection"], size, rounds_of)
            counts[what] = counts.get(what, 0) + 1
            colour = ROLE_STYLE[what]
            ax.add_patch(FancyBboxPatch((x, y), cell, cell, boxstyle="round,pad=0,rounding_size=5",
                                        facecolor=colour, edgecolor="white", linewidth=1.5))
            states = status.get(b["Box"], [])
            if states and all(s == "FALSE" for s in states):
                ax.text(x + cell / 2, y + cell / 2, "✗", ha="center", va="center", fontsize=15,
                        color="white", fontweight="bold")
            elif "TBD" in states:
                ax.add_patch(Circle((x + cell / 2, y + cell / 2), 5, facecolor="white", edgecolor=INK, linewidth=1))
        infected = plants[(plants["Experiment"] == name) & (plants["Infection"] == "Pst")]
        marks = infected["IncludedAnalysis"].astype(str).str.upper().value_counts()
        label = {"Exp1": "Round 1 (training)", "Exp2": "Round 2 (training)", "Exp3": "Round 3 (test)"}[name]
        ax.text(x0, 488, label, fontsize=13, fontweight="bold")
        ax.text(x0, 168, f"{len(infected)} infected plants: TRUE {marks.get('TRUE', 0)}, "
                f"TBD {marks.get('TBD', 0)}, FALSE {marks.get('FALSE', 0)}", fontsize=10.5, color=SOFT)
    # Legend, with the number of boxes of each kind across all three rounds
    legend = [("training", "training community"), ("test", "test community"),
              ("every round", "in every round (Mix69, Mix70)"), ("all 35", "all 35 strains (Mix71)"),
              ("no strains", "no strains (controls)")]
    for i, (key, text) in enumerate(legend):
        x = 40 + (i % 3) * 385
        y = 120 - (i // 3) * 34
        ax.add_patch(FancyBboxPatch((x, y - 9), 20, 20, boxstyle="round,pad=0,rounding_size=4",
                                    facecolor=ROLE_STYLE[key], edgecolor="white"))
        ax.text(x + 30, y + 1, f"{text}: {counts.get(key, 0)} boxes", fontsize=11, va="center")
    ax.add_patch(FancyBboxPatch((40 + 2 * 385, 77), 20, 20, boxstyle="round,pad=0,rounding_size=4",
                                facecolor=BLUE, edgecolor="white"))
    ax.add_patch(Circle((40 + 2 * 385 + 10, 87), 5, facecolor="white", edgecolor=INK, linewidth=1))
    ax.text(40 + 2 * 385 + 30, 87, "box dropped, plants recovered (TBD)", fontsize=11, va="center")
    ax.add_patch(FancyBboxPatch((40 + 2 * 385, 43), 20, 20, boxstyle="round,pad=0,rounding_size=4",
                                facecolor=BLUE, edgecolor="white"))
    ax.text(40 + 2 * 385 + 10, 53, "✗", ha="center", va="center", fontsize=12, color="white", fontweight="bold")
    ax.text(40 + 2 * 385 + 30, 53, "every plant left out", fontsize=11, va="center")
    ax.text(40, 18, "Source: Emmenegger et al. 2023, Zenodo 10.5281/zenodo.10118600 (CC-BY 4.0). "
            "Files: 20200828_Box.txt, 20200828_Mixes.txt, the cleaned plant file.", fontsize=9.5, color=SOFT)
    save(fig, "layer1_rounds.png")


# ---------------------------------------------------------------------------
# 4. Every community, to click through (needs the Phase 1 download)
# ---------------------------------------------------------------------------

def communities_page():
    design, boxes, plants, size, rounds_of = load_layer1()
    strains = list(design.columns)
    infected = plants[plants["Infection"] == "Pst"]
    marks = infected["IncludedAnalysis"].astype(str).str.upper()
    kept = (marks == "TRUE").groupby(infected["Mix"]).sum()
    undecided = (marks == "TBD").groupby(infected["Mix"]).sum()
    grown = infected.groupby("Mix").size()
    communities = []
    for mix, row in design[design.sum(axis=1) == 5].iterrows():
        communities.append({
            "mix": mix,
            "role": role(mix, "Pst", size, rounds_of),
            "strains": [s for s in strains if row[s] == 1],
            "rounds": sorted(rounds_of.get(mix, [])),
            "kept": int(kept.get(mix, 0)),
            "tbd": int(undecided.get(mix, 0)),
            "grown": int(grown.get(mix, 0)),
        })
    communities.sort(key=lambda c: int(c["mix"][3:]))
    page = PAGE.replace("__DATA__", json.dumps({"strains": strains, "communities": communities}))
    INTERACTIVE.mkdir(parents=True, exist_ok=True)
    (INTERACTIVE / "communities.html").write_text(page, encoding="utf-8")
    print(f"  wrote docs/interactive/communities.html ({len(communities)} communities)")


PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Every community in the screen</title>
<style>
  :root { --ink:#1F2933; --soft:#5F6B7A; --line:#D5DCE6; --bg:#FBFCFE; --card:#FFFFFF;
          --train:#5B8DEF; --test:#C9A227; --every:#9C6ADE; --dim:#E3E8EF; --focus:#1F2933; }
  @media (prefers-color-scheme: dark) {
    :root { --ink:#E8ECF1; --soft:#A9B4C2; --line:#3A4350; --bg:#16191D; --card:#1E2228; --dim:#2A3038; --focus:#E8ECF1; }
  }
  * { box-sizing:border-box; }
  body { margin:0; font-family:"Segoe UI", Helvetica, Arial, sans-serif; color:var(--ink); background:var(--bg); line-height:1.5; }
  main { max-width:1000px; margin:0 auto; padding:24px 16px 40px; }
  h1 { font-size:22px; margin:0 0 6px; }
  p { margin:6px 0; }
  .soft { color:var(--soft); font-size:14px; }
  .chips { display:flex; flex-wrap:wrap; gap:6px; margin:12px 0; }
  .chip { border:1px solid var(--line); background:var(--card); color:var(--ink); border-radius:999px; padding:4px 10px; font-size:13px; cursor:pointer; }
  .chip[aria-pressed="true"] { background:var(--ink); color:var(--bg); border-color:var(--ink); }
  .panel { background:var(--card); border:1px solid var(--line); border-radius:14px; padding:12px 14px; margin:12px 0; }
  .panel h2 { font-size:15px; margin:0 0 8px; }
  .grid { display:flex; flex-wrap:wrap; gap:4px; }
  .sq { width:18px; height:18px; border-radius:4px; border:0; padding:0; cursor:pointer; }
  .sq.training { background:var(--train); } .sq.test { background:var(--test); } .sq.every { background:var(--every); }
  .sq.off { background:var(--dim); }
  .sq:focus-visible, .chip:focus-visible { outline:3px solid var(--focus); outline-offset:2px; }
  #detail { min-height:3.2em; }
  .key { display:inline-block; width:12px; height:12px; border-radius:3px; margin:0 4px 0 10px; vertical-align:-1px; }
</style></head>
<body><main>
<h1>Every community in the screen</h1>
<p>206 communities of five strains each, from a pool of 35. Pick one or more strains to see which communities
held them; pick a square to see what was in it. The colours show what the community was used for:
<span class="key" style="background:var(--train)"></span>training
<span class="key" style="background:var(--test)"></span>test
<span class="key" style="background:var(--every)"></span>grown in every round.</p>
<div class="chips" id="chips" role="group" aria-label="Strains"></div>
<p id="summary" class="soft" aria-live="polite"></p>
<div id="panels"></div>
<div class="panel"><h2>Selected community</h2><div id="detail" aria-live="polite" class="soft">Pick a square.</div></div>
<p class="soft">Data: Emmenegger et al. 2023, Zenodo 10.5281/zenodo.10118600 (CC-BY 4.0), files
20200828_Mixes.txt and the cleaned plant file. Built by figures/make_phase2_figures.py. Works offline.</p>
</main>
<script>
const DATA = __DATA__;
const picked = new Set();
const groups = [["training", "Training: rounds 1 and 2 only"], ["every", "Grown in every round"], ["test", "Test: round 3 only"]];
const roleClass = r => r === "every round" ? "every" : r;
const chips = document.getElementById("chips");
DATA.strains.forEach(s => {
  const b = document.createElement("button");
  b.className = "chip"; b.textContent = s; b.setAttribute("aria-pressed", "false");
  b.onclick = () => { picked.has(s) ? picked.delete(s) : picked.add(s); b.setAttribute("aria-pressed", picked.has(s)); draw(); };
  chips.appendChild(b);
});
function matches(c) { return [...picked].every(s => c.strains.includes(s)); }
function draw() {
  const panels = document.getElementById("panels"); panels.innerHTML = "";
  let counts = {};
  groups.forEach(([key, title]) => {
    const list = DATA.communities.filter(c => roleClass(c.role) === key);
    const hit = list.filter(matches);
    counts[key] = hit.length;
    const div = document.createElement("div"); div.className = "panel";
    div.innerHTML = `<h2>${title}: ${picked.size ? hit.length + " of " : ""}${list.length}</h2>`;
    const grid = document.createElement("div"); grid.className = "grid";
    list.forEach(c => {
      const b = document.createElement("button");
      b.className = "sq " + (matches(c) ? key : "off");
      b.setAttribute("aria-label", `${c.mix}: ${c.strains.join(", ")}`);
      b.title = c.mix;
      b.onclick = () => show(c);
      grid.appendChild(b);
    });
    div.appendChild(grid); panels.appendChild(div);
  });
  const sum = document.getElementById("summary");
  sum.textContent = picked.size
    ? `Communities holding ${[...picked].join(" and ")}: ${counts.training} training, ${counts.every} in every round, ${counts.test} test.`
    : "No strain picked: every community is shown.";
}
function show(c) {
  document.getElementById("detail").innerHTML =
    `<strong>${c.mix}</strong>: ${c.strains.join(", ")}<br>` +
    `Grown in ${c.rounds.join(", ") || "no round"}; ${c.grown} infected plants: ` +
    `${c.kept} marked TRUE, ${c.tbd} TBD, ${c.grown - c.kept - c.tbd} FALSE.`;
}
draw();
</script></body></html>
"""


def main() -> int:
    three_checks_figure()
    source_register_figure()
    if all(p.exists() for p in (DESIGN, BOXES, PLANTS)):
        layer1_rounds_figure()
        communities_page()
    else:
        print("  skipped figures/layer1_rounds.png and docs/interactive/communities.html:")
        print("  they need the Phase 1 download (python scripts/fetch_data.py)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
