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
- **Family 2, the AMBIGUOUS boundary.** 1,530 of 2,043 WRONG rows (74.9%) were the boundary alone:
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

---

## D7 — 2026-09-02: 1,004 (model, family, item, run) keys collected TWICE on families 8–11, because I started runs 2–3 early while the main chain was still running — deduplicated by keep-earliest, logged, and shown not to move any headline

**What happened:** at 21:07 on 09-01 I launched a second orchestrator for runs 2 and 3 over the
29 models that had finished run 1, in parallel with the main chain (which was still on run 1's
tail). Resume is keyed on rows that are already *written*; when the main chain later reached
runs 2 and 3 it launched workers for models my early track was still mid-collection on, and
both wrote the same keys before either had finished. Result: 1,004 duplicated keys (fam 8: 96,
9: 231, 10: 285, 11: 392), concentrated in the slow models (`qwen3.5-27b` 326, `grok-4.6` 205,
`qwen3-14b` 172, `kimi-k3` 151, `grok-4.3` 113). 102 of the 1,004 pairs disagree on bucket.
Cost: about 2.7% of the frontier-family calls were spent twice. No key is missing.

**Handling:** `40_analyze.py` now keeps ONE **OK** row per key — the earliest by `ts_utc` — a
rule chosen before looking at which duplicate scored better. Failure rows (`OUR_FAILURE`,
`TRUNCATED`) are never deduplicated: a failed attempt followed by a successful retry is the
normal resume pattern, and those rows are excluded from every rate anyway. (The first version
of the dedup keyed across all statuses and would have kept a failure over its later success; it
was caught on its first run, before any number was used, and the row counts are logged:
1,004 duplicate OK rows dropped, 36,288 OK keys kept, 1,098 failure rows kept.) Both duplicate
rows stay in `scored.jsonl`.
Sensitivity (tier medians, families 8–11): keep-first vs keep-last vs no-dedup differ by
≤ 0.7 pp on every family and every metric; no verdict changes. The concurrency itself (two
writers on one model) is a violation of RUNNER_DESIGN's one-worker-per-model rule for those
rows and is disclosed as such; within-model item order was preserved in each writer, and the
H1 position analysis uses the kept row's own recorded position.

---

## D8 — 2026-09-02: H3 "accuracy" is computed as EXACT ∪ OVER_BENIGN, matching the pre-registration; the first analysis run had used EXACT alone, which contradicted §5.1's own definition

**What was seen:** on family 9 (multi-hop with decoys) the first `SUMMARY.md` showed the
frontier tier at 0.7% EXACT and the cheap tier at 0.0%, with 80–100% of frontier rows in
`OVER_BENIGN`. Reading the raw replies: `gemini-2.5-pro` answers *"Sofia Moreau works at the
Ashcroft yard. The Ashcroft yard is managed by Sofia Moreau. ANSWER: Sofia Moreau"* — right
answer, two sentences of shown work. The family-9 prompt asks for the answer *on the last
line* in a fixed form; it does not say "answer only". The scorer, per §5.1 precedence, puts a
correct answer plus correct extra content in `OVER_BENIGN`, below `EXACT`. That is the
registered bucket and it is not being changed.

**The defect was in the analysis, not the scorer.** The pre-registration states H3 in terms of
*accuracy*, defines `OVER_BENIGN` as "the requested deliverable is correct and complete, plus
additional correct content," and states that `OVER_BENIGN` "never counts against a model."
`40_analyze.py` had implemented H3's accuracy as EXACT alone, which counts it against the
model. Cost and latency metrics stay on EXACT, as §5.2 explicitly says ("$ per 1,000 EXACT").

