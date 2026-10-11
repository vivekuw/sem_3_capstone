"""Bulk loader for Tennessee Eastman Process (TEP) benchmark datasets into TimescaleDB.

Loads benchmark CSV datasets from data/raw/ into the sensor_readings hypertable,
preserving the fault_label column for supervised anomaly detection and evaluation.
Generates comprehensive synthetic baseline and fault scenarios if raw files are absent.
"""

import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Optional
import numpy as np
import pandas as pd

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ingestion.timescale_client import (
    get_connection,
    create_tables,
    insert_readings,
)

RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

# Standard 22 continuous process measurement variables (XMEAS 1 - 22)
TEP_SENSORS = [
    "XMEAS_1", "XMEAS_2", "XMEAS_3", "XMEAS_4", "XMEAS_5",
    "XMEAS_6", "XMEAS_7", "XMEAS_8", "XMEAS_9", "XMEAS_10",
    "XMEAS_11", "XMEAS_12", "XMEAS_13", "XMEAS_14", "XMEAS_15",
    "XMEAS_16", "XMEAS_17", "XMEAS_18", "XMEAS_19", "XMEAS_20",
    "XMEAS_21", "XMEAS_22"
]

# Nominal steady-state setpoints and standard deviations
BASE_STATS = {
    "XMEAS_1": (0.25, 0.01),      # A Feed (kscmh)
    "XMEAS_2": (3660.0, 15.0),    # D Feed (kg/h)
    "XMEAS_3": (4500.0, 20.0),    # E Feed (kg/h)
    "XMEAS_4": (9.2, 0.15),       # A/C Feed (kscmh)
    "XMEAS_5": (27.0, 0.5),       # Recycle Flow (kscmh)
    "XMEAS_6": (42.0, 0.6),       # Reactor Feed (kscmh)
    "XMEAS_7": (2705.0, 10.0),    # Reactor Pressure (kPa)
    "XMEAS_8": (65.0, 1.2),       # Reactor Level (%)
    "XMEAS_9": (120.5, 0.4),      # Reactor Temp (°C)
    "XMEAS_10": (0.33, 0.02),     # Purge Rate (kscmh)
    "XMEAS_11": (80.1, 0.5),      # Sep Temp (°C)
    "XMEAS_12": (50.0, 1.5),      # Sep Level (%)
    "XMEAS_13": (2630.0, 8.0),    # Sep Pressure (kPa)
    "XMEAS_14": (25.1, 0.4),      # Sep Underflow (m3/h)
    "XMEAS_15": (50.0, 1.1),      # Strip Level (%)
    "XMEAS_16": (3010.0, 12.0),   # Strip Pressure (kPa)
    "XMEAS_17": (22.5, 0.3),      # Strip Underflow (m3/h)
    "XMEAS_18": (65.5, 0.3),      # Strip Temp (°C)
    "XMEAS_19": (1080.0, 15.0),   # Strip Steam (kg/h)
    "XMEAS_20": (340.0, 5.0),     # Compressor Work (kW)
    "XMEAS_21": (94.2, 0.8),      # Reactor Coolant Temp (°C)
    "XMEAS_22": (77.8, 0.7),      # Condenser Coolant Temp (°C)
}


def generate_benchmark_run(
    num_samples: int = 360,
    fault_type: str = "NORMAL",
    start_time: Optional[datetime] = None
) -> pd.DataFrame:
    """Generate a realistic TEP continuous simulation run for a specific operating mode."""
    if start_time is None:
        start_time = datetime(2026, 10, 11, 0, 0, 0, tzinfo=timezone.utc)

    timestamps = pd.date_range(start=start_time, periods=num_samples, freq="10s")
    data = {"time": timestamps}

    for sensor in TEP_SENSORS:
        mean, std = BASE_STATS.get(sensor, (100.0, 5.0))
        noise = np.random.normal(0, std, len(timestamps))
        series = mean + noise

        # Inject signature physical deviations if fault scenario
        if fault_type == "IDV(4)":  # Reactor cooling water inlet temp rise
            # Excursion on reactor temp (XMEAS_9) and cooling water return (XMEAS_21)
            ramp = np.clip(np.linspace(0, 12.0, num_samples), 0, 12.0)
            if sensor == "XMEAS_9":
                series += ramp
            elif sensor == "XMEAS_21":
                series += ramp * 1.2
            elif sensor == "XMEAS_7":
                series += ramp * 8.0

        elif fault_type == "IDV(6)":  # A Feed loss
            # Loss of Stream 1 flow and pressure drop
            drop = np.clip(np.linspace(0, 0.22, num_samples), 0, 0.22)
            if sensor == "XMEAS_1":
                series = np.maximum(0.01, series - drop)
            elif sensor == "XMEAS_7":
                series -= drop * 400.0

        elif fault_type == "IDV(11)":  # Reactor cooling water valve sticking
            # Oscillatory behavior on cooling circuits
            t = np.arange(num_samples)
            osc = 4.5 * np.sin(2 * np.pi * t / 25.0)
            if sensor in ("XMEAS_9", "XMEAS_21"):
                series += osc

        data[sensor] = np.round(series, 4)

    wide_df = pd.DataFrame(data)
    wide_df["fault_label"] = fault_type
    return wide_df


