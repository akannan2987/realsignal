"""
tests/test_exploration.py: the Phase 4 questions, on a made-up warehouse.

The real warehouse is never committed, so these tests build a small stand-in
with the marts' own columns: six strains in communities of two (not 35 in
fives, so nothing that assumes the real screen's size can pass), three rounds,
controls with and without the pathogen, the whole library, and a community
grown in every round. Its numbers are chosen so the answers are known in
advance: communities holding Leaf1 have about 10,000 times less pathogen,
one plant sits far from the rest of its community, and the normalised values
follow the rules Phase 4 works out from the real data.

The most important test changes every value measured on a test plant and
checks that the report, the explorer's output and every answer stay exactly
the same: the test set is sealed.

Run from the project folder:  pytest -q
"""

import contextlib
import importlib.util
import io
import itertools
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd
import pytest

from realsignal import exploration as ex

ROOT = Path(__file__).resolve().parents[1]

STRAINS = [f"Leaf{i}" for i in range(1, 7)]
PAIRS = list(itertools.combinations(STRAINS, 2))               # 15 communities of two
TRAINING = {f"Mix{i}": PAIRS[i - 1] for i in range(1, 13)}      # Mix1 to Mix12
TEST = {f"Mix{i}": PAIRS[i - 1] for i in range(13, 16)}         # Mix13 to Mix15
REFERENCE = "Mix15"                                             # also grown in Exp1 and Exp2
PLANTS_PER_BOX = 3
FAR_PLANT = "1_3"                                               # the planted outlier


