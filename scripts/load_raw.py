"""
scripts/load_raw.py: copy every raw table into the warehouse, unchanged.

WHAT THIS SCRIPT DOES
---------------------
  --list     Print sources/tables.csv: every table that gets loaded, the file
             (and sheet) it comes from, and what it holds.
  (default)  Read each of those tables and write it into the DuckDB database
             data/warehouse/realsignal.duckdb, in a schema called raw, with
             every value kept as the text the file holds. The three tables in
             sources/ (the register, the file list and the table list) go in
             too, and raw.load_log records what was loaded, from where, and
             each file's SHA-256.

WHY IT EXISTS
-------------
  dbt transforms tables that are already inside a database. Something has to
  put them there first: that's this script, the "load" in ELT (extract, load,
  transform). It changes nothing on the way in. Values stay text, a heading
  stays as the file spells it, and footnotes under a table come along too.
  Every decision about what a value means is made afterwards, in dbt, where
  it's written down and tested. The only things added are a column _row (the
  row number a spreadsheet program shows for that line, so any value can be
  found in its file) and, for genomes, the counting described below.

  A genome file isn't a table, so for Layer 2 the script writes one row per
  contig: its name, its description, its length and its number of G and C
  letters. That's the smallest table a FASTA file can become.

  Nothing is loaded unless every file is present, so a failed run never leaves
  a half-filled warehouse behind.

Run from the project folder, with the virtual environment active, after
scripts/fetch_data.py and scripts/fetch_sources.py:

    python scripts/load_raw.py --list
    python scripts/load_raw.py

Explained in docs/04-phase-3-harmonisation.md, section 6.
"""

from __future__ import annotations

import argparse
import datetime as dt
import gzip
import math
import sys
import textwrap
from pathlib import Path

import duckdb
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))          # so Python finds src/realsignal/
from realsignal import helpers  # noqa: E402  (has to come after the line above)

SOURCES_DIR = PROJECT_ROOT / "sources"
TABLES_PATH = SOURCES_DIR / "tables.csv"
WAREHOUSE = PROJECT_ROOT / "data" / "warehouse" / "realsignal.duckdb"

# The project's own tables, loaded first, so that dbt can check every raw table
# against the register and match genome files to strains.
REGISTERS = {"source_register": "register.csv",
             "source_files": "files.csv",
             "source_tables": "tables.csv"}


def rel(path: Path) -> str:
    return helpers.rel(path, PROJECT_ROOT)


# ---------------------------------------------------------------------------
# Turning cells into text
# ---------------------------------------------------------------------------

def as_text(value) -> str | None:
    """A cell's value as the text a person would read in the file.

    Workbook cells arrive as numbers, dates or text. An empty cell becomes a
    missing value (NULL in the database); a whole number stays without a
    decimal point (12, not 12.0); everything else is written as it is."""
    if value is None:
        return None
    if isinstance(value, float):
        if math.isnan(value):
            return None
        return str(int(value)) if value.is_integer() else repr(value)
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    if isinstance(value, (pd.Timestamp, dt.datetime, dt.date)):
        return value.isoformat()
    text = str(value)
    return text if text != "" else None


def column_names(header: list) -> list[str]:
    """The headings as written, made usable as column names.

    Spaces at either end are removed; an empty heading becomes column_<n>; a
    heading that repeats (Table S4 names each growth medium once per sensitive
    strain) gets _2, _3 and so on, because a table can't have two columns with
    the same name."""
    names, seen = [], {}
    for number, cell in enumerate(header, 1):
        name = (as_text(cell) or "").strip() or f"column_{number}"
        seen[name] = seen.get(name, 0) + 1
        names.append(name if seen[name] == 1 else f"{name}_{seen[name]}")
    return names


def grid_to_table(grid: pd.DataFrame, header_row: int) -> pd.DataFrame:
    """Rows below the heading row, with _row numbered as a spreadsheet shows it.

    Rows with nothing in them are skipped; every other row is kept, footnotes
    and total rows included, because deciding what a row means is dbt's job."""
    header = list(grid.iloc[header_row - 1])
    body = grid.iloc[header_row:].map(as_text)
    body.columns = column_names(header)
    body.insert(0, "_row", range(header_row + 1, header_row + 1 + len(body)))
    filled = body.drop(columns="_row").notna().any(axis=1)
    return body[filled].reset_index(drop=True)