def prepare_raw_datasets_if_needed() -> List[Path]:
    """Ensure benchmark CSV files exist in data/raw/; generate them if not present."""
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    existing_csvs = list(RAW_DATA_DIR.glob("*.csv"))

    if not existing_csvs:
        print(f"[INFO] No CSV datasets found in {RAW_DATA_DIR}. Generating standard benchmark files...")
        scenarios = [
            ("tep_normal_baseline.csv", "NORMAL", 360),
            ("tep_fault_idv04.csv", "IDV(4)", 360),
            ("tep_fault_idv06.csv", "IDV(6)", 360),
            ("tep_fault_idv11.csv", "IDV(11)", 360),
        ]
        base_time = datetime(2026, 10, 11, 0, 0, 0, tzinfo=timezone.utc)
        for i, (fname, label, samples) in enumerate(scenarios):
            run_time = base_time + pd.Timedelta(hours=i * 2)
            df = generate_benchmark_run(num_samples=samples, fault_type=label, start_time=run_time)
            target = RAW_DATA_DIR / fname
            df.to_csv(target, index=False)
            print(f"  -> Generated {fname} ({len(df)} timesteps, label: {label})")

        existing_csvs = list(RAW_DATA_DIR.glob("*.csv"))

    return existing_csvs


def load_tep_dataset() -> None:
    """Read CSV files from data/raw/ and stream into TimescaleDB, preserving fault labels."""
    create_tables()
    csv_files = prepare_raw_datasets_if_needed()

    print(f"\n[INFO] Starting bulk load for {len(csv_files)} TEP dataset files...")

    for csv_file in csv_files:
        print(f"[INFO] Processing: {csv_file.name} ...")
        df = pd.read_csv(csv_file)

        # Convert from wide format (one column per sensor) to long format if needed
        if "sensor_id" not in df.columns:
            id_vars = ["time"]
            if "fault_label" in df.columns:
                id_vars.append("fault_label")

            value_vars = [c for c in df.columns if c not in id_vars]
            long_df = df.melt(
                id_vars=id_vars,
                value_vars=value_vars,
                var_name="sensor_id",
                value_name="value"
            )
        else:
            long_df = df

        if "fault_label" not in long_df.columns:
            long_df["fault_label"] = "NORMAL"

        inserted = insert_readings(long_df)
        print(f"  -> Ingested {inserted} sensor reading rows from {csv_file.name}.")

    # Report summary row counts from TimescaleDB
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT fault_label, COUNT(*) AS count
                FROM sensor_readings
                GROUP BY fault_label
                ORDER BY count DESC;
            """)
            label_counts = cur.fetchall()

            cur.execute("SELECT COUNT(*) FROM sensor_readings;")
            total_records = cur.fetchone()[0]

            cur.execute("SELECT COUNT(DISTINCT coalesce(sensor_id, sensor_name)) FROM sensor_readings;")
            sensor_count = cur.fetchone()[0]

        print("\n" + "=" * 55)
        print("     TIMESCALEDB INGESTION ROW COUNT REPORT         ")
        print("=" * 55)
        for label, count in label_counts:
            print(f"  Fault Mode: {label:<16} -> {count:>7} rows")
        print("-" * 55)
        print(f"  Total Unique Sensors Ingested : {sensor_count:>7}")
        print(f"  Total Records in Hypertable   : {total_records:>7}")
        print("=" * 55)
        print("[SUCCESS] Phase 3 benchmark dataset ingestion complete.")

    finally:
        conn.close()


def print_row_counts() -> None:
    """Helper function to print row counts at any time."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT fault_label, COUNT(*) AS count
                FROM sensor_readings
                GROUP BY fault_label
                ORDER BY count DESC;
            """)
            label_counts = cur.fetchall()

            cur.execute("SELECT COUNT(*) FROM sensor_readings;")
            total_records = cur.fetchone()[0]

        print("TimescaleDB 'sensor_readings' Counts by Label:")
        for label, count in label_counts:
            print(f"  - {label}: {count} rows")
        print(f"Total: {total_records} rows")
    finally:
        conn.close()


if __name__ == "__main__":
    load_tep_dataset()
