"""
figures/make_illustrations.py: the project's logo and the Handbook's journey map.

Writes small, crisp SVG pictures (vector graphics stay sharp at any zoom, and
they're plain text, so Git can show what changed in them):

    docs/img/realsignal_logo.svg      the banner at the top of the README
    docs/img/realsignal_icon.svg      the square icon
    docs/img/realsignal_wordmark.svg  the icon and the name side by side
    docs/img/journey_map.svg          the road from day 0 to the product, with status

and one interactive page:

    docs/interactive/journey.html     the same journey, clickable: each stage's What,
                                      Why, Checkpoint and commit, read from docs/HANDBOOK.md

The journey map takes its stage list from STAGES below. When a stage is
finished, change its status here, run this script again, and the picture in
the Handbook updates. The same status lives in docs/HANDBOOK.md and
docs/ROADMAP.md, and all three change in the same commit (tests/test_docs.py
checks that the Handbook and this list agree). The interactive page reads
its text from the Handbook itself, so it can't drift from it.

Run from the project folder, with the virtual environment active:
    python figures/make_illustrations.py
"""
import html
import json
import re
from pathlib import Path
from xml.sax.saxutils import escape   # turns "&" into "&amp;" so the SVG stays valid

ROOT = Path(__file__).resolve().parents[1]
IMG = ROOT / "docs" / "img"
INTERACTIVE = ROOT / "docs" / "interactive"
HANDBOOK = ROOT / "docs" / "HANDBOOK.md"
GITHUB = "https://github.com/akannan2987/realsignal/blob/master"

BLUE, GREEN, GOLD, GREY, PURPLE, RED = "#5B8DEF", "#4CAF7D", "#C9A227", "#8A94A6", "#9C6ADE", "#D9634C"
INK, SOFT = "#1F2933", "#5F6B7A"
FONT = "Segoe UI, Helvetica, Arial, sans-serif"

# (stage, short label, which phase, status). Status is done, next or later.
STAGES = [
    ("0", "Understand", "why and what", "done"),
    ("1", "Set up", "once per machine", "done"),
    ("2", "Version control", "Git + safety gate", "done"),
    ("3", "Real data", "Phase 1", "done"),
    ("4", "More sources", "Phase 2", "done"),
    ("5", "Harmonise", "Phase 3", "done"),
    ("6", "Explore", "Phase 4", "done"),
    ("7", "Reproduce", "Phase 5", "next"),
    ("8", "Original R code", "Phase 6", "later"),
    ("9", "Prototype app", "Phase 7", "later"),
    ("10", "Multi-omics", "Phase 8", "later"),
    ("11", "Validate", "Phase 9", "later"),
    ("12", "Database + API", "Phase 10", "later"),
    ("13", "React frontend", "Phase 11", "later"),
    ("14", "Orchestrate", "Phase 12", "later"),
    ("15", "Knowledge graph", "Phase 13", "later"),
    ("16", "GraphRAG", "Phase 14", "later"),
    ("17", "MCP server", "Phase 15", "later"),
    ("18", "Agent", "Phase 16", "later"),
    ("19", "Containers", "Phase 17", "later"),
    ("20", "Release 1.0", "Phase 18", "later"),
    ("21", "The product", "beyond the repo", "later"),
]
STATUS_STYLE = {"done": (GREEN, "#E6F4EA", "built"),
                "next": (GOLD, "#FFF3CD", "next"),
                "later": (GREY, "#F5F5F5", "planned")}


def leaf_and_signal(scale: float = 1.0) -> str:
    """The mark: a leaf with bacteria on it, and a signal line whose one clear
    peak rises out of the noise (a real signal, found and checked)."""
    return f"""
  <path d="M 42 158 C 40 88, 96 40, 182 38 C 180 116, 128 166, 42 158 Z" fill="#E6F4EA" stroke="{GREEN}" stroke-width="{5 * scale}"/>
  <path d="M 48 152 C 90 120, 130 84, 176 44" fill="none" stroke="{GREEN}" stroke-width="{3 * scale}" stroke-linecap="round"/>
  <circle cx="86" cy="108" r="8" fill="{BLUE}"/><circle cx="118" cy="122" r="6" fill="{PURPLE}"/>
  <circle cx="132" cy="70" r="7" fill="{GOLD}"/><circle cx="104" cy="78" r="5" fill="{BLUE}"/>
  <polyline points="20,132 32,126 42,136 52,124 62,134 72,128 82,133 94,46 106,133 118,127 130,134 142,126 154,133 166,128 196,131"
            fill="none" stroke="{INK}" stroke-width="{4.5 * scale}" stroke-linejoin="round" stroke-linecap="round"/>
  <circle cx="94" cy="46" r="{7 * scale}" fill="{RED}" stroke="white" stroke-width="2"/>"""


