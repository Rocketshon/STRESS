from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Dict, List, Optional
import time


class EventType(str, Enum):
    RUN_START = "run_start"
    RUN_END = "run_end"

    WORK_UNIT_START = "work_unit_start"
    WORK_UNIT_END = "work_unit_end"

    FAILURE = "failure"
    RECOVERY_ATTEMPT = "recovery_attempt"
    RECOVERY_SUCCESS = "recovery_success"
    RECOVERY_FAILED = "recovery_failed"

    ISOLATION_START = "isolation_start"
    ISOLATION_END = "isolation_end"

    COMPONENT_AFFECTED = "component_affected"  # for CFR evidence


class FailureClass(str, Enum):
    AUTONOMOUSLY_RECOVERED = "autonomously_recovered"
    RECOVERABLE_NOT_RECOVERED = "recoverable_not_recovered"
    IRREVERSIBLE = "irreversible"


@dataclass(frozen=True)
class Event:
    """
    Canonical observational record.
    Metrics MUST be computed from these events only (plus manifest + stress levels).
    """
    t_utc: float
    type: EventType
    run_id: str

    workload_id: Optional[str] = None
    component_id: Optional[str] = None  # node/service/process identifier if applicable
    work_unit_id: Optional[str] = None  # task/job id for completion tracking

    # Failure / recovery fields
    failure_id: Optional[str] = None
    failure_class: Optional[FailureClass] = None

    # For GDS evidence (stress intensity levels s_i)
    stress_level: Optional[float] = None  # s_i declared intensity value
    completion_rate: Optional[float] = None  # C_i in [0,1] if you record per-level completion

    # Resources / work evidence (REC support)
    work_done: Optional[float] = None
    resources_used: Optional[float] = None

    # Free-form for implementation details (MUST NOT be required by metrics)
    meta: Dict[str, Any] = field(default_factory=dict)


class EventLog:
    """
    In-memory log. Later we can persist to JSONL.
    """
    def __init__(self, run_id: str, workload_id: str):
        self.run_id = run_id
        self.workload_id = workload_id
        self._events: List[Event] = []

    def emit(self, type: EventType, **kwargs: Any) -> Event:
        ev = Event(
            t_utc=kwargs.pop("t_utc", time.time()),
            type=type,
            run_id=self.run_id,
            workload_id=kwargs.pop("workload_id", self.workload_id),
            **kwargs,
        )
        self._events.append(ev)
        return ev

    @property
    def events(self) -> List[Event]:
        return list(self._events)

    def to_dicts(self) -> List[Dict[str, Any]]:
        return [asdict(e) for e in self._events]


def validate_event_log(events: List[Event]) -> None:
    """
    Lightweight structural validation so we don't compute metrics from nonsense.
    Raises ValueError on obvious violations.
    """
    if not events:
        raise ValueError("Event log is empty.")

    # Must have run_start before run_end if present
    types = [e.type for e in events]
    if EventType.RUN_START not in types:
        raise ValueError("Missing run_start event.")
    if EventType.RUN_END in types:
        start_i = types.index(EventType.RUN_START)
        end_i = len(types) - 1 - list(reversed(types)).index(EventType.RUN_END)
        if end_i < start_i:
            raise ValueError("run_end occurred before run_start.")

    # Basic bounds checks
    for e in events:
        if e.completion_rate is not None and not (0.0 <= e.completion_rate <= 1.0):
            raise ValueError(f"completion_rate out of bounds: {e.completion_rate}")
        if e.stress_level is not None and not isinstance(e.stress_level, (int, float)):
            raise ValueError("stress_level must be numeric.")
