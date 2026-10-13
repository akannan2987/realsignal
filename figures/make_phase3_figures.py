"""
figures/make_phase3_figures.py: the pictures for Phase 3.

    figures/lineage.png         every table dbt builds and the tables it's built
                                from, read from dbt/target/manifest.json
    figures/data_model.png      the marts and how they point at each other, from
                                the relationships tests in the same file
    figures/plant_choices.png   from 960 plants to the ones later phases use,
                                counted in the warehouse

Run from the project folder, with the virtual environment active, after
scripts/load_raw.py and dbt build (run inside dbt/):

    python figures/make_phase3_figures.py

A picture whose input isn't there yet is skipped, with a note. Nothing here
types in a count: change a model or a choice, rebuild, and run this again.
Explained in docs/04-phase-3-harmonisation.md, section 11.
"""

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")                              # draw to files, never open a window
import duckdb                                       # noqa: E402
import matplotlib.pyplot as plt                     # noqa: E402
from matplotlib.patches import FancyBboxPatch, Rectangle  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "figures"
MANIFEST = ROOT / "dbt" / "target" / "manifest.json"
WAREHOUSE = ROOT / "data" / "warehouse" / "realsignal.duckdb"

# The project's colours. Each layer of the warehouse keeps one colour in every
# picture; the order (blue, gold, green, purple) passes a colour-blindness check
# for neighbouring colours. Raw tables are grey on purpose: nothing has been
# done to them. Every label is written in dark ink, never in the layer colour.
BLUE, GREEN, GOLD, PURPLE, GREY = "#5B8DEF", "#4CAF7D", "#C9A227", "#9C6ADE", "#8A94A6"
INK, SOFT, LINE, SURFACE = "#1F2933", "#5F6B7A", "#D5DCE6", "#FBFCFE"
PALE = {BLUE: "#EAF1FD", GREEN: "#E6F4EA", GOLD: "#FFF3CD", PURPLE: "#F2EAFB", GREY: "#F1F3F6"}
LAYERS = [("raw", GREY, "raw tables (scripts/load_raw.py)"),
          ("staging", BLUE, "staging: one per raw table"),
          ("intermediate", GOLD, "intermediate: sources meet"),
          ("marts", GREEN, "marts: what later phases read")]

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11, "text.color": INK,
                     "figure.facecolor": SURFACE, "savefig.facecolor": SURFACE,
                     "hatch.color": GOLD, "hatch.linewidth": 1.5})


def canvas(width, height):
    fig = plt.figure(figsize=(width / 100, height / 100), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, width)
    ax.set_ylim(0, height)
    ax.axis("off")
    return fig, ax


def card(ax, x, y, w, h, colour, radius=8, fill=None):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={radius}",
                                facecolor=fill or PALE[colour], edgecolor=colour, linewidth=1.6))


def save(fig, name):
    path = OUT / name
    fig.savefig(path, dpi=100)
    plt.close(fig)
    print(f"  drew {path.relative_to(ROOT).as_posix()}")


def read_manifest():
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# 1. The lineage graph
# ---------------------------------------------------------------------------

def lineage_nodes(manifest):
    """Every source, model and seed, with its layer and the nodes it reads."""
    nodes = {}
    for uid, source in manifest["sources"].items():
        nodes[uid] = {"name": source["name"], "layer": "raw", "parents": [],
                      "path": "~" + source["name"]}
    for uid, node in manifest["nodes"].items():
        if node["resource_type"] == "model":
            layer = node["fqn"][1]                       # staging, intermediate or marts
            nodes[uid] = {"name": node["name"], "layer": layer,
                          "parents": node["depends_on"]["nodes"], "path": node["original_file_path"]}
        elif node["resource_type"] == "seed":
            nodes[uid] = {"name": node["name"], "layer": "marts", "parents": [],
                          "path": "~~" + node["name"], "seed": True}
    return nodes


def lineage_order(nodes):
    """Columns from left to right, each ordered so that lines cross as little as
    they can: staging by folder, raw in the order staging reads it, and each
    later model at the average height of the models it reads."""
    by_layer = {layer: [] for layer, *_ in LAYERS}
    staging = sorted((u for u, n in nodes.items() if n["layer"] == "staging"), key=lambda u: nodes[u]["path"])
    by_layer["staging"] = staging
    for uid in staging:
        for parent in nodes[uid]["parents"]:
            if nodes[parent]["layer"] == "raw" and parent not in by_layer["raw"]:
                by_layer["raw"].append(parent)
    by_layer["raw"] += sorted(u for u, n in nodes.items() if n["layer"] == "raw" and u not in by_layer["raw"])
    position = {u: i for layer in ("raw", "staging") for i, u in enumerate(by_layer[layer])}
    for layer in ("intermediate", "marts"):
        pending = [u for u, n in nodes.items() if n["layer"] == layer]
        placed = []
        while pending:                                    # a mart may read another mart
            ready = [u for u in pending if all(p in position or nodes[p]["layer"] != layer
                                               for p in nodes[u]["parents"])]
            for uid in ready or pending:
                known = [position[p] for p in nodes[uid]["parents"] if p in position]
                key = sum(known) / len(known) if known else 1e9
                placed.append((key, nodes[uid].get("seed", False), nodes[uid]["name"], uid))
                pending.remove(uid)
                position[uid] = key
        placed.sort()
        by_layer[layer] = [uid for *_, uid in placed]
        for i, uid in enumerate(by_layer[layer]):
            position[uid] = i * len(by_layer["staging"]) / max(len(placed), 1)
    return by_layer


