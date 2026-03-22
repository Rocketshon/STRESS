use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum EventType {
    RunStart,
    RunEnd,
    WorkUnitStart,
    WorkUnitEnd,
    Failure,
    RecoveryAttempt,
    RecoverySuccess,
    RecoveryFailed,
    IsolationStart,
    IsolationEnd,
    ComponentAffected,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum FailureClass {
    AutonomouslyRecovered,
    RecoverableNotRecovered,
    Irreversible,
}

/// Canonical observational record. All metrics MUST be computed from these events.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Event {
    pub t_utc: f64,
    #[serde(rename = "type")]
    pub event_type: EventType,
    pub run_id: String,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub workload_id: Option<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub component_id: Option<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub work_unit_id: Option<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub failure_id: Option<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub failure_class: Option<FailureClass>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub stress_level: Option<f64>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub completion_rate: Option<f64>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub work_done: Option<f64>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub resources_used: Option<f64>,
}

/// In-memory event log for a single run.
pub struct EventLog {
    pub run_id: String,
    pub workload_id: String,
    events: Vec<Event>,
}

impl EventLog {
    pub fn new(run_id: &str, workload_id: &str) -> Self {
        Self {
            run_id: run_id.to_string(),
            workload_id: workload_id.to_string(),
            events: Vec::new(),
        }
    }

    pub fn emit(&mut self, event_type: EventType) -> &mut Event {
        let now = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap()
            .as_secs_f64();
        self.emit_at(event_type, now)
    }

    pub fn emit_at(&mut self, event_type: EventType, t_utc: f64) -> &mut Event {
        let event = Event {
            t_utc,
            event_type,
            run_id: self.run_id.clone(),
            workload_id: Some(self.workload_id.clone()),
            component_id: None,
            work_unit_id: None,
            failure_id: None,
            failure_class: None,
            stress_level: None,
            completion_rate: None,
            work_done: None,
            resources_used: None,
        };
        self.events.push(event);
        self.events.last_mut().unwrap()
    }

    pub fn events(&self) -> &[Event] {
        &self.events
    }
}
