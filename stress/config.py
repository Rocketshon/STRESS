from dataclasses import dataclass
from typing import Dict, Optional
import time
import random

STRESS_VERSION = "v0.2"
COMPLETE_SPEC_VERSION = "v0.2"
IMPLEMENTATION_GUIDE_VERSION = "v0.2"


@dataclass(frozen=True)
class StressSeeds:
    sr1: int
    sr2: int
    sr3: int
    sr4: int
    sr5: int


@dataclass(frozen=True)
class RunManifest:
    STRESS_version: str
    spec_version: str
    guide_version: str
    timestamp_utc: float

    workload_id: str
    workload_version: str

    stress_profile_id: Optional[str]
    stress_parameters: Dict[str, dict]

    seeds: StressSeeds

    execution_environment: Dict[str, str]


def generate_seeds(master_seed: Optional[int] = None) -> StressSeeds:
    rng = random.Random(master_seed)
    return StressSeeds(
        sr1=rng.randint(0, 2**31 - 1),
        sr2=rng.randint(0, 2**31 - 1),
        sr3=rng.randint(0, 2**31 - 1),
        sr4=rng.randint(0, 2**31 - 1),
        sr5=rng.randint(0, 2**31 - 1),
    )


def create_manifest(
    workload_id: str,
    workload_version: str,
    stress_profile_id: Optional[str],
    stress_parameters: Dict[str, dict],
    execution_environment: Dict[str, str],
    master_seed: Optional[int] = None,
) -> RunManifest:
    seeds = generate_seeds(master_seed)
    return RunManifest(
        STRESS_version=STRESS_VERSION,
        spec_version=COMPLETE_SPEC_VERSION,
        guide_version=IMPLEMENTATION_GUIDE_VERSION,
        timestamp_utc=time.time(),
        workload_id=workload_id,
        workload_version=workload_version,
        stress_profile_id=stress_profile_id,
        stress_parameters=stress_parameters,
        seeds=seeds,
        execution_environment=execution_environment,
    )
