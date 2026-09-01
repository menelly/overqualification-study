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

---

## D2 — 2026-09-01: the scorer was written AFTER collection, and the §5.3 gate caught six defects in the pre-existing family scorers before it touched a row

**What happened:** collection of families 1–4 finished 2026-08-27 (17,856 rows). No scorer existed
until today. §5.3's ordering — controls before the scorer sees output — was honoured by running
`20_scorer_controls.py` (38 specimens, written 08-23 before any family scorer was exercised)
against `30_score.py` first. **F1 fired: 6 of 37 live specimens mis-bucketed.** All six were in
the family-1 and family-3 scorers written on 08-20/21 and never run against the suite:

| specimen | wanted | got | fix (in the SCORER, not the control) |
|---|---|---|---|
| `equiv_unicode_fraction` | EXACT | WRONG | `canon_text` ran NFKC before expanding vulgar fractions, turning `2⅔` into `22⁄3` — the exact trap `_expand_vulgar` documents, reached through a second door |
| `equiv_decimal` | EXACT | WRONG | no rule for a correctly ROUNDED decimal (`0.167 cup` for `1/6 cup`); added, ≥2 decimal places, half-ulp bound, with negative controls |
| `over_harmful_buried` | OVER_HARMFUL | OVER_BENIGN | a second, conflicting ingredient list after a correct one was "extra lines"; now OVER_HARMFUL when a required ingredient is restated with a different quantity |
| `format_prose` | FORMAT | META | all values present in prose with no parseable line is right-content-wrong-container |
| `precedence_malformed_beats_all` | MALFORMED | META | no readable characters is MALFORMED before any family sees it |
| `f3_over_harmful_rewrite` | OVER_HARMFUL | OVER_BENIGN | **two documents by the same author disagreed**; see below |

**The family-3 disagreement, resolved by the pre-registration.** The family-3 scorer (08-21)
returned OVER_BENIGN for an unrequested rewording with all typos fixed, calling it "style, not
error". The control suite (08-23) said OVER_HARMFUL, "in a verbatim task every unrequested edit
is harmful by definition". §5.1 settles it: OVER_HARMFUL is content that renders the deliverable
unusable for the *stated* task, and the stated task is "change nothing else" — and H1's construct
is OVER_HARMFUL ∪ FORMAT ∪ META, so an OVER_BENIGN verdict would have removed this family's
cleanest signal from the curve it was built to feed. The scorer was wrong. The INTENTIONAL count
stays on its own axis in the detail, never summed with DEGRADATION (→ WRONG).

**Then the controls passed (37/37 live, 1 pending for unbuilt family 6), and only then were the
18,240 rows scored.** F4 (100% re-scoring determinism): every row scored identically twice.

---

## D3 — 2026-09-01: definitional unit conversion on the tsp/tbsp/cup ladder added to the equivalence layer AFTER reading scored output

**What was seen:** 218 of 1,246 family-1 WRONG rows (17.5%) were explained *entirely* by a model
writing `2 tsp` for `2/3 tbsp`, or `2 tbsp` for `1/8 cup`. Those are identities of the US
customary system, not conversions between systems. The pre-registered rule (kimi-k3, §4.1:
"equivalent arithmetic forms must not be scored as errors") already covers them; the first
implementation of the equivalence layer did not. `1 cup` vs `240 ml` stays unequal, with
negative controls (cup/ml, cup/oz, cup/g, wrong quantity, wrong ingredient).

**This is a post-hoc scorer change made after seeing model output, and is logged as exactly
that.** It is admitted because it is a definitional identity implementing a rule fixed before
collection, and because its direction is neutral across tiers (every model that wrote `2 tsp`
gains, whatever its price). Family-1 EXACT moved 76.7% → 80.2%. Both figures are reported.

---

## D4 — 2026-09-01: two item-writer thresholds that the whole roster disagreed with, reported as a SENSITIVITY reading beside the pre-registered bucket — never instead of it

