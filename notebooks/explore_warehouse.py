"""
notebooks/explore_warehouse.py: what the harmonised warehouse holds.

After scripts/load_raw.py and dbt build, the warehouse
data/warehouse/realsignal.duckdb holds the raw tables and every layer dbt
built from them. This script opens it read-only and answers, from the marts:

  * how many strains the sources name, and what each layer covers;
  * the communities by role, and the ones that need a decision;
  * the plants by split, and why the ones not used aren't;
  * what the modelling table holds, and whether it matches the authors';
  * the measurements, and where the sources disagree.

Every number comes from a query. Nothing here repeats a number found earlier,
so the output changes if the data or a choice in dbt/dbt_project.yml does.

Run from the project folder, with the virtual environment active:

    python notebooks/explore_warehouse.py

Explained in docs/04-phase-3-harmonisation.md, section 10.
"""

import sys
import textwrap
from pathlib import Path

import duckdb

PROJECT_ROOT = Path(__file__).resolve().parents[1]
WAREHOUSE = PROJECT_ROOT / "data" / "warehouse" / "realsignal.duckdb"


def strain_order(strain: str) -> tuple:
    """Leaf15 before Leaf130: by the number, then by the name."""
    digits = "".join(c for c in strain if c.isdigit())
    return (strain.rstrip("0123456789"), int(digits) if digits else 0)


def names(values) -> str:
    return ", ".join(sorted(values, key=strain_order)) or "none"


