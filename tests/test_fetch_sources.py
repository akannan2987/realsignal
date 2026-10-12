"""
tests/test_fetch_sources.py: the source register and scripts/fetch_sources.py.

Two kinds of test:

* The register itself (sources/register.csv and sources/files.csv), checked
  as committed: every source has terms and a status, every file belongs to a
  source, every address is HTTPS, every genome accession looks like one.
* The fetcher, without the internet. A small web server runs on this computer
  for the length of a test, serving a stand-in for NCBI's genome folders (with
  their md5checksums.txt) and a stand-in for a journal's supplementary file.
  Python's own web server lists folders the way NCBI's does, so the script
  finds the genome folders exactly as it does for real.

Run from the project folder:  pytest -q
"""

import csv
import functools
import gzip
import hashlib
import http.server
import importlib.util
import re
import threading
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "fetch_sources.py"
LOOK_ALIKES = ("\u2014", "\u2013", "\u201c", "\u201d")   # long dashes and curly quotes, as escape codes


def load_script():
    spec = importlib.util.spec_from_file_location("fetch_sources", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read(path: Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


# ---------------------------------------------------------------------------
# The register as committed
# ---------------------------------------------------------------------------

def test_every_source_has_terms_a_status_and_a_date():
    module = load_script()
    for source in read(ROOT / "sources" / "register.csv"):
        assert source["terms"].strip(), source["source_id"]
        assert source["status"] in module.STATUSES, source["source_id"]
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", source["checked_on"]), source["source_id"]
        assert source["doi"].startswith("10."), source["source_id"]


def test_every_file_belongs_to_a_source_and_has_a_proper_address():
    sources = {s["source_id"] for s in read(ROOT / "sources" / "register.csv")}
    files = read(ROOT / "sources" / "files.csv")
    targets = set()
    for row in files:
        assert row["source_id"] in sources, row["file_id"]
        assert (row["source_id"], row["target"]) not in targets, row["file_id"]
        targets.add((row["source_id"], row["target"]))
        if row["kind"] == "url":
            assert all(u.strip().startswith("https://") for u in row["location"].split("|")), row["file_id"]
        else:
            assert row["kind"] == "ncbi_assembly", row["file_id"]
            assert re.fullmatch(r"GC[AF]_\d{9}\.\d+", row["location"]), row["file_id"]
            assert row["strain"].startswith("Leaf"), row["file_id"]
        if row["pinned_sha256"]:
            assert re.fullmatch(r"[0-9a-f]{64}", row["pinned_sha256"]), row["file_id"]


# ---------------------------------------------------------------------------
# The fetcher, against a stand-in web server
# ---------------------------------------------------------------------------

GENOME = gzip.compress(b">contig_1\nACGTACGTGGCC\n", mtime=0)    # a real (tiny) .fna.gz
TABLE = b"PK\x03\x04 a stand-in for a journal's supplementary table"  # starts like an .xlsx
PAGE = b"<html><body>Please accept our cookies</body></html>"


@pytest.fixture
def site(tmp_path):
    """A tiny web server with an NCBI-like genome folder and a journal file."""
    web = tmp_path / "web"
    folder = web / "GCF" / "001" / "422" / "065" / "GCF_001422065.1_Leaf76"
    folder.mkdir(parents=True)
    (folder / "GCF_001422065.1_Leaf76_genomic.fna.gz").write_bytes(GENOME)
    md5 = hashlib.md5(GENOME).hexdigest()
    (folder / "md5checksums.txt").write_text(f"{md5}  ./GCF_001422065.1_Leaf76_genomic.fna.gz\n", encoding="utf-8")
    (web / "esm").mkdir()
    (web / "esm" / "tables.xlsx").write_bytes(TABLE)
    (web / "esm" / "page.xlsx").write_bytes(PAGE)      # a mirror that answers with a web page

    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(web))
    handler.log_message = lambda *args: None
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_address[1]}"
    server.shutdown()
    server.server_close()


