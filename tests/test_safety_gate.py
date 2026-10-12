"""
tests/test_safety_gate.py: the safety gate (check-public-safe.sh) has tests too.

A guard nobody tests can quietly stop guarding. Each test builds a small,
throw-away Git repository in a temporary folder, copies the gate into it,
plants one thing that must never be published, and checks that the gate
refuses. A clean repository must pass.

The gate is a bash script, so these tests need bash. On Windows they run only
when pytest is started from Git Bash (which sets MSYSTEM); from PowerShell they
are skipped, because the "bash" found there may be WSL's, which can't read
Windows paths.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

GATE = Path(__file__).resolve().parents[1] / "check-public-safe.sh"
ON_WINDOWS_OUTSIDE_GIT_BASH = sys.platform == "win32" and "MSYSTEM" not in os.environ
pytestmark = pytest.mark.skipif(
    shutil.which("bash") is None or shutil.which("git") is None or ON_WINDOWS_OUTSIDE_GIT_BASH,
    reason="needs bash and git (on Windows, run pytest from Git Bash)")


def git(folder: Path, *args: str) -> None:
    """Run one git command inside the test repository."""
    subprocess.run(["git", *args], cwd=folder, check=True, capture_output=True)


def run_gate(folder: Path) -> subprocess.CompletedProcess:
    return subprocess.run(["bash", "check-public-safe.sh"], cwd=folder, capture_output=True, text=True)


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """A tiny repository with the gate, a README and the project's ignore rules."""
    git(tmp_path, "init", "-q")
    git(tmp_path, "config", "user.email", "test@example.com")
    git(tmp_path, "config", "user.name", "Test")
    shutil.copy(GATE, tmp_path / "check-public-safe.sh")
    (tmp_path / "README.md").write_text("# A tiny project\n", encoding="utf-8")
    (tmp_path / ".gitignore").write_text(".venv/\ndata/\n.env\n.local-notes/\n.DS_Store\n", encoding="utf-8")
    git(tmp_path, "add", "-A")
    git(tmp_path, "commit", "-q", "-m", "start")
    return tmp_path


def test_a_clean_repository_is_safe(repo):
    result = run_gate(repo)
    assert result.returncode == 0, result.stdout
    assert "SAFE TO PUSH" in result.stdout


def test_a_new_file_with_a_key_is_caught_before_it_is_added(repo):
    fake_key = "sk-" + "a1b2c3d4" * 4            # built here, so this file holds no key-shaped text
    (repo / "notes.md").write_text(f"my key is {fake_key}\n", encoding="utf-8")
    result = run_gate(repo)
    assert result.returncode == 1
    assert "credential" in result.stdout


def test_force_added_data_is_caught(repo):
    (repo / "data" / "raw").mkdir(parents=True)
    (repo / "data" / "raw" / "table.csv").write_text("a,b\n1,2\n", encoding="utf-8")
    git(repo, "add", "-f", "data/raw/table.csv")
    result = run_gate(repo)
    assert result.returncode == 1
    assert "WOULD BE PUBLISHED: data" in result.stdout


def test_a_home_folder_path_is_caught(repo):
    home = "/" + "Users" + "/somebody/"          # split, so this file doesn't trip the gate itself
    (repo / "guide.md").write_text(f"open {home}projects/x\n", encoding="utf-8")
    assert run_gate(repo).returncode == 1


def test_placeholders_and_link_anchors_are_fine(repo):
    anchor = "#task-" + "a" * 30                 # contains "sk-" followed by a long run
    (repo / "guide.md").write_text(f"open /Users/<you>/projects/x, see [it]({anchor})\n", encoding="utf-8")
    result = run_gate(repo)
    assert result.returncode == 0, result.stdout


def test_a_tracked_ds_store_is_caught(repo):
    (repo / "sub").mkdir()
    (repo / "sub" / ".DS_Store").write_bytes(b"\x00\x00")
    git(repo, "add", "-f", "sub/.DS_Store")
    result = run_gate(repo)
    assert result.returncode == 1
    assert "git rm --cached" in result.stdout


def test_a_picture_with_hidden_records_is_caught(repo):
    marker = "c2" + "pa"                         # built here, so this file holds no marker
    (repo / "plain.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg"></svg>\n', encoding="utf-8")
    (repo / "logo.svg").write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg"><metadata><{marker}:manifest>x</{marker}:manifest>'
        "</metadata></svg>\n", encoding="utf-8")
    result = run_gate(repo)
    assert result.returncode == 1
    assert "hidden records" in result.stdout
    assert "logo.svg" in result.stdout
    assert "plain.svg" not in result.stdout
