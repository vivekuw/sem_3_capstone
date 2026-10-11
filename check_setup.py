"""Verification script for Chemical Process RCA Agent Data Layer.

Tests:
1. TimescaleDB connection & sensor_readings hypertable row count.
2. Neo4j graph connection & node/relationship counts.
3. Topological upstream traversal for R-103 (expected: HX-102, V-101, P-100).
Prints explicit [PASS] or [FAIL] lines for every component.
"""

import sys
from pathlib import Path
from typing import List

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ingestion.timescale_client import get_connection
from knowledge_graph.loader import get_driver
from knowledge_graph.queries import get_upstream


def check_timescaledb() -> bool:
    """Validate TimescaleDB connectivity and telemetry row count."""
    print("=" * 60)
    print("CHECK 1: TimescaleDB Time-Series Data Layer")
    print("=" * 60)

    try:
        conn = get_connection()
        print("[PASS] TimescaleDB connection successful.")
    except Exception as exc:
        print(f"[FAIL] TimescaleDB connection failed: {exc}")
        print("       -> Is the TimescaleDB Docker container running on port 5432?")
        return False

    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM sensor_readings;")
            row_count = cur.fetchone()[0]

        print(f"[INFO] TimescaleDB 'sensor_readings' row count: {row_count}")
        if row_count > 0:
            print(f"[PASS] TimescaleDB hypertable is populated ({row_count} readings).")
            return True
        else:
            print("[FAIL] TimescaleDB 'sensor_readings' table is empty. Please run: python ingestion/load_csv.py")
            return False
    except Exception as exc:
        print(f"[FAIL] Failed querying TimescaleDB table: {exc}")
        return False
    finally:
        conn.close()


def check_neo4j() -> bool:
    """Validate Neo4j graph database connectivity and graph element counts."""
    print("\n" + "=" * 60)
    print("CHECK 2: Neo4j Knowledge Graph Data Layer")
    print("=" * 60)

    try:
        driver = get_driver()
        print("[PASS] Neo4j connection successful.")
    except Exception as exc:
        print(f"[FAIL] Neo4j connection failed: {exc}")
        print("       -> Is the Neo4j Docker container running on bolt://localhost:7687?")
        return False

    all_passed = True
    try:
        with driver.session() as session:
            eq_cnt = session.run("MATCH (e:Equipment) RETURN count(e) AS cnt").single()["cnt"]
            sensor_cnt = session.run("MATCH (s:Sensor) RETURN count(s) AS cnt").single()["cnt"]
            feeds_cnt = session.run("MATCH ()-[r:FEEDS]->() RETURN count(r) AS cnt").single()["cnt"]
            measures_cnt = session.run("MATCH ()-[r:MEASURES]->() RETURN count(r) AS cnt").single()["cnt"]

        print(f"[INFO] Neo4j Equipment Nodes     : {eq_cnt} (expected >= 4)")
        print(f"[INFO] Neo4j Sensor Nodes        : {sensor_cnt} (expected >= 12)")
        print(f"[INFO] Neo4j FEEDS Relationships : {feeds_cnt} (expected >= 3)")
        print(f"[INFO] Neo4j MEASURES Relations  : {measures_cnt} (expected >= 12)")

        if eq_cnt >= 4 and sensor_cnt >= 12 and feeds_cnt >= 3 and measures_cnt >= 12:
            print("[PASS] Neo4j node and relationship counts verified.")
        else:
            print("[FAIL] Neo4j graph counts are lower than expected. Please run: python knowledge_graph/loader.py")
            all_passed = False

        # Check upstream tracing for R-103
        print("\n" + "=" * 60)
        print("CHECK 3: Topology Traversal - Upstream Units of R-103")
        print("=" * 60)

        upstream_units = get_upstream("R-103", driver=driver)
        upstream_ids = [u["id"] for u in upstream_units]
        expected_ids = ["HX-102", "V-101", "P-100"]

        print(f"[INFO] Upstream units retrieved : {upstream_ids}")
        print(f"[INFO] Upstream units expected  : {expected_ids}")

        if upstream_ids == expected_ids:
            print("[PASS] Upstream topology traversal for R-103 verified (HX-102 -> V-101 -> P-100).")
        else:
            print(f"[FAIL] Upstream units mismatch. Expected {expected_ids}, got {upstream_ids}")
            all_passed = False

        return all_passed
    except Exception as exc:
        print(f"[FAIL] Error during Neo4j graph verification: {exc}")
        return False
    finally:
        driver.close()


def main() -> None:
    """Run full suite of data layer verification checks."""
    print("============================================================")
    print("      DATA LAYER VERIFICATION TEST (Viva / Demo Ready)       ")
    print("============================================================")

    ts_ok = check_timescaledb()
    neo_ok = check_neo4j()

    print("\n" + "=" * 60)
    print("FINAL SUMMARY")
    print("=" * 60)
    if ts_ok and neo_ok:
        print("[PASS] ALL DATA LAYER VERIFICATIONS PASSED SUCCESSFULLY.")
        print("       TimescaleDB and Neo4j are primed and ready for Agent & RCA reasoning.")
        sys.exit(0)
    else:
        print("[FAIL] ONE OR MORE VERIFICATION CHECKS FAILED.")
        sys.exit(1)


if __name__ == "__main__":
    main()
