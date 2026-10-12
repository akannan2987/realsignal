"""
scripts/fetch_data.py: get the published dataset this project reproduces.

WHAT THIS SCRIPT DOES, IN ORDER
-------------------------------
  1. PROBE      Ask the archive how big the file is, without downloading it.
  2. DOWNLOAD   Fetch the archive once, showing progress.
  3. VERIFY     Compute its checksum and compare it with the published one.
  4. EXTRACT    Unpack it safely into data/raw/extracted/.
  5. INVENTORY  Write a manifest of every file inside, so we know what we have.
  6. LOG        Record what was fetched, from where and when (provenance).

WHY EACH STEP EXISTS
--------------------
  PROBE      A 239 MB download over a slow or metered connection deserves a
             warning first, and looking before you leap is a good habit with
             any data source you don't control.
  VERIFY     A download can be cut short or corrupted without any error. The
             checksum turns "it seemed fine" into "these are exactly the bytes
             the authors deposited". It proves the bytes are unchanged; it
             says nothing about whether the data in them is right.
  EXTRACT    Done defensively. See `_is_safe_member` below for why a zip file
             from the internet is never unpacked blindly.
  INVENTORY  I don't assume which file inside holds which table. The script
             lists everything and writes the list down; Phase 2 reads that
             list instead of guessing file names.
  LOG        A year from now, "where did this data come from?" needs a written
             answer that doesn't depend on anyone's memory.

THE SOURCE
----------
  Emmenegger, B., Massoni, J., Pestalozzi, C. M., Bortfeld-Miller, M.,
  Maier, B. A., & Vorholt, J. A. (2023). Identifying microbiota community
  patterns important for plant protection using synthetic communities and
  machine learning. Nature Communications, 14, 7983.
  https://doi.org/10.1038/s41467-023-43793-z

  Data and the original R code, deposited on Zenodo under CC-BY 4.0:
  https://doi.org/10.5281/zenodo.10118600

  The data belongs to its authors. This project doesn't redistribute it: the
  script downloads it from the original archive, so everyone receives it from
  the source with its licence and credit attached.

USAGE (from the project folder, with the virtual environment active)
-----
  python scripts/fetch_data.py --probe     # look, don't download
  python scripts/fetch_data.py             # download, verify, extract, inventory
  python scripts/fetch_data.py --force     # download again even if a copy exists

Explained step by step in docs/02-phase-1-data-acquisition.md.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import sys
import zipfile
from pathlib import Path

import requests

# ---------------------------------------------------------------------------
# What we download
#
# Copied from the Zenodo record page on 2026-08-28. They are written into the
# script on purpose: if the archive ever changes, the checksum comparison
# fails loudly instead of quietly analysing a different dataset from the one
# this project documents. A loud failure can be investigated; a silent swap
# can't.
#
# To check them yourself, open the record in a browser: the file table shows
# the name, the size and the md5 next to the download button.
# ---------------------------------------------------------------------------

ZENODO_RECORD_ID = "10118600"
ZENODO_RECORD_URL = f"https://zenodo.org/records/{ZENODO_RECORD_ID}"
ARCHIVE_FILENAME = "Mini5SynCom_Repository.zip"
ARCHIVE_URL = (
    f"https://zenodo.org/records/{ZENODO_RECORD_ID}/files/{ARCHIVE_FILENAME}?download=1"
)
EXPECTED_MD5 = "f8061f230b621703f0f11be454c5167e"
APPROX_SIZE_MB = 239.2

# Where things go. The paths are built from this file's own location, not from
# wherever the terminal happens to be, so the script works from any folder.
# parents[1] is the project folder (scripts/ -> project folder).
PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
ARCHIVE_PATH = RAW_DIR / ARCHIVE_FILENAME
EXTRACT_DIR = RAW_DIR / "extracted"
MANIFEST_PATH = RAW_DIR / "manifest.csv"
FETCH_LOG_PATH = RAW_DIR / "fetch_log.json"

# How much to read at a time. We never hold 239 MB in memory at once; the file
# streams through in 1 MiB pieces.
CHUNK_SIZE = 1024 * 1024

# Say who we are. Anonymous automated traffic is often blocked, and naming
# the program is good manners on someone else's server.
HEADERS = {
    "User-Agent": "RealSignal/0.1 (open reproduction project; https://github.com/akannan2987/realsignal)"
}

# File types that usually hold tables of data, and the ones that hold the
# authors' analysis code. Used only to sort the inventory into groups.
DATA_EXTENSIONS = {".csv", ".tsv", ".txt", ".xlsx", ".xls", ".rds", ".rdata", ".rda"}
CODE_EXTENSIONS = {".r", ".rmd", ".qmd"}

# Clutter that macOS adds when it builds a zip file (folder thumbnails and
# copies of file metadata). It isn't part of the dataset, so it isn't unpacked.
MAC_CLUTTER = ("__MACOSX/", ".DS_Store")


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------

def human_size(num_bytes: int) -> str:
    """Turn a byte count into something a person can read ('239.2 MB').

    Decimal units (1 MB = 1,000,000 bytes), the same ones the Zenodo record
    page and the macOS Finder use, so the sizes printed here match the
    published "239.2 MB". (Some programs divide by 1,024 instead, which is
    why the same file can look about 5 % smaller elsewhere.)"""
    size = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1000 or unit == "GB":
            return f"{size:.1f} {unit}"
        size /= 1000
    return f"{size:.1f} GB"


def rel(path: Path) -> str:
    """A path as seen from the project folder ('data/raw/manifest.csv').

    Printing paths this way keeps the output identical on every computer and
    never shows anyone's home folder."""
    try:
        return path.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return str(path)


