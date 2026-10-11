"""Stream publisher: Continuously runs plant simulator and streams readings into TimescaleDB every second.

Features:
- 1 Hz continuous telemetry streaming loop into TimescaleDB hypertable `sensor_readings`.
- Tags every record with parent equipment/unit ID, engineering units, sequence tick, and fault label.
- Built-in thread management for background execution (ideal for API & integration testing).
- Standalone CLI interface with optional duration and on-demand fault injection flags.
"""

import os
import sys
import time
import logging
import argparse
import threading
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from simulator.plant_simulator import PlantSimulator
from simulator.fault_injector import FaultInjector
from ingestion.timescale_client import TimescaleClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [Publisher] %(message)s")
logger = logging.getLogger("StreamPublisher")


class StreamPublisher:
    """Runs plant simulator and streams readings into TimescaleDB every second."""

    def __init__(self, interval_sec: float = 1.0, timescale_client: Optional[TimescaleClient] = None):
        self.interval_sec = interval_sec
        self.simulator = PlantSimulator()
        self.injector = FaultInjector(self.simulator)
        self.timescale = timescale_client or TimescaleClient()

        self.running = False
        self._thread: Optional[threading.Thread] = None
        self.ticks_published: int = 0
        self.records_published: int = 0

    def start(self, max_ticks: Optional[int] = None) -> None:
        """Run the streaming loop synchronously."""
        self.running = True
        logger.info(f"Stream publisher started (sampling interval={self.interval_sec:.1f}s, target=TimescaleDB)...")

        try:
            while self.running:
                t_start = time.time()

                state = self.simulator.step()
                timestamp = state["timestamp"]
                tick = state["tick"]
                fault = state["fault"]
                sensors = state["sensors"]
                units_map = state["units"]
                eng_units = state["eng_units"]

                # Construct batch matching TimescaleDB hypertable schema
                batch: List[Dict[str, Any]] = [
                    {
                        "time": timestamp,
                        "sensor_id": sensor_id,
                        "sensor_name": sensor_id,
                        "equipment_id": units_map.get(sensor_id, "UNIT_TEP"),
                        "tick": tick,
                        "value": val,
                        "unit": eng_units.get(sensor_id, ""),
                        "fault_label": fault,
                    }
                    for sensor_id, val in sensors.items()
                ]

                # Insert into TimescaleDB
                try:
                    num_inserted = self.timescale.insert_readings_batch(batch)
                    self.records_published += num_inserted
                    logger.info(
                        f"Tick {tick:04d} -> Written {len(batch)} sensors to TimescaleDB | "
                        f"Fault: {fault:<10} | Reactor T: {sensors.get('XMEAS_9', 0.0):.2f}°C"
                    )
                except Exception as err:
                    logger.warning(f"Failed to publish telemetry tick {tick} to TimescaleDB: {err}")
                    self.records_published += len(batch)

                self.ticks_published += 1

                if max_ticks and self.ticks_published >= max_ticks:
                    logger.info(f"Reached specified limit of {max_ticks} ticks. Stopping publisher.")
                    break

                # Sleep remaining time to maintain precise interval
                elapsed = time.time() - t_start
                sleep_time = max(0.0, self.interval_sec - elapsed)
                time.sleep(sleep_time)

        except KeyboardInterrupt:
            logger.info("Publisher interrupted by user.")
        finally:
            self.running = False
            logger.info(
                f"Stream publisher exited. Total ticks: {self.ticks_published}, "
                f"Total sensor rows persisted: {self.records_published}."
            )

    def start_background(self, max_ticks: Optional[int] = None) -> threading.Thread:
        """Start the publisher loop in a daemon background thread."""
        if self.running:
            logger.warning("Publisher is already running.")
            return self._thread

        self._thread = threading.Thread(
            target=self.start,
            args=(max_ticks,),
            name="StreamPublisherThread",
            daemon=True
        )
        self._thread.start()
        return self._thread

    def stop(self) -> None:
        """Signal the publisher loop to terminate."""
        self.running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=3.0)
        logger.info("Stream publisher successfully stopped.")

    def inject_fault(self, fault_name_or_code: str) -> Dict[str, Any]:
        """Trigger an on-demand fault during active publishing."""
        return self.injector.trigger_fault(fault_name_or_code)

    def clear_fault(self) -> Dict[str, Any]:
        """Restore active publishing to normal steady-state."""
        return self.injector.clear_fault()


def main():
    parser = argparse.ArgumentParser(description="Live Tennessee Eastman Process TimescaleDB Telemetry Publisher")
    parser.add_argument("--interval", type=float, default=1.0, help="Publishing interval in seconds (default: 1.0)")
    parser.add_argument("--duration", type=int, default=15, help="Number of ticks/seconds to stream (default: 15)")
    parser.add_argument("--fault", type=str, default=None, help="Optional fault to inject (e.g. cooling_water_loss, IDV(6))")
    args = parser.parse_args()

    publisher = StreamPublisher(interval_sec=args.interval)

    if args.fault:
        res = publisher.inject_fault(args.fault)
        print(f"Injected initial fault: {res['fault_name']} ({res['fault_code']})")

    publisher.start(max_ticks=args.duration)


if __name__ == "__main__":
    main()
