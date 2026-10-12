"""
notebooks/explore_sources.py: a first look at the other layers, once fetched.

scripts/fetch_sources.py downloads the files in the source register. This
script opens them and answers the questions Phase 2 has to answer before any
later phase relies on them:

  * Supplementary tables (Layers 3, 4 and 5): which sheets are there, what
    each one is called, how big it is, and how many of the screen's 35
    strains it mentions.
  * Genomes (Layer 2): for each strain, how many pieces (contigs) the genome
    is in, how long it is, and its GC content.

It describes the files; it doesn't analyse them. The protection scores in
Layer 5, for example, are compared with the model's ranking in Phase 9, not
here.

Run from the project folder, with the virtual environment active, after
scripts/fetch_data.py and scripts/fetch_sources.py:

    python notebooks/explore_sources.py

Explained in docs/03-phase-2-more-sources.md, section 9.
"""

import csv
import gzip
import re
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCES = PROJECT_ROOT / "data" / "raw" / "sources"
FILES = PROJECT_ROOT / "sources" / "files.csv"
DESIGN = PROJECT_ROOT / "data" / "raw" / "extracted" / "Data" / "MetaData" / "Mini5SynComScreen" / "20200828_Mixes.txt"


def screen_strains() -> list[str]:
    """The 35 strains of the community screen, read from Layer 1's design file."""
    return list(pd.read_csv(DESIGN, sep="\t", nrows=0).columns[1:])


def strains_mentioned(sheet: pd.DataFrame, strains: list[str]) -> set[str]:
    """Which of the screen strains a sheet mentions.

    Strains appear as 'Leaf15' in some tables and as the bare number 15 in a
    'Strain_ID' column in others, so both are looked for."""
    wanted = set(strains)
    found = set()
    for column in sheet.columns:
        values = [str(v).strip() for v in sheet[column] if pd.notna(v)]
        # A column counts as a strain-ID column when one of its first cells says so.
        id_column = any("Strain_ID" in v or v == "Strain" for v in values[:6])
        for value in values:
            if value in wanted:
                found.add(value)
            elif id_column and re.fullmatch(r"\d+(\.0)?", value):
                name = "Leaf" + value.removesuffix(".0")
                if name in wanted:
                    found.add(name)
    return found


def describe_workbook(path: Path, strains: list[str]) -> None:
    """One line per sheet: name, size, its title, and strain coverage."""
    sheets = pd.read_excel(path, sheet_name=None, header=None)
    print(f"  {len(sheets)} sheets")
    print("  sheet       rows  cols  strains  title")
    nearly = []
    for name, sheet in sheets.items():
        title = next((str(v) for v in sheet.iloc[:, 0] if isinstance(v, str) and v.strip()), "")
        found = strains_mentioned(sheet, strains)
        print(f"  {name:<10}{sheet.shape[0]:>6}{sheet.shape[1]:>6}{len(found):>6}/{len(strains)}  {title[:40].rstrip()}")
        if len(strains) - 5 <= len(found) < len(strains):
            nearly.append((name, [s for s in strains if s not in found]))
    # A sheet that names almost every strain is the interesting case: which
    # strains does it leave out, and is that missing data or a real "none"?
    if nearly:
        print("  sheets that name all but a few strains, and the strains they leave out:")
        for name, missing in nearly:
            print(f"    {name:<10}{', '.join(missing)}")


def genome_stats(path: Path) -> tuple[int, int, float]:
    """Contigs, total length and GC content (%) of a gzipped FASTA file.

    FASTA is plain text: a line starting with '>' names a piece of sequence
    (a contig), and the lines after it are the letters A, C, G and T."""
    contigs = length = gc = 0
    with gzip.open(path, "rt") as handle:
        for line in handle:
            if line.startswith(">"):
                contigs += 1
                continue
            seq = line.strip().upper()
            length += len(seq)
            gc += seq.count("G") + seq.count("C")
    return contigs, length, (100 * gc / length if length else 0.0)


def main() -> int:
    if not DESIGN.exists():
        print("Layer 1 isn't unpacked yet. Run:  python scripts/fetch_data.py")
        return 1
    if not SOURCES.exists():
        print("Nothing fetched yet. Run:  python scripts/fetch_sources.py")
        return 1
    strains = screen_strains()
    with open(FILES, newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    for row in [r for r in rows if r["kind"] == "url"]:
        path = SOURCES / row["source_id"] / row["target"]
        print(f"{row['source_id']}: {row['target']}")
        if path.exists():
            describe_workbook(path, strains)
        else:
            print("  not fetched yet")
        print()

    genomes = [r for r in rows if r["kind"] == "ncbi_assembly"]
    print(f"refseq_genomes: {len(genomes)} genomes listed for the {len(strains)} screen strains")
    without = sorted(set(strains) - {r["strain"] for r in genomes}, key=lambda s: int(s[4:]))
    print(f"  no genome listed : {', '.join(without) or 'none'}")
    print("  strain    contigs   length (Mb)   GC %")
    totals = []
    for row in genomes:
        path = SOURCES / row["source_id"] / row["target"]
        if not path.exists():
            print(f"  {row['strain']:<10} not fetched yet")
            continue
        contigs, length, gc = genome_stats(path)
        totals.append((contigs, length, gc))
        print(f"  {row['strain']:<10}{contigs:>7}{length / 1e6:>14.2f}{gc:>7.1f}")
    if totals:
        lengths = [t[1] / 1e6 for t in totals]
        gcs = [t[2] for t in totals]
        print(f"  {len(totals)} genomes: {min(lengths):.2f} to {max(lengths):.2f} Mb, "
              f"GC {min(gcs):.1f} to {max(gcs):.1f} %")
    return 0


if __name__ == "__main__":
    sys.exit(main())
