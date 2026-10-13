"""
tests/test_warehouse.py: the whole Phase 3 pipeline on a made-up screen.

The real screen has 35 strains in communities of five. Nothing in the dbt
models is supposed to know that, so this test makes up a different screen,
with files laid out exactly like the real ones, and runs the real loader
(scripts/load_raw.py) and the real dbt project on it:

  * a library of 4 strains, in communities of 2, with 2 plants to a box;
  * two training communities (rounds Exp1 and Exp2), two test communities
    (Exp3), one of them also grown in Exp1, like the real reference ones;
  * a box marked TBD, a plant marked FALSE, two strains with no inhibition
    seen, and a strain with no genome.

If a model had 35 or 5 written into it, the counts below would come out
wrong. The test then builds once more with keep_undecided_plants set to
false, to check that Choice 1 is a setting and not a rewrite.

The tests that compare the real sources with seeds/known_source_differences.csv
are left out here, since a made-up screen has different strains. They run on
the real data in every dbt build.

It takes about half a minute, most of it dbt starting up. Skipped if dbt
isn't installed. Run from the project folder:  pytest -q
"""

import gzip
import importlib.util
import math
import shutil
import subprocess
import sys
from pathlib import Path

import duckdb
import pytest

pytest.importorskip("dbt.cli.main")          # skipped where dbt isn't installed
openpyxl = pytest.importorskip("openpyxl")

ROOT = Path(__file__).resolve().parents[1]

# The made-up screen ---------------------------------------------------------
STRAINS = ["Leaf1", "Leaf2", "Leaf3", "Leaf4"]
COMMUNITIES = {"axenic": [], "Mix1": ["Leaf1", "Leaf2"], "Mix2": ["Leaf3", "Leaf4"],
               "Mix3": ["Leaf1", "Leaf3"], "Mix4": ["Leaf2", "Leaf4"], "Mix5": STRAINS}
# box: (community, infection, round)
BOXES = {1: ("axenic", "NI", "Exp1"), 2: ("axenic", "Pst", "Exp1"), 3: ("Mix1", "Pst", "Exp1"),
         4: ("Mix4", "Pst", "Exp1"), 5: ("Mix2", "Pst", "Exp2"), 6: ("Mix5", "Pst", "Exp2"),
         7: ("Mix3", "Pst", "Exp3"), 8: ("Mix4", "Pst", "Exp3")}
PLANTS_PER_BOX = 2
MARKS = {"5_1": ("TBD", "box dropped"), "5_2": ("TBD", "box dropped"),
         "7_2": ("FALSE", "fungal contamination")}
GENOMES = {"Leaf1": "GCF_000000001.1", "Leaf2": "GCF_000000002.1", "Leaf3": "GCF_000000003.1"}
# The plants the rules should pick with the default settings.
EXPECTED = {"3_1", "3_2", "5_1", "5_2", "7_1", "8_1", "8_2"}


