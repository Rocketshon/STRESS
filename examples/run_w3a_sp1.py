"""Example: Run W3-A distributed coordination under SP-1 moderate stress."""
from stress.runner import run_benchmark

run_benchmark(
    out_dir="report_w3a_sp1",
    workload_id="W3-A",
    workload_version="0.1",
    stress_profile_id="SP-1",
    stress_parameters={
        "SP-1": {"rate": 0.01},
        "SP-4": {"baseline_latency_ms": 20.0, "jitter_pct": 50.0, "packet_loss_probability": 0.1},
        "SP-5": {"max_duration_s": 30.0, "trigger_offset_s": 5.0},
    },
    execution_environment={"os": "linux", "runtime": "python"},
    master_seed=123,
    n_runs=10,
    gds_levels=[0.1, 0.2, 0.3],
    isolation_duration_declared=30.0,
    C_total=5,
)
print("Done! Results in report_w3a_sp1/")