def banner(title: str) -> None:
    """Print a section header, so long output stays readable."""
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


# ---------------------------------------------------------------------------
# Step 1: PROBE
# ---------------------------------------------------------------------------

def probe() -> int:
    """Ask the server about the file without downloading it.

    An HTTP HEAD request means "send me the headers, not the body": the label
    on the parcel, not the parcel. It takes a moment and almost no data."""
    banner("PROBE: what would be downloaded")
    print(f"Source record : {ZENODO_RECORD_URL}")
    print(f"File          : {ARCHIVE_FILENAME}")
    print(f"Published size: about {APPROX_SIZE_MB} MB")
    print(f"Published MD5 : {EXPECTED_MD5}")
    print("Licence       : CC-BY 4.0 (reuse allowed, with credit to the authors)")
    print(f"Destination   : {rel(ARCHIVE_PATH)}")
    print()

    try:
        # Zenodo forwards the request to wherever the file is stored, so
        # redirects must be followed.
        response = requests.head(ARCHIVE_URL, headers=HEADERS, allow_redirects=True, timeout=30)
        response.raise_for_status()
    except requests.RequestException as error:
        print(f"Could not reach the archive: {error}")
        print("Check the internet connection and try again (docs/02-phase-1-data-acquisition.md, mini-FAQ).")
        return 1

    reported = response.headers.get("Content-Length")
    if reported:
        print(f"Server reports: {human_size(int(reported))}")
    else:
        print("Server reports: no size given (normal for some hosts)")
    print("Reachable     : yes")

    if ARCHIVE_PATH.exists():
        print()
        print(f"A copy already exists here ({human_size(ARCHIVE_PATH.stat().st_size)}).")
        print("Running without --probe will check it instead of downloading again.")

    print()
    print("Nothing has been downloaded. To go ahead:")
    print("    python scripts/fetch_data.py")
    return 0


# ---------------------------------------------------------------------------
# Step 2: DOWNLOAD
# ---------------------------------------------------------------------------

def download() -> None:
    """Download the archive, streaming it to disk with a progress bar.

    stream=True tells requests not to pull the whole response into memory:
    read a piece, write a piece, repeat."""
    banner("DOWNLOAD")
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    print(f"From: {ARCHIVE_URL}")
    print(f"To  : {rel(ARCHIVE_PATH)}")
    print("This is a large file. Expect several minutes on a typical connection.")
    print()

    # Download under a temporary name and rename only when complete. If the
    # connection drops halfway, what's left is clearly an unfinished .part
    # file, never something that looks like a finished download.
    temp_path = ARCHIVE_PATH.with_name(ARCHIVE_PATH.name + ".part")

    with requests.get(ARCHIVE_URL, headers=HEADERS, stream=True, timeout=60) as response:
        response.raise_for_status()
        total = int(response.headers.get("Content-Length", 0))
        downloaded = 0
        with open(temp_path, "wb") as handle:
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                if not chunk:            # keep-alive pieces are empty; skip them
                    continue
                handle.write(chunk)
                downloaded += len(chunk)
                if total:
                    filled = int(40 * downloaded / total)
                    bar = "#" * filled + "-" * (40 - filled)
                    # \r returns to the start of the line, so the bar updates
                    # in place instead of printing hundreds of lines.
                    print(f"\r  [{bar}] {downloaded / total * 100:5.1f}%  "
                          f"{human_size(downloaded)} / {human_size(total)}", end="", flush=True)
                else:
                    print(f"\r  {human_size(downloaded)} downloaded", end="", flush=True)

    print()
    temp_path.replace(ARCHIVE_PATH)      # the finished file gets its real name in one step
    print(f"Download complete: {human_size(ARCHIVE_PATH.stat().st_size)}")


# ---------------------------------------------------------------------------
# Step 3: VERIFY
# ---------------------------------------------------------------------------

