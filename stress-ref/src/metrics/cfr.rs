use std::collections::BTreeSet;

use crate::types::events::{Event, EventType};

#[derive(Debug, Clone)]
pub struct CfrResult {
    pub cfr: Option<f64>,
    pub c_total: Option<i64>,
    pub c_local: Option<i64>,
    pub na_reason: Option<String>,
}

/// BP-5: Cascading Failure Resistance. CFR = 1 - (C_local / C_total).
pub fn compute_cfr(events: &[Event], c_total: Option<i64>) -> CfrResult {
    let c_total = match c_total {
        Some(c) if c > 1 => c,
        Some(c) if c <= 1 => {
            return CfrResult {
                cfr: None, c_total: Some(c), c_local: None,
                na_reason: Some("C_total <= 1; CFR not applicable".to_string()),
            }
        }
        _ => {
            return CfrResult {
                cfr: None, c_total: None, c_local: None,
                na_reason: Some("C_total not declared".to_string()),
            }
        }
    };

    let mut affected = BTreeSet::new();
    for e in events {
        if e.event_type == EventType::ComponentAffected || e.event_type == EventType::Failure {
            if let Some(ref cid) = e.component_id {
                affected.insert(cid.clone());
            }
        }
    }

    if affected.is_empty() {
        return CfrResult {
            cfr: None, c_total: Some(c_total), c_local: Some(0),
            na_reason: Some("No affected components recorded".to_string()),
        };
    }

    let c_local = affected.len() as i64;
    if c_local > c_total {
        return CfrResult {
            cfr: None,
            c_total: Some(c_total),
            c_local: Some(c_local),
            na_reason: Some(format!("C_local ({c_local}) > C_total ({c_total}); invalid")),
        };
    }

    let cfr = (1.0 - (c_local as f64 / c_total as f64)).clamp(0.0, 1.0);

    CfrResult {
        cfr: Some(cfr),
        c_total: Some(c_total),
        c_local: Some(c_local),
        na_reason: None,
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::types::events::{EventLog, EventType};

    #[test]
    fn perfect_containment() {
        let mut log = EventLog::new("t", "W3-A");
        log.emit(EventType::RunStart);
        let e = log.emit(EventType::ComponentAffected);
        e.component_id = Some("node-1".into());
        log.emit(EventType::RunEnd);

        let result = compute_cfr(log.events(), Some(5));
        assert_eq!(result.cfr, Some(0.8)); // 1 - 1/5 = 0.8
    }

    #[test]
    fn total_cascade() {
        let mut log = EventLog::new("t", "W3-A");
        log.emit(EventType::RunStart);
        for i in 0..5 {
            let e = log.emit(EventType::ComponentAffected);
            e.component_id = Some(format!("node-{i}"));
        }
        log.emit(EventType::RunEnd);

        let result = compute_cfr(log.events(), Some(5));
        assert_eq!(result.cfr, Some(0.0)); // 1 - 5/5 = 0.0
    }

    #[test]
    fn no_components_na() {
        let mut log = EventLog::new("t", "W3-A");
        log.emit(EventType::RunStart);
        log.emit(EventType::RunEnd);

        let result = compute_cfr(log.events(), Some(5));
        assert!(result.cfr.is_none());
    }

    #[test]
    fn single_component_na() {
        let mut log = EventLog::new("t", "W1-A");
        log.emit(EventType::RunStart);
        log.emit(EventType::RunEnd);

        let result = compute_cfr(log.events(), Some(1));
        assert!(result.cfr.is_none());
    }

    #[test]
    fn duplicate_components_counted_once() {
        let mut log = EventLog::new("t", "W3-A");
        log.emit(EventType::RunStart);
        let e = log.emit(EventType::ComponentAffected);
        e.component_id = Some("node-1".into());
        let e = log.emit(EventType::ComponentAffected);
        e.component_id = Some("node-1".into()); // duplicate
        log.emit(EventType::RunEnd);

        let result = compute_cfr(log.events(), Some(5));
        assert_eq!(result.cfr, Some(0.8)); // Still 1 unique
    }
}
