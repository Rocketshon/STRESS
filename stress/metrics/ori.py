from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass(frozen=True)
class ORIResult:
    ori: Optional[float]
    weights: Dict[str, float]
    na_reason: Optional[str] = None


def compute_ori(
    proxies: Dict[str, Optional[float]],
    weights: Optional[Dict[str, float]] = None,
) -> ORIResult:
    """
    ORI is the weighted aggregate of the five behavioral proxies.
    v0 default: equal weights.

    Proxies expected keys:
      gds, arr, ist, rec, cfr

    Rule:
      If any required proxy is N/A, ORI is N/A (must be disclosed).
      (This keeps comparability intact.)
    """
    if weights is None:
        weights = {"gds": 0.2, "arr": 0.2, "ist": 0.2, "rec": 0.2, "cfr": 0.2}

    missing = [k for k in weights.keys() if k not in proxies]
    if missing:
        return ORIResult(ori=None, weights=weights, na_reason=f"missing proxies: {missing}")

    na = [k for k in weights.keys() if proxies.get(k) is None]
    if na:
        return ORIResult(ori=None, weights=weights, na_reason=f"ORI N/A because proxies N/A: {na}")

    ori = 0.0
    for k, w in weights.items():
        ori += float(proxies[k]) * float(w)

    # Numerical guardrail
    ori = max(0.0, min(1.0, ori))
    return ORIResult(ori=ori, weights=weights, na_reason=None)
