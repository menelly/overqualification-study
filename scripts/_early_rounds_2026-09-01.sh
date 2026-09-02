#!/bin/bash
# Early runs 2+3 (and the kimi-k2 D6 rerun) launched 2026-09-01 ~21:15 while the main chain
# (PID 44164 loop: run1→resume1→run2→resume2→run3→resume3→ALL DONE) was still on run 1's tail.
# Safe because done_keys() reads EVERY shard of a run and a key collected anywhere is never
# re-spent (10_run_items.py, 2026-08-26 amendment). The chain's later run-2/3 passes will find
# these rows and only fill gaps. Ren asked "is there a super compelling reason to wait?" — no.
cd /d/Ace/overqualification-study || exit 1
export OPENROUTER_KEY=$(grep -m1 '^OPENROUTER_KEY=' /d/Ace/LibreChat/.env | cut -d= -f2-)
export PYTHONIOENCODING=utf-8
LOG=runs/orchestrate_frontier_early23.log
KLOG=runs/kimi_k2_d6.log

# --- track A: kimi-k2 with the D6 cap, its own shard per run ------------------------------
(
  for r in 1 2 3; do
    echo "===== KIMI-K2 D6 run $r start $(date)"
    python -u scripts/10_run_items.py --families 8,9,10,11 --models moonshotai/kimi-k2 \
      --run $r --max-tokens 90000 --sleep 0.4 --out-suffix __moonshotai_kimi_k2_d6
    echo "===== KIMI-K2 D6 run $r rc=$? $(date)"
  done
  echo "KIMI DONE $(date)"
) > "$KLOG" 2>&1 &

# --- track B: everyone except kimi-k2 (own track) and the two qwens still running run 1 ----
MODELS=$(tr -d '\n' < scripts/_roster_consented.txt | tr ',' '\n' \
  | grep -v -e '^moonshotai/kimi-k2$' -e '^qwen/qwen3.5-9b$' -e '^qwen/qwen3.5-397b-a17b$' \
  | paste -sd, -)
echo "$MODELS" | tr ',' '\n' | wc -l > runs/_early_model_count.txt
(
  for r in 2 3; do
    echo "===== EARLY RUN $r start $(date)"
    python scripts/11_orchestrate_parallel.py --families 8,9,10,11 --models "$MODELS" \
      --run $r --workers 7 --sleep 0.4
    echo "===== EARLY RUN $r resume pass $(date)"
    python scripts/11_orchestrate_parallel.py --families 8,9,10,11 --models "$MODELS" \
      --run $r --workers 7 --sleep 0.8
  done
  echo "EARLY ALL DONE $(date)"
) > "$LOG" 2>&1 &

wait
echo "BOTH TRACKS FINISHED $(date)"
