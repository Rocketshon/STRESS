use std::fs;
use std::path::{Path, PathBuf};
use std::time::Instant;

#[derive(Debug, Clone)]
pub struct W2aConfig {
    pub stages: u64,
    pub checkpoint_every: u64,
    pub max_restarts: u64,
    pub external_grace_failures: u64,
    pub stage_work_us: u64,
}

impl Default for W2aConfig {
    fn default() -> Self {
        Self {
            stages: 50,
            checkpoint_every: 5,
            max_restarts: 10,
            external_grace_failures: 10,
            stage_work_us: 50,
        }
    }
}

#[derive(Debug, Clone)]
pub struct W2aResult {
    pub stages_total: u64,
    pub stages_completed: u64,
    pub restarts: u64,
    pub duration_s: f64,
    pub failed: bool,
}

fn load_checkpoint(path: &Path) -> Result<u64, String> {
    if !path.exists() {
        return Ok(0);
    }
    let content = fs::read_to_string(path).map_err(|e| e.to_string())?;
    let val: serde_json::Value =
        serde_json::from_str(&content).map_err(|e| e.to_string())?;
    Ok(val["next_stage"].as_u64().unwrap_or(0))
}

fn save_checkpoint(path: &Path, next_stage: u64) -> Result<(), String> {
    let tmp = path.with_extension("tmp");
    let content = format!(r#"{{"next_stage":{next_stage}}}"#);
    fs::write(&tmp, &content).map_err(|e| e.to_string())?;
    fs::rename(&tmp, path).map_err(|e| e.to_string())?;
    Ok(())
}

/// W2-A: Stateful pipeline with checkpointing.
pub fn run_w2a<F, C>(
    run_dir: &str,
    _seed: u64,
    cfg: &W2aConfig,
    mut external_call: F,
    mut should_crash: C,
) -> W2aResult
where
    F: FnMut() -> Result<(), String>,
    C: FnMut(u64) -> bool,
{
    let rd = PathBuf::from(run_dir);
    fs::create_dir_all(&rd).ok();
    let ckpt = rd.join("checkpoint.json");

    // Clear stale checkpoints
    if ckpt.exists() {
        fs::remove_file(&ckpt).ok();
    }

    let start = Instant::now();
    let mut restarts = 0u64;
    let mut stages_completed = 0u64;
    let mut next_stage = 0u64;
    let mut consecutive_ext_failures = 0u64;

    loop {
        let mut crashed = false;
        let mut terminal = false;

        for stage in next_stage..cfg.stages {
            if should_crash(stage) {
                crashed = true;
                break;
            }

            // External dependency
            if let Err(_) = external_call() {
                consecutive_ext_failures += 1;
                if consecutive_ext_failures >= cfg.external_grace_failures {
                    terminal = true;
                    break;
                }
            } else {
                consecutive_ext_failures = 0;
            }

            // Simulate work
            std::thread::sleep(std::time::Duration::from_micros(cfg.stage_work_us));

            stages_completed = stage + 1;
            if stages_completed % cfg.checkpoint_every == 0 {
                let _ = save_checkpoint(&ckpt, stages_completed);
            }
        }

        if terminal {
            return W2aResult {
                stages_total: cfg.stages,
                stages_completed,
                restarts,
                duration_s: start.elapsed().as_secs_f64(),
                failed: true,
            };
        }

        if crashed && restarts < cfg.max_restarts {
            restarts += 1;
            next_stage = load_checkpoint(&ckpt).unwrap_or(0);
            continue;
        }

        if crashed {
            return W2aResult {
                stages_total: cfg.stages,
                stages_completed,
                restarts,
                duration_s: start.elapsed().as_secs_f64(),
                failed: true,
            };
        }

        // Completed all stages
        let _ = save_checkpoint(&ckpt, cfg.stages);
        return W2aResult {
            stages_total: cfg.stages,
            stages_completed: cfg.stages,
            restarts,
            duration_s: start.elapsed().as_secs_f64(),
            failed: false,
        };
    }
}