def main() -> int:
    if not WAREHOUSE.exists():
        print("No warehouse yet. Run:  python scripts/load_raw.py,")
        print("then from inside dbt/:  dbt build")
        return 1
    try:
        con = duckdb.connect(str(WAREHOUSE), read_only=True)
    except duckdb.IOException:
        print("The warehouse is open in another program (dbt docs serve is fine;")
        print("a running dbt build or a Python session isn't). Close it and try again.")
        return 1
    tables = {row[0] for row in con.execute(
        "select table_schema || '.' || table_name from information_schema.tables").fetchall()}
    if "marts.model_plants" not in tables:
        print("The raw tables are loaded, but dbt hasn't built the marts yet.")
        print("From inside dbt/:  dbt build")
        return 1

    def one(sql):
        return con.execute(sql).fetchone()

    def rows(sql):
        return con.execute(sql).fetchall()

    # ---- 1. Schemas ----------------------------------------------------------
    print("THE WAREHOUSE: data/warehouse/realsignal.duckdb")
    print()
    print("Schemas, in the order data flows through them")
    for schema, n_tables, n_views in rows("""
            select table_schema,
                   count(*) filter (where table_type = 'BASE TABLE'),
                   count(*) filter (where table_type = 'VIEW')
            from information_schema.tables
            where table_schema in ('raw', 'staging', 'intermediate', 'marts', 'reference')
            group by 1
            order by list_position(['raw', 'staging', 'intermediate', 'marts', 'reference'],
                                   table_schema)"""):
        parts = [f"{n_tables} {'table' if n_tables == 1 else 'tables'}" if n_tables else "",
                 f"{n_views} {'view' if n_views == 1 else 'views'}" if n_views else ""]
        print(f"  {schema:<14}{' and '.join(p for p in parts if p)}")
    print()

    # ---- 2. The strains -------------------------------------------------------
    total, library, with_genome, screened = one("""
        select count(*), count(*) filter (where in_screen_library),
               count(*) filter (where in_screen_library and has_genome),
               count(*) filter (where in_interaction_screen)
        from marts.dim_strain""")
    no_genome = [r[0] for r in rows(
        "select strain_id from marts.dim_strain where in_screen_library and not has_genome")]
    library_screened = one("select count(*) from marts.dim_strain "
                           "where in_screen_library and in_interaction_screen")[0]
    silent = [r[0] for r in rows("""
        select strain_id from marts.dim_strain
        where in_screen_library and inhibits = 0 and inhibited_by = 0""")]
    low_len, high_len, low_ctg, high_ctg, low_gc, high_gc = one("""
        select min(genome_length_bp) / 1e6, max(genome_length_bp) / 1e6, min(contigs),
               max(contigs), min(gc_percent), max(gc_percent)
        from marts.dim_strain where in_screen_library and has_genome""")
    print("The strains (marts.dim_strain)")
    print(f"  named by any source         : {total}")
    print(f"  in the community screen     : {library}")
    print(f"  screen strains with a genome: {with_genome} (none for {names(no_genome)})")
    print(f"  in the interaction screen   : {screened}, {library_screened} of the "
          f"{library} screen strains among them")
    print(f"  no inhibition seen, given or received: {names(silent)}")
    print(f"  their genomes: {low_len:.2f} to {high_len:.2f} Mb, {low_ctg} to {high_ctg} "
          f"contigs, GC {low_gc:.1f} to {high_gc:.1f} %")
    print()

    # ---- 3. The communities ---------------------------------------------------
    print("The communities (marts.dim_community)")
    print("  role      kind            communities  with plants for modelling")
    for role, kind, n, used in rows("""
            select role, kind, count(*), count(*) filter (where has_plants_for_modelling)
            from marts.dim_community group by role, kind
            order by list_position(['training', 'test', 'control'], role), kind"""):
        print(f"  {role:<10}{kind:<16}{n:>11}{used:>27}")
    sizes = [r[0] for r in rows(
        "select distinct community_size from marts.dim_community where kind = 'community'")]
    print(f"  strains per community: {', '.join(str(s) for s in sizes)}")
    several = rows("""select community_id, label from marts.dim_community
                      where kind = 'community' and rounds_grown like '%,%' order by 1""")
    print("  grown in more than one round: "
          + ", ".join(f"{c} ({label})" for c, label in several))
    empty = rows("""select community_id, rounds_grown from marts.dim_community
                    where kind = 'community' and not has_plants_for_modelling
                    order by cast(regexp_extract(community_id, '[0-9]+') as integer)""")
    print(f"  communities with no plant for modelling: {len(empty)}")
    if empty:
        listed = ", ".join(f"{c} in {r}" for c, r in empty)
        print(textwrap.fill(listed, width=78, initial_indent="    ", subsequent_indent="    "))
    print()

    # ---- 4. The plants ---------------------------------------------------------
    print("The plants (marts.fct_plant)")
    print("  split                      plants   used for modelling")
    for split, n, used in rows("""
            select split, count(*), count(*) filter (where use_for_modelling)
            from marts.fct_plant group by split
            order by list_position(['training', 'test', 'between-round reference', 'control'],
                                   split)"""):
        print(f"  {split:<25}{n:>8}{used:>21}")
    print("  why the others aren't used:")
    for reason, n in rows("""select not_used_because, count(*) from marts.fct_plant
                             where not use_for_modelling group by 1 order by 2 desc, 1"""):
        print(f"    {n:>4}  {reason[:66]}")
    print()

    # ---- 5. The modelling table -----------------------------------------------
    n_plants, n_train, n_test, n_comm, c_train, c_test, tbd, with_outcome = one("""
        select count(*), count(*) filter (where split = 'training'),
               count(*) filter (where split = 'test'), count(distinct community_id),
               count(distinct community_id) filter (where split = 'training'),
               count(distinct community_id) filter (where split = 'test'),
               count(*) filter (where inclusion_mark = 'TBD'), count(outcome)
        from marts.model_plants""")
    outcome = one("select any_value(outcome_measurement) from marts.model_plants")[0]
    differ = one("""
        select count(*) from (
            (select plant_id from marts.model_plants
             except select plant_id from staging.stg_screen__authors_model_plants)
            union all
            (select plant_id from staging.stg_screen__authors_model_plants
             except select plant_id from marts.model_plants))""")[0]
    print("The modelling table (marts.model_plants)")
    print(f"  plants      : {n_plants} (training {n_train}, test {n_test})")
    print(f"  communities : {n_comm} (training {c_train}, test {c_test})")
    print(f"  undecided (TBD) plants in it: {tbd}")
    print(f"  outcome     : {outcome}, present for {with_outcome} of {n_plants}")
    print("  the same plants as the authors' table: "
          + ("yes" if differ == 0 else f"no, {differ} differ"))
    if differ and tbd == 0:
        print("    (expected while keep_undecided_plants is false: theirs keeps them)")
    print()

    # ---- 6. Measurements ----------------------------------------------------------
    print("Measurements (marts.fct_plant_measurement)")
    print("  measurement                    plants    rows  unit")
    for measurement, plants, n, unit in rows("""
            select measurement, count(distinct plant_id), count(*), any_value(unit)
            from marts.fct_plant_measurement group by 1 order by 1"""):
        print(f"  {measurement:<29}{plants:>7}{n:>8}  {unit[:30]}")
    print()

    # ---- 7. Where the sources disagree -----------------------------------------------
    print("Where the sources disagree (reference.known_source_differences)")
    for what, n, strains in rows("""
            select what_differs, count(*), list(strain_id)
            from reference.known_source_differences group by what_differs
            order by list_position(['gene_cluster_count', 'family', 'genus'], what_differs)"""):
        listed = names(strains) if n <= 3 else f"{n} strains"
        print(f"  {what:<20}{listed}")
    screen = [r[0] for r in rows("""
        select distinct d.strain_id from reference.known_source_differences d
        join marts.dim_strain s using (strain_id) where s.in_screen_library""")]
    print(f"  of them, screen strains: {names(screen)}")
    con.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
