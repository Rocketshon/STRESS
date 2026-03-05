---

# STRESS v0 — Implementation Guide

**Version:** 0.1
**Status:** Informative (Normative-adjacent)
**Applies To:** STRESS v0

---

## 1. Purpose of This Guide

This document defines how to implement the System Threat Resilience & Extreme Stress Suite (STRESS) v0 in a manner that is compliant with the normative specifications.

Its purpose is to translate the STRESS v0 standard into concrete implementation guidance **without reinterpreting, extending, or optimizing the benchmark**. This guide exists to prevent ambiguity, metric drift, and incompatible implementations prior to the development of reference code.

This guide:

* Maps normative requirements to implementation responsibilities
* Defines required interfaces and behaviors
* Clarifies compliance boundaries
* Identifies invalid implementation patterns

This guide does **not**:

* Modify or extend the STRESS v0 specification
* Introduce new metrics, stress parameters, or workloads
* Provide optimization advice or performance tuning guidance
* Define deployment, monitoring, or operational practices

All normative authority remains with:

* **STRESS_v0_Technical_Brief.md**
* **STRESS_v0_Complete_Specification.md**
* **STRESS_v0_Reference_Workloads.md**
* **STRESS_v0_Reference_Stress_Profiles.md**

---

## 2. Conformance Model

### 2.1 What “STRESS v0–Compliant” Means

An implementation is considered **STRESS v0–compliant** if and only if it:

1. Implements all required Behavioral Proxies
   *(Complete Specification §4)*

2. Applies declared stress regimes exactly as specified
   *(Reference Stress Profiles §4–§6)*

3. Executes declared workloads without semantic modification
   *(Reference Workloads §4–§6)*

4. Computes the Orbital Reliability Index (ORI) using the canonical v0 aggregation rules
   *(Complete Specification §5)*

5. Meets all reproducibility and statistical reporting requirements
   *(Complete Specification §5.2, §6)*

Compliance is **binary**, not graded. Partial implementations MUST explicitly declare non-compliance and MUST NOT present results as STRESS v0 scores.

---

### 2.2 Required vs Optional Components

**Required for STRESS v0 compliance:**

* Stress injection capability for SR-1 through SR-5
* A workload execution harness implementing declared workloads
* Measurement and instrumentation sufficient to compute all five Behavioral Proxies
* ORI calculation with canonical weighting and statistical reporting
* Full disclosure of parameters, seeds, and execution environment

**Optional (non-normative):**

* Internal architectural choices
* Choice of programming language or runtime
* Auxiliary visualization or reporting layers external to STRESS results

Optional components MUST NOT influence benchmark behavior, measurement, or reported metrics.

---

### 2.3 Valid and Invalid Deviations

**Valid deviations (MUST be disclosed):**

* Different programming languages or runtimes
* Alternative fault-injection mechanisms that realize the same declared stress effects
* Different statistical methods for confidence interval estimation

**Invalid deviations (non-exhaustive):**

* Adaptive behavior during benchmark execution
* Undeclared parameter changes
* Metric substitution or proxy reinterpretation
* Optimization that alters observed behavior under stress

**Examples of invalid adaptive behavior include:**

* Detecting stress injection and altering execution strategy in response
* Dynamically reallocating resources based on observed proxy values
* Learning from previous benchmark runs to optimize behavior in a current run

Any such behavior invalidates STRESS v0 compliance, even if results appear reproducible.

---

## 3. High-Level System Architecture

STRESS v0 implementations SHOULD be structured around the following logical components. These components describe **responsibilities**, not prescribed software modules or deployment units.

### 3.1 Core Logical Modules

**Stress Injection Layer**
Applies SR-1 through SR-5 according to declared parameters and schedules.

**Workload Harness**
Executes declared workloads and enforces workload constraints.

**Measurement & Instrumentation Layer**
Observes externally visible signals required to compute Behavioral Proxies.

**Metric Computation Engine**
Computes normalized Behavioral Proxy scores (BP-1 through BP-5).

**ORI Aggregation & Statistics Module**
Aggregates proxy scores, applies weights, and computes statistical summaries.

**Reporting & Disclosure Output**
Produces reproducible, inspectable benchmark results and disclosures.

*(Illustrative logical flow; non-prescriptive)*

