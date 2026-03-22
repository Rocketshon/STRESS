use rand::Rng;
use rand::SeedableRng;
use rand_chacha::ChaCha8Rng;

/// SP-3: Power Disruption — intermittent availability windows.
pub struct PowerStressor {
    enabled: bool,
    availability_pct: f64,
    interruption_duration_s: f64,
    schedule: PowerSchedule,
    rng: ChaCha8Rng,
    active: bool,
    start_time: Option<f64>,
    interruption_starts: Vec<f64>,
    generated: bool,
}

#[derive(Debug, Clone, Copy)]
pub enum PowerSchedule {
    Periodic,
    Stochastic,
}

impl PowerStressor {
    pub fn new(
        enabled: bool,
        seed: u64,
        availability_pct: f64,
        interruption_duration_s: f64,
        schedule: PowerSchedule,
    ) -> Self {
        Self {
            enabled,
            availability_pct,
            interruption_duration_s,
            schedule,
            rng: ChaCha8Rng::seed_from_u64(seed),
            active: false,
            start_time: None,
            interruption_starts: Vec::new(),
            generated: false,
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

    fn ensure_generated(&mut self, duration: f64) {
        if self.generated {
            return;
        }
        self.generated = true;

        let avail_frac = self.availability_pct / 100.0;
        if avail_frac >= 1.0 {
            return;
        }

        match self.schedule {
            PowerSchedule::Periodic => {
                let cycle_time = self.interruption_duration_s / (1.0 - avail_frac);
                let available_time = cycle_time * avail_frac;
                let mut t = available_time;
                while t < duration {
                    self.interruption_starts.push(t);
                    t += cycle_time;
                }
            }
            PowerSchedule::Stochastic => {
                // Mean up-time (gap between interruptions) = avail * interrupt_dur / (1 - avail)
                let mean_gap = avail_frac * self.interruption_duration_s / (1.0 - avail_frac);
                // First interruption after initial up-time
                let mut t: f64 = -mean_gap * self.rng.gen::<f64>().max(1e-15).ln();
                while t < duration {
                    self.interruption_starts.push(t);
                    let next_gap: f64 = -mean_gap * self.rng.gen::<f64>().max(1e-15).ln();
                    t += self.interruption_duration_s + next_gap;
                }
            }
        }
    }

    pub fn is_available(&mut self, t: f64, total_duration: f64) -> bool {
        if !self.active || !self.enabled {
            return true;
        }
        self.ensure_generated(total_duration);
        let elapsed = t - self.start_time.unwrap_or(t);
        !self
            .interruption_starts
            .iter()
            .any(|&start| elapsed >= start && elapsed < start + self.interruption_duration_s)
    }
}