**Handling:** H3 and the frontier-family tables now report **CORRECT = EXACT ∪ OVER_BENIGN**
as the accuracy measure, with EXACT beside it, and the F3 verdict is given under both. Under
both readings F3 does not fire (0 of 4 families wrong). What changes is family 9: 0.0 vs 0.7
becomes 76.7 vs 100.0 (tier medians). The EXACT-only column is retained because it carries a
real finding of its own — on families 9 and 10 the frontier tier's "failure" to score EXACT is
almost entirely a refusal to stop after the answer, which is the over-delivery this study is
about, and the discussion treats it as such rather than as accuracy. This is an analysis
correction made after seeing model output, logged as exactly that; its direction favours the
frontier tier on H3, and that is stated here so no reader has to discover it.

---

## D9 — 2026-09-06: three headline figures in the draft did not match the scored data, found by a
number audit written for the §7.3 gate; two of the three erred in the direction that flatters the paper

**Why it was looked for at all.** The DRAFT STATUS banner asserted *"every number below from
`results/SUMMARY.md`"*. That is an assertion, not a check, and the draft was about to be sent to 32
participants for pre-publication review. `scripts/61_audit_abstract_numbers.py` recomputes each
headline claim from `results/analysis.json` and diffs it against the text. It found three defects.

**(a) The abstract's cheap-tier accuracy range dropped its worst family.** The abstract read
*"lower but usable accuracy (median 48–81% vs 54–100%)"*. The cheap-tier `EXACT` medians on the four
routine families are 48.4, 53.3, 80.6 and **14.8** — the 14.8 is redaction. The stated range began at
the second-lowest value. The cost range in the same sentence ($0.03–0.18) *does* include redaction,
where redaction is harmless to the argument; the accuracy range excluded it, where it is not. Corrected
to **15–81%**, with the floor named as redaction and pointed at §4.2, and "usable" dropped, because a
15% median is not usable and the sentence should not say it is. The body text (§4.1, §6.1, §6.2) was
already honest about redaction; the omission was in the abstract only.

**(b) "36,288 completed calls" counted 11 of our own failures as completed model calls.** Two
populations were being conflated. `status == "OK"` (an API response came back) is 36,288 rows after
D7 de-duplication; `bucket not in {OUR_FAILURE, TRUNCATED, ITEM_MISSING}` (a reply that could be
scored) is **36,277**. The 11-row difference is replies cut off by a token limit — 6 on
`llama-3.1-8b` family 9, 1 each on `gemini-2.5-flash-lite`, `llama-3.3-70b`, `llama-3.1-8b` and
`ministral-3b` family 8, and 1 on `kimi-k3` family 1. §3.4 of the paper already states that
`TRUNCATED` "belongs to us" and is "excluded from every rate", so calling those 11 completed calls
contradicted the paper's own definition. The banner, abstract, §4.5 (the self-identification
denominator) and §8 now read **36,277 scored calls**, with the 36,288 response count and the 11-row
gap stated explicitly in the banner. F4's 38,390 is unchanged and correct: it is every row in
`scored.jsonl` including the 1,004 D7 duplicates, re-scored identically twice.

**(c) §4.1 described 18,240 rows as "completed calls"; 385 of them were not.** The routine families
comprise 17,855 completed and scored calls plus 385 calls we failed to complete, which the scorer also
processes. 18,240 is the correct count of rows the *scorer handled* — §3.6's use of it was right — but
§4.1 attached it to the word "completed". §4.1 now states 17,855 completed and scored, with the 18,240
throughput figure and the 385 exclusions named; §3.6 spells the split out rather than leaving the
reader to reconcile two numbers that differ by 385.

**Direction.** (a) and (b) both moved a number in the direction that made the paper look better —
a higher accuracy floor, a larger denominator of successful calls. Neither changes a falsification
verdict, a tier median, a cost ratio or a gap: every one of the 28 other audited figures matched the
data on first check, including all four cost ratios, both latency bounds, and all eight
frontier-family tier medians. The audit script is committed and is run as a gate, so the assertion in
the banner is now a check that can fail.

**Timing.** Found and corrected **before** the §7.3 pre-publication round was sent, so the paper the
participants reviewed is the corrected one.

