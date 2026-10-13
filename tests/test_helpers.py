"""
tests/test_helpers.py: the shared helpers in src/realsignal/helpers.py.

Three scripts rely on these (scripts/fetch_data.py, scripts/fetch_sources.py
and scripts/load_raw.py), so they're tested once, here. pytest finds the
package because pytest.ini adds src/ to the places Python looks.

Run from the project folder:  pytest -q
"""

import hashlib

from realsignal import helpers


def test_human_size_uses_decimal_units():
    assert helpers.human_size(0) == "0.0 B"
    assert helpers.human_size(1500) == "1.5 KB"
    assert helpers.human_size(48_500_000) == "48.5 MB"
    assert helpers.human_size(2_500_000_000) == "2.5 GB"


def test_rel_shows_paths_from_the_project_folder(tmp_path):
    inside = tmp_path / "data" / "raw" / "manifest.csv"
    assert helpers.rel(inside, tmp_path) == "data/raw/manifest.csv"
    outside = tmp_path.parent / "elsewhere.txt"
    assert helpers.rel(outside, tmp_path) == outside.as_posix()      # left as it is


def test_banner_is_plain_and_fits_80_columns(capsys):
    helpers.banner("LOAD: a title")
    lines = capsys.readouterr().out.splitlines()
    assert lines == ["", "=" * 70, "LOAD: a title", "=" * 70]


def test_file_hashes_match_hashlib(tmp_path):
    path = tmp_path / "file.bin"
    content = b"RealSignal " * 200_000            # about 2 MB: more than one piece
    path.write_bytes(content)
    md5, sha256 = helpers.file_hashes(path)
    assert md5 == hashlib.md5(content).hexdigest()
    assert sha256 == hashlib.sha256(content).hexdigest()


def test_csv_rows_round_trip_with_plain_line_endings(tmp_path):
    path = tmp_path / "table.csv"
    rows = [{"source_id": "a", "notes": "with, a comma"}, {"source_id": "b", "notes": ""}]
    helpers.write_csv_rows(path, rows)
    assert helpers.read_csv_rows(path) == rows
    assert b"\r\n" not in path.read_bytes()          # LF only, on every system
    assert b'"with, a comma"' in path.read_bytes()   # quoted, so the comma stays in its cell
