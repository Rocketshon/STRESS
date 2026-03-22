"""SP-2: Thermal Cycling — periodic stress modulation.

Modulates SP-1 fault rate using a sinusoidal function.
Purely deterministic; no RNG needed.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass

from stress.stress.base import Stressor, StressorConfig


@dataclass(frozen=True)
class ThermalConfig(StressorConfig):
    """SP-2 configuration."""
    cycle_period_s: float = 600.0  # Period of one thermal cycle in seconds
    amplitude: float = 3.0  # Peak multiplier on SP-1 fault rate


class ThermalStressor(Stressor):
    """Deterministic periodic thermal cycling.

    Produces a multiplier >= 1.0 that modulates the SP-1 fault rate.
    """

    def __init__(self, config: ThermalConfig):
        super().__init__(config)
        self._cfg: ThermalConfig = config

    def reset(self) -> None:
        self._rng = random.Random(self._config.seed)
        self._active = False
        self._start_time = None

    def get_thermal_multiplier(self, t: float) -> float:
        """Get the thermal multiplier at time t.

        Returns a value >= 1.0 that should be applied to SP-1's fault rate.
        The multiplier follows a sinusoidal curve:
          1.0 + (amplitude - 1.0) * (0.5 + 0.5 * sin(2*pi*t / period))
        """
        if not self._active or not self._cfg.enabled:
            return 1.0

        elapsed = self._elapsed(t)
        phase = 2.0 * math.pi * elapsed / self._cfg.cycle_period_s
        # Range: [1.0, amplitude]
        return 1.0 + (self._cfg.amplitude - 1.0) * (0.5 + 0.5 * math.sin(phase))
