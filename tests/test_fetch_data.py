"""
tests/test_fetch_data.py: checks for scripts/fetch_data.py that need no internet.

The real archive is 239 MB and lives on Zenodo. These tests build a tiny
stand-in archive in a temporary folder instead, so they run in a second on any
computer, offline. They check the parts that protect us: the zip-slip guard,
the checksum, the unpacking, the inventory, and that a second run checks the
existing copy instead of downloading again.

Run from the project folder:  pytest -q
"""

import hashlib
import importlib.util
import json
import zipfile
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "fetch_data.py"
LOOK_ALIKES = ("\u2014", "\u2013", "\u201c", "\u201d")   # long dashes and curly quotes, as escape codes


def load_script():
    """Import scripts/fetch_data.py as a module (scripts/ isn't a package)."""
    spec = importlib.util.spec_from_file_location("fetch_data", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def fetch(tmp_path, monkeypatch):
    """The script, with every path pointed at a temporary project folder."""
    module = load_script()
    raw = tmp_path / "data" / "raw"
    raw.mkdir(parents=True)
    monkeypatch.setattr(module, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(module, "RAW_DIR", raw)
    monkeypatch.setattr(module, "ARCHIVE_PATH", raw / module.ARCHIVE_FILENAME)
    monkeypatch.setattr(module, "EXTRACT_DIR", raw / "extracted")
    monkeypatch.setattr(module, "MANIFEST_PATH", raw / "manifest.csv")
    monkeypatch.setattr(module, "FETCH_LOG_PATH", raw / "fetch_log.json")
    return module


def make_archive(path: Path) -> None:
    """A small zip shaped like a real research deposit, with two traps in it."""
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("Repository/Data/composition.csv", "syncom,strain\nMix1,Leaf15\n")
        archive.writestr("Repository/Data/outcomes.xlsx", b"not really excel")
        archive.writestr("Repository/Scripts/analysis.R", "# R code\n")
        archive.writestr("__MACOSX/Repository/Data/._composition.csv", b"mac metadata")
        archive.writestr("Repository/.DS_Store", b"mac folder settings")
        archive.writestr("../escaped.txt", "a file trying to land outside the folder")


def test_sizes_read_like_a_person_would_say_them(fetch):
    # Decimal units, as on the Zenodo record page (1 MB = 1,000,000 bytes).
    assert fetch.human_size(0) == "0.0 B"
    assert fetch.human_size(1500) == "1.5 KB"
    assert fetch.human_size(239_200_000) == "239.2 MB"
    assert fetch.human_size(2_500_000_000) == "2.5 GB"


def test_zip_slip_entries_are_refused(fetch):
    assert not fetch._is_safe_member("../escaped.txt")
    assert not fetch._is_safe_member("folder/../../escaped.txt")
    assert not fetch._is_safe_member("/etc/hosts")
    assert not fetch._is_safe_member("..\\escaped.txt")
    assert fetch._is_safe_member("Repository/Data/composition.csv")
    assert fetch._is_safe_member("Repository/..hidden_but_harmless")


def test_mac_clutter_is_recognised(fetch):
    assert fetch._is_mac_clutter("__MACOSX/Repository/._file.csv")
    assert fetch._is_mac_clutter("Repository/.DS_Store")
    assert not fetch._is_mac_clutter("Repository/Data/composition.csv")


def test_the_checksum_is_the_standard_md5(fetch, tmp_path):
    sample = tmp_path / "sample.bin"
    sample.write_bytes(b"RealSignal" * 100_000)
    assert fetch.compute_md5(sample) == hashlib.md5(sample.read_bytes()).hexdigest()


def test_unpacking_skips_traps_and_clutter(fetch, tmp_path):
    make_archive(fetch.ARCHIVE_PATH)
    counts = fetch.extract()
    assert counts == {"skipped": False, "entries": 6, "clutter": 2, "unsafe": 1}
    assert (fetch.EXTRACT_DIR / "Repository/Data/composition.csv").exists()
    assert not (fetch.EXTRACT_DIR / "__MACOSX").exists()
    assert not (tmp_path / "data" / "escaped.txt").exists()
    assert not (fetch.RAW_DIR / "escaped.txt").exists()


def test_the_inventory_lists_every_unpacked_file(fetch):
    make_archive(fetch.ARCHIVE_PATH)
    fetch.extract()
    rows = fetch.inventory()
    paths = sorted(r["relative_path"] for r in rows)
    assert paths == ["Repository/Data/composition.csv", "Repository/Data/outcomes.xlsx",
                     "Repository/Scripts/analysis.R"]
    header = fetch.MANIFEST_PATH.read_text(encoding="utf-8").splitlines()[0]
    assert header == "relative_path,extension,size_bytes,size_human"


def test_a_second_run_checks_the_copy_instead_of_downloading(fetch, monkeypatch, capsys):
    make_archive(fetch.ARCHIVE_PATH)
    monkeypatch.setattr(fetch, "EXPECTED_MD5", fetch.compute_md5(fetch.ARCHIVE_PATH))

    def no_download():
        raise AssertionError("the script tried to download again")
    monkeypatch.setattr(fetch, "download", no_download)

    # A log from the (pretend) first download, which a check must not overwrite.
    fetch.RAW_DIR.mkdir(parents=True, exist_ok=True)
    fetch.FETCH_LOG_PATH.write_text('{"downloaded_at_utc": "2026-01-01T00:00:00+00:00", '
                                    '"mac_clutter_skipped": 2, "unsafe_entries_skipped": 1}', encoding="utf-8")
    fetch.EXTRACT_DIR.mkdir(parents=True)
    (fetch.EXTRACT_DIR / "already-unpacked.txt").write_text("x", encoding="utf-8")

    assert fetch.main([]) == 0
    out = capsys.readouterr().out
    assert "already here: data/raw/Mini5SynCom_Repository.zip" in out
    assert "MATCH." in out
    log = json.loads(fetch.FETCH_LOG_PATH.read_text(encoding="utf-8"))
    assert log["checksum_verified"] is True
    assert log["files_in_manifest"] == 1            # the one file already unpacked
    assert "Already unpacked" in out
    assert log["mac_clutter_skipped"] == 2          # kept from the run that unpacked
    assert log["unsafe_entries_skipped"] == 1
    assert log["downloaded_at_utc"] == "2026-01-01T00:00:00+00:00"
    assert log["last_verified_utc"] > log["downloaded_at_utc"]


def test_a_wrong_checksum_stops_before_unpacking(fetch, monkeypatch, capsys):
    make_archive(fetch.ARCHIVE_PATH)
    monkeypatch.setattr(fetch, "EXPECTED_MD5", "0" * 32)
    assert fetch.main([]) == 1
    assert "MISMATCH" in capsys.readouterr().out
    assert not fetch.EXTRACT_DIR.exists()


def test_output_shows_project_paths_and_plain_characters(fetch, monkeypatch, capsys):
    make_archive(fetch.ARCHIVE_PATH)
    monkeypatch.setattr(fetch, "EXPECTED_MD5", fetch.compute_md5(fetch.ARCHIVE_PATH))
    fetch.main([])
    out = capsys.readouterr().out
    assert str(fetch.PROJECT_ROOT) not in out          # no home folders in the output
    assert not any(ch in out for ch in LOOK_ALIKES)     # safe to paste anywhere