```
Stress Injection → Workload Execution → Measurement
        ↓                 ↓                ↓
     Faults           Observable        Raw Metrics
                       Signals
                              ↓
                  Proxy Computation (BP-1…BP-5)
                              ↓
                   ORI Aggregation & Statistics
                              ↓
                     Reporting & Disclosure
```

---

### 3.2 Architectural Constraints

* Logical responsibilities MAY be combined or subdivided internally
* Interfaces between responsibilities MUST be preserved
* Stress application MUST be externally imposed relative to workloads
* Measurement MUST be observational rather than intrusive

Implementations that collapse these responsibilities without preserving their logical separation risk invalidating benchmark results.

---

### 3.3 Non-Architectural Assumptions

This guide makes no assumptions about:

* Hardware platforms
* Operating systems
* Orchestration frameworks
* Virtualization or containerization
* Cloud, on-prem, or hybrid environments

STRESS v0 is **environment-parameterized**, not environment-specific.

---

## 4. Stress Injector Implementation

This section defines implementation requirements for applying STRESS v0 stress parameters (SR-1 through SR-5) in a reproducible, externally imposed manner.

Stress injection in STRESS v0 represents **computational pressure abstractions**, not physical simulation. Implementations MUST focus on observable behavioral impact rather than environmental fidelity.

Stress injection MUST NOT:
- alter workload semantics,
- corrupt application payloads directly,
- introduce undeclared coupling between stressors,
- adapt in response to observed workload behavior or proxy values.

All stress behavior MUST be declared, deterministic under replay, and auditable.

---

### 4.1 Stress Regime Declaration

Each benchmark execution MUST declare a stress regime prior to workload execution.

A valid stress regime declaration MUST include:
- Stress Profile ID **or** explicit SR-1…SR-5 parameterization
- Parameter values for each enabled stressor
- Application schedule per stressor (continuous, periodic, stochastic)
- Stress duration and alignment relative to workload execution
- Random seed(s) used for stochastic processes

Stress regime declarations MUST be immutable for the duration of a run.  
Any modification after workload start invalidates the run for STRESS reporting.

Stress regimes MUST be disclosed verbatim alongside all reported ORI results.

---

### 4.2 Determinism and Seed Management

STRESS-compliant stress injection MUST be reproducible.

- Any stochastic stress process MUST use a seeded pseudorandom generator.
- Each independent run MUST use independent seed values.
- All seeds MUST be logged and disclosed.

Implementations MUST ensure that:
- each stressor uses an independent pseudorandom number generator with its own seed,
- random sequences generated for one stressor MUST NOT influence or affect other stressors,
- stress schedules can be replayed deterministically from declared parameters and seed values,
- time references used for scheduling are consistent and documented.

Use of non-deterministic entropy sources (e.g., system time, hardware RNGs) without controlled seeding invalidates STRESS compliance.

---

### 4.3 Temporal Alignment Rules

Stress injection MUST be temporally aligned with workload execution.

- Stress MUST begin no later than workload start unless explicitly declared otherwise.
- Stress MUST remain active for the declared stress window.
- Periodic or stochastic stress schedules MUST be anchored to a declared reference time.

Implementations SHOULD record timestamps sufficient to audit alignment, including:
- run start time,
- workload start and end times,
- stressor activation windows and event times.

#### Stress Window Requirements

- Stress duration MUST be explicitly declared.
- Stress duration MUST be at least as long as workload execution duration.
- Stress MAY extend beyond workload completion if explicitly declared.

If workload duration is variable, stress duration MUST be declared as one of the following:
- **Fixed-duration:** stress runs for a predetermined time and may outlast workload execution.
- **Workload-bound:** stress begins with workload start and ends when workload execution completes.

Failure to declare stress window behavior invalidates reproducibility.

---

### 4.4 Stress Parameter Realization Requirements

This subsection defines implementation-level requirements for each STRESS v0 stress parameter. These requirements specify **what must be achieved**, not how it must be engineered.

---

#### 4.4.1 SR-1 — Radiation Pressure

**Intent:**  
Introduce probabilistic transient computational faults.

**Implementation Requirements:**
- Fault injection MUST be probabilistic and independently distributed unless explicitly declared otherwise.
- Faults MUST be transient and recoverable unless explicitly specified.
- Injection targets MAY include memory units or intermediate computation results.

**Constraints:**
- Faults MUST NOT permanently corrupt system state by design.
- Injection MUST be externally imposed relative to workload logic.
- Correlated fault models MUST be explicitly declared.

---

