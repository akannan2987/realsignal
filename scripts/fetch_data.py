"""
fetch_data.py — obtain the published dataset this project reproduces.

WHAT THIS SCRIPT DOES, IN ORDER
-------------------------------
  1. PROBE      Ask the archive how big the file is, without downloading it.
  2. DOWNLOAD   Fetch the archive once, showing progress.
  3. VERIFY     Compute its checksum and compare with the published one.
  4. EXTRACT    Unpack it safely into data/raw/extracted/.
  5. INVENTORY  Write a manifest of every file inside, so we know what we have.
  6. LOG        Record what happened, when, and from where (provenance).

WHY EACH STEP EXISTS
--------------------
  PROBE      A 239 MB download over a slow or metered connection deserves a
             warning first. "Look before you leap" is also a good habit with
             any external data source you do not control.
  VERIFY     A download can silently truncate or corrupt. A checksum turns
             "it seemed fine" into "it is provably the exact file the authors
             deposited". Analogy: the tamper-evident seal on a medicine
             bottle. It does not prove the medicine works; it proves nobody
             opened it on the way.
  EXTRACT    Done defensively — see `_is_safe_member` below for why a zip file
             from the internet is never unpacked blindly.
  INVENTORY  We do not yet know exactly which file inside holds which table.
             Rather than guess, we list everything and look. Phase 2 uses this
             manifest to find what it needs.
  LOG        In a year, "where did this data come from?" must have a written
             answer that does not rely on anyone's memory. That is called
             provenance, and it is the difference between a result and a
             rumour.

THE SOURCE
----------
  Emmenegger, B., Massoni, J., Pestalozzi, C. M., Bortfeld-Miller, M.,
  Maier, B. A., & Vorholt, J. A. (2023). Identifying microbiota community
  patterns important for plant protection using synthetic communities and
  machine learning. Nature Communications, 14, 7983.
  https://doi.org/10.1038/s41467-023-43793-z

  Data and original R code, deposited on Zenodo under CC-BY 4.0:
  https://doi.org/10.5281/zenodo.10118600

  The data is theirs. This project neither owns it nor redistributes it —
  the script downloads it from the original archive so that every user
  receives it from the source, with its licence and credit attached.

USAGE
-----
  python scripts/fetch_data.py --probe     # look, don't download
  python scripts/fetch_data.py             # download, verify, extract, inventory
  python scripts/fetch_data.py --force     # re-download even if already present
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
# CONFIGURATION
#
# These values are transcribed from the Zenodo record page listed above, on
# 2026-08-28. They are hard-coded deliberately: if the archive ever changes,
# the checksum comparison will FAIL LOUDLY rather than quietly analysing a
# different dataset than the one this project documents. A noisy failure you
# can investigate always beats a silent substitution you cannot.
#
# To re-check these yourself, open the Zenodo record in a browser: the file
# table shows the name, the size and the md5 next to the download button.
# ---------------------------------------------------------------------------

ZENODO_RECORD_ID = "10118600"
ZENODO_RECORD_URL = f"https://zenodo.org/records/{ZENODO_RECORD_ID}"
ARCHIVE_FILENAME = "Mini5SynCom_Repository.zip"
ARCHIVE_URL = (
    f"https://zenodo.org/records/{ZENODO_RECORD_ID}/files/{ARCHIVE_FILENAME}?download=1"
)
EXPECTED_MD5 = "f8061f230b621703f0f11be454c5167e"
APPROX_SIZE_MB = 239.2

# Where things go. Paths are built from this file's own location rather than
# from wherever the terminal happens to be, so the script works no matter which
# directory you run it from. `parents[1]` is the project root: scripts/ -> root.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
ARCHIVE_PATH = RAW_DIR / ARCHIVE_FILENAME
EXTRACT_DIR = RAW_DIR / "extracted"
MANIFEST_PATH = RAW_DIR / "manifest.csv"
FETCH_LOG_PATH = RAW_DIR / "fetch_log.json"

# How many bytes to read at a time. We never load 239 MB into memory at once:
# we stream it through in small pieces. 1 MiB is a good, unremarkable choice.
CHUNK_SIZE = 1024 * 1024

# Identify ourselves politely to the server. Anonymous automated traffic is
# often blocked, and saying who you are is simply good manners on someone
# else's infrastructure.
HEADERS = {
    "User-Agent": "RealSignal/0.1 (educational reproduction project; contact via GitHub)"
}


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------

def human_size(num_bytes: int) -> str:
    """Turn a byte count into something a person can read ('239.2 MB')."""
    size = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} GB"  # unreachable, but keeps every path returning a value


def banner(title: str) -> None:
    """Print a section header, so long output stays readable."""
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


# ---------------------------------------------------------------------------
# Step 1 — PROBE
# ---------------------------------------------------------------------------

def probe() -> None:
    """
    Ask the server about the file without downloading it.

    HOW: an HTTP HEAD request means "send me the headers, not the body" — the
    label on the parcel, not the parcel. The server replies with the size and
    type, costing a fraction of a second and almost no data.
    """
    banner("PROBE — what would be downloaded")
    print(f"Source record : {ZENODO_RECORD_URL}")
    print(f"File          : {ARCHIVE_FILENAME}")
    print(f"Published size: ~{APPROX_SIZE_MB} MB")
    print(f"Published MD5 : {EXPECTED_MD5}")
    print(f"Licence       : CC-BY 4.0 (reuse permitted with attribution)")
    print(f"Destination   : {ARCHIVE_PATH}")
    print()

    try:
        # allow_redirects=True because Zenodo forwards the request to wherever
        # the file is actually stored.
        response = requests.head(
            ARCHIVE_URL, headers=HEADERS, allow_redirects=True, timeout=30
        )
        response.raise_for_status()
        reported = response.headers.get("Content-Length")
        if reported:
            print(f"Server reports: {human_size(int(reported))}")
        else:
            print("Server did not report a size (this is normal for some hosts).")
        print("Reachable     : yes")
    except requests.RequestException as error:
        print(f"Could not reach the archive: {error}")
        print("Check your internet connection, then try again.")
        return

    if ARCHIVE_PATH.exists():
        print()
        print(f"NOTE: a copy already exists locally "
              f"({human_size(ARCHIVE_PATH.stat().st_size)}).")
        print("Running without --probe will verify it rather than re-download.")

    print()
    print("Nothing has been downloaded. To proceed:")
    print("    python scripts/fetch_data.py")


# ---------------------------------------------------------------------------
# Step 2 — DOWNLOAD
# ---------------------------------------------------------------------------

def download() -> None:
    """
    Download the archive, streaming it to disk with a progress indicator.

    WHY STREAM: `stream=True` tells requests not to pull the whole response
    into memory. We read a megabyte, write a megabyte, repeat. A 239 MB file
    then needs 239 MB of disk and about 1 MB of memory, instead of both.
    """
    banner("DOWNLOAD")
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    print(f"From: {ARCHIVE_URL}")
    print(f"To  : {ARCHIVE_PATH}")
    print("This is a large file. Expect several minutes on a typical connection.")
    print()

    # Download to a temporary name first, and rename only once complete.
    # WHY: if the connection drops halfway, we are left with a clearly-named
    # partial file rather than something that looks like a finished download.
    temp_path = ARCHIVE_PATH.with_suffix(ARCHIVE_PATH.suffix + ".part")

    with requests.get(ARCHIVE_URL, headers=HEADERS, stream=True, timeout=60) as response:
        response.raise_for_status()
        total = int(response.headers.get("Content-Length", 0))
        downloaded = 0

        with open(temp_path, "wb") as handle:
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                if not chunk:          # keep-alive chunks are empty; skip them
                    continue
                handle.write(chunk)
                downloaded += len(chunk)

                if total:
                    percent = downloaded / total * 100
                    bar_width = 40
                    filled = int(bar_width * downloaded / total)
                    bar = "#" * filled + "-" * (bar_width - filled)
                    # \r returns the cursor to the line start so the progress
                    # bar updates in place instead of printing 239 lines.
                    print(f"\r  [{bar}] {percent:5.1f}%  "
                          f"{human_size(downloaded)} / {human_size(total)}",
                          end="", flush=True)
                else:
                    print(f"\r  {human_size(downloaded)} downloaded",
                          end="", flush=True)

    print()  # end the progress line
    temp_path.replace(ARCHIVE_PATH)     # atomic rename: partial becomes final
    print(f"Download complete: {human_size(ARCHIVE_PATH.stat().st_size)}")


# ---------------------------------------------------------------------------
# Step 3 — VERIFY
# ---------------------------------------------------------------------------

def compute_md5(path: Path) -> str:
    """
    Compute a file's MD5 checksum.

    Read in chunks for the same reason we downloaded in chunks: a checksum of
    a 239 MB file should not require 239 MB of memory.

    NOTE ON MD5: it is not suitable for security (a determined attacker can
    construct collisions). It is entirely suitable for what we use it for —
    detecting accidental corruption and truncation — and it is what Zenodo
    publishes, so it is what we compare against.
    """
    digest = hashlib.md5()
    with open(path, "rb") as handle:
        while chunk := handle.read(CHUNK_SIZE):
            digest.update(chunk)
    return digest.hexdigest()


def verify() -> bool:
    """Compare the downloaded file's checksum with the published one."""
    banner("VERIFY — is this exactly the file the authors deposited?")
    print("Computing checksum (this takes a few seconds)...")

    actual = compute_md5(ARCHIVE_PATH)
    print(f"  Expected: {EXPECTED_MD5}")
    print(f"  Actual  : {actual}")
    print()

    if actual == EXPECTED_MD5:
        print("MATCH. This is provably the published archive, byte for byte.")
        return True

    print("MISMATCH — do not proceed with this file.")
    print()
    print("The most likely cause is an interrupted or corrupted download.")
    print("Delete the file and try again:")
    print(f"    (remove {ARCHIVE_PATH})")
    print("    python scripts/fetch_data.py")
    print()
    print("If it fails a second time with the same result, the archive itself")
    print("may have been updated by its authors. In that case, check the")
    print(f"record at {ZENODO_RECORD_URL} and note the discrepancy in the")
    print("project README — a changed source is a finding, not a nuisance.")
    return False


