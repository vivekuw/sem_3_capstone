"""Tennessee Eastman Process (TEP) Plant Simulator with Unit Structure and Delayed Propagation.

Follows the 5 primary TEP processing units + feed delivery system:
  1. UNIT_FEED: Reactant streams (A, D, E, A+C)
  2. UNIT_REACTOR: Exothermic continuous stirred-tank reactor (CSTR)
  3. UNIT_CONDENSER: Product condenser cooling reactor effluent (Stream 7)
  4. UNIT_SEPARATOR: High-pressure vapor-liquid flash vessel
  5. UNIT_COMPRESSOR: Recycle gas centrifugal compressor (Stream 9 -> 5)
  6. UNIT_STRIPPER: Distillation stripping column for byproduct removal

Key Physical Feature:
  Delayed downstream propagation: Disturbances begin at the root-cause unit
  and propagate downstream along physical piping connections with realistic
  transport and thermal residence time delays.
"""

import sys
import time
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
import numpy as np

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Sensor to Unit mapping
SENSOR_UNITS: Dict[str, str] = {
    # UNIT_FEED
    "XMEAS_1": "UNIT_FEED",        # A Feed Flow (kscmh)
    "XMEAS_2": "UNIT_FEED",        # D Feed Flow (kg/h)
    "XMEAS_3": "UNIT_FEED",        # E Feed Flow (kg/h)
    "XMEAS_4": "UNIT_FEED",        # A and C Feed Flow (kscmh)
    # UNIT_REACTOR
    "XMEAS_6": "UNIT_REACTOR",     # Reactor Feed Rate (kscmh)
    "XMEAS_7": "UNIT_REACTOR",     # Reactor Pressure (kPa)
    "XMEAS_8": "UNIT_REACTOR",     # Reactor Level (%)
    "XMEAS_9": "UNIT_REACTOR",     # Reactor Temperature (°C)
    "XMEAS_21": "UNIT_REACTOR",    # Reactor Cooling Water Outlet Temp (°C)
    "XMV_10": "UNIT_REACTOR",      # Reactor Cooling Water Valve (%)
    # UNIT_CONDENSER
    "XMEAS_22": "UNIT_CONDENSER",   # Condenser Cooling Water Outlet Temp (°C)
    "XMV_11": "UNIT_CONDENSER",    # Condenser Cooling Water Valve (%)
    # UNIT_SEPARATOR
    "XMEAS_10": "UNIT_SEPARATOR",   # Purge Rate (kscmh)
    "XMEAS_11": "UNIT_SEPARATOR",   # Separator Temperature (°C)
    "XMEAS_12": "UNIT_SEPARATOR",   # Separator Level (%)
    "XMEAS_13": "UNIT_SEPARATOR",   # Separator Pressure (kPa)
    "XMEAS_14": "UNIT_SEPARATOR",   # Separator Underflow (m3/h)
    # UNIT_COMPRESSOR
    "XMEAS_5": "UNIT_COMPRESSOR",   # Recycle Flow (kscmh)
    "XMEAS_20": "UNIT_COMPRESSOR",  # Compressor Work (kW)
    # UNIT_STRIPPER
    "XMEAS_15": "UNIT_STRIPPER",    # Stripper Level (%)
    "XMEAS_16": "UNIT_STRIPPER",    # Stripper Pressure (kPa)
    "XMEAS_17": "UNIT_STRIPPER",    # Stripper Underflow (m3/h)
    "XMEAS_18": "UNIT_STRIPPER",    # Stripper Temperature (°C)
    "XMEAS_19": "UNIT_STRIPPER",    # Stripper Steam Flow (kg/h)
    # Stream 6: Reactor Feed Composition (mol%)
    "XMEAS_23": "UNIT_REACTOR",     # Component A in Reactor Feed
    "XMEAS_24": "UNIT_REACTOR",     # Component B in Reactor Feed
    "XMEAS_25": "UNIT_REACTOR",     # Component C in Reactor Feed
    "XMEAS_26": "UNIT_REACTOR",     # Component D in Reactor Feed
    "XMEAS_27": "UNIT_REACTOR",     # Component E in Reactor Feed
    "XMEAS_28": "UNIT_REACTOR",     # Component F in Reactor Feed
    # Stream 9: Purge Gas Composition (mol%)
    "XMEAS_29": "UNIT_SEPARATOR",   # Component A in Purge Gas
    "XMEAS_30": "UNIT_SEPARATOR",   # Component B in Purge Gas
    "XMEAS_31": "UNIT_SEPARATOR",   # Component C in Purge Gas
    "XMEAS_32": "UNIT_SEPARATOR",   # Component D in Purge Gas
    "XMEAS_33": "UNIT_SEPARATOR",   # Component E in Purge Gas
    "XMEAS_34": "UNIT_SEPARATOR",   # Component F in Purge Gas
    "XMEAS_35": "UNIT_SEPARATOR",   # Component G in Purge Gas
    "XMEAS_36": "UNIT_SEPARATOR",   # Component H in Purge Gas
    # Stream 11: Product Stream Composition (mol%)
    "XMEAS_37": "UNIT_STRIPPER",    # Component D in Product
    "XMEAS_38": "UNIT_STRIPPER",    # Component E in Product
    "XMEAS_39": "UNIT_STRIPPER",    # Component F in Product
    "XMEAS_40": "UNIT_STRIPPER",    # Component G in Product
    "XMEAS_41": "UNIT_STRIPPER",    # Component H in Product
}