def tsv(path: Path, header: list, rows: list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["\t".join(header)] + ["\t".join("" if v is None else str(v) for v in row) for row in rows]
    path.write_text("\n".join(lines) + "\n")


def sheet(book, name: str, heading_rows: list, rows: list, after: list = ()) -> None:
    """A sheet laid out like the journals': a title, a blank row, then the headings."""
    ws = book.create_sheet(name)
    ws.append([f"Supplementary {name}: a made-up table"])
    for row in heading_rows + rows + list(after):
        ws.append(row)


def plants():
    for box, (community, infection, round_id) in BOXES.items():
        for position in range(1, PLANTS_PER_BOX + 1):
            yield f"{box}_{position}", box, position, community, infection, round_id


def build_files(project: Path) -> None:
    """Every raw file of sources/tables.csv, made up, at its real path."""
    data = project / "data" / "raw" / "extracted" / "Data"
    meta = data / "MetaData" / "Mini5SynComScreen"
    clean = data / "CleanData" / "2023-01-16Mini5SynComScreen_"

    tsv(meta / "20200828_Mixes.txt", ["Mix"] + STRAINS,
        [[c] + [int(s in members) for s in STRAINS] for c, members in COMMUNITIES.items()])
    tsv(meta / "20200828_Box.txt",
        ["Box", "Mix", "Infection", "Replicate", "Experiment", "Unique_Mix", "Initial_Mix", "Comment_General"],
        [[b, c, i, 1, r, f"{b}_{c}", c, "box dropped" if b == 5 else None]
         for b, (c, i, r) in BOXES.items()])
    labels = {"Mix4": "SynCom-Ref"}
    tsv(data / "CleanData" / "2023-01-16Mini5SynComScreen_CommentsFile.txt",
        ["Uid", "Box", "Plant", "Mix", "Infection", "FigureLabel", "IncludedAnalysis", "Experiment"],
        [[u, b, p, c, i, labels.get(c, c + ("_NI" if i == "NI" else "")),
          MARKS.get(u, ("TRUE",))[0], r] for u, b, p, c, i, r in plants()])
    tsv(meta / "20201130_Comments.txt",
        ["Box", "Plant", "IncludedAnalysis", "ExclusionJustification", "Comment_General",
         "Comment_Infection", "Comment_Weight", "Comment_Harvest", "Comment_CommensalCount"],
        [[b, p, MARKS.get(u, ("TRUE",))[0], MARKS.get(u, (None, None))[1], None, None, None, None, None]
         for u, b, p, c, i, r in plants()])
    infected = [x for x in plants() if x[4] == "Pst"]
    tsv(Path(str(clean) + "PathogenCFUs.txt"), ["Uid", "CFUgFW", "LogCFUgFW", "NormLogCFUgFW"],
        [[u, 10 ** (5 + b / 10), 5 + b / 10, b / 10 - 3] for u, b, *_ in infected])
    tsv(Path(str(clean) + "Weights.txt"), ["Uid", "PlantWeight", "NormPlantWeight"],
        [[u, 30 + b, 1.0] for u, b, *_ in plants()])
    with_strains = [x for x in plants() if COMMUNITIES[x[3]]]
    tsv(Path(str(clean) + "TotalCommensalCFU.txt"), ["Uid", "CFUgFW", "LogCFUgFW"],
        [[u, 1e8, 8.0] for u, *_ in with_strains])
    tsv(Path(str(clean) + "IndividualStrainColonization.txt"),
        ["Uid", "Strain_ID", "AmbiguousSingleStrains", "CFUgFW", "LogCFUgFW"],
        [[u, s, "FALSE", 1e7, 7.0] for u, b, p, c, *_ in with_strains for s in COMMUNITIES[c]])
    tsv(data / "EditedData" / "ML_DataInput" / "MLData_DF_Ind_TRUE_CommPresence.txt",
        ["Uid", "Mix", "Experiment", "IncludedAnalysis", "PathCFU", "Class"] + STRAINS,
        [[u, c, r, MARKS.get(u, ("TRUE",))[0], 6.0, "Protected"] + [int(s in COMMUNITIES[c]) for s in STRAINS]
         for u, b, p, c, i, r in plants() if u in EXPECTED])
    taxonomy = ["Proteobacteria", "Alphaproteobacteria", "Rhizobiaceae", "Rhizobium"]
    tsv(data / "MetaData" / "AtSPHERE" / "dataAtLSPHERE.txt",
        ["Strain_ID", "Phylum", "Class", "Family", "Genus", "Genomes_published_Bai2015", "ExtendedAtSPHERE"],
        [[s] + taxonomy + ["yes" if s in GENOMES else "no", "NA"] for s in STRAINS]
        + [["Leaf9"] + taxonomy + ["NA", "extended"]])

    # Layers 3 and 4: one workbook, five sheets laid out as in the real one.
    helfrich = openpyxl.Workbook()
    helfrich.remove(helfrich.active)
    screened = STRAINS + ["Leaf9"]
    sheet(helfrich, "Table_S1", [[], ["Inhibitor", "Sensitive", "Interaction", "Medium"]],
          [["Leaf1", "Leaf2", "weak", "R2AM"], ["Leaf9", "Leaf1", "strong", "R2AM; MMGlcM"]])
    sheet(helfrich, "Table_S4", [[], [None, None, "Toy sp. Leaf2", None, "Toy sp. Leaf3", None],
                                 ["Inhibitor", "Genus", "R2A+M", "R2A", "R2A+M", "R2A"]],
          [[s, "Rhizobium", "none", "none", "none", "none"] for s in screened])
    sheet(helfrich, "Table_S24", [[], ["Strain", "Genus", "Medium1", "Medium2"]],
          [[s, "Rhizobium", "R2A+M", None] for s in screened],
          after=[["*a footnote under the table"]])
    counts = {"Leaf1": (1, 1), "Leaf2": (0, 1), "Leaf3": (1, 0), "Leaf9": (0, 0)}
    sheet(helfrich, "Table_S9", [[], ["Strain", "Genus", "NRPS", "terpene", "Total"]],
          [[s, "Rhizobium", a, b, a + b] for s, (a, b) in counts.items()],
          after=[["Total", None, 2, 2, 4], ["Strain", "Genus", "NRPS", "terpene", "Total"],
                 [None, None, None, None, 1.0]])
    sheet(helfrich, "Table_S11", [[], ["Strain", "Genus", "Accession", "Cluster", "AntiSMASH BGC_type",
                                       "Potentially_inhibitory", "Start", "End", "Genes"]],
          [["Leaf1", "Rhizobium", "AAA101000001.1", 1, "nrps", "put_inhib (toxin)", 1, 40, "g1;g2"],
           ["Leaf1", "Rhizobium", "AAA101000002.1", 2, "terpene", None, 5, 20, "g3"],
           ["Leaf2", "Rhizobium", "AAA201000001.1", 1, "terpene", None, 1, 30, "g1"],
           ["Leaf3", "Rhizobium", "AAA301000001.1", 1, "nrps", "put_inhib", 2, 50, "g1;g2;g3"]])
    path = project / "data" / "raw" / "sources" / "helfrich2018_supplement" / "41564_2018_200_MOESM3_ESM.xlsx"
    path.parent.mkdir(parents=True)
    helfrich.save(path)

    # Layer 5: the strain list, with the bare-number column and a footnote.
    vogel = openpyxl.Workbook()
    vogel.remove(vogel.active)
    sheet(vogel, "ST12", [[], ["Strain", "Strain_ID", "Phylum", "Class", "Order", "Family", "Genus1",
                               "RefSeq_Assembly_Accession", "Comment"]],
          [[s, int(s[4:]), taxonomy[0], taxonomy[1], "Hyphomicrobiales", taxonomy[2],
            taxonomy[3] + ("" if s in GENOMES else "*"), GENOMES.get(s), "At-LSPHERE"] for s in screened],
          after=[["1The genus information is a made-up footnote."]])
    path = project / "data" / "raw" / "sources" / "vogel2021_supplement" / "41564_2021_997_MOESM3_ESM.xlsx"
    path.parent.mkdir(parents=True)
    vogel.save(path)

    # Layer 2: Leaf1's genome in two contigs, Leaf2 and Leaf3 in one each, Leaf4 none.
    folder = project / "data" / "raw" / "sources" / "refseq_genomes"
    folder.mkdir(parents=True)
    for n, (strain, accession) in enumerate(GENOMES.items(), 1):
        with gzip.open(folder / f"{strain}_{accession}_genomic.fna.gz", "wt") as handle:
            for contig in range(1, 3 if strain == "Leaf1" else 2):
                handle.write(f">NZ_AAA{n}01{contig:06d}.1 Toy sp. {strain} contig_{contig}\n")
                handle.write("ACGTGC" * 10 + "\n")


def build_sources(project: Path) -> None:
    """sources/: the real table list, and a register and file list for the made-up screen."""
    from realsignal.helpers import file_hashes
    sources = project / "sources"
    sources.mkdir()
    shutil.copy(ROOT / "sources" / "tables.csv", sources / "tables.csv")
    ids = ["emmenegger2023_archive", "refseq_genomes", "helfrich2018_supplement", "vogel2021_supplement"]
    (sources / "register.csv").write_text(
        "source_id,layer,layer_name,what_it_holds,citation,doi,where_from,terms,status,checked_on,notes\n"
        + "".join(f"{s},{n},toy,toy,toy,10.0/toy,toy,toy,fetched,2026-01-01,\n" for n, s in enumerate(ids, 1)))
    raw = project / "data" / "raw" / "sources"
    lines = ["file_id,source_id,kind,location,target,published_md5,pinned_sha256,same_as,strain"]
    for file_id, source, name in (("helfrich2018_tables", ids[2], "41564_2018_200_MOESM3_ESM.xlsx"),
                                  ("vogel2021_tables", ids[3], "41564_2021_997_MOESM3_ESM.xlsx")):
        pin = file_hashes(raw / source / name)[1]
        lines.append(f"{file_id},{source},url,https://example.org/{name},{name},,{pin},,")
    for strain, accession in GENOMES.items():
        lines.append(f"genome_{strain},refseq_genomes,ncbi_assembly,{accession},"
                     f"{strain}_{accession}_genomic.fna.gz,,,,{strain}")
    (sources / "files.csv").write_text("\n".join(lines) + "\n")


def run_dbt(project: Path, extra: list) -> None:
    """dbt build, in a process of its own, so it lets go of the database when it ends."""
    profiles = project / "profiles"
    profiles.mkdir(exist_ok=True)
    warehouse = (project / "data" / "warehouse" / "realsignal.duckdb").as_posix()
    (profiles / "profiles.yml").write_text(
        f"realsignal:\n  target: local\n  outputs:\n    local:\n      type: duckdb\n"
        f"      path: '{warehouse}'\n      threads: 4\n")
    result = subprocess.run(
        [sys.executable, "-m", "dbt.cli.main", "build", "--project-dir", str(ROOT / "dbt"),
         "--profiles-dir", str(profiles), "--target-path", str(project / "target"),
         "--log-path", str(project / "logs"), "--exclude", "known_source_differences+"] + extra,
        capture_output=True, text=True)
    report = [line for line in result.stdout.splitlines() if "FAIL" in line or "ERROR" in line]
    assert result.returncode == 0, "\n".join(report or result.stdout.splitlines()[-20:])


@pytest.fixture(scope="module")
def warehouse(tmp_path_factory):
    project = tmp_path_factory.mktemp("mini_screen")
    build_files(project)
    build_sources(project)
    spec = importlib.util.spec_from_file_location("load_raw_mini", ROOT / "scripts" / "load_raw.py")
    loader = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loader)
    loader.PROJECT_ROOT = project
    loader.SOURCES_DIR = project / "sources"
    loader.TABLES_PATH = project / "sources" / "tables.csv"
    loader.WAREHOUSE = project / "data" / "warehouse" / "realsignal.duckdb"
    assert loader.main([]) == 0
    run_dbt(project, [])
    con = duckdb.connect(str(loader.WAREHOUSE), read_only=True)
    yield project, con
    con.close()


