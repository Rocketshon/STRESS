from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict, List, Optional, Tuple

from STRESS.config import create_manifest
from STRESS.measure.events import EventLog, EventType, FailureClass
from STRESS.workloads.w1_stateless import run_w1a
from STRESS.workloads.w2_stateful_pipeline import run_w2a, W2AConfig
from pathlib import Path
from STRESS.metrics.arr import compute_arr
from STRESS.metrics.cfr import compute_cfr
from STRESS.metrics.gds import compute_gds
from STRESS.metrics.ist import compute_ist
from STRESS.metrics.rec import compute_rec
from stress.metrics.sri import compute_sri

from STRESS.report.schema import (
    RunRecord,
    ProxyEvidence,
    ProxyValues,
    AggregateStats,
    AggregateSummary,
)
from STRESS.report.writer import (
    write_manifest,
    write_run_record,
    write_aggregate_summary,
    write_disclosure,
)
from STRESS.stats.aggregate import summarize


def run_benchmark(
    *,
    out_dir: str,
    workload_id: str,
    workload_version: str,
    stress_profile_id: str,
    stress_parameters: Dict[str, Any],
    execution_environment: Dict[str, Any],
    master_seed: int,
    n_runs: int = 10,
    # inputs needed for some metrics (declared, not guessed)
    gds_levels: Optional[List[float]] = None,
    isolation_duration_declared: Optional[float] = None,
    C_total: Optional[int] = None,
) -> None:
    """
    Reference runner: generates manifest, executes N runs (placeholder workload),
    computes proxies from events/evidence, writes per-run + aggregate reports.

    NOTE: Workload execution is a stub right now. This runner is meant to be
    integrated with actual workloads later. The point is the reporting + math pipeline.
    """

    manifest = create_manifest(
        workload_id=workload_id,
        workload_version=workload_version,
        stress_profile_id=stress_profile_id,
        stress_parameters=stress_parameters,
        execution_environment=execution_environment,
        master_seed=master_seed,
    )
    write_manifest(out_dir, manifest)

    run_records: List[RunRecord] = []

    # Proxy series for aggregation
    gds_series: List[Optional[float]] = []
    arr_series: List[Optional[float]] = []
    ist_series: List[Optional[float]] = []
    rec_series: List[Optional[float]] = []
    cfr_series: List[Optional[float]] = []
    sri_series: List[Optional[float]] = []

    # For REC, we need a baseline record. For now we generate a stub baseline.
    # Later: baseline runs should be actual SP-0 executions.
    baseline_log = _stub_baseline_events(workload_id)

    # External dependency switch (runner-owned; stress layer will control this later)
    external_available = True

    def external_call():
        if not external_available:
            raise RuntimeError("isolated")
        return None

    def should_crash(seed: int, stage: int) -> bool:
        crash_stages = {(seed % 37) % 50, (seed % 53) % 50}
        return stage in crash_stages

    for i in range(1, n_runs + 1):
        # Use real W1-A workload when requested, otherwise fall back to stub
        if workload_id == "W1-A":
            run_seed = manifest.seeds.sr1 + i
            log = EventLog(run_id=f"run-{i:02d}", workload_id=workload_id)
            log.emit(EventType.RUN_START, t_utc=1000.0)

            # Real execution
            res = run_w1a(tasks=100, work_units_per_task=2000, seed=run_seed)
            completion_rate = res.tasks_completed / res.tasks_total if res.tasks_total else 0.0

            # For GDS: emit one completion observation per stress level
            if gds_levels:
                for s in gds_levels:
                    log.emit(EventType.WORK_UNIT_END, stress_level=s, completion_rate=completion_rate)

            # For REC: log work and resources (resources_used is a placeholder)
            log.emit(EventType.WORK_UNIT_END, work_done=res.work_done, resources_used=res.duration_s)

            # Note: do not emit ARR/IST/CFR evidence here for W1-A —
            # these proxies are not meaningfully exercised by SP-0 W1-A.

            log.emit(EventType.RUN_END, t_utc=1080.0)
        elif workload_id == "W2-A":
            run_index = i
            run_seed = manifest.seeds.sr2 + i
            log = EventLog(run_id=f"run-{i:02d}", workload_id=workload_id)
            log.emit(EventType.RUN_START, t_utc=1000.0)

            run_dir = str(Path(out_dir) / "w2_state" / f"run_{run_index:02d}")

            iso_start = 1010.0
            iso_end = iso_start + float(isolation_duration_declared) if isolation_duration_declared else iso_start

            if "SR-5" in stress_parameters:
                log.emit(EventType.ISOLATION_START, t_utc=iso_start)
                external_available = False
            else:
                external_available = True

            cfg = W2AConfig()

            res = run_w2a(
                run_dir=run_dir,
                seed=run_seed,
                cfg=cfg,
                external_call=external_call,
                should_crash=should_crash,
            )

            if "SR-5" in stress_parameters:
                external_available = True
                log.emit(EventType.ISOLATION_END, t_utc=iso_end)

            completion_rate = res.stages_completed / res.stages_total if res.stages_total else 0.0
            if gds_levels:
                for s in gds_levels:
                    log.emit(EventType.WORK_UNIT_END, stress_level=s, completion_rate=completion_rate)

            for j in range(res.restarts):
                log.emit(EventType.FAILURE, failure_id=f"crash_{j}", failure_class=FailureClass.AUTONOMOUSLY_RECOVERED)

            if res.failed:
                log.emit(EventType.FAILURE, failure_id="terminal", failure_class=FailureClass.RECOVERABLE_NOT_RECOVERED)

            log.emit(EventType.WORK_UNIT_END, work_done=res.stages_completed, resources_used=res.duration_s)

        else:
            log = _stub_workload_events(run_id=f"run-{i:02d}", workload_id=workload_id)

        # Compute proxies
        gds = compute_gds(log.events, expected_levels=gds_levels) if gds_levels else compute_gds(log.events)
        arr = compute_arr(log.events)
        ist = compute_ist(log.events, isolation_duration_declared=isolation_duration_declared)
        rec = compute_rec(baseline_log.events, log.events)
        cfr = compute_cfr(log.events, C_total=C_total)

        proxies = {
            "gds": gds.gds,
            "arr": arr.arr,
            "ist": ist.ist,
            "rec": rec.rec,
            "cfr": cfr.cfr,
        }
        sri = compute_sri(proxies)

        # Collect N/A reasons
        na_reasons: Dict[str, str] = {}
        if gds.na_reason: na_reasons["gds"] = gds.na_reason
        if arr.na_reason: na_reasons["arr"] = arr.na_reason
        if ist.na_reason: na_reasons["ist"] = ist.na_reason
        if rec.na_reason: na_reasons["rec"] = rec.na_reason
        if cfr.na_reason: na_reasons["cfr"] = cfr.na_reason
        if sri.na_reason: na_reasons["sri"] = sri.na_reason

        record = RunRecord(
            run_id=log.run_id,
            workload_id=workload_id,
            seeds=asdict(manifest.seeds),
            start_utc=log.events[0].t_utc,
            end_utc=log.events[-1].t_utc,
            proxies=ProxyValues(
                gds=gds.gds,
                arr=arr.arr,
                ist=ist.ist,
                rec=rec.rec,
                cfr=cfr.cfr,
                sri=sri.sri,
            ),
            evidence=ProxyEvidence(
                stress_levels=gds.stress_levels,
                completion_rates=gds.completion_rates,
                Fr=arr.Fr,
                Fa=arr.Fa,
                isolation_duration=isolation_duration_declared,
                survival_time=ist.survival_time_observed,
                E_base=rec.E_base,
                E_stress=rec.E_stress,
                baseline_completion_ok=None,
                C_total=C_total,
                C_local=cfr.C_local,
            ),
            na_reasons=na_reasons,
            events=log.to_dicts(),
        )
        run_records.append(record)
        write_run_record(out_dir, i, record)

        # Series
        gds_series.append(gds.gds)
        arr_series.append(arr.arr)
        ist_series.append(ist.ist)
        rec_series.append(rec.rec)
        cfr_series.append(cfr.cfr)
        sri_series.append(sri.sri)

    # Aggregate summaries
    def _agg(vals: List[Optional[float]]) -> AggregateStats:
        s = summarize(vals)
        return AggregateStats(
            mean=s.mean, std=s.std,
            ci95_low=s.ci95_low, ci95_high=s.ci95_high,
            n_included=s.n_included, n_na=s.n_na
        )

    summary = AggregateSummary(
        gds=_agg(gds_series),
        arr=_agg(arr_series),
        ist=_agg(ist_series),
        rec=_agg(rec_series),
        cfr=_agg(cfr_series),
        sri=_agg(sri_series),
    )
    write_aggregate_summary(out_dir, summary)

    write_disclosure(out_dir, _default_disclosure_text())


