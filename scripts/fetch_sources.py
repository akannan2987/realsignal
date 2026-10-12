"""
scripts/fetch_sources.py: fetch the other published data layers, verified.

WHAT THIS SCRIPT DOES
---------------------
  --list     Print the source register (sources/register.csv): every source,
             what it holds, the terms it comes with, and its status.
  --probe    Check that every file in sources/files.csv can be reached,
             without downloading anything.
  (default)  Fetch every file once into data/raw/sources/<source>/. A download
             that does not start the way its kind of file always starts (a
             web page sent instead of a workbook) is thrown away and the next
             address is tried. Then check the file:
               1. against a checksum the publisher published (NCBI does, for
                  every genome file), or
               2. against the SHA-256 pinned in sources/files.csv after an
                  earlier download, or
               3. if neither exists yet, report its SHA-256 so it can be pinned.
             Where the same file also sits in the Phase 1 archive, compare the
             two copies: byte for byte, and for workbooks also cell by cell. Record everything in data/raw/sources/fetch_log.json.
  --pin      After a fetch, record what happened: write the SHA-256 of first
             downloads into sources/files.csv, so every later download is
             checked against it, and each source's status and date into
             sources/register.csv.

WHY EACH STEP EXISTS
--------------------
  The register     One table answers "what do we use, from where, under which
                   terms, and could we get it?", including for sources that
                   turn out to be unobtainable.
  Pinning          Journals publish no checksum for supplementary files. The
                   first verified download becomes the reference, so a file
                   that changes later is noticed instead of used.
  Cross-check      Two copies with the same bytes are the same file, whatever
                   their names say. Two workbooks can differ in their bytes
                   (saved again, at another time) and still hold the same data.

Run from the project folder, with the virtual environment active:

    python scripts/fetch_sources.py --list
    python scripts/fetch_sources.py --probe
    python scripts/fetch_sources.py
    python scripts/fetch_sources.py --pin

Explained in docs/03-phase-2-more-sources.md.

The small helpers (sizes, paths, banners) are the same as in
scripts/fetch_data.py. They move into src/realsignal/ in Phase 3, once a
third program needs them.
"""

import argparse
import csv
import datetime as dt
import hashlib
import json
import re
import sys
import textwrap
import time
from pathlib import Path

import requests

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REGISTER_PATH = PROJECT_ROOT / "sources" / "register.csv"
FILES_PATH = PROJECT_ROOT / "sources" / "files.csv"
RAW_DIR = PROJECT_ROOT / "data" / "raw"
SOURCES_DIR = RAW_DIR / "sources"
ARCHIVE_DIR = RAW_DIR / "extracted"            # what scripts/fetch_data.py unpacked
LOG_PATH = SOURCES_DIR / "fetch_log.json"

NCBI_ALL = "https://ftp.ncbi.nlm.nih.gov/genomes/all"
# NCBI allows scripts without a key 3 requests a second on its programming
# interface (E-utilities). The download site gets the same pace, to be polite.
NCBI_PAUSE_SECONDS = 0.4
CHUNK_SIZE = 1024 * 1024
# The first bytes every file of a kind starts with. An .xlsx workbook is a zip
# archive inside ("PK"), a .gz file starts with 1f 8b. A server that answers
# with a web page (a cookie notice, a "please log in") fails this test.
FIRST_BYTES = {".xlsx": b"PK\x03\x04", ".gz": b"\x1f\x8b"}
TIMEOUT_SECONDS = 60
HEADERS = {"User-Agent": "RealSignal/0.2 (open reproduction project; "
                         "https://github.com/akannan2987/realsignal)"}
STATUSES = {"fetched", "to fetch", "partly fetched", "not available"}


# ---------------------------------------------------------------------------
# Small helpers (the same as in scripts/fetch_data.py)
# ---------------------------------------------------------------------------

def human_size(num_bytes: float) -> str:
    """Decimal units (1 MB = 1,000,000 bytes), as the publishers' pages use."""
    for unit in ("B", "KB", "MB", "GB"):
        if num_bytes < 1000 or unit == "GB":
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1000
    return f"{num_bytes:.1f} GB"


