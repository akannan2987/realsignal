"""
scripts/check_env.py: prove that this computer is set up correctly for RealSignal.

WHY THIS FILE EXISTS
--------------------
An installation that "seemed to work" isn't the same as one that does. This
script imports every package the project needs and prints one clear verdict,
so a problem shows up now, in ten seconds, with a short list of likely causes,
instead of three weeks from now in the middle of an analysis, where it would
look like a bug in your own code.

Run it from the project folder, with the virtual environment active:

    python scripts/check_env.py

Explained in docs/01-setup.md ("Verify everything works").
"""

import importlib
import importlib.metadata
import platform
import sys
from pathlib import Path

# The project folder: this file lives in scripts/, one level below it.
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# The oldest Python this project supports. Some of the packages below no
# longer support anything older than 3.11.
REQUIRED_PYTHON = (3, 11)

# Every package the project needs: the name used in `import`, then the name
# pip installs it under (not always the same: you install scikit-learn and
# import sklearn) and what it's for. The version shown is the one pip
# recorded, read with importlib.metadata.
REQUIRED_PACKAGES = {
    "pandas": ("pandas", "tables of data"),
    "numpy": ("numpy", "fast arithmetic"),
    "openpyxl": ("openpyxl", "reading Excel files"),
    "duckdb": ("duckdb", "the local SQL database"),
    "dbt.cli.main": ("dbt-core", "the harmonisation pipeline"),
    "dbt.adapters.duckdb": ("dbt-duckdb", "lets dbt work with DuckDB"),
    "sklearn": ("scikit-learn", "machine learning"),
    "scipy": ("scipy", "statistics"),
    "matplotlib": ("matplotlib", "charts"),
    "requests": ("requests", "downloading the dataset"),
    "streamlit": ("streamlit", "the interactive app"),
    "pytest": ("pytest", "automated tests"),
}


def check_python_version() -> bool:
    """Is the running Python new enough?"""
    actual = sys.version_info[:2]
    ok = actual >= REQUIRED_PYTHON
    print(f"[{'OK  ' if ok else 'FAIL'}] Python {actual[0]}.{actual[1]} "
          f"(need {REQUIRED_PYTHON[0]}.{REQUIRED_PYTHON[1]} or newer)")
    return ok


def check_virtual_environment() -> bool:
    """Are we running inside a virtual environment?

    When one is active, Python's sys.prefix points at the environment's folder
    while sys.base_prefix still points at the Python it was made from. If the
    two are the same, no environment is active."""
    inside = sys.prefix != sys.base_prefix
    status = "active" if inside else "NOT ACTIVE (see docs/01-setup.md, 'Activate it')"
    print(f"[{'OK  ' if inside else 'WARN'}] Virtual environment: {status}")
    # Show the Python program's path from the project folder when it lives
    # there (.venv/bin/python3), so the output is the same on every computer.
    program = Path(sys.executable)
    try:
        program = program.relative_to(PROJECT_ROOT)
    except ValueError:
        pass
    print(f"       Python program in use: {program.as_posix() if not program.is_absolute() else program}")
    return inside


def check_packages() -> list[str]:
    """Try to import each required package; return the ones that failed."""
    missing = []
    for module_name, (pip_name, purpose) in REQUIRED_PACKAGES.items():
        try:
            importlib.import_module(module_name)
            version = importlib.metadata.version(pip_name)
            print(f"[OK  ] {pip_name:<13}{version:<10}  {purpose}")
        except (ImportError, importlib.metadata.PackageNotFoundError):
            print(f"[FAIL] {pip_name:<13}{'MISSING':<10}  {purpose}")
            missing.append(pip_name)
    return missing


def main() -> int:
    """Run every check and print one verdict."""
    print("=" * 68)
    print("RealSignal: environment check")
    print("=" * 68)
    print(f"Operating system: {platform.system()} {platform.release()}")
    print("-" * 68)
    python_ok = check_python_version()
    venv_ok = check_virtual_environment()
    print("-" * 68)
    missing = check_packages()
    print("=" * 68)

    if python_ok and venv_ok and not missing:
        print("ALL CHECKS PASSED. Your workshop is ready.")
        print("Next: docs/HANDBOOK.md, the stage after the one you are on.")
        return 0

    print("SOMETHING NEEDS ATTENTION:")
    if not python_ok:
        print("  - Python is too old. See docs/01-setup.md, 'Install Python'.")
    if not venv_ok:
        print("  - The virtual environment isn't active. See docs/01-setup.md, 'Activate it'.")
    if missing:
        print(f"  - Missing packages: {', '.join(missing)}")
        print("    Fix: python -m pip install -r requirements.txt")
    print("More help: docs/01-setup.md, 'Troubleshooting'.")
    return 1


if __name__ == "__main__":
    # 0 means success by long-standing convention; anything else means failure.
    sys.exit(main())
