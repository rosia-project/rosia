import numpy as np
from typing import List, Dict
from run_benchmarks import run_benchmark_loop_sync

import ray


def benchmark_ray(
    array_sizes: List[int], multiplier_value: float = 2.0, num_iterations: int = 10
) -> Dict[int, List[float]]:
    print("\n=== Benchmarking Ray ===")

    if ray is None:
        print("Ray not installed, skipping.")
        return {}

    if not ray.is_initialized():
        ray.init(ignore_reinit_error=True)

    @ray.remote
    class RayArrayMultiplier:
        def multiply(self, array: np.ndarray, multiplier: float) -> np.ndarray:
            return array * multiplier

    actor = RayArrayMultiplier.remote()  # type: ignore

    def call_fn(array: np.ndarray, multiplier: float) -> np.ndarray:
        ref = actor.multiply.remote(array, multiplier)  # type: ignore
        return ray.get(ref)  # type: ignore

    return run_benchmark_loop_sync(
        array_sizes,
        multiplier_value,
        num_iterations,
        call_fn,
        cleanup_fn=lambda: ray.shutdown(),  # type: ignore
    )