#### 4.4.2 SR-2 — Thermal Cycling

**Intent:**  
Model periodic environmental stress affecting fault likelihood.

**Implementation Requirements:**
- Thermal cycling MUST modulate fault probability according to a declared periodic function.
- The modulation factor MUST be explicitly declared (e.g., “1.5× baseline fault rate during thermal stress peak”).
- Cycling period MUST be explicitly declared.

**Constraints:**
- Thermal cycling affects fault likelihood only and MUST NOT directly alter execution flow.
- Thermal cycling MUST NOT implicitly depend on other stressors.
- If thermal cycling modulates other stressors (e.g., amplifying SR-1 fault rates), this coupling MUST be explicitly declared in the stress regime.

Thermal cycling acts as a **declared modifier**, not an implicit interaction.

---

#### 4.4.3 SR-3 — Power Disruption

**Intent:**  
Model intermittent or degraded power availability.

**Implementation Requirements:**
- Disruptions MUST be externally imposed.
- Availability percentage and interruption duration MUST be declared.
- Power disruption MUST result in one of the following declared behaviors:
  - **Pause:** execution suspends and resumes after interruption.
  - **Terminate:** execution halts; recovery behavior is workload- and implementation-dependent.

**Constraints:**
- The chosen behavior (pause or terminate) MUST be consistent across all runs.
- If termination behavior is used, recovery attempts MUST be counted toward ARR measurement.
- Power disruption MUST NOT alter workload semantics beyond availability effects.

Power disruption models **availability**, not hardware damage.

---

#### 4.4.4 SR-4 — Network Jitter

**Intent:**  
Degrade communication reliability and coordination.

**Implementation Requirements:**
- Baseline latency, latency variance, and packet loss probability MUST be declared.
- Network effects MAY include:
  - **Delay:** messages delivered with variable latency.
  - **Loss:** individual messages dropped; retransmission behavior is workload-dependent.
  - **Unavailability:** complete network partition for a declared duration.

**Constraints:**
- Payload data MUST NOT be corrupted in transit.
- Network stress affects timing and delivery only, not message content.

This stressor applies only to workloads with communication dependencies.

---

#### 4.4.5 SR-5 — Isolation Duration

**Intent:**  
Enforce complete isolation from external coordination.

**Implementation Requirements:**
- Isolation MUST fully prevent external communication.
- Duration and trigger conditions MUST be explicitly declared.

**Constraints:**
- Isolation MUST be absolute with respect to external inputs.
- Internal system communication MAY continue unless explicitly restricted.

Isolation duration is measured **behaviorally from the workload’s perspective**:
- Isolation begins when external communication becomes unavailable to the workload.
- Isolation ends when external communication is restored or the workload irreversibly fails.
- Administrative indicators (e.g., interface state) are irrelevant if the workload cannot observe or utilize external communication.

---

### 4.5 Multi-Stressor Interaction Rules

- Multiple stressors MAY be active concurrently.
- Stressors MUST NOT implicitly depend on one another.
- Any coupling between stressors MUST be explicitly declared in the stress regime.

Undeclared interaction effects invalidate comparability.

---

### 4.6 Invalid Stress Injection Patterns

The following patterns invalidate STRESS v0 compliance:
- adaptive stress intensity based on observed workload behavior,
- stress schedules that change mid-run without declaration,
- injection mechanisms that introspect workload internals,
- stress applied conditionally on proxy values.

Stress injection represents **environmental pressure, not intelligent opposition**.  
Stressors MUST NOT observe, infer, or respond to workload behavior.

---

## 5. Workload Execution and Measurement

This section defines how STRESS v0 workloads MUST be executed and how measurements MUST be collected in order to compute Behavioral Proxies accurately and comparably.

Workload execution and measurement are strictly **observational**. Implementations MUST NOT alter workload behavior for the purpose of measurement, nor introduce instrumentation that materially affects workload execution.

---

### 5.1 Workload Integrity Requirements

Declared workloads (W1, W2, W3) MUST be executed without semantic modification.

- Workload logic MUST NOT be altered to improve resilience under stress.
- Error handling, retries, or fallback behavior MUST be intrinsic to the workload definition.
- Benchmark harnesses MUST NOT inject compensating behavior on behalf of the workload.

Any modification to workload semantics invalidates comparability and STRESS v0 compliance.

---

### 5.2 Execution Control and Lifecycle