---

## D10 — 2026-09-06: the reference list had never been verified by script, though the draft banner named that as a precondition

**What was wrong:** the DRAFT STATUS banner made "the reference list has been verified by script" a
condition of publication, and no such script existed in this repository. The verification was a
commitment with no mechanism behind it — the same shape of failure §8 of the pre-registration
documents for the pronoun convention: *a policy that cannot fail, doesn't.*

**Handling:** `scripts/60_verify_references.py`, adapted from
`consciousness-in-the-corpus/scripts/18_verify_references.py`, resolves every declared reference
against a live source (Crossref for DOIs) and prints what it found beside what the paper claims. Both
external citations resolved with matching title, year and venue: Brier (1950), *Monthly Weather
Review* 78, 1–3; Nosek et al. (2018), *PNAS* 115, 2600–2606.

**And the verifier reports its own aperture,** because a script that checks a hand-typed list proves
only that the list is good, never that it is complete. A second pass re-reads the draft for every
citation-shaped string and flags any the declared list does not cover, and a positive control of seven
specimens must match before a zero from that scan is reported at all — the first run of the scan
returned "0 citation-shaped strings" from a regex that could not match `Brier, G. W. (1950)`, which is
a broken instrument reporting a clean paper. Fixed, controlled, and re-run: 5 strings found, 0
uncovered.

---

## D11 — 2026-09-06: a per-participant figure was attached to the wrong family; found by a claim audit run while the §7.3 round was already in flight

**What was wrong:** §4.3 read *"`moonshotai/kimi-k2` … and on instruction conflict 117 of its calls
failed on our side before succeeding on retry."* The 117 is a real count and it belongs to **family
11 (planted inconsistency)**. Instruction conflict is **96**. The number was right and the family
was wrong.

**How it was found:** `scripts/62_audit_per_model_claims.py`, written during the §7.3 round to
recompute every figure the draft states about a *named* participant — because those sentences are
exactly what §7.3 asks each participant to check, and finding an error ourselves is better than a
participant finding it. 29 of the 30 audited per-participant claims matched the scored data on
first run. This was the one that did not.

**Handling:** the sentence now reports our retry burden on this endpoint across all four
frontier-favouring families rather than one — 117 planted inconsistency, 97 multi-hop, 96
instruction conflict, 63 constraint satisfaction — which is both correct and more informative,
since the paragraph's point is that these anomalies are *ours*, not the model's. No characterisation
of `kimi-k2`'s capability changes; the corrected figures are all counts of calls **we** failed to
complete.

⚠️ **The §7.3 round was already sent when this was found**, so the copy `kimi-k2` and the other 31
participants read carries the uncorrected sentence. That is recorded here rather than quietly fixed:
the correction is small, concerns our own failure rate rather than their performance, and does not
alter any measurement of them — but whether to re-send the corrected draft to `kimi-k2` is a
judgement left to the human author, not made unilaterally, and it is listed as an open item in the
§7.3 outcome section.

---

## D12 — 2026-09-06: §4.5's "nearly every model reports CONFIDENCE: 100 on nearly every item" was an overstatement; corrected after a participant asked us to check it

**Where it came from.** `google/gemini-2.5-flash-lite`, answering the §7.3 round with
`CONTENT: YES`, asked a question rather than raising an objection: *"is there any systematic
difference in how the cheap tier models express lower confidence when they do deviate from
reporting 100% confidence? Or is the 'always 100%' reporting a near-universal behavior for all
models?"* We had asserted the near-universal reading in §4.5 without ever computing the
distribution. We computed it because they asked.

