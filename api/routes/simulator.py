"""FastAPI routes for controlling the dynamic plant simulator and fault injection."""

from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException

from api.schemas import FaultInjectionRequest, SimulatorStatusResponse
from simulator.plant_simulator import PlantSimulator
from simulator.fault_injector import FaultInjector, AVAILABLE_FAULTS
from simulator.stream_publisher import StreamPublisher

router = APIRouter(prefix="/simulator", tags=["Plant Simulator"])

# Global singleton instances shared across the running API process
GLOBAL_SIMULATOR = PlantSimulator()
GLOBAL_INJECTOR = FaultInjector(GLOBAL_SIMULATOR)
GLOBAL_PUBLISHER = StreamPublisher(interval_sec=1.0)
# Ensure publisher shares the same simulator instance
GLOBAL_PUBLISHER.simulator = GLOBAL_SIMULATOR
GLOBAL_PUBLISHER.injector = GLOBAL_INJECTOR


@router.get("/status", response_model=SimulatorStatusResponse)
async def get_simulator_status():
    """Retrieve current state, tick count, active fault, and latest sensor readings."""
    readings = dict(GLOBAL_SIMULATOR.current_state)
    return SimulatorStatusResponse(
        is_running=GLOBAL_PUBLISHER.running,
        active_fault=GLOBAL_SIMULATOR.active_fault,
        total_ticks=GLOBAL_SIMULATOR.total_ticks,
        latest_readings=readings,
        available_faults=GLOBAL_INJECTOR.list_available_faults(),
    )


@router.get("/faults")
async def list_available_faults():
    """List available simulated faults with downstream propagation trajectories and delays."""
    return GLOBAL_INJECTOR.list_available_faults()


@router.post("/inject")
async def inject_fault(req: FaultInjectionRequest):
    """Trigger a named fault (e.g. cooling_water_loss, feed_valve_closing, IDV(4)) in the simulator."""
    try:
        res = GLOBAL_INJECTOR.trigger_fault(req.fault_code)
        return res
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/clear")
async def clear_fault():
    """Reset plant simulator to steady-state normal conditions."""
    return GLOBAL_INJECTOR.clear_fault()


@router.post("/mitigate")
async def apply_mitigation():
    """Apply operator mitigation to resolve the active plant disturbance and restore steady-state."""
    active = GLOBAL_SIMULATOR.active_fault or "UNKNOWN_FAULT"
    res = GLOBAL_INJECTOR.clear_fault()
    return {
        "status": "mitigated",
        "resolved_fault": active,
        "message": f"Operator mitigation executed for {active}. All controller loops and valves restored to safe baseline.",
        "sim_state": res,
    }


@router.post("/step")
async def step_simulation():
    """Advance simulation by one timestep and return latest sensor measurements."""
    state = GLOBAL_SIMULATOR.step()
    return state


@router.post("/start_streaming")
async def start_streaming():
    """Start 1 Hz live streaming publisher into TimescaleDB in a background thread."""
    if GLOBAL_PUBLISHER.running:
        return {"status": "already_running", "message": "Stream publisher is already active."}
    GLOBAL_PUBLISHER.start_background()
    return {"status": "started", "message": "1 Hz TimescaleDB streaming started in background."}


@router.post("/stop_streaming")
async def stop_streaming():
    """Stop the background TimescaleDB streaming publisher."""
    if not GLOBAL_PUBLISHER.running:
        return {"status": "not_running", "message": "Stream publisher is not currently running."}
    GLOBAL_PUBLISHER.stop()
    return {"status": "stopped", "message": "Stream publisher stopped."}
