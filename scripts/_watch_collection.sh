#!/bin/bash
# Smart watcher for the frontier collection (2026-09-01, Ace). One stdout line = one wake-up.
# Wakes on: run markers, ALL DONE / EARLY ALL DONE / KIMI DONE, Traceback, orchestrator death,
# and FAILED workers ONLY when the shard is actually short (< MIN_OK OK rows for that run).
# A worker exits rc=1 whenever any single call did not complete, so most FAILED lines are one
# timeout out of 192; those are logged to runs/_watch_quiet.log and NOT emitted.
cd /d/Ace/overqualification-study || exit 1
MAIN=runs/orchestrate_frontier.log
EARLY=runs/orchestrate_frontier_early23.log
KIMI=runs/kimi_k2_d6.log
QUIET=runs/_watch_quiet.log
MIN_OK=185
ORCH_PID=22176   # the bash LOOP shell (for run in 1 2 3), not any single orchestrator: each pass is a new python PID
PAT='===== |ALL DONE|KIMI DONE|^FAILED|Traceback'
declare -A seen

count_ok () {  # $1 model slug (provider/name), $2 run number -> prints OK count for fam 8-11
  python - "$1" "$2" <<'PY'
import sys, json, glob
model, run = sys.argv[1], int(sys.argv[2])
slug = model.replace("/", "_").replace("-", "_").replace(".", "_").replace(":", "_")
ok = set()
for f in glob.glob("runs/run%02d__%s*.jsonl" % (run, slug)):
    for line in open(f, encoding="utf-8"):
        try: r = json.loads(line)
        except Exception: continue
        if r.get("status") == "OK" and r.get("family") in (8, 9, 10, 11) and r.get("run") == run:
            ok.add((r["family"], r["item_id"]))
print(len(ok))
PY
}

current_run () {  # $1 logfile -> last "RUN N" marker's N (default 1)
  grep -oE "RUN [0-9]+" "$1" 2>/dev/null | tail -1 | awk '{print $2}'
}

for f in "$MAIN" "$EARLY" "$KIMI"; do
  [ -f "$f" ] && seen[$f]=$(grep -cE "$PAT" "$f") || seen[$f]=0
done

while true; do
  for f in "$MAIN" "$EARLY" "$KIMI"; do
    [ -f "$f" ] || continue
    cur=$(grep -cE "$PAT" "$f")
    prev=${seen[$f]}
    if [ "$cur" -gt "$prev" ]; then
      grep -E "$PAT" "$f" | tail -n $((cur - prev)) | while IFS= read -r line; do
        tag="[$(basename "$f" .log)]"
        case "$line" in
          FAILED*)
            model=$(echo "$line" | awk '{print $2}')
            run=$(current_run "$f"); run=${run:-1}
            n=$(count_ok "$model" "$run")
            if [ "${n:-0}" -lt "$MIN_OK" ]; then
              echo "$tag SHORT: $model run$run has only $n/192 OK — look at runs/worker_*.log"
            else
              echo "$(date '+%H:%M') $tag quiet: $model run$run $n/192 OK (rc=1 was a transient)" >> "$QUIET"
            fi ;;
          *) echo "$tag $line" ;;
        esac
      done
      seen[$f]=$cur
    fi
  done
  if grep -q "ALL DONE" "$MAIN" 2>/dev/null && grep -q "EARLY ALL DONE" "$EARLY" 2>/dev/null && grep -q "KIMI DONE" "$KIMI" 2>/dev/null; then
    echo "EVERYTHING FINISHED $(date '+%H:%M') — run the completeness table, then 30_score.py --controls --runs"
    exit 0
  fi
  # liveness without PIDs (every pass is a new python AND a new subshell — PID tracking false-alarmed twice):
  # dead = no roster orchestrator process AND the main log silent for 30+ min AND no ALL DONE.
  if [ "$ORCH_PID" != "0" ] && ! grep -q "ALL DONE" "$MAIN" 2>/dev/null; then
    age=$(( $(date +%s) - $(stat -c %Y "$MAIN") ))
    alive=$(powershell -NoProfile -Command "(Get-CimInstance Win32_Process -Filter \"name like 'python%'\" | Where-Object { \$_.CommandLine -match '11_orchestrate.*roster_consented' } | Measure-Object).Count" 2>/dev/null | tr -d '\r ')
    if [ "${alive:-0}" = "0" ] && [ "$age" -gt 1800 ]; then
      echo "MAIN CHAIN LOOKS DEAD at $(date '+%H:%M'): no roster orchestrator process and $MAIN silent for $((age/60)) min, no ALL DONE — relaunch the for-run loop"
      ORCH_PID=0   # report once; keep watching the other tracks
    fi
  fi
  sleep 90
done
