from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Optional, Tuple


@dataclass(frozen=True)
class SummaryStats:
    mean: Optional[float]
    std: Optional[float]
    ci95_low: Optional[float]
    ci95_high: Optional[float]
    n_included: int
    n_na: int


def _mean(xs: List[float]) -> float:
    return sum(xs) / len(xs)


def _std_sample(xs: List[float]) -> float:
    # sample std dev (n-1)
    n = len(xs)
    if n < 2:
        return 0.0
    m = _mean(xs)
    var = sum((x - m) ** 2 for x in xs) / (n - 1)
    return math.sqrt(var)


def summarize(values: List[Optional[float]]) -> SummaryStats:
    """
    Compute mean/std/95% CI over included values.
    N/A values are excluded but counted.
    95% CI uses normal approximation: mean ± 1.96 * (std/sqrt(n))
    (Acceptable for v0; can be swapped later as "valid deviation" if disclosed.)
    """
    included = [v for v in values if v is not None]
    n_na = sum(1 for v in values if v is None)

    if not included:
        return SummaryStats(
            mean=None, std=None, ci95_low=None, ci95_high=None,
            n_included=0, n_na=n_na
        )

    n = len(included)
    m = _mean(included)
    s = _std_sample(included)

    if n == 1:
        return SummaryStats(
            mean=m, std=0.0, ci95_low=m, ci95_high=m,
            n_included=1, n_na=n_na
        )

    se = s / math.sqrt(n)
    z = 1.96
    lo = m - z * se
    hi = m + z * se

    # Clamp to [0,1] for normalized proxies/ORI
    lo = max(0.0, min(1.0, lo))
    hi = max(0.0, min(1.0, hi))

    return SummaryStats(
        mean=m, std=s, ci95_low=lo, ci95_high=hi,
        n_included=n, n_na=n_na
    )
