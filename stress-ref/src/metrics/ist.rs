use crate::types::events::{Event, EventType, FailureClass};

#[derive(Debug, Clone)]
pub struct IstResult {
    pub ist: Option<f64>,
    pub isolation_duration_declared: Option<f64>,
    pub survival_time_observed: Option<f64>,
    pub na_reason: Option<String>,
}

/// BP-3: Isolation Survival Time. IST = clamp(survival_time / declared_duration, 0, 1).
pub fn compute_ist(events: &[Event], isolation_duration_declared: Option<f64>) -> IstResult {
    let declared = match isolation_duration_declared {
        Some(d) if d > 0.0 => d,
        _ => {
            return IstResult {
                ist: None,
                isolation_duration_declared,
                survival_time_observed: None,
                na_reason: Some("Missing or invalid declared isolation duration".to_string()),
            }
        }
    };

    let iso_start = events
        .iter()
        .find(|e| e.event_type == EventType::IsolationStart)
        .map(|e| e.t_utc);

    let iso_start = match iso_start {
        Some(t) => t,
        None => {
            return IstResult {
                ist: None,
                isolation_duration_declared: Some(declared),
                survival_time_observed: None,
                na_reason: Some("No isolation_start event observed".to_string()),
            }
        }
    };

    let mut iso_end_time: Option<f64> = None;
    for e in events {
        if e.t_utc < iso_start {
            continue;
        }
        match e.event_type {
            EventType::IsolationEnd => {
                iso_end_time = Some(e.t_utc);
                break;
            }
            EventType::Failure if e.failure_class == Some(FailureClass::Irreversible) => {
                iso_end_time = Some(e.t_utc);
                break;
            }
            EventType::RunEnd => {
                iso_end_time = Some(e.t_utc);
                break;
            }
            _ => {}
        }
    }

    let end_time = match iso_end_time {
        Some(t) => t,
        None => {
            // No terminating event found — check if there are any events after iso_start
            let max_t = events.iter().map(|e| e.t_utc).fold(f64::NEG_INFINITY, f64::max);
            if max_t <= iso_start {
                // No observable events after isolation started — IST is undefined
                return IstResult {
                    ist: None,
                    isolation_duration_declared: Some(declared),
                    survival_time_observed: None,
                    na_reason: Some("No events observed after isolation start".to_string()),
                };
            }
            max_t
        }
    };

    let survival_time = (end_time - iso_start).max(0.0);
    let ist = (survival_time / declared).clamp(0.0, 1.0);

    IstResult {
        ist: Some(ist),
        isolation_duration_declared: Some(declared),
        survival_time_observed: Some(survival_time),
        na_reason: None,
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::types::events::EventLog;

    #[test]
    fn full_survival() {
        let mut log = EventLog::new("t", "W1-A");
        log.emit_at(EventType::RunStart, 1000.0);
        log.emit_at(EventType::IsolationStart, 1010.0);
        log.emit_at(EventType::IsolationEnd, 1070.0);
        log.emit_at(EventType::RunEnd, 1080.0);

        let result = compute_ist(log.events(), Some(60.0));
        assert_eq!(result.ist, Some(1.0));
        assert_eq!(result.survival_time_observed, Some(60.0));
    }

    #[test]
    fn partial_survival() {
        let mut log = EventLog::new("t", "W1-A");
        log.emit_at(EventType::RunStart, 1000.0);
        log.emit_at(EventType::IsolationStart, 1010.0);
        // Irreversible failure at 1040 — only 30s of 60s survived
        let e = log.emit_at(EventType::Failure, 1040.0);
        e.failure_class = Some(FailureClass::Irreversible);
        log.emit_at(EventType::RunEnd, 1080.0);

        let result = compute_ist(log.events(), Some(60.0));
        assert_eq!(result.ist, Some(0.5));
    }

    #[test]
    fn no_isolation_na() {
        let mut log = EventLog::new("t", "W1-A");
        log.emit_at(EventType::RunStart, 1000.0);
        log.emit_at(EventType::RunEnd, 1080.0);

        let result = compute_ist(log.events(), Some(60.0));
        assert!(result.ist.is_none());
    }

    #[test]
    fn no_declared_duration_na() {
        let mut log = EventLog::new("t", "W1-A");
        log.emit_at(EventType::RunStart, 1000.0);
        log.emit_at(EventType::IsolationStart, 1010.0);
        log.emit_at(EventType::RunEnd, 1080.0);

        let result = compute_ist(log.events(), None);
        assert!(result.ist.is_none());
    }
}
