use std::collections::BTreeMap;

use crate::stress::isolation::IsolationStressor;
use crate::stress::network::NetworkStressor;
use crate::stress::power::{PowerSchedule, PowerStressor};
use crate::stress::radiation::RadiationStressor;
use crate::stress::thermal::ThermalStressor;
use crate::types::config::StressSeeds;

/// Composite of all five stressors with a unified query interface.
pub struct StressRegime {
    pub radiation: RadiationStressor,
    pub thermal: ThermalStressor,
    pub power: PowerStressor,
    pub network: NetworkStressor,
    pub isolation: IsolationStressor,
}

impl StressRegime {
    pub fn start_all(&mut self, t: f64) {
        if self.radiation.enabled() { self.radiation.start(t); }
        if self.thermal.enabled() { self.thermal.start(t); }
        if self.power.enabled() { self.power.start(t); }
        if self.network.enabled() { self.network.start(t); }
        if self.isolation.enabled() { self.isolation.start(t); }
    }

    pub fn stop_all(&mut self) {
        self.radiation.stop();
        self.thermal.stop();
        self.power.stop();
        self.network.stop();
        self.isolation.stop();
    }

    /// Apply SP-2 thermal multiplier to SP-1 radiation fault rate.
    pub fn update_thermal_coupling(&mut self, t: f64) {
        let m = self.thermal.get_thermal_multiplier(t);
        self.radiation.set_fault_multiplier(m);
    }

    pub fn should_inject_fault(&mut self, t: f64) -> bool {
        self.update_thermal_coupling(t);
        self.radiation.should_inject_fault(t)
    }

    pub fn is_available(&mut self, t: f64, total_duration: f64) -> bool {
        self.power.is_available(t, total_duration)
    }

    pub fn is_isolated(&self, t: f64) -> bool {
        self.isolation.is_isolated(t)
    }

    pub fn get_network_latency_ms(&mut self, t: f64) -> f64 {
        self.network.get_latency_ms(t)
    }

    pub fn is_packet_lost(&mut self, t: f64) -> bool {
        self.network.is_packet_lost(t)
    }
}

fn get_f64(params: &BTreeMap<String, f64>, key: &str, default: f64) -> f64 {
    params.get(key).copied().unwrap_or(default)
}

pub fn create_regime(
    seeds: &StressSeeds,
    params: &BTreeMap<String, BTreeMap<String, f64>>,
) -> StressRegime {
    let sp1 = params.get("SP-1").or_else(|| params.get("SR-1"));
    let sp2 = params.get("SP-2").or_else(|| params.get("SR-2"));
    let sp3 = params.get("SP-3").or_else(|| params.get("SR-3"));
    let sp4 = params.get("SP-4").or_else(|| params.get("SR-4"));
    let sp5 = params.get("SP-5").or_else(|| params.get("SR-5"));

    let empty = BTreeMap::new();

    StressRegime {
        radiation: RadiationStressor::new(
            sp1.is_some(),
            seeds.sr1,
            get_f64(sp1.unwrap_or(&empty), "rate", 0.001),
        ),
        thermal: ThermalStressor::new(
            sp2.is_some(),
            seeds.sr2,
            get_f64(sp2.unwrap_or(&empty), "cycle_period_s", 600.0),
            get_f64(sp2.unwrap_or(&empty), "amplitude", 3.0),
        ),
        power: PowerStressor::new(
            sp3.is_some(),
            seeds.sr3,
            get_f64(sp3.unwrap_or(&empty), "availability_pct", 80.0),
            get_f64(sp3.unwrap_or(&empty), "interruption_duration_s", 5.0),
            if sp3.map_or(false, |p| p.get("schedule").copied() == Some(1.0)) {
                PowerSchedule::Stochastic
            } else {
                PowerSchedule::Periodic
            },
        ),
        network: NetworkStressor::new(
            sp4.is_some(),
            seeds.sr4,
            get_f64(sp4.unwrap_or(&empty), "baseline_latency_ms", 50.0),
            get_f64(sp4.unwrap_or(&empty), "jitter_pct", 50.0),
            get_f64(sp4.unwrap_or(&empty), "packet_loss_probability", 0.05),
        ),
        isolation: IsolationStressor::new(
            sp5.is_some(),
            seeds.sr5,
            get_f64(sp5.unwrap_or(&empty), "max_duration_s", 120.0),
            get_f64(sp5.unwrap_or(&empty), "trigger_offset_s", 10.0),
        ),
    }
}

pub fn create_baseline_regime(seeds: &StressSeeds) -> StressRegime {
    create_regime(seeds, &BTreeMap::new())
}
