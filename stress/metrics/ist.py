from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from OCRB.measure.events import Event, EventType, FailureClass


@dataclass(frozen=True)
class ISTResult:
    ist: Optional[float]                 # None = N/A
    isolation_duration_declared: Optional[float]
    survival_time_observed: Optional[float]
    na_reason: Optional[str] = None


def compute_ist(
    events: List[Event],
    isolation_duration_declared: Optional[float],
) -> ISTResult:
    """
    BP-3 — Isolation Survival Time (IST)

    Normalized definition:
      IST = clamp( survival_time / isolation_duration_declared, 0, 1 )

    Measurement rules (behavioral):
      - Isolation starts at ISOLATION_START.
      - Isolation ends when:
          a) ISOLATION_END occurs (survived isolation), OR
          b) an IRREVERSIBLE failure occurs while isolated, OR
          c) RUN_END occurs while isolated.

    Edge cases:
      - If isolation_duration_declared is missing or <= 0 -> IST is N/A.
      - If no isolation_start event exists -> IST is N/A (not applicable).
    """
    if isolation_duration_declared is None or isolation_duration_declared <= 0:
        return ISTResult(
            ist=None,
            isolation_duration_declared=isolation_duration_declared,
            survival_time_observed=None,
            na_reason="Missing or invalid declared isolation duration.",
        )

    # Find isolation start
    iso_start: Optional[float] = None
    for e in events:
        if e.type == EventType.ISOLATION_START:
            iso_start = e.t_utc
            break

    if iso_start is None:
        return ISTResult(
            ist=None,
            isolation_duration_declared=isolation_duration_declared,
            survival_time_observed=None,
            na_reason="No isolation_start event observed (IST not applicable).",
        )

    # Track whether we're currently isolated
    isolated = True

    # Find first terminating event after iso_start
    iso_end_time: Optional[float] = None

    for e in events:
        if e.t_utc < iso_start:
            continue

        if isolated and e.type == EventType.ISOLATION_END:
            iso_end_time = e.t_utc
            isolated = False
            break

        if isolated and e.type == EventType.FAILURE and e.failure_class == FailureClass.IRREVERSIBLE:
            iso_end_time = e.t_utc
            break

        if isolated and e.type == EventType.RUN_END:
            iso_end_time = e.t_utc
            break

    if iso_end_time is None:
        # No terminating event observed; assume survived until last event timestamp
        iso_end_time = max(e.t_utc for e in events)

    survival_time = max(0.0, iso_end_time - iso_start)
    ist = survival_time / float(isolation_duration_declared)
    ist = max(0.0, min(1.0, ist))

    return ISTResult(
        ist=ist,
        isolation_duration_declared=float(isolation_duration_declared),
        survival_time_observed=survival_time,
        na_reason=None,
    )
