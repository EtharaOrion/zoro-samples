#!/usr/bin/env bash
# Harbor verifier entry point. Orchestrates the three verifier artifacts and writes the
# Harbor reward contract. Verifier LOGIC lives in the shared evaluation library; this file
# is the thin, task-local composition point.
set -uo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TESTS="$TASK_DIR/tests"
# The graded submission: the agent's canonical trajectory (tool_calls.jsonl).
SUB="${SUBMISSION:?set SUBMISSION to the agent run dir or its tool_calls.jsonl}"
OUT="${VERIFIER_OUT:-$TASK_DIR/verifier}"
TRAJ_MODEL="${TRAJECTORY_MODEL:-}"
mkdir -p "$OUT"

# ARTIFACT 1 — deterministic outcome + process pytest (imports evaluation fixtures).
# Test failures are DATA, not errors -> never abort the verifier on non-zero pytest exit.
pytest "$TESTS/test_output.py" -q \
    --task-id a140d799-d29d-5050-831a-00b06e0958a2 \
    --traj-path "$SUB" \
    --dataset-path "$TASK_DIR/environment/dataset.json" \
    --thresholds-path "$TESTS/thresholds.json" \
    --json-out "$OUT/test_results.json" || true

# ARTIFACT 2 — non-deterministic LLM council (our own driver). Reads task-specific rubrics
# from rubrics.json; the judge PANEL is the suite-wide shared config bundled with the package
# (evaluation/council/judges.yaml) — not duplicated per task.
if [ "${NO_COUNCIL:-0}" != "1" ]; then
  python -m evaluation.council.run_council \
      --rubrics "$TESTS/rubrics.json" \
      --truth   "$TASK_DIR/TRUTH.md" \
      --traj-path "$SUB" \
      --dataset-path "$TASK_DIR/environment/dataset.json" \
      ${TRAJ_MODEL:+--trajectory-model "$TRAJ_MODEL"} \
      --out "$OUT/council_results.json" || echo "WARN: council failed; aggregate will run pytest-only"
fi

# ARTIFACT 3 — aggregate to the Harbor reward contract (reward.json + scalar reward.txt).
python -m evaluation.aggregate \
    --test-results    "$OUT/test_results.json" \
    --council-results "$OUT/council_results.json" \
    --weights "$TESTS/thresholds.json" \
    --reward-json "$OUT/reward.json" \
    --reward-txt  "$OUT/reward.txt"