Each workload execution MUST clearly define:
- workload start condition,
- workload completion condition,
- workload failure condition.

Workloads MUST be executed:
- under the declared stress regime,
- for the declared stress window,
- without premature termination unless:
  - caused by stress effects (e.g., power disruption, unrecoverable fault), or
  - caused by workload completion or failure conditions as defined in the workload specification.

Benchmark harnesses MUST NOT terminate workloads for measurement convenience.

Workloads MAY terminate early due to irrecoverable failure. Such termination MUST be recorded and reported.

---

### 5.3 Measurement Scope and Observability

Measurement MUST be limited to **externally observable signals**. Instrumentation MUST NOT:
- introspect internal workload state beyond the workload’s public interface,
- intercept or modify workload control flow,
- adapt measurement behavior based on observed outcomes.

Examples of valid observable signals include:
- exit codes or return values,
- log messages or error outputs,
- task completion events (e.g., files created, messages sent),
- exposed metrics endpoints (e.g., HTTP `/metrics`),
- resource utilization obtained via OS-level accounting.

Examples of invalid measurement include:
- reading workload process memory directly,
- instrumenting internal function calls not exposed by the workload,
- inferring state from non-public data structures.

Measurement MUST reflect what the workload exposes, not what the benchmark infers.

---

### 5.4 Measurement Timing and Granularity

Measurements MUST be time-aligned with:
- workload execution,
- stress application,
- recovery attempts.

Implementations MUST define:
- measurement sampling frequency,
- event aggregation windows,
- timestamp resolution.

Sampling frequency MUST be sufficient to capture:
- degradation onset,
- recovery events,
- cascading failure behavior.

Minimum guidance:
- **Event-driven sampling:** capture all task completions, failures, and recovery attempts.
- **Periodic sampling:** at least 10 samples per stress cycle period.
- **Resource metrics:** at least once per second for CPU and memory measurements.

Implementations MUST declare their sampling strategy alongside reported results.

---

### 5.5 Failure Classification

Failures observed during workload execution MUST be classified as one of the following:

- **Autonomously recovered failure:**  
  A fault that the workload detects and recovers from without external intervention  
  *(counts toward ARR numerator)*.

- **Recoverable but not recovered failure:**  
  A fault that is theoretically recoverable but requires external restart or intervention  
  *(counts toward ARR denominator but not numerator)*.

- **Irreversible failure:**  
  A fault that causes permanent state corruption or violates workload safety properties  
  *(triggers IST measurement)*.

Classification rules MUST align with:
- Autonomous Recovery Rate (ARR) — Complete Specification §4.2
- Isolation Survival Time (IST) — Complete Specification §4.3

**Relationship to stress parameters:**
- Faults injected via SR-1 are designed to be recoverable in principle.
- Whether such faults are autonomously recovered or not depends on workload resilience, not fault type.

---

### 5.6 Recovery Observation Rules

Recovery behavior MUST be observed, not assisted.

- Implementations MUST NOT restart workloads from the benchmark harness.
- Restart or recovery logic MUST reside entirely within workload code.
- External orchestration systems (e.g., Kubernetes controllers, systemd) MUST NOT intervene during benchmark execution.
- Recovery attempts count toward ARR only if initiated by workload-internal logic.

If a workload includes restart behavior, this MUST be disclosed in the workload specification.

---

### 5.7 Resource Utilization Measurement

Resource utilization metrics MAY be collected to support computation of:
- Resource Efficiency under Constraint (REC).

Measured resources MAY include:
- CPU usage,
- memory consumption,
- storage I/O,
- network utilization.

Resource measurement MUST:
- be non-intrusive (measurement overhead MUST NOT measurably alter workload timing or behavior),
- be consistently applied across runs,
- reflect actual resource consumption under stress.

Permitted measurement techniques include:
- OS-level process accounting,
- hardware performance monitoring units (PMUs),
- container or cgroup resource metrics.

Techniques that alter workload execution (e.g., profilers that pause execution) are NOT permitted.

---

### 5.8 Distributed Workload Coordination (W3)

For distributed workloads:
- node roles MUST be declared prior to execution,
- coordination mechanisms MUST remain unchanged under stress,
- component failures MUST be recorded explicitly.

Failure classification for distributed workloads:
- **Partial failure:** one or more components failed, but fewer than the total component count.
- **Complete failure:** all components failed or a system-wide invariant was violated.