@pytest.fixture
def fetch(tmp_path, site, monkeypatch):
    """The script, pointed at a temporary project and the stand-in server."""
    module = load_script()
    project = tmp_path / "project"
    (project / "sources").mkdir(parents=True)
    raw = project / "data" / "raw"
    monkeypatch.setattr(module, "PROJECT_ROOT", project)
    monkeypatch.setattr(module, "REGISTER_PATH", project / "sources" / "register.csv")
    monkeypatch.setattr(module, "FILES_PATH", project / "sources" / "files.csv")
    monkeypatch.setattr(module, "RAW_DIR", raw)
    monkeypatch.setattr(module, "SOURCES_DIR", raw / "sources")
    monkeypatch.setattr(module, "ARCHIVE_DIR", raw / "extracted")
    monkeypatch.setattr(module, "LOG_PATH", raw / "sources" / "fetch_log.json")
    monkeypatch.setattr(module, "NCBI_ALL", site)
    monkeypatch.setattr(module, "NCBI_PAUSE_SECONDS", 0)

    with open(module.REGISTER_PATH, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["source_id", "layer", "layer_name", "what_it_holds", "citation", "doi",
                         "where_from", "terms", "status", "checked_on", "notes"])
        writer.writerow(["genomes", "2", "Genomes", "genomes", "a paper", "10.1/x", "NCBI", "open",
                         "to fetch", "2026-10-12", ""])
        writer.writerow(["tables", "5", "Tables", "tables", "a paper", "10.1/y", "a journal", "terms",
                         "to fetch", "2026-10-12", ""])
    module.write_files = functools.partial(write_files, module)
    module.write_files([
        ["genome_Leaf76", "genomes", "ncbi_assembly", "GCF_001422065.1",
         "Leaf76_GCF_001422065.1_genomic.fna.gz", "", "", "", "Leaf76"],
        ["tables", "tables", "url",
         f"{site}/esm/missing.xlsx | {site}/esm/page.xlsx | {site}/esm/tables.xlsx",
         "tables.xlsx", "", "", "Data/tables_copy.xlsx", ""],
    ])
    return module


def write_files(module, rows):
    with open(module.FILES_PATH, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["file_id", "source_id", "kind", "location", "target", "published_md5",
                         "pinned_sha256", "same_as", "strain"])
        writer.writerows(rows)


def test_a_web_page_is_not_taken_for_the_file(tmp_path):
    module = load_script()
    page, table = tmp_path / "page.xlsx", tmp_path / "table.xlsx"
    page.write_bytes(PAGE)
    table.write_bytes(TABLE)
    assert not module.looks_like(page, "x.xlsx")
    assert module.looks_like(table, "x.xlsx")
    assert module.looks_like(page, "notes.txt")             # no rule for .txt


def test_ncbi_folder_layout():
    module = load_script()
    assert module.ncbi_folder_url("GCF_001422065.1").endswith("/GCF/001/422/065/")


def test_probe_reaches_every_file_and_downloads_nothing(fetch, capsys):
    assert fetch.main(["--probe"]) == 0
    out = capsys.readouterr().out
    assert "Leaf76" in out and "2 of 2 files reachable" in out
    assert not fetch.SOURCES_DIR.exists()


def test_fetch_checks_published_md5_tries_mirrors_and_logs(fetch, capsys):
    assert fetch.main([]) == 0
    out = capsys.readouterr().out
    assert "MD5 matches the publisher" in out              # the genome, against md5checksums.txt
    assert "new: SHA-256 not pinned yet" in out            # the table: first download
    assert "--pin" in out
    assert (fetch.SOURCES_DIR / "tables" / "tables.xlsx").read_bytes() == TABLE   # third mirror used
    assert not list(fetch.SOURCES_DIR.rglob("*.part"))     # the web page was thrown away
    log = fetch.read_log()
    assert log["tables"]["url"].endswith("/esm/tables.xlsx")
    assert log["genome_Leaf76"]["published_md5"] == hashlib.md5(GENOME).hexdigest()


def test_pinning_then_a_second_run_checks_without_downloading(fetch, capsys, monkeypatch):
    fetch.main([])
    assert fetch.main(["--pin"]) == 0
    rows = read(fetch.FILES_PATH)
    assert rows[1]["pinned_sha256"] == hashlib.sha256(TABLE).hexdigest()
    assert rows[0]["pinned_sha256"] == ""                   # published MD5 already covers the genome
    statuses = [s["status"] for s in read(fetch.REGISTER_PATH)]
    assert statuses == ["fetched", "fetched"]                # both sources complete
    first = fetch.read_log()["tables"]["downloaded_at_utc"]

    def no_download(*args, **kwargs):
        raise AssertionError("the script tried to download again")
    monkeypatch.setattr(fetch, "download", no_download)
    monkeypatch.setattr(fetch, "resolve_ncbi", no_download)
    capsys.readouterr()
    assert fetch.main([]) == 0
    out = capsys.readouterr().out
    assert "SHA-256 matches the pin" in out and "MD5 matches the publisher" in out
    assert "already here" in out
    assert fetch.read_log()["tables"]["downloaded_at_utc"] == first