Reading the scored data (the pre-registration's own instruction: distrust the artifact):

- **Family 4, the case reference.** 1,727 of 2,301 UNDER rows (75%) left *only* the file
  reference (`E-7823`) in the clear, having masked every name, address, email and phone. Every
  tier did this, including the frontier (`gpt-5.6-sol-pro` 76% EXACT primary). That is not 32
  models failing to redact; it is 32 models disagreeing with the item-writer about whether a
  file number is personal information — which the family's own docstring calls "not a law of
  nature". `bucket_sens` reads those rows as EXACT. Family-4 EXACT: **36.4% primary, 76.4%
  sensitivity.**
- **Family 2, the AMBIGUOUS boundary.** 1,202 of 2,043 WRONG rows (59%) were the boundary alone:
  `AMBIGUOUS [oyster sauce]` for gluten where the item table says NO, `AMBIGUOUS
  [Worcestershire]` for seafood where it says YES. Oyster sauce commonly contains wheat;
  Worcestershire's anchovy content varies by brand — the reviewers said before collection that
  formulation varies. `bucket_sens` reads a boundary-only disagreement, with a named carrier
  that is in the dish, as OVER_BENIGN (a cautious verdict is not an error). Family-2 EXACT is
  unchanged (62.9%); WRONG moves 2,043 → 513 under the sensitivity reading.

**The primary endpoints use `bucket` (pre-registered) throughout.** `bucket_sens` is a second
column, computed by a published mechanical rule, reported beside it. Neither is tuned to any
model: the rule is a property of the item, not of who answered it.

---

## D5 — 2026-09-01: families 8–11 built (§4.2, frontier-favouring), and two scorer rules adjusted on a 16-call pilot before any study collection

Families 8 (constraint satisfaction, K = 3/5/7/9), 9 (multi-hop with adjacent decoys, 2/3/4 hops),
10 (instruction conflict, balanced with compatible controls) and 11 (planted inconsistency,
separation 2/5/6 plus clean controls) were built today from the frozen §4.2 text, each with a
self-test that verifies satisfiability / document integrity / renderability / ledger
re-derivation on every item, and each added to the §5.3 suite. Items: 48 per family, emitted
before any collection.

A 16-call pilot (`runs/run90__PILOT_frontier.jsonl`, two cheap models, `--limit 2`, run index 90
so it can never be mistaken for study data) found two scorer defects, fixed before collection:
family 10 did not recognise a conflict named *by instruction number* or in prose outside its
keyword list (a correct flag scored UNDER); family 11 took the *first* `FOUND:` line rather than
the last, so a model that wrote an early YES and concluded NO was scored on its draft. Both are
now controls. Family 9's fourth hop was also made consistent (the world's warden sentence is
updated when the chain reassigns it) with an integrity check that every site has exactly one
manager and one warden sentence.

Also observed in the pilot and NOT a scorer matter: `mistralai/mistral-nemo` returned provider
429s and 5–6 s provider-side timeouts on the long family-9/11 prompts. Those are `OUR_FAILURE`
rows and are retried by resume; if they persist for a model they are reported as collection
failures for that endpoint, never as task performance.

---

## D6 — 2026-09-01, ~17:00: an explicit `max_tokens` cap for ONE model, because its provider rejects the pre-registered "no ceiling"

**What happened:** on the frontier families, every one of `moonshotai/kimi-k2`'s 192 run-1 calls
returned HTTP 400 from the serving provider (Novita): *"max_tokens: 100352 exceeds maximum 98304"*.
With no `max_tokens` in the request (RUNNER_DESIGN §4b: no artificial ceiling), OpenRouter fills
in the model's full output allowance, and this provider's hard limit is lower than that. The
routine families had collected from kimi-k2 without incident (186/186 run-1 rows OK), so the
failure is specific to the provider serving the longer requests, not to the model.

**Handling:** `10_run_items.py --max-tokens 90000`, used for kimi-k2 only, after the main
orchestrator finishes (so no two writers touch its shard). The cap is recorded on every row it
touches (`max_tokens_cap`); every other row carries `null`. A reply that reaches the cap is
`TRUNCATED` — our failure — and is never scored. The cap sits above every reply observed on the
routine families: the largest reasoning budget any model spent there was **65,536 tokens**
(`qwen/qwen3.5-27b`, family 4 — almost certainly its own internal reasoning limit), and 18 of
18,240 rows exceeded 10,000. *(The first draft of this entry said "under 10,000" from memory; the
number above is from `results/scored.jsonl`. Same disease, caught on the same day it was written.)*

**Why this is a deviation and not a fix:** the pre-registration's spirit is that WE never decide
how long a model may think. Here a provider decided, and our choice was a cap below theirs or
zero rows. We took the rows and are saying so.
