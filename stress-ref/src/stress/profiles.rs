use std::collections::BTreeMap;

pub fn sp0() -> BTreeMap<String, BTreeMap<String, f64>> {
    BTreeMap::new()
}

pub fn sp1() -> BTreeMap<String, BTreeMap<String, f64>> {
    let mut params = BTreeMap::new();
    params.insert("SP-1".into(), [("rate".into(), 0.001)].into_iter().collect());
    params.insert("SP-2".into(), [("cycle_period_s".into(), 600.0), ("amplitude".into(), 2.0)].into_iter().collect());
    params.insert("SP-3".into(), [("availability_pct".into(), 90.0), ("interruption_duration_s".into(), 3.0)].into_iter().collect());
    params.insert("SP-4".into(), [("baseline_latency_ms".into(), 50.0), ("jitter_pct".into(), 30.0), ("packet_loss_probability".into(), 0.02)].into_iter().collect());
    params.insert("SP-5".into(), [("max_duration_s".into(), 60.0), ("trigger_offset_s".into(), 30.0)].into_iter().collect());
    params
}

pub fn sp2() -> BTreeMap<String, BTreeMap<String, f64>> {
    let mut params = BTreeMap::new();
    params.insert("SP-1".into(), [("rate".into(), 0.01)].into_iter().collect());
    params.insert("SP-2".into(), [("cycle_period_s".into(), 300.0), ("amplitude".into(), 5.0)].into_iter().collect());
    params.insert("SP-3".into(), [("availability_pct".into(), 60.0), ("interruption_duration_s".into(), 10.0), ("schedule".into(), 1.0)].into_iter().collect());
    params.insert("SP-4".into(), [("baseline_latency_ms".into(), 200.0), ("jitter_pct".into(), 80.0), ("packet_loss_probability".into(), 0.15)].into_iter().collect());
    params.insert("SP-5".into(), [("max_duration_s".into(), 120.0), ("trigger_offset_s".into(), 15.0)].into_iter().collect());
    params
}
