"""SP-3: Power Disruption — intermittent availability windows.

Models power availability as either periodic duty cycles or
stochastic (Poisson) interruption events.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Literal

from stress.stress.base import Stressor, StressorConfig


@dataclass(frozen=True)
class PowerConfig(StressorConfig):
    """SP-3 configuration."""
    availability_pct: float = 80.0  # Percentage of time power is available
    interruption_duration_s: float = 5.0  # Duration of each interruption
    schedule: str = "periodic"  # "periodic" or "stochastic"


class PowerStressor(Stressor):
    """Power disruption via duty cycle or stochastic interruptions."""

    def __init__(self, config: PowerConfig):
        super().__init__(config)
        self._cfg: PowerConfig = config
        self._interruption_times: list[float] = []
        self._generated = False

    def reset(self) -> None:
        self._rng = random.Random(self._config.seed)
        self._interruption_times = []
        self._generated = False
        self._active = False
        self._start_time = None

    def _ensure_generated(self, duration: float) -> None:
        """Pre-generate interruption schedule for reproducibility."""
        if self._generated:
            return
        self._generated = True

        if self._cfg.schedule == "periodic":
            # Duty cycle: available_time + interruption_time = cycle_time
            # availability_pct determines the split
            avail_frac = self._cfg.availability_pct / 100.0
            if avail_frac >= 1.0:
                return  # Never interrupted
            cycle_time = self._cfg.interruption_duration_s / (1.0 - avail_frac)
            available_time = cycle_time * avail_frac
            t = available_time  # First interruption starts after initial available period
            while t < duration:
                self._interruption_times.append(t)
                t += cycle_time
        else:
            # Stochastic: Poisson arrivals
            avail_frac = self._cfg.availability_pct / 100.0
            if avail_frac >= 1.0:
                return
            # Mean up-time (gap) = avail * interrupt_dur / (1 - avail)
            mean_gap = avail_frac * self._cfg.interruption_duration_s / (1.0 - avail_frac) if avail_frac < 1.0 else float("inf")
            t = self._rng.expovariate(1.0 / mean_gap) if mean_gap < float("inf") else float("inf")
            while t < duration:
                self._interruption_times.append(t)
                next_gap = self._rng.expovariate(1.0 / mean_gap)
                t += self._cfg.interruption_duration_s + next_gap

    def is_available(self, t: float, total_duration: float = 3600.0) -> bool:
        """Check if power is available at time t.

        Returns False during interruption windows.
        """
        if not self._active or not self._cfg.enabled:
            return True

        self._ensure_generated(total_duration)
        elapsed = self._elapsed(t)

        for start in self._interruption_times:
            if start <= elapsed < start + self._cfg.interruption_duration_s:
                return False
        return True