def load(relative: str, name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def boxes():
    """(box, community, infected, round, split, mark), in box order."""
    rows, box = [], 0
    for i, community in enumerate(TRAINING):
        box += 1
        rows.append((box, community, True, "Exp1" if i % 2 == 0 else "Exp2", "training",
                     "TBD" if box == 3 else "TRUE"))
    for community in TEST:
        box += 1
        rows.append((box, community, True, "Exp3", "test", "TRUE"))
    for round_id in ("Exp1", "Exp2"):
        box += 1
        rows.append((box, REFERENCE, True, round_id, "between-round reference", "TRUE"))
    for round_id in ("Exp1", "Exp2", "Exp3"):
        for n, (community, infected) in enumerate((("axenic", True), ("axenic", True),
                                                   ("axenic", False), ("Mix16", True))):
            box += 1
            dropped = round_id == "Exp1" and n == 0          # a dropped box with no strains
            rows.append((box, community, infected, round_id, "control", "TBD" if dropped else "TRUE"))
    return rows


def pathogen(community: str, round_id: str, position: int, plant_id: str) -> float:
    """A log10 count: about 8 without Leaf1, about 4 with it, 9 with no strains."""
    shift = {"Exp1": 0.0, "Exp2": 0.2, "Exp3": 0.4}[round_id] + (position - 2) * 0.1
    if community == "axenic":
        return 9.0 + shift
    if community == "Mix16":
        return 3.0 + shift
    members = {**TRAINING, **TEST}[community]
    value = (4.0 if "Leaf1" in members else 8.0) + shift
    return value - 3.0 if plant_id == FAR_PLANT else value


def build(path: Path, test_value=None, reverse=False) -> None:
    """The stand-in warehouse. test_value, if given, replaces every value
    measured on a test plant (the sealing test). reverse inserts every table's
    rows in the opposite order, so a query without ORDER BY hands them back in
    another order (the row-order test)."""
    def ordered(rows):
        return list(reversed(rows)) if reverse else rows

    con = duckdb.connect(str(path))
    con.execute("create schema marts")
    con.execute("create schema raw")
    con.execute("create table raw.load_log (table_name varchar, source_id varchar, rows bigint, "
                "sha256 varchar)")
    con.execute("insert into raw.load_log values ('screen_plants', 'toy', 10, 'abc'), "
                "('source_register', 'register', 4, 'changes with line endings')")
    communities = {"axenic": ("axenic", 0, "no strains", "control"),
                   "Mix16": ("SynCom-6", 6, "whole library", "control")}
    communities.update({c: (c, 2, "community", "training") for c in TRAINING})
    communities.update({c: (("SynCom-Ref" if c == REFERENCE else c), 2, "community", "test") for c in TEST})
    con.execute("create table marts.dim_community (community_id varchar, label varchar, "
                "community_size integer, kind varchar, role varchar, has_plants_for_modelling boolean)")
    con.executemany("insert into marts.dim_community values (?, ?, ?, ?, ?, true)",
                    ordered([[c, *v] for c, v in communities.items()]))
    members = [(c, s) for c, team in {**TRAINING, **TEST}.items() for s in team]
    members += [("Mix16", s) for s in STRAINS]
    con.execute("create table marts.community_member (community_id varchar, strain_id varchar)")
    con.executemany("insert into marts.community_member values (?, ?)", ordered(members))
    con.execute("create table marts.dim_strain (strain_id varchar, in_screen_library boolean, "
                "genome_length_bp bigint, gc_percent double, clusters_listed integer, "
                "potentially_inhibitory_clusters integer, inhibits integer, inhibited_by integer)")
    con.executemany("insert into marts.dim_strain values (?, true, ?, ?, ?, ?, ?, ?)",
                    ordered([[s, 4_000_000 + 100_000 * i, 60.0 + i, i, i % 2, 6 - i, i]
                             for i, s in enumerate(STRAINS, 1)]
                            + [["Leaf99", None, None, None, None, None, None]]))
    con.execute("update marts.dim_strain set in_screen_library = false where strain_id = 'Leaf99'")

    plants, measurements, model = [], [], []
    for box, community, infected, round_id, split, mark in boxes():
        for position in range(1, PLANTS_PER_BOX + 1):
            plant_id = f"{box}_{position}"
            use = split in ("training", "test")
            plants.append([plant_id, box, round_id, community, "Pst" if infected else None, mark, split, use])
            rows = {"fresh_weight": 30.0 + box + position}
            if infected:
                rows[ex.PATHOGEN_LOG10] = pathogen(community, round_id, position, plant_id)
                rows["pathogen_cfu_per_g"] = 10 ** rows[ex.PATHOGEN_LOG10]
            if community != "axenic":
                rows[ex.COMMENSAL_LOG10] = 8.0 + 0.01 * position
            for name, value in rows.items():
                measurements.append([plant_id, name, None, value, False])
            if communities[community][1] == 2:
                for strain in {**TRAINING, **TEST}[community]:
                    measurements.append([plant_id, ex.STRAIN_LOG10, strain, 7.0, strain == "Leaf2"])
            if use:
                outcome = rows[ex.PATHOGEN_LOG10]
                model.append([plant_id, community, round_id, split, mark, ex.PATHOGEN_LOG10, outcome])
    con.execute("create table marts.fct_plant (plant_id varchar, box_id integer, round_id varchar, "
                "community_id varchar, pathogen varchar, inclusion_mark varchar, split varchar, "
                "use_for_modelling boolean)")
    con.executemany("insert into marts.fct_plant values (?, ?, ?, ?, ?, ?, ?, ?)", ordered(plants))
    con.execute("create table marts.fct_plant_measurement (plant_id varchar, measurement varchar, "
                "strain_id varchar, value double, is_ambiguous boolean)")
    con.executemany("insert into marts.fct_plant_measurement values (?, ?, ?, ?, ?)", ordered(measurements))
    # The two normalised measurements, made by the rules Phase 4 works out:
    # the pathogen minus the median of the round's infected plants with no
    # strains, and the weight divided by the healthy plants' median in Exp1.
    con.execute(f"""
        insert into marts.fct_plant_measurement
        with base as (
            select p.round_id, median(m.value) as median
            from marts.fct_plant_measurement as m join marts.fct_plant as p using (plant_id)
            where m.measurement = '{ex.PATHOGEN_LOG10}' and p.community_id = 'axenic'
            group by 1)
        select m.plant_id, '{ex.PATHOGEN_NORMALISED}', null, m.value - base.median, false
        from marts.fct_plant_measurement as m
        join marts.fct_plant as p using (plant_id)
        join base using (round_id)
        where m.measurement = '{ex.PATHOGEN_LOG10}'""")
    healthy = con.execute("""select median(m.value) from marts.fct_plant_measurement m
                             join marts.fct_plant p using (plant_id)
                             where m.measurement = 'fresh_weight' and p.community_id = 'axenic'
                               and p.pathogen is null and p.round_id = 'Exp1'""").fetchone()[0]
    con.execute(f"""insert into marts.fct_plant_measurement
                    select plant_id, '{ex.FRESH_WEIGHT_NORMALISED}', null, value / {healthy}, false
                    from marts.fct_plant_measurement where measurement = 'fresh_weight'""")
    con.execute("create table marts.model_plants (plant_id varchar, community_id varchar, round_id varchar, "
                "split varchar, inclusion_mark varchar, outcome_measurement varchar, outcome double)")
    con.executemany("insert into marts.model_plants values (?, ?, ?, ?, ?, ?, ?)", ordered(model))
    if test_value is not None:
        # Every value on a test plant, normalised ones included, made nonsense.
        test_plants = "select plant_id from marts.fct_plant where split = 'test'"
        con.execute(f"update marts.fct_plant_measurement set value = ? where plant_id in ({test_plants})",
                    [test_value])
        con.execute(f"update marts.model_plants set outcome = ? where plant_id in ({test_plants})",
                    [test_value])
    con.close()


@pytest.fixture
def warehouse(tmp_path, monkeypatch):
    path = tmp_path / "realsignal.duckdb"
    build(path)
    monkeypatch.setattr(ex, "WAREHOUSE", path)
    return path


def run(module, *args):
    """A script's main(), with what it prints."""
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = module.main(*args)
    return code, out.getvalue()


def test_the_stand_in_uses_only_documented_columns():
    """Every column the stand-in invents is one the real marts document."""
    yaml = pytest.importorskip("yaml")              # comes with dbt
    documented = {m["name"]: {c["name"] for c in m.get("columns", [])} for m in
                  yaml.safe_load((ROOT / "dbt" / "models" / "marts" / "_marts.yml").read_text())["models"]}
    tables = {"dim_community": {"community_id", "label", "community_size", "kind", "role",
                                "has_plants_for_modelling"},
              "community_member": {"community_id", "strain_id"},
              "dim_strain": {"strain_id", "in_screen_library"} | set(ex.STRAIN_FEATURES),
              "fct_plant": {"plant_id", "box_id", "round_id", "community_id", "pathogen",
                            "inclusion_mark", "split", "use_for_modelling"},
              "fct_plant_measurement": {"plant_id", "measurement", "strain_id", "value", "is_ambiguous"},
              "model_plants": {"plant_id", "community_id", "round_id", "split", "inclusion_mark",
                               "outcome_measurement", "outcome"}}
    for table, columns in tables.items():
        assert columns <= documented[table], f"{table}: {sorted(columns - documented[table])}"


def test_the_answers_are_the_ones_built_in(warehouse):
    con = ex.open_warehouse()
    a = ex.answers(con)
    con.close()
    shape = a["shape"]
    assert shape["plants"] == 12 * PLANTS_PER_BOX and shape["communities"] == 12
    assert shape["rounds"] == ["Exp1", "Exp2"]
    assert len(shape["peaks"]) == 2 and shape["peaks"][0] < shape["dip"] < shape["peaks"][1]
    # Leaf1 is in 5 of the 15 pairs, 5 of them training: the only strain to stand out.
    assert a["strains"]["stands_out"] == ["Leaf1"]
    row = a["strains"]["table"].set_index("strain_id").loc["Leaf1"]
    assert row["communities_with"] == 5 and row["difference"] < -3
    # The planted outlier, and nothing else.
    assert list(a["outliers"]["listed"]["plant_id"]) == [FAR_PLANT]
    # Design: membership only, test communities included.
    d = a["design"]
    assert d["library"] == 6 and d["sizes"] == [2]
    assert d["communities"] == {"training": 12, "test": 3}
    assert d["pairs"] == 15 and d["pairs_never_together"] == 3          # the three test pairs
    assert int(d["counts"].loc["Leaf1", "training"]) == 5
    # Nothing missing among the plants used for modelling.
    assert int(a["missing"]["used_missing"].sum()) == 0
    assert a["missing"]["strain_counts_short"] == 0
    # The normalised values are recognised for what they are.
    assert a["normalisation"]["pathogen"]["matching"] == a["normalisation"]["pathogen"]["plants"]
    weight = a["normalisation"]["weight"]
    assert weight["one_number"] and weight["matching_rounds"] == ["Exp1"]
    # Round shifts: the whole library moved +0.2 from Exp1 to Exp2, as built.
    shifts = a["shifts"].set_index(["group", "later_round"])["shift"]
    assert shifts[("whole library", "Exp2")] == pytest.approx(0.2)
    # The undecided box is compared within its round.
    assert [r["group"] for r in a["undecided"]] == ["training", "no strains, infected"]


def test_the_test_set_stays_sealed(tmp_path, monkeypatch):
    """Change every value measured on a test plant: no answer may move."""
    report = load("scripts/make_quality_report.py", "make_quality_report_sealed")
    explorer = load("notebooks/explore_marts.py", "explore_marts_sealed")
    outputs = []
    for name, value in (("before", None), ("after", 999.0)):
        path = tmp_path / f"{name}.duckdb"
        build(path, test_value=value)
        monkeypatch.setattr(ex, "WAREHOUSE", path)
        con = ex.open_warehouse()
        text = report.render(ex.answers(con))
        con.close()
        outputs.append((text, run(explorer)[1]))
    with duckdb.connect(str(tmp_path / "after.duckdb"), read_only=True) as con:
        changed = con.execute("select count(*) from marts.model_plants where outcome = 999").fetchone()[0]
    assert changed == len(TEST) * PLANTS_PER_BOX                    # the change really happened
    assert outputs[0][0] == outputs[1][0]
    assert outputs[0][1] == outputs[1][1]


def test_the_answers_do_not_depend_on_row_order(tmp_path, monkeypatch):
    """A query without ORDER BY may hand rows back in any order, which can differ
    between computers. The same tables with every row inserted the other way
    round must give the same report and the same shuffle thresholds."""
    report = load("scripts/make_quality_report.py", "make_quality_report_order")
    results = []
    for name, reverse in (("forward", False), ("reversed", True)):
        path = tmp_path / f"{name}.duckdb"
        build(path, reverse=reverse)
        monkeypatch.setattr(ex, "WAREHOUSE", path)
        con = ex.open_warehouse()
        a = ex.answers(con)
        con.close()
        results.append((report.render(a), a["strains"]["threshold"], a["layers"]["threshold"]))
    assert results[0] == results[1]


def test_the_shuffle_test_does_not_depend_on_row_order(tmp_path):
    """Question 7's shuffle test on 20 strains, enough for the threshold to show
    a difference: the strains' properties inserted in one order and then in the
    other must give the same correlations and the same threshold."""
    rng = np.random.default_rng(3)
    strains = [f"Leaf{i}" for i in range(1, 21)]
    rows = [[s, True, 3_000_000 + 50_000 * int(rng.integers(0, 80)), float(rng.uniform(55, 70)),
             int(rng.integers(0, 15)), int(rng.integers(0, 5)), int(rng.integers(0, 40)),
             int(rng.integers(0, 6))] for s in strains]
    differences = pd.DataFrame({"strain_id": strains, "difference": rng.normal(0, 0.8, len(strains))})
    answers = []
    for name, ordered in (("forward", rows), ("reversed", rows[::-1])):
        con = duckdb.connect(str(tmp_path / f"{name}.duckdb"))
        con.execute("create schema marts")
        con.execute("create table marts.dim_strain (strain_id varchar, in_screen_library boolean, "
                    "genome_length_bp bigint, gc_percent double, clusters_listed integer, "
                    "potentially_inhibitory_clusters integer, inhibits integer, inhibited_by integer)")
        con.executemany("insert into marts.dim_strain values (?, ?, ?, ?, ?, ?, ?, ?)", ordered)
        # Empty plant tables: no commensal load to compare, which layers() allows.
        con.execute("create table marts.dim_community (community_id varchar, label varchar, "
                    "community_size integer, kind varchar, role varchar, has_plants_for_modelling boolean)")
        con.execute("create table marts.fct_plant (plant_id varchar, box_id integer, round_id varchar, "
                    "community_id varchar, pathogen varchar, inclusion_mark varchar, split varchar, "
                    "use_for_modelling boolean)")
        con.execute("create table marts.fct_plant_measurement (plant_id varchar, measurement varchar, "
                    "strain_id varchar, value double, is_ambiguous boolean)")
        con.execute("create table marts.model_plants (plant_id varchar, community_id varchar, "
                    "round_id varchar, split varchar, inclusion_mark varchar, outcome_measurement varchar, "
                    "outcome double)")
        found = ex.layers(con, differences)
        con.close()
        answers.append((found["threshold"], list(found["table"]["rho"])))
    assert answers[0] == answers[1]


def test_no_query_hands_over_a_test_value(warehouse):
    """The seal itself: values() never returns a test plant, whatever the measurement."""
    con = ex.open_warehouse()
    kinds = [r[0] for r in con.execute("select distinct measurement from marts.fct_plant_measurement").fetchall()]
    for measurement in kinds:
        assert "test" not in set(ex.values(con, measurement)["split"]), measurement
    assert set(ex.training_outcomes(con)["plant_id"]).isdisjoint(
        r[0] for r in con.execute("select plant_id from marts.fct_plant where split = 'test'").fetchall())
    con.close()


def test_the_report_comes_out_the_same_every_time(warehouse, tmp_path, monkeypatch):
    report = load("scripts/make_quality_report.py", "make_quality_report_twice")
    monkeypatch.setattr(report, "REPORT", tmp_path / "reports" / "data-quality.md")
    monkeypatch.setattr(report, "PROJECT_ROOT", tmp_path)
    first = run(report)
    content = report.REPORT.read_bytes()
    second = run(report)
    assert first[0] == second[0] == 0
    assert "new" in first[1] and "unchanged" in second[1]
    assert report.REPORT.read_bytes() == content
    text = content.decode("utf-8")
    assert "\r" not in text and "## 7. How the other layers relate" in text
    assert "Leaf1 | 5 |" in text


def test_the_explorer_prints_short_clean_lines(warehouse):
    explorer = load("notebooks/explore_marts.py", "explore_marts_lines")
    code, out = run(explorer)
    assert code == 0
    lines = out.splitlines()
    assert lines[0].startswith("EXPLORING THE MARTS")
    assert not [line for line in lines if len(line) > 80], "lines over 80 characters"
    assert not [line for line in lines if line != line.rstrip()], "trailing spaces"
    assert "standing out: Leaf1" in out


def test_a_missing_warehouse_is_explained(tmp_path, monkeypatch):
    monkeypatch.setattr(ex, "WAREHOUSE", tmp_path / "nothing.duckdb")
    with pytest.raises(ex.WarehouseNotReady, match="python scripts/load_raw.py"):
        ex.open_warehouse()
    explorer = load("notebooks/explore_marts.py", "explore_marts_missing")
    code, out = run(explorer)
    assert code == 1 and "No warehouse yet" in out


def test_two_humps_are_found_where_they_are():
    rng = np.random.default_rng(1)
    y = np.concatenate([rng.normal(4.5, 0.4, 300), rng.normal(8.0, 0.5, 500)])
    found = ex.humps(y)
    assert found["peaks"][0] == pytest.approx(4.5, abs=0.2)
    assert found["peaks"][1] == pytest.approx(8.0, abs=0.2)
    assert 5.0 < found["dip"] < 7.5


def test_the_figures_draw_from_a_different_screen(warehouse, tmp_path, monkeypatch):
    figures = load("figures/make_phase4_figures.py", "make_phase4_figures_toy")
    monkeypatch.setattr(figures, "OUT", tmp_path)
    monkeypatch.setattr(figures, "ROOT", tmp_path)
    code, out = run(figures)
    assert code == 0
    drawn = sorted(p.name for p in tmp_path.glob("*.png"))
    assert drawn == ["missing_values.png", "one_strain_at_a_time.png", "outcome_shape.png",
                     "rounds_compared.png", "strain_frequency.png"]
