"""SP-4: Network Jitter — latency variance + packet loss simulation."""
from __future__ import annotations

import random
from dataclasses import dataclass

from stress.stress.base import Stressor, StressorConfig


@dataclass(frozen=True)
class NetworkConfig(StressorConfig):
    """SP-4 configuration."""
    baseline_latency_ms: float = 50.0
    jitter_pct: float = 50.0  # Variance as percentage of baseline
    packet_loss_probability: float = 0.05


class NetworkStressor(Stressor):
    """Network jitter and packet loss simulation.

    Applied to workloads with communication dependencies (W2-A external calls,
    W3-A inter-node messaging).
    """

    def __init__(self, config: NetworkConfig):
        super().__init__(config)
        self._cfg: NetworkConfig = config

    def reset(self) -> None:
        self._rng = random.Random(self._config.seed)
        self._active = False
        self._start_time = None

    def get_latency_ms(self, t: float) -> float:
        """Get simulated network latency at time t.

        Returns baseline + jitter drawn from normal distribution,
        clipped to [0, 2 * baseline].
        """
        if not self._active or not self._cfg.enabled:
            return 0.0

        jitter_std = self._cfg.baseline_latency_ms * (self._cfg.jitter_pct / 100.0)
        latency = self._rng.gauss(self._cfg.baseline_latency_ms, jitter_std)
        return max(0.0, min(latency, 2.0 * self._cfg.baseline_latency_ms))

    def is_packet_lost(self, t: float) -> bool:
        """Check if a packet is lost at time t (Bernoulli trial)."""
        if not self._active or not self._cfg.enabled:
            return False
        return self._rng.random() < self._cfg.packet_loss_probability
