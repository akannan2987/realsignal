# 01 — Setup: from a blank laptop to a working workshop

**Prerequisites:** a computer running Windows 10/11, macOS, or Linux
(these instructions are tested against RHEL 8 and work on Ubuntu and
Fedora too), an internet connection, and permission to install software
on it. **No programming experience is assumed.** If you have never
opened a terminal in your life, start here and do not skip anything.

**Learning goal:** by the end you will have Python, Git, a code editor,
a GitHub account and a sealed project environment — and, more
importantly, you will understand *what each one is for*, so that when
something breaks you can reason about it instead of searching blindly.

**Time:** 60–90 minutes the first time. You do this once per machine.
After that, starting work takes ten seconds.

> Every term here is defined in [`GLOSSARY.md`](GLOSSARY.md).

---

## Contents

- [0. How to read this document](#0-how-to-read-this-document)
- [1. What we are installing, and why](#1-what-we-are-installing-and-why)
- [2. Opening a terminal](#2-opening-a-terminal)
- [3. Install Python](#3-install-python)
- [4. Install Git](#4-install-git)
- [5. Install a code editor (recommended)](#5-install-a-code-editor-recommended)
- [6. Create a GitHub account and an empty repository](#6-create-a-github-account-and-an-empty-repository)
- [7. Create the project folder](#7-create-the-project-folder)
- [8. Create the virtual environment](#8-create-the-virtual-environment)
- [9. Install the project's packages](#9-install-the-projects-packages)
- [10. Verify everything works](#10-verify-everything-works)
- [11. Protect the repository with .gitignore](#11-protect-the-repository-with-gitignore)
- [12. Connect to GitHub and create the branches](#12-connect-to-github-and-create-the-branches)
- [13. Checkpoint](#13-checkpoint)
- [14. Starting work on any later day](#14-starting-work-on-any-later-day)
- [15. Troubleshooting](#15-troubleshooting)

---

## 0. How to read this document

**Commands are shown one per box.** Copy the whole line, paste it into
your terminal, press Enter. Commands are shown *without* the prompt
symbol (`$`, `>`, `PS>`), so what you see is exactly what you type.

**After most commands there is an "Expected output" block.** Compare
what you got against it. It will rarely match word for word — version
numbers and paths differ between machines — but it should match in
*shape*. If it does not, §15 covers what to do.

**Platform blocks look like this:**

> **🪟 Windows** — instructions for PowerShell
> **🍎 macOS** — instructions for Terminal
> **🐧 Linux** — instructions for bash (RHEL 8, Ubuntu, Fedora)

Do only your own platform's block. Everything *outside* these blocks is
identical on all three.

**One rule above all:** do not skip a verification step because the
install "looked fine". Verifying takes five seconds; debugging a
silently broken environment three phases later takes an evening. That
habit — *check, don't assume* — is worth more than any single command
in this document.

---

## 1. What we are installing, and why

Five things. Here is what each one is for, in plain words, before you
install anything.

| # | Thing | What it is | Everyday analogy |
|---|---|---|---|
| 1 | **Python** | The programming language everything is written in | The language the recipes are written in |
| 2 | **Git** | Records every change to your files, permanently | A save-game system for your work |
| 3 | **A code editor** (VS Code) | A comfortable place to write and read code | A word processor, but for code |
| 4 | **A GitHub account** | An online home for your project | The shared photo album |
| 5 | **A virtual environment** | A sealed toolbox of packages, for this project only | A chef's knife roll per restaurant, not one shared drawer |

The fifth one is the one beginners skip, and it is the one that saves
the most pain. §8 explains it properly.

---

## 2. Opening a terminal

The **terminal** is a window where you type commands as text instead of
clicking. *Analogy:* ordering at a counter by saying exactly what you
want, rather than pointing at pictures. Slower to learn; far faster and
far more precise afterwards — and crucially, every instruction can be
written down exactly, which is why documentation uses it.

> **🪟 Windows**
> Press the Windows key, type `powershell`, and click **Windows
> PowerShell**. (Not "Command Prompt" — PowerShell is the modern one
> and these instructions assume it.)

> **🍎 macOS**
> Press `Cmd + Space`, type `terminal`, press Enter.

> **🐧 Linux**
> Press `Ctrl + Alt + T`, or find "Terminal" in your applications. On a
> server or VM you are usually already in one.

**Your first command.** This asks "which folder am I in?" It changes
nothing and cannot break anything.

> **🪟 Windows**
> ```powershell
> Get-Location
> ```
> Expected output:
> ```
> Path
> ----
> C:\Users\yourname
> ```

> **🍎 macOS / 🐧 Linux**
> ```bash
> pwd
> ```
> Expected output:
> ```
> /Users/yourname          (macOS)
> /home/yourname           (Linux)
> ```

That folder is your **home directory** — your personal space on the
machine. Two more commands worth knowing right now:

| Purpose | Windows | macOS / Linux |
|---|---|---|
| List what's in this folder | `ls` | `ls` |
| Move into a folder | `cd foldername` | `cd foldername` |
| Move up one folder | `cd ..` | `cd ..` |
| Go home | `cd ~` | `cd ~` |

That is genuinely enough terminal to complete this entire project.

---

## 3. Install Python

**What Python is:** the programming language this project is written
in. Free, open source, and by a wide margin the standard language for
data work and machine learning.

**Which version:** **3.11 or newer.** Not 3.8 (too old for some
packages we use), not "whatever is already there" without checking.

### First, check whether you already have it

```bash
python3 --version
```

> **🪟 Windows** — try both of these, as Windows names it differently:
> ```powershell
> python --version
> py --version
> ```

**Expected output if you have a suitable version:**

```
Python 3.11.9
```

Anything 3.11 or higher: skip to §4. Anything lower, or
"command not found": install it below.

> ⚠️ **A trap on macOS and Linux.** These systems ship with a Python
> that the *operating system itself* uses. It is often old (RHEL 8
> ships 3.6). Do not remove it, do not upgrade it in place, and do not
> install project packages into it — parts of your OS depend on it.
> Install a newer Python alongside it. That is exactly what the
> instructions below do.

### Install

> **🪟 Windows**
>
> 1. Go to <https://www.python.org/downloads/>
> 2. Click the yellow **Download Python 3.x** button.
> 3. Run the downloaded installer.
> 4. **On the first screen, tick "Add python.exe to PATH".** This is the
>    single most important click in this entire document. Without it,
>    Windows will not find Python when you type `python`, and you will
>    get "command not found" for reasons that make no sense.
>    *Analogy:* the shop exists, but it isn't on the map your driver is
>    using.
> 5. Click **Install Now** and wait.
> 6. **Close PowerShell completely and open a new one.** PATH changes
>    only apply to windows opened afterwards. (This catches almost
>    everyone.)
> 7. Verify:
>    ```powershell
>    python --version
>    ```

> **🍎 macOS**
>
> **Option A — the installer (simplest):**
> 1. Go to <https://www.python.org/downloads/>
> 2. Download and run the macOS installer, accepting the defaults.
> 3. Open a *new* Terminal window and verify:
>    ```bash
>    python3 --version
>    ```
>
> **Option B — Homebrew** (if you already have it):
> ```bash
> brew install python@3.12
> python3 --version
> ```

> **🐧 Linux — RHEL 8 / Rocky / AlmaLinux**
>
> RHEL 8 ships Python 3.6, which is too old. Install 3.11 from the
> standard AppStream repository — this sits *alongside* the system
> Python without disturbing it:
> ```bash
> sudo dnf install -y python3.11 python3.11-pip
> ```
> `sudo` means "run as administrator". You will be asked for your
> password; nothing appears as you type it, which is normal and
> deliberate.
>
> Verify — note the explicit `3.11`, which is how you will refer to it:
> ```bash
> python3.11 --version
> ```
> ```
> Python 3.11.5
> ```
>
> **If `sudo` is not available to you** (common on managed corporate
> machines), ask whoever administers the machine for `python3.11`. If
> that is not possible, `pyenv` (<https://github.com/pyenv/pyenv>) can
> install Python into your home directory with no administrator rights.

> **🐧 Linux — Ubuntu / Debian**
> ```bash
> sudo apt update
> sudo apt install -y python3 python3-venv python3-pip
> python3 --version
> ```
> If that gives less than 3.11, add the deadsnakes archive:
> ```bash
> sudo add-apt-repository ppa:deadsnakes/ppa
> sudo apt update
> sudo apt install -y python3.11 python3.11-venv
> ```

> **🐧 Linux — Fedora**
> ```bash
> sudo dnf install -y python3.11
> ```

### ⚠️ Remember your Python command

From here on, this document writes **`python3`**. Substitute whatever
worked on *your* machine:

| Your platform | Your command |
|---|---|
| Windows | `python` |
| macOS | `python3` |
| RHEL 8 | `python3.11` |
| Ubuntu (if you installed 3.11 explicitly) | `python3.11` |

Write it on a sticky note. This one substitution is the source of most
early confusion, and it disappears entirely after §8 — once the virtual
environment is active, `python` means the right thing everywhere.

---

## 4. Install Git

**What Git is:** the save-game system for your work. Full explanation
in [`GIT_WORKFLOW.md`](GIT_WORKFLOW.md); for now, install it.

**Check first:**

```bash
git --version
```

**Expected:** `git version 2.39.3` (any 2.x is fine).

> **🪟 Windows**
> Download from <https://git-scm.com/download/win> and run the
> installer. **Accept every default** — the defaults are sensible and
> the option screens are genuinely confusing on a first pass. Then close
> and reopen PowerShell.

> **🍎 macOS**
> ```bash
> git --version
> ```
> If Git is missing, macOS will pop up a dialogue offering to install
> the developer tools. Click **Install** and wait. That is the whole
> procedure.

> **🐧 Linux — RHEL 8 / Rocky / Fedora**
> ```bash
> sudo dnf install -y git
> ```
> **Ubuntu / Debian:**
> ```bash
> sudo apt install -y git
> ```

### Tell Git who you are

Once per machine. Every commit records its author, which is why this is
required.

```bash
git config --global user.name "Your Name"
git config --global user.email "your-email@example.com"
```

Use the email you will register with GitHub, so your commits are linked
to your account.

**Verify:**

```bash
git config --global --list
```

```
user.name=Your Name
user.email=your-email@example.com
```

---

## 5. Install a code editor (recommended)

**Optional but strongly recommended.** Everything in this project works
in any text editor, but a proper editor colours your code, highlights
mistakes as you type, and has a built-in terminal so you are not
switching windows constantly.

**VS Code** (Visual Studio Code) is free, made by Microsoft, and behaves
identically on all three operating systems.

1. Download from <https://code.visualstudio.com/>
2. Install with the defaults.
   > **🪟 Windows** — tick **"Add to PATH"** if offered.
3. Open it, click the **Extensions** icon in the left bar (four small
   squares), search for **Python**, and install the one published by
   Microsoft.

That extension gives you syntax colouring, error highlighting and the
ability to run a file with one click.

---

## 6. Create a GitHub account and an empty repository

**What GitHub is:** a website that stores a copy of your project
online — backed up, shareable, and visible to anyone you point at it.

### Create the account

1. Go to <https://github.com/signup>
2. Use the same email as in §4.
3. Choose a username you would be comfortable putting on professional
   work. It becomes part of every link to everything you publish.
4. Verify your email address.

### Create the repository

1. Once signed in, click the **+** at the top right → **New
   repository**.
2. Fill in:
   - **Repository name:** `realsignal`
   - **Description:** `Independent reproduction and extension of a published machine-learning study on plant-protective bacteria`
   - **Public** — this is work you want to be able to share.
   - **Do NOT tick** "Add a README file".
   - **Do NOT** add a `.gitignore` or a licence here.
3. Click **Create repository**.

> **Why create it empty?** Because we are going to build the project on
> your machine first and then connect it. If GitHub creates files too,
> both sides have history the other does not, and your first push fails
> with an error about unrelated histories. Starting empty avoids a
> confusing problem you would otherwise have to solve before you had
> learned enough Git to understand it.

4. GitHub now shows a page of setup commands. **Leave this page open** —
   you need the URL from it in §12. It looks like:
   `https://github.com/YOURNAME/realsignal.git`

---

## 7. Create the project folder

Pick a sensible home for your projects.

> **🪟 Windows**
> ```powershell
> cd $HOME
> mkdir projects -Force
> cd projects
> mkdir realsignal
> cd realsignal
> ```

> **🍎 macOS / 🐧 Linux**
> ```bash
> cd ~
> mkdir -p projects
> cd projects
> mkdir realsignal
> cd realsignal
> ```

**Confirm where you are** — this matters, because every later command
assumes you are inside `realsignal`:

> **🪟 Windows:** `Get-Location` → `C:\Users\yourname\projects\realsignal`
> **🍎 macOS / 🐧 Linux:** `pwd` → `/home/yourname/projects/realsignal`

> ⚠️ **A word of warning about cloud-synced folders.** Avoid putting the
> project inside OneDrive, Dropbox, iCloud Drive or Google Drive. Those
> tools continuously copy files in the background, which conflicts with
> Git's own file management and with virtual environments, producing
> genuinely baffling errors. Git already gives you backup and sync —
> that is its job. Keep the two apart.

### Create the folder structure

These are the folders described in
[`00-architecture.md`](00-architecture.md).

> **🪟 Windows**
> ```powershell
> mkdir docs, scripts, notebooks, tests, app, figures
> mkdir src\realsignal
> mkdir data\raw, data\processed
> ```

> **🍎 macOS / 🐧 Linux**
> ```bash
> mkdir -p docs scripts notebooks tests app figures src/realsignal data/raw data/processed
> ```

Git does not track empty folders (it tracks files, not directories), so
add a placeholder to the ones that will be empty for a while. The name
`.gitkeep` is a convention, not a Git feature — any file would do.

> **🪟 Windows**
> ```powershell
> "" | Out-File -Encoding utf8 notebooks\.gitkeep
> "" | Out-File -Encoding utf8 tests\.gitkeep
> "" | Out-File -Encoding utf8 app\.gitkeep
> "" | Out-File -Encoding utf8 figures\.gitkeep
> "" | Out-File -Encoding utf8 src\realsignal\__init__.py
> ```

> **🍎 macOS / 🐧 Linux**
> ```bash
> touch notebooks/.gitkeep tests/.gitkeep app/.gitkeep figures/.gitkeep
> touch src/realsignal/__init__.py
> ```

> **What is `__init__.py`?** An empty file that tells Python "this
> folder is a package you can import from". Without it, `import
> realsignal` fails. It stays empty for now, and that is correct.

**Now copy the documentation files into `docs/`** — this document,
`00-architecture.md`, `GIT_WORKFLOW.md` and `GLOSSARY.md` — and
`README.md` into the project root.

---

## 8. Create the virtual environment

This is the section people skip. Read it; it is short and it will save
you an evening.

### The problem it solves

You install a package for this project. Next month, a different project
needs an older version of the same package. You install that. **The
first project silently breaks** — not with a clear message, but with
subtly different results or a crash in a place that used to work.

*Analogy:* one shared kitchen drawer where every restaurant in the
street keeps its knives. Someone sharpens one differently, someone else
takes one home, and nobody can cook reliably.

### The solution

A **virtual environment** is a private, sealed copy of Python and its
packages that belongs to one project only. Its own knife roll. Projects
cannot interfere with each other, and — just as importantly — the exact
contents can be written down and rebuilt by somebody else, which is what
makes the project reproducible at all.

### Create it

Run this **inside the `realsignal` folder**, using *your* Python
command from §3:

> **🪟 Windows**
> ```powershell
> python -m venv .venv
> ```

> **🍎 macOS**
> ```bash
> python3 -m venv .venv
> ```

> **🐧 Linux — RHEL 8**
> ```bash
> python3.11 -m venv .venv
> ```
> If that fails with a message about `ensurepip`, install the venv
> module first:
> ```bash
> sudo dnf install -y python3.11-devel
> ```

It prints nothing and takes a few seconds. A hidden folder `.venv`
now exists. Confirm:

> **🪟 Windows:** `ls -Force` (the `-Force` reveals hidden items)
> **🍎 macOS / 🐧 Linux:** `ls -a`

You should see `.venv` listed.

> **Why the name `.venv`?** The leading dot makes it hidden on
> macOS/Linux, and it is the near-universal convention, which means
> tools like VS Code find it automatically. Do not rename it.

### Activate it

Creating the toolbox is not the same as picking it up. **Activating**
tells this terminal session: "for now, `python` means *this* project's
Python".

> **🪟 Windows PowerShell**
> ```powershell
> .\.venv\Scripts\Activate.ps1
> ```
> If you get a red error mentioning *execution policies*, Windows is
> blocking scripts by default. Allow them for your own account only:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```
> Answer `Y`, then run the activate command again. This is a normal,
> safe adjustment: it permits scripts you wrote locally, while still
> requiring downloaded scripts to be signed.

> **🍎 macOS / 🐧 Linux**
> ```bash
> source .venv/bin/activate
> ```

**How you know it worked:** your prompt gains a `(.venv)` prefix.

```
(.venv) yourname@machine realsignal %
```

**That prefix is your single most useful status light.** No `(.venv)`
means the environment is not active, which means packages will install
in the wrong place and imports will fail with confusing errors. If
anything ever behaves strangely, look at the prompt first.

**Verify Python now points inside the project:**

> **🪟 Windows**
> ```powershell
> where.exe python
> ```
> ```
> C:\Users\yourname\projects\realsignal\.venv\Scripts\python.exe
> ```

> **🍎 macOS / 🐧 Linux**
> ```bash
> which python
> ```
> ```
> /home/yourname/projects/realsignal/.venv/bin/python
> ```

The path must contain `.venv`. If it does not, activation did not take
effect — see §15.

**To leave the environment** (rarely needed): type `deactivate`.

> **You must activate again in every new terminal window.** It is not
> permanent, and that is by design — it is a per-session choice, not a
> machine-wide setting. Forgetting is the most common beginner
> confusion, which is why the `(.venv)` prefix exists.

---

## 9. Install the project's packages

### First, a note on `pip` and pinning

**pip** is Python's package installer — it fetches libraries from
**PyPI**, the public warehouse of Python packages.

We list what we need in a file called `requirements.txt` so that anyone
(including you, on another machine, in a year) can rebuild the identical
toolbox with one command. *Analogy:* the parts list that comes with
flat-pack furniture.

### Create `requirements.txt`

Create a file called `requirements.txt` in the project root — in VS
Code: **File → New File**, paste, save with that exact name — containing:

```
# RealSignal — Python dependencies
# Install with:  pip install -r requirements.txt
#
# Version ranges: the lower bound is the oldest version known to work;
# the upper bound keeps a future major release from silently breaking
# the project. After a successful install, run
#     pip freeze > requirements.lock.txt
# to record the exact versions you actually got. That lock file is what
# makes an install truly reproducible; this file is what makes it
# installable in the first place.

# --- Core data handling -------------------------------------------------
pandas>=2.2,<4.0          # tables of data, driven by code
numpy>=1.24,<3.0          # fast arithmetic underneath everything else
openpyxl>=3.1,<4.0        # lets pandas read .xlsx files (the published data)

# --- Storage ------------------------------------------------------------
duckdb>=1.0,<2.0          # a complete SQL database in a single file

# --- Modelling ----------------------------------------------------------
scikit-learn>=1.4,<2.0    # the machine-learning models and evaluation tools
scipy>=1.11,<2.0          # statistics used for confidence intervals

# --- Charts -------------------------------------------------------------
matplotlib>=3.8,<4.0      # charts, saved as image files by code

# --- Getting the data ---------------------------------------------------
requests>=2.31,<3.0       # downloading files over the internet

# --- The application ----------------------------------------------------
streamlit>=1.36,<2.0      # turns a Python script into a clickable web app

# --- Quality ------------------------------------------------------------
pytest>=8.0,<9.0          # automated tests
```

> **Why ranges rather than exact `==` versions?** Because exact pins can
> fail to install on a platform where that precise build isn't
> available — a real problem when a project must run on Windows, macOS
> *and* RHEL 8. So we install with sensible ranges, then *record* what
> we actually got in a lock file. You get both reliability and
> reproducibility, and you learn the distinction professionals make
> between the two.

### Install

With `(.venv)` visible in your prompt:

```bash
python -m pip install --upgrade pip
```

```bash
pip install -r requirements.txt
```

**Expected output** — several minutes of download progress, ending with:

```
Successfully installed duckdb-1.1.3 matplotlib-3.9.2 numpy-2.1.3
openpyxl-3.1.5 pandas-2.2.3 pytest-8.3.3 requests-2.32.3
scikit-learn-1.5.2 scipy-1.14.1 streamlit-1.39.0 ...
```

Your version numbers will differ. That is expected and fine.

> **Why `python -m pip` rather than just `pip`?** It guarantees you are
> using the pip belonging to the Python you are actually running. On a
> machine with several Pythons, a bare `pip` can belong to a different
> one — a genuinely maddening bug where packages install successfully
> and then cannot be imported.

### Record exactly what you got

```bash
pip freeze > requirements.lock.txt
```

That writes a file listing every package with its exact version. Commit
it. In a year, if something breaks, this file tells you precisely what
"working" looked like.

---

## 10. Verify everything works

Trust nothing; check everything. Create `scripts/check_env.py` with the
content below.

```python
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
```

**Run it:**

```bash
python scripts/check_env.py
```

**Expected output:**

```
====================================================================
RealSignal — environment check
====================================================================
Operating system: Linux 4.18.0-513.el8.x86_64
--------------------------------------------------------------------
[OK  ] Python 3.11 (need 3.11 or newer)
[OK  ] Virtual environment: active
       Python executable: /home/you/projects/realsignal/.venv/bin/python
--------------------------------------------------------------------
[OK  ] pandas       2.2.3        — tables of data
[OK  ] numpy        2.1.3        — fast arithmetic
[OK  ] openpyxl     3.1.5        — reading Excel files
[OK  ] duckdb       1.1.3        — the local SQL database
[OK  ] sklearn      1.5.2        — machine learning (installed as 'scikit-learn')
[OK  ] scipy        1.14.1       — statistics
[OK  ] matplotlib   3.9.2        — charts
[OK  ] requests     2.32.3       — downloading the dataset
[OK  ] streamlit    1.39.0       — the interactive application
[OK  ] pytest       8.3.3        — automated tests
====================================================================
ALL CHECKS PASSED — your workshop is ready.
Next: docs/02-phase-1-data-acquisition.md
```

🎉 **If you see that, stop and appreciate it.** You have installed a
programming language, a version-control system, an isolated
environment, and ten libraries — and you have *proved* it rather than
assumed it. That verification habit is the thing separating people who
can debug from people who can only hope.

---

## 11. Protect the repository with `.gitignore`

Before the first commit — because it is far easier to keep something
out of history than to remove it afterwards.

`.gitignore` lists things Git must never record. Create it in the
project root:

```gitignore
# ---------------------------------------------------------------------
# RealSignal — files Git must never track
# ---------------------------------------------------------------------

# The virtual environment. Hundreds of megabytes, machine-specific, and
# fully rebuildable from requirements.txt. Never commit it.
.venv/
venv/
env/

# Downloaded and generated data. Rebuilt by scripts/fetch_data.py,
# verified by checksum. Keeping it out is deliberate: the script working
# is the proof the project works. (See README, "Repository map".)
data/

# Python's compiled cache files — generated automatically, never useful
# to anyone else.
__pycache__/
*.py[cod]
*.egg-info/
.pytest_cache/

# Jupyter notebook checkpoints
.ipynb_checkpoints/

# Secrets. This project uses only public data and needs no credentials,
# but the rule belongs here permanently: a secret committed once is
# compromised forever, because history is permanent.
.env
*.key
secrets.*

# Operating-system clutter
.DS_Store          # macOS Finder
Thumbs.db          # Windows Explorer
desktop.ini

# Editor settings — personal, not project-wide
.vscode/
.idea/
*.swp
```

**Verify it is working** — this is worth doing, because a `.gitignore`
with a typo silently does nothing:

```bash
git status
```

At this stage Git is not yet initialised, so you will see
`fatal: not a git repository`. That is expected; §12 fixes it, and you
will re-run `git status` there.

---

## 12. Connect to GitHub and create the branches

Now the project becomes a real repository with the three branches
described in [`GIT_WORKFLOW.md`](GIT_WORKFLOW.md).

**Step 1 — start tracking the folder:**

```bash
git init
```
```
Initialized empty Git repository in /home/you/projects/realsignal/.git/
```

**Step 2 — name the first branch `master`:**

```bash
git branch -M master
```

**Step 3 — check what Git proposes to record.** Read this output
carefully; it is the moment to catch a `.gitignore` mistake:

```bash
git status
```

You should see `README.md`, `requirements.txt`, `requirements.lock.txt`,
`.gitignore`, `docs/`, `scripts/` and the `.gitkeep` placeholders.

> ⚠️ **You must NOT see `.venv/` or `data/`.** If you do, `.gitignore`
> is not in the project root, or its name is wrong (a common Windows
> trap: Notepad saving it as `.gitignore.txt`). Fix that before
> continuing — this is exactly the check that stops a 239 MB accident.

**Step 4 — the first commit:**

```bash
git add -A
git commit -m "chore: initial project structure, documentation and environment"
```
```
[master (root-commit) a1b2c3d] chore: initial project structure, documentation and environment
 8 files changed, 1247 insertions(+)
```

**Step 5 — connect to your GitHub repository.** Use the URL from §6:

```bash
git remote add origin https://github.com/YOURNAME/realsignal.git
```

Replace `YOURNAME`. Verify:

```bash
git remote -v
```
```
origin  https://github.com/YOURNAME/realsignal.git (fetch)
origin  https://github.com/YOURNAME/realsignal.git (push)
```

**Step 6 — push `master`:**

```bash
git push -u origin master
```

> **You will be asked to sign in.** GitHub no longer accepts your
> account password here. On Windows and macOS a browser window opens —
> sign in and approve. On Linux, or if no window appears, create a
> **personal access token**: GitHub → your avatar → **Settings** →
> **Developer settings** → **Personal access tokens** → **Tokens
> (classic)** → **Generate new token**, tick the `repo` scope, set an
> expiry, and copy the token. Paste it when asked for your *password*.
> Store it in a password manager — GitHub will never show it again.

**Step 7 — create and push `beta` and `develop`:**

```bash
git branch beta
git branch develop
git push -u origin beta
git push -u origin develop
```

**Step 8 — move to the working branch:**

```bash
git switch develop
```
```
Switched to branch 'develop'
Your branch is up to date with 'origin/develop'.
```

**Step 9 — verify all six branch references exist:**

```bash
git branch -a
```
```
  beta
* develop
  master
  remotes/origin/beta
  remotes/origin/develop
  remotes/origin/master
```

**Step 10 — look at it in a browser.** Open
`https://github.com/YOURNAME/realsignal`. Your README is rendered on the
front page, and a branch dropdown offers all three branches.

---

## 13. Checkpoint

Tick these off honestly:

- [ ] `python --version` reports 3.11 or newer
- [ ] `git --version` works, and `git config --global --list` shows your
      name and email
- [ ] The folder `~/projects/realsignal` exists with the full structure
- [ ] Your terminal prompt shows `(.venv)` after activation
- [ ] `which python` / `where.exe python` points inside `.venv`
- [ ] `python scripts/check_env.py` prints **ALL CHECKS PASSED**
- [ ] `git status` does **not** list `.venv/` or `data/`
- [ ] `git branch -a` shows all three branches locally and on `origin`
- [ ] Your README is visible on GitHub in a browser

**Commit the checkpoint:**

```bash
git switch develop
git add -A
git commit -m "chore: verified environment setup on this machine"
git push origin develop develop:beta develop:master

git switch master
git pull --ff-only origin master
git switch develop
```

Every line of that is explained in
[`GIT_WORKFLOW.md`](GIT_WORKFLOW.md) §6.

---

## 14. Starting work on any later day

Three commands. Put them somewhere you can find them.

> **🪟 Windows**
> ```powershell
> cd $HOME\projects\realsignal
> .\.venv\Scripts\Activate.ps1
> git switch develop
> ```

> **🍎 macOS / 🐧 Linux**
> ```bash
> cd ~/projects/realsignal
> source .venv/bin/activate
> git switch develop
> ```

Then confirm you are where you think you are:

```bash
git status
```

Three commands and one check. That is the whole start-up ritual, for
the rest of the project.

---

## 15. Troubleshooting

### `python: command not found` / `'python' is not recognized`

Python is not installed, or not on your PATH.

- **Windows:** almost always the "Add python.exe to PATH" tick box was
  missed in §3. Re-run the installer, choose **Modify**, and ensure it
  is ticked. Then **open a new PowerShell window** — PATH changes never
  apply to already-open windows.
- **macOS/Linux:** try `python3` instead of `python`. On RHEL 8 use
  `python3.11`.

### `pip: command not found`

Use `python -m pip` instead of bare `pip`. This always works, because
it explicitly asks the Python you are running for its own pip.

### PowerShell: "running scripts is disabled on this system"

Windows blocks scripts by default. Allow them for your own account:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### No `(.venv)` in the prompt after activating

- Check you are in the right folder (`Get-Location` / `pwd`).
- Check `.venv` exists (`ls -Force` / `ls -a`).
- Windows users: the path uses `\` and `Scripts`; macOS/Linux use `/`
  and `bin`. They are not interchangeable.
- If `.venv` is missing or corrupted, delete it and rebuild — this is
  always safe, because it is fully rebuildable:
  ```bash
  rm -rf .venv                    # macOS/Linux
  Remove-Item -Recurse -Force .venv   # Windows
  ```
  then repeat §8 and §9.

### `ModuleNotFoundError: No module named 'pandas'`

The environment is not active, or packages went somewhere else. Check
the prompt for `(.venv)`, activate, and re-run
`pip install -r requirements.txt`. Then `python scripts/check_env.py`.

This error is nearly always the venv, not the package.

### `SSL: CERTIFICATE_VERIFY_FAILED` when pip downloads

Usually a corporate network inspecting traffic. Ask your IT team for the
company certificate bundle; they will have handled this before. Do not
disable certificate verification — that turns off the check that the
code you are downloading is genuinely from PyPI.

### `Permission denied` on Linux

You are trying to write somewhere you do not own. Work inside your home
directory (`~/projects/...`), and never use `sudo pip install` — that
installs into the system Python, which is precisely what the virtual
environment exists to avoid.

### RHEL 8: `python3.11 -m venv` fails mentioning `ensurepip`

```bash
sudo dnf install -y python3.11-devel
```
then retry.

### Git asks for a password and rejects the right one

GitHub removed password authentication for Git operations. Use a
personal access token as your password — see §12, Step 6.

### `git push` rejected: "Updates were rejected"

The remote has commits you do not. Pull first:

```bash
git pull --ff-only origin develop
```

Then push again. Do not use `--force` to make the message disappear; it
overwrites history on GitHub permanently.

### `.gitignore` seems to be ignored

Two usual causes:

1. **Wrong filename.** On Windows, Notepad may have saved it as
   `.gitignore.txt`. Check with `ls -Force` (Windows) or `ls -a`
   (macOS/Linux). Create it in VS Code instead, which saves the exact
   name.
2. **The file was already committed before you ignored it.** `.gitignore`
   only affects *untracked* files. Untrack it, keeping the file on disk:
   ```bash
   git rm -r --cached data/
   git commit -m "chore: stop tracking data directory"
   ```

---

**Next:** [`02-phase-1-data-acquisition.md`](02-phase-1-data-acquisition.md)
— downloading the real published dataset, verifying it by checksum, and
seeing what is actually inside it.
