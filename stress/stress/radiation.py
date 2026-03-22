"""SP-1: Radiation Pressure — probabilistic bit-flip / transient fault injection.

Uses a Poisson process: given dt since last check, probability of at least
one fault is 1 - exp(-rate * dt).
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass

from stress.stress.base import Stressor, StressorConfig


@dataclass(frozen=True)
class RadiationConfig(StressorConfig):
    """SP-1 configuration."""
    fault_rate_per_second: float = 0.001  # Expected faults per second


class RadiationStressor(Stressor):
    """Probabilistic transient fault injection via Poisson process."""

    def __init__(self, config: RadiationConfig):
        super().__init__(config)
        self._cfg: RadiationConfig = config
        self._last_check: float = 0.0
        self._fault_multiplier: float = 1.0

    def reset(self) -> None:
        self._rng = random.Random(self._config.seed)
        self._last_check = 0.0
        self._fault_multiplier = 1.0
        self._active = False
        self._start_time = None

    def set_fault_multiplier(self, multiplier: float) -> None:
        """Allow SP-2 (thermal) to modulate the effective fault rate."""
        self._fault_multiplier = multiplier

    def should_inject_fault(self, t: float) -> bool:
        """Query whether a fault should be injected at time t.

        Returns True with probability derived from Poisson process.
        """
        if not self._active or not self._cfg.enabled:
            return False

        dt = t - self._last_check if self._last_check > 0 else 0.01
        self._last_check = t

        if dt <= 0:
            return False

        effective_rate = self._cfg.fault_rate_per_second * self._fault_multiplier
        # Probability of at least one event in dt: 1 - e^(-rate * dt)
        p = 1.0 - math.exp(-effective_rate * dt)
        return self._rng.random() < p

    @property
    def effective_rate(self) -> float:
        return self._cfg.fault_rate_per_second * self._fault_multiplier
