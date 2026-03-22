"""STRESS injection layer — composes SP-1 through SP-5 into a StressRegime."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from stress.stress.radiation import RadiationStressor, RadiationConfig
from stress.stress.thermal import ThermalStressor, ThermalConfig
from stress.stress.power import PowerStressor, PowerConfig
from stress.stress.network import NetworkStressor, NetworkConfig
from stress.stress.isolation import IsolationStressor, IsolationConfig


@dataclass
class StressRegime:
    """Composite of all five stressors with a unified query interface."""
    radiation: RadiationStressor
    thermal: ThermalStressor
    power: PowerStressor
    network: NetworkStressor
    isolation: IsolationStressor

    def start_all(self, t: float) -> None:
        """Start all enabled stressors at time t."""
        for s in [self.radiation, self.thermal, self.power, self.network, self.isolation]:
            if s.enabled:
                s.start(t)

    def stop_all(self) -> None:
        """Stop all stressors."""
        for s in [self.radiation, self.thermal, self.power, self.network, self.isolation]:
            s.stop()

    def reset_all(self) -> None:
        """Reset all stressors for reproducibility."""
        for s in [self.radiation, self.thermal, self.power, self.network, self.isolation]:
            s.reset()

    def update_thermal_coupling(self, t: float) -> None:
        """Apply SP-2 thermal multiplier to SP-1 radiation fault rate.

        This coupling is explicitly declared per spec.
        """
        multiplier = self.thermal.get_thermal_multiplier(t)
        self.radiation.set_fault_multiplier(multiplier)

    def should_inject_fault(self, t: float) -> bool:
        """Query SP-1 (with SP-2 modulation) for fault injection."""
        self.update_thermal_coupling(t)
        return self.radiation.should_inject_fault(t)

    def is_available(self, t: float, total_duration: float = 3600.0) -> bool:
        """Query SP-3 for power availability."""
        return self.power.is_available(t, total_duration)

    def is_isolated(self, t: float) -> bool:
        """Query SP-5 for isolation state."""
        return self.isolation.is_isolated(t)

    def get_network_latency_ms(self, t: float) -> float:
        """Query SP-4 for network latency."""
        return self.network.get_latency_ms(t)

    def is_packet_lost(self, t: float) -> bool:
        """Query SP-4 for packet loss."""
        return self.network.is_packet_lost(t)


def create_regime(
    seeds: "stress.config.StressSeeds",
    params: dict,
    enabled: bool = True,
) -> StressRegime:
    """Create a StressRegime from seeds and parameter dict."""
    sp1_params = params.get("SP-1", params.get("SR-1", {}))
    sp2_params = params.get("SP-2", params.get("SR-2", {}))
    sp3_params = params.get("SP-3", params.get("SR-3", {}))
    sp4_params = params.get("SP-4", params.get("SR-4", {}))
    sp5_params = params.get("SP-5", params.get("SR-5", {}))

    return StressRegime(
        radiation=RadiationStressor(RadiationConfig(
            enabled=enabled and bool(sp1_params),
            seed=seeds.sr1,
            fault_rate_per_second=sp1_params.get("rate", 0.001),
        )),
        thermal=ThermalStressor(ThermalConfig(
            enabled=enabled and bool(sp2_params),
            seed=seeds.sr2,
            cycle_period_s=sp2_params.get("cycle_period_s", 600.0),
            amplitude=sp2_params.get("amplitude", 3.0),
        )),
        power=PowerStressor(PowerConfig(
            enabled=enabled and bool(sp3_params),
            seed=seeds.sr3,
            availability_pct=sp3_params.get("availability_pct", 80.0),
            interruption_duration_s=sp3_params.get("interruption_duration_s", 5.0),
            schedule=sp3_params.get("schedule", "periodic"),
        )),
        network=NetworkStressor(NetworkConfig(
            enabled=enabled and bool(sp4_params),
            seed=seeds.sr4,
            baseline_latency_ms=sp4_params.get("baseline_latency_ms", 50.0),
            jitter_pct=sp4_params.get("jitter_pct", 50.0),
            packet_loss_probability=sp4_params.get("packet_loss_probability", 0.05),
        )),
        isolation=IsolationStressor(IsolationConfig(
            enabled=enabled and bool(sp5_params),
            seed=seeds.sr5,
            max_duration_s=sp5_params.get("max_duration_s", 120.0),
            trigger_offset_s=sp5_params.get("trigger_offset_s", 10.0),
        )),
    )


def create_baseline_regime(seeds: "stress.config.StressSeeds") -> StressRegime:
    """Create SP-0 baseline regime with all stressors disabled."""
    return create_regime(seeds, {}, enabled=False)
