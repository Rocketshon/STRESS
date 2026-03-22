"""Base classes for STRESS injectors.

Each stressor is independent, seeded, declarable before execution,
and non-intrusive to measurement.
"""
from __future__ import annotations

import random
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class StressorConfig:
    """Base configuration for all stressors. Immutable after declaration."""
    enabled: bool
    seed: int


class Stressor(ABC):
    """Abstract base for all stress profile injectors (SP-1 through SP-5)."""

    def __init__(self, config: StressorConfig):
        self._config = config
        self._rng = random.Random(config.seed)
        self._active = False
        self._start_time: Optional[float] = None

    @property
    def config(self) -> StressorConfig:
        return self._config

    @property
    def enabled(self) -> bool:
        return self._config.enabled

    @property
    def active(self) -> bool:
        return self._active

    def start(self, t: float) -> None:
        """Start this stressor at time t."""
        self._active = True
        self._start_time = t

    def stop(self) -> None:
        """Stop this stressor."""
        self._active = False

    @abstractmethod
    def reset(self) -> None:
        """Reset internal state, re-seed RNG for reproducibility."""
        ...

    def _elapsed(self, t: float) -> float:
        """Elapsed time since start."""
        if self._start_time is None:
            return 0.0
        return t - self._start_time