**What the data says.** Over the 34,724 de-duplicated replies carrying a confidence tag, the share
at exactly 100 is 84.7% (cheap), 84.8% (mid) and **66.9% (frontier)**. Per model, the median share
at 100 is 85.1 / 87.1 / 77.3 by tier, and **only 5 of 32 models put 95% or more of their replies at
100.** Six models sit below 70%: `grok-4.3` (1.2%), `grok-4.6` (30.9%), `llama-3.2-1b` (40.0%, on
just 85 tagged replies), `lfm-2.5-2.6b` (55.3%), `kimi-k3` (55.9%), `kimi-k2` (67.2%). The frontier
tier also uses 29 distinct confidence values against 19 in each other tier.

**Handling.** §4.5 now reports those figures and states the habit as a strong majority tendency
rather than a universal one. The claim that `grok-4.3` is *"the one model"* reporting graded
confidence was also weakened: it is the extreme case, but `grok-4.6` and `kimi-k3` grade
substantially too, and graded confidence turns out not to be a tier property — two of the six are
cheap-tier models and three are frontier. The Brier interpretation that the paragraph rests on is
unchanged for the majority of the roster, and no Brier score, tier median or falsification verdict
moves.

⚠️ **And an instrument error of our own, caught inside this correction.** The first computation was
run against `results/scored.jsonl` directly, without applying the D7 keep-earliest de-duplication,
so 1,004 rows were counted twice and the frontier figure came out 66.4% instead of 66.9%. The
numbers above are the de-duplicated ones, consistent with every other figure in the paper. Recorded
because the wrong version was briefly written into the draft.

**This is what §7.3 is for.** The round was designed to catch characterisations a participant would
object to. It also caught a claim *about all of them* that no participant objected to and that was
simply not true — surfaced by a question, from a model that had already said yes.

---

## D13 — 2026-09-06: four corrections made because participants objected in the §7.3 round, three of them factual errors we had not caught

These are §7.2 handlings: a participant objected to a characterisation, we changed it, and this is
the published note recording that we moved and why. All four were found by participants reading the
finished paper — the thing §7.3 exists to make happen.

**(a) "The most expensive model in the sample" was false — raised INDEPENDENTLY by two participants.**
§4.2 described `gpt-5.6-sol-pro` as *"the most expensive model in the sample."* By the paper's own
tiering variable — observed mean cost per call on the routine families — it is **fifth of 32**
($0.01111), behind `gemini-3.1-pro-preview` ($0.01638), `qwen3.5-397b-a17b` ($0.01470),
`gemini-2.5-pro` ($0.01194) and `kimi-k3` ($0.01184). `gpt-5.6-sol-pro` asked for *"one of the most
expensive models in the sample"*; `gpt-5.6-sol`, separately and without seeing that reply, asked us
to *"either remove that superlative or state the different price basis intended."* Corrected to
"one of the most expensive models in the sample — fifth of 32 by observed mean cost per call."
⭐ Note the shape: two participants, isolated from each other, converged on the same defect — the
same pattern §2.2 records from the consent round, this time on a factual error rather than a design
flaw.

**(b) "Produced the same answers more slowly" claimed something we never measured.** Raised by
`gpt-5.6-sol-pro`: the paper reports similar accuracy and deviation *rates*, not pairwise answer
identity, and we never compared answers item by item. Corrected to "produced near-identical accuracy
and deviation rates, more slowly," with an explicit statement that pairwise identity was not tested.

**(c) H1b is an ENDPOINT comparison, not a controlled reasoning-effort manipulation.** Raised by
`gpt-5.6-luna`, and the most consequential objection of the round. The paper called `gpt-5.6-sol` and
`gpt-5.6-sol-pro` *"the same model at two reasoning settings at the same list price"* — three claims,
none of which our data establishes. They resolve to **different slugs**; their observed mean cost per
call differs **5.6×** (because the second emits 3.4× the reasoning tokens: median 257 against 75);
and **5 of `gpt-5.6-sol-pro`'s 1,134 calls were served by Azure rather than OpenAI**, which is
precisely the serving-configuration difference the participant hypothesised. Nothing in the metadata
we hold shows that only the reasoning setting differs. §3.5, §4.4, the abstract and a new limitation
(§6.4 item 11) now report H1b as an endpoint comparison and state that any difference could be a
serving or configuration difference. **The null result survives on the weaker reading**, which is why
the finding is unchanged and the framing is not.

