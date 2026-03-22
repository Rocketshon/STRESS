from stress.measure.events import EventLog, EventType, FailureClass
from stress.metrics.sri import compute_sri

def test_sri_computation():
    log = EventLog(run_id="t", workload_id="W1-A")
    log.emit(EventType.RUN_START)
    log.emit(EventType.FAILURE, failure_id="f1", failure_class=FailureClass.AUTONOMOUSLY_RECOVERED)
    log.emit(EventType.RUN_END)

    sri = compute_sri(
        proxies={
            "gds": 1.0,
            "arr": 1.0,
            "ist": 1.0,
            "rec": 1.0,
            "cfr": 1.0,
        }
    )

    assert sri.sri == 100.0
