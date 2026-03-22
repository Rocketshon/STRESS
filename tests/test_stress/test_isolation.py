"""Tests for SP-5: Isolation stressor."""
from stress.stress.isolation import IsolationStressor, IsolationConfig


def test_isolation_window():
    """Isolation is active only during the declared window."""
    cfg = IsolationConfig(enabled=True, seed=42, max_duration_s=60.0, trigger_offset_s=10.0)
    s = IsolationStressor(cfg)
    s.start(0.0)

    assert not s.is_isolated(0.0)    # Before window
    assert not s.is_isolated(9.9)    # Just before
    assert s.is_isolated(10.0)       # Start of window
    assert s.is_isolated(50.0)       # Middle
    assert s.is_isolated(69.9)       # Near end
    assert not s.is_isolated(70.0)   # End of window


def test_disabled_never_isolated():
    """Disabled stressor never reports isolation."""
    cfg = IsolationConfig(enabled=False, seed=42, max_duration_s=60.0, trigger_offset_s=0.0)
    s = IsolationStressor(cfg)
    s.start(0.0)
    assert not s.is_isolated(30.0)
