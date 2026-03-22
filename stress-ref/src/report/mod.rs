use std::fs;
use std::path::Path;

use crate::types::config::RunManifest;
use crate::types::report::{AggregateSummary, RunRecord};

pub fn write_manifest(out_dir: &str, manifest: &RunManifest) -> std::io::Result<()> {
    let dir = Path::new(out_dir);
    fs::create_dir_all(dir)?;
    let json = serde_json::to_string_pretty(manifest)
        .map_err(|e| std::io::Error::new(std::io::ErrorKind::Other, e))?;
    fs::write(dir.join("manifest.json"), json)
}

pub fn write_run_record(out_dir: &str, index: usize, record: &RunRecord) -> std::io::Result<()> {
    let dir = Path::new(out_dir).join("runs");
    fs::create_dir_all(&dir)?;
    let json = serde_json::to_string_pretty(record)
        .map_err(|e| std::io::Error::new(std::io::ErrorKind::Other, e))?;
    fs::write(dir.join(format!("run_{index:02}.json")), json)
}

pub fn write_aggregate_summary(out_dir: &str, summary: &AggregateSummary) -> std::io::Result<()> {
    let json = serde_json::to_string_pretty(summary)
        .map_err(|e| std::io::Error::new(std::io::ErrorKind::Other, e))?;
    fs::write(Path::new(out_dir).join("aggregate_summary.json"), json)
}

pub fn write_disclosure(out_dir: &str, text: &str) -> std::io::Result<()> {
    fs::write(Path::new(out_dir).join("disclosure.md"), text)
}