def logo_svg() -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="720" height="200" viewBox="0 0 720 200" role="img" aria-label="RealSignal logo">
  <title>RealSignal</title>
  <rect width="720" height="200" rx="18" fill="#F5F9FF"/>
  <g transform="translate(14,0)">{leaf_and_signal()}
  </g>
  <text x="238" y="106" font-family="{FONT}" font-size="58" font-weight="700" fill="{INK}">Real<tspan fill="{GREEN}">Signal</tspan></text>
  <text x="241" y="143" font-family="{FONT}" font-size="19" fill="{SOFT}">reproduce, check and extend a published result</text>
</svg>
"""


def icon_svg() -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="256" height="256" viewBox="0 0 256 256" role="img" aria-label="RealSignal icon">
  <title>RealSignal icon</title>
  <rect width="256" height="256" rx="48" fill="#F5F9FF"/>
  <g transform="translate(20,28) scale(1.08)">{leaf_and_signal()}
  </g>
</svg>
"""


def wordmark_svg() -> str:
    """The icon and the name on one line, for small spaces such as an app's sidebar."""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="400" height="96" viewBox="0 0 400 96" role="img" aria-label="RealSignal">
  <title>RealSignal</title>
  <g transform="translate(0,2) scale(0.46)">{leaf_and_signal(1.4)}
  </g>
  <text x="102" y="62" font-family="{FONT}" font-size="44" font-weight="700" fill="{INK}">Real<tspan fill="{GREEN}">Signal</tspan></text>
