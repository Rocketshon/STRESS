# STRESS — System Threat Resilience & Extreme Stress Suite (v0.2)

STRESS is a reliability benchmarking framework designed to evaluate how computational workloads behave when foundational operating assumptions are violated by environmental and systemic constraints. Unlike terrestrial benchmarks — which typically assume continuous power, stable connectivity, and rare environmental disruption — STRESS focuses on resilience and behavioral stability under persistent stress, rather than performance optimization, throughput, or cost efficiency.

## Status
- Specification: Frozen (v0.2)
- Reference Implementation: Rust (`stress-ref/`) + Python (`stress/`)
- Compliance: Binary

## Full Specification

- **[STRESS v0.2 Specification](./docs/specification-v0.2.md)** — Complete technical specification
- **[Implementation Guide](./STRESS_v0_Implementation_Guide.md)** — Implementation details
- **[Complete Specification](./docs/STRESS_v0_Complete_Specification.md)** — Extended technical document
- **[Reference Workloads](./docs/STRESS_v0_Reference_Workloads.md)** — W1-A, W2-A, W3-A definitions
- **[Stress Profiles](./docs/STRESS_v0_Reference_Stress_Profiles.md)** — SP-0 through SP-5 definitions
- **[Glossary](./docs/glossary.md)** — Term definitions

## Repository Structure

| Path | Description |
|------|-------------|
| `docs/` | Normative specification, workload definitions, stress profiles, glossary |
| `stress-ref/` | **Rust reference implementation** (canonical) |
| `stress/` | Python reference implementation |
| `examples/` | Usage examples |
| `tests/` | Python test suite |

## What This Repo Is NOT
- Not a performance benchmark
- Not an optimization framework
- Not adaptive or learning-based

## Running a Benchmark

### Rust (recommended)

```bash
cd stress-ref
cargo run -- --workload W1-A --profile SP-1 --seed 42 --runs 10 \
  --gds-levels 0.1,0.2,0.3 --isolation-duration 60.0 --c-total 5
```

### Python

```python
from stress.runner import run_benchmark

run_benchmark(
    out_dir="report",
    workload_id="W1-A",
    workload_version="0.1",
    stress_profile_id="SP-1",
    stress_parameters={"SP-1": {"rate": 0.001}},
    execution_environment={"os": "linux", "runtime": "python"},
    master_seed=123,
    n_runs=10,
    gds_levels=[0.1, 0.2, 0.3],
    isolation_duration_declared=120.0,
    C_total=5,
)
```

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v0.2 | 2026-03 | STRESS — Current specification with SRI [0,100] scale |
| v0.1 | (Archived) | OCRB — Original specification with ORI [0,1] scale |

## Migration from OCRB v0.1

STRESS v0.2 supersedes OCRB (Orbital Compute Readiness Benchmark) v0.1.

| OCRB v0.1 | STRESS v0.2 | Conversion |
|-----------|-------------|------------|
| ORI [0, 1] | SRI [0, 100] | `SRI = ORI * 100` |
| 0.85 threshold | 85 threshold | Direct mapping |
| Stress Regimes | Stress Profiles | Renamed |
| SR-1 to SR-5 | SP-1 to SP-5 | Renamed |

### Archives

- [OCRB v0.1 Specification (Deprecated)](./docs/historical/ocrb-v0.1-deprecated.md) — Original specification preserved for reference

---

*Maintained by Obelus Labs, LLC*