# ---------------------------------------------------------------------------
# Reading each kind of file
# ---------------------------------------------------------------------------

def read_text_table(path: Path, separator: str, header_row: int) -> pd.DataFrame:
    """A tab- or comma-separated file, every value read as text.

    keep_default_na=False stops pandas from turning words such as NA or TRUE
    into something else; only an empty cell counts as missing."""
    grid = pd.read_csv(path, sep=separator, header=None, dtype=str,
                       keep_default_na=False, na_values=[""])
    return grid_to_table(grid, header_row)


def read_sheet(path: Path, sheet: str, header_row: int) -> pd.DataFrame:
    """One sheet of a workbook, from its heading row down."""
    grid = pd.read_excel(path, sheet_name=sheet, header=None, dtype=object)
    return grid_to_table(grid, header_row)


def read_contigs(paths: list[Path]) -> pd.DataFrame:
    """One row per contig of every gzipped FASTA file.

    A line starting with '>' names a contig ('>NZ_LMKQ01000001.1 Rhizobium sp.
    Leaf68 contig_1, ...'): the first word is its accession, the rest a
    description. The lines after it are its letters, counted here."""
    rows = []
    for path in paths:
        contig = description = None
        length = gc = 0
        with gzip.open(path, "rt") as handle:
            for line in handle:
                if line.startswith(">"):
                    if contig is not None:
                        rows.append((path.name, contig, description, length, gc))
                    words = line[1:].strip().split(" ", 1)
                    contig, description = words[0], (words[1] if len(words) > 1 else "")
                    length = gc = 0
                else:
                    letters = line.strip().upper()
                    length += len(letters)
                    gc += letters.count("G") + letters.count("C")
        if contig is not None:
            rows.append((path.name, contig, description, length, gc))
    table = pd.DataFrame(rows, columns=["file", "contig", "description", "length", "gc_count"])
    table = table.astype({"length": str, "gc_count": str})     # text, like every raw value
    table.insert(0, "_row", range(1, len(table) + 1))
    return table


def files_for(spec: dict) -> list[Path]:
    """The file a row of sources/tables.csv points to, or for a pattern such
    as *_genomic.fna.gz, every file that matches it, in name order."""
    path = PROJECT_ROOT / spec["path"]
    if "*" in path.name:
        return sorted(path.parent.glob(path.name))
    return [path] if path.exists() else []


def read_one(spec: dict) -> pd.DataFrame:
    paths = files_for(spec)
    kind, header_row = spec["format"], int(spec["header_row"] or 1)
    if kind == "tsv":
        return read_text_table(paths[0], "\t", header_row)
    if kind == "csv":
        return read_text_table(paths[0], ",", header_row)
    if kind == "xlsx":
        return read_sheet(paths[0], spec["sheet"], header_row)
    if kind == "fasta_gz":
        return read_contigs(paths)
    raise ValueError(f"unknown format '{kind}' for {spec['table_name']}")


# ---------------------------------------------------------------------------
# Listing and loading
# ---------------------------------------------------------------------------

def table_specs() -> list[dict]:
    return helpers.read_csv_rows(TABLES_PATH)


def register_specs() -> list[dict]:
    """The three tables in sources/, described the way sources/tables.csv
    describes the others, so they go through the same code."""
    return [{"table_name": name, "source_id": "register", "format": "csv",
             "path": f"sources/{file}", "sheet": "", "header_row": "1"}
            for name, file in REGISTERS.items()]


def where_from(spec: dict) -> str:
    """Where a table comes from, short enough for one line: a file of the
    Phase 1 archive from inside its Data/ folder ('CleanData/...'), a sheet
    of a workbook, or the pattern genome files match."""
    path = Path(spec["path"])
    if spec["format"] == "fasta_gz":
        return f"{path.parent.as_posix()}/{path.name}"
    if spec["sheet"]:
        return f"{path.name}, sheet {spec['sheet']}, headings in row {spec['header_row']}"
    return spec["path"].removeprefix("data/raw/extracted/Data/")


