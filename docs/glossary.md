# STRESS Glossary

| Term | Definition |
|------|-----------|
| **STRESS** | System Threat Resilience & Extreme Stress Suite |
| **SRI** | Stress Resilience Index — composite score [0, 100] from 5 behavioral proxies |
| **BP** | Behavioral Proxy — one of five measurable resilience dimensions |
| **GDS** | Graceful Degradation Score (BP-1) — average completion rate across stress levels |
| **ARR** | Autonomous Recovery Rate (BP-2) — fraction of recoverable faults resolved without intervention |
| **IST** | Isolation Survival Time (BP-3) — workload endurance during complete isolation |
| **REC** | Resource Efficiency Under Constraint (BP-4) — work-per-resource ratio under stress vs baseline |
| **CFR** | Cascading Failure Resistance (BP-5) — containment of failures to initially-affected components |
| **SP-0** | Baseline stress profile — no stress applied |
| **SP-1** | Moderate stress profile |
| **SP-2** | Severe stress profile |
| **SP-1 (stressor)** | Radiation Pressure — probabilistic bit-flip / transient fault injection |
| **SP-2 (stressor)** | Thermal Cycling — periodic stress modulation affecting fault rates |
| **SP-3** | Power Disruption — intermittent availability windows |
| **SP-4** | Network Jitter — latency variance + packet loss simulation |
| **SP-5** | Isolation Duration — complete external disconnection |
| **W1-A** | Stateless independent task processing workload |
| **W2-A** | Stateful multi-stage pipeline with checkpointing |
| **W3-A** | Distributed coordination (leader election) workload |
| **Event** | Canonical observational record emitted during workload execution |
| **EventLog** | Ordered collection of events from a single run |
| **N/A** | Metric value is undefined due to insufficient evidence |
| **StressRegime** | Composite of all five stressors with unified query interface |
