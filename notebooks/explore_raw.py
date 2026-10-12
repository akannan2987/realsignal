"""
notebooks/explore_raw.py: a first look at what the downloaded archive contains.

It reads data/raw/manifest.csv, the list of files that scripts/fetch_data.py
wrote, and summarises it four ways: files by type, files per folder, the files
that probably hold data, and the authors' own R code.

Never assume the shape of data you didn't create. This script is how Phase 1
finds out what is actually there, so Phase 2 can read files by their real
names instead of guessed ones.

Run from the project folder, with the virtual environment active:

    python notebooks/explore_raw.py

Explained in docs/02-phase-1-data-acquisition.md, section 8.
"""

import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST = PROJECT_ROOT / "data" / "raw" / "manifest.csv"

# The same groups scripts/fetch_data.py uses. R projects also keep data in
# R's own formats (.rds, .rdata, .rda), which Phase 6 reads.
DATA_EXTENSIONS = [".csv", ".tsv", ".txt", ".xlsx", ".xls", ".rds", ".rdata", ".rda"]
CODE_EXTENSIONS = [".r", ".rmd", ".qmd"]


def human_size(num_bytes: float) -> str:
    """Decimal units (1 MB = 1,000,000 bytes), as scripts/fetch_data.py prints them."""
    for unit in ("B", "KB", "MB", "GB"):
        if num_bytes < 1000 or unit == "GB":
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1000
    return f"{num_bytes:.1f} GB"


def folder_of(path: str, levels: int = 2) -> str:
    """The first one or two folders of a path ('Output/MachineLearning')."""
    folders = path.split("/")[:-1]          # leave out the file name itself
    return "/".join(folders[:levels]) if folders else "(top level)"


def show_files(rows: pd.DataFrame) -> None:
    """Print size and path, one file per line, sizes lined up on the right."""
    for size, path in zip(rows["size_human"], rows["relative_path"]):
        print(f"  {size:>10}  {path}")


if not MANIFEST.exists():
    print("data/raw/manifest.csv doesn't exist yet.")
    print("Run the download first:  python scripts/fetch_data.py")
    sys.exit(1)

manifest = pd.read_csv(MANIFEST)
print(f"Files in the archive : {len(manifest)}")
print(f"Total size unpacked  : {human_size(manifest['size_bytes'].sum())}")
print()

# Grouping by file type is the quickest way to understand an unfamiliar folder.
print("Files by type:")
by_type = (manifest.groupby("extension")
           .agg(files=("relative_path", "size"), size=("size_bytes", "sum"))
           .sort_values(["files", "size"], ascending=False))
for extension, row in by_type.iterrows():
    print(f"  {extension:<14}{row['files']:>5}  {human_size(row['size']):>10}")
print()

# Where do the files sit? The first two folder levels show how the authors
# organised their deposit: what they started from, and what their code wrote.
print("Files per folder (first two levels):")
counts = manifest["relative_path"].map(folder_of).value_counts()
for folder, count in counts.items():
    print(f"  {folder:<44}{count:>5}")
print()

# Data files, split by where they sit: Data/ holds what the authors started
# from; Output/ holds what their code produced (results, tables, saved models).
data = manifest[manifest["extension"].isin(DATA_EXTENSIONS)]
inputs = data[data["relative_path"].str.startswith("Data/")]
outputs = data[data["relative_path"].str.startswith("Output/")]
other = data.drop(inputs.index).drop(outputs.index)

print(f"Files that probably hold data: {len(data)}")
print(f"  in Data/, what the authors started from ({len(inputs)}):")
show_files(inputs)
print(f"  in Output/, what the authors' code wrote: {len(outputs)} files")
print("  (results, tables and saved models; all listed in data/raw/manifest.csv)")
if len(other):
    print(f"  elsewhere ({len(other)}):")
    show_files(other)
print()

# The authors' analysis code. Phase 6 runs it, so the rebuild can be checked
# against what they actually ran. (Phase 5 is written before opening it.)
code = manifest[manifest["extension"].isin(CODE_EXTENSIONS)]
print(f"The authors' R code ({len(code)} {'file' if len(code) == 1 else 'files'}):")
if len(code):
    show_files(code)
else:
    print("  none")