</svg>
"""


def journey_svg() -> str:
    """A winding road of stepping stones: rows of eight, left to right, then
    right to left, then left to right again, so 22 stages fit on one screen."""
    per_row, width = 8, 1180
    xs = [90 + i * 143 for i in range(per_row)]
    ys = [150, 345, 540]
    points = []
    for row, y in enumerate(ys):
        row_xs = xs if row % 2 == 0 else list(reversed(xs))
        points += [(x, y) for x in row_xs]
    points = points[:len(STAGES)]
    height = ys[-1] + 130
    path = f"M {points[0][0]} {points[0][1]}"
    for i in range(1, len(points)):
        (x0, y0), (x1, y1) = points[i - 1], points[i]
        if y0 == y1:
            path += f" L {x1} {y1}"
        else:                              # the turn at the end of a row
            bulge = 90 if x0 > width / 2 else -90
            path += f" C {x0 + bulge} {y0}, {x1 + bulge} {y1}, {x1} {y1}"
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
           f'viewBox="0 0 {width} {height}" role="img" aria-label="RealSignal journey map">',
           "<title>RealSignal: the journey from day 0 to the product</title>",
           f'<rect width="{width}" height="{height}" rx="18" fill="#FBFCFE"/>',
           f'<text x="{width / 2}" y="44" text-anchor="middle" font-family="{FONT}" font-size="22" '
           f'font-weight="700" fill="{INK}">The RealSignal journey, from a blank laptop to a finished product</text>',
           f'<path d="{path}" fill="none" stroke="#D5DCE6" stroke-width="16" stroke-linecap="round" '
           'stroke-linejoin="round"/>']
    for (x, y), (num, label, tag, status) in zip(points, STAGES):
        edge, fill, _word = STATUS_STYLE[status]
        tick = "✓" if status == "done" else ("▶" if status == "next" else "")
        dash = ' stroke-dasharray="6 4"' if status == "later" else ""
        out += [f'<circle cx="{x}" cy="{y}" r="34" fill="{fill}" stroke="{edge}" stroke-width="4"{dash}/>',
                f'<text x="{x}" y="{y + 10}" text-anchor="middle" font-family="{FONT}" font-size="28" '
                f'font-weight="700" fill="{edge}">{num}</text>',
                f'<text x="{x + 27}" y="{y - 24}" font-family="{FONT}" font-size="16" font-weight="700" '
                f'fill="{edge}">{tick}</text>',
                f'<text x="{x}" y="{y + 56}" text-anchor="middle" font-family="{FONT}" font-size="13.5" '
                f'font-weight="600" fill="{INK}">{escape(label)}</text>',
                f'<text x="{x}" y="{y + 73}" text-anchor="middle" font-family="{FONT}" font-size="11.5" '
                f'fill="{SOFT}">{escape(tag)}</text>']
    legend_y = height - 24
    for i, (status, (edge, fill, word)) in enumerate(STATUS_STYLE.items()):
        lx = 880 + i * 100
        dash = ' stroke-dasharray="4 3"' if status == "later" else ""
        out += [f'<circle cx="{lx}" cy="{legend_y - 4}" r="8" fill="{fill}" stroke="{edge}" stroke-width="3"{dash}/>',
                f'<text x="{lx + 15}" y="{legend_y}" font-family="{FONT}" font-size="13" fill="{INK}">{word}</text>']
    out.append("</svg>")
    return "\n".join(out) + "\n"


# =============================================================================
# The interactive journey, read from docs/HANDBOOK.md
# =============================================================================

def github_anchor(heading: str) -> str:
    """The link anchor GitHub gives a heading: lower case, punctuation dropped,
    spaces turned into hyphens ("Stage 3: Phase 1, ..." -> "stage-3-phase-1-...")."""
    return re.sub(r"[^\w\- ]", "", heading.strip().lower()).replace(" ", "-")


def md_inline(text: str, base: str = "docs") -> str:
    """The little Markdown the Handbook uses inside a paragraph, as HTML:
    **bold**, *italics*, `code` and [links](...). Relative links become links
    to the same file on GitHub, so they work from a downloaded page too."""
    def link(m):
        label, target = m.group(1), m.group(2)
        if target.startswith("#"):
            url = f"{GITHUB}/docs/HANDBOOK.md{target}"
        elif re.match(r"https?://", target):
            url = target
        else:
            parts = []
            for piece in (Path(base) / target.split("#")[0]).as_posix().split("/"):
                if piece == "..":
                    parts.pop()
                elif piece not in ("", "."):
                    parts.append(piece)
            url = f"{GITHUB}/{'/'.join(parts)}" + (f"#{target.split('#', 1)[1]}" if "#" in target else "")
        return f'<a href="{html.escape(url, quote=True)}" target="_blank" rel="noopener">{label}</a>'
    codes: list[str] = []

    def keep_code(m):                    # protect `code` from the other rules
        codes.append(f"<code>{html.escape(m.group(1))}</code>")
        return f"\x00{len(codes) - 1}\x00"
    out = re.sub(r"`([^`]+)`", keep_code, text)
    out = html.escape(out, quote=False)
    out = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link, out)
    out = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", out)
    out = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?!\w)", r"<em>\1</em>", out)
    return re.sub("\x00(\\d+)\x00", lambda m: codes[int(m.group(1))], out)


def handbook_stages(path: Path = HANDBOOK) -> list[dict]:
    """Each stage of the Handbook: its row in the stage table and its What,
    Why, Checkpoint and commit paragraphs."""
    text = path.read_text(encoding="utf-8")
    rows = {}
    for line in text.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 6 and re.fullmatch(r"\d+(\.\d+)?", cells[0]):
            rows[cells[0]] = {"area": cells[1], "title": cells[2], "guide": cells[3], "time": cells[4]}
    # Split at "## " headings, ignoring lines inside code blocks (a "## --tags"
    # comment in a command block isn't a heading).
    sections, heading, lines, in_code = [], None, [], False
    for line in text.splitlines():
        if line.startswith("```"):
            in_code = not in_code
        if line.startswith("## ") and not in_code:
            if heading:
                sections.append((heading, lines))
            heading, lines = line[3:].strip(), []
        elif heading:
            lines.append(line)
    if heading:
        sections.append((heading, lines))

    stages = []
    for heading, body in sections:
        m = re.match(r"Stage (\d+(?:\.\d+)?): ", heading)
        if not m:
            continue
        number = m.group(1)
        parts, current, in_code = {}, None, False
        for line in body:
            if line.startswith("```"):
                in_code = not in_code
                continue
            if in_code:
                # A stage's save block: show its commit message and tag, not every command.
                saved = re.match(r'\s*git (commit -m|tag -a \S+ -m) "(.*)"', line)
                if saved and current == "Commit":
                    what = "Commit message" if saved.group(1).startswith("commit") else "Tag " + saved.group(1).split()[2]
                    parts[current].append(f"{what}: `{saved.group(2)}`")
                continue
            if line.strip() == "---":            # a horizontal rule ends the stage's text
                continue
            label = re.match(r"\*\*(What|Why|Checkpoint|Commit messages used|Commit message|Save it)(?: \(planned\))?[.:]?\*\*[.:]?\s*(.*)", line)
            if label:
                current = "Commit" if label.group(1).startswith(("Commit", "Save")) else label.group(1)
                parts[current] = [label.group(2)]
            elif current and line.strip() and not line.startswith(("![", "|", ">", "    ")):
                parts[current].append(line.strip())

        def to_html(lines):
            out, items = [], []
            for ln in lines:
                if re.match(r"\d+\. ", ln):
                    items.append(md_inline(re.sub(r"^\d+\. ", "", ln)))
                    continue
                if items:
                    out.append("<ol>" + "".join(f"<li>{i}</li>" for i in items) + "</ol>")
                    items = []
                if ln:
                    out.append(f"<p>{md_inline(ln)}</p>")
            if items:
                out.append("<ol>" + "".join(f"<li>{i}</li>" for i in items) + "</ol>")
            return "".join(out)
        row = rows.get(number, {})
        stages.append({"number": number, "heading": heading.split(": ", 1)[1],
                       "anchor": f"{GITHUB}/docs/HANDBOOK.md#{github_anchor(heading)}",
                       "area": row.get("area", ""), "time": row.get("time", ""),
                       "guide": md_inline(row.get("guide", "")) if row.get("guide") else "",
                       **{k.lower(): to_html(v) for k, v in parts.items()}})
    status_of = {num: status for num, _, _, status in STAGES}
    labels = {num: label for num, label, _, _ in STAGES}
    for st in stages:
        st["status"] = status_of.get(st["number"], "done")
        st["label"] = labels.get(st["number"], st["heading"])
    return stages


def journey_html() -> str:
    """A small page that works offline: no internet, no libraries."""
    stages = handbook_stages()
    words = {key: style[2] for key, style in STATUS_STYLE.items()}
    data = json.dumps(stages, ensure_ascii=False).replace("</", "<\\/")
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>RealSignal journey</title>
<style>
  :root {{ --ink:{INK}; --soft:{SOFT}; --line:#D5DCE6; --bg:#FBFCFE; --card:#FFFFFF; --done:{GREEN}; --next:{GOLD}; --later:{GREY}; --code:#F1F4F8; --link:#2E5FC1; }}
  @media (prefers-color-scheme: dark) {{
    :root {{ --ink:#E8ECF1; --soft:#A9B4C2; --line:#3A4350; --bg:#16191D; --card:#1E2228; --code:#2A3038; --link:#8FB0F5; }}
  }}
  * {{ box-sizing: border-box; }}
  body {{ margin:0; font-family:{FONT}; color:var(--ink); background:var(--bg); }}
  header {{ padding:24px 16px 8px; max-width:1100px; margin:0 auto; }}
  h1 {{ font-size:24px; margin:0 0 6px; }}
  header p {{ margin:4px 0; color:var(--soft); }}
  .filters {{ display:flex; gap:8px; flex-wrap:wrap; margin:12px 0 4px; }}
  .filters button {{ border:1px solid var(--line); background:var(--card); border-radius:999px; padding:6px 14px; cursor:pointer; font:inherit; color:var(--ink); }}
  .filters button[aria-pressed="true"] {{ background:var(--ink); color:var(--bg); border-color:var(--ink); }}
  .road {{ display:grid; grid-template-columns:repeat(auto-fill, minmax(150px, 1fr)); gap:12px; padding:12px 16px; max-width:1100px; margin:0 auto; }}
  .stone {{ border:2px solid var(--later); background:var(--card); border-radius:14px; padding:10px 12px; text-align:left; cursor:pointer; font:inherit; color:var(--ink); }}
  .stone .num {{ display:inline-block; min-width:30px; height:30px; line-height:26px; text-align:center; border-radius:15px; border:2px solid var(--later); font-weight:700; margin-right:6px; }}
  .stone .what {{ font-weight:600; }}
  .stone .tag {{ display:block; font-size:12px; color:var(--soft); margin-top:4px; }}
  .stone.done, .stone.done .num {{ border-color:var(--done); }}
  .stone.next, .stone.next .num {{ border-color:var(--next); }}
  .stone.later {{ border-style:dashed; }}
  .stone[aria-selected="true"] {{ box-shadow:0 0 0 3px #B9D2FF; }}
  .stone:focus-visible {{ outline:3px solid #5B8DEF; outline-offset:2px; }}
  .detail {{ max-width:1100px; margin:8px auto 40px; padding:0 16px; }}
  .card {{ background:var(--card); border:1px solid var(--line); border-radius:16px; padding:18px 22px; }}
  .card h2 {{ margin:0 0 4px; font-size:20px; }}
  .meta {{ color:var(--soft); font-size:14px; margin-bottom:10px; }}
  .badge {{ display:inline-block; padding:2px 10px; border-radius:999px; font-size:12px; font-weight:700; color:#fff; margin-right:6px; }}
  .badge.done {{ background:var(--done); }} .badge.next {{ background:var(--next); }} .badge.later {{ background:var(--later); }}
  .section h3 {{ font-size:13px; text-transform:uppercase; letter-spacing:.06em; color:var(--soft); margin:14px 0 4px; }}
  .section p, .section li {{ line-height:1.55; margin:4px 0; overflow-wrap:anywhere; }}
  code {{ background:var(--code); padding:1px 5px; border-radius:5px; font-size:90%; }}
  a {{ color:var(--link); }}
  footer {{ text-align:center; color:var(--soft); font-size:12px; padding:0 16px 30px; }}
</style></head>
<body>
<header>
  <h1>The RealSignal journey</h1>
  <p>From a blank laptop to a finished product. Pick a stage to see what you do, why, and how you know you're done.</p>
  <p>Green: {words["done"]}, gold: {words["next"]}, dashed grey: {words["later"]}. Every word below comes from <a href="{GITHUB}/docs/HANDBOOK.md" target="_blank" rel="noopener">docs/HANDBOOK.md</a>.</p>
  <div class="filters" role="group" aria-label="Show stages">
    <button data-filter="all" aria-pressed="true">All stages</button>
    <button data-filter="done" aria-pressed="false">Built</button>
    <button data-filter="next" aria-pressed="false">Next</button>
    <button data-filter="later" aria-pressed="false">Planned</button>
  </div>
</header>
<nav class="road" id="road" aria-label="Stages"></nav>
<main class="detail" id="detail" aria-live="polite"></main>
<footer>RealSignal: an open reproduction of a published study, built and documented in the open.</footer>
<script>
const STAGES = {data};
const WORDS = {json.dumps(words)};
const road = document.getElementById("road"), detail = document.getElementById("detail");
function show(i) {{
  const s = STAGES[i];
  document.querySelectorAll(".stone").forEach((b, j) => b.setAttribute("aria-selected", j === i));
  const block = (title, body) => body ? `<div class="section"><h3>${{title}}</h3>${{body}}</div>` : "";
  detail.innerHTML = `<article class="card">
    <h2>Stage ${{s.number}}: ${{s.heading}}</h2>
    <div class="meta"><span class="badge ${{s.status}}">${{WORDS[s.status]}}</span>${{s.area}}${{s.time ? ", " + s.time : ""}}${{s.guide ? ". Guide: " + s.guide : ""}}</div>
    ${{block("What", s.what)}}${{block("Why", s.why)}}${{block("Checkpoint", s.checkpoint)}}${{block("Commit", s.commit)}}
    <p><a href="${{s.anchor}}" target="_blank" rel="noopener">Read this stage in the Handbook</a></p></article>`;
  history.replaceState(null, "", "#stage-" + s.number);
}}
STAGES.forEach((s, i) => {{
  const b = document.createElement("button");
  b.className = "stone " + s.status; b.dataset.status = s.status;
  b.innerHTML = `<span class="num">${{s.number}}</span><span class="what">${{s.label}}</span><span class="tag">${{s.area}}, ${{WORDS[s.status]}}</span>`;
  b.addEventListener("click", () => show(i));
  road.appendChild(b);
}});
document.querySelectorAll(".filters button").forEach(f => f.addEventListener("click", () => {{
  document.querySelectorAll(".filters button").forEach(x => x.setAttribute("aria-pressed", x === f));
  document.querySelectorAll(".stone").forEach(b => b.hidden = !(f.dataset.filter === "all" || b.dataset.status === f.dataset.filter));
}}));
const wanted = location.hash.replace("#stage-", "");
const start = STAGES.findIndex(s => s.number === wanted);
show(start >= 0 ? start : Math.max(0, STAGES.findIndex(s => s.status === "next")));
</script>
</body></html>
"""


if __name__ == "__main__":
    IMG.mkdir(parents=True, exist_ok=True)
    for name, svg in [("realsignal_logo.svg", logo_svg()), ("realsignal_icon.svg", icon_svg()),
                      ("realsignal_wordmark.svg", wordmark_svg()), ("journey_map.svg", journey_svg())]:
        (IMG / name).write_text(svg, encoding="utf-8")
        print(f"  drew docs/img/{name}")
    if HANDBOOK.exists():
        INTERACTIVE.mkdir(parents=True, exist_ok=True)
        (INTERACTIVE / "journey.html").write_text(journey_html(), encoding="utf-8")
        print(f"  wrote docs/interactive/journey.html ({len(handbook_stages())} stages, read from docs/HANDBOOK.md)")
