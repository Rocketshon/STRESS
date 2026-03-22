use crate::types::events::Event;

#[derive(Debug, Clone)]
pub struct GdsResult {
    pub gds: Option<f64>,
    pub n_levels: usize,
    pub stress_levels: Vec<f64>,
    pub completion_rates: Vec<f64>,
    pub na_reason: Option<String>,
}

/// BP-1: Graceful Degradation Score.
/// GDS = (1/n) * sum(C_i) where C_i is completion rate at stress level i.
pub fn compute_gds(events: &[Event], expected_levels: Option<&[f64]>) -> GdsResult {
    let mut levels = Vec::new();
    let mut rates = Vec::new();

    for e in events {
        if let (Some(sl), Some(cr)) = (e.stress_level, e.completion_rate) {
            levels.push(sl);
            rates.push(cr);
        }
    }

    if levels.is_empty() {
        return GdsResult {
            gds: None, n_levels: 0,
            stress_levels: vec![], completion_rates: vec![],
            na_reason: Some("No (stress_level, completion_rate) evidence found".to_string()),
        };
    }

    for &r in &rates {
        if !(0.0..=1.0).contains(&r) {
            return GdsResult {
                gds: None, n_levels: levels.len(),
                stress_levels: levels, completion_rates: rates,
                na_reason: Some(format!("completion_rate out of bounds: {r}")),
            };
        }
    }

    // Tolerance-based expected level enforcement
    if let Some(expected) = expected_levels {
        let missing: Vec<f64> = expected
            .iter()
            .filter(|&&exp| !levels.iter().any(|&got| (exp - got).abs() < 1e-9))
            .copied()
            .collect();
        if !missing.is_empty() {
            return GdsResult {
                gds: None, n_levels: levels.len(),
                stress_levels: levels, completion_rates: rates,
                na_reason: Some(format!("Missing declared stress levels: {missing:?}")),
            };
        }
    }

    let n = rates.len() as f64;
    let gds = (rates.iter().sum::<f64>() / n).clamp(0.0, 1.0);

    // Sort by stress level for disclosure
    let mut paired: Vec<(f64, f64)> = levels.into_iter().zip(rates).collect();
    paired.sort_by(|a, b| a.0.partial_cmp(&b.0).unwrap_or(std::cmp::Ordering::Equal));

    GdsResult {
        gds: Some(gds),
        n_levels: paired.len(),
        stress_levels: paired.iter().map(|p| p.0).collect(),
        completion_rates: paired.iter().map(|p| p.1).collect(),
        na_reason: None,
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::types::events::{EventLog, EventType};

    #[test]
    fn perfect_gds() {
        let mut log = EventLog::new("t", "W1-A");
        log.emit(EventType::RunStart);
        for &level in &[0.1, 0.2, 0.3] {
            let e = log.emit(EventType::WorkUnitEnd);
            e.stress_level = Some(level);
            e.completion_rate = Some(1.0);
        }
        log.emit(EventType::RunEnd);

        let result = compute_gds(log.events(), Some(&[0.1, 0.2, 0.3]));
        assert_eq!(result.gds, Some(1.0));
    }

    #[test]
    fn degrading_gds() {
        let mut log = EventLog::new("t", "W1-A");
        log.emit(EventType::RunStart);
        for (&level, &rate) in [0.1, 0.2, 0.3].iter().zip(&[1.0, 0.5, 0.0]) {
            let e = log.emit(EventType::WorkUnitEnd);
            e.stress_level = Some(level);
            e.completion_rate = Some(rate);
        }
        log.emit(EventType::RunEnd);

        let result = compute_gds(log.events(), Some(&[0.1, 0.2, 0.3]));
        assert!((result.gds.unwrap() - 0.5).abs() < 0.01);
    }

    #[test]
    fn no_evidence_na() {
        let mut log = EventLog::new("t", "W1-A");
        log.emit(EventType::RunStart);
        log.emit(EventType::RunEnd);
        let result = compute_gds(log.events(), None);
        assert!(result.gds.is_none());
    }
}
