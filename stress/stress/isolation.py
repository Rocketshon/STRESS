"""SP-5: Isolation Duration — complete external disconnection."""
from __future__ import annotations

import random
from dataclasses import dataclass

from stress.stress.base import Stressor, StressorConfig


@dataclass(frozen=True)
class IsolationConfig(StressorConfig):
    """SP-5 configuration."""
    max_duration_s: float = 120.0  # Duration of isolation window
    trigger_offset_s: float = 10.0  # Time after run start to begin isolation


class IsolationStressor(Stressor):
    """Binary isolation: completely disconnects external communications
    for a defined time window.
    """

    def __init__(self, config: IsolationConfig):
        super().__init__(config)
        self._cfg: IsolationConfig = config

    def reset(self) -> None:
        self._rng = random.Random(self._config.seed)
        self._active = False
        self._start_time = None

    @property
    def trigger_offset_s(self) -> float:
        return self._cfg.trigger_offset_s

    @property
    def max_duration_s(self) -> float:
        return self._cfg.max_duration_s

    def is_isolated(self, t: float) -> bool:
        """Check if the system is in isolation at time t.

        Returns True during the isolation window:
        [trigger_offset_s, trigger_offset_s + max_duration_s)
        """
        if not self._active or not self._cfg.enabled:
            return False

        elapsed = self._elapsed(t)
        return (self._cfg.trigger_offset_s
                <= elapsed
                < self._cfg.trigger_offset_s + self._cfg.max_duration_s)
