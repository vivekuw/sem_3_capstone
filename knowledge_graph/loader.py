"""Knowledge Graph Loader for Tennessee Eastman Process (TEP).

Executes schema.cypher and seed_tep_topology.cypher against Neo4j,
establishing constraints, plant units, sensors, failure modes, and flow topology.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from neo4j import GraphDatabase, Driver
from neo4j.exceptions import ServiceUnavailable, AuthError

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Load environment configuration
load_dotenv(dotenv_path=PROJECT_ROOT / ".env", override=True)


def get_driver() -> Driver:
    """Establish and return an authenticated Neo4j Bolt driver.

    Returns:
        Driver: Active Neo4j driver instance.

    Raises:
        ConnectionError: If Neo4j cannot be reached or authentication fails.
    """
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "password123")

    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        driver.verify_connectivity()
        return driver
    except ServiceUnavailable as exc:
        err_msg = (
            f"Failed to connect to Neo4j at {uri}.\n"
            f"Is the Docker container running? Error details: {exc}"
        )
        print(f"[ERROR] {err_msg}", file=sys.stderr)
        raise ConnectionError(err_msg) from exc
    except AuthError as exc:
        err_msg = f"Authentication failed for Neo4j user '{user}'. Error details: {exc}"
        print(f"[ERROR] {err_msg}", file=sys.stderr)
        raise ConnectionError(err_msg) from exc


def execute_cypher_file(driver: Driver, file_path: Path) -> int:
    """Read and execute semicolon-delimited Cypher statements from a file.

    Args:
        driver: Active Neo4j driver.
        file_path: Path to .cypher file.

    Returns:
        int: Number of non-empty statements executed.

    Raises:
        FileNotFoundError: If the specified file does not exist.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Cypher script file not found: {file_path}")

    print(f"[INFO] Executing Cypher statements from: {file_path.name}")
    content = file_path.read_text(encoding="utf-8")

    # Split by semicolon delimiter
    raw_statements = [stmt.strip() for stmt in content.split(";") if stmt.strip()]
    executed_count = 0

    with driver.session() as session:
        for stmt in raw_statements:
            # Strip comment-only lines
            lines = [line for line in stmt.splitlines() if not line.strip().startswith("//")]
            cleaned_stmt = "\n".join(lines).strip()
            if not cleaned_stmt:
                continue

            session.run(cleaned_stmt)
            executed_count += 1

    print(f"[INFO] Successfully executed {executed_count} statements from {file_path.name}.")
    return executed_count


def load_knowledge_graph() -> None:
    """Execute schema and seed scripts against Neo4j and report ontology statistics."""
    kg_dir = Path(__file__).resolve().parent
    schema_file = kg_dir / "schema.cypher"
    tep_seed_file = kg_dir / "seed_tep_topology.cypher"
    basic_seed_file = kg_dir / "seed.cypher"

    driver = get_driver()
    try:
        # 1. Apply Schema Constraints & Indexes
        execute_cypher_file(driver, schema_file)

        # 2. Seed Full TEP Topology (5 units, 24 sensors, IDV 1-21 failure modes)
        if tep_seed_file.exists():
            execute_cypher_file(driver, tep_seed_file)

        # 3. Seed Basic Equipment Segment (if present)
        if basic_seed_file.exists():
            execute_cypher_file(driver, basic_seed_file)

        # 4. Report Current Graph State
        with driver.session() as session:
            unit_count = session.run("MATCH (u:Unit) RETURN count(u) AS cnt").single()["cnt"]
            sensor_count = session.run("MATCH (s:Sensor) RETURN count(s) AS cnt").single()["cnt"]
            fault_count = session.run("MATCH (f:FailureMode) RETURN count(f) AS cnt").single()["cnt"]
            feeds_count = session.run("MATCH ()-[r:FEEDS]->() RETURN count(r) AS cnt").single()["cnt"]
            measures_count = session.run("MATCH ()-[r:MEASURES]->() RETURN count(r) AS cnt").single()["cnt"]
            suscept_count = session.run("MATCH ()-[r:SUSCEPTIBLE_TO]->() RETURN count(r) AS cnt").single()["cnt"]
            causes_count = session.run("MATCH ()-[r:TYPICALLY_CAUSES]->() RETURN count(r) AS cnt").single()["cnt"]

        print("\n" + "=" * 55)
        print("          KNOWLEDGE GRAPH ONTOLOGY SUMMARY          ")
        print("=" * 55)
        print(f"Plant Units (:Unit)                : {unit_count}")
        print(f"Sensors (:Sensor)                  : {sensor_count}")
        print(f"Failure Modes (:FailureMode)       : {fault_count} (IDV 1 to 21)")
        print(f"Process Material Flows (:FEEDS)    : {feeds_count}")
        print(f"Sensor Measurements (:MEASURES)    : {measures_count}")
        print(f"Unit Vulnerabilities (:SUSCEPTIBLE): {suscept_count}")
        print(f"Cascading Fault Links (:CAUSES)    : {causes_count}")
        print("=" * 55)
        print("[SUCCESS] Knowledge graph loaded successfully into Neo4j.")
    finally:
        driver.close()


def main() -> None:
    """Entry point for standalone execution."""
    try:
        load_knowledge_graph()
    except Exception as exc:
        print(f"[FAIL] Knowledge graph loader failed: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