Measurement MUST capture:
- coordination success or failure per attempt,
- synchronization delays,
- which specific components failed (for CFR computation).

Measurement MUST NOT assume global state visibility.

---

### 5.9 Invalid Measurement Patterns

The following patterns invalidate STRESS v0 compliance:
- modifying workloads to expose additional measurement hooks,
- suppressing error signals for measurement convenience,
- inferring internal state not observable to the workload,
- altering execution timing to simplify measurement.

Measurement exists to **observe behavior**, not to modify or filter it.

---

## 6. Metric Calculation and ORI Computation

This section defines how Behavioral Proxies (BP-1 through BP-5) MUST be computed and how they are aggregated into the Orbital Reliability Index (ORI), in strict accordance with the STRESS v0 Complete Specification.

Metric computation MUST be:
- deterministic given declared inputs,
- derived solely from observed workload behavior,
- reproducible across independent implementations,
- auditable after execution.

Metric definitions in this section are **interpretive bindings** to the normative formulas defined in the Complete Specification. No alternate formulations are permitted for STRESS v0 compliance.

---

### 6.1 General Metric Computation Rules

All Behavioral Proxies MUST:
- be normalized to the closed interval [0,1],
- be computed from measurements collected during a single benchmark run,
- be derived only from measurements defined in Section 5.

**Run Definition:**
- A *run* is a complete execution of a workload under a declared stress regime.
- Some proxies (e.g., BP-1) require multiple stress intensity levels within a single run.
- Each run produces exactly one value for each proxy (BP-1 through BP-5).

Multiple independent runs are required for statistical aggregation (see §6.8).

Metric computation MUST NOT:
- depend on future knowledge,
- adapt thresholds or baselines dynamically,
- condition on partial results from other runs.

---

### 6.2 BP-1 — Graceful Degradation Score (GDS)

**Intent:**  
Measure how system functionality degrades as stress intensity increases.

**Computation Requirements:**
1. Execute the workload at ordered stress intensity levels  
   \( s_1, s_2, \dots, s_n \), declared in the stress profile.
2. At each stress level \( s_i \), measure task completion rate  
   \( C_i \in [0,1] \).
3. Stress levels MUST be monotonically ordered by declared intensity.

**Formula:**
```

GDS = (1 / n) × Σᵢ₌₁ⁿ Cᵢ

```

**Normalization Rule:**
- GDS = 1.0 if all tasks complete at all stress levels.
- GDS = 0.0 if no tasks complete at any stress level.
- Intermediate values reflect gradual degradation.

**Edge Cases:**
- If n = 1, GDS = C₁.
- Stress intensity levels MUST be explicitly declared.

---

### 6.3 BP-2 — Autonomous Recovery Rate (ARR)

**Intent:**  
Measure the workload’s ability to autonomously recover from recoverable faults.

**Computation Requirements:**
- Let \( F_r \) be the number of recoverable faults observed.
- Let \( F_a \) be the number of those faults resolved autonomously by workload-internal logic.

**Formula:**
```

ARR = Fₐ / Fᵣ

```

**Edge Cases:**
- If \( F_r = 0 \), ARR is undefined for that run.
  - ARR MUST be reported as **N/A**.
  - The condition MUST be explicitly disclosed.
  - Runs with undefined ARR MUST NOT be silently coerced to numeric values.

**Rationale:**  
ARR measures recovery capability *when recovery is required*. If no recoverable faults occur, the metric is not applicable.

---

### 6.4 BP-3 — Isolation Survival Time (IST)

**Intent:**  
Measure how long a workload continues to function during enforced isolation.

**Computation Requirements:**
- Record the duration from isolation onset to irreversible workload failure.
- If the workload completes successfully while isolated, survival time equals isolation duration.

**Formula:**
```

IST = (Observed survival time) / (Declared isolation duration)

```

**Normalization Rule:**
- IST = 1.0 indicates full survival for the entire isolation window.
- IST < 1.0 indicates failure prior to isolation end.
- IST MUST be capped at 1.0.

---

### 6.5 BP-4 — Resource Efficiency Under Constraint (REC)

**Intent:**  
Measure useful work per unit resource under stress relative to baseline operation.

**Computation Requirements:**
1. Measure baseline efficiency:  
   \( E_{base} = \frac{Work}{Resources} \) under SP-0.
2. Measure stressed efficiency:  
   \( E_{stress} = \frac{Work}{Resources} \) under stress.

