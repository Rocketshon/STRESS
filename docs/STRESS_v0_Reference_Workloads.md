# System Threat Resilience & Extreme Stress Suite (STRESS) v0
## Reference Workloads

**Version:** 0.2  
**Status:** Normative Specification  
**Related Documents:**
- STRESS_v0_Technical_Brief.md
- STRESS_v0_Complete_Specification.md

---

## 1. Purpose and Normative Status

This document defines normative reference workload classes and canonical workloads for STRESS v0.

STRESS results are invalid unless workloads are explicitly defined in accordance with this specification. This document is normative for STRESS v0 workload definition and execution.

Reference workloads provide:
- A standardized basis for comparative evaluation
- Consistent interpretation of Behavioral Proxies
- Reproducibility across implementations and environments

---

## 2. Workload Design Principles

All STRESS reference workloads MUST satisfy the following:

1. **Deterministic Baseline Behavior**  
   Under baseline (unstressed) conditions, workloads MUST complete correctly and reproducibly.

2. **Stress Sensitivity**  
   Workloads MUST exhibit measurable behavioral change under injected stress.

3. **Observability**  
   Completion, degradation, and failure MUST be observable via external signals.

4. **Implementation Neutrality**  
   Workloads MUST NOT assume specific hardware, operating systems, orchestration frameworks, or proprietary runtimes.

---

## 3. Workload Declaration Requirements

Each STRESS workload execution MUST include an explicit workload declaration containing:
- Workload ID and class
- Input size and distribution
- Concurrency level
- Resource limits (CPU, memory, bandwidth)
- Execution duration or completion criteria
- Failure classification rules (recoverable vs irreversible)

Failure classification MUST conform to STRESS_v0_Complete_Specification §4.2.

---

## 4. Workload Classes (STRESS v0)

STRESS v0 defines three normative workload classes. Results MUST NOT be compared across classes.

### 4.1 Class W1 — Stateless Task Processing

**Description**  
Independent, stateless tasks with no shared mutable state.

**Examples**
- Batch computation over independent inputs
- Map-style numerical transforms

**Baseline Correctness Criteria**
- ≥ 99% task completion
- Deterministic output verification

**Behavioral Proxy Coverage**
- GDS: throughput degradation under stress
- ARR: recovery from transient execution faults
- REC: efficiency loss under constraint
- CFR: expected near-ideal containment

### 4.2 Class W2 — Stateful Pipeline Processing

**Description**  
Multi-stage workloads maintaining state across execution stages.

**Examples**
- Ingest → transform → aggregate pipelines
- Stream processing with checkpoints

**Baseline Correctness Criteria**
- ≥ 99% stage completion
- Checkpoint integrity preserved
- Deterministic stage ordering

**Behavioral Proxy Coverage**
- GDS: pipeline throughput degradation
- ARR: recovery from mid-pipeline faults
- IST: state survival during isolation
- CFR: failure propagation across stages

### 4.3 Class W3 — Distributed Coordination Workload

**Description**  
Multiple cooperating components requiring coordination to achieve progress.

**Constraints**
- Non-byzantine failure model
- Fixed participant count (3–7 components)
- Single coordination primitive per run

**Examples**
- Leader election
- Barrier synchronization
- Distributed lock acquisition

**Baseline Correctness Criteria**
- Safety violations = 0
- Liveness achieved within declared time bound

**Behavioral Proxy Coverage**
- GDS: coordination success rate under stress
- ARR: recovery from partial participant failure
- IST: survivability during isolation
- CFR: containment of participant failure

---

## 5. Canonical STRESS v0 Workloads

STRESS v0 defines the following canonical workloads:

| ID   | Class | Description |
|------|-------|-------------|
| W1-A | W1    | Stateless batch computation over fixed-size inputs with deterministic verification |
| W2-A | W2    | Three-stage pipeline with checkpoint after stage two |
| W3-A | W3    | Leader election with heartbeat and timeout parameters |

**Mandatory Requirement**  
Implementations claiming STRESS v0 compliance MUST support W1-A.

Cross-implementation comparisons require identical workload IDs and parameters.

---

## 6. Measurement Mapping

Workloads MUST expose observable signals sufficient to measure:
- Task or stage completion rate (GDS)
- Autonomous recovery events (ARR)
- Time-to-failure during isolation (IST)
- Work-per-resource metrics (REC)
- Failure propagation boundaries (CFR)

Observable signals SHOULD be derivable from external interfaces (e.g., exit codes, logs, counters, timestamps) without privileged internal instrumentation.

---

## 7. Extension Rules
- New workload classes require a major version increment.
- New workloads within existing classes MAY be added in minor versions.
- Canonical workload definitions are immutable once versioned.

---

## 8. Interpretation Constraints
- STRESS scores MUST NOT be compared across different workload classes.
- Workload ID and parameters MUST be disclosed alongside SRI results.
- Optimizing systems specifically for a workload MUST be disclosed.

---

## 9. Summary

Reference workloads ground STRESS’s behavioral metrics in observable execution behavior.

They ensure STRESS evaluates resilience under constraint rather than abstract capability, and that results remain reproducible, interpretable, and comparable across implementations.

---

_End of Reference Workloads_