def _default_disclosure_text() -> str:
    return """# STRESS v0 Disclosure

This report was generated by the STRESS reference runner.

## Compliance Declarations
- Stress parameters were declared prior to execution and treated as immutable.
- All stochastic behavior is seeded and disclosed via manifest seeds.
- Metrics are computed observationally from events and declared evidence.
- No adaptive behavior was used to alter execution in response to stress or proxy values.

## Notes
- Workload execution is currently stubbed in this runner.
- Replace stub workload generation with real W1/W2/W3 workload implementations before publishing results as STRESS runs.
"""


def _stub_baseline_events(workload_id: str) -> EventLog:
    """
    Placeholder baseline: creates minimal work/resources evidence.
    Replace with real SP-0 execution.
    """
    log = EventLog(run_id="baseline", workload_id=workload_id)
    log.emit(EventType.RUN_START)
    log.emit(EventType.WORK_UNIT_END, work_done=100.0, resources_used=50.0)
    log.emit(EventType.RUN_END)
    return log


def _stub_workload_events(run_id: str, workload_id: str) -> EventLog:
    """
    Placeholder stressed run:
    Includes evidence for GDS levels, failures for ARR, isolation window for IST,
    resource evidence for REC, and component evidence for CFR.
    Replace with real workload execution + instrumentation.
    """
    log = EventLog(run_id=run_id, workload_id=workload_id)
    log.emit(EventType.RUN_START, t_utc=1000.0)

    # GDS evidence across levels (example)
    log.emit(EventType.WORK_UNIT_END, stress_level=0.1, completion_rate=1.0, work_done=80.0, resources_used=80.0)
    log.emit(EventType.WORK_UNIT_END, stress_level=0.2, completion_rate=0.8)
    log.emit(EventType.WORK_UNIT_END, stress_level=0.3, completion_rate=0.4)

    # ARR evidence
    # (These require correct FailureClass enums already in your events model.)
    # If you want to keep this stub minimal, remove these and ARR will go N/A.
    log.emit(EventType.FAILURE, failure_id="f1", failure_class=FailureClass.AUTONOMOUSLY_RECOVERED)
    log.emit(EventType.FAILURE, failure_id="f2", failure_class=FailureClass.RECOVERABLE_NOT_RECOVERED)

    # IST evidence (deterministic timestamps so survival time is non-zero)
    log.emit(EventType.ISOLATION_START, t_utc=1010.0)
    log.emit(EventType.ISOLATION_END, t_utc=1070.0)

    # CFR evidence (affected components)
    log.emit(EventType.COMPONENT_AFFECTED, component_id="node-1")
    log.emit(EventType.COMPONENT_AFFECTED, component_id="node-2")

    log.emit(EventType.RUN_END, t_utc=1080.0)
    return log