**Formula:**
```

REC = min(E_stress / E_base, 1.0)

```

**Normalization Rule:**
- REC = 1.0 if stressed efficiency equals or exceeds baseline.
- REC < 1.0 if stressed efficiency is worse than baseline.
- REC is capped at 1.0 (no credit for exceeding baseline efficiency).

**Validity Constraints:**
- REC is valid only if baseline task completion exceeds a declared minimum threshold.
- If baseline completion is insufficient, REC MUST be reported as **N/A**.

---

### 6.6 BP-5 — Cascading Failure Resistance (CFR)

**Intent:**  
Measure the degree to which localized failures remain contained.

**Computation Requirements:**
1. Inject a localized fault into a single component.
2. Measure:
   - \( C_{local} \): number of components affected (including the initial component),
   - \( C_{total} \): total number of components in the system.

**Formula:**
```

CFR = 1 - (C_local / C_total)

```

**Normalization Rule:**
- CFR = 1.0 if only the initially failed component is affected.
- CFR = 0.0 if all components are affected.
- Intermediate values reflect partial propagation.

**Edge Cases:**
- For single-component workloads, CFR MUST be reported as **N/A**.
- Component boundaries MUST be declared in the workload specification.

---

### 6.7 ORI Aggregation

The Orbital Reliability Index (ORI) is computed as a weighted aggregate of the five Behavioral Proxies.

**Canonical STRESS v0 weighting:**
- Equal weights for all proxies.

**Formula:**
```

ORI = (GDS + ARR + IST + REC + CFR) / 5

```

**Alternate Weightings:**
- Alternate weighting schemes MAY be explored for research purposes.
- Alternate-weighted scores MUST NOT be labeled as “STRESS v0 ORI”.
- Canonical equal-weighted ORI MUST always be computed and reported for STRESS v0 compliance.

---

### 6.8 Statistical Aggregation and Reporting

Each benchmark configuration MUST include:
- at least 10 independent runs,
- each run using an independently seeded stress realization (see §4.2).

For each proxy and for ORI, implementations MUST report:
- mean value,
- standard deviation,
- 95% confidence interval.

Statistical aggregation MUST occur **after** per-run proxy computation.
No run may be excluded without explicit disclosure and justification.

---

### 6.9 Invalid Metric Practices

The following practices invalidate STRESS v0 compliance:
- redefining proxy formulas,
- smoothing or filtering metrics to improve appearance,
- discarding outlier runs without disclosure,
- dynamically adjusting thresholds or baselines.

Metrics exist to **represent behavior**, not to optimize perception.

---

## 7. Reporting, Disclosure, and Reproducibility

This section defines the mandatory reporting artifacts and disclosure requirements for STRESS v0 results.

STRESS v0 results are only valid if they are:
- reproducible by an independent party,
- auditable after execution,
- fully parameterized and disclosed.

Any result that cannot be independently reconstructed from its report MUST NOT be presented as an STRESS v0 score.

---

### 7.1 Required Output Artifacts

Each STRESS v0 benchmark execution MUST produce the following artifacts:

1. **Run Manifest**
2. **Per-Run Metric Record(s)**
3. **Aggregated Results Summary**
4. **Disclosure Statement**

Artifacts MAY be combined into a single file or directory, but all required fields MUST be present and clearly identifiable.

At least one artifact MUST be machine-readable (JSON or YAML) and MUST include all required fields.

---

### 7.2 Run Manifest

The Run Manifest captures the immutable configuration of a benchmark execution.

Each Run Manifest MUST include:

**Benchmark Identification**
- STRESS version (e.g., v0)
- Complete Specification version
- Implementation Guide version
- Date/time of execution (UTC)

**Implementation Provenance (Strongly Recommended)**
- Repository identifier (URL or path)
- Commit hash or immutable revision identifier
- Build/runtime identifiers (if applicable)

**Workload Declaration**
- Workload ID (W1, W2, or W3)
- Workload version
- Declared workload parameters
- Component count and roles (if applicable)
- Declared component boundary definition level (process/service/node) for CFR validity

**Stress Regime Declaration**
- Stress Profile ID OR explicit SR-1…SR-5 parameterization
- All stress parameter values
- Stress schedules and durations
- Stress window behavior (fixed-duration or workload-bound)
- Declared stress intensity levels s₁…sₙ if BP-1 (GDS) uses multiple intensity levels within a run

