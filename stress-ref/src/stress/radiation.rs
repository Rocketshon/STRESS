use rand::Rng;
use rand::SeedableRng;
use rand_chacha::ChaCha8Rng;

/// SP-1: Radiation Pressure — probabilistic transient fault injection via Poisson process.
pub struct RadiationStressor {
    enabled: bool,
    seed: u64,
    fault_rate_per_second: f64,
    rng: ChaCha8Rng,
    last_check: Option<f64>,
    fault_multiplier: f64,
    active: bool,
}

impl RadiationStressor {
    pub fn new(enabled: bool, seed: u64, fault_rate_per_second: f64) -> Self {
        Self {
            enabled,
            seed,
            fault_rate_per_second,
            rng: ChaCha8Rng::seed_from_u64(seed),
            last_check: None,
            fault_multiplier: 1.0,
            active: false,
        }
    }

    pub fn start(&mut self, _t: f64) {
        self.active = true;
        self.last_check = None;
    }

    pub fn stop(&mut self) {
        self.active = false;
    }

    pub fn reset(&mut self) {
        self.rng = ChaCha8Rng::seed_from_u64(self.seed);
        self.last_check = None;
        self.fault_multiplier = 1.0;
        self.active = false;
    }

    pub fn set_fault_multiplier(&mut self, m: f64) {
        self.fault_multiplier = m;
    }

    pub fn effective_rate(&self) -> f64 {
        self.fault_rate_per_second * self.fault_multiplier
    }

    pub fn enabled(&self) -> bool {
        self.enabled
    }

    /// Returns true if a fault should be injected at time t.
    pub fn should_inject_fault(&mut self, t: f64) -> bool {
        if !self.active || !self.enabled {
            return false;
        }

        let dt = match self.last_check {
            Some(last) => (t - last).max(0.0),
            None => 0.01,
        };
        self.last_check = Some(t);

        if dt <= 0.0 {
            return false;
        }

        let rate = self.effective_rate();
        let p = 1.0 - (-rate * dt).exp();
        self.rng.gen::<f64>() < p
    }
}