def lineage_figure(manifest):
    nodes = lineage_nodes(manifest)
    columns = lineage_order(nodes)
    rows = max(len(c) for c in columns.values())
    box_w, box_h, gap, col_gap = 310, 24, 7, 92
    left, top = 40, 150
    height = top + rows * (box_h + gap) + 70
    width = left * 2 + len(LAYERS) * box_w + (len(LAYERS) - 1) * col_gap + 40   # room for loops on the right
    fig, ax = canvas(width, height)
    ax.text(left, height - 40, "From raw tables to marts: the lineage dbt keeps", fontsize=21, weight="bold")
    ax.text(left, height - 72, "Each line is a source() or ref() in a model: the box on the right is built "
            "from the box on the left. Drawn from dbt/target/manifest.json.", fontsize=12.5, color=SOFT)

    where = {}
    for col, (layer, colour, title) in enumerate(LAYERS):
        x = left + col * (box_w + col_gap)
        ids = columns[layer]
        span = rows * (box_h + gap)
        offset = (span - len(ids) * (box_h + gap)) / 2      # short columns sit in the middle
        ax.text(x, height - top + 34, title, fontsize=13, weight="bold")
        ax.add_patch(Rectangle((x, height - top + 22), 40, 4, color=colour))
        seeds = sum(1 for uid in ids if nodes[uid].get("seed"))
        count = len(ids) - seeds
        ax.text(x + 48, height - top + 18, f"{count} {'table' if count == 1 else 'tables'}"
                + (f" and {seeds} seed" if seeds else ""), fontsize=10.5, color=SOFT, va="center")
        for i, uid in enumerate(ids):
            y = height - top - offset - (i + 1) * (box_h + gap) + gap
            seed = nodes[uid].get("seed", False)
            card(ax, x, y, box_w, box_h, PURPLE if seed else colour, radius=6)
            label = nodes[uid]["name"] + (" (seed)" if seed else "")
            ax.text(x + 10, y + box_h / 2, label, fontsize=10.5, va="center", family="DejaVu Sans Mono")
            where[uid] = (x, y + box_h / 2)

    for uid, node in nodes.items():
        for parent in node["parents"]:
            if parent in where and uid in where:
                (x0, y0), (x1, y1) = where[parent], where[uid]
                if x0 == x1:
                    # Two tables in the same column (a mart that reads a mart):
                    # a loop on the right-hand side, from one box to the other.
                    bend = x0 + box_w + 14 + 6 * (abs(y1 - y0) // (box_h + gap) % 3)
                    xs, ys = [x0 + box_w, bend, bend, x1 + box_w], [y0, y0, y1, y1]
                else:
                    xs = [x0 + box_w, x0 + box_w + col_gap * 0.45, x1 - col_gap * 0.45, x1]
                    ys = [y0, y0, y1, y1]
                ax.plot(xs, ys, color=GREY, linewidth=0.9, alpha=0.55, zorder=0)
    ax.text(left, 24, "Grey: as loaded. Blue, gold, green: the three layers dbt builds. Purple: a table "
            "written by hand (a seed) that the tests compare the data with.", fontsize=11, color=SOFT)
    save(fig, "lineage.png")


# ---------------------------------------------------------------------------
# 2. The data model of the marts
# ---------------------------------------------------------------------------

KIND = {"dim": (BLUE, "dimension: one row per thing"),
        "community": (GOLD, "bridge: links two dimensions"),
        "fct": (GREEN, "fact: one row per event or measurement"),
        "model": (PURPLE, "ready for modelling")}
# Where each mart sits on the picture (left, top), in pixels.
PLACES = {"fct_strain_interaction": (40, 760), "dim_strain": (40, 520), "fct_gene_cluster": (40, 240),
          "community_member": (520, 640), "fct_plant_measurement": (520, 330),
          "dim_community": (1000, 760), "fct_plant": (1000, 470), "model_plants": (1000, 220)}


def mart_tables(manifest):
    """Each mart's columns, its key and the columns that point at another mart."""
    marts = {n["name"]: n for n in manifest["nodes"].values()
             if n["resource_type"] == "model" and n["fqn"][1] == "marts"}
    keys, links = {}, []
    for node in manifest["nodes"].values():
        if node["resource_type"] != "test" or not node.get("test_metadata"):
            continue
        model = next((marts[d.split(".")[-1]]["name"] for d in node["depends_on"]["nodes"]
                      if d.split(".")[-1] in marts), None)
        test, column = node["test_metadata"]["name"], node.get("column_name")
        if model is None or column is None:
            continue
        if test == "unique" and model == node["attached_node"].split(".")[-1]:
            keys.setdefault(model, column)
        if test == "relationships":
            target = node["test_metadata"]["kwargs"]["to"].split("'")[1]
            child = node["attached_node"].split(".")[-1]
            if child in marts and target in marts:
                links.append((child, column, target))
    return marts, keys, sorted(set(links))


def data_model_figure(manifest):
    marts, keys, links = mart_tables(manifest)
    width, height = 1460, 900
    fig, ax = canvas(width, height)
    ax.text(40, height - 40, "The marts, and how they point at each other", fontsize=21, weight="bold")
    ax.text(40, height - 72, "An arrow is a relationships test: every value in the column at its tail must "
            "exist in the table it points to.", fontsize=12.5, color=SOFT)
    box_w, line_h = 380, 21
    boxes = {}
    for name, (x, top) in PLACES.items():
        if name not in marts:
            continue
        colour = next(c for prefix, (c, _) in KIND.items() if name.startswith(prefix))
        columns = list(marts[name]["columns"])
        shown = [c for c in columns if c == keys.get(name) or any(l[0] == name and l[1] == c for l in links)]
        rest = len(columns) - len(shown)
        lines = [(c, "key" if c == keys.get(name) else "points to") for c in shown]
        h = 42 + line_h * (len(lines) + (1 if rest else 0)) + 8
        card(ax, x, top - h, box_w, h, colour, radius=10)
        ax.text(x + 14, top - 24, name, fontsize=13.5, weight="bold", family="DejaVu Sans Mono")
        for i, (column, role) in enumerate(lines):
            y = top - 50 - i * line_h
            ax.text(x + 18, y, column, fontsize=11, family="DejaVu Sans Mono")
            ax.text(x + box_w - 14, y, role, fontsize=10, color=SOFT, ha="right")
        if rest:
            ax.text(x + 18, top - 50 - len(lines) * line_h, f"and {rest} more columns", fontsize=10.5, color=SOFT)
        boxes[name] = (x, top - h, box_w, h)

    def anchor(box, towards):
        x, y, w, h = box
        cx, cy = x + w / 2, y + h / 2
        tx, ty = towards
        if abs(tx - cx) > w / 2 + 20:                     # leave from the side facing the target
            return (x + w if tx > cx else x, cy)
        return (cx, y + h if ty > cy else y)

    def crosses(start, end, skip):
        """True if the straight line from start to end passes through another box."""
        for name, (x, y, w, h) in boxes.items():
            if name in skip:
                continue
            for t in (i / 50 for i in range(51)):
                px, py = start[0] + t * (end[0] - start[0]), start[1] + t * (end[1] - start[1])
                if x < px < x + w and y < py < y + h:
                    return True
        return False

    for child, target in sorted(set((c, t) for c, _, t in links)):
        cbox, tbox = boxes[child], boxes[target]
        start = anchor(cbox, (tbox[0] + tbox[2] / 2, tbox[1] + tbox[3] / 2))
        end = anchor(tbox, start)
        if crosses(start, end, {child, target}):
            # Go round on the right: out of the child's right side, up, into the target's.
            right = max(cbox[0] + cbox[2], tbox[0] + tbox[2]) + 32
            start = (cbox[0] + cbox[2], cbox[1] + cbox[3] / 2)
            end = (tbox[0] + tbox[2], tbox[1] + tbox[3] / 2)
            ax.plot([start[0], right, right], [start[1], start[1], end[1]], color=SOFT, linewidth=1.3)
            ax.annotate("", xy=end, xytext=(right, end[1]),
                        arrowprops=dict(arrowstyle="-|>", color=SOFT, linewidth=1.3, shrinkA=0, shrinkB=2))
            continue
        ax.annotate("", xy=end, xytext=start,
                    arrowprops=dict(arrowstyle="-|>", color=SOFT, linewidth=1.3, shrinkA=2, shrinkB=2,
                                    connectionstyle="arc3,rad=0.06"))
    for i, (prefix, (colour, text)) in enumerate(KIND.items()):
        x = 40 + i * 350
        card(ax, x, 26, 22, 16, colour, radius=4)
        ax.text(x + 30, 34, text, fontsize=11, va="center")
    save(fig, "data_model.png")


# ---------------------------------------------------------------------------
# 3. From 960 plants to the ones later phases use
# ---------------------------------------------------------------------------

def plant_choices_figure(con):
    total, control, reference, false_n, tbd_out, used, tbd_used, rounds_test = con.execute("""
        select count(*),
               count(*) filter (where split = 'control'),
               count(*) filter (where split = 'between-round reference'),
               count(*) filter (where split in ('training', 'test') and not use_for_modelling
                                and inclusion_mark = 'FALSE'),
               count(*) filter (where split in ('training', 'test') and not use_for_modelling
                                and inclusion_mark = 'TBD'),
               count(*) filter (where use_for_modelling),
               count(*) filter (where use_for_modelling and inclusion_mark = 'TBD'),
               string_agg(distinct round_id, ', ') filter (where split = 'test')
        from marts.fct_plant""").fetchone()
    empty = con.execute("""select community_id from marts.dim_community
                           where kind = 'community' and not has_plants_for_modelling
                           order by community_id""").fetchall()
    steps = [("Every plant in the plant file", total, "start"),
             ("Control plants: no strains, or the whole library", -control, "out"),
             (f"Grown before {rounds_test} in a test community (Choice 2)", -reference, "out"),
             ("Marked FALSE by the authors", -false_n, "out")]
    if tbd_out:
        steps.append(("Marked TBD, left out (Choice 1)", -tbd_out, "out"))
    steps.append(("Used for modelling: marts.model_plants", used, "end"))

    width, height = 1400, 150 + 62 * len(steps) + 90
    fig, ax = canvas(width, height)
    ax.text(40, height - 40, "Which plants the models will see", fontsize=21, weight="bold")
    ax.text(40, height - 72, "Each bar is a count in marts.fct_plant; each plant leaves at the first "
            "reason that applies.", fontsize=12.5, color=SOFT)
    x0, scale, bar_h = 560, 720 / total, 34
    remaining = total
    for i, (label, n, kind) in enumerate(steps):
        y = height - 140 - i * 62
        ax.text(x0 - 16, y + bar_h / 2, label, fontsize=12.5, ha="right", va="center")
        if kind == "start":
            ax.add_patch(Rectangle((x0, y), total * scale, bar_h, color=BLUE))
            ax.text(x0 + total * scale + 10, y + bar_h / 2, f"{total}", fontsize=13, va="center", weight="bold")
        elif kind == "out":
            remaining += n
            ax.add_patch(Rectangle((x0 + remaining * scale, y), -n * scale, bar_h,
                                   facecolor=PALE[GREY], edgecolor=GREY, linewidth=1.2))
            ax.text(x0 + (remaining - n) * scale + 10, y + bar_h / 2, f"minus {-n}", fontsize=12.5, va="center")
        else:
            kept = n - tbd_used
            ax.add_patch(Rectangle((x0, y), kept * scale, bar_h, color=GREEN))
            if tbd_used:
                ax.add_patch(Rectangle((x0 + kept * scale + 2, y), tbd_used * scale - 2, bar_h,
                                       facecolor=PALE[GOLD], edgecolor=GOLD, hatch="///", linewidth=1.2))
            ax.text(x0 + n * scale + 10, y + bar_h / 2, f"{n}", fontsize=13, va="center", weight="bold")
            note = (f"of which {tbd_used} marked TBD and kept (Choice 1, the hatched part)" if tbd_used
                    else "no TBD plants: keep_undecided_plants is false")
            ax.text(x0, y - 18, note, fontsize=11.5, color=SOFT, va="center")
    choice3 = (f"Choice 3: {len(empty)} communities have no plant left "
               f"({', '.join(c for (c,) in empty[:4])}{', ...' if len(empty) > 4 else ''}). "
               "They keep their row in marts.dim_community, with plants_for_modelling = 0.")
    ax.text(40, 30, choice3, fontsize=11.5, color=SOFT)
    save(fig, "plant_choices.png")


def main() -> int:
    if MANIFEST.exists():
        manifest = read_manifest()
        lineage_figure(manifest)
        data_model_figure(manifest)
    else:
        print("  skipped lineage.png and data_model.png: no dbt/target/manifest.json yet")
        print("  (from inside dbt/, run dbt build first)")
    if WAREHOUSE.exists():
        try:
            con = duckdb.connect(str(WAREHOUSE), read_only=True)
        except duckdb.IOException:
            print("  skipped plant_choices.png: the warehouse is open in another program")
            return 1
        with con:
            if con.execute("select count(*) from information_schema.tables "
                           "where table_schema = 'marts' and table_name = 'fct_plant'").fetchone()[0]:
                plant_choices_figure(con)
            else:
                print("  skipped plant_choices.png: the marts aren't built yet (dbt build)")
    else:
        print("  skipped plant_choices.png: no warehouse yet (python scripts/load_raw.py, then dbt build)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
