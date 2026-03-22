use clap::Parser;
use std::collections::BTreeMap;

use stress_ref::runner::{run_benchmark, BenchmarkConfig};

#[derive(Parser)]
#[command(name = "stress")]
#[command(about = "STRESS v0.2 — System Threat Resilience & Extreme Stress Suite")]
#[command(version)]
struct Cli {
    /// Output directory for reports
    #[arg(long, default_value = "report")]
    out_dir: String,

    /// Workload ID (W1-A, W2-A, W3-A)
    #[arg(long, default_value = "W1-A")]
    workload: String,

    /// Stress profile (SP-0, SP-1, SP-2)
    #[arg(long, default_value = "SP-1")]
    profile: String,

    /// Master seed for reproducibility
    #[arg(long, default_value = "42")]
    seed: u64,

    /// Number of independent runs
    #[arg(long, default_value = "10")]
    runs: usize,

    /// GDS stress levels (comma-separated)
    #[arg(long, default_value = "0.1,0.2,0.3")]
    gds_levels: String,

    /// Declared isolation duration (seconds)
    #[arg(long)]
    isolation_duration: Option<f64>,

    /// Total components for CFR
    #[arg(long)]
    c_total: Option<i64>,
}

fn main() {
    tracing_subscriber::fmt::init();
    let cli = Cli::parse();

    let stress_parameters = match cli.profile.as_str() {
        "SP-0" => stress_ref::stress::profiles::sp0(),
        "SP-1" => stress_ref::stress::profiles::sp1(),
        "SP-2" => stress_ref::stress::profiles::sp2(),
        other => {
            eprintln!("Unknown profile: {other}. Use SP-0, SP-1, or SP-2.");
            std::process::exit(1);
        }
    };

    let gds_levels: Vec<f64> = cli
        .gds_levels
        .split(',')
        .filter_map(|s| s.trim().parse().ok())
        .collect();

    let mut env = BTreeMap::new();
    env.insert("os".into(), std::env::consts::OS.into());
    env.insert("arch".into(), std::env::consts::ARCH.into());
    env.insert("runtime".into(), "rust".into());

    let config = BenchmarkConfig {
        out_dir: cli.out_dir,
        workload_id: cli.workload,
        workload_version: "0.1".into(),
        stress_profile_id: cli.profile,
        stress_parameters,
        execution_environment: env,
        master_seed: cli.seed,
        n_runs: cli.runs,
        gds_levels: Some(gds_levels),
        isolation_duration_declared: cli.isolation_duration,
        c_total: cli.c_total,
    };

    match run_benchmark(&config) {
        Ok(()) => println!("Benchmark complete. Results in {}", config.out_dir),
        Err(e) => {
            eprintln!("Benchmark failed: {e}");
            std::process::exit(1);
        }
    }
}
