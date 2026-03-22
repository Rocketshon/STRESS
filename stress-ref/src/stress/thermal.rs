use std::f64::consts::PI;

/// SP-2: Thermal Cycling — deterministic periodic multiplier on SP-1 fault rate.
pub struct ThermalStressor {
    enabled: bool,
    cycle_period_s: f64,
    amplitude: f64,
    active: bool,
    start_time: Option<f64>,
}

impl ThermalStressor {
    pub fn new(enabled: bool, _seed: u64, cycle_period_s: f64, amplitude: f64) -> Self {
        Self {
            enabled,
            cycle_period_s,
            amplitude: amplitude.max(1.0), // Thermal stress can only increase fault rate
            active: false,
            start_time: None,
        }
    }

    pub fn start(&mut self, t: f64) {
        self.active = true;
        self.start_time = Some(t);
    }

    pub fn stop(&mut self) {
        self.active = false;
    }

    pub fn enabled(&self) -> bool {
        self.enabled
    }

    /// Returns thermal multiplier >= 1.0 following sinusoidal curve.
    pub fn get_thermal_multiplier(&self, t: f64) -> f64 {
        if !self.active || !self.enabled {
            return 1.0;
        }
        let elapsed = t - self.start_time.unwrap_or(t);
        let phase = 2.0 * PI * elapsed / self.cycle_period_s;
        1.0 + (self.amplitude - 1.0) * (0.5 + 0.5 * phase.sin())
    }
}
