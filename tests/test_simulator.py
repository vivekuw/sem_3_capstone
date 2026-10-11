"""Comprehensive unit and integration tests for Phase 7: TEP Live Simulator, Fault Injector & Stream Publisher."""

import sys
import time
from pathlib import Path
import pytest

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from simulator.plant_simulator import PlantSimulator, SENSOR_UNITS
from simulator.fault_injector import FaultInjector, AVAILABLE_FAULTS
from simulator.stream_publisher import StreamPublisher


def test_plant_simulator_units_and_baseline():
    """Verify simulator follows the 5 TEP units and produces valid nominal signals."""
    sim = PlantSimulator(random_seed=123)

    # Required TEP Units
    expected_units = {"UNIT_FEED", "UNIT_REACTOR", "UNIT_CONDENSER", "UNIT_SEPARATOR", "UNIT_COMPRESSOR", "UNIT_STRIPPER"}
    actual_units = set(SENSOR_UNITS.values())
    assert expected_units.issubset(actual_units)

    # Step simulator in steady state
    state = sim.step()
    assert state["fault"] == "NORMAL"
    assert len(state["sensors"]) >= 22
    assert "XMEAS_9" in state["sensors"]  # Reactor Temp
    assert "XMEAS_22" in state["sensors"] # Condenser Temp
    assert "XMEAS_11" in state["sensors"] # Separator Temp
    assert "XMEAS_5" in state["sensors"]  # Compressor Recycle
    assert "XMEAS_18" in state["sensors"] # Stripper Temp

    # Verify nominal ranges
    assert 115.0 <= state["sensors"]["XMEAS_9"] <= 125.0
    assert 74.0 <= state["sensors"]["XMEAS_22"] <= 80.0
    assert 2600.0 <= state["sensors"]["XMEAS_7"] <= 2800.0


def test_delayed_downstream_propagation_cooling_water_loss():
    """Verify that cooling water loss exhibits true physical downstream propagation delays."""
    sim = PlantSimulator(random_seed=42)
    injector = FaultInjector(sim)

    # Baseline step
    base_state = sim.step()
    base_r_temp = base_state["sensors"]["XMEAS_9"]
    base_c_temp = base_state["sensors"]["XMEAS_22"]
    base_s_temp = base_state["sensors"]["XMEAS_11"]

    # Inject cooling_water_loss in UNIT_REACTOR
    injector.trigger_fault("cooling_water_loss")

    # t = 1: UNIT_REACTOR should deviate immediately, downstream units should remain nominal
    s1 = sim.step()
    assert s1["sensors"]["XMEAS_9"] > base_r_temp + 0.2  # Reactor surge immediate
    assert abs(s1["sensors"]["XMEAS_22"] - base_c_temp) < 1.0  # Condenser not yet affected
    assert abs(s1["sensors"]["XMEAS_11"] - base_s_temp) < 1.0  # Separator not yet affected

    # Step up to t = 6 (Delay for Condenser is 5s)
    for _ in range(5):
        s_mid = sim.step()

    # At t = 6: Condenser should show significant deviation
    assert s_mid["sensors"]["XMEAS_22"] > base_c_temp + 0.15
    # Separator (delay = 12s) should STILL be near nominal
    assert abs(s_mid["sensors"]["XMEAS_11"] - base_s_temp) < 1.0

    # Step up to t = 15 (Delay for Separator is 12s)
    for _ in range(9):
        s_late = sim.step()

    # At t = 15: Separator temperature should also have surged!
    assert s_late["sensors"]["XMEAS_11"] > base_s_temp + 0.3


def test_delayed_downstream_propagation_feed_valve_closing():
    """Verify that feed valve closing drops feed immediately and propagates to reactor & separator."""
    sim = PlantSimulator(random_seed=42)
    injector = FaultInjector(sim)

    base = sim.step()
    base_feed = base["sensors"]["XMEAS_1"]
    base_r_press = base["sensors"]["XMEAS_7"]

    # Inject feed valve closing
    injector.trigger_fault("feed_valve_closing")

    # t = 1: Feed drops immediately
    s1 = sim.step()
    assert s1["sensors"]["XMEAS_1"] < base_feed

    # Advance to t = 8 (Reactor delay is 4s)
    for _ in range(7):
        s8 = sim.step()

    # Reactor pressure should have dropped noticeably
    assert s8["sensors"]["XMEAS_7"] < base_r_press - 10.0


def test_fault_injector_alias_handling_and_clearing():
    """Verify injector accepts both named faults and standard IDV codes, and clears cleanly."""
    sim = PlantSimulator()
    injector = FaultInjector(sim)

    # Test IDV code alias
    res_idv = injector.trigger_fault("IDV(4)")
    assert res_idv["status"] == "injected"
    assert res_idv["fault_code"] == "IDV(4)"
    assert res_idv["primary_unit"] == "UNIT_REACTOR"

    # Test named fault alias
    res_named = injector.trigger_fault("feed_valve_closing")
    assert res_named["status"] == "injected"
    assert res_named["fault_code"] == "IDV(6)"
    assert res_named["primary_unit"] == "UNIT_FEED"

    # Clear fault
    res_clear = injector.clear_fault()
    assert res_clear["status"] == "cleared"
    assert injector.get_current_fault() is None

    # Step simulator after clear -> should be NORMAL
    st = sim.step()
    assert st["fault"] == "NORMAL"


def test_stream_publisher_batch_generation_and_persistence():
    """Verify StreamPublisher formats and persists live ticks to TimescaleDB."""
    publisher = StreamPublisher(interval_sec=0.01)

    # Run publisher for 3 fast test ticks
    publisher.start(max_ticks=3)

    assert publisher.ticks_published == 3
    assert publisher.records_published >= 3 * 22  # At least 22 sensors per tick