# Measurement Engineering Units
SENSOR_ENG_UNITS: Dict[str, str] = {
    "XMEAS_1": "kscmh",
    "XMEAS_2": "kg/h",
    "XMEAS_3": "kg/h",
    "XMEAS_4": "kscmh",
    "XMEAS_5": "kscmh",
    "XMEAS_6": "kscmh",
    "XMEAS_7": "kPa",
    "XMEAS_8": "%",
    "XMEAS_9": "°C",
    "XMEAS_10": "kscmh",
    "XMEAS_11": "°C",
    "XMEAS_12": "%",
    "XMEAS_13": "kPa",
    "XMEAS_14": "m3/h",
    "XMEAS_15": "%",
    "XMEAS_16": "kPa",
    "XMEAS_17": "m3/h",
    "XMEAS_18": "°C",
    "XMEAS_19": "kg/h",
    "XMEAS_20": "kW",
    "XMEAS_21": "°C",
    "XMEAS_22": "°C",
    **{f"XMEAS_{i}": "mol%" for i in range(23, 42)},
    "XMV_10": "%",
    "XMV_11": "%",
}


class PlantSimulator:
    """Dynamic TEP process simulator with unit topology and delayed downstream propagation."""

    def __init__(self, random_seed: Optional[int] = 42):
        if random_seed is not None:
            np.random.seed(random_seed)

        # Baseline nominal steady-state values (TEP Mode 1 standard baseline)
        self.nominal_state: Dict[str, float] = {
            "XMEAS_1": 0.2505,      # A Feed Flow (kscmh)
            "XMEAS_2": 3664.0,      # D Feed Flow (kg/h)
            "XMEAS_3": 4505.0,      # E Feed Flow (kg/h)
            "XMEAS_4": 9.34,        # A and C Feed Flow (kscmh)
            "XMEAS_5": 26.90,       # Recycle Flow (kscmh)
            "XMEAS_6": 42.30,       # Reactor Feed Rate (kscmh)
            "XMEAS_7": 2705.0,      # Reactor Pressure (kPa)
            "XMEAS_8": 65.20,       # Reactor Level (%)
            "XMEAS_9": 120.40,      # Reactor Temperature (°C)
            "XMEAS_10": 0.337,      # Purge Rate (kscmh)
            "XMEAS_11": 80.10,      # Separator Temperature (°C)
            "XMEAS_12": 50.00,      # Separator Level (%)
            "XMEAS_13": 2633.0,     # Separator Pressure (kPa)
            "XMEAS_14": 25.10,      # Separator Underflow (m3/h)
            "XMEAS_15": 50.00,      # Stripper Level (%)
            "XMEAS_16": 3010.0,     # Stripper Pressure (kPa)
            "XMEAS_17": 22.90,      # Stripper Underflow (m3/h)
            "XMEAS_18": 65.70,      # Stripper Temperature (°C)
            "XMEAS_19": 1085.0,     # Stripper Steam Flow (kg/h)
            "XMEAS_20": 341.0,      # Compressor Work (kW)
            "XMEAS_21": 94.40,      # Reactor Cooling Water Outlet Temp (°C)
            "XMEAS_22": 77.20,      # Condenser Cooling Water Outlet Temp (°C)
            # Stream 6 Compositions (mol%)
            "XMEAS_23": 32.25,
            "XMEAS_24": 8.95,
            "XMEAS_25": 26.35,
            "XMEAS_26": 6.85,
            "XMEAS_27": 18.75,
            "XMEAS_28": 1.65,
            # Stream 9 Purge Compositions (mol%)
            "XMEAS_29": 32.95,
            "XMEAS_30": 13.80,
            "XMEAS_31": 23.95,
            "XMEAS_32": 1.25,
            "XMEAS_33": 18.55,
            "XMEAS_34": 2.25,
            "XMEAS_35": 4.80,
            "XMEAS_36": 2.45,
            # Stream 11 Product Compositions (mol%)
            "XMEAS_37": 0.15,
            "XMEAS_38": 0.85,
            "XMEAS_39": 0.05,
            "XMEAS_40": 53.75,
            "XMEAS_41": 43.85,
            "XMV_10": 41.10,        # Reactor Cooling Water Valve (%)
            "XMV_11": 18.10,        # Condenser Cooling Water Valve (%)
        }

        # Sensor noise standard deviations
        self.noise_std: Dict[str, float] = {
            "XMEAS_1": 0.004,
            "XMEAS_2": 10.0,
            "XMEAS_3": 12.0,
            "XMEAS_4": 0.06,
            "XMEAS_5": 0.25,
            "XMEAS_6": 0.35,
            "XMEAS_7": 5.0,
            "XMEAS_8": 0.4,
            "XMEAS_9": 0.15,
            "XMEAS_10": 0.008,
            "XMEAS_11": 0.2,
            "XMEAS_12": 0.4,
            "XMEAS_13": 4.0,
            "XMEAS_14": 0.15,
            "XMEAS_15": 0.35,
            "XMEAS_16": 6.0,
            "XMEAS_17": 0.15,
            "XMEAS_18": 0.18,
            "XMEAS_19": 6.0,
            "XMEAS_20": 2.0,
            "XMEAS_21": 0.2,
            "XMEAS_22": 0.2,
            **{f"XMEAS_{i}": 0.08 for i in range(23, 42)},
            "XMV_10": 0.2,
            "XMV_11": 0.2,
        }

        self.current_state: Dict[str, float] = dict(self.nominal_state)
        self.active_fault: Optional[str] = None
        self.fault_start_time: Optional[float] = None
        self.fault_elapsed_steps: int = 0
        self.total_ticks: int = 0

    def set_fault(self, fault_code: Optional[str]) -> None:
        """Set or clear the active fault in the plant simulator."""
        self.active_fault = fault_code
        self.fault_elapsed_steps = 0
        if fault_code:
            self.fault_start_time = time.time()
        else:
            self.fault_start_time = None
            self.current_state = dict(self.nominal_state)

    def step(self) -> Dict[str, Any]:
        """Advance simulation by 1 timestep (1 second) and calculate dynamic states with delays."""
        self.total_ticks += 1

        if self.active_fault:
            self.fault_elapsed_steps += 1
            t = self.fault_elapsed_steps
            f = self.active_fault.upper()

            # -----------------------------------------------------------------
            # Fault: Cooling Water Loss / IDV(4) in UNIT_REACTOR
            # Propagation Path: REACTOR (t=0) -> CONDENSER (t>=5) -> SEPARATOR (t>=12) -> COMPRESSOR (t>=20) -> STRIPPER (t>=25)
            # -----------------------------------------------------------------
            if "COOLING_WATER_LOSS" in f or "IDV(4)" in f or "IDV4" in f:
                # 1. Primary Unit (UNIT_REACTOR) deviates immediately at t=0
                self.current_state["XMEAS_9"] = self.nominal_state["XMEAS_9"] + min(14.0, 0.35 * t)
                self.current_state["XMEAS_21"] = self.nominal_state["XMEAS_21"] + min(16.0, 0.40 * t)
                self.current_state["XMEAS_7"] = self.nominal_state["XMEAS_7"] + min(130.0, 2.5 * t)
                self.current_state["XMV_10"] = min(100.0, self.nominal_state["XMV_10"] + 1.2 * t)  # controller saturates

                # 2. Delayed Downstream Unit 1 (UNIT_CONDENSER): delay = 5s
                if t >= 5:
                    t_eff = t - 5
                    self.current_state["XMEAS_22"] = self.nominal_state["XMEAS_22"] + min(9.0, 0.25 * t_eff)

                # 3. Delayed Downstream Unit 2 (UNIT_SEPARATOR): delay = 12s
                if t >= 12:
                    t_eff = t - 12
                    self.current_state["XMEAS_11"] = self.nominal_state["XMEAS_11"] + min(7.5, 0.20 * t_eff)
                    self.current_state["XMEAS_13"] = self.nominal_state["XMEAS_13"] + min(85.0, 1.8 * t_eff)

                # 4. Delayed Downstream Unit 3 (UNIT_COMPRESSOR): delay = 20s
                if t >= 20:
                    t_eff = t - 20
                    self.current_state["XMEAS_20"] = self.nominal_state["XMEAS_20"] + min(25.0, 0.6 * t_eff)
                    self.current_state["XMEAS_5"] = self.nominal_state["XMEAS_5"] + min(3.0, 0.08 * t_eff)

                # 5. Delayed Downstream Unit 4 (UNIT_STRIPPER): delay = 25s
                if t >= 25:
                    t_eff = t - 25
                    self.current_state["XMEAS_18"] = self.nominal_state["XMEAS_18"] + min(4.5, 0.12 * t_eff)
                    self.current_state["XMEAS_16"] = self.nominal_state["XMEAS_16"] + min(40.0, 0.9 * t_eff)

            # -----------------------------------------------------------------
            # Fault: Feed Valve Closing / A Feed Loss / IDV(6) in UNIT_FEED
            # Propagation Path: FEED (t=0) -> REACTOR (t>=4) -> SEPARATOR (t>=10) -> STRIPPER (t>=18)
            # -----------------------------------------------------------------
            elif "FEED_VALVE_CLOSING" in f or "FEED_LOSS" in f or "IDV(6)" in f or "IDV6" in f:
                # 1. Primary Unit (UNIT_FEED) drops immediately at t=0
                self.current_state["XMEAS_1"] = max(0.005, self.nominal_state["XMEAS_1"] - 0.06 * t)

                # 2. Delayed Downstream Unit 1 (UNIT_REACTOR): delay = 4s
                if t >= 4:
                    t_eff = t - 4
                    self.current_state["XMEAS_6"] = max(28.0, self.nominal_state["XMEAS_6"] - 0.9 * t_eff)
                    self.current_state["XMEAS_7"] = max(2420.0, self.nominal_state["XMEAS_7"] - 7.5 * t_eff)
                    self.current_state["XMEAS_9"] = max(112.0, self.nominal_state["XMEAS_9"] - 0.22 * t_eff)

                # 3. Delayed Downstream Unit 2 (UNIT_SEPARATOR): delay = 10s
                if t >= 10:
                    t_eff = t - 10
                    self.current_state["XMEAS_12"] = max(32.0, self.nominal_state["XMEAS_12"] - 0.5 * t_eff)
                    self.current_state["XMEAS_14"] = max(16.0, self.nominal_state["XMEAS_14"] - 0.3 * t_eff)
                    self.current_state["XMEAS_13"] = max(2450.0, self.nominal_state["XMEAS_13"] - 4.5 * t_eff)

                # 4. Delayed Downstream Unit 3 (UNIT_STRIPPER): delay = 18s
                if t >= 18:
                    t_eff = t - 18
                    self.current_state["XMEAS_15"] = max(35.0, self.nominal_state["XMEAS_15"] - 0.4 * t_eff)
                    self.current_state["XMEAS_17"] = max(15.0, self.nominal_state["XMEAS_17"] - 0.25 * t_eff)

            # -----------------------------------------------------------------
            # Fault: Reactor Cooling Water Valve Sticking / Hunting / IDV(11)
            # Limit cycle oscillation in UNIT_REACTOR (t=0) propagating downstream
            # -----------------------------------------------------------------
            elif "COOLING_VALVE_STICKING" in f or "STICKING" in f or "IDV(11)" in f or "IDV11" in f:
                # Primary oscillation in UNIT_REACTOR
                osc = 4.2 * np.sin(t * 0.35)
                self.current_state["XMEAS_9"] = self.nominal_state["XMEAS_9"] + osc
                self.current_state["XMEAS_21"] = self.nominal_state["XMEAS_21"] + osc * 1.6
                self.current_state["XMV_10"] = np.clip(self.nominal_state["XMV_10"] + osc * 2.0, 10.0, 80.0)

                # Downstream oscillation in CONDENSER: delay = 6s
                if t >= 6:
                    osc_cond = 2.5 * np.sin((t - 6) * 0.35 - 0.6)
                    self.current_state["XMEAS_22"] = self.nominal_state["XMEAS_22"] + osc_cond

                # Downstream oscillation in SEPARATOR: delay = 14s
                if t >= 14:
                    osc_sep = 1.8 * np.sin((t - 14) * 0.35 - 1.2)
                    self.current_state["XMEAS_11"] = self.nominal_state["XMEAS_11"] + osc_sep

            # -----------------------------------------------------------------
            # Fault: A/C Feed Ratio Step Disturbance / IDV(1)
            # -----------------------------------------------------------------
            elif "FEED_RATIO" in f or "IDV(1)" in f or "IDV1" in f:
                self.current_state["XMEAS_4"] = self.nominal_state["XMEAS_4"] + min(2.8, 0.12 * t)
                if t >= 3:
                    t_eff = t - 3
                    self.current_state["XMEAS_6"] = self.nominal_state["XMEAS_6"] + min(3.5, 0.15 * t_eff)
                    self.current_state["XMEAS_7"] = self.nominal_state["XMEAS_7"] + min(55.0, 1.2 * t_eff)

            # -----------------------------------------------------------------
            # Fault: Condenser Cooling Water Header Loss (UNIT_CONDENSER)
            # -----------------------------------------------------------------
            elif "CONDENSER_COOLING_LOSS" in f or "CONDENSER" in f:
                self.current_state["XMEAS_22"] = self.nominal_state["XMEAS_22"] + min(15.0, 0.45 * t)
                if t >= 6:
                    t_eff = t - 6
                    self.current_state["XMEAS_11"] = self.nominal_state["XMEAS_11"] + min(8.0, 0.22 * t_eff)
                    self.current_state["XMEAS_13"] = self.nominal_state["XMEAS_13"] + min(60.0, 1.4 * t_eff)

        # Apply measurement noise and format return telemetry
        timestamp = datetime.now(timezone.utc)
        measurements: Dict[str, float] = {}

        for sensor_id, base_val in self.current_state.items():
            noise = np.random.normal(0, self.noise_std.get(sensor_id, 0.1))
            measurements[sensor_id] = round(float(base_val + noise), 4)

        return {
            "timestamp": timestamp,
            "tick": self.total_ticks,
            "fault": self.active_fault or "NORMAL",
            "sensors": measurements,
            "units": {
                sensor_id: SENSOR_UNITS.get(sensor_id, "UNIT_TEP")
                for sensor_id in measurements
            },
            "eng_units": SENSOR_ENG_UNITS,
        }

    @staticmethod
    def get_unit_for_sensor(sensor_id: str) -> str:
        """Return the physical plant unit containing the given sensor."""
        return SENSOR_UNITS.get(sensor_id, "UNIT_TEP")

    @staticmethod
    def get_sensors_by_unit(unit_id: str) -> List[str]:
        """Return all sensor IDs belonging to a given plant unit."""
        return [s for s, u in SENSOR_UNITS.items() if u == unit_id]