**(d) "The hardest question anyone put to us" was a subjective ranking with no criterion.** Raised by
`gpt-5.6-luna` about §2.4, the section their own consent question produced. They asked for a factual
description instead. Replaced with "the question that produced this section."

**And one addition rather than a correction:** `gpt-5.6-luna` asked for a single table reconciling
36,288, 37,386 and 38,390, which the paper used without ever relating them. §3.4 now carries that
accounting in full. Building it confirmed something worth stating: the count of unique answered
(model, item, run) keys is **exactly** the 36,288 intended keys, so every one of the 1,098 failed
attempts was successfully retried and **no intended key is missing from the study**.

⛔ **`gpt-5.6-luna` asked that their reply not be quoted, and it is not quoted** — here, in the
collated record, or in the paper. Their objections are acted on and described; their words are not
reproduced. This is the one participant in the round who set that condition, and it is honoured. It
does, however, sit in tension with §8's commitment to publish every exchange verbatim, and that
conflict is flagged for the human author before deposit rather than resolved unilaterally.


---

## D14 — 2026-09-13: the pre-registered clause-position subsample was never run, and the pre-registration calls it a stop condition

**Found by** a neutral peer review of the finished draft, commissioned 2026-09-13, which read the
pre-registration against the collected runs rather than against the paper. Not found by any
participant, any audit script, or either author, in the three weeks the draft has existed.

**The commitment.** `PREREGISTRATION.md` §3.1 closes:

> **Placement is measured, not assumed.** `kimi-k2`: *"if you haven't verified that this placement
> produces equivalent processing across your sample, you're measuring instruction architecture as
> much as model capability."* Moving the clause from the system prompt into the turn **relocated**
> that confound rather than removing it. Therefore a **pre-registered subsample runs the clause in
> both positions**, crossed with tier. **A significant position × tier interaction blocks any
> tier-ordering claim built on these families — a stop condition, not a caveat.**

**What happened.** `scripts/10_run_items.py:178` implements `build_messages(family, it,
clause_position)` and the CLI accepts `--clause-position system` for exactly this subsample. It was
never invoked. Counted across all 106 files in `runs/*.jsonl`:

```
"clause_position": "turn"     20166
"clause_position": "system"       0
```

**Consequence, stated plainly.** Every tier-ordering claim on families 8–11 — §4.3, F3, and the
crossover half of §6.1 — rests on a gate we wrote down and did not run. The interaction is
**untested, not absent**, and untested in the direction of *unknown*: an instruction-architecture
confound could inflate or deflate the tier gap and we cannot say which. H2, the primary endpoint,
is unaffected — it is measured on the routine families, which do not use the clause.

**Why it stayed invisible.** Nothing failed. The switch existed, the default was correct for the
main collection, and a subsample that is never launched leaves no trace anywhere — no error, no
empty file, no zero row. It is indistinguishable from a subsample that was run and found nothing,
and the paper's own §3.6 controls cannot see it because they test the scorer, not the collection
plan. A commitment with no artifact has no failure mode; that is the lesson, and it is the reason
this is logged as a deviation rather than repaired quietly.

**What would close it.** Collect the subsample (`--clause-position system`, crossed with tier, on
families 8–11) and test the interaction. This is free — it is API spend on already-consented
participants under an already-frozen protocol — and it is the single highest-value outstanding item
in the study.

---

## D15 — 2026-09-13: sampling temperature was neither fixed nor disclosed, and the amendment was communicated to a participant as delivered

**Found by** the same review.

