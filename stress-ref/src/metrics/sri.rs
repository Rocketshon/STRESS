use std::collections::BTreeMap;

#[derive(Debug, Clone)]
pub struct SriResult {
    pub sri: Option<f64>,
    pub na_reason: Option<String>,
}

/// SRI = (sum of proxies / 5) * 100, on [0, 100] scale per spec v0.2.
/// N/A if any proxy is N/A.
pub fn compute_sri(proxies: &BTreeMap<&str, Option<f64>>) -> SriResult {
    let required = ["gds", "arr", "ist", "rec", "cfr"];

    let missing: Vec<&&str> = required
        .iter()
        .filter(|k| !proxies.contains_key(*k))
        .collect();
    if !missing.is_empty() {
        return SriResult {
            sri: None,
            na_reason: Some(format!("missing proxies: {missing:?}")),
        };
    }

    let na: Vec<&&str> = required
        .iter()
        .filter(|k| proxies.get(*k).copied().flatten().is_none())
        .collect();
    if !na.is_empty() {
        return SriResult {
            sri: None,
            na_reason: Some(format!("SRI N/A because proxies N/A: {na:?}")),
        };
    }

    let sum: f64 = required
        .iter()
        .map(|k| proxies.get(k).unwrap().unwrap())
        .sum();

    let sri = ((sum / 5.0) * 100.0).clamp(0.0, 100.0);

    SriResult {
        sri: Some(sri),
        na_reason: None,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn perfect_sri() {
        let mut proxies = BTreeMap::new();
        for k in &["gds", "arr", "ist", "rec", "cfr"] {
            proxies.insert(*k, Some(1.0));
        }
        let result = compute_sri(&proxies);
        assert_eq!(result.sri, Some(100.0));
    }

    #[test]
    fn partial_na() {
        let mut proxies = BTreeMap::new();
        proxies.insert("gds", Some(1.0));
        proxies.insert("arr", None);
        proxies.insert("ist", Some(1.0));
        proxies.insert("rec", Some(1.0));
        proxies.insert("cfr", Some(1.0));
        let result = compute_sri(&proxies);
        assert!(result.sri.is_none());
    }

    #[test]
    fn weighted_average() {
        let mut proxies = BTreeMap::new();
        proxies.insert("gds", Some(0.8));
        proxies.insert("arr", Some(0.6));
        proxies.insert("ist", Some(1.0));
        proxies.insert("rec", Some(0.4));
        proxies.insert("cfr", Some(0.2));
        let result = compute_sri(&proxies);
        let expected = ((0.8 + 0.6 + 1.0 + 0.4 + 0.2) / 5.0) * 100.0;
        assert!((result.sri.unwrap() - expected).abs() < 0.1);
    }
}
