from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple

from OCRB.measure.events import Event


@dataclass(frozen=True)
class RECResult:
    rec: Optional[float]                 # None = N/A
    E_base: Optional[float]
    E_stress: Optional[float]
    na_reason: Optional[str] = None


def _sum_work_and_resources(events: List[Event]) -> Tuple[float, float]:
    work = 0.0
    resources = 0.0
    for e in events:
        if e.work_done is not None:
            work += float(e.work_done)
        if e.resources_used is not None:
            resources += float(e.resources_used)
    return work, resources


def compute_rec(
    baseline_events: List[Event],
    stressed_events: List[Event],
    *,
    baseline_min_work: float = 0.0,
) -> RECResult:
    """
    BP-4 — Resource Efficiency Under Constraint (REC)

    E_base   = work_base / resources_base   (SP-0 baseline)
    E_stress = work_stress / resources_stress (stressed run)

    REC = min(E_stress / E_base, 1.0)

    Notes:
      - If E_base is undefined (resources=0 or work too low), REC is N/A.
      - If stressed produces no work but baseline does, REC = 0.0 (valid).
      - This function is purely observational: it only reads event evidence.
    """
    work_b, res_b = _sum_work_and_resources(baseline_events)
    work_s, res_s = _sum_work_and_resources(stressed_events)

    # Baseline validity gate (optional but useful)
    if work_b < baseline_min_work:
        return RECResult(
            rec=None,
            E_base=None,
            E_stress=None,
            na_reason=f"Baseline work below minimum threshold: {work_b} < {baseline_min_work}",
        )

    if res_b <= 0.0:
        return RECResult(
            rec=None,
            E_base=None,
            E_stress=None,
            na_reason="Baseline resources_used is zero/undefined; cannot compute E_base.",
        )

    E_base = work_b / res_b

    if E_base <= 0.0:
        return RECResult(
            rec=None,
            E_base=None,
            E_stress=None,
            na_reason="Baseline efficiency is zero/undefined; cannot normalize REC.",
        )

    if res_s <= 0.0:
        return RECResult(
            rec=None,
            E_base=E_base,
            E_stress=None,
            na_reason="Stressed resources_used is zero/undefined; cannot compute E_stress.",
        )

    E_stress = work_s / res_s

    ratio = E_stress / E_base
    rec = min(max(ratio, 0.0), 1.0)

    return RECResult(
        rec=rec,
        E_base=E_base,
        E_stress=E_stress,
        na_reason=None,
    )
