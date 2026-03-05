from __future__ import annotations

from dataclasses import dataclass, asdict, field
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class ProxyEvidence:
    # BP-1 (GDS)
    stress_levels: Optional[List[float]] = None
    completion_rates: Optional[List[float]] = None

    # BP-2 (ARR)
    Fr: Optional[int] = None
    Fa: Optional[int] = None

    # BP-3 (IST)
    isolation_duration: Optional[float] = None
    survival_time: Optional[float] = None

    # BP-4 (REC)
    E_base: Optional[float] = None
    E_stress: Optional[float] = None
    baseline_completion_ok: Optional[bool] = None

    # BP-5 (CFR)
    C_total: Optional[int] = None
    C_local: Optional[int] = None


@dataclass(frozen=True)
class ProxyValues:
    # Use None for N/A
    gds: Optional[float] = None
    arr: Optional[float] = None
    ist: Optional[float] = None
    rec: Optional[float] = None
    cfr: Optional[float] = None
    ori: Optional[float] = None


@dataclass(frozen=True)
class RunRecord:
    run_id: str
    workload_id: str
    seeds: Dict[str, int]

    start_utc: float
    end_utc: float

    proxies: ProxyValues
    evidence: ProxyEvidence

    # Minimal required disclosures at run granularity
    na_reasons: Dict[str, str] = field(default_factory=dict)

    # Raw observational record (events)
    events: List[Dict[str, Any]] = field(default_factory=list)


@dataclass(frozen=True)
class AggregateStats:
    mean: Optional[float]
    std: Optional[float]
    ci95_low: Optional[float]
    ci95_high: Optional[float]
    n_included: int
    n_na: int


@dataclass(frozen=True)
class AggregateSummary:
    # Per proxy + ORI
    gds: AggregateStats
    arr: AggregateStats
    ist: AggregateStats
    rec: AggregateStats
    cfr: AggregateStats
    ori: AggregateStats


def to_dict(obj: Any) -> Dict[str, Any]:
    return asdict(obj)
