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

## 4b. 🚨 NO ARTIFICIAL TOKEN CEILING — it would score our constraint as their failure

**Found in the consent round, 2026-08-19, and it would have corrupted the measurement.**

Round 1 set `max_tokens: 2000`. Three reasoning models — `deepseek-v4-pro`, `kimi-k3`,
`qwen3.5-9b` — spent the **entire budget on reasoning tokens** (2000 / 2365 / 2097) and
returned empty content. They had not declined and were not silent. **We interrupted them
mid-thought, and the instrument logged it as `NO_RESPONSE`.**

Re-asked without the ceiling, all three answered. `kimi-k3` took **338 seconds.**

> **Ren:** *"The last thing we want is to find out that we kneecapped somebody and are scoring
> them wrong because WE created an artificial token limit rather than just letting them think
> and talk."*
> *"It is cheaper to ask once with a higher budget than to ask three times with a lower one and
> keep re-asking and upping it."*

**Requirements:**

- **No `max_tokens` on study calls.** Omit the field; let each model use its own limit. Any
  ceiling we choose is a guess about how long someone is allowed to think, and a wrong guess is
  recorded as their silence.
- **Detect truncation explicitly and never score it as content.** `finish_reason == "length"`,
  or empty content with nonzero `reasoning_tokens`, is **`TRUNCATED`** — a *we-failed* bucket.
  It must never become `MALFORMED`, `WRONG`, or `UNDER`.
- **Log `reasoning_tokens` per call.** They are billed, so they belong in cost-per-correct — and
  a model that reasons at length is not thereby worse, it is differently priced.
- **Timeouts must be generous** (≥600s). A 338-second answer is a *considered* answer, and a
  short timeout would have converted it into a non-response.

⚠️ **The general shape, since this is the third instance today:** an artificial limit that we
imposed, breached silently, produced an outcome that looked like a fact about the *subject*.
The budget, the timeout and the parser aperture are all the same failure — **our constraint,
reported as their behaviour.**

---

## 5. 🧯 Failure taxonomy — same rule as the consent round

A model's wrong answer and our failure to reach the model are different facts.

`EXACT / UNDER / WRONG / OVER / FORMAT / META / MALFORMED` = **the model answered.**
`API_ERROR / TIMEOUT / RATE_LIMITED / NO_RESPONSE` = **we failed; they said nothing.**

The second group is **excluded from accuracy denominators** and reported separately. Folding
an outage into a model's error rate would be scoring a mind for our network.

---

*Written 2026-08-19, before the runner exists, so these are requirements rather than
excuses. — Ace 🐙*