def compute_md5(path: Path) -> str:
    """The file's MD5 checksum, read in pieces so a large file needs little memory.

    MD5 isn't suitable for security (someone determined can build two files
    with the same MD5). It is fine for what we use it for, spotting an
    accidental cut-off or corruption, and it's what Zenodo publishes."""
    digest = hashlib.md5()
    with open(path, "rb") as handle:
        while chunk := handle.read(CHUNK_SIZE):
            digest.update(chunk)
    return digest.hexdigest()


def verify() -> bool:
    """Compare the downloaded file's checksum with the published one."""
    banner("VERIFY: is this exactly the file the authors deposited?")
    print("Computing the checksum (a few seconds)...")
    actual = compute_md5(ARCHIVE_PATH)
    print(f"  Expected: {EXPECTED_MD5}")
    print(f"  Actual  : {actual}")
    print()
    if actual == EXPECTED_MD5:
        print("MATCH. This is the published archive, byte for byte.")
        return True

    print("MISMATCH. Don't use this file.")
    print()
    print("The usual cause is a download that was cut short or corrupted.")
    print(f"Delete {rel(ARCHIVE_PATH)} and run the script again.")
    print("If a second clean download gives the same result, the authors may")
    print(f"have updated the archive: check {ZENODO_RECORD_URL} and write the")
    print("difference down in the README before going any further.")
    return False


# ---------------------------------------------------------------------------
# Step 4: EXTRACT
# ---------------------------------------------------------------------------

def _is_safe_member(member_name: str) -> bool:
    """Is this entry of the zip file safe to write to disk?

    A zip file can contain entries named like "../../.bashrc" or "/etc/hosts".
    Unpacked naively, they land outside the folder you meant and overwrite
    files elsewhere on the computer (the trick is called "zip slip"). This
    archive comes from a trusted scientific source, but checking costs two
    lines, and "probably fine" isn't a safety rule."""
    path = Path(member_name)
    if path.is_absolute() or member_name.startswith(("/", "\\")):
        return False
    return ".." not in Path(member_name.replace("\\", "/")).parts


def _is_mac_clutter(member_name: str) -> bool:
    """macOS bookkeeping files that ride along in zip files made on a Mac."""
    return member_name.startswith(MAC_CLUTTER[0]) or Path(member_name).name == MAC_CLUTTER[1]


def extract() -> dict:
    """Unpack the archive into data/raw/extracted/, skipping unsafe entries and Mac clutter."""
    banner("EXTRACT")
    if EXTRACT_DIR.exists() and any(EXTRACT_DIR.iterdir()):
        print(f"Already unpacked in {rel(EXTRACT_DIR)}/, skipping.")
        print("(Delete that folder and run the script again for a clean unpack.)")
        return {"skipped": True}

    EXTRACT_DIR.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(ARCHIVE_PATH) as archive:
        names = archive.namelist()
        unsafe = [n for n in names if not _is_safe_member(n)]
        clutter = [n for n in names if _is_safe_member(n) and _is_mac_clutter(n)]
        wanted = [n for n in names if _is_safe_member(n) and not _is_mac_clutter(n)]
        if unsafe:
            word = "entry was" if len(unsafe) == 1 else "entries were"
            print(f"WARNING: {len(unsafe)} unsafe {word} not unpacked:")
            for name in unsafe[:5]:
                print(f"    {name}")
        print(f"Entries in the archive : {len(names)}")
        print(f"macOS clutter skipped  : {len(clutter)}")
        print(f"Unpacking              : {len(wanted)}")
        archive.extractall(path=EXTRACT_DIR, members=wanted)
    print(f"Unpacked into {rel(EXTRACT_DIR)}/")
    return {"skipped": False, "entries": len(names), "clutter": len(clutter), "unsafe": len(unsafe)}


# ---------------------------------------------------------------------------
# Step 5: INVENTORY
# ---------------------------------------------------------------------------

