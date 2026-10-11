"""Stream consumer that polls live sensor readings from TimescaleDB and invokes anomaly detection."""

import time
import logging
from datetime import datetime, timedelta, timezone
from typing import Callable, Optional
from ingestion.timescale_client import TimescaleClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("StreamConsumer")


class StreamConsumer:
    """Reads newly ingested telemetry and pushes sliding windows to anomaly detectors."""

    def __init__(self, poll_interval_sec: float = 2.0, window_size_sec: int = 120):
        self.client = TimescaleClient()
        self.poll_interval = poll_interval_sec
        self.window_size_sec = window_size_sec
        self.running = False
        self._last_processed_time = datetime.now(timezone.utc) - timedelta(seconds=window_size_sec)

    def start(self, on_window_callback: Optional[Callable] = None):
        """Start the polling loop."""
        self.running = True
        logger.info(f"Stream consumer started (polling every {self.poll_interval}s, window={self.window_size_sec}s)...")

        while self.running:
            try:
                now = datetime.now(timezone.utc)
                start_window = now - timedelta(seconds=self.window_size_sec)
                readings = self.client.query_window(start_window, now)

                if readings and on_window_callback:
                    on_window_callback(readings)

                self._last_processed_time = now
            except Exception as e:
                logger.error(f"Error in consumer loop: {e}")

            time.sleep(self.poll_interval)

    def stop(self):
        """Stop polling loop."""
        self.running = False
        logger.info("Stream consumer stopped.")


if __name__ == "__main__":
    consumer = StreamConsumer(poll_interval_sec=3.0)
    def dummy_callback(readings):
        print(f"Received {len(readings)} readings in window.")
    consumer.start(dummy_callback)
