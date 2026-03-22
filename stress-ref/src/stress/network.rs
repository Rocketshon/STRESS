use rand::Rng;
use rand::SeedableRng;
use rand_chacha::ChaCha8Rng;

/// SP-4: Network Jitter — latency variance + packet loss.
pub struct NetworkStressor {
    enabled: bool,
    baseline_latency_ms: f64,
    jitter_pct: f64,
    packet_loss_probability: f64,
    rng: ChaCha8Rng,
    active: bool,
}

impl NetworkStressor {
    pub fn new(
        enabled: bool,
        seed: u64,
        baseline_latency_ms: f64,
        jitter_pct: f64,
        packet_loss_probability: f64,
    ) -> Self {
        Self {
            enabled,
            baseline_latency_ms,
            jitter_pct,
            packet_loss_probability,
            rng: ChaCha8Rng::seed_from_u64(seed),
            active: false,
        }
    }

    pub fn start(&mut self, _t: f64) {
        self.active = true;
    }

    pub fn stop(&mut self) {
        self.active = false;
    }

    pub fn enabled(&self) -> bool {
        self.enabled
    }

    pub fn get_latency_ms(&mut self, _t: f64) -> f64 {
        if !self.active || !self.enabled {
            return 0.0;
        }
        let jitter_std = self.baseline_latency_ms * (self.jitter_pct / 100.0);
        // Box-Muller transform for normal distribution
        let u1: f64 = self.rng.gen::<f64>().max(1e-10);
        let u2: f64 = self.rng.gen();
        let z = (-2.0 * u1.ln()).sqrt() * (2.0 * std::f64::consts::PI * u2).cos();
        let latency = self.baseline_latency_ms + jitter_std * z;
        latency.clamp(0.0, 2.0 * self.baseline_latency_ms)
    }

    pub fn is_packet_lost(&mut self, _t: f64) -> bool {
        if !self.active || !self.enabled {
            return false;
        }
        self.rng.gen::<f64>() < self.packet_loss_probability
    }
}
