"""Tests for BP-2: Autonomous Recovery Rate."""
from stress.measure.events import EventLog, EventType, FailureClass
from stress.metrics.arr import compute_arr


def test_all_recovered():
    log = EventLog(run_id="test", workload_id="test")
    log.emit(EventType.RUN_START)
    log.emit(EventType.FAILURE, failure_id="f1", failure_class=FailureClass.AUTONOMOUSLY_RECOVERED)
    log.emit(EventType.FAILURE, failure_id="f2", failure_class=FailureClass.AUTONOMOUSLY_RECOVERED)
    log.emit(EventType.RUN_END)
    result = compute_arr(log.events)
    assert result.arr == 1.0


def test_partial_recovery():
    log = EventLog(run_id="test", workload_id="test")
    log.emit(EventType.RUN_START)
    log.emit(EventType.FAILURE, failure_id="f1", failure_class=FailureClass.AUTONOMOUSLY_RECOVERED)
    log.emit(EventType.FAILURE, failure_id="f2", failure_class=FailureClass.RECOVERABLE_NOT_RECOVERED)
    log.emit(EventType.RUN_END)
    result = compute_arr(log.events)
    assert result.arr == 0.5


def test_no_failures_na():
    log = EventLog(run_id="test", workload_id="test")
    log.emit(EventType.RUN_START)
    log.emit(EventType.RUN_END)
    result = compute_arr(log.events)
    assert result.arr is None
    assert result.na_reason is not None
