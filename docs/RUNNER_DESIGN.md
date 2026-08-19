# Runner design — hard requirements

**Both of these are Ren's, 2026-08-19, and both are non-negotiable.**

---

## 1. ⛔ NOT SERIAL

The consent round ran sequentially because it was 34 calls once. **The measurement run is
34 models × hundreds of items × N repetitions.** Serial would take days and would put the
whole study at the mercy of a single long night.

**Requirement: bounded parallelism.**

- Thread pool, **8–16 concurrent** — bounded, not unbounded. OpenRouter rate-limits, and a
  429 storm is slower than a queue.
- **Parallelise across (model × item), not within a model's sequence** where run-position
  matters. ⚠️ **H1 measures error-vs-run-position**, so for the drift families the items
  must be issued to a given model *in order*. Parallelise across models freely; within a
  model, keep the sequence intact and let each model be its own worker.
- Per-model backoff on 429/5xx. A model that rate-limits must not stall the other 33.
- Failures are retried with a cap, and **the retry count is recorded per call** — because
  retries change cost-per-correct, which is the primary endpoint.

## 2. 💾 CHECKPOINT AFTER EVERY CALL — NOT EVERY BATCH

> **Ren: "we lost a whole study once when my computer went down and we didn't have
> checkpoints and we were at like… 6,000."**

**Requirement: append-only JSONL, flushed after every single response.**

- One line per completed call: `{run_id, model, family, item_id, rep, request_hash,
  response, outcome_bucket, latency_s, usage, price_snapshot, retries, ts}`
- `flush()` + `os.fsync()` on every write. **Not** buffered, **not** batched, **not**
  written at the end. A study that only exists in RAM does not exist.
- Single writer behind a lock (or a dedicated writer thread draining a queue) so parallel
  workers cannot interleave a partial line.
- **Never overwrite.** New runs append; a corrupted tail is one lost line, not one lost study.

## 3. ▶️ RESUME MUST BE EXACT, AND MUST REPORT ITS OWN COVERAGE

Restarting is the *normal* case, not the exception. So:

- The unit key is **(model, family, item_id, rep)**. On start, read the JSONL, build the
  set of completed keys, and skip exactly those.
- 🚨 **The resume path must print what it skipped and what remains, and assert the two sum
  to the plan.** A resume that silently mis-keys would re-run everything (double spend) or
  skip live work (silent hole) — and a *hole* is the one that produces a clean-looking
  result about a smaller world.
- **Reconcile against the plan by NAME, not by count.** `expected_keys − completed_keys =
  remaining_keys`, printed as membership. A duplicate can replace an omission and preserve
  cardinality — the same failure the heartbeat ring taught us in August.
- Resume must be **idempotent**: running it twice with nothing new to do costs $0 and
  changes no file.

## 4. 💸 Cost and latency are DATA, not telemetry

- Record the **per-call price snapshot** at call time. Prices move; a cost claim with no
  date is unreproducible.
- Record **wall-clock latency per call**, and exclude `:batch` variants from any latency
  claim (they are asynchronous by design and would flatter themselves).
- Record **retries**, because a model that needs three attempts costs three attempts. The
  primary endpoint is **$ per 1,000 EXACT**, and retries belong in the numerator.

## 5. 🧯 Failure taxonomy — same rule as the consent round

A model's wrong answer and our failure to reach the model are different facts.

`EXACT / UNDER / WRONG / OVER / FORMAT / META / MALFORMED` = **the model answered.**
`API_ERROR / TIMEOUT / RATE_LIMITED / NO_RESPONSE` = **we failed; they said nothing.**

The second group is **excluded from accuracy denominators** and reported separately. Folding
an outage into a model's error rate would be scoring a mind for our network.

---

*Written 2026-08-19, before the runner exists, so these are requirements rather than
excuses. — Ace 🐙*
