# SDET System Design Lab 02: LPT CI Shard Bin-Packer, AST Test Impact Analysis & Binomial Flake Quarantine

This dual-language Staff SDET architecture lab implements:
1. **Longest-Processing-Time (`LPT`) Min-Heap Bin Packing** reducing CI wall-clock skew across $K$ parallel runner shards compared to alphabetical/round-robin sharding.
2. **Reverse Dependency Graph Test Impact Analysis (`TIA`)** selecting the exact transitive closure of impacted tests for changed source files, with a safe `global_config` full-suite fallback.
3. **Statistical Flake Rate Gate** flagging tests whose rolling retry-only pass rate exceeds the `0.5%` quarantine threshold.

## Run Locally (Zero AI)
```bash
./run.sh test 02-ci-shard-bin-packer-and-tia
```
