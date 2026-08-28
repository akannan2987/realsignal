"""
check_env.py — proves this machine is set up correctly for RealSignal.

WHY THIS FILE EXISTS
--------------------
An installation that "seemed to work" is not the same as one that does.
This script imports every package the project needs and prints a clear
verdict, so that a problem is found now — in ten seconds, with a short
list of possible causes — rather than in three weeks, buried inside an
analysis, where it will look like a bug in your own code.

Run it with:   python scripts/check_env.py
"""

import platform
import sys

# The minimum Python version this project supports.
# 3.11 because some of our dependencies dropped support for older ones.
REQUIRED_PYTHON = (3, 11)

# Every package the project needs, mapped to a one-line reminder of why.
# The key is the name used in `import`, which is NOT always the name used
# by pip (scikit-learn installs, but you import sklearn).
REQUIRED_PACKAGES = {
    "pandas": "tables of data",
    "numpy": "fast arithmetic",
    "openpyxl": "reading Excel files",
    "duckdb": "the local SQL database",
    "sklearn": "machine learning (installed as 'scikit-learn')",
    "scipy": "statistics",
    "matplotlib": "charts",
    "requests": "downloading the dataset",
    "streamlit": "the interactive application",
    "pytest": "automated tests",
}


def check_python_version() -> bool:
    """Confirm the running Python is new enough. Returns True if OK."""
    actual = sys.version_info[:2]
    ok = actual >= REQUIRED_PYTHON
    symbol = "OK  " if ok else "FAIL"
    print(f"[{symbol}] Python {actual[0]}.{actual[1]} "
          f"(need {REQUIRED_PYTHON[0]}.{REQUIRED_PYTHON[1]} or newer)")
    return ok


def check_virtual_environment() -> bool:
    """
    Confirm we are running inside a virtual environment.

    HOW THIS WORKS: when a venv is active, Python sets `sys.prefix` to the
    venv folder while `sys.base_prefix` still points at the original
    system Python. If the two are equal, no venv is active.
    """
    inside = sys.prefix != sys.base_prefix
    symbol = "OK  " if inside else "WARN"
    print(f"[{symbol}] Virtual environment: "
          f"{'active' if inside else 'NOT ACTIVE — see docs/01-setup.md section 8'}")
    print(f"       Python executable: {sys.executable}")
    return inside


def check_packages() -> list[str]:
    """Try to import each required package. Returns the list that failed."""
    missing = []
    for module_name, purpose in REQUIRED_PACKAGES.items():
        try:
            module = __import__(module_name)
            # Most packages expose their version; a few do not, so be tolerant.
            version = getattr(module, "__version__", "version unknown")
            print(f"[OK  ] {module_name:<12} {version:<12} — {purpose}")
        except ImportError:
            print(f"[FAIL] {module_name:<12} {'MISSING':<12} — {purpose}")
            missing.append(module_name)
    return missing


def main() -> int:
    """Run every check and print a single, unambiguous verdict."""
    print("=" * 68)
    print("RealSignal — environment check")
    print("=" * 68)
    print(f"Operating system: {platform.system()} {platform.release()}")
    print("-" * 68)

    python_ok = check_python_version()
    venv_ok = check_virtual_environment()
    print("-" * 68)
    missing = check_packages()
    print("=" * 68)

    if python_ok and venv_ok and not missing:
        print("ALL CHECKS PASSED — your workshop is ready.")
        print("Next: docs/02-phase-1-data-acquisition.md")
        return 0

    print("SOMETHING NEEDS ATTENTION:")
    if not python_ok:
        print("  - Python is too old. See docs/01-setup.md section 3.")
    if not venv_ok:
        print("  - The virtual environment is not active.")
        print("    See docs/01-setup.md section 8 ('Activate it').")
    if missing:
        print(f"  - Missing packages: {', '.join(missing)}")
        print("    Fix with: pip install -r requirements.txt")
    print("Full troubleshooting: docs/01-setup.md section 15.")
    return 1


if __name__ == "__main__":
    # `sys.exit` with a number lets other tools know whether this passed.
    # 0 means success by long-standing convention; anything else is failure.
    sys.exit(main())