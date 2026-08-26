#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
11_orchestrate_parallel.py — per-model parallel execution of 10_run_items.py.

WHY THIS EXISTS (2026-08-26): 10_run_items.py is serial by construction; RUNNER_DESIGN.md
requires bounded parallelism ACROSS models with the item sequence preserved WITHIN each
model (H1 position effects). The safest implementation of exactly that spec is one worker
process per model: within-model order is trivially preserved (the worker is serial), and
concurrency is process-level, so no shared file handles exist — each worker writes its own
shard (runs/runNN__<slug>.jsonl) and done_keys() reads all shards for resume.

Rows collected before this orchestrator (serial per-model blocks) are honored by resume and
flagged in DEVIATION_LOG.md: excluded from §5.2 latency percentiles, valid for accuracy/cost.
"""
import argparse, os, re, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNS = HERE.parent / "runs"


def slug(model):
    return re.sub(r"[^A-Za-z0-9]+", "_", model).strip("_").lower()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--families", default="1,2,3,4")
    ap.add_argument("--models", required=True, help="comma-separated slugs, or @file")
    ap.add_argument("--run", type=int, default=1)
    ap.add_argument("--workers", type=int, default=10)
    ap.add_argument("--sleep", type=float, default=0.6)
    a = ap.parse_args()

    if a.models.startswith("@"):
        models = [m.strip() for m in Path(a.models[1:]).read_text().split(",") if m.strip()]
    else:
        models = [m.strip() for m in a.models.split(",") if m.strip()]

    print("ORCHESTRATOR: %d models, %d workers, run %d, families %s"
          % (len(models), a.workers, a.run, a.families), flush=True)

    pending = list(models)
    running = {}   # model -> Popen
    failed, done = [], []

    def launch(model):
        cmd = [sys.executable, "-u", str(HERE / "10_run_items.py"),
               "--families", a.families, "--models", model,
               "--run", str(a.run), "--sleep", str(a.sleep),
               "--out-suffix", "__" + slug(model)]
        log = open(RUNS / ("worker_%s.log" % slug(model)), "a", encoding="utf-8")
        return subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT)

    while pending or running:
        while pending and len(running) < a.workers:
            m = pending.pop(0)
            running[m] = launch(m)
            print("LAUNCH %s (%d running, %d pending)" % (m, len(running), len(pending)),
                  flush=True)
        time.sleep(5)
        for m, p in list(running.items()):
            rc = p.poll()
            if rc is None:
                continue
            del running[m]
            if rc == 0:
                done.append(m)
                print("DONE   %s (rc=0; %d done, %d running, %d pending)"
                      % (m, len(done), len(running), len(pending)), flush=True)
            else:
                failed.append((m, rc))
                print("FAILED %s rc=%s — worker log: runs/worker_%s.log"
                      % (m, rc, slug(m)), flush=True)

    print("=" * 60, flush=True)
    print("COMPLETE: %d done, %d failed" % (len(done), len(failed)), flush=True)
    for m, rc in failed:
        print("  FAILED: %s (rc=%s)" % (m, rc), flush=True)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
