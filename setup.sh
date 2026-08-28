#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# setup.sh — one-command environment setup for macOS and Linux.
#
# WHAT IT DOES
#   1. Finds a suitable Python (3.11 or newer).
#   2. Creates the .venv virtual environment if it does not exist.
#   3. Installs the pinned dependencies into it.
#   4. Records the exact versions installed, in requirements.lock.txt.
#   5. Runs the environment check and reports the verdict.
#
# WHY IT EXISTS
#   docs/01-setup.md walks through each of these steps by hand and explains
#   what every one is for — do that first, at least once, because
#   understanding your environment is worth more than automating it. This
#   script is the shortcut for afterwards: setting up a second machine, or
#   rebuilding after something broke.
#
# USAGE
#   ./setup.sh
#   (if it will not run:  chmod +x setup.sh  — that grants permission to
#    execute the file, which is a separate thing from permission to read it)
# ---------------------------------------------------------------------------

# 'set -e' stops the script the moment any command fails, instead of pressing
# on and producing a confusing error three steps later.
set -e

echo "======================================================================"
echo "RealSignal — environment setup (macOS / Linux)"
echo "======================================================================"

# --- 1. Find a Python interpreter of at least version 3.11 -----------------
# Different systems name it differently, so we try the likely candidates in
# order of preference rather than assuming one.
PYTHON_CMD=""
for candidate in python3.13 python3.12 python3.11 python3; do
    if command -v "$candidate" >/dev/null 2>&1; then
        # Ask that interpreter whether it is new enough, and let it answer.
        if "$candidate" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)' 2>/dev/null; then
            PYTHON_CMD="$candidate"
            break
        fi
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    echo "ERROR: no Python 3.11 or newer found on this machine."
    echo
    echo "  RHEL 8 / Rocky / Alma :  sudo dnf install -y python3.11"
    echo "  Fedora                :  sudo dnf install -y python3.11"
    echo "  Ubuntu / Debian       :  sudo apt install -y python3.11 python3.11-venv"
    echo "  macOS                 :  https://www.python.org/downloads/"
    echo
    echo "Full instructions: docs/01-setup.md, section 3."
    exit 1
fi

echo "[1/5] Using $PYTHON_CMD ($($PYTHON_CMD --version))"

# --- 2. Create the virtual environment -------------------------------------
if [ -d ".venv" ]; then
    echo "[2/5] .venv already exists — reusing it."
else
    echo "[2/5] Creating the virtual environment in .venv ..."
    "$PYTHON_CMD" -m venv .venv
fi

# --- 3. Install dependencies ------------------------------------------------
# We call the venv's own python explicitly rather than activating, because
# activation only affects an interactive shell, not this script's child
# processes. Being explicit is more reliable and easier to reason about.
echo "[3/5] Installing dependencies (this takes a few minutes) ..."
./.venv/bin/python -m pip install --quiet --upgrade pip
./.venv/bin/python -m pip install --quiet -r requirements.txt

# --- 4. Record exactly what was installed -----------------------------------
echo "[4/5] Recording exact versions in requirements.lock.txt ..."
./.venv/bin/python -m pip freeze > requirements.lock.txt

# --- 5. Verify --------------------------------------------------------------
echo "[5/5] Verifying the environment ..."
echo
./.venv/bin/python scripts/check_env.py

echo
echo "======================================================================"
echo "Setup complete. Activate the environment in this terminal with:"
echo
echo "    source .venv/bin/activate"
echo
echo "Then continue with docs/02-phase-1-data-acquisition.md"
echo "======================================================================"