# ---------------------------------------------------------------------------
# Step 4 — EXTRACT
# ---------------------------------------------------------------------------

def _is_safe_member(member_name: str) -> bool:
    """
    Decide whether a file inside the zip is safe to write to disk.

    WHY THIS EXISTS: a zip file can contain entries with names like
    "../../.bashrc" or "/etc/passwd". Unpacked naively, those escape the folder
    you intended and overwrite files elsewhere on your machine. The attack is
    known as "zip slip". This archive is from a trusted scientific source and
    is certainly fine — but "it is probably fine" is not a security model, and
    the check costs two lines.

    Analogy: you would still glance inside a parcel from a known sender before
    emptying it over your desk.
    """
    path = Path(member_name)
    if path.is_absolute():
        return False
    return ".." not in path.parts


def extract() -> None:
    """Unpack the archive into data/raw/extracted/, skipping unsafe entries."""
    banner("EXTRACT")

    if EXTRACT_DIR.exists() and any(EXTRACT_DIR.iterdir()):
        print(f"Already extracted at {EXTRACT_DIR} — skipping.")
        print("(Delete that folder and re-run if you want a clean unpack.)")
        return

    EXTRACT_DIR.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(ARCHIVE_PATH) as archive:
        members = archive.namelist()
        safe = [name for name in members if _is_safe_member(name)]
        rejected = [name for name in members if not _is_safe_member(name)]

        if rejected:
            print(f"WARNING: skipped {len(rejected)} unsafe entries:")
            for name in rejected[:5]:
                print(f"    {name}")

        print(f"Unpacking {len(safe)} entries...")
        archive.extractall(path=EXTRACT_DIR, members=safe)

    print(f"Extracted to: {EXTRACT_DIR}")


# ---------------------------------------------------------------------------
# Step 5 — INVENTORY
# ---------------------------------------------------------------------------

def inventory() -> list[dict]:
    """
    Walk the extracted folder and record every file found.

    WHY: we deliberately do not assume what is inside. Guessing filenames is
    how scripts break silently on someone else's machine. Instead we look,
    write down what is actually there, and let the next phase work from that
    written record. This is also simply good practice with any dataset you did
    not create: find out what you have before deciding what to do with it.
    """
    banner("INVENTORY — what is actually inside")

    rows: list[dict] = []
    for path in sorted(EXTRACT_DIR.rglob("*")):
        if path.is_file():
            rows.append({
                "relative_path": str(path.relative_to(EXTRACT_DIR)),
                "extension": path.suffix.lower() or "(none)",
                "size_bytes": path.stat().st_size,
                "size_human": human_size(path.stat().st_size),
            })

    # Write the manifest so later phases (and other people) can read it.
    with open(MANIFEST_PATH, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["relative_path", "extension", "size_bytes", "size_human"],
        )
        writer.writeheader()
        writer.writerows(rows)

    # Summarise by file type — the fastest way to see the shape of an archive.
    by_extension: dict[str, list[dict]] = {}
    for row in rows:
        by_extension.setdefault(row["extension"], []).append(row)

    print(f"Total files: {len(rows)}")
    print()
    print(f"{'Type':<12} {'Count':>6} {'Total size':>12}")
    print("-" * 32)
    for extension, group in sorted(
        by_extension.items(), key=lambda item: -len(item[1])
    ):
        total = sum(row["size_bytes"] for row in group)
        print(f"{extension:<12} {len(group):>6} {human_size(total):>12}")

    # Show the data-bearing files, since those are what Phase 2 needs.
    data_extensions = {".csv", ".tsv", ".txt", ".xlsx", ".xls", ".rds", ".rdata"}
    data_files = [r for r in rows if r["extension"] in data_extensions]

    print()
    print(f"Likely data files ({len(data_files)} found):")
    print("-" * 70)
    for row in data_files[:30]:
        print(f"  {row['size_human']:>10}  {row['relative_path']}")
    if len(data_files) > 30:
        print(f"  ... and {len(data_files) - 30} more (see {MANIFEST_PATH.name})")

    print()
    print(f"Full manifest written to: {MANIFEST_PATH}")
    return rows


