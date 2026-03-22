/// SP-5: Isolation Duration — binary external disconnection window.
pub struct IsolationStressor {
    enabled: bool,
    max_duration_s: f64,
    trigger_offset_s: f64,
    active: bool,
    start_time: Option<f64>,
}

impl IsolationStressor {
    pub fn new(enabled: bool, _seed: u64, max_duration_s: f64, trigger_offset_s: f64) -> Self {
        Self {
            enabled,
            max_duration_s,
            trigger_offset_s,
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

    pub fn trigger_offset_s(&self) -> f64 {
        self.trigger_offset_s
    }

    pub fn max_duration_s(&self) -> f64 {
        self.max_duration_s
    }

    pub fn is_isolated(&self, t: f64) -> bool {
        if !self.active || !self.enabled {
            return false;
        }
        let elapsed = t - self.start_time.unwrap_or(t);
        elapsed >= self.trigger_offset_s
            && elapsed < self.trigger_offset_s + self.max_duration_s
    }
}