def test_communities_are_sized_and_placed_from_the_data(warehouse):
    _, con = warehouse
    rows = dict(((c, (size, kind, role)) for c, size, kind, role in con.execute(
        "select community_id, community_size, kind, role from marts.dim_community").fetchall()))
    assert rows == {"axenic": (0, "no strains", "control"), "Mix1": (2, "community", "training"),
                    "Mix2": (2, "community", "training"), "Mix3": (2, "community", "test"),
                    "Mix4": (2, "community", "test"), "Mix5": (4, "whole library", "control")}


def test_the_plants_follow_the_three_choices(warehouse):
    _, con = warehouse
    chosen = {r[0] for r in con.execute("select plant_id from marts.model_plants").fetchall()}
    assert chosen == EXPECTED                       # TBD kept, FALSE left out
    reference = {r[0] for r in con.execute(
        "select plant_id from marts.fct_plant where split = 'between-round reference'").fetchall()}
    assert reference == {"4_1", "4_2"}              # Mix4 before the test round
    splits = dict(con.execute("select split, count(*) from marts.model_plants group by 1").fetchall())
    assert splits == {"training": 4, "test": 3}


def test_strains_from_every_layer(warehouse):
    _, con = warehouse
    rows = {r[0]: r[1:] for r in con.execute(
        "select strain_id, in_screen_library, has_genome, inhibits, inhibited_by, "
        "clusters_listed, communities_designed from marts.dim_strain").fetchall()}
    assert set(rows) == {"Leaf1", "Leaf2", "Leaf3", "Leaf4", "Leaf9"}
    assert rows["Leaf1"] == (True, True, 1, 1, 2, 2)
    assert rows["Leaf3"] == (True, True, 0, 0, 1, 2)      # screened, nothing seen: zero
    assert rows["Leaf4"] == (True, False, 0, 0, None, 2)  # no genome, not analysed: unknown
    assert rows["Leaf9"][0] is False                      # in the collection, not the screen
    gc = con.execute("select gc_percent from marts.dim_strain where strain_id = 'Leaf2'").fetchone()[0]
    assert math.isclose(gc, 200 / 3)                      # ACGTGC: four of six letters


def test_undecided_plants_can_be_left_out_by_a_setting(warehouse):
    project, con = warehouse
    con.close()                                            # dbt needs to write to it
    run_dbt(project, ["--vars", "{keep_undecided_plants: false}"])
    with duckdb.connect(str(project / "data" / "warehouse" / "realsignal.duckdb"), read_only=True) as again:
        chosen = {r[0] for r in again.execute("select plant_id from marts.model_plants").fetchall()}
        empty = again.execute("select community_id from marts.dim_community "
                              "where kind = 'community' and not has_plants_for_modelling").fetchall()
    assert chosen == EXPECTED - {"5_1", "5_2"}
    assert empty == [("Mix2",)]                            # its only box was the dropped one
