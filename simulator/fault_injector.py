"""Fault injector module to manipulate simulator conditions on demand.

Supports named faults (e.g. cooling_water_loss, feed_valve_closing) as well as
standard Tennessee Eastman Process IDV codes (e.g. IDV(4), IDV(6), IDV(11)).
Tracks downstream propagation trajectories and delays across plant units.
"""

import sys
from pathlib import Path
from typing import List, Dict, Optional, Any

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from simulator.plant_simulator import PlantSimulator

AVAILABLE_FAULTS = [
    {
        "id": "cooling_water_loss",
        "code": "IDV(4)",
        "name": "Cooling Water Loss",
        "title": "Reactor Cooling Water Inlet Temp Step Increase / Supply Loss",
        "primary_unit": "UNIT_REACTOR",
        "initiating_sensors": ["XMEAS_9", "XMEAS_21"],
        "propagation_path": ["UNIT_REACTOR", "UNIT_CONDENSER", "UNIT_SEPARATOR", "UNIT_COMPRESSOR", "UNIT_STRIPPER"],
        "delays_sec": {
            "UNIT_REACTOR": 0,
            "UNIT_CONDENSER": 5,
            "UNIT_SEPARATOR": 12,
            "UNIT_COMPRESSOR": 20,
            "UNIT_STRIPPER": 25,
        },
        "description": "Step increase in cooling water temperature causing reactor thermal excursion that propagates downstream through product condenser.",
    },
    {
        "id": "feed_valve_closing",
        "code": "IDV(6)",
        "name": "Feed Valve Closing",
        "title": "Reactant A Feed Valve Closing / Feed Loss",
        "primary_unit": "UNIT_FEED",
        "initiating_sensors": ["XMEAS_1"],
        "propagation_path": ["UNIT_FEED", "UNIT_REACTOR", "UNIT_SEPARATOR", "UNIT_STRIPPER"],
        "delays_sec": {
            "UNIT_FEED": 0,
            "UNIT_REACTOR": 4,
            "UNIT_SEPARATOR": 10,
            "UNIT_STRIPPER": 18,
        },
        "description": "Sudden loss of reactant A feed stream causing reactor starvation, pressure drop, and reduced product underflow.",
    },
    {
        "id": "cooling_valve_sticking",
        "code": "IDV(11)",
        "name": "Cooling Valve Sticking",
        "title": "Reactor Cooling Water Valve Sticking / Hunting",
        "primary_unit": "UNIT_REACTOR",
        "initiating_sensors": ["XMEAS_9", "XMEAS_21", "XMV_10"],
        "propagation_path": ["UNIT_REACTOR", "UNIT_CONDENSER", "UNIT_SEPARATOR"],
        "delays_sec": {
            "UNIT_REACTOR": 0,
            "UNIT_CONDENSER": 6,
            "UNIT_SEPARATOR": 14,
        },
        "description": "Mechanical valve stiction inducing limit cycle oscillations across reactor temperature control loop.",
    },
    {
        "id": "feed_ratio_step",
        "code": "IDV(1)",
        "name": "Feed Ratio Step Change",
        "title": "A/C Feed Ratio Step Disturbance",
        "primary_unit": "UNIT_FEED",
        "initiating_sensors": ["XMEAS_4"],
        "propagation_path": ["UNIT_FEED", "UNIT_REACTOR"],
        "delays_sec": {
            "UNIT_FEED": 0,
            "UNIT_REACTOR": 3,
        },
        "description": "Feed composition step change disturbing reaction kinetics and stoichiometry.",
    },
    {
        "id": "condenser_cooling_loss",
        "code": "CONDENSER_COOLING_LOSS",
        "name": "Condenser Cooling Loss",
        "title": "Condenser Cooling Water Failure",
        "primary_unit": "UNIT_CONDENSER",
        "initiating_sensors": ["XMEAS_22"],
        "propagation_path": ["UNIT_CONDENSER", "UNIT_SEPARATOR"],
        "delays_sec": {
            "UNIT_CONDENSER": 0,
            "UNIT_SEPARATOR": 6,
        },
        "description": "Condenser cooling water supply restriction leading to higher separator inlet vapor temperatures.",
    },
    {
        "id": "plant_wide_cascade",
        "code": "ALL(43)",
        "name": "Plant-Wide Multi-Unit Cascade",
        "title": "Severe Plant-Wide Cascade Propagating Across All 43 Sensors & 6 Units",
        "primary_unit": "UNIT_FEED",
        "initiating_sensors": [f"XMEAS_{i}" for i in range(1, 42)] + ["XMV_10", "XMV_11"],
        "propagation_path": ["UNIT_FEED", "UNIT_REACTOR", "UNIT_CONDENSER", "UNIT_SEPARATOR", "UNIT_COMPRESSOR", "UNIT_STRIPPER"],
        "delays_sec": {
            "UNIT_FEED": 0,
            "UNIT_REACTOR": 4,
            "UNIT_CONDENSER": 8,
            "UNIT_SEPARATOR": 12,
            "UNIT_COMPRESSOR": 18,
            "UNIT_STRIPPER": 24,
        },
        "description": "Massive cascading stoichiometric imbalance initiated at feed manifold and propagating across all 6 unit operations, affecting all 43 sensors and control valves.",
    },
]

