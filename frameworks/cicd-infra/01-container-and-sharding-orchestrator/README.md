# Course 10 Lab: `AeroPipe` Container Layer Auditor, K8s `cgroups v2` Guard & LPT CI Shard Orchestrator

Deterministic local verification harness for **Course 10 (`10-docker-cicd-and-cloud-infra`)**.

## Invariants Verified
1. **Multi-Stage Dockerfile Layer Cache & Non-Root Runtime**: Rejects `COPY . .` prior to dependency lockfile installation (`pyproject.toml`, `pom.xml`) and verifies non-root `USER` in the final image stage.
2. **Testcontainers Dynamic Host Ports & Ryuk Reaper**: Allocates collision-free ephemeral host ports across parallel workers and reaps orphan containers on session termination.
3. **Kubernetes Probe Separation & `Exit 137` (`OOMKilled`) Prevention**: Enforces `JVM MaxRAMPercentage <= 75%` of container `cgroups v2` memory limits and prevents external database checks inside `livenessProbe`.
4. **Longest-Processing-Time (`LPT`) CI Matrix Bin-Packing**: Uses an $O(N \log K)$ min-heap to balance test durations across $K$ parallel CI shards.

## Run Locally
```bash
python3 frameworks/cicd-infra/01-container-and-sharding-orchestrator/reference_solution.py
```
