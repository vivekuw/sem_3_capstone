"""TimescaleDB client module for chemical plant sensor telemetry.

Provides high-throughput time-series storage and retrieval using TimescaleDB
hypertables on PostgreSQL. Includes idempotent table creation, bulk inserts,
time-window queries, and latest-sample inspection.
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import pandas as pd
import psycopg2
from psycopg2.extensions import connection as PgConnection
from psycopg2.extras import execute_values
from dotenv import load_dotenv

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Load connection credentials from .env located at project root
ENV_PATH = PROJECT_ROOT / ".env"
load_dotenv(dotenv_path=ENV_PATH, override=True)


def get_connection() -> PgConnection:
    """Establish and return a connection to the TimescaleDB database.

    Returns:
        psycopg2.extensions.connection: An active PostgreSQL connection object.

    Raises:
        ConnectionError: If connection cannot be established, advising Docker check.
    """
    host = os.getenv("TIMESCALE_HOST", "localhost")
    port = int(os.getenv("TIMESCALE_PORT", "5432"))
    dbname = os.getenv("TIMESCALE_DB", "plant_data")
    user = os.getenv("TIMESCALE_USER", "postgres")
    password = os.getenv("TIMESCALE_PASSWORD", "password123")

    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            dbname=dbname,
            user=user,
            password=password,
            connect_timeout=5,
        )
        return conn
    except psycopg2.OperationalError as exc:
        err_msg = (
            f"Failed to connect to TimescaleDB at {host}:{port}/{dbname}.\n"
            f"Is the Docker container running? Error details: {exc}"
        )
        print(f"[ERROR] {err_msg}", file=sys.stderr)
        raise ConnectionError(err_msg) from exc


def create_tables() -> None:
    """Create the sensor_readings table and convert it to a TimescaleDB hypertable.

    Schema:
        - time (TIMESTAMPTZ): Telemetry timestamp (hypertable partition column).
        - sensor_id (VARCHAR(50)): Process variable identifier (e.g., XMEAS_9, V101_pos).
        - sensor_name (TEXT): Sensor descriptive name.
        - equipment_id (TEXT): Associated equipment unit (e.g., UNIT_REACTOR, P-100).
        - tick (INT): Simulation tick index.
        - value (DOUBLE PRECISION): Sensor measurement value.
        - unit (VARCHAR(50)): Engineering unit (°C, kPa, kg/h).
        - fault_label (VARCHAR(50)): Label indicating operating state (NORMAL, IDV(4), etc.).

    Safe to run repeatedly (uses IF NOT EXISTS).
    """
    statements = [
        "CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;",
        """
        CREATE TABLE IF NOT EXISTS sensor_readings (
            time TIMESTAMPTZ NOT NULL,
            sensor_id VARCHAR(50),
            sensor_name TEXT,
            equipment_id TEXT,
            tick INT,
            value DOUBLE PRECISION NOT NULL,
            unit VARCHAR(50),
            fault_label VARCHAR(50) DEFAULT 'NORMAL'
        );
        """,
        "SELECT create_hypertable('sensor_readings', 'time', if_not_exists => TRUE);",
        # Ensure columns allow NULL when not provided
        "ALTER TABLE sensor_readings ALTER COLUMN tick DROP NOT NULL;",
        "ALTER TABLE sensor_readings ALTER COLUMN equipment_id DROP NOT NULL;",
        "ALTER TABLE sensor_readings ALTER COLUMN sensor_name DROP NOT NULL;",
        # Backfill sensor_id from sensor_name if null
        "UPDATE sensor_readings SET sensor_id = sensor_name WHERE sensor_id IS NULL AND sensor_name IS NOT NULL;",
        # Standard composite unique index for ON CONFLICT (time, sensor_id)
        "DROP INDEX IF EXISTS idx_sensor_readings_unique;",
        """
        CREATE UNIQUE INDEX IF NOT EXISTS idx_sensor_readings_unique
        ON sensor_readings (time, sensor_id);
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_sensor_readings_sensor_time
        ON sensor_readings (sensor_id, time DESC);
        """,
    ]

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            for stmt in statements:
                cur.execute(stmt)
        conn.commit()
        print("[INFO] sensor_readings hypertable verified/created successfully.")
    finally:
        conn.close()


def insert_readings(df: pd.DataFrame) -> int:
    """Perform fast bulk insert of sensor readings DataFrame into TimescaleDB.

    Args:
        df: Pandas DataFrame containing sensor data.
            Supported column variations:
            [time/timestamp, sensor_id/sensor_name, value, unit, fault_label, tick, equipment_id].

    Returns:
        int: Number of records processed for insertion.
    """
    if df.empty:
        return 0

    df_work = df.copy()

    # Normalize timestamp column
    if "timestamp" in df_work.columns and "time" not in df_work.columns:
        df_work = df_work.rename(columns={"timestamp": "time"})
    df_work["time"] = pd.to_datetime(df_work["time"])

    # Harmonize sensor_id / sensor_name
    if "sensor_id" not in df_work.columns and "sensor_name" in df_work.columns:
        df_work["sensor_id"] = df_work["sensor_name"]
    elif "sensor_name" not in df_work.columns and "sensor_id" in df_work.columns:
        df_work["sensor_name"] = df_work["sensor_id"]
    elif "sensor_id" in df_work.columns and "sensor_name" in df_work.columns:
        df_work["sensor_id"] = df_work["sensor_id"].fillna(df_work["sensor_name"])

    # Optional defaults
    if "fault_label" not in df_work.columns:
        df_work["fault_label"] = "NORMAL"
    if "equipment_id" not in df_work.columns:
        df_work["equipment_id"] = None
    if "tick" not in df_work.columns:
        df_work["tick"] = None
    if "unit" not in df_work.columns:
        df_work["unit"] = ""

    records = [
        (
            row["time"],
            str(row["sensor_id"]) if pd.notna(row["sensor_id"]) else "UNKNOWN",
            str(row["sensor_name"]) if pd.notna(row["sensor_name"]) else str(row["sensor_id"]),
            str(row["equipment_id"]) if pd.notna(row["equipment_id"]) else "UNIT_TEP",
            int(row["tick"]) if pd.notna(row["tick"]) else 0,
            float(row["value"]),
            str(row["unit"]) if pd.notna(row["unit"]) else "",
            str(row["fault_label"]) if pd.notna(row["fault_label"]) else "NORMAL",
        )
        for _, row in df_work.iterrows()
    ]

    insert_query = """
    INSERT INTO sensor_readings (time, sensor_id, sensor_name, equipment_id, tick, value, unit, fault_label)
    VALUES %s
    ON CONFLICT (time, sensor_id) DO NOTHING;
    """

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            execute_values(cur, insert_query, records, page_size=2000)
        conn.commit()
        return len(records)
    finally:
        conn.close()


def query_window(
    sensor_ids: Optional[List[str]] = None,
    start: Optional[Union[datetime, str]] = None,
    end: Optional[Union[datetime, str]] = None,
) -> pd.DataFrame:
    """Query telemetry readings for a specific list of sensors across a time window.

    Args:
        sensor_ids: List of sensor IDs to query (e.g., ['XMEAS_9', 'XMEAS_21']).
        start: Start timestamp (inclusive).
        end: End timestamp (inclusive).

    Returns:
        pd.DataFrame: Retrieved telemetry readings ordered by time.
    """
    conditions = []
    params: List[Any] = []

    if sensor_ids:
        conditions.append("(sensor_id = ANY(%s) OR sensor_name = ANY(%s))")
        params.extend([sensor_ids, sensor_ids])

    if start is not None:
        conditions.append("time >= %s")
        params.append(pd.to_datetime(start))

    if end is not None:
        conditions.append("time <= %s")
        params.append(pd.to_datetime(end))

    where_clause = ""
    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)

    query = f"""
    SELECT time, sensor_id, sensor_name, equipment_id, tick, value, unit, fault_label
    FROM sensor_readings
    {where_clause}
    ORDER BY time ASC, sensor_id ASC;
    """

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(query, tuple(params) if params else None)
            rows = cur.fetchall()
            colnames = [desc[0] for desc in cur.description]
            return pd.DataFrame(rows, columns=colnames)
    finally:
        conn.close()


def get_window(
    equipment_ids: Optional[List[str]] = None,
    sensor_names: Optional[List[str]] = None,
    start: Optional[Union[datetime, str]] = None,
    end: Optional[Union[datetime, str]] = None,
) -> pd.DataFrame:
    """Retrieve sensor readings with optional equipment and sensor filters."""
    conditions = []
    params: List[Any] = []

    if equipment_ids:
        conditions.append("equipment_id = ANY(%s)")
        params.append(equipment_ids)

    if sensor_names:
        conditions.append("(sensor_name = ANY(%s) OR sensor_id = ANY(%s))")
        params.extend([sensor_names, sensor_names])

    if start is not None:
        conditions.append("time >= %s")
        params.append(pd.to_datetime(start))

    if end is not None:
        conditions.append("time <= %s")
        params.append(pd.to_datetime(end))

    where_clause = ""
    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)

    query = f"""
    SELECT time, tick, equipment_id, sensor_name, sensor_id, value, unit, fault_label
    FROM sensor_readings
    {where_clause}
    ORDER BY time ASC;
    """

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(query, tuple(params) if params else None)
            rows = cur.fetchall()
            colnames = [desc[0] for desc in cur.description]
            return pd.DataFrame(rows, columns=colnames)
    finally:
        conn.close()


def get_latest(n: int = 10) -> pd.DataFrame:
    """Fetch the latest n sensor readings recorded in the hypertable.

    Args:
        n: Number of readings to return (default 10).

    Returns:
        pd.DataFrame: Most recent n readings sorted by time descending.
    """
    query = """
    SELECT time, sensor_id, sensor_name, equipment_id, tick, value, unit, fault_label
    FROM sensor_readings
    ORDER BY time DESC
    LIMIT %s;
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(query, (n,))
            rows = cur.fetchall()
            colnames = [desc[0] for desc in cur.description]
            return pd.DataFrame(rows, columns=colnames)
    finally:
        conn.close()


