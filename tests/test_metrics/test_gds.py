"""Tests for BP-1: Graceful Degradation Score."""
from stress.measure.events import EventLog, EventType
from stress.metrics.gds import compute_gds


def _make_log(levels_rates):
    """Create an event log with GDS evidence at given (level, rate) pairs."""
    log = EventLog(run_id="test", workload_id="test")
    log.emit(EventType.RUN_START)
    for level, rate in levels_rates:
        log.emit(EventType.WORK_UNIT_END, stress_level=level, completion_rate=rate)
    log.emit(EventType.RUN_END)
    return log


def test_perfect_gds():
    log = _make_log([(0.1, 1.0), (0.2, 1.0), (0.3, 1.0)])
    result = compute_gds(log.events, expected_levels=[0.1, 0.2, 0.3])
    assert result.gds == 1.0


def test_degrading_gds():
    log = _make_log([(0.1, 1.0), (0.2, 0.5), (0.3, 0.0)])
    result = compute_gds(log.events, expected_levels=[0.1, 0.2, 0.3])
    assert abs(result.gds - 0.5) < 0.01


def test_no_levels_na():
    log = EventLog(run_id="test", workload_id="test")
    log.emit(EventType.RUN_START)
    log.emit(EventType.RUN_END)
    result = compute_gds(log.events)
    assert result.gds is None
    assert result.na_reason is not None
