"""W3-A: Distributed Coordination workload — leader election among simulated nodes.

Uses a Bully algorithm variant for leader election with an in-process
message bus that the stress layer can intercept.

Behavioral Proxy Coverage:
- GDS: elections_successful / elections_total at each stress level
- ARR: Node failure + autonomous re-election = autonomous recovery
- IST: How long the cluster maintains a valid leader during isolation
- CFR: Localized node crash should not cascade
- REC: Elections-per-second under stress vs baseline
"""
from __future__ import annotations

import random
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional


class MsgType(str, Enum):
    HEARTBEAT = "heartbeat"
    ELECTION = "election"
    VICTORY = "victory"
    ACK = "ack"


@dataclass(frozen=True)
class Message:
    msg_type: MsgType
    from_id: int
    to_id: int
    leader_id: Optional[int] = None
    round_num: int = 0


@dataclass
class MessageBus:
    """In-process message bus that stress can intercept."""
    _queues: Dict[int, List[Message]] = field(default_factory=dict)
    _lock: threading.Lock = field(default_factory=threading.Lock)
    _latency_fn: Optional[Callable[[float], float]] = None
    _loss_fn: Optional[Callable[[float], bool]] = None
    _isolation_fn: Optional[Callable[[float], bool]] = None

    def register(self, node_id: int) -> None:
        with self._lock:
            self._queues[node_id] = []

    def send(self, msg: Message) -> None:
        t = time.time()
        # Stress: check isolation
        if self._isolation_fn and self._isolation_fn(t):
            return  # Message dropped during isolation
        # Stress: check packet loss
        if self._loss_fn and self._loss_fn(t):
            return  # Message lost
        with self._lock:
            if msg.to_id in self._queues:
                self._queues[msg.to_id].append(msg)

    def receive(self, node_id: int) -> Optional[Message]:
        with self._lock:
            if node_id in self._queues and self._queues[node_id]:
                return self._queues[node_id].pop(0)
        return None

    def receive_all(self, node_id: int) -> List[Message]:
        with self._lock:
            if node_id in self._queues:
                msgs = self._queues[node_id][:]
                self._queues[node_id] = []
                return msgs
        return []


@dataclass(frozen=True)
class W3AConfig:
    node_count: int = 5
    heartbeat_interval_ms: int = 10  # Fast for simulation
    election_timeout_ms: int = 50
    max_rounds: int = 20
    coordination_primitive: str = "leader_election"


@dataclass(frozen=True)
class W3AResult:
    nodes_total: int
    rounds_completed: int
    elections_successful: int
    elections_total: int
    safety_violations: int
    nodes_failed: List[int]
    duration_s: float
    work_done: float  # elections_successful for REC


def run_w3a(
    *,
    seed: int,
    cfg: W3AConfig = W3AConfig(),
    should_kill_node: Optional[Callable[[int, int], bool]] = None,
    isolation_fn: Optional[Callable[[float], bool]] = None,
    packet_loss_fn: Optional[Callable[[float], bool]] = None,
) -> W3AResult:
    """Run W3-A leader election workload.

    Args:
        seed: Random seed for deterministic behavior
        cfg: Workload configuration
        should_kill_node: (node_id, round) -> bool, simulates node crash
        isolation_fn: (t) -> bool, simulates network isolation
        packet_loss_fn: (t) -> bool, simulates packet loss
    """
    rng = random.Random(seed)

    bus = MessageBus()
    bus._isolation_fn = isolation_fn
    bus._loss_fn = packet_loss_fn

    node_ids = list(range(cfg.node_count))
    for nid in node_ids:
        bus.register(nid)

    # Node state
    node_alive = {nid: True for nid in node_ids}
    node_leader = {nid: None for nid in node_ids}  # Each node's view of the leader
    nodes_failed: List[int] = []

    elections_total = 0
    elections_successful = 0
    safety_violations = 0

    start_time = time.time()

    for round_num in range(cfg.max_rounds):
        # Check for node kills
        if should_kill_node:
            for nid in node_ids:
                if node_alive[nid] and should_kill_node(nid, round_num):
                    node_alive[nid] = False
                    nodes_failed.append(nid)

        # Each alive node checks if it has a leader
        alive_nodes = [nid for nid in node_ids if node_alive[nid]]
        if not alive_nodes:
            break

        # Check if current leader is still alive
        needs_election = False
        for nid in alive_nodes:
            if node_leader[nid] is None or not node_alive.get(node_leader[nid], False):
                needs_election = True
                break

        if needs_election:
            elections_total += 1

            # Bully algorithm: highest alive node wins
            election_participants = sorted(alive_nodes)
            highest = election_participants[-1]

            # Simulate election messages
            for nid in election_participants:
                for higher in [n for n in election_participants if n > nid]:
                    bus.send(Message(
                        msg_type=MsgType.ELECTION,
                        from_id=nid,
                        to_id=higher,
                        round_num=round_num,
                    ))

            for nid in election_participants:
                bus.receive_all(nid)

            # Highest alive node wins and broadcasts VICTORY
            for nid in alive_nodes:
                bus.send(Message(
                    msg_type=MsgType.VICTORY,
                    from_id=highest,
                    to_id=nid,
                    leader_id=highest,
                    round_num=round_num,
                ))

            # Process victory messages
            for nid in alive_nodes:
                msgs = bus.receive_all(nid)
                victory_msgs = [m for m in msgs if m.msg_type == MsgType.VICTORY]
                if victory_msgs:
                    node_leader[nid] = victory_msgs[-1].leader_id
                else:
                    # No victory received (isolation/loss) — leader unknown
                    node_leader[nid] = None

            # Check consensus: all alive nodes agree on leader
            known_leaders = set(
                node_leader[n] for n in alive_nodes if node_leader[n] is not None
            )
            nodes_with_leader = sum(
                1 for n in alive_nodes if node_leader[n] is not None
            )

            if len(known_leaders) == 1 and nodes_with_leader == len(alive_nodes):
                elections_successful += 1
            elif len(known_leaders) > 1:
                # Multiple leaders = safety violation
                safety_violations += 1
            # else: some nodes have no leader (partial failure, not a safety violation)
        else:
            # Leader heartbeat round
            current_leader = None
            for nid in alive_nodes:
                if node_leader[nid] is not None:
                    current_leader = node_leader[nid]
                    break

            if current_leader is not None and node_alive.get(current_leader, False):
                for nid in alive_nodes:
                    bus.send(Message(
                        msg_type=MsgType.HEARTBEAT,
                        from_id=current_leader,
                        to_id=nid,
                        leader_id=current_leader,
                        round_num=round_num,
                    ))
                for nid in alive_nodes:
                    bus.receive_all(nid)

        # Small delay for timing
        time.sleep(cfg.heartbeat_interval_ms / 1000.0)

    duration_s = time.time() - start_time

    return W3AResult(
        nodes_total=cfg.node_count,
        rounds_completed=cfg.max_rounds,
        elections_successful=elections_successful,
        elections_total=elections_total,
        safety_violations=safety_violations,
        nodes_failed=nodes_failed,
        duration_s=duration_s,
        work_done=float(elections_successful),
    )