# Fast lookup index mapping any alias/name/code to canonical fault dict
_ALIAS_LOOKUP: Dict[str, Dict[str, Any]] = {}
for _f in AVAILABLE_FAULTS:
    _ALIAS_LOOKUP[_f["id"].lower()] = _f
    _ALIAS_LOOKUP[_f["code"].lower()] = _f
    _ALIAS_LOOKUP[_f["name"].lower().replace(" ", "_")] = _f
    # normalized variants: idv4, idv(4), etc.
    clean_code = _f["code"].lower().replace("(", "").replace(")", "")
    _ALIAS_LOOKUP[clean_code] = _f


class FaultInjector:
    """Manages injection and clearance of named faults on an active PlantSimulator instance."""

    def __init__(self, simulator: PlantSimulator):
        self.simulator = simulator

    def list_available_faults(self) -> List[Dict[str, Any]]:
        """List all supported named fault scenarios and their physical propagation paths."""
        return AVAILABLE_FAULTS

    def trigger_fault(self, fault_name_or_code: str) -> Dict[str, Any]:
        """Inject a named fault into the running simulator.

        Args:
            fault_name_or_code: Named fault (e.g. 'cooling_water_loss') or IDV code (e.g. 'IDV(4)').

        Returns:
            Dict containing injection status, canonical fault info, and propagation trajectory.
        """
        key = str(fault_name_or_code).strip().lower().replace(" ", "_")
        fault_info = _ALIAS_LOOKUP.get(key)

        if not fault_info:
            valid_names = [f["id"] for f in AVAILABLE_FAULTS] + [f["code"] for f in AVAILABLE_FAULTS]
            raise ValueError(f"Unknown fault '{fault_name_or_code}'. Available faults: {valid_names}")

        canonical_code = fault_info["code"]
        self.simulator.set_fault(canonical_code)

        return {
            "status": "injected",
            "fault_id": fault_info["id"],
            "fault_code": canonical_code,
            "fault_name": fault_info["name"],
            "primary_unit": fault_info["primary_unit"],
            "propagation_path": fault_info["propagation_path"],
            "delays_sec": fault_info["delays_sec"],
            "message": f"Fault '{fault_info['name']}' ({canonical_code}) activated in {fault_info['primary_unit']}.",
        }

    def clear_fault(self) -> Dict[str, Any]:
        """Clear the active fault and restore normal steady-state plant operation."""
        self.simulator.set_fault(None)
        return {
            "status": "cleared",
            "message": "Plant restored to normal steady-state operation.",
        }

    def get_current_fault(self) -> Optional[Dict[str, Any]]:
        """Return the currently active fault details, or None if operating normally."""
        active_code = self.simulator.active_fault
        if not active_code:
            return None

        key = active_code.lower().replace(" ", "_")
        return _ALIAS_LOOKUP.get(key, {"code": active_code, "name": active_code})


if __name__ == "__main__":
    print("=" * 70)
    print("Testing Phase 7 Fault Injector on Demand...")
    print("=" * 70)

    sim = PlantSimulator()
    injector = FaultInjector(sim)

    print("\n1. Available named faults:")
    for f in injector.list_available_faults():
        print(f"  * {f['id']:<22} [{f['code']:<7}] -> Unit: {f['primary_unit']:<15} Path: {' -> '.join(f['propagation_path'])}")

    print("\n2. Triggering named fault: 'cooling_water_loss'...")
    res1 = injector.trigger_fault("cooling_water_loss")
    print(f"  Result: {res1['status']} | Active: {injector.get_current_fault()['name']}")

    print("\n3. Triggering IDV code: 'IDV(6)' (Feed valve closing)...")
    res2 = injector.trigger_fault("IDV(6)")
    print(f"  Result: {res2['status']} | Active: {injector.get_current_fault()['name']}")

    print("\n4. Clearing fault...")
    res3 = injector.clear_fault()
    print(f"  Result: {res3['status']} | Active: {injector.get_current_fault()}")

    print("=" * 70)
    print("[PASS] FaultInjector verified successfully!")
    print("=" * 70)
