# Benchmark

Compares rclpy (ROS 2) vs Ray vs rosia for array multiplication latency across different array sizes.

## Run

```bash
docker compose -f benchmark/docker-compose.yml up --build
```

Results are saved to `benchmark/results/`.
