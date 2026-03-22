use serde::{Deserialize, Serialize};
use std::collections::BTreeMap;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ProxyValues {
    pub gds: Option<f64>,
    pub arr: Option<f64>,
    pub ist: Option<f64>,
    pub rec: Option<f64>,
    pub cfr: Option<f64>,
    pub sri: Option<f64>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ProxyEvidence {
    pub stress_levels: Vec<f64>,
    pub completion_rates: Vec<f64>,
    #[serde(rename = "Fr")]
    pub fr: i64,
    #[serde(rename = "Fa")]
    pub fa: i64,
    pub isolation_duration: Option<f64>,
    pub survival_time: Option<f64>,
    #[serde(rename = "E_base")]
    pub e_base: Option<f64>,
    #[serde(rename = "E_stress")]
    pub e_stress: Option<f64>,
    #[serde(rename = "C_total")]
    pub c_total: Option<i64>,
    #[serde(rename = "C_local")]
    pub c_local: Option<i64>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RunRecord {
    pub run_id: String,
    pub workload_id: String,
    pub seeds: crate::types::config::StressSeeds,
    pub start_utc: f64,
    pub end_utc: f64,
    pub proxies: ProxyValues,
    pub evidence: ProxyEvidence,
    pub na_reasons: BTreeMap<String, String>,
    pub events: Vec<crate::types::events::Event>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AggregateStats {
    pub mean: Option<f64>,
    pub std: Option<f64>,
    pub ci95_low: Option<f64>,
    pub ci95_high: Option<f64>,
    pub n_included: usize,
    pub n_na: usize,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AggregateSummary {
    pub gds: AggregateStats,
    pub arr: AggregateStats,
    pub ist: AggregateStats,
    pub rec: AggregateStats,
    pub cfr: AggregateStats,
    pub sri: AggregateStats,
}
