use sha2::{Digest, Sha256};
use std::time::Instant;

#[derive(Debug, Clone)]
pub struct W1aResult {
    pub tasks_total: u64,
    pub tasks_completed: u64,
    pub work_done: u64,
    pub duration_s: f64,
}

/// Deterministic CPU-bound work using SHA256 chain.
fn cpu_work(units: u64, seed: u64) -> u64 {
    let mut h = Sha256::digest(seed.to_le_bytes());
    let mut acc: u64 = 0;
    for i in 0..units {
        let mut hasher = Sha256::new();
        hasher.update(&h);
        hasher.update(&i.to_le_bytes());
        h = hasher.finalize();
        acc ^= u64::from_le_bytes(h[..8].try_into().unwrap());
    }
    acc
}

/// W1-A: Stateless independent task processing.
pub fn run_w1a(tasks: u64, work_units_per_task: u64, seed: u64) -> W1aResult {
    let start = Instant::now();
    let mut completed = 0u64;

    for i in 0..tasks {
        let sub_seed = seed.wrapping_mul(1_000_003).wrapping_add(i);
        let _ = cpu_work(work_units_per_task, sub_seed);
        completed += 1;
    }

    W1aResult {
        tasks_total: tasks,
        tasks_completed: completed,
        work_done: completed,
        duration_s: start.elapsed().as_secs_f64(),
    }
}