# ---------------------------------------------------------------------------
# Step 6 — LOG (provenance)
# ---------------------------------------------------------------------------

def write_fetch_log(file_count: int, checksum_ok: bool) -> None:
    """Record what was fetched, from where, and when."""
    log = {
        "fetched_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "source_record": ZENODO_RECORD_URL,
        "source_doi": "10.5281/zenodo.10118600",
        "paper_doi": "10.1038/s41467-023-43793-z",
        "licence": "CC-BY 4.0",
        "archive_filename": ARCHIVE_FILENAME,
        "archive_size_bytes": ARCHIVE_PATH.stat().st_size if ARCHIVE_PATH.exists() else None,
        "expected_md5": EXPECTED_MD5,
        "checksum_verified": checksum_ok,
        "files_extracted": file_count,
        "python_version": sys.version.split()[0],
    }
    with open(FETCH_LOG_PATH, "w", encoding="utf-8") as handle:
        json.dump(log, handle, indent=2)
    print(f"Provenance log written to: {FETCH_LOG_PATH}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Download and verify the published dataset RealSignal reproduces."
    )
    parser.add_argument(
        "--probe",
        action="store_true",
        help="report what would be downloaded, without downloading it",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="download again even if a verified copy already exists",
    )
    args = parser.parse_args()

    if args.probe:
        probe()
        return 0

    # IDEMPOTENCE: running this twice must not cost another 239 MB. If a copy
    # exists and passes its checksum, we keep it.
    if ARCHIVE_PATH.exists() and not args.force:
        print(f"Archive already present: {ARCHIVE_PATH}")
        print("Verifying it rather than downloading again "
              "(use --force to re-download).")
        if not verify():
            return 1
    else:
        try:
            download()
        except requests.RequestException as error:
            print(f"\nDownload failed: {error}")
            print("Check your connection and try again. Partial files ending")
            print("in .part can be safely deleted.")
            return 1
        if not verify():
            return 1

    extract()
    rows = inventory()
    write_fetch_log(file_count=len(rows), checksum_ok=True)

    banner("DONE")
    print("The published dataset is now on your machine, verified.")
    print()
    print("What you have:")
    print(f"  {ARCHIVE_PATH}      the archive, exactly as deposited — never edit this")
    print(f"  {EXTRACT_DIR}/      its contents, unpacked")
    print(f"  {MANIFEST_PATH}     a list of every file inside")
    print(f"  {FETCH_LOG_PATH}    where it came from and when")
    print()
    print("Next: docs/02-phase-1-data-acquisition.md, section 7 "
          "('Look at what you got').")
    return 0


if __name__ == "__main__":
    sys.exit(main())
