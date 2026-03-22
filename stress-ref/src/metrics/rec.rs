use crate::types::events::Event;

#[derive(Debug, Clone)]
pub struct RecResult {
    pub rec: Option<f64>,
    pub e_base: Option<f64>,
    pub e_stress: Option<f64>,
    pub na_reason: Option<String>,
}

fn sum_work_and_resources(events: &[Event]) -> (f64, f64) {
    let mut work = 0.0;
    let mut resources = 0.0;
    for e in events {
        if let Some(w) = e.work_done {
            work += w;
        }
        if let Some(r) = e.resources_used {
            resources += r;
        }
    }
    (work, resources)
}

/// BP-4: Resource Efficiency Under Constraint.
/// E = work / resources. REC = min(E_stress / E_base, 1.0).
pub fn compute_rec(baseline_events: &[Event], stressed_events: &[Event]) -> RecResult {
    let (work_b, res_b) = sum_work_and_resources(baseline_events);
    let (work_s, res_s) = sum_work_and_resources(stressed_events);

    if res_b <= 0.0 {
        return RecResult {
            rec: None, e_base: None, e_stress: None,
            na_reason: Some("Baseline resources_used is zero".to_string()),
        };
    }

    let e_base = work_b / res_b;
    if e_base <= 0.0 {
        return RecResult {
            rec: None, e_base: None, e_stress: None,
            na_reason: Some("Baseline efficiency is zero".to_string()),
        };
    }

    if res_s <= 0.0 {
        return RecResult {
            rec: None, e_base: Some(e_base), e_stress: None,
            na_reason: Some("Stressed resources_used is zero".to_string()),
        };
    }

    let e_stress = work_s / res_s;
    let rec = (e_stress / e_base).clamp(0.0, 1.0);

    RecResult {
        rec: Some(rec),
        e_base: Some(e_base),
        e_stress: Some(e_stress),
        na_reason: None,
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::types::events::{EventLog, EventType};

    #[test]
    fn equal_efficiency() {
        let mut base = EventLog::new("b", "W1-A");
        base.emit(EventType::RunStart);
        let e = base.emit(EventType::WorkUnitEnd);
        e.work_done = Some(100.0);
        e.resources_used = Some(50.0);
        base.emit(EventType::RunEnd);

        let mut stressed = EventLog::new("s", "W1-A");
        stressed.emit(EventType::RunStart);
        let e = stressed.emit(EventType::WorkUnitEnd);
        e.work_done = Some(100.0);
        e.resources_used = Some(50.0);
        stressed.emit(EventType::RunEnd);

        let result = compute_rec(base.events(), stressed.events());
        assert_eq!(result.rec, Some(1.0));
    }

    #[test]
    fn degraded_efficiency() {
        let mut base = EventLog::new("b", "W1-A");
        base.emit(EventType::RunStart);
        let e = base.emit(EventType::WorkUnitEnd);
        e.work_done = Some(100.0);
        e.resources_used = Some(50.0);
        base.emit(EventType::RunEnd);

        let mut stressed = EventLog::new("s", "W1-A");
        stressed.emit(EventType::RunStart);
        let e = stressed.emit(EventType::WorkUnitEnd);
        e.work_done = Some(50.0);
        e.resources_used = Some(50.0);
        stressed.emit(EventType::RunEnd);

        let result = compute_rec(base.events(), stressed.events());
        assert_eq!(result.rec, Some(0.5));
    }

    #[test]
    fn zero_baseline_na() {
        let mut base = EventLog::new("b", "W1-A");
        base.emit(EventType::RunStart);
        base.emit(EventType::RunEnd);

        let mut stressed = EventLog::new("s", "W1-A");
        stressed.emit(EventType::RunStart);
        let e = stressed.emit(EventType::WorkUnitEnd);
        e.work_done = Some(50.0);
        e.resources_used = Some(50.0);
        stressed.emit(EventType::RunEnd);

        let result = compute_rec(base.events(), stressed.events());
        assert!(result.rec.is_none());
    }

    #[test]
    fn capped_at_one() {
        let mut base = EventLog::new("b", "W1-A");
        base.emit(EventType::RunStart);
        let e = base.emit(EventType::WorkUnitEnd);
        e.work_done = Some(50.0);
        e.resources_used = Some(50.0);
        base.emit(EventType::RunEnd);

        let mut stressed = EventLog::new("s", "W1-A");
        stressed.emit(EventType::RunStart);
        let e = stressed.emit(EventType::WorkUnitEnd);
        e.work_done = Some(200.0);
        e.resources_used = Some(50.0);
        stressed.emit(EventType::RunEnd);

        let result = compute_rec(base.events(), stressed.events());
        assert_eq!(result.rec, Some(1.0));
    }
}
