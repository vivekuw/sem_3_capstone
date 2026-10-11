"""Script to generate realistic synthetic sensor telemetry for Tennessee Eastman process segment:
P-100 (Pump) -> V-101 (Valve) -> HX-102 (HeatExchanger) -> R-103 (Reactor).
Fault at V-101 starts at tick 40 and propagates downstream.
"""

from datetime import datetime, timezone, timedelta
from pathlib import Path
import numpy as np
import pandas as pd


def generate_sensor_data(output_path: Path, num_ticks: int = 100) -> pd.DataFrame:
    """Generate synthetic process data and save to CSV."""
    np.random.seed(42)
    start_time = datetime(2026, 10, 10, 12, 0, 0, tzinfo=timezone.utc)
    records = []

    for tick in range(num_ticks):
        t_stamp = start_time + timedelta(seconds=tick * 5)
        is_fault = tick >= 40
        fault_age = max(0, tick - 40)

        # 1. V-101: Valve (Fault source at tick 40)
        # Position drops from nominal ~50% towards ~15% due to valve stem binding/failure
        if not is_fault:
            v101_pos = 50.0 + np.random.normal(0, 0.4)
            v101_flow = 100.0 + np.random.normal(0, 0.8)
            v101_dp = 1.20 + np.random.normal(0, 0.02)
        else:
            decay = min(1.0, fault_age / 5.0)
            v101_pos = 50.0 - 35.0 * decay + np.random.normal(0, 0.4)
            v101_flow = 100.0 - 70.0 * decay + np.random.normal(0, 0.8)
            v101_dp = 1.20 + 1.80 * decay + np.random.normal(0, 0.03)

        # 2. P-100: Pump (Upstream of V-101)
        # Backpressure increases, mass throughput decreases
        if not is_fault:
            p100_flow = 100.0 + np.random.normal(0, 0.7)
            p100_pressure = 5.0 + np.random.normal(0, 0.03)
            p100_power = 45.0 + np.random.normal(0, 0.2)
        else:
            decay = min(1.0, fault_age / 5.0)
            p100_flow = 100.0 - 68.0 * decay + np.random.normal(0, 0.7)
            p100_pressure = 5.0 + 0.8 * decay + np.random.normal(0, 0.03)
            p100_power = 45.0 - 10.0 * decay + np.random.normal(0, 0.2)

        # 3. HX-102: Heat Exchanger (Downstream of V-101, thermal lag ~ 2 ticks: tick 42)
        hx_fault_age = max(0, tick - 42)
        hx_decay = min(1.0, hx_fault_age / 6.0) if tick >= 42 else 0.0
        hx102_temp_in = 40.0 + np.random.normal(0, 0.3)
        # Fluid velocity slows down through heat exchanger tube bundles -> outlet temp spikes
        hx102_temp_out = 85.0 + 22.0 * hx_decay + np.random.normal(0, 0.4)
        hx102_coolant_flow = 250.0 - 50.0 * hx_decay + np.random.normal(0, 1.2)

        # 4. R-103: Reactor (Downstream of HX-102, reaction/level lag ~ 5 ticks: tick 45)
        r_fault_age = max(0, tick - 45)
        r_decay = min(1.0, r_fault_age / 8.0) if tick >= 45 else 0.0
        r103_temp = 120.0 + 25.0 * r_decay + np.random.normal(0, 0.5)
        r103_pressure = 2700.0 - 350.0 * r_decay + np.random.normal(0, 4.0)
        r103_level = 65.0 - 20.0 * r_decay + np.random.normal(0, 0.3)

        # Map to required schema: timestamp, tick, equipment_id, sensor_name, value, unit
        equipment_sensors = [
            ("P-100", "P100_flow", round(p100_flow, 3), "m3/h"),
            ("P-100", "P100_pressure", round(p100_pressure, 3), "bar"),
            ("P-100", "P100_power", round(p100_power, 3), "kW"),
            ("V-101", "V101_pos", round(v101_pos, 3), "%"),
            ("V-101", "V101_flow", round(v101_flow, 3), "m3/h"),
            ("V-101", "V101_dp", round(v101_dp, 3), "bar"),
            ("HX-102", "HX102_temp_in", round(hx102_temp_in, 3), "°C"),
            ("HX-102", "HX102_temp_out", round(hx102_temp_out, 3), "°C"),
            ("HX-102", "HX102_coolant_flow", round(hx102_coolant_flow, 3), "kg/h"),
            ("R-103", "R103_temp", round(r103_temp, 3), "°C"),
            ("R-103", "R103_pressure", round(r103_pressure, 3), "kPa"),
            ("R-103", "R103_level", round(r103_level, 3), "%"),
        ]

        for eq_id, s_name, val, unit in equipment_sensors:
            records.append({
                "timestamp": t_stamp.isoformat(),
                "tick": tick,
                "equipment_id": eq_id,
                "sensor_name": s_name,
                "value": val,
                "unit": unit,
            })

    df = pd.DataFrame(records)
    df.to_csv(output_path, index=False)
    print(f"Saved {len(df)} rows to {output_path}")
    return df


if __name__ == "__main__":
    out_file = Path(__file__).resolve().parent / "sensor_data.csv"
    generate_sensor_data(out_file)
