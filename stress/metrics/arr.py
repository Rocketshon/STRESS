from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from OCRB.measure.events import Event, EventType, FailureClass


@dataclass(frozen=True)
class ARRResult:
    arr: Optional[float]          # None = N/A
    Fr: int                       # recoverable failures observed
    Fa: int                       # autonomously recovered failures observed
    na_reason: Optional[str] = None


def compute_arr(events: List[Event]) -> ARRResult:
    """
    BP-2 — Autonomous Recovery Rate (ARR)
    ARR = Fa / Fr

    Where:
      Fr = number of recoverable failures observed (incl. auto-recovered + not recovered)
      Fa = number of recoverable failures autonomously recovered

    Edge case:
      If Fr == 0, ARR is N/A (metric not applicable). Must be disclosed.
    """
    Fr = 0
    Fa = 0

    for e in events:
        if e.type == EventType.FAILURE and e.failure_class is not None:
            if e.failure_class in (
                FailureClass.AUTONOMOUSLY_RECOVERED,
                FailureClass.RECOVERABLE_NOT_RECOVERED,
            ):
                Fr += 1
                if e.failure_class == FailureClass.AUTONOMOUSLY_RECOVERED:
                    Fa += 1

    if Fr == 0:
        return ARRResult(arr=None, Fr=0, Fa=0, na_reason="Fr=0 (no recoverable failures observed)")

    return ARRResult(arr=Fa / Fr, Fr=Fr, Fa=Fa, na_reason=None)
