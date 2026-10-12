"""
tests/test_docs.py: checks that keep the documentation trustworthy.

Documentation is a large part of this project, and it rots in quiet ways: a
heading gets renamed and every link to it breaks, or a long dash pasted from
a word processor ends up inside a command and breaks it in a terminal. These
tests catch both, and they keep the Handbook's stage table and the journey
map's stage list in step.

Run from the project folder:  pytest -q
"""

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# Written as escape codes so this file passes its own check.
LOOK_ALIKES = {"\u2014": "long dash", "\u2013": "en dash", "\u201c": "curly quote", "\u201d": "curly quote"}
TEXT_SUFFIXES = {".md", ".py", ".txt", ".sh", ".ps1", ".ini", ".html", ".svg", ".cfg", ".toml", ".json", ".yml", ".yaml"}


def markdown_files() -> list[Path]:
    """README, CHANGELOG and every guide in docs/."""
    files = [ROOT / "README.md", ROOT / "CHANGELOG.md"] + sorted((ROOT / "docs").glob("*.md"))
    return [f for f in files if f.exists()]


def project_files() -> list[Path]:
    """The files a commit could publish: tracked plus new, ignored ones left out."""
    out = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard"],
                         cwd=ROOT, capture_output=True, text=True, check=True).stdout
    return [ROOT / line for line in out.splitlines() if (ROOT / line).is_file()]


def github_anchor(heading: str) -> str:
    """The anchor GitHub gives a heading: lower case, punctuation dropped, spaces to hyphens."""
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", heading)        # [text](link) -> text
    text = re.sub(r"[^\w\- ]", "", text.strip().lower())
    return text.replace(" ", "-")


def anchors_of(path: Path) -> set[str]:
    """Every anchor a Markdown file offers, skipping lines inside code blocks."""
    seen: dict[str, int] = {}
    found, in_code = set(), False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.lstrip().startswith("```"):
            in_code = not in_code
            continue
        match = re.match(r"^(#{1,6})\s+(.*)", line)
        if match and not in_code:
            base = github_anchor(match.group(2))
            n = seen.get(base, 0)
            found.add(base if n == 0 else f"{base}-{n}")
            seen[base] = n + 1
    return found


def links_of(path: Path):
    """Every Markdown link target outside code blocks and inline code."""
    in_code = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.lstrip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        for target in re.findall(r"\]\(([^)\s]+)\)", re.sub(r"`[^`]*`", "", line)):
            yield target


def test_every_link_between_the_documents_resolves():
    problems = []
    for doc in markdown_files():
        for target in links_of(doc):
            if re.match(r"(https?|mailto):", target):
                continue
            file_part, _, anchor = target.partition("#")
            dest = (doc.parent / file_part).resolve() if file_part else doc
            if not dest.exists():
                problems.append(f"{doc.relative_to(ROOT)}: missing file {target}")
                continue
            if anchor and dest.suffix == ".md" and anchor not in anchors_of(dest):
                problems.append(f"{doc.relative_to(ROOT)}: no heading for #{anchor} in {dest.relative_to(ROOT)}")
    assert not problems, "\n".join(problems)


def test_no_long_dashes_or_curly_quotes():
    problems = []
    for path in project_files():
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        for number, line in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
            for char, name in LOOK_ALIKES.items():
                if char in line:
                    problems.append(f"{path.relative_to(ROOT)}:{number}: {name}")
    assert not problems, "\n".join(problems[:40])


def test_handbook_stage_table_matches_the_journey_map():
    """The Handbook's stage table and figures/make_illustrations.py tell the same story."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("ill", ROOT / "figures" / "make_illustrations.py")
    ill = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ill)
    table = {}
    for line in (ROOT / "docs" / "HANDBOOK.md").read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 6 and re.fullmatch(r"\d+(\.\d+)?", cells[0]):
            table[cells[0]] = cells[5]
    words = {"done": "✅", "next": "⏳", "later": "⬜"}
    for number, _label, _tag, status in ill.STAGES:
        assert number in table, f"stage {number} is missing from the Handbook's table"
        assert table[number].startswith(words[status]), (
            f"stage {number}: Handbook says '{table[number]}', the journey map says '{status}'")