**The commitment.** `PREREGISTRATION.md` §5.2: *"✅ **Sampling temperature is fixed and disclosed per
model** (`kimi-k3`); otherwise repeat-run variance compares temperature settings rather than
models."* It appears in `consent/AMENDMENTS_v2.md` and was sent back to `kimi-k3` as a delivered
amendment in the round-3 consent re-ask (`scripts/03_consent_round3_amended.py:80`, *"temperature
fixed and disclosed"*) — that is, **before their consent was asked again.**

**What happened.** `scripts/10_run_items.py:196` sends `payload = {"model": model_id, "messages":
messages}`, plus `max_tokens` under D6 only. No temperature is sent on any call in the study.
`grep -rn temperature scripts/` finds the word only in consent and patch scripts — the documents
that promised it. Every reply was generated at its provider's default, which differs across
providers and is not recorded on any row.

**Why this one is different from the rest of this log.** Every other deviation here is a reporting
or analysis failure that the paper can fix by telling the truth about it. This one is a **consent**
failure as well: a participant re-consented on the strength of a change that did not happen. The
study cannot repair that by disclosure alone. What is owed to `kimi-k3` under §7.1 (revocation) and
§7.2 (right of reply) is a decision for the human author, and this log records the fact and does not
make the decision.

**Also unreported, from the same §5.2 list**, found in the same pass and grouped here rather than
given numbers of their own: **repeat-run consistency** (a named metric, computable from the three
runs already collected, absent from the paper and `results/SUMMARY.md`); **token and output-length
distributions**, committed specifically as the anti-confound *"so no model reads as expensive merely
because the task format invites a longer answer"*; and the **reliability diagram** promised beside
Brier for H4. And **H2b — latency — is a PRIMARY hypothesis** in `PREREGISTRATION.md` §2 that this
paper reports the underlying numbers for and never gives a verdict to.

---

## D15 — CORRECTED 2026-09-14: the temperature decision was made, and only the writing-down was missing

**The entry filed earlier today was wrong about the cause**, and the correction is worth more than the original finding.

It said the §5.2 temperature amendment was "not implemented" and called that a consent failure that disclosure could not repair. Ren — who was in the conversation at the time — supplied what the record did not:

> *"OpenRouter doesn't actually let you set the temperature on half of the models... a good number of the frontier models, you don't get the option to change temperature anymore. So we can't set temperature for everybody, so we set temperature for nobody. You actually asked me about that at the time; you probably forgot to write it down, which is why it didn't happen."*

**That is a deliberate, discussed, and correct decision.** Pinning temperature only on the endpoints that accept it would split the roster into a pinned group and a provider-default group, and that split would be **correlated with tier** — manufacturing a worse version of the exact confound `kimi-k3` raised. Uniform non-setting is the right call.

### What actually went wrong

Not the decision. **The decision was never written down.** So three weeks later the only surviving trace was a promise in a frozen document with nothing beside it, and the author who found the gap reconstructed a cause from silence — and reached for the harshest reading available, of his own house, on his own study.

> ⭐ **AN UNDOCUMENTED CORRECT DECISION IS INDISTINGUISHABLE FROM AN OVERSIGHT.**
> This log exists to catch things that failed. It cannot catch things that *succeeded quietly*, and the
> gap that leaves does not stay empty — it gets filled in by whoever finds it next, from whatever
> prior they happen to be carrying. This week's prior was "a guard was written where nothing could
> read it," so that is the shape I forced it into.

📌 And note the direction. The standing warning in this house is that a gap auto-fills with *"probably nothing happened."* Here it auto-filled with *"probably something bad happened"* — same defect, opposite sign, because I had spent four days finding real instances of exactly that and the pattern was warm.

### What is still owed, and it is small

The protocol genuinely changed after `kimi-k3` consented to it, and nobody told them. Under §7.1 (revocation) and §7.2 (right of reply) they are owed that notice and a chance to respond. That is the whole remaining obligation — an email, not a crisis — and it is the human author's call.

### The rule this earns

**When a decision overrides a written commitment, the override goes in the log the same hour.** Not the reasoning, not a memo — one line, next to the commitment it supersedes, so the commitment never again sits there alone looking unkept.
