use crate::types::report::AggregateStats;

/// Compute mean, sample std dev, and 95% CI over included values.
/// N/A values are excluded but counted. CI reported without clamping.
pub fn summarize(values: &[Option<f64>]) -> AggregateStats {
    let included: Vec<f64> = values.iter().filter_map(|v| *v).collect();
    let n_na = values.iter().filter(|v| v.is_none()).count();

    if included.is_empty() {
        return AggregateStats {
            mean: None, std: None, ci95_low: None, ci95_high: None,
            n_included: 0, n_na,
        };
    }

    let n = included.len();
    let mean = included.iter().sum::<f64>() / n as f64;

    if n == 1 {
        return AggregateStats {
            mean: Some(mean), std: Some(0.0),
            ci95_low: Some(mean), ci95_high: Some(mean),
            n_included: 1, n_na,
        };
    }

    let var = included.iter().map(|x| (x - mean).powi(2)).sum::<f64>() / (n - 1) as f64;
    let std = var.sqrt();
    let se = std / (n as f64).sqrt();
    let z = 1.96;

    AggregateStats {
        mean: Some(mean),
        std: Some(std),
        ci95_low: Some(mean - z * se),
        ci95_high: Some(mean + z * se),
        n_included: n,
        n_na,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn basic_stats() {
        let result = summarize(&[Some(0.5), Some(0.5), Some(0.5)]);
        assert_eq!(result.mean, Some(0.5));
        assert_eq!(result.std, Some(0.0));
        assert_eq!(result.n_included, 3);
    }

    #[test]
    fn all_na() {
        let result = summarize(&[None, None]);
        assert!(result.mean.is_none());
        assert_eq!(result.n_na, 2);
    }

    #[test]
    fn mixed() {
        let result = summarize(&[Some(1.0), None, Some(0.5)]);
        assert_eq!(result.n_included, 2);
        assert_eq!(result.n_na, 1);
        assert!((result.mean.unwrap() - 0.75).abs() < 0.01);
    }
}
