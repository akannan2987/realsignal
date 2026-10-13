"""
tests/test_load_raw.py: scripts/load_raw.py, on tiny made-up files.

The script reads real files that are never committed, so each test builds a
small stand-in project: a tab-separated table, a workbook laid out like the
journals' (a title, a blank row, headings in row 3, a repeated heading, a
footnote), and a gzipped genome in two pieces. The checks: values stay text,
row numbers point back into the file, the genome's letters are counted, a run
with a file missing loads nothing, and a second run replaces instead of adding.

Run from the project folder:  pytest -q
"""

import gzip
import importlib.util
import re
from pathlib import Path

import duckdb
import openpyxl
import pytest

ROOT = Path(__file__).resolve().parents[1]
LOOK_ALIKES = ("\u2014", "\u2013", "\u201c", "\u201d")   # long dashes and curly quotes, as escape codes


def load_script():
    spec = importlib.util.spec_from_file_location("load_raw", ROOT / "scripts" / "load_raw.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def project(tmp_path, monkeypatch):
    """A stand-in project folder with three small raw files and the tables in sources/."""
    sources = tmp_path / "sources"
    sources.mkdir()
    (sources / "register.csv").write_text(
        "source_id,layer,status\ntoy_archive,1,fetched\ntoy_journal,3,fetched\ntoy_genomes,2,fetched\n")
    (sources / "files.csv").write_text("file_id,source_id,target\nbook,toy_journal,book.xlsx\n")
    (sources / "tables.csv").write_text(
        "table_name,source_id,format,path,sheet,header_row,what_it_holds\n"
        "toy_plants,toy_archive,tsv,data/raw/toy/plants.txt,,1,a few plants\n"
        "toy_sheet,toy_journal,xlsx,data/raw/toy/book.xlsx,Table_S1,3,a sheet laid out like a journal's\n"
        "toy_contigs,toy_genomes,fasta_gz,data/raw/toy/*_genomic.fna.gz,,,one genome in two pieces\n")

    raw = tmp_path / "data" / "raw" / "toy"
    raw.mkdir(parents=True)
    (raw / "plants.txt").write_text("Uid\tMark\tCount\n1_1\tTRUE\t007\n1_2\tNA\t\n")

    book = openpyxl.Workbook()
    sheet = book.active
    sheet.title = "Table_S1"
    sheet.append(["Supplementary Table 1: a title above the table"])
    sheet.append([])
    sheet.append(["Strain", "Medium", "Medium", "Total"])        # a heading that repeats
    sheet.append(["Leaf1", "R2A", "MM", 12.0])                   # a whole number stored as 12.0
    sheet.append([])                                             # an empty row, skipped
    sheet.append(["Leaf2", "R2A", None, 0.5])
    sheet.append(["*a footnote under the table"])                # kept: dbt decides
    book.save(raw / "book.xlsx")

    with gzip.open(raw / "Leaf1_GCF_000000001.1_genomic.fna.gz", "wt") as handle:
        handle.write(">NZ_TOY01000001.1 Toy sp. Leaf1 contig_1\nACGT\nGGCC\n")
        handle.write(">NZ_TOY01000002.1 Toy sp. Leaf1 contig_2\nAATT\n")

    module = load_script()
    monkeypatch.setattr(module, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(module, "SOURCES_DIR", sources)
    monkeypatch.setattr(module, "TABLES_PATH", sources / "tables.csv")
    monkeypatch.setattr(module, "WAREHOUSE", tmp_path / "data" / "warehouse" / "toy.duckdb")
    return module


def query(module, sql):
    with duckdb.connect(str(module.WAREHOUSE), read_only=True) as con:
        return con.execute(sql).fetchall()


def test_list_loads_nothing(project, capsys):
    assert project.main(["--list"]) == 0
    out = capsys.readouterr().out
    assert "toy_sheet\n    book.xlsx, sheet Table_S1, headings in row 3\n" in out
    assert "Nothing has been loaded." in out
    assert not project.WAREHOUSE.exists()


def test_text_files_keep_their_text(project):
    assert project.main([]) == 0
    rows = query(project, 'select _row, "Uid", "Mark", "Count" from raw.toy_plants order by _row')
    # 007 stays 007, NA stays the word NA, and only the empty cell is missing.
    assert rows == [(2, "1_1", "TRUE", "007"), (3, "1_2", "NA", None)]


def test_workbook_rows_headings_and_numbers(project):
    assert project.main([]) == 0
    columns = [c[0] for c in query(project, "describe raw.toy_sheet")]
    assert columns == ["_row", "Strain", "Medium", "Medium_2", "Total"]
    rows = query(project, 'select _row, "Strain", "Medium_2", "Total" from raw.toy_sheet order by _row')
    assert rows == [(4, "Leaf1", "MM", "12"),                    # 12, not 12.0
                    (6, "Leaf2", None, "0.5"),                   # row 5 was empty
                    (7, "*a footnote under the table", None, None)]
    types = {name: kind for name, kind, *_ in query(project, "describe raw.toy_sheet")}
    assert types["Total"] == "VARCHAR" and types["_row"] == "INTEGER"


def test_genome_is_counted_contig_by_contig(project):
    assert project.main([]) == 0
    rows = query(project, "select file, contig, length, gc_count from raw.toy_contigs order by contig")
    assert rows == [("Leaf1_GCF_000000001.1_genomic.fna.gz", "NZ_TOY01000001.1", "8", "6"),
                    ("Leaf1_GCF_000000001.1_genomic.fna.gz", "NZ_TOY01000002.1", "4", "0")]


def test_registers_and_load_log(project):
    assert project.main([]) == 0
    tables = {r[0] for r in query(project, "select table_name from raw.load_log")}
    assert tables == {"source_register", "source_files", "source_tables",
                      "toy_plants", "toy_sheet", "toy_contigs"}
    sha = query(project, "select sha256 from raw.load_log where table_name = 'toy_sheet'")[0][0]
    from realsignal.helpers import file_hashes
    assert sha == file_hashes(project.PROJECT_ROOT / "data" / "raw" / "toy" / "book.xlsx")[1]
    files = query(project, "select files, sha256 from raw.load_log where table_name = 'toy_contigs'")
    assert files == [(1, file_hashes(next((project.PROJECT_ROOT / "data" / "raw" / "toy")
                                          .glob("*.fna.gz")))[1])]


def test_a_missing_file_loads_nothing(project, capsys):
    (project.PROJECT_ROOT / "data" / "raw" / "toy" / "plants.txt").unlink()
    assert project.main([]) == 1
    out = capsys.readouterr().out
    assert "nothing has been loaded" in out and "python scripts/fetch_data.py" in out
    assert not project.WAREHOUSE.exists()


def test_a_second_run_replaces_the_tables(project):
    assert project.main([]) == 0
    assert project.main([]) == 0
    assert query(project, "select count(*) from raw.toy_plants") == [(2,)]
    assert query(project, "select count(*) from raw.load_log") == [(6,)]


def test_output_is_plain_and_fits_80_columns(project, capsys):
    project.main(["--list"])
    project.main([])
    out = capsys.readouterr().out
    assert not any(ch in out for ch in LOOK_ALIKES)
    assert str(project.PROJECT_ROOT) not in out                # no home folders in the output
    too_long = [line for line in out.splitlines() if len(line) > 80]
    assert not too_long, too_long
    assert not re.search(r"[ \t]+$", out, flags=re.MULTILINE)  # no trailing spaces


def test_the_real_table_list_fits_80_columns(capsys):
    """--list on the committed sources/tables.csv, which has the longest file names."""
    load_script().main(["--list"])
    too_long = [line for line in capsys.readouterr().out.splitlines() if len(line) > 80]
    assert not too_long, too_long
