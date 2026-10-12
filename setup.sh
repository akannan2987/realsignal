#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# setup.sh: one-command environment setup for macOS and Linux (RHEL 8 too).
#
# What it does
#   1. Finds a Python that is 3.11 or newer.
#   2. Creates the .venv virtual environment if it doesn't exist.
#   3. Installs the packages from requirements.txt into it.
#   4. Records the exact versions installed, in requirements.lock.txt.
#   5. Runs scripts/check_env.py and reports the verdict.
#
# Why it exists
#   docs/01-setup.md walks through each of these steps by hand and explains
#   what every one is for. Do that at least once. This script is the shortcut
#   for afterwards: a second computer, or a rebuild after something broke
#   (docs/01-setup.md, section 16).
#
# Usage, from the project folder
#   ./setup.sh
#   If it won't run:  chmod +x setup.sh
#   (that marks the file as runnable, which is separate from being readable)
# ---------------------------------------------------------------------------

# Stop at the first command that fails, instead of carrying on and producing
# a confusing error three steps later.
set -e

echo "======================================================================"
echo "RealSignal: environment setup (macOS / Linux)"
echo "======================================================================"

# --- 1. Find a Python that is 3.11 or newer ---------------------------------
# Systems name Python differently (RHEL 8 has python3.11 and python3.12 next
# to an older python3), so try the likely names, newest first, and ask each
# one whether it is new enough.
PYTHON_CMD=""
for candidate in python3.14 python3.13 python3.12 python3.11 python3; do
    if command -v "$candidate" >/dev/null 2>&1; then
        if "$candidate" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)' 2>/dev/null; then
            PYTHON_CMD="$candidate"
            break
        fi
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    echo "No Python 3.11 or newer was found on this computer."
    echo
    echo "  RHEL 8 / Rocky / Alma :  sudo dnf install -y python3.12   (or python3.11)"
    echo "  Ubuntu / Debian       :  sudo apt install -y python3.12 python3.12-venv"
    echo "  macOS                 :  https://www.python.org/downloads/"
    echo
    echo "Full instructions: docs/01-setup.md, section 3."
    exit 1
fi

echo "[1/5] Using $PYTHON_CMD ($($PYTHON_CMD --version))"

# --- 2. Create the virtual environment --------------------------------------
if [ -d ".venv" ]; then
    echo "[2/5] .venv already exists, reusing it."
else
    echo "[2/5] Creating the virtual environment in .venv ..."
    "$PYTHON_CMD" -m venv .venv
fi

# --- 3. Install the packages -------------------------------------------------
# Call the environment's own Python by its path instead of activating it:
# activation changes an interactive terminal, not the programs a script starts.
echo "[3/5] Installing the packages (this takes a few minutes) ..."
./.venv/bin/python -m pip install --quiet --upgrade pip
./.venv/bin/python -m pip install --quiet -r requirements.txt

# --- 4. Record exactly what was installed -----------------------------------
echo "[4/5] Recording the exact versions in requirements.lock.txt ..."
./.venv/bin/python -m pip freeze > requirements.lock.txt

# --- 5. Check ----------------------------------------------------------------
echo "[5/5] Checking the environment ..."
echo
./.venv/bin/python scripts/check_env.py

echo
echo "======================================================================"
echo "Setup complete. Activate the environment in this terminal with:"
echo
echo "    source .venv/bin/activate"
echo
echo "Then carry on from docs/HANDBOOK.md, at the stage you are on."
echo "======================================================================"
