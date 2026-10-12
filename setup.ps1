# ---------------------------------------------------------------------------
# setup.ps1: one-command environment setup for Windows PowerShell.
#
# What it does
#   1. Finds a Python that is 3.11 or newer.
#   2. Creates the .venv virtual environment if it doesn't exist.
#   3. Installs the packages from requirements.txt into it.
#   4. Records the exact versions installed, in requirements.lock.txt.
#   5. Runs scripts\check_env.py and reports the verdict.
#
# Why it exists
#   docs\01-setup.md walks through each step by hand and explains what every
#   one is for. Do that at least once. This script is the shortcut for
#   afterwards: a second computer, or a rebuild after something broke
#   (docs\01-setup.md, section 16).
#
# Usage, from the project folder
#   .\setup.ps1
#
#   If PowerShell refuses with "running scripts is disabled on this system",
#   allow scripts you write or download yourself, for your account only:
#       Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
# ---------------------------------------------------------------------------

# Stop at the first error instead of carrying on and failing confusingly later.
$ErrorActionPreference = "Stop"

Write-Host "======================================================================"
Write-Host "RealSignal: environment setup (Windows)"
Write-Host "======================================================================"

# --- 1. Find a Python that is 3.11 or newer ---------------------------------
# Windows usually has both 'python' and the launcher 'py'. Ask each one
# whether it is new enough, instead of reading version numbers by hand.
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
    Write-Host "No Python 3.11 or newer was found on this computer." -ForegroundColor Red
    Write-Host ""
    Write-Host "Install it from https://www.python.org/downloads/"
    Write-Host "On the installer's first screen, tick 'Add python.exe to PATH',"
    Write-Host "then close and reopen PowerShell (open windows don't see the change)."
    Write-Host ""
    Write-Host "Full instructions: docs\01-setup.md, section 3."
    exit 1
}

$version = & $pythonCmd --version
Write-Host "[1/5] Using $pythonCmd ($version)"

# --- 2. Create the virtual environment --------------------------------------
if (Test-Path ".venv") {
    Write-Host "[2/5] .venv already exists, reusing it."
} else {
    Write-Host "[2/5] Creating the virtual environment in .venv ..."
    & $pythonCmd -m venv .venv
}

# --- 3. Install the packages -------------------------------------------------
# Call the environment's own Python by its path instead of activating it:
# activation changes an interactive window, not the programs a script starts.
$venvPython = ".\.venv\Scripts\python.exe"

Write-Host "[3/5] Installing the packages (this takes a few minutes) ..."
& $venvPython -m pip install --quiet --upgrade pip
& $venvPython -m pip install --quiet -r requirements.txt

# --- 4. Record exactly what was installed -----------------------------------
# ASCII keeps the file identical in form to the one macOS and Linux write.
Write-Host "[4/5] Recording the exact versions in requirements.lock.txt ..."
& $venvPython -m pip freeze | Out-File -Encoding ascii requirements.lock.txt

# --- 5. Check ----------------------------------------------------------------
Write-Host "[5/5] Checking the environment ..."
Write-Host ""
& $venvPython scripts\check_env.py

Write-Host ""
Write-Host "======================================================================"
Write-Host "Setup complete. Activate the environment in this window with:"
Write-Host ""
Write-Host "    .\.venv\Scripts\Activate.ps1"
Write-Host ""
Write-Host "Then carry on from docs\HANDBOOK.md, at the stage you are on."
Write-Host "======================================================================"
