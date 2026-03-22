"""Tests for SP-1: Radiation Pressure stressor."""
from stress.stress.radiation import RadiationStressor, RadiationConfig


def test_determinism():
    """Same seed produces identical fault sequence."""
    cfg = RadiationConfig(enabled=True, seed=42, fault_rate_per_second=0.1)
    s1 = RadiationStressor(cfg)
    s2 = RadiationStressor(cfg)
    s1.start(0.0)
    s2.start(0.0)

    results1 = [s1.should_inject_fault(t * 0.1) for t in range(100)]
    results2 = [s2.should_inject_fault(t * 0.1) for t in range(100)]
    assert results1 == results2


def test_different_seeds_diverge():
    """Different seeds produce different sequences."""
    c1 = RadiationConfig(enabled=True, seed=42, fault_rate_per_second=0.5)
    c2 = RadiationConfig(enabled=True, seed=99, fault_rate_per_second=0.5)
    s1 = RadiationStressor(c1)
    s2 = RadiationStressor(c2)
    s1.start(0.0)
    s2.start(0.0)

    r1 = [s1.should_inject_fault(t * 0.1) for t in range(100)]
    r2 = [s2.should_inject_fault(t * 0.1) for t in range(100)]
    assert r1 != r2


def test_disabled_never_faults():
    """Disabled stressor never injects faults."""
    cfg = RadiationConfig(enabled=False, seed=42, fault_rate_per_second=1.0)
    s = RadiationStressor(cfg)
    s.start(0.0)
    assert all(not s.should_inject_fault(t) for t in range(100))


def test_rate_calibration():
    """Over many trials, observed fault rate is within statistical bounds."""
    cfg = RadiationConfig(enabled=True, seed=123, fault_rate_per_second=0.5)
    s = RadiationStressor(cfg)
    s.start(0.0)

    n = 10000
    dt = 0.01
    faults = sum(1 for t in range(n) if s.should_inject_fault(t * dt))

    # Expected: ~50 faults (0.5 * 0.01 * 10000 = 50)
    # Allow generous bounds for stochastic test
    assert 20 < faults < 100


def test_multiplier_affects_rate():
    """Setting fault multiplier changes effective fault rate."""
    cfg = RadiationConfig(enabled=True, seed=42, fault_rate_per_second=0.01)
    s = RadiationStressor(cfg)
    s.start(0.0)
    s.set_fault_multiplier(100.0)
    assert s.effective_rate == 1.0
