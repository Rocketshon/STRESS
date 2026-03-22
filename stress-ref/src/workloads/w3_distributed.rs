use std::collections::BTreeSet;
use std::time::Instant;

#[derive(Debug, Clone)]
pub struct W3aConfig {
    pub node_count: usize,
    pub heartbeat_interval_us: u64,
    pub max_rounds: usize,
}

impl Default for W3aConfig {
    fn default() -> Self {
        Self {
            node_count: 5,
            heartbeat_interval_us: 100,
            max_rounds: 20,
        }
    }
}

#[derive(Debug, Clone)]
pub struct W3aResult {
    pub nodes_total: usize,
    pub rounds_completed: usize,
    pub elections_successful: usize,
    pub elections_total: usize,
    pub safety_violations: usize,
    pub nodes_failed: Vec<usize>,
    pub duration_s: f64,
    pub work_done: f64,
}

/// W3-A: Distributed coordination — leader election via Bully algorithm.
pub fn run_w3a<K, I, L>(
    cfg: &W3aConfig,
    mut should_kill_node: K,
    mut is_isolated: I,
    mut is_packet_lost: L,
) -> W3aResult
where
    K: FnMut(usize, usize) -> bool,
    I: FnMut() -> bool,
    L: FnMut() -> bool,
{
    let start = Instant::now();
    let node_ids: Vec<usize> = (0..cfg.node_count).collect();
    let mut node_alive: Vec<bool> = vec![true; cfg.node_count];
    let mut node_leader: Vec<Option<usize>> = vec![None; cfg.node_count];
    let mut nodes_failed: Vec<usize> = Vec::new();
    let mut elections_total = 0usize;
    let mut elections_successful = 0usize;
    let mut safety_violations = 0usize;

    for round in 0..cfg.max_rounds {
        // Kill nodes
        for &nid in &node_ids {
            if node_alive[nid] && should_kill_node(nid, round) {
                node_alive[nid] = false;
                nodes_failed.push(nid);
            }
        }

        let alive: Vec<usize> = node_ids.iter().copied().filter(|&n| node_alive[n]).collect();
        if alive.is_empty() {
            break;
        }

        // Check if election needed
        let needs_election = alive.iter().any(|&n| {
            match node_leader[n] {
                None => true,
                Some(leader) => leader >= cfg.node_count || !node_alive[leader],
            }
        });

        if needs_election {
            elections_total += 1;
            let highest = *alive.last().unwrap();

            // Broadcast VICTORY (subject to isolation/loss)
            let isolated = is_isolated();
            for &nid in &alive {
                if isolated || is_packet_lost() {
                    node_leader[nid] = None;
                } else {
                    node_leader[nid] = Some(highest);
                }
            }

            // Check consensus
            let known_leaders: BTreeSet<usize> = alive
                .iter()
                .filter_map(|&n| node_leader[n])
                .collect();
            let nodes_with_leader = alive.iter().filter(|&&n| node_leader[n].is_some()).count();

            if known_leaders.len() == 1 && nodes_with_leader == alive.len() {
                elections_successful += 1;
            } else if known_leaders.len() > 1 {
                safety_violations += 1;
            }
        } else {
            // Heartbeat round — leader broadcasts
            // (no state change needed for measurement)
        }

        std::thread::sleep(std::time::Duration::from_micros(cfg.heartbeat_interval_us));
    }

    W3aResult {
        nodes_total: cfg.node_count,
        rounds_completed: cfg.max_rounds,
        elections_successful,
        elections_total,
        safety_violations,
        nodes_failed,
        duration_s: start.elapsed().as_secs_f64(),
        work_done: elections_successful as f64,
    }
}
