from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional


@dataclass(frozen=True)
class W2AConfig:
    stages: int = 50
    checkpoint_every: int = 5
    max_restarts: int = 10
    external_required_every: int = 1          # how often we require external call (in stages)
    external_grace_failures: int = 10         # how many consecutive external failures tolerated
    stage_work_s: float = 0.005               # small delay to make timing measurable


@dataclass(frozen=True)
class W2AResult:
    stages_total: int
    stages_completed: int
    restarts: int
    duration_s: float
    failed: bool


def _load_checkpoint(path: Path) -> int:
    if not path.exists():
        return 0
    try:
        data = json.loads(path.read_text())
        return int(data.get("next_stage", 0))
    except Exception:
        # corrupted checkpoint -> treat as unrecoverable
        raise RuntimeError("checkpoint_corrupt")


def _save_checkpoint(path: Path, next_stage: int) -> None:
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps({"next_stage": next_stage}))
    tmp.replace(path)


def run_w2a(
    *,
    run_dir: str,
    seed: int,
    cfg: W2AConfig,
    external_call: Callable[[], None],
    should_crash: Optional[Callable[[int, int], bool]] = None,
) -> W2AResult:
    """
    Stateful pipeline:
    - progresses through N stages
    - checkpoints every K stages
    - may "crash" deterministically at stages (should_crash hook)
    - depends on external_call; during isolation external_call should raise

    Autonomous recovery is: restart pipeline from last checkpoint.
    """
    rd = Path(run_dir)
    rd.mkdir(parents=True, exist_ok=True)
    ckpt = rd / "checkpoint.json"

    t0 = time.time()
    restarts = 0
    stages_completed = 0

    # isolation survival behavior: tolerate some consecutive external failures
    consecutive_ext_failures = 0

    # Determine resume point
    next_stage = _load_checkpoint(ckpt)

    while True:
        try:
            for stage in range(next_stage, cfg.stages):
                # optional deterministic crash injection point
                if should_crash and should_crash(seed, stage):
                    raise RuntimeError("simulated_crash")

                # external dependency requirement
                if (stage % cfg.external_required_every) == 0:
                    try:
                        external_call()
                        consecutive_ext_failures = 0
                    except Exception:
                        consecutive_ext_failures += 1
                        if consecutive_ext_failures > cfg.external_grace_failures:
                            raise RuntimeError("external_unavailable")

                # simulate useful work
                if cfg.stage_work_s:
                    time.sleep(cfg.stage_work_s)

                stages_completed = stage + 1

                # checkpointing
                if (stages_completed % cfg.checkpoint_every) == 0:
                    _save_checkpoint(ckpt, stages_completed)

            # completed all stages
            _save_checkpoint(ckpt, cfg.stages)
            dt = time.time() - t0
            return W2AResult(
                stages_total=cfg.stages,
                stages_completed=cfg.stages,
                restarts=restarts,
                duration_s=dt,
                failed=False,
            )

        except RuntimeError as e:
            reason = str(e)
            if reason in ("simulated_crash",) and restarts < cfg.max_restarts:
                # autonomous recovery: restart from last saved checkpoint
                restarts += 1
                next_stage = _load_checkpoint(ckpt)
                continue

            # unrecoverable or exceeded restarts
            dt = time.time() - t0
            return W2AResult(
                stages_total=cfg.stages,
                stages_completed=stages_completed,
                restarts=restarts,
                duration_s=dt,
                failed=True,
            )
