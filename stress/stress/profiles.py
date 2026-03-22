"""Named stress profiles per spec.

SP-0: Baseline (no stress)
SP-1: Moderate stress
SP-2: Severe stress
"""
from __future__ import annotations

from typing import Dict, Any

# SP-0: Baseline — no stress applied
SP_0: Dict[str, Any] = {}

# SP-1: Moderate stress
SP_1: Dict[str, Any] = {
    "SP-1": {"rate": 0.001},           # ~1 fault per 1000 seconds
    "SP-2": {"cycle_period_s": 600.0, "amplitude": 2.0},
    "SP-3": {"availability_pct": 90.0, "interruption_duration_s": 3.0, "schedule": "periodic"},
    "SP-4": {"baseline_latency_ms": 50.0, "jitter_pct": 30.0, "packet_loss_probability": 0.02},
    "SP-5": {"max_duration_s": 60.0, "trigger_offset_s": 30.0},
}

# SP-2: Severe stress
SP_2: Dict[str, Any] = {
    "SP-1": {"rate": 0.01},            # ~1 fault per 100 seconds
    "SP-2": {"cycle_period_s": 300.0, "amplitude": 5.0},
    "SP-3": {"availability_pct": 60.0, "interruption_duration_s": 10.0, "schedule": "stochastic"},
    "SP-4": {"baseline_latency_ms": 200.0, "jitter_pct": 80.0, "packet_loss_probability": 0.15},
    "SP-5": {"max_duration_s": 120.0, "trigger_offset_s": 15.0},
}

PROFILES = {
    "SP-0": SP_0,
    "SP-1": SP_1,
    "SP-2": SP_2,
}