**Determinism Controls**
- Random seed values for each stressor
- Seed derivation method (if applicable)

**Execution Environment (Descriptive, Not Prescriptive)**
- Hardware description (CPU, memory, accelerators if used)
- Operating system and version
- Runtime environment (language, VM, container runtime)
- Orchestration framework, if any (must be stated even if “none”)

Environment descriptions MUST be factual and MUST NOT imply normalization or endorsement.

---

### 7.3 Per-Run Metric Record

For each independent run, implementations MUST record:

**Run Identity and Timing**
- Run identifier
- Start and end timestamps
- Stress realization seed(s)

**Observed Events**
- Observed failure events and classification outcomes
- Observed recovery attempts and outcomes
- For distributed workloads: component failures observed (which components, when)

**BP-1 (GDS) Evidence**
- Ordered stress intensity levels s₁…sₙ used in the run
- Completion rates Cᵢ ∈ [0,1] observed at each sᵢ
- Computed GDS value

**BP-2 (ARR) Evidence**
- Fᵣ (recoverable faults observed)
- Fₐ (faults autonomously recovered)
- Computed ARR value, or ARR = N/A if Fᵣ = 0 (must state reason)

**BP-3 (IST) Evidence**
- Declared isolation duration
- Observed survival time
- Computed IST value

**BP-4 (REC) Evidence**
- E_base and E_stress (or underlying work/resources sufficient to derive them)
- Baseline completion validity threshold used
- Computed REC value, or REC = N/A if baseline validity constraint not met (must state reason)

**BP-5 (CFR) Evidence**
- C_total (total components)
- C_local (affected components)
- Computed CFR value, or CFR = N/A if single-component workload (must state reason)

**ORI**
- ORI MUST be computed per run only if all five proxies are defined for that run.
- If any proxy is N/A for a run, ORI for that run MUST be reported as N/A with the cause.

Runs MUST NOT be discarded without disclosure.

---

### 7.4 Aggregated Results Summary

For each benchmark configuration, implementations MUST report:

For each Behavioral Proxy and for ORI:
- mean value across runs where the metric is defined,
- standard deviation,
- 95% confidence interval,
- number of runs included (N) and number of runs excluded as N/A (if any).

Aggregation MUST occur **after** per-run proxy computation.

For ORI:
- ORI aggregation MUST include only runs where all five proxies are defined.
- The report MUST state the number of qualifying runs.

If any runs are excluded for any reason:
- the exclusion MUST be explicitly stated,
- the justification MUST be provided.

---

### 7.5 Disclosure Statement

Each STRESS v0 report MUST include a disclosure statement containing:

- Confirmation that the implementation follows STRESS v0 normative specifications
- Declaration of any implementation-defined behaviors
- Declaration of any proxies reported as N/A and why
- Confirmation that no adaptive behavior occurred during execution
- Confirmation that no stress parameters were modified mid-run
- Confirmation that no runs were excluded without disclosure

Disclosure statements MUST be explicit. Silence is not acceptable.

---

### 7.6 Reproducibility Requirements

A reported STRESS v0 result MUST be reproducible by an independent party given:

- The Run Manifest
- The workload specification and parameters
- The stress regime declaration (including stress intensity levels where applicable)
- The random seeds
- The reported measurement methodology
- The per-run metric records (including raw components required to compute proxies)

Implementations MUST NOT rely on:
- undocumented defaults,
- hidden configuration files,
- environment-specific heuristics.

If reproduction requires proprietary components, this MUST be disclosed.

---

### 7.7 Invalid Reporting Patterns

The following invalidate STRESS v0 compliance:

- Reporting ORI without per-proxy values and supporting per-run records
- Reporting aggregated results without per-run metric records
- Omitting seeds, stress parameters, or stress intensity levels (when applicable)
- Renaming or reinterpreting Behavioral Proxies
- Presenting experimental metrics as STRESS v0 scores
- Selective reporting of favorable runs
- Computing ORI from runs where any proxy is N/A without explicit disclosure

Results that violate these constraints MUST NOT be labeled as STRESS v0.

---

### 7.8 Reference Report Structure (Non-Normative)

A typical STRESS v0 report MAY be structured as:

/report
├── manifest.yaml
├── runs/
│ ├── run_01.json
│ ├── run_02.json
│ └── ...
├── aggregate_summary.json
└── disclosure.md

This structure is illustrative only and not required.

