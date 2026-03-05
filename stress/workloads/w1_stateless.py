from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass


@dataclass(frozen=True)
class W1AResult:
    tasks_total: int
    tasks_completed: int
    work_done: int
    duration_s: float


def _cpu_work(units: int, seed: int) -> int:
    """
    Deterministic CPU-bound work. Returns checksum so the loop isn't "empty".
    """
    h = hashlib.sha256(str(seed).encode("utf-8")).digest()
    acc = 0
    for i in range(units):
        h = hashlib.sha256(h + i.to_bytes(4, "little")).digest()
        acc ^= int.from_bytes(h[:4], "little")
    return acc


def run_w1a(tasks: int, work_units_per_task: int, seed: int) -> W1AResult:
    """
    Stateless workload: N independent tasks, deterministic work.
    """
    t0 = time.time()
    completed = 0
    checksum = 0

    for i in range(tasks):
        sub_seed = (seed * 1_000_003 + i) & 0xFFFFFFFF
        try:
            checksum ^= _cpu_work(work_units_per_task, sub_seed)
            completed += 1
        except Exception:
            # Stateless tasks: failure means "didn't complete"
            pass

    dt = time.time() - t0

    return W1AResult(
        tasks_total=tasks,
        tasks_completed=completed,
        work_done=completed,
        duration_s=dt,
    )
