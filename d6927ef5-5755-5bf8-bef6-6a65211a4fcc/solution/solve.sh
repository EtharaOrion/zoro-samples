#!/usr/bin/env bash
# Reference solution = the RetailBench Oracle (rule-based, non-LLM shopkeeper).
# Deterministic: the environment seeds random + np.random from global_random_seed (300007),
# so this reproduces byte-identically (see tools/verify_oracle_reproducibility.py).
#
# The committed artifacts (tool_calls.jsonl, golden.json, metadata.json) in this directory
# were produced by exactly this command; solve.sh is the reproducible recipe + Harbor's
# oracle-agent sanity check. Threshold calibration additionally sweeps the policy knobs
# (sample_size x bulk_qty_multiplier) at the SAME seed — see script/generate_thresholds.py.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TASK_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
HARNESS="${RETAILBENCH_HARNESS:-$(cd "$SCRIPT_DIR/../../../.." && pwd)}"

python "$HARNESS/tools/run_oracle.py" \
    --task "$TASK_DIR/environment/dataset.json" \
    --days 180 \
    --sample_size 2 \
    --bulk_qty_multiplier 4 \
    --out "$TASK_DIR/solution"
# Emits: solution/tool_calls.jsonl, solution/golden.json, solution/metadata.json
