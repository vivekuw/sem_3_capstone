"""CSV Loader module for populating TimescaleDB with chemical sensor telemetry.

Reads sensor_data.csv, ensures tables exist, performs fast bulk insertion,
guarantees idempotency (skips duplicate records), and outputs total row counts.
"""

import sys
from pathlib import Path

# Add project root to sys.path to support direct execution: python ingestion/load_csv.py
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
from ingestion.timescale_client import (
    get_connection,
    create_tables,
    insert_readings,
)


def load_csv(csv_path: Path) -> int:
    """Load sensor telemetry from CSV file into TimescaleDB hypertable.

    Args:
        csv_path: Absolute or relative Path to sensor_data.csv.

    Returns:
        int: Total row count currently stored in sensor_readings table.

    Raises:
        FileNotFoundError: If csv_path does not exist.
        ConnectionError: If TimescaleDB container is not reachable.
    """
    if not csv_path.exists():
        err_msg = f"Target CSV file not found at: {csv_path}"
        print(f"[ERROR] {err_msg}", file=sys.stderr)
        raise FileNotFoundError(err_msg)

    print(f"[INFO] Reading sensor telemetry from: {csv_path}")
    df = pd.read_csv(csv_path)
    print(f"[INFO] Loaded {len(df)} rows from CSV ({df['sensor_name'].nunique()} unique sensors across {df['equipment_id'].nunique()} units).")

    # Ensure table and hypertable exist
    print("[INFO] Verifying TimescaleDB table schema...")
    create_tables()

    # Bulk insert records (idempotent ON CONFLICT DO NOTHING)
    print("[INFO] Bulk inserting records into TimescaleDB (sensor_readings)...")
    inserted_count = insert_readings(df)
    print(f"[INFO] Processed {inserted_count} records for bulk insert.")

    # Query current row count in database
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM sensor_readings;")
            total_db_rows = cur.fetchone()[0]
        print(f"[INFO] Total row count in TimescaleDB 'sensor_readings': {total_db_rows}")
        return total_db_rows
    finally:
        conn.close()


def main() -> None:
    """Entry point for standalone execution."""
    root_dir = Path(__file__).resolve().parent.parent
    csv_file = root_dir / "sensor_data.csv"

    # Fallback to data/raw if not in root
    if not csv_file.exists():
        csv_file = root_dir / "data" / "raw" / "sensor_data.csv"

    try:
        total_rows = load_csv(csv_file)
        print(f"[SUCCESS] CSV loading complete. Total records in database: {total_rows}")
    except Exception as exc:
        print(f"[FAIL] load_csv failed: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