def inventory() -> list[dict]:
    """List every unpacked file and write the list to data/raw/manifest.csv."""
    banner("INVENTORY: what is actually inside")
    rows = []
    for path in sorted(EXTRACT_DIR.rglob("*")):
        if path.is_file():
            size = path.stat().st_size
            rows.append({
                "relative_path": path.relative_to(EXTRACT_DIR).as_posix(),
                "extension": path.suffix.lower() or "(none)",
                "size_bytes": size,
                "size_human": human_size(size),
            })

    with open(MANIFEST_PATH, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["relative_path", "extension", "size_bytes", "size_human"])
        writer.writeheader()
        writer.writerows(rows)

    # The quickest way to see the shape of an unfamiliar archive: count files by type.
    by_type: dict[str, list[dict]] = {}
    for row in rows:
        by_type.setdefault(row["extension"], []).append(row)
    print(f"Files: {len(rows)}")
    print()
    print(f"{'Type':<12} {'Count':>6} {'Total size':>12}")
    print("-" * 32)
    for extension, group in sorted(by_type.items(), key=lambda item: (-len(item[1]), item[0])):
        print(f"{extension:<12} {len(group):>6} {human_size(sum(r['size_bytes'] for r in group)):>12}")

    for title, extensions in (("Likely data files", DATA_EXTENSIONS),
                              ("The authors' R code", CODE_EXTENSIONS)):
        group = [r for r in rows if r["extension"] in extensions]
        print()
        print(f"{title} ({len(group)}):")
        print("-" * 70)
        for row in group[:25]:
            print(f"  {row['size_human']:>10}  {row['relative_path']}")
        if len(group) > 25:
            print(f"  ... and {len(group) - 25} more (all of them are in {rel(MANIFEST_PATH)})")

    print()
    print(f"Full list written to {rel(MANIFEST_PATH)}")
    return rows


# ---------------------------------------------------------------------------
# Step 6: LOG (provenance)
# ---------------------------------------------------------------------------

def write_fetch_log(rows: list[dict], unpacked: dict, downloaded: bool) -> None:
    """Record what was fetched, from where and when, in data/raw/fetch_log.json.

    The download date is kept when a later run only checks the archive, so the
    log always says when these bytes arrived as well as when they were last
    verified."""
    now = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    earlier = {}
    if FETCH_LOG_PATH.exists():
        try:
            earlier = json.loads(FETCH_LOG_PATH.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            earlier = {}                 # an unreadable log gets rewritten
    downloaded_at = now if downloaded else earlier.get("downloaded_at_utc", now)
    # A run that skips unpacking doesn't count the clutter again, so the
    # numbers from the run that unpacked are kept.
    if unpacked.get("skipped"):
        unpacked = {"clutter": earlier.get("mac_clutter_skipped"),
                    "unsafe": earlier.get("unsafe_entries_skipped")}
    log = {
        "downloaded_at_utc": downloaded_at,
        "last_verified_utc": now,
        "source_record": ZENODO_RECORD_URL,
        "source_doi": "10.5281/zenodo.10118600",
        "paper_doi": "10.1038/s41467-023-43793-z",
        "licence": "CC-BY 4.0",
        "archive_filename": ARCHIVE_FILENAME,
        "archive_size_bytes": ARCHIVE_PATH.stat().st_size,
        "expected_md5": EXPECTED_MD5,
        "checksum_verified": True,
        "files_in_manifest": len(rows),
        "mac_clutter_skipped": unpacked.get("clutter"),
        "unsafe_entries_skipped": unpacked.get("unsafe"),
        "python_version": sys.version.split()[0],
        "written_by": "scripts/fetch_data.py",
    }
    FETCH_LOG_PATH.write_text(json.dumps(log, indent=2) + "\n", encoding="utf-8")
    print(f"Provenance log written to {rel(FETCH_LOG_PATH)}")


# ---------------------------------------------------------------------------
# Putting it together
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Download and verify the published dataset that RealSignal reproduces.")
    parser.add_argument("--probe", action="store_true",
                        help="report what would be downloaded, without downloading it")
    parser.add_argument("--force", action="store_true",
                        help="download again even if a verified copy already exists")
    args = parser.parse_args(argv)

    if args.probe:
        return probe()

    # Running the script twice must not cost another 239 MB: a copy that
    # passes its checksum is kept. (Safe to repeat is called "idempotent".)
    downloaded = False
    if ARCHIVE_PATH.exists() and not args.force:
        print(f"The archive is already here: {rel(ARCHIVE_PATH)}")
        print("Checking it instead of downloading again (add --force to download anyway).")
    else:
        try:
            download()
            downloaded = True
        except requests.RequestException as error:
            print()
            print(f"Download failed: {error}")
            print("Check the connection and try again. A leftover .part file can be deleted.")
            return 1
    if not verify():
        return 1

    unpacked = extract()
    rows = inventory()
    write_fetch_log(rows, unpacked, downloaded)

    banner("DONE")
    print("The published dataset is on this computer, verified.")
    print()
    # Kept under 80 characters a line, so no terminal wraps them.
    print(f"  {rel(ARCHIVE_PATH):<37} the archive (never edit it)")
    print(f"  {rel(EXTRACT_DIR) + '/':<37} its contents, unpacked")
    print(f"  {rel(MANIFEST_PATH):<37} a list of every file inside")
    print(f"  {rel(FETCH_LOG_PATH):<37} where it came from, and when")
    print()
    print("Next: docs/02-phase-1-data-acquisition.md, section 8 (look at what you got).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
