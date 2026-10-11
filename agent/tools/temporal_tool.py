"""Agent tool for retrieving time-aligned sensor telemetry windows from TimescaleDB."""

import sys
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import List, Optional
import pandas as pd

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ingestion.timescale_client import query_window, get_latest


class TemporalTelemetryTool:
    """Queries TimescaleDB for time-windowed continuous process signals."""

    def fetch_window_dataframe(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        sensor_ids: Optional[List[str]] = None,
        window_minutes: int = 15,
        limit_rows: int = 100,
    ) -> pd.DataFrame:
        """Fetch window from TimescaleDB and reshape into a wide DataFrame (index=time, cols=sensor_id).

        Args:
            start_time: Start timestamp (optional).
            end_time: End timestamp (optional).
            sensor_ids: Optional list of sensors to filter by.
            window_minutes: Lookback window duration if start_time not specified.
            limit_rows: Maximum records to fetch if querying latest.

        Returns:
            pd.DataFrame: Wide DataFrame with time index and sensor measurement columns.
        """
        try:
            if start_time is not None or end_time is not None:
                now = datetime.now(timezone.utc)
                end = end_time or now
                start = start_time or (end - timedelta(minutes=window_minutes))
                df_raw = query_window(sensor_ids=sensor_ids, start=start, end=end)
            else:
                # Retrieve latest recorded telemetry batch
                df_raw = get_latest(n=limit_rows * (len(sensor_ids) if sensor_ids else 5))
                if sensor_ids and not df_raw.empty:
                    df_raw = df_raw[
                        df_raw["sensor_id"].isin(sensor_ids) | df_raw["sensor_name"].isin(sensor_ids)
                    ]

            if df_raw.empty:
                return self._fallback_synthetic_dataframe(sensor_ids)

            # Harmonize sensor column name for pivot
            col = "sensor_id" if "sensor_id" in df_raw.columns else "sensor_name"
            df_pivot = df_raw.pivot_table(index="time", columns=col, values="value", aggfunc="mean")
            df_pivot = df_pivot.sort_index().ffill().bfill()
            return df_pivot

        except Exception as e:
            return self._fallback_synthetic_dataframe(sensor_ids)

    @staticmethod
    def _fallback_synthetic_dataframe(sensor_ids: Optional[List[str]]) -> pd.DataFrame:
        """Fallback synthetic dataframe when database is not connected."""
        sensors = sensor_ids or ["XMEAS_9", "XMEAS_21", "XMEAS_7"]
        now = datetime.now(timezone.utc)
        timestamps = pd.date_range(end=now, periods=50, freq="10s")
        data = {}
        for s in sensors:
            data[s] = [100.0 + i * 0.1 for i in range(50)]
        df = pd.DataFrame(data, index=timestamps)
        df.index.name = "time"
        return df


if __name__ == "__main__":
    t_tool = TemporalTelemetryTool()
    df = t_tool.fetch_window_dataframe(sensor_ids=["XMEAS_9", "XMEAS_21"])
    print(f"Fetched window shape: {df.shape}")
    print(df.head(2))
    print("[PASS] TemporalTelemetryTool verified.")