def rel(path: Path) -> str:
    """A path as seen from the project folder, so output is the same on every computer."""
    try:
        return path.resolve().relative_to(PROJECT_ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def banner(title: str) -> None:
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


def file_hashes(path: Path) -> tuple[str, str]:
    """MD5 and SHA-256 of a file, read a megabyte at a time."""
    md5, sha256 = hashlib.md5(), hashlib.sha256()
    with open(path, "rb") as handle:
        for piece in iter(lambda: handle.read(CHUNK_SIZE), b""):
            md5.update(piece)
            sha256.update(piece)
    return md5.hexdigest(), sha256.hexdigest()


# ---------------------------------------------------------------------------
# The register and the file list
# ---------------------------------------------------------------------------

def read_csv(path: Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def read_register() -> list[dict]:
    return read_csv(REGISTER_PATH)


def read_files(only: str | None = None) -> list[dict]:
    rows = read_csv(FILES_PATH)
    return [r for r in rows if only is None or r["source_id"] == only]


def target_path(row: dict) -> Path:
    return SOURCES_DIR / row["source_id"] / row["target"]


def show_register() -> int:
    banner("SOURCE REGISTER: sources/register.csv")
    files = read_csv(FILES_PATH)
    for source in read_register():
        count = sum(1 for f in files if f["source_id"] == source["source_id"])
        where = (f"{count} {'file' if count == 1 else 'files'} in sources/files.csv" if count
                 else source["where_from"])
        print(f"Layer {source['layer']}: {source['layer_name']} ({source['source_id']})")
        for label, text in (("holds", source["what_it_holds"]),
                            ("from", f"{source['citation']}, doi:{source['doi']}"),
                            ("terms", source["terms"]),
                            ("status", f"{source['status']} (checked {source['checked_on']}); {where}")):
            # Wrapped to 78 characters, so no terminal breaks a line in the middle of a word.
            print(textwrap.fill(text, width=78, initial_indent=f"  {label:<7}: ",
                                subsequent_indent=" " * 11))
        print()
    return 0


# ---------------------------------------------------------------------------
# Finding where a file lives
# ---------------------------------------------------------------------------

def ncbi_folder_url(accession: str) -> str:
    """GCF_001422065.1 -> .../genomes/all/GCF/001/422/065/ (NCBI's folder layout)."""
    prefix, digits = accession.split("_")[0], accession.split("_")[1].split(".")[0]
    return f"{NCBI_ALL}/{prefix}/{digits[0:3]}/{digits[3:6]}/{digits[6:9]}/"


def resolve_ncbi(accession: str, session: requests.Session) -> tuple[str, str]:
    """The download address of an assembly's genome file, and the MD5 NCBI publishes for it.

    NCBI keeps each assembly in a folder named after the accession and the
    assembly's name (for example GCF_001422065.1_Leaf76). The folder holds the
    sequence file and md5checksums.txt, a list of every file's MD5."""
    listing_url = ncbi_folder_url(accession)
    listing = session.get(listing_url, headers=HEADERS, timeout=TIMEOUT_SECONDS)
    listing.raise_for_status()
    found = re.search(rf'href="({re.escape(accession)}_[^"/]+)/?"', listing.text)
    if not found:
        raise RuntimeError(f"no folder for {accession} at {listing_url}")
    folder = found.group(1)
    time.sleep(NCBI_PAUSE_SECONDS)
    sums = session.get(f"{listing_url}{folder}/md5checksums.txt", headers=HEADERS, timeout=TIMEOUT_SECONDS)
    sums.raise_for_status()
    name = f"{folder}_genomic.fna.gz"
    for line in sums.text.splitlines():
        parts = line.split()
        if len(parts) == 2 and parts[1].lstrip("./") == name:
            return f"{listing_url}{folder}/{name}", parts[0].lower()
    raise RuntimeError(f"{name} is not listed in md5checksums.txt")


def candidate_urls(row: dict) -> list[str]:
    """A 'url' row may list mirrors separated by ' | ', tried in order."""
    return [u.strip() for u in row["location"].split("|") if u.strip()]


# ---------------------------------------------------------------------------
# Probing, downloading, checking
# ---------------------------------------------------------------------------

def probe(rows: list[dict], session: requests.Session) -> int:
    banner("PROBE: can every file be reached?")
    problems = 0
    for row in rows:
        label = row["strain"] or row["file_id"]
        try:
            if row["kind"] == "ncbi_assembly":
                url, _ = resolve_ncbi(row["location"], session)
                time.sleep(NCBI_PAUSE_SECONDS)
                urls = [url]
            else:
                urls = candidate_urls(row)
            reached, status = None, None
            for url in urls:
                answer = ask_headers(url, session)
                status = answer.status_code
                if row["kind"] == "ncbi_assembly":
                    time.sleep(NCBI_PAUSE_SECONDS)          # a pause after every request to NCBI
                if answer.ok:
                    reached = answer
                    break
            if reached is None:
                raise RuntimeError(f"HTTP {status}")
            size = reached.headers.get("Content-Length")
            shown = human_size(int(size)) if size else "size unknown"
            print(f"  {label:<22} reachable   {shown:>10}")
        except (requests.RequestException, RuntimeError) as error:
            problems += 1
            print(f"  {label:<22} NOT REACHED  {error}")
    print()
    print(f"{len(rows) - problems} of {len(rows)} files reachable. Nothing has been downloaded.")
    return 1 if problems else 0


def ask_headers(url: str, session: requests.Session) -> requests.Response:
    """Ask for a file's details without its contents. Some servers refuse the
    short HEAD request; for those, start a normal download and stop at once."""
    answer = session.head(url, headers=HEADERS, timeout=TIMEOUT_SECONDS, allow_redirects=True)
    if answer.status_code in (403, 405):
        answer = session.get(url, headers=HEADERS, timeout=TIMEOUT_SECONDS, stream=True)
        answer.close()
    return answer


class NotTheFile(RuntimeError):
    """The server answered, but with something other than the file asked for."""


def looks_like(path: Path, name: str) -> bool:
    """True if the file starts the way files with this name's ending always do."""
    for ending, first in FIRST_BYTES.items():
        if name.endswith(ending):
            with open(path, "rb") as handle:
                return handle.read(len(first)) == first
    return True      # no rule for this kind of file


def download(url: str, destination: Path, session: requests.Session) -> None:
    """Stream to a .part file and rename it only when complete, as in Phase 1.
    A download that turns out to be a web page is thrown away."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    partial = destination.with_name(destination.name + ".part")
    with session.get(url, headers=HEADERS, timeout=TIMEOUT_SECONDS, stream=True) as answer:
        answer.raise_for_status()
        with open(partial, "wb") as handle:
            for piece in answer.iter_content(chunk_size=CHUNK_SIZE):
                handle.write(piece)
    if not looks_like(partial, destination.name):
        partial.unlink()
        raise NotTheFile("the server sent something else (a web page?)")
    partial.replace(destination)


def check(row: dict, path: Path, published_md5: str) -> tuple[str, str, str]:
    """Compare a file with the best reference there is. Returns (verdict, md5, sha256)."""
    md5, sha256 = file_hashes(path)
    if published_md5:
        return ("MD5 matches the publisher" if md5 == published_md5 else "MISMATCH with published MD5"), md5, sha256
    if row["pinned_sha256"]:
        return ("SHA-256 matches the pin" if sha256 == row["pinned_sha256"] else "MISMATCH with pinned SHA-256"), md5, sha256
    return "new: SHA-256 not pinned yet", md5, sha256


def fetch(rows: list[dict], session: requests.Session, force: bool) -> int:
    banner("FETCH: download once, then check")
    log = read_log()
    now = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    problems = 0
    current_source = None
    for row in rows:
        if row["source_id"] != current_source:
            current_source = row["source_id"]
            print(f"{current_source}:")
        label = row["strain"] or row["file_id"]
        path = target_path(row)
        earlier = log.get(row["file_id"], {})
        published = row["published_md5"].lower() or earlier.get("published_md5", "")
        url = earlier.get("url", "")
        downloaded = False
        try:
            if force or not path.exists():
                if row["kind"] == "ncbi_assembly":
                    url, published = resolve_ncbi(row["location"], session)
                    time.sleep(NCBI_PAUSE_SECONDS)
                    candidates = [url]
                else:
                    candidates = candidate_urls(row)
                failure = None
                for candidate in candidates:
                    try:
                        download(candidate, path, session)
                        url, downloaded = candidate, True
                        break
                    except (requests.RequestException, NotTheFile) as error:
                        failure = error
                    finally:
                        if row["kind"] == "ncbi_assembly":
                            time.sleep(NCBI_PAUSE_SECONDS)
                if not downloaded:
                    raise failure
        except (requests.RequestException, RuntimeError) as error:
            problems += 1
            print(f"  {label:<22} FAILED: {error}")
            continue

        verdict, md5, sha256 = check(row, path, published)
        action = "downloaded" if downloaded else "already here"
        print(f"  {label:<22} {human_size(path.stat().st_size):>10}  {action:<12} {verdict}")
        if verdict.startswith("MISMATCH"):
            problems += 1
            rejected = path.with_name(path.name + ".rejected")
            path.replace(rejected)
            print(f"    moved aside to {rel(rejected)}; don't use it")
            continue

        same = cross_check(row, path, sha256)
        if same:
            print(f"    {same}")
        log[row["file_id"]] = {
            "source_id": row["source_id"],
            "file": rel(path),
            "url": url,
            "size_bytes": path.stat().st_size,
            "published_md5": published,
            "md5": md5,
            "sha256": sha256,
            "checked_against": verdict,
            "downloaded_at_utc": now if downloaded else earlier.get("downloaded_at_utc", now),
            "last_verified_utc": now,
        }
    write_log(log)
    summarise(rows, log, problems)
    return 1 if problems else 0


def cross_check(row: dict, path: Path, sha256: str) -> str:
    """Compare with the same file inside the Phase 1 archive, if the register names one."""
    if not row["same_as"]:
        return ""
    other = ARCHIVE_DIR / row["same_as"]
    if not other.exists():
        return "cross-check skipped: the archive copy isn't here (run scripts/fetch_data.py)"
    if file_hashes(other)[1] == sha256:
        return "cross-check: same bytes as the copy in the Phase 1 archive"
    sheets = same_cells(path, other) if path.name.endswith(".xlsx") else 0
    if sheets:
        # A workbook opened and saved again keeps its values but not its bytes:
        # the save time, the folder and the selected cell are stored in it too.
        return ("cross-check: not the same bytes as the Phase 1 archive copy, but\n"
                f"    every cell of {'its one sheet' if sheets == 1 else f'all {sheets} sheets'}"
                " holds the same value")
    return "cross-check: DIFFERENT from the copy in the Phase 1 archive"


def same_cells(first: Path, second: Path) -> int:
    """The number of sheets if two workbooks hold the same values in every
    cell of every sheet, else 0 (also when either can't be read as a workbook)."""
    import pandas as pd     # only needed here, so only loaded here
    try:
        a = pd.read_excel(first, sheet_name=None, header=None)
        b = pd.read_excel(second, sheet_name=None, header=None)
    except Exception:       # not a workbook after all: treat as different
        return 0
    if list(a) != list(b) or not all(a[name].equals(b[name]) for name in a):
        return 0
    return len(a)


# ---------------------------------------------------------------------------
# The log and pinning
# ---------------------------------------------------------------------------

def read_log() -> dict:
    if LOG_PATH.exists():
        try:
            return json.loads(LOG_PATH.read_text(encoding="utf-8")).get("files", {})
        except (ValueError, OSError):
            return {}
    return {}


def write_log(files: dict) -> None:
    SOURCES_DIR.mkdir(parents=True, exist_ok=True)
    log = {"written_by": "scripts/fetch_sources.py",
           "register": "sources/register.csv",
           "python_version": sys.version.split()[0],
           "files": files}
    LOG_PATH.write_text(json.dumps(log, indent=2) + "\n", encoding="utf-8")


def summarise(rows: list[dict], log: dict, problems: int) -> None:
    banner("SUMMARY")
    verdicts = [log[r["file_id"]]["checked_against"] for r in rows if r["file_id"] in log]
    published = sum(v.startswith("MD5 matches") for v in verdicts)
    pinned = sum(v.startswith("SHA-256 matches") for v in verdicts)
    new = sum(v.startswith("new") for v in verdicts)
    total = sum(log[r["file_id"]]["size_bytes"] for r in rows if r["file_id"] in log)
    print(f"Files checked          : {len(verdicts)} of {len(rows)} ({human_size(total)})")
    print(f"Match a published MD5  : {published}")
    print(f"Match a pinned SHA-256 : {pinned}")
    print(f"New, not pinned yet    : {new}")
    print(f"Failed or mismatched   : {problems}")
    print(f"Provenance log written to {rel(LOG_PATH)}")
    stale = [s for s in read_register() if outcome(s, read_files(), log) not in ("", s["status"])]
    if new or stale:
        print()
        print("Record the new checksums and each source's status:")
        print("    python scripts/fetch_sources.py --pin")


def outcome(source: dict, files: list[dict], log: dict) -> str:
    """'fetched', 'partly fetched' or 'to fetch' for a source, from the files
    that are here and passed their check. Empty for a source with no files in
    sources/files.csv (Layer 1, which scripts/fetch_data.py fetches)."""
    mine = [f for f in files if f["source_id"] == source["source_id"]]
    if not mine:
        return ""
    good = sum(1 for f in mine if f["file_id"] in log and target_path(f).exists())
    if good == len(mine):
        return "fetched"
    return "partly fetched" if good else "to fetch"


def write_csv(path: Path, rows: list[dict]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def pin() -> int:
    """Record the outcome of a fetch in the two committed tables:
    the SHA-256 of first downloads in sources/files.csv, and each source's
    status (with today's date) in sources/register.csv."""
    banner("PIN: record the checksums and the status of each source")
    log = read_log()
    rows = read_csv(FILES_PATH)
    pinned = 0
    for row in rows:
        entry = log.get(row["file_id"])
        if entry and not row["pinned_sha256"] and not row["published_md5"] and entry["checked_against"].startswith("new"):
            row["pinned_sha256"] = entry["sha256"]
            pinned += 1
            print(f"  {row['file_id']}")
            print(f"    {entry['sha256']}")             # 64 characters: a line of its own
    if pinned:
        write_csv(FILES_PATH, rows)
    print(f"{pinned} {'checksum' if pinned == 1 else 'checksums'} pinned in sources/files.csv")

    # A status changes only when the outcome changed, so the date says when.
    register = read_register()
    today = dt.date.today().isoformat()
    changed = 0
    print()
    for source in register:
        now = outcome(source, rows, log)
        if now and now != source["status"]:
            print(f"  {source['source_id']:<24} {source['status']} -> {now}")
            source["status"], source["checked_on"] = now, today
            changed += 1
    if changed:
        write_csv(REGISTER_PATH, register)
    print(f"{changed} {'status' if changed == 1 else 'statuses'} updated in sources/register.csv")
    if pinned or changed:
        print()
        print("Commit the changed tables with the phase.")
    return 0


# ---------------------------------------------------------------------------
# Putting it together
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Fetch the other published data layers, verified.")
    parser.add_argument("--list", action="store_true", help="print the source register")
    parser.add_argument("--probe", action="store_true", help="check every file can be reached; download nothing")
    parser.add_argument("--pin", action="store_true", help="record the SHA-256 of first downloads")
    parser.add_argument("--force", action="store_true", help="download again even if a file is already here")
    parser.add_argument("--only", metavar="SOURCE_ID", help="work on one source from the register")
    args = parser.parse_args(argv)

    if args.list:
        return show_register()
    if args.pin:
        return pin()
    rows = read_files(args.only)
    if not rows:
        print(f"No files for '{args.only}'. Sources: "
              + ", ".join(r["source_id"] for r in read_register()))
        return 1
    with requests.Session() as session:
        if args.probe:
            return probe(rows, session)
        return fetch(rows, session, args.force)


if __name__ == "__main__":
    sys.exit(main())