def show_list() -> int:
    helpers.banner("RAW TABLES: sources/tables.csv")
    source = None
    for spec in table_specs():
        if spec["source_id"] != source:
            source = spec["source_id"]
            inside = " (files in data/raw/extracted/Data/)" if spec["path"].startswith(
                "data/raw/extracted/Data/") else ""
            print(f"{source}{inside}:")
        # The table's name, then where it comes from, then what it holds.
        print(f"  {spec['table_name']}")
        print(f"    {where_from(spec)}")
        print(textwrap.fill(spec["what_it_holds"], width=78,
                            initial_indent="    ", subsequent_indent="    "))
    print()
    print(f"{len(table_specs())} tables, plus the three tables in sources/. "
          "Nothing has been loaded.")
    return 0


def missing_files(specs: list[dict]) -> list[dict]:
    return [s for s in specs if not files_for(s)]


def load(specs: list[dict]) -> int:
    helpers.banner("LOAD: the raw tables, exactly as the sources wrote them")
    gone = missing_files(specs)
    if gone:
        print("These files aren't here yet, so nothing has been loaded:")
        for spec in gone:
            print(f"  {spec['table_name']:<28} {spec['path'][:48]}")
        print()
        print("Fetch them first:")
        print("    python scripts/fetch_data.py       (Layer 1, the archive)")
        print("    python scripts/fetch_sources.py    (Layers 2 to 5)")
        return 1

    print(f"Into {rel(WAREHOUSE)}, schema raw")
    WAREHOUSE.parent.mkdir(parents=True, exist_ok=True)
    now = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    try:
        con = duckdb.connect(str(WAREHOUSE))
    except duckdb.IOException:
        print()
        print("The warehouse is open in another program, so it can't be written.")
        print("Close that program (a Python session, a database viewer, a dbt")
        print("command still running) and run this again.")
        return 1

    log, total_rows, source = [], 0, None
    try:
        # One transaction: either every table is replaced, or none is.
        con.execute("BEGIN TRANSACTION")
        con.execute("CREATE SCHEMA IF NOT EXISTS raw")
        for spec in specs:
            if spec["source_id"] != source:
                source = spec["source_id"]
                print("the registers in sources/:" if source == "register" else f"{source}:")
            table = read_one(spec)
            write_table(con, spec["table_name"], table)
            paths = files_for(spec)
            columns = table.shape[1] - 1                     # _row isn't the source's
            extra = (f"{len(paths)} files" if len(paths) > 1 else spec["sheet"])
            line = f"  {spec['table_name']:<28}{len(table):>6} rows{columns:>4} columns  {extra}"
            print(line.rstrip())
            total_rows += len(table)
            log.append({"table_name": spec["table_name"], "source_id": spec["source_id"],
                        "path": spec["path"], "sheet": spec["sheet"] or None,
                        "rows": len(table), "columns": columns, "files": len(paths),
                        "sha256": helpers.file_hashes(paths[0])[1] if len(paths) == 1 else None,
                        "loaded_at_utc": now})
        con.register("load_log_frame", pd.DataFrame(log))
        con.execute("CREATE OR REPLACE TABLE raw.load_log AS SELECT * FROM load_log_frame")
        con.unregister("load_log_frame")
        con.execute("COMMIT")
    except Exception:
        con.execute("ROLLBACK")
        raise
    finally:
        con.close()

    helpers.banner("SUMMARY")
    from_sources = sum(1 for s in specs if s["source_id"] != "register")
    print(f"Tables loaded : {len(specs)} ({from_sources} from sources/tables.csv, "
          f"{len(specs) - from_sources} from sources/)")
    print(f"Rows loaded   : {total_rows:,}")
    print("Load log      : raw.load_log")
    print("Next          : cd dbt, then dbt build")
    return 0


def write_table(con: duckdb.DuckDBPyConnection, name: str, table: pd.DataFrame) -> None:
    """Replace raw.<name> with this table: _row as a whole number, every other
    column as text (VARCHAR), whatever pandas made of it."""
    columns = ", ".join(f'"{c}" {"INTEGER" if c == "_row" else "VARCHAR"}' for c in table.columns)
    con.execute(f'CREATE OR REPLACE TABLE raw."{name}" ({columns})')
    con.register("incoming", table)
    con.execute(f'INSERT INTO raw."{name}" SELECT * FROM incoming')
    con.unregister("incoming")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Copy every raw table into the warehouse, unchanged.")
    parser.add_argument("--list", action="store_true", help="print sources/tables.csv; load nothing")
    args = parser.parse_args(argv)
    if args.list:
        return show_list()
    return load(register_specs() + table_specs())


if __name__ == "__main__":
    sys.exit(main())
