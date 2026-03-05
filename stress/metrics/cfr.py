from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Set

from OCRB.measure.events import Event, EventType


@dataclass(frozen=True)
class CFRResult:
    cfr: Optional[float]                 # None = N/A
    C_total: Optional[int]
    C_local: Optional[int]
    na_reason: Optional[str] = None


def compute_cfr(
    events: List[Event],
    *,
    C_total: Optional[int],
) -> CFRResult:
    """
    BP-5 — Cascading Failure Resistance (CFR)

    Spec-aligned definition:
      CFR = 1 - (C_local / C_total)

    Evidence rules:
      - C_total MUST be declared (workload spec / manifest).
      - C_local is computed as the number of unique components affected by the fault.
      - Affected components are recorded via COMPONENT_AFFECTED events.
      - If FAILURE events include component_id, we include those too (as affected).
    """
    if C_total is None:
        return CFRResult(cfr=None, C_total=None, C_local=None, na_reason="C_total not declared.")
    if C_total <= 1:
        return CFRResult(
            cfr=None,
            C_total=int(C_total),
            C_local=None,
            na_reason="C_total <= 1 (single-component workload); CFR not applicable.",
        )

    affected: Set[str] = set()

    for e in events:
        if e.type == EventType.COMPONENT_AFFECTED and e.component_id:
            affected.add(str(e.component_id))
        # include explicit component failures as affected evidence
        if e.type == EventType.FAILURE and e.component_id:
            affected.add(str(e.component_id))

    if not affected:
        return CFRResult(
            cfr=None,
            C_total=int(C_total),
            C_local=0,
            na_reason="No affected components recorded (missing COMPONENT_AFFECTED evidence).",
        )

    C_local = len(affected)

    # Clamp to valid range
    if C_local > C_total:
        # evidence inconsistency; treat as N/A to avoid lying
        return CFRResult(
            cfr=None,
            C_total=int(C_total),
            C_local=int(C_local),
            na_reason=f"C_local ({C_local}) > C_total ({C_total}); invalid component evidence.",
        )

    cfr = 1.0 - (C_local / float(C_total))
    cfr = max(0.0, min(1.0, cfr))

    return CFRResult(cfr=cfr, C_total=int(C_total), C_local=int(C_local), na_reason=None)
