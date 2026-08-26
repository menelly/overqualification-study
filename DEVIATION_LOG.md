# DEVIATION LOG — post-freeze execution deviations, logged as they happen

## D1 — 2026-08-26, ~10:30–11:20am: first 358 rows of run 1 collected in SERIAL per-model blocks

**What happened:** run 1 was launched with `10_run_items.py`, which implements the collection
loop serially (model → family → item). RUNNER_DESIGN.md's bounded-parallelism requirement and
the pre-registration's §5.2 interleaving requirement ("models are interleaved across the
collection window, never run in per-model blocks") were not implemented in that script.
Detected at 358 rows (deepseek-v4-flash complete, deepseek-v4-pro at 172); run stopped.

**Impact:** WITHIN-model item order was preserved throughout (the serial loop is sequential per
model), so H1 position analysis is unaffected. Accuracy and cost-per-correct are unaffected.
**Latency fairness is affected for those 358 rows** — they were collected in per-model blocks.

**Handling, fixed now:**
1. The 358 rows are KEPT for accuracy/cost analyses and **excluded from §5.2 latency percentiles**.
2. Collection resumed via `11_orchestrate_parallel.py`: one worker process per model (within-model
   sequence preserved by construction), 10 concurrent, per-model shard files, resume across all
   shards by (model, family, item_id, run). This implements the frozen design as written.
3. Nothing was re-collected or double-spent; resume skipped all 358 completed keys by name.

**This is an execution deviation, not a methodology amendment** — the fix brings execution INTO
compliance with the frozen protocol. Logged same-day, before any scoring.
