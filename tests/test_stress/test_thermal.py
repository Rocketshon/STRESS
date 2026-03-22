"""Tests for SP-2: Thermal Cycling stressor."""
import math
from stress.stress.thermal import ThermalStressor, ThermalConfig


def test_multiplier_range():
    """Multiplier stays within [1.0, amplitude]."""
    cfg = ThermalConfig(enabled=True, seed=42, cycle_period_s=100.0, amplitude=5.0)
    s = ThermalStressor(cfg)
    s.start(0.0)

    for t in range(1000):
        m = s.get_thermal_multiplier(t * 0.1)
        assert 1.0 <= m <= 5.0, f"multiplier {m} out of range at t={t*0.1}"


def test_periodicity():
    """Multiplier repeats with the declared period."""
    cfg = ThermalConfig(enabled=True, seed=42, cycle_period_s=100.0, amplitude=3.0)
    s = ThermalStressor(cfg)
    s.start(0.0)

    m_at_50 = s.get_thermal_multiplier(50.0)
    m_at_150 = s.get_thermal_multiplier(150.0)
    assert abs(m_at_50 - m_at_150) < 0.01


def test_disabled_returns_one():
    """Disabled thermal stressor always returns 1.0."""
    cfg = ThermalConfig(enabled=False, seed=42, cycle_period_s=100.0, amplitude=5.0)
    s = ThermalStressor(cfg)
    s.start(0.0)
    assert s.get_thermal_multiplier(50.0) == 1.0
