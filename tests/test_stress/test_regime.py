"""Tests for StressRegime composite."""
from stress.config import StressSeeds
from stress.stress import create_regime, create_baseline_regime
from stress.stress.profiles import SP_1


def test_create_regime():
    """Create a stress regime from seeds and params."""
    seeds = StressSeeds(sr1=100, sr2=200, sr3=300, sr4=400, sr5=500)
    regime = create_regime(seeds, SP_1)

    assert regime.radiation.enabled
    assert regime.thermal.enabled
    assert regime.power.enabled
    assert regime.network.enabled
    assert regime.isolation.enabled


def test_baseline_all_disabled():
    """Baseline regime has all stressors disabled."""
    seeds = StressSeeds(sr1=100, sr2=200, sr3=300, sr4=400, sr5=500)
    regime = create_baseline_regime(seeds)

    assert not regime.radiation.enabled
    assert not regime.thermal.enabled
    assert not regime.power.enabled
    assert not regime.network.enabled
    assert not regime.isolation.enabled


def test_baseline_no_faults():
    """Baseline regime never injects faults."""
    seeds = StressSeeds(sr1=100, sr2=200, sr3=300, sr4=400, sr5=500)
    regime = create_baseline_regime(seeds)
    regime.start_all(0.0)

    assert not regime.should_inject_fault(1.0)
    assert regime.is_available(1.0)
    assert not regime.is_isolated(1.0)


def test_thermal_coupling():
    """SP-2 thermal multiplier affects SP-1 fault rate."""
    seeds = StressSeeds(sr1=100, sr2=200, sr3=300, sr4=400, sr5=500)
    regime = create_regime(seeds, SP_1)
    regime.start_all(0.0)

    # After coupling, the effective rate should be modulated
    regime.update_thermal_coupling(0.0)
    rate = regime.radiation.effective_rate
    assert rate >= regime.radiation._cfg.fault_rate_per_second