def test_a_missing_file_makes_a_source_partly_fetched(fetch, capsys):
    fetch.write_files([
        ["genome_Leaf76", "genomes", "ncbi_assembly", "GCF_001422065.1",
         "Leaf76_GCF_001422065.1_genomic.fna.gz", "", "", "", "Leaf76"],
        ["genome_Leaf99", "genomes", "ncbi_assembly", "GCF_009999999.1",
         "Leaf99_GCF_009999999.1_genomic.fna.gz", "", "", "", "Leaf99"],
    ])
    assert fetch.main([]) == 1                               # Leaf99 isn't on the server
    assert "FAILED" in capsys.readouterr().out
    fetch.main(["--pin"])
    register = {s["source_id"]: s for s in read(fetch.REGISTER_PATH)}
    assert register["genomes"]["status"] == "partly fetched"
    assert register["tables"]["status"] == "to fetch"         # no files of its own in this list


def test_a_changed_file_is_moved_aside(fetch, capsys):
    fetch.main([])
    fetch.main(["--pin"])
    (fetch.SOURCES_DIR / "tables" / "tables.xlsx").write_bytes(b"someone changed this")
    assert fetch.main([]) == 1
    assert "MISMATCH with pinned SHA-256" in capsys.readouterr().out
    assert (fetch.SOURCES_DIR / "tables" / "tables.xlsx.rejected").exists()
    assert not (fetch.SOURCES_DIR / "tables" / "tables.xlsx").exists()


def test_cross_check_with_the_archive_copy(fetch, capsys):
    copy = fetch.ARCHIVE_DIR / "Data" / "tables_copy.xlsx"
    copy.parent.mkdir(parents=True)
    copy.write_bytes(TABLE)
    fetch.main([])
    assert "same bytes as the copy in the Phase 1 archive" in capsys.readouterr().out
    copy.write_bytes(b"a different file")
    fetch.main([])
    assert "DIFFERENT from the copy" in capsys.readouterr().out


def test_output_is_plain_and_shows_no_home_folder(fetch, capsys):
    fetch.main(["--list"])
    fetch.main([])
    fetch.main(["--pin"])
    out = capsys.readouterr().out
    assert "pinned in sources/files.csv" in out
    assert str(fetch.PROJECT_ROOT) not in out
    assert not any(char in out for char in LOOK_ALIKES)
    long = [line for line in out.splitlines() if len(line) > 80]
    assert not long, long


def test_a_workbook_saved_again_has_the_same_cells(fetch, tmp_path):
    """Different bytes, same values: what happens when a workbook is opened and
    saved again. Built by writing a workbook, then changing only its document
    properties (where the save time lives) inside the zip."""
    import zipfile
    import pandas as pd
    first = tmp_path / "first.xlsx"
    pd.DataFrame({"strain": ["Leaf15", "Leaf68"], "score": [0.9, 0.4]}).to_excel(first, index=False)
    second = tmp_path / "second.xlsx"
    with zipfile.ZipFile(first) as old, zipfile.ZipFile(second, "w") as new:
        for item in old.infolist():
            data = old.read(item.filename)
            if item.filename == "docProps/core.xml":
                data = data.replace(b"</cp:coreProperties>", b"<!-- saved again --></cp:coreProperties>")
            new.writestr(item, data)
    assert first.read_bytes() != second.read_bytes()
    assert fetch.same_cells(first, second) == 1
    different = tmp_path / "different.xlsx"
    pd.DataFrame({"strain": ["Leaf15", "Leaf68"], "score": [0.9, 0.5]}).to_excel(different, index=False)
    assert fetch.same_cells(first, different) == 0

    row = {"same_as": "Data/second.xlsx"}
    (fetch.ARCHIVE_DIR / "Data").mkdir(parents=True)
    second.replace(fetch.ARCHIVE_DIR / "Data" / "second.xlsx")
    message = fetch.cross_check(row, first, fetch.file_hashes(first)[1])
    assert "every cell of its one sheet holds the same value" in message
