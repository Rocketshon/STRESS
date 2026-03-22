use rand::Rng;
use serde::{Deserialize, Serialize};
use std::collections::BTreeMap;

pub const STRESS_VERSION: &str = "v0.2";

#[derive(Debug, Clone, Copy, Serialize, Deserialize)]
pub struct StressSeeds {
    pub sr1: u64,
    pub sr2: u64,
    pub sr3: u64,
    pub sr4: u64,
    pub sr5: u64,
}

impl StressSeeds {
    pub fn generate(master_seed: u64) -> Self {
        use rand::SeedableRng;
        let mut rng = rand_chacha::ChaCha8Rng::seed_from_u64(master_seed);
        Self {
            sr1: rng.gen(),
            sr2: rng.gen(),
            sr3: rng.gen(),
            sr4: rng.gen(),
            sr5: rng.gen(),
        }
    }

    /// Derive independent per-run seeds using prime offsets.
    pub fn derive_for_run(&self, run_index: u64) -> Self {
        Self {
            sr1: self.sr1.wrapping_add(run_index.wrapping_mul(7919)),
            sr2: self.sr2.wrapping_add(run_index.wrapping_mul(7927)),
            sr3: self.sr3.wrapping_add(run_index.wrapping_mul(7933)),
            sr4: self.sr4.wrapping_add(run_index.wrapping_mul(7937)),
            sr5: self.sr5.wrapping_add(run_index.wrapping_mul(7949)),
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RunManifest {
    pub stress_version: String,
    pub timestamp_utc: f64,
    pub workload_id: String,
    pub workload_version: String,
    pub stress_profile_id: String,
    pub stress_parameters: BTreeMap<String, BTreeMap<String, f64>>,
    pub seeds: StressSeeds,
    pub execution_environment: BTreeMap<String, String>,
}

pub fn create_manifest(
    workload_id: &str,
    workload_version: &str,
    stress_profile_id: &str,
    stress_parameters: BTreeMap<String, BTreeMap<String, f64>>,
    execution_environment: BTreeMap<String, String>,
    master_seed: u64,
) -> RunManifest {
    let now = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .unwrap()
        .as_secs_f64();

    RunManifest {
        stress_version: STRESS_VERSION.to_string(),
        timestamp_utc: now,
        workload_id: workload_id.to_string(),
        workload_version: workload_version.to_string(),
        stress_profile_id: stress_profile_id.to_string(),
        stress_parameters,
        seeds: StressSeeds::generate(master_seed),
        execution_environment,
    }
}
