"""Example: Run W1-A workload under SP-1 moderate stress."""
from stress.runner import run_benchmark

run_benchmark(
    out_dir="report_w1a_sp1",
    workload_id="W1-A",
    workload_version="0.1",
    stress_profile_id="SP-1",
    stress_parameters={"SP-1": {"rate": 0.001}},
    execution_environment={"os": "linux", "runtime": "python"},
    master_seed=42,
    n_runs=10,
    gds_levels=[0.1, 0.2, 0.3],
    isolation_duration_declared=60.0,
    C_total=5,
)
print("Done! Results in report_w1a_sp1/")