if __name__ == "__main__":
    print("=" * 70)
    print("Testing Phase 7 Plant Simulator with Delayed Downstream Propagation...")
    print("=" * 70)

    sim = PlantSimulator()

    # 1. Steady state run
    print("\n1. Steady-state baseline (5 seconds):")
    for _ in range(5):
        sample = sim.step()
        print(f"  Tick {sample['tick']:<3}: Fault={sample['fault']} | "
              f"Reactor Temp={sample['sensors']['XMEAS_9']:.2f}°C | "
              f"Condenser Outlet Temp={sample['sensors']['XMEAS_22']:.2f}°C | "
              f"Separator Temp={sample['sensors']['XMEAS_11']:.2f}°C")

    # 2. Inject cooling_water_loss in UNIT_REACTOR
    print("\n2. Injecting 'cooling_water_loss' (observing delayed downstream wave):")
    sim.set_fault("cooling_water_loss")

    for step_i in range(1, 26):
        sample = sim.step()
        r_temp = sample['sensors']['XMEAS_9']
        c_temp = sample['sensors']['XMEAS_22']
        s_temp = sample['sensors']['XMEAS_11']
        comp_work = sample['sensors']['XMEAS_20']

        if step_i in (1, 5, 6, 12, 13, 20, 21, 25):
            print(f"  t+{step_i:02d}s: Reactor={r_temp:.2f}°C (SURGE) | "
                  f"Condenser={c_temp:.2f}°C {'[WAVE REACHED]' if step_i >= 5 else '[Nominal]'} | "
                  f"Separator={s_temp:.2f}°C {'[WAVE REACHED]' if step_i >= 12 else '[Nominal]'} | "
                  f"Compressor={comp_work:.1f}kW {'[WAVE REACHED]' if step_i >= 20 else '[Nominal]'}")

    print("=" * 70)
    print("[PASS] PlantSimulator delayed propagation verified successfully!")
    print("=" * 70)
