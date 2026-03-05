from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from OCRB.measure.events import Event, EventType


@dataclass(frozen=True)
class GDSResult:
    gds: Optional[float]               # None = N/A
    n_levels: int
    stress_levels: List[float]
    completion_rates: List[float]
    na_reason: Optional[str] = None


def compute_gds(
    events: List[Event],
    expected_levels: Optional[List[float]] = None,
) -> GDSResult:
    """
    BP-1 — Graceful Degradation Score (GDS)

    Spec-aligned definition:
      Execute at ordered stress intensity levels s1..sn
      Measure completion rate Ci at each level
      GDS = (1/n) * Σ Ci

    Data source:
      We accept per-level completion evidence as events with:
        - type == WORK_UNIT_END (optional per-task) OR
        - events that directly carry (stress_level, completion_rate)
      For v0 reference implementation, we prefer the explicit evidence events:
        Event with completion_rate != None and stress_level != None.

    expected_levels:
      If provided, enforce that we have data for each declared level (orderable).
    """
    levels: List[float] = []
    rates: List[float] = []

    # Prefer explicit evidence events (stress_level + completion_rate)
    for e in events:
        if e.stress_level is not None and e.completion_rate is not None:
            levels.append(float(e.stress_level))
            rates.append(float(e.completion_rate))

    if not levels:
        return GDSResult(
            gds=None,
            n_levels=0,
            stress_levels=[],
            completion_rates=[],
            na_reason="No (stress_level, completion_rate) evidence found in events.",
        )

    # Basic bounds check
    for r in rates:
        if not (0.0 <= r <= 1.0):
            return GDSResult(
                gds=None,
                n_levels=len(levels),
                stress_levels=levels,
                completion_rates=rates,
                na_reason=f"completion_rate out of bounds: {r}",
            )

    # If expected levels are declared, enforce coverage
    if expected_levels is not None:
        exp = [float(x) for x in expected_levels]
        got = set(levels)
        missing = [x for x in exp if x not in got]
        if missing:
            return GDSResult(
                gds=None,
                n_levels=len(levels),
                stress_levels=levels,
                completion_rates=rates,
                na_reason=f"Missing declared stress levels: {missing}",
            )

    n = len(rates)
    gds = sum(rates) / n
    gds = max(0.0, min(1.0, gds))

    # Ensure stress levels are monotonically orderable (spec requirement)
    # We don’t force monotonic in events ordering, but we ensure they can be sorted and disclosed.
    paired = sorted(zip(levels, rates), key=lambda x: x[0])
    s_sorted = [p[0] for p in paired]
    c_sorted = [p[1] for p in paired]

    return GDSResult(
        gds=gds,
        n_levels=n,
        stress_levels=s_sorted,
        completion_rates=c_sorted,
        na_reason=None,
    )