class TimescaleClient:
    """Object-oriented interface for TimescaleDB sensor telemetry."""

    def __init__(self):
        self.conn_params = {
            "host": os.getenv("TIMESCALE_HOST", "localhost"),
            "port": int(os.getenv("TIMESCALE_PORT", 5432)),
            "dbname": os.getenv("TIMESCALE_DB", "plant_data"),
            "user": os.getenv("TIMESCALE_USER", "postgres"),
            "password": os.getenv("TIMESCALE_PASSWORD", "password123"),
        }

    def get_connection(self) -> PgConnection:
        """Establish connection."""
        return get_connection()

    def init_db(self) -> None:
        """Create hypertable and indexes."""
        create_tables()

    def insert_readings_batch(self, readings: List[Dict[str, Any]]) -> int:
        """Batch insert telemetry records from list of dictionaries."""
        if not readings:
            return 0
        df = pd.DataFrame(readings)
        return insert_readings(df)

    def insert_readings(self, df: pd.DataFrame) -> int:
        """Insert DataFrame into hypertable."""
        return insert_readings(df)

    def query_window(
        self,
        sensor_ids: Optional[List[str]] = None,
        start: Optional[Union[datetime, str]] = None,
        end: Optional[Union[datetime, str]] = None,
    ) -> pd.DataFrame:
        """Query time window for sensors."""
        return query_window(sensor_ids=sensor_ids, start=start, end=end)

    def get_latest_readings(self, limit: int = 100) -> pd.DataFrame:
        """Fetch latest readings."""
        return get_latest(n=limit)


if __name__ == "__main__":
    print("--- Testing Phase 3 TimescaleDB Client Standalone ---")
    try:
        conn_test = get_connection()
        print("[PASS] TimescaleDB connection established.")
        conn_test.close()

        create_tables()

        latest_df = get_latest(5)
        print(f"[INFO] Latest readings sample ({len(latest_df)} rows):")
        print(latest_df)

        print("[PASS] timescale_client.py completed successfully.")
    except Exception as error:
        print(f"[FAIL] timescale_client encountered error: {error}")
        sys.exit(1)
