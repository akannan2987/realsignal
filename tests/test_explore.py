"""
tests/test_explore.py: the two Phase 2 explorers, on tiny made-up tables.

notebooks/explore_layer1.py and notebooks/explore_sources.py read real files
that are never committed, so these tests build small stand-ins with the same
columns: three rounds, a community grown in every round, one whose plants
were all left out, a two-contig genome and a two-sheet workbook. The numbers
they print must match what the stand-ins contain.

Run from the project folder:  pytest -q
"""

import gzip
import importlib.util
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]


def load(relative: str, name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def layer1(tmp_path, monkeypatch):
    """Made-up Layer 1 files with the published files' columns."""
    module = load("notebooks/explore_layer1.py", "explore_layer1")
    data = tmp_path / "Data"
    for path in (module.DESIGN, module.REASONS, module.PLANTS, module.ML_INPUT):
        relative = path.relative_to(module.DATA)
        monkeypatch.setattr(module, {module.DESIGN: "DESIGN", module.REASONS: "REASONS",
                                     module.PLANTS: "PLANTS", module.ML_INPUT: "ML_INPUT"}[path],
                            data / relative)
        (data / relative).parent.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(module, "DATA", data)
    monkeypatch.setattr(module, "ML_FOLDER", module.ML_INPUT.parent)
    strains = [f"Leaf{i}" for i in range(1, 7)]
    design = pd.DataFrame([[m] + v for m, v in [
        ("axenic", [0] * 6), ("Mix1", [1, 1, 1, 1, 1, 0]), ("Mix2", [0, 1, 1, 1, 1, 1]),
        ("Mix3", [1, 0, 1, 1, 1, 1]), ("Mix4", [1] * 6)]], columns=["Mix"] + strains)
    design.to_csv(module.DESIGN, sep="\t", index=False)
    plants, reasons, box = [], [], 0
    for exp, mixes in (("Exp1", ["Mix1", "Mix3"]), ("Exp2", ["Mix3"]), ("Exp3", ["Mix2", "Mix3"])):
        for mix in mixes + ["axenic"]:
            box += 1
            for plant in (1, 2):
                status = "FALSE" if (exp, mix) == ("Exp1", "Mix1") else "TRUE"
                plants.append([f"{box}_{plant}", box, plant, mix, "Pst", "x", status, exp])
                reasons.append([box, plant, status, "fungal contamination" if status == "FALSE" else None])
    pd.DataFrame(plants, columns=["Uid", "Box", "Plant", "Mix", "Infection", "FigureLabel",
                                  "IncludedAnalysis", "Experiment"]).to_csv(module.PLANTS, sep="\t", index=False)
    pd.DataFrame(reasons, columns=["Box", "Plant", "IncludedAnalysis", "ExclusionJustification"]).to_csv(
        module.REASONS, sep="\t", index=False)
    # Boxes 6 and 7 hold Mix2 and Mix3 in round 3: the plants the rule keeps.
    ml = pd.DataFrame([[uid, mix, "Exp3", "TRUE", 7.1, "Protected"] + presence
                       for uid, mix, presence in [
                           ("6_1", "Mix2", [0, 1, 1, 1, 1, 1]), ("6_2", "Mix2", [0, 1, 1, 1, 1, 1]),
                           ("7_1", "Mix3", [1, 0, 1, 1, 1, 1]), ("7_2", "Mix3", [1, 0, 1, 1, 1, 1])]],
                      columns=["Uid", "Mix", "Experiment", "IncludedAnalysis", "PathCFU", "Class"] + strains)
    ml.to_csv(module.ML_INPUT, sep="\t", index=False)
    return module


def test_layer1_explorer_counts_what_the_tables_hold(layer1, capsys):
    assert layer1.main() == 0
    out = capsys.readouterr().out
    assert "five-strain communities    : 3" in out
    assert "all strains together       : 1 (Mix4)" in out
    assert "grown in more than one round : Mix3" in out
    assert "labelled in the plant file   : Mix3 x" in out
    assert "rounds 1 and 2 only          : 1 communities (training)" in out
    assert "round 3 only                 : 1 communities (testing)" in out
    assert "communities with every plant left out: Mix1 (Exp1)" in out
    assert "Mix3 appears as : Exp3 only" in out
    assert "rebuilt from the plant file : 4 plants, the same ones: yes" in out
    assert "tables: 1 (1 with one row per plant, 0 with one row per community)" in out


def test_layer1_explorer_says_what_to_run_when_data_is_missing(tmp_path, monkeypatch, capsys):
    module = load("notebooks/explore_layer1.py", "explore_layer1_empty")
    monkeypatch.setattr(module, "DESIGN", tmp_path / "missing.txt")
    assert module.main() == 1
    assert "python scripts/fetch_data.py" in capsys.readouterr().out


def test_genome_statistics(tmp_path):
    module = load("notebooks/explore_sources.py", "explore_sources")
    path = tmp_path / "g.fna.gz"
    with gzip.open(path, "wt") as handle:
        handle.write(">contig_1\nGGCCAATT\n>contig_2\nGC\n")
    contigs, length, gc = module.genome_stats(path)
    assert (contigs, length) == (2, 10)
    assert gc == pytest.approx(60.0)


def test_strains_are_found_by_name_and_by_number():
    module = load("notebooks/explore_sources.py", "explore_sources_names")
    sheet = pd.DataFrame({0: ["Table 1", None, "Strain_ID", "15", "68", "999"],
                          1: [None, None, "Genus", "Pseudomonas", "Rhizobium", "Other"],
                          2: [None, None, "Partner", "Leaf76", None, None]})
    found = module.strains_mentioned(sheet, ["Leaf15", "Leaf68", "Leaf76", "Leaf21"])
    assert found == {"Leaf15", "Leaf68", "Leaf76"}


def test_workbook_description_counts_sheets_and_strains(tmp_path, capsys):
    """Two sheets: one names strains as Leaf15, the other as bare numbers under
    a Strain_ID heading, with an empty cell (which pandas 3 keeps as a number)."""
    module = load("notebooks/explore_sources.py", "explore_sources_book")
    path = tmp_path / "book.xlsx"
    with pd.ExcelWriter(path) as writer:
        pd.DataFrame([["Supplementary Table 1: strains"], ["Leaf15"], ["Leaf68"]]).to_excel(
            writer, sheet_name="ST1", header=False, index=False)
        pd.DataFrame([["Supplementary Table 2"], ["Strain_ID"], [76], [None]]).to_excel(
            writer, sheet_name="ST2", header=False, index=False)
    module.describe_workbook(path, ["Leaf15", "Leaf68", "Leaf76"])
    out = capsys.readouterr().out
    assert "2 sheets" in out
    rows = {line.split()[0]: line for line in out.splitlines() if "/3  " in line}
    assert "2/3  Supplementary Table 1: strains" in rows["ST1"]
    assert "1/3  Supplementary Table 2" in rows["ST2"]
    assert "    ST1       Leaf76" in out                     # the one strain ST1 leaves out
