"""
src/realsignal/helpers.py: small helpers that several programs share.

Phases 1 and 2 each carried their own copy of these (sizes, paths, banners,
checksums, reading and writing CSV tables). Phase 3 adds a third program that
needs them, scripts/load_raw.py, so they live here now, once, with tests in
tests/test_helpers.py.

A script imports them like this (the scripts/ folder isn't a package, so each
script first tells Python where to find src/realsignal/):

    sys.path.insert(0, str(PROJECT_ROOT / "src"))
    from realsignal import helpers

Explained in docs/04-phase-3-harmonisation.md, section 4.
"""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path

# How much of a file to read at a time when calculating a checksum. Large
# files stream through in 1 MiB pieces instead of being held in memory.
CHUNK_SIZE = 1024 * 1024


def human_size(num_bytes: float) -> str:
    """A byte count a person can read: 239154876 -> '239.2 MB'.

    Decimal units (1 MB = 1,000,000 bytes), the ones the Zenodo record page,
    NCBI and the macOS Finder use, so the sizes printed here match theirs.
    (Some programs divide by 1,024 instead, which is why the same file can
    look about 5 % smaller elsewhere.)"""
    size = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1000 or unit == "GB":
            return f"{size:.1f} {unit}"
        size /= 1000
    return f"{size:.1f} GB"


def rel(path: Path, root: Path) -> str:
    """A path as seen from the project folder: 'data/raw/manifest.csv'.

    Printing paths this way keeps the output the same on every computer and
    never shows anyone's home folder. The project folder is passed in, so a
    test can point a script at a stand-in folder."""
    try:
        return Path(path).resolve().relative_to(Path(root).resolve()).as_posix()
    except ValueError:
        return Path(path).as_posix()


def banner(title: str) -> None:
    """A section header, so long output stays readable."""
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


def file_hashes(path: Path) -> tuple[str, str]:
    """The MD5 and SHA-256 checksums of a file, read a megabyte at a time.

    MD5 is what Zenodo and NCBI publish; SHA-256 is what this project pins
    (docs/03-phase-2-more-sources.md, section 3, says why both)."""
    md5, sha256 = hashlib.md5(), hashlib.sha256()
    with open(path, "rb") as handle:
        for piece in iter(lambda: handle.read(CHUNK_SIZE), b""):
            md5.update(piece)
            sha256.update(piece)
    return md5.hexdigest(), sha256.hexdigest()


def read_csv_rows(path: Path) -> list[dict]:
    """Every row of a CSV table, as dictionaries keyed by the column names."""
    with open(path, newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv_rows(path: Path, rows: list[dict]) -> None:
    """Write rows back with the same columns, one line each, LF line endings.

    The fixed line ending keeps `git diff` quiet on Windows, where a program
    would otherwise write CRLF and every line would look changed."""
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
