# ---------------------------------------------------------------------------
# setup.ps1 — one-command environment setup for Windows PowerShell.
#
# WHAT IT DOES
#   1. Finds a suitable Python (3.11 or newer).
#   2. Creates the .venv virtual environment if it does not exist.
#   3. Installs the pinned dependencies into it.
#   4. Records the exact versions installed, in requirements.lock.txt.
#   5. Runs the environment check and reports the verdict.
#
# WHY IT EXISTS
#   docs/01-setup.md walks through each step by hand and explains what every
#   one is for — do that first, at least once, because understanding your
#   environment is worth more than automating it. This script is the shortcut
#   for afterwards: a second machine, or a rebuild after something broke.
#
# USAGE
#   .\setup.ps1
#
#   If PowerShell refuses with "running scripts is disabled on this system",
#   allow scripts for your own account only (this is a normal, safe setting):
#       Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
# ---------------------------------------------------------------------------

# Stop at the first error rather than pressing on and failing confusingly later.
$ErrorActionPreference = "Stop"

Write-Host "======================================================================"
Write-Host "RealSignal - environment setup (Windows)"
Write-Host "======================================================================"

# --- 1. Find a Python interpreter of at least version 3.11 -----------------
# Windows usually provides both 'python' and the launcher 'py'. We try each
# and ask the interpreter itself whether it is new enough, rather than parsing
# version strings by hand (which breaks on unexpected formats).
$pythonCmd = $null
foreach ($candidate in @("python", "py")) {
    if (Get-Command $candidate -ErrorAction SilentlyContinue) {
        & $candidate -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)" 2>$null
        if ($LASTEXITCODE -eq 0) {
            $pythonCmd = $candidate
            break
        }
    }
}

if (-not $pythonCmd) {
    Write-Host "ERROR: no Python 3.11 or newer found on this machine." -ForegroundColor Red
    Write-Host ""
    Write-Host "Install it from https://www.python.org/downloads/"
    Write-Host "IMPORTANT: tick 'Add python.exe to PATH' on the first installer screen,"
    Write-Host "then close and reopen PowerShell (PATH changes do not affect open windows)."
    Write-Host ""
    Write-Host "Full instructions: docs\01-setup.md, section 3."
    exit 1
}

$version = & $pythonCmd --version
Write-Host "[1/5] Using $pythonCmd ($version)"

# --- 2. Create the virtual environment -------------------------------------
if (Test-Path ".venv") {
    Write-Host "[2/5] .venv already exists - reusing it."
} else {
    Write-Host "[2/5] Creating the virtual environment in .venv ..."
    & $pythonCmd -m venv .venv
}

# --- 3. Install dependencies ------------------------------------------------
# Call the venv's own python directly rather than activating: activation
# affects an interactive shell, not this script's child processes.
$venvPython = ".\.venv\Scripts\python.exe"

Write-Host "[3/5] Installing dependencies (this takes a few minutes) ..."
& $venvPython -m pip install --quiet --upgrade pip
& $venvPython -m pip install --quiet -r requirements.txt

# --- 4. Record exactly what was installed -----------------------------------
Write-Host "[4/5] Recording exact versions in requirements.lock.txt ..."
& $venvPython -m pip freeze | Out-File -Encoding utf8 requirements.lock.txt

# --- 5. Verify --------------------------------------------------------------
Write-Host "[5/5] Verifying the environment ..."
Write-Host ""
& $venvPython scripts\check_env.py

Write-Host ""
Write-Host "======================================================================"
Write-Host "Setup complete. Activate the environment in this terminal with:"
Write-Host ""
Write-Host "    .\.venv\Scripts\Activate.ps1"
Write-Host ""
Write-Host "Then continue with docs\02-phase-1-data-acquisition.md"
Write-Host "======================================================================"
