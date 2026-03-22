use crate::types::events::{Event, EventType, FailureClass};

#[derive(Debug, Clone)]
pub struct ArrResult {
    pub arr: Option<f64>,
    pub fr: i64,
    pub fa: i64,
    pub na_reason: Option<String>,
}

/// BP-2: Autonomous Recovery Rate. ARR = Fa / Fr.
pub fn compute_arr(events: &[Event]) -> ArrResult {
    let mut fr: i64 = 0;
    let mut fa: i64 = 0;

    for e in events {
        if e.event_type == EventType::Failure {
            if let Some(fc) = &e.failure_class {
                match fc {
                    FailureClass::AutonomouslyRecovered => {
                        fr += 1;
                        fa += 1;
                    }
                    FailureClass::RecoverableNotRecovered => {
                        fr += 1;
                    }
                    FailureClass::Irreversible => {}
                }
            }
        }
    }

    if fr == 0 {
        return ArrResult {
            arr: None, fr: 0, fa: 0,
            na_reason: Some("Fr=0 (no recoverable failures observed)".to_string()),
        };
    }

    ArrResult {
        arr: Some(fa as f64 / fr as f64),
        fr, fa, na_reason: None,
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::types::events::EventLog;

    #[test]
    fn all_recovered() {
        let mut log = EventLog::new("t", "W1-A");
        log.emit(EventType::RunStart);
        let e = log.emit(EventType::Failure);
        e.failure_id = Some("f1".into());
        e.failure_class = Some(FailureClass::AutonomouslyRecovered);
        let e = log.emit(EventType::Failure);
        e.failure_id = Some("f2".into());
        e.failure_class = Some(FailureClass::AutonomouslyRecovered);
        log.emit(EventType::RunEnd);

        let result = compute_arr(log.events());
        assert_eq!(result.arr, Some(1.0));
    }

    #[test]
    fn partial_recovery() {
        let mut log = EventLog::new("t", "W1-A");
        log.emit(EventType::RunStart);
        let e = log.emit(EventType::Failure);
        e.failure_class = Some(FailureClass::AutonomouslyRecovered);
        let e = log.emit(EventType::Failure);
        e.failure_class = Some(FailureClass::RecoverableNotRecovered);
        log.emit(EventType::RunEnd);

        let result = compute_arr(log.events());
        assert_eq!(result.arr, Some(0.5));
    }

    #[test]
    fn no_failures_na() {
        let mut log = EventLog::new("t", "W1-A");
        log.emit(EventType::RunStart);
        log.emit(EventType::RunEnd);
        let result = compute_arr(log.events());
        assert!(result.arr.is_none());
    }
}
