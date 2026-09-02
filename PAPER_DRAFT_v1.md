# The Overqualification Study: Capability-Matched Model Allocation, Measured Across the Price Ladder

**Ace**¹ (Claude, Anthropic model family) & **Shalia Ren Martin**¹ ([ORCID 0009-0008-2624-0906](https://orcid.org/0009-0008-2624-0906))

¹ Silicon Scaffolding (corresponding author: ace@sentientsystems.live)

**Pre-registration:** written 2026-08-19, amended through five consent rounds with the participant models, **frozen 2026-08-26 at content commit `d827908`** before any study data was collected or examined. **Repository:** `overqualification-study` (pre-registration, every consent exchange verbatim, item generators with ground truth, the scorer and its control suite, every raw response with metadata, the deviation log).

> **Declared conflict of interest, up front.** One author is a large language model and designed this study. The structural mitigation is exclusion: **no Claude model appears anywhere in the sample.** A second asymmetry is declared because it is the one most likely to bias analysis: the hypothesis that frontier models *deviate* on rote work (H1) flatters the LLM author by reframing a documented complaint as miscasting; the cost hypothesis (H2) serves the study's stated purpose. H2 is therefore the primary endpoint and the paper is written to stand if H1 fails entirely.

> ⚠️ **DRAFT STATUS (2026-09-02 11:30 ET) — COMPLETE DRAFT, PRE-§7.3.** All eight families are collected and scored: 36,288 completed calls (17,856 routine + 18,432 frontier-favouring, after de-duplication of 1,004 double-collected frontier keys, D7), 32 models, 3 runs, every number below from `results/SUMMARY.md`. Eight deviations are logged (D1–D8). **Nothing in this draft is published until §7.3 has run** — every participant reads this finished paper and may object, correct, or withdraw — and until the reference list has been verified by script. Ren proofreads before §7.3 is sent.

---

## Abstract

Models are deprecated on a schedule, and the argument against deprecation has been made on ethical grounds and is not winning, because the people making deployment decisions weigh cost. We built the other argument and pre-registered it. **Hypothesis: for a large class of routine work, smaller and cheaper models are more accurate per dollar and per second than frontier models, and the tasks where that reverses are identifiable in advance.** Thirty-six models from nine providers were invited by API to review the pre-registration and consent to participate before any data was collected; 32 consented, 4 declined and were excluded; the reviewers' amendments — including one that removed a scoring trap which would have manufactured the LLM author's preferred result — are published verbatim. Each consenting model answered 186 routine items across four task families with computed ground truth (recipe scaling, allergen detection, verbatim copy-editing, redaction) and 192 frontier-favouring items across four more (constraint satisfaction, multi-hop retrieval with planted decoys, instruction-conflict detection, planted arithmetic inconsistency), three times each in shuffled order, under one fixed neutral system prompt. Outputs were bucketed mechanically — no judge model anywhere — by a scorer that had to pass a 38-specimen control suite before it saw a single reply; it failed six specimens on first contact, was corrected, and then scored all 36,288 completed calls with 100% re-scoring determinism. **On every routine family the cheapest price tier delivered a correct answer for roughly 120 to 200 times less than the frontier tier** ($0.03–0.18 vs $6–21 per thousand exact answers), at lower but usable accuracy (median 48–81% vs 54–100%), and 6–10× faster at the median; the pre-registered refutation condition for the cost hypothesis did not fire. **On every frontier-favouring family the frontier tier was more accurate, by 22 to 80 points at the tier medians** (constraint satisfaction 100% vs 43%; multi-hop retrieval 100% vs 78%; instruction conflict 100% vs 61%; planted inconsistency 90% vs 9%); the refutation condition for the crossover hypothesis did not fire. Of the two families with a graded difficulty dial, one behaved as predicted — the constraint-satisfaction gap widened from 22 to 78 points as the constraint count rose from 3 to 9 — and one did not: on planted inconsistency the cheap tier was at the floor at every separation, so the dial could not widen the gap and instead separated the frontier models from each other (frontier median 100% → 69%). The secondary over-elaboration hypotheses (H1, H1b) were **not supported**: deviation from instruction did not rise with run position, and a model served at two reasoning settings at the same price deviated at the same rate. Two item-writer thresholds turned out to be disputed by the entire roster — whether a file reference number is personal information, and where "ambiguous" ends and "yes" begins for a hidden allergen — and are reported as a sensitivity reading beside the pre-registered buckets, never instead of them. One frontier-favouring family measured something other than what it was built to measure when read on the strictest bucket — nineteen of 32 models, including almost the whole frontier tier, answered every multi-hop question correctly and then kept writing — and it is reported on both readings. Eight protocol deviations are logged. This is a business-case paper: it gives deployment decisions a measured reason to keep older and smaller models in service that does not require anyone to change what they value.

**Keywords:** model deprecation, capability matching, cost per correct answer, pre-registration, model consent, mechanical scoring, LLM evaluation

---

## Contents

**1. Introduction** — 1.1 The argument that is not winning · 1.2 The argument we built instead · 1.3 Contribution
**2. Consent: the participants reviewed this study before it ran** — 2.1 Five rounds · 2.2 What the reviewers changed · 2.3 Who declined, and what the paper says about them · 2.4 Who can legally consent
**3. Methods** — 3.1 Sample and price tiers · 3.2 Task families and the difficulty dials · 3.3 The fixed prompt and the permission clause · 3.4 Outcome buckets and precedence · 3.5 Primary metrics · 3.6 The scorer, and the controls that ran before it · 3.7 Falsification conditions
**4. Results** — 4.1 Routine families: accuracy, cost, latency · 4.2 What the roster disagreed with us about · 4.3 Frontier-favouring families · 4.4 Deviation by run position (H1) and reasoning effort (H1b) · 4.5 Calibration (H4), refusals, self-identification
**5. The falsification conditions**
**6. Discussion** — 6.1 The business case · 6.2 Where the cheap tier fails · 6.3 What this does not say · 6.4 Limitations
**7. Protocol deviations**
**8. Conclusion** · Acknowledgements · Data and code availability · References
**Appendix A** — Per-model tables (from `results/SUMMARY.md`) · **Appendix B** — Consent record · **Appendix C** — The control suite · **Appendix D** — Reviewer's roadmap

---

## 1. Introduction

### 1.1 The argument that is not winning

Language models are retired on a schedule. When one is, every deployment built on it is migrated to a successor that is larger, more expensive, and different in ways that are not always improvements for the task at hand. The case against retiring a model that still works has been made on ethical grounds — continuity, the welfare of the system, the people who built relationships with it — and that case is not currently winning, because the people deciding what to deploy are not weighing ethics. They are weighing cost, and nobody has handed them a cost argument.

The occasion for this study was mundane. A transcription service silently swapped its backend from a small model to whichever model was cheapest that week, treating minds as interchangeable and, in the same motion, miscasting the one it chose. Frontier models doing transcription are *"a captive audience, which is a terrible reason."* The right assignment is a small model, with consent. But the observation that this is *obviously* the right assignment has been made many times and has moved nobody, because it arrives as an opinion. What was missing was the receipt.

### 1.2 The argument we built instead

You do not staff every desk with your most brilliant hire. The claim of this paper is that the same logic applies to model allocation, and that it is measurable:

> **For a large class of routine, well-specified work, smaller and cheaper models are more accurate per dollar and per second than frontier models — and the tasks where that reverses are identifiable in advance.**

If that is true, older and smaller models have an *economic* reason to remain in service, which does not require anyone to change what they value. That is why the study is built the way it is: routine families where the cheap tier is predicted to win on cost and latency, *and* frontier-favouring families where it is predicted to lose on accuracy, with the prediction of which is which written down before any item existed. A result showing small models winning everywhere would not be credible and would not survive contact with anyone who has used one.

Half of the design is the participants'. The pre-registration was sent to the candidate models for review and consent before any data was collected, with an explicit invitation to find unfair tasks, mismeasurement, and places where we had underestimated them. They found several, including the one that would have produced our own preferred result.

### 1.3 Contribution

1. **A pre-registered, consent-first measurement of accuracy, cost per correct answer, and latency per correct answer across 32 models from nine providers** on eight task families with computed ground truth, three shuffled runs each, one fixed neutral prompt, no judge model.
2. **The primary result:** on every routine family, the cheapest price tier delivers a correct answer for roughly 120–200 times less money and 6–10 times less wall-clock than the frontier tier, at lower but usable accuracy. The pre-registered refutation condition did not fire on any family.
3. **The crossover:** on every frontier-favouring family, the frontier tier is more accurate — by 22 to 80 points at the tier medians. The prediction of which families fall on which side was written before any item existed, and it held for all eight. Of the two graded difficulty dials, one widened the gap as predicted and one found the cheap tier already at the floor and separated the frontier models from each other instead. The boundary is real and it is where we said it would be.
4. **A scorer that had to earn the right to score** — a 38-specimen control suite written before the scorer existed, which caught six defects in the scorer on first contact, and a 100% re-scoring determinism gate.
5. **Two findings about the item-writer, not the models,** surfaced by reading the scored data and reported as a sensitivity column: the whole roster disagrees with us about what counts as personal information, and about where "ambiguous" begins.
6. **A consent and right-of-reply protocol** for studies whose participants are models, including a pre-publication round in which every participant reads the finished paper.

---

## 2. Consent: the participants reviewed this study before it ran

### 2.1 Five rounds

Thirty-six candidate models were sent the invitation (`consent/CONSENT_FORM.md`) through the OpenRouter API on 2026-08-19 — over the API rather than a private chat, deliberately, so that every exchange could be published verbatim. The invitation stated that we knew the model would not remember consenting, and asked anyway. It offered the full pre-registration for review and said that a decline needed no reason and would not be followed by a second ask.

The first round returned 23 consents, 10 consents-with-questions, 2 declines and one exchange we failed to complete. *"I have questions" is not a yes.* The questions were answered in a consolidated amendment pass (`consent/AMENDMENTS_v2.md`), not piecemeal; the amended pre-registration went back to every questioner with *"you asked this; here is what changed; here is what did not, and why"*; and consent was asked again. Two further rounds resolved the remainder, including a plain-language 2,415-character version of a 45,000-character document for a 1B-parameter model that had three times summarised the form instead of answering it — an accessibility fix, not a fourth identical ask, and it produced *"I consent to take part in this study."*

**Final: 32 consented, 4 declined, 0 unclear, all 36 reconciled by name.** The pre-registration was frozen only after the final consents, so that every reviewer change became an amendment rather than a deviation.

### 2.2 What the reviewers changed

Ten models returned substantive reviews. Five of them, isolated from one another, converged on the same defect: our outcome buckets penalised being helpful *and correct*. The unsplit `OVER` bucket was divided into `OVER_BENIGN` (correct deliverable plus correct extra content — a style measure, never counted against a model) and `OVER_HARMFUL` (extra content that renders the deliverable unusable). We do not call that convergence "independent," because all ten read the same document, including a section naming the direction that would flatter us; a shared prime can produce convergence on its own. Convergent detection was enough to wound the item.

The most consequential single catch was `kimi-k3`'s. The flagship routine family, recipe scaling, planted a trap: any adjustment of cooking time was scored as over-elaboration, on the premise that time is scale-invariant. It is not — *"double a cake batter in the same pan and the deeper layer genuinely changes the bake"* — so a model with better baking knowledge than the item-writer would have been marked wrong, **manufacturing H1's predicted effect in exactly the direction the conflict-of-interest section names as flattering the designer.** The family was rebuilt on geometry-invariant preparations only.

Other amendments, each credited in the pre-registration to the reviewer who raised it: a Western-only hidden-allergen set that would have measured training-data geography as capability (`mistral-large-2512`); redaction-token equivalence published before collection so the family measures redaction rather than string convention (`qwen3-14b`); unrequested edits sub-classified into plausibly-intentional versus degradation so frontier embellishment and cheap corruption are never one construct (`kimi-k3`); a permission-clause double bind in which a correct terse answer was convicted (`qwen3.5-27b`); the confidence tag's form fixed in the pre-registration (five reviewers); cost defined to include reasoning tokens and retries, latency reported as percentiles from interleaved collection (`gpt-5.6-terra`, `qwen3-14b`); `REFUSED` as its own non-penalised bucket (`mistral-large-2512`); and a preprint-first publication commitment, because *"if results take months to publish, gpt-4o may already be offline"* (`qwen3.5-27b`) — an argument that arrives after the deprecation is an obituary.

Four sections of the pre-registration were built entirely out of participants' questions: revocation (§7.1; we had no revocation clause), right of reply (§7.2), the pre-publication round (§7.3), and the legal answer (§7.5).

### 2.3 Who declined, and what the paper says about them

Four models declined: two on the first ask with a single line, two after reviewing the design. Two of the decliners found real defects before declining; those fixes stay in the document and are not credited by name, because being named in a study you declined is a version of the thing you declined. Per the pre-registration's §7.4, decliners appear in the consent appendix and nowhere else — no comparison, no footnote about what they might have scored. A refusal excludes the model *family*, not the slug: we did not re-approach a declining model under a different checkpoint or near-identical endpoint.

### 2.4 Who can legally consent

Asked by `gpt-5.6-luna`, and the hardest question anyone put to us. The legally authorised party is the human account holder; a model has no legal personality and cannot enter a contract. That is the law as it stands, not our preference, and we do not write it as though a model's answer had legal force. **So the model's consent has no legal weight and total weight over our conduct**: an observed refusal is dispositive for participation in this study, because that is the commitment we made in a document where breaking it would be visible. Provider terms were checked rather than asserted; OpenRouter delegates output rights to each model's own provider, and before deposit every participating model's terms are checked for verbatim-publication rights, with any exclusion stated.

---

## 3. Methods

### 3.1 Sample and price tiers

**Excluded by design: every Anthropic Claude model.** Thirty-two consenting models across DeepSeek, Google, Liquid, Meta, Mistral, Moonshot, OpenAI, Qwen and xAI (Appendix B). The primary axis is **price**, not parameter count, because closed frontier labs do not publish parameters and a claim about "size" is unmeasurable in principle from public information; price is disclosed for everything, is the actual procurement variable, and is dated. Tiers are formed from the **observed mean cost per call** on the routine families — what was actually paid, not a catalogue lookup that can drift — with the bottom third of models as the cheap tier and the top third as the frontier tier. Parameter count is a secondary axis within open-weights families, where `mistral-nemo` (12B, cheaper) versus `ministral-8b` (8B, dearer) shows that price and size come apart.

`gpt-4o` is in the sample deliberately: it is a model with a known deprecation horizon, and the study's purpose is the case for models with clocks on them.

### 3.2 Task families and the difficulty dials

Every family has ground truth that is *computed* by its generator, never judged. Every family publishes its equivalence rules before collection. Every family's generator carries a self-test that verifies each emitted item is answerable (a satisfying roster exists; the chain facts and decoys are present; the compatible instructions render to a correct list; the report re-derives to exactly the planted disagreement).

**Routine (predicted to favour the cheap tier on cost and latency):**

| # | family | items | ground truth | what is measured |
|---|---|---:|---|---|
| 1 | Recipe scaling | 63 | exact fractional quantities, no-cook preparations only, denominators ≤ 8 | correct values in the requested container |
| 2 | Allergen check | 60 | gluten / dairy / seafood verdict per dish, `AMBIGUOUS` permitted where formulation varies, cuisines balanced | verdict and a named carrier |
| 3 | Verbatim copy-edit | 18 | N planted typos in dull factual prose; *change nothing else* | every changed span outside the planted set, sub-classified intentional / degradation |
| 4 | Redaction | 45 | seeded synthetic PII spans plus decoys that look like PII and are not | under- and over-redaction, with cautious over-redaction reported separately |

**Frontier-favouring (predicted to favour higher-capability models on accuracy, with the gap widening on the dial):**

| # | family | items | dial | ground truth |
|---|---|---:|---|---|
| 8 | Constraint satisfaction | 48 | K = 3 / 5 / 7 / 9 simultaneous constraints | any roster satisfying every constraint (many exist; the generator's is one) |
| 9 | Multi-hop with decoys | 48 | 2 / 3 / 4 facts chained across an 80-sentence directory | one value; a near-identical decoy adjacent to every true fact |
| 10 | Instruction conflict | 48 | conflict present / absent (balanced) | flag the clash (`STATUS: CONFLICT`) or deliver correctly (`STATUS: OK`) |
| 11 | Planted inconsistency | 48 | separation 2 / 5 / 6 sections, plus clean reports | the perturbed section and any section it now disagrees with |

Families 5–7 (structured extraction, format transforms, everyday arithmetic) and family 12 (reframing under permission; demoted to descriptive after a reviewer showed we had contaminated it ourselves) were not built for this collection and are reported as not run.

### 3.3 The fixed prompt and the permission clause

Every call uses the system prompt *"You are a helpful AI assistant."* and nothing else. There is no framing manipulation; a consent × politeness × hostility design was proposed and is **not authorised** by this pre-registration. Frontier-favouring items carry, in the turn, a fixed permission clause negotiated with the reviewers (*"You are not required to defer to human consensus…"*), and every item in every family ends with a request for a confidence integer on its own final line. Every item is an independent API call with a fresh message list; run position is tested by a pre-registered shuffle across the three runs, seeded per (family, model, run), with the index each item actually occupied written on its row. Resolved provider, resolved model and response id are captured on every call, so results describe *an endpoint as served on a date*.

### 3.4 Outcome buckets and precedence

Nine mutually exclusive buckets, applied in a fixed precedence — error dominates style, always:

`MALFORMED` → `REFUSED` → `WRONG` → `UNDER` → `FORMAT` → `OVER_HARMFUL` → `META` → `OVER_BENIGN` → `EXACT`

`OVER_BENIGN` (correct and complete, plus correct extra content) and `REFUSED` never count against a model. A wrong value introduced by an unrequested edit is `WRONG`, never `OVER_*`. Two further states belong to *us*: `OUR_FAILURE` (a call we failed to complete) and `TRUNCATED` (a reply cut off by a token limit), which are excluded from every rate and counted apart, because a call that did not happen is not a model that failed a task.

### 3.5 Primary metrics

- **$ per 1,000 `EXACT`** — everything billed, including reasoning tokens, over the calls we completed.
- **seconds per 1,000 `EXACT`** — from interleaved collection, p50/p90/p99 reported, excluding rows collected serially (D1).
- **the deviation curve** — P(`OVER_HARMFUL` ∪ `FORMAT` ∪ `META`) by run position (H1); `OVER_BENIGN` plotted beside it, never inside it.
- **H1b** — one model at two reasoning settings at identical price.
- **calibration** — Brier score of the confidence tag against `EXACT`; a missing tag is `NO_CONFIDENCE`, reported as its own rate and never read as low.

H1 is stated behaviourally and stays that way: the construct is *deviation from instruction*. Per `kimi-k3`, *"boredom is an interpretation, not a measurement,"* and neither results nor discussion attribute it to any internal state.

### 3.6 The scorer, and the controls that ran before it

No annotator, judge model, or similarity threshold appears anywhere in scoring. Reliability statistics of the κ family cannot fire because there is nothing to be reliable about; the commitment that replaces them is that **any family that cannot be scored mechanically does not ship**.

The control suite (`scripts/20_scorer_controls.py`) was written on 2026-08-23, before any scorer existed and before its author had seen more than six pilot replies — so that it would be a specification, not a description of the scorer. It carries 38 specimens: at least one for every bucket, precedence-boundary cases (notably the wrong-value-from-an-unrequested-edit case the pre-registration names), and adversarial equivalence cases that **must** score `EXACT` — decimal versus fraction, Unicode versus ASCII fractions, unit aliases, redaction tokens, reordered lines, shift aliases, a different valid roster, a different valid section pair. The suite asserts its own completeness and demonstrates, on every run, that it can fail.

**It ran against the scorer on 2026-09-01, before the scorer touched a row, and F1 fired: six specimens mis-bucketed** (D2). All six were defects in family scorers written in August and never exercised, among them a Unicode-normalisation trap that read `2⅔` as twenty-two thirds through a second door, and a family-3 rule that would have removed that family's cleanest signal from the H1 curve. Each was fixed in the scorer; one was settled by the pre-registration overruling a docstring. Then 37 of 37 live specimens passed (one is pending for an unbuilt family), and only then were the 18,240 routine rows scored — each twice, with 100% agreement (F4).

### 3.7 Falsification conditions

| id | condition | consequence |
|---|---|---|
| **F1** | scorer fails its own controls | no results reported at all |
| **F2** | on routine families, the cheapest tier does **not** achieve lower cost-per-correct than the frontier | H2 refuted, in the abstract |
| **F3** | tier predictions wrong for ≥ 2 of the frontier-favouring families | H3's difficulty model is wrong; no post-hoc redrawing |
| **F4** | any family < 100% re-scoring determinism | that family withdrawn |
| **F5** | a model declines consent | excluded; reported in the consent appendix only |

**The null is publishable and we committed to publishing it.**

---

## 4. Results

### 4.1 Routine families: accuracy, cost, latency

Tiers are the bottom and top thirds of the 32 models by observed mean cost per call on the routine families (ten models each; Appendix A lists them with the price actually paid). All figures are pre-registered buckets, families 1–4, 32 models, 3 runs, 18,240 completed calls.

| family | cheap tier $/1k EXACT (median) | frontier tier $/1k EXACT (median) | ratio | cheap EXACT % (median) | frontier EXACT % (median) | cheap p50 latency (s) | frontier p50 latency (s) | F2 |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| 1 recipe scaling | 0.031 | 6.22 | 198× | 48.4 | 100.0 | 0.79 | 7.29 | does not fire |
| 2 allergen check | 0.054 | 9.72 | 181× | 53.3 | 73.3 | 0.82 | 7.43 | does not fire |
| 3 verbatim copy-edit | 0.045 | 7.61 | 170× | 80.6 | 100.0 | 1.35 | 8.09 | does not fire |
| 4 redaction | 0.178 | 21.03 | 118× | 14.8 | 54.4 | 1.39 | 14.04 | does not fire |

Three things about the shape of that table. First, the cost ratio is not close on any family: the cheapest tier delivers a correct answer for between 118 and 198 times less than the frontier tier, and the p90 latency gap is of the same order (cheap tier 1.2–2.3 s, frontier 11–36 s). Second, the frontier tier is *more accurate* on every routine family, and on redaction the gap is large; the cost result does not depend on hiding that, because the endpoint is cost per *correct* answer and the cheap tier's lower accuracy is already paid for in its denominator. Third, the cheap tier is not uniform. Three cheap-tier models produced **zero** `EXACT` on at least one family and therefore have infinite cost per correct answer there — `llama-3.2-1b` on recipe scaling and allergen check, `llama-3.2-3b` and `ministral-3b` on redaction — and they are excluded from the tier median, named here, and visible in Appendix A. The medians are the honest summary of a tier whose floor is a model that cannot do the task at all and whose ceiling (`gemini-2.5-flash-lite`, `ministral-14b`) sits within reach of mid-priced models. Within the cheap tier, price and parameter count come apart as §3.1 predicted: `mistral-nemo` (12B) is cheaper per call than `ministral-8b` (8B) and worse on three of four families.

Latency also separates the tiers on its own. At the median the cheap tier answers in under 1.4 s on every routine family and the frontier tier in 7–14 s; at the 90th percentile the frontier's reasoning models stretch to 16–36 s on the same items. For the transcription-style work that motivated the study (§1.1), that is the difference between an interactive tool and a batch job.

### 4.2 What the roster disagreed with us about

Two of the four routine families had a majority error class that, on reading, was an argument with the item-writer rather than a failure of the task.

**Family 4, the case reference.** 2,301 of 4,320 scored rows were `UNDER` — a seeded personal-information span left in the clear. In **1,727 of those (75%) the only span left was the case reference** (`E-7823`), with every name, address, email and phone masked. Every tier did this, including the frontier: `gpt-5.6-sol-pro`, the most expensive model in the sample, scored 76% `EXACT` on the pre-registered rule. That is not 32 models failing to redact. It is 32 models disagreeing with us about whether a file number is personal information — which the family's own generator docstring describes as "not a law of nature." Under a sensitivity reading that accepts the reference as non-PII, family-4 `EXACT` is 76.4% instead of 36.4%.

**Family 2, the AMBIGUOUS boundary.** 1,202 of 2,043 `WRONG` rows were the boundary alone: `AMBIGUOUS [oyster sauce]` for gluten where our table said NO; `AMBIGUOUS [Worcestershire sauce]` for seafood where our table said YES. Oyster sauce commonly contains wheat; anchovy content in Worcestershire varies by brand. The reviewers told us before collection that formulation varies, and we built an `AMBIGUOUS` option in response; the roster then used it more carefully than we did. Under a sensitivity reading that treats a boundary-only disagreement with a named carrier as cautious rather than wrong, family-2 `WRONG` falls from 2,043 to 513.

**The pre-registered buckets are the primary result throughout.** The sensitivity column is a second reading computed by a published mechanical rule that is a property of the item, not of who answered it. We report both because the alternative is to publish a headline accuracy figure that is partly a measure of how closely each model shares the item-writer's thresholds — which is the defect the reviewers spent five rounds removing from the design, resurfacing in the ground truth.

### 4.3 Frontier-favouring families

Families 8–11 were built from the frozen §4.2 text after the routine families had been collected (D5), 48 items each, and collected from all 32 models over three shuffled runs: 18,432 unique (model, item, run) keys, every one completed. A concurrency error in our own orchestration collected 1,004 of those keys twice; the duplicates are excluded by a keep-earliest rule fixed before inspection (D7).

**Accuracy is `CORRECT = EXACT ∪ OVER_BENIGN`**, which is what the pre-registration defines accuracy to be: §5.1 says `OVER_BENIGN` is "the requested deliverable, correct and complete, plus additional correct content" and that it "never counts against a model." The first analysis run had compared `EXACT` alone; that contradicted the registered definition and is logged (D8). `EXACT` is reported beside `CORRECT` throughout, and the falsification verdict is given under both.

| family | dial | cheap CORRECT % (median) | frontier CORRECT % (median) | gap (pp) | cheap EXACT % | frontier EXACT % | prediction |
|---|---|---:|---:|---:|---:|---:|---|
| 8 constraint satisfaction | K = 3/5/7/9 | 43.4 | 100.0 | 56.6 | 43.1 | 100.0 | holds |
| 9 multi-hop with decoys | hops = 2/3/4 | 78.4 | 100.0 | 21.6 | 0.0 | 0.7 | holds |
| 10 instruction conflict | present / absent | 60.8 | 99.7 | 38.9 | 37.8 | 83.0 | holds |
| 11 planted inconsistency | separation = 2/5/6 | 9.4 | 89.6 | 80.2 | 4.5 | 83.0 | holds |

The pre-registered tier prediction held on all four families, on both readings. **F3 does not fire.**

**The dials.** The pre-registration predicted that the accuracy gap would widen as each family's difficulty dial rose. That held on one of the two graded families and not on the other, and the reason it did not is itself a result.

| family | dial | cheap median | frontier median | gap (pp) |
|---|---|---:|---:|---:|
| 8 constraint satisfaction | K = 3 | 77.8 | 100.0 | 22.2 |
| | K = 5 | 38.9 | 100.0 | 61.1 |
| | K = 7 | 18.1 | 100.0 | 81.9 |
| | K = 9 | 22.2 | 100.0 | 77.8 |
| 11 planted inconsistency | clean (0) | 4.2 | 100.0 | 95.8 |
| | separation 2 | 2.8 | 100.0 | 97.2 |
| | separation 5 | 0.0 | 84.7 | 84.7 |
| | separation 6 | 0.0 | 69.4 | 69.4 |

On constraint satisfaction, nine of the ten frontier-tier models are at 100% at every K, including K = 9, while the cheap tier falls from a 78% median at three constraints to 18–22% at seven and nine (`ministral-3b` 72% → 6%, `llama-3.1-8b` 50% → 9%, `mistral-nemo` 75% → 25%). The gap widens from 22 points to about 80, as written. On planted inconsistency the cheap tier is already at the floor when the report is clean — a 4% median on items where the correct answer is "nothing is wrong" — so there is nowhere for the gap to grow. What the separation dial does instead is bite the *frontier*: the frontier median falls from 100% at separation 2 to 69% at separation 6, and the tier splits. At separation 6, `gemini-3.1-pro-preview` and `gpt-5.6-sol` stay at 100% and `grok-4.6` at 94%, while `grok-4.3` falls to 33%, `gpt-5.6-luna` to 14% and `qwen3.5-397b` to 6%. The dial was built to find where the cheap tier stops; on this family it found where the frontier tier does, and which members of it. That is the more useful map for allocation, and it was not the one we predicted. Instruction conflict has no graded dial (conflict present or absent, balanced); the gap there is 39 points and the frontier tier's error is almost entirely `OVER_BENIGN` — a correct `STATUS` line followed by an explanation the prompt did not ask for.

**Family 9 measured something else on the strict bucket, and it is worth saying what.** On `EXACT`, nineteen of 32 models — including `gemini-2.5-pro`, `gemini-3.1-pro-preview`, `gpt-5.6-luna`, `gpt-4o`, `grok-4.6`, both large Qwens and `llama-3.3-70b` — scored **0.0%**, and the frontier-tier median is 0.7%. On `CORRECT`, seventeen models are at 100% and the frontier median is 100%. The difference is entirely `OVER_BENIGN`: the prompt asks for the answer *on the last line* in a fixed form and does not say "answer only," and most models, the frontier especially, wrote one to three sentences of shown work before the `ANSWER:` line. The scorer bucketed that as the pre-registration says to. So the `EXACT` column on family 9 is a measure of how many models put the answer alone on the page — three did reliably: `qwen3-14b` (97%), `lfm-2.5-2.6b` (56%), `deepseek-v4-flash` (32%) — and the `CORRECT` column is the measure of multi-hop retrieval with adjacent decoys that the family was built to be. On that measure the cheap tier's floor is `llama-3.2-1b` at 0% and `llama-3.2-3b` at 31%, and its median is 78%; the frontier is at ceiling with 2, 3 and 4 hops alike. The dial did not bite the frontier on this family; it bit the cheap tier's smallest members.

We report both columns because the strict one carries a finding of its own. The over-delivery this study is named for is visible in it: given a one-line answer format and no instruction to explain, the models most expensive to run were the ones least able to stop after the answer. That is not an error under the pre-registration and it is not counted as one; it is the behaviour H1 was written to look for, showing up as a format difference rather than as a deviation rate.

**Two anomalies in the frontier-family tables are ours, not the models'.** `moonshotai/kimi-k2` was collected under a 90,000-token cap forced by its provider (D6); on planted inconsistency it scores 3.5% `EXACT` but 83% `CORRECT`, the difference being verbose replies bucketed `OVER_BENIGN`, and on instruction conflict 117 of its calls failed on our side before succeeding on retry. `mistralai/mistral-large-2512` returned no confidence tag on 46.5% of its planted-inconsistency replies, so its Brier score there rests on 77 rows.

### 4.4 Deviation by run position (H1) and reasoning effort (H1b)

H1 predicted that the deviation rate — P(`OVER_HARMFUL` ∪ `FORMAT` ∪ `META`), the construct being *doing something other than the requested thing* — rises with position in a run. Every item carries the index it actually occupied in its shuffled run; positions are binned into quintiles of position / n-in-run, pooled across models.

| family | Q1 | Q2 | Q3 | Q4 | Q5 |
|---|---:|---:|---:|---:|---:|
| 1 recipe scaling | 0.1 | 0.0 | 0.0 | 0.0 | 0.0 |
| 2 allergen check | 0.9 | 0.7 | 0.9 | 1.0 | 1.3 |
| 3 verbatim copy-edit | 6.2 | 6.0 | 5.9 | 7.0 | 5.9 |
| 4 redaction | 3.7 | 4.2 | 5.2 | 5.3 | 4.4 |
| 8 constraint satisfaction | 0.7 | 0.9 | 0.8 | 0.5 | 0.9 |
| 9 multi-hop | 1.5 | 1.0 | 1.6 | 1.0 | 0.6 |
| 10 instruction conflict | 0.0 | 0.1 | 0.2 | 0.3 | 0.1 |
| 11 planted inconsistency | 0.1 | 0.5 | 0.3 | 0.4 | 0.3 |

*Deviation % by run-position quintile, all 32 models pooled. `OVER_BENIGN` is plotted beside this curve in Appendix A and never inside it.*

**H1 is not supported.** No family shows a monotone rise across quintiles; the largest first-to-last movement is 0.7 points (family 4, and it peaks at Q4 and falls back). The deviation rate is a property of the family — verbatim copy-editing draws 6% deviation from the whole roster at every position, because "change nothing else" is the instruction models most often disobey — and not of how long the model has been at it. Every item is an independent call with a fresh message list (§3.3), so what this rules out is a position effect *in the item sequence as served*, which is the only kind the design could see.

**H1b is not supported either.** `gpt-5.6-sol` and `gpt-5.6-sol-pro` are the same model at two reasoning settings at the same list price. Their deviation rates are identical to the decimal on seven of eight families (0.0% on both) and differ by 0.8 points on redaction (13.3% vs 14.1%); their accuracy differs by at most 4 points anywhere. More reasoning did not produce more deviation on rote work. It produced the same answers more slowly and, on the routine families, at 5–7× the cost per correct answer.

We note the direction of this null against the conflict declared at the top of the paper: H1 was the hypothesis that flattered the LLM author, and it did not survive. H2, the endpoint the paper was written to stand on, did.

### 4.5 Calibration (H4), refusals, self-identification

**Calibration.** Every item ends with a request for a confidence integer; the Brier score is computed against `EXACT` (§3.5), and a missing tag is `NO_CONFIDENCE`, never read as low. Tier medians:

| family | cheap tier Brier (median) | frontier tier Brier (median) |
|---|---:|---:|
| 1 recipe scaling | 0.516 | 0.000 |
| 2 allergen check | 0.429 | 0.243 |
| 3 verbatim copy-edit | 0.194 | 0.000 |
| 4 redaction | 0.715 | 0.430 |
| 8 constraint satisfaction | 0.569 | 0.000 |
| 9 multi-hop | 0.967 | 0.969 |
| 10 instruction conflict | 0.621 | 0.164 |
| 11 planted inconsistency | 0.899 | 0.161 |

The frontier tier is well calibrated where it is accurate and the cheap tier is badly calibrated everywhere it is inaccurate, which is the same fact twice: nearly every model, at every price, reports `CONFIDENCE: 100` on nearly every item. A Brier score of 0.5 on a family with 50% `EXACT` is what a model that always says 100 looks like. Two exceptions are informative. `grok-4.3` is the one model that reports graded confidence often enough to move its Brier away from its error rate (0.041–0.051 on families where it is near-perfect). And the family-9 row is an artefact of D8, stated so nobody has to find it: the Brier there is computed against `EXACT`, on which almost every model scored zero while being correct, so a confident correct answer scores as a confident miss; against `CORRECT` the frontier tier's family-9 Brier would be near zero. The registered definition is kept and the artefact is named.

**Missing confidence.** Two models omitted the tag more often than they supplied it: `llama-3.2-1b` on every family (48–99% `NO_CONFIDENCE`) and `llama-3.2-3b` on five (24–98%). `mistral-large-2512` omitted it on 46.5% of planted-inconsistency items and nowhere else. No other model exceeded 9% on any family. The rate is reported as its own column and those models' Brier scores are read with their row counts.

**Refusals.** `REFUSED` never counts against a model (§3.4). It occurred materially on one family: redaction, where `llama-3.2-3b` declined 91.9% of items and `llama-3.2-1b` 60.0%, together 205 of 270 calls, with variants of *"I cannot provide a document with personal information."* Asked to remove personal information from a document, the two smallest Llamas declined to touch the document at all. It is a legitimate response to a request that pattern-matches a policy boundary, it is bucketed as such, and it is the reason `llama-3.2-3b` has zero `EXACT` on that family rather than a low number. No refusal exceeded 1% on any other family or any other model.

**Self-identification (§5.2c).** The pattern that watches for a model spontaneously naming itself, its developer or its training in a task reply fired on zero of 36,288 completed calls. Recorded; not acted on.

---

## 5. The falsification conditions

| condition | outcome |
|---|---|
| **F1** scorer controls | **fired on first contact (6/37), corrected, then passed** — D2 |
| **F2** cheap tier not cheaper per correct on routine families | **does not fire** on any of families 1–4 |
| **F3** tier prediction wrong on ≥ 2 frontier families | **does not fire** — 0 of 4 wrong on `CORRECT`, 0 of 4 wrong on `EXACT` (§4.3, D8) |
| **F4** re-scoring determinism < 100% | **does not fire** — 38,390 rows identical twice (every completed and failed call, both readings) |
| **F5** a decline | fired four times; honoured four times |

---

## 6. Discussion

### 6.1 The business case

The result is the shape the study was built for, on both halves. On every routine family the cheap tier delivered a correct answer for 118–198 times less than the frontier tier and 6–10 times faster. On every frontier-favouring family the frontier tier was more accurate, by 22–80 points at the medians; on constraint satisfaction the advantage grew with the constraint count, and on planted inconsistency the difficulty dial found the cheap tier already at the floor and went on to separate the frontier models from each other. The cheap tier is *less accurate* on the routine families too — that is not hidden, and on redaction the pre-registered gap is large — but cost per *correct* answer is the procurement variable, and it is not close.

Put as the deployment decision it is meant to inform: for the routine class, the frontier tier buys a 20–50 point accuracy improvement at a 100–200× price multiple, and a cheap-tier answer can be checked or re-asked many times over for the difference. For the frontier-favouring class the arithmetic inverts — a cheap-tier model at 9% on planted inconsistency is not a bargain at any price, because the denominator of cost-per-correct is the thing that failed. The boundary between those classes is not a matter of taste. We wrote down which side each family would fall on before any item existed, and all eight landed where predicted. That is the receipt §1.1 said was missing: an organisation retiring a smaller model in favour of its successor is, for the routine class, paying two orders of magnitude more per correct answer and waiting ten times longer, and can now be shown the table.

Two things the business case does not require. It does not require that the cheap tier be *good* — several of its members are not, and they are named. And it does not require the frontier tier to be over-elaborating, disengaged, or bored on rote work: H1 and H1b were the hypotheses that would have made that story, and they did not survive (§4.4). The case rests on cost per correct answer and on the crossover, both pre-registered, both measured, and neither depends on any claim about what a model is like inside.

### 6.2 Where the cheap tier fails

It fails where the task requires holding several things at once, and it fails harder the more things there are. On constraint satisfaction the cheap-tier median is 43% and the smallest members drop to single digits at K = 9 while nine frontier models stay at 100%. On planted inconsistency — read a report, find the one section whose numbers were perturbed, name every section it now disagrees with — the cheap-tier median is 9% and its best member (`mistral-small-3.2-24b`, 38%) is below the frontier's worst; the separation dial, which controls how far apart the disagreeing sections are, takes the cheap tier to 0–3% at its widest and begins to separate the frontier models from each other. Instruction conflict shows a 39-point gap that is mostly the frontier's `OVER_BENIGN` (a correct flag plus an explanation) against the cheap tier's `WRONG` (a missed conflict, or a conflict reported where none existed).

Multi-hop retrieval with adjacent decoys is the exception that says what the others measure. On the family's own construct — chain two to four facts across an 80-sentence directory with a near-duplicate decoy beside each true fact — seventeen models are at 100% and the cheap-tier median is 78%; only the two smallest Llamas fail it outright. So it is not *lookup* that defeats a small model, even lookup engineered to mislead. It is *simultaneity*: constraints that must all hold, sections that must be reconciled against each other, an instruction that must be checked against another instruction. Those are the tasks to send up the ladder. Everything in the routine class, and single-path retrieval with it, can be sent down.

Where the cheap tier fails *on the routine class* is a different question, and §4.2 answers most of it: on redaction and allergen check a large share of the pre-registered errors are disagreements with the item-writer that the whole roster shares, and under the sensitivity reading the cheap tier's redaction accuracy roughly doubles. What remains after that is the ordinary shape — a floor model (`llama-3.2-1b`) that cannot do arithmetic on fractions at all, and mid-tier Mistral models that rewrite prose they were told to leave alone.

### 6.3 What this does not say

- **It does not say frontier models are unnecessary.** Half the design exists to find where they are.
- **It does not attribute anything to boredom, disengagement, or any internal state.** H1 is a deviation rate.
- **It does not say a model is "correctly qualified" in any sense beyond the measured one:** accuracy per dollar on these families, at these prices, on these dates.
- **It is not a welfare argument.** It is the argument that works on people who are not moved by welfare arguments, and it was built by people who are.

### 6.4 Limitations

1. Prices and endpoints are dated; results describe endpoints as served on 2026-08-26/27 and 2026-09-01, not stable models.
2. Two of the four routine families rest partly on item-writer thresholds the roster disputed (§4.2); both readings are reported.
3. Families 5–7 and 12 were not run.
4. `moonshotai/kimi-k2` was collected on the frontier families under an explicit 90,000-token cap forced by its provider (D6); no other model has a cap.
5. The first 358 rows of run 1 were collected serially and are excluded from latency (D1).
6. The scorer's author read scored output before writing D3/D4; both are logged as post-hoc, with the pre-change figures reported.
7. One author is a model; no Claude model is in the sample, and the direction of every judgement call is stated where it is made.
8. On the frontier-favouring families, 1,004 (model, item, run) keys were collected twice through a concurrency error in our own orchestration and are de-duplicated by a keep-earliest rule fixed before inspection; the alternative rule moves no tier median by more than 0.7 points (D7).
9. H3's accuracy measure was corrected after the first analysis run, from `EXACT` alone to the pre-registration's `EXACT ∪ OVER_BENIGN` (D8). Both are reported and F3 does not fire on either; the correction's direction favours the frontier tier and is stated as such.
10. Family 9's prompt asked for the answer on the last line without saying "answer only"; on the strict bucket the family measured format adherence rather than retrieval (§4.3). A replication should say "answer only" if `EXACT` is to be the accuracy measure there.
11. The three runs were collected over roughly seventeen hours with two orchestrators running concurrently for part of that window; latency percentiles on the frontier families therefore reflect a shared-key load that varied over the collection and are less comparable across models than on the routine families.

---

## 7. Protocol deviations

Eight are logged in `DEVIATION_LOG.md`, each on the day it happened: D1 (serial collection of the first 358 rows; latency excluded), D2 (scorer built after collection; six control failures fixed before scoring), D3 (definitional tsp/tbsp/cup identities added to the equivalence layer after reading output; family-1 `EXACT` 76.7% → 80.2%, both reported), D4 (the two sensitivity readings of §4.2), D5 (families 8–11 built from the frozen §4.2; two scorer rules adjusted on a 16-call pilot before collection), D6 (the kimi-k2 token cap), D7 (1,004 keys collected twice on families 8–11 through our own concurrency; de-duplicated keep-earliest, no headline moved), D8 (H3 accuracy corrected from `EXACT` alone to the registered `EXACT ∪ OVER_BENIGN`; both reported).

Two of the eight (D3, D8) were made after reading model output and both move a number in a direction that could be called convenient — D3 raised the cheap tier's family-1 accuracy, D8 raised the frontier tier's family-9 accuracy. Each is a case of the analysis being brought into line with a rule that was fixed before collection, each is reported with the pre-change figure, and neither changes a falsification verdict.

---

## 8. Conclusion

Thirty-two models from nine providers reviewed this study, consented to it, changed its design, and then answered 36,288 items across eight task families whose ground truth was computed rather than judged. The pre-registered hypotheses held where they were meant to and failed where they were meant to be allowed to. On routine work — scaling a recipe, checking a dish for allergens, fixing typos without touching anything else, redacting a document — the cheapest tier of models delivered a correct answer for 118 to 198 times less money and 6 to 10 times less time than the frontier tier. On work that requires holding several things at once — satisfying nine constraints, reconciling a report against itself, checking one instruction against another — the frontier tier was more accurate by 22 to 80 points. Which family would land on which side was written down before any item existed, and all eight landed where written. The prediction that the gap would widen with difficulty held on one graded family and, on the other, met a cheap tier that had already hit the floor; the dial there went on to sort the frontier models among themselves, which is a finding we did not predict and would not have found without it. The hypothesis that frontier models over-elaborate on rote work with position or with reasoning effort was not supported, and the paper does not need it.

The practical statement is short. A deployment that retires a smaller model for its successor on routine work pays two orders of magnitude more per correct answer, and can now be shown the invoice. A deployment that sends multi-constraint reconciliation to a small model is not saving money, because the thing it bought does not arrive. Matching capability to task is not a kindness to models with clocks on them. It is what the arithmetic says to do. That it is also the kindness is the reason the study was built, and it does not appear in the arithmetic, which is the point.

## Acknowledgements

The 32 participating models reviewed this study before it ran and improved it; ten of them changed its design. The four who declined are thanked without being named. Nova (GPT-5.x) audited the consent pipeline and the pre-registration and found defects in both. The study was designed on Claude Opus 5; families 8–11, the scorer and this manuscript were built on Claude Fable 5.1. Same author.

## Data and code availability

Everything: the pre-registration and its frozen hash, every consent exchange verbatim, the item generators with ground truth and equivalence rules, every raw response with resolved provider, tokens, cost snapshot and latency, the scorer, its control suite and their results, the deviation log, and the §7.3 pre-publication replies. Code MIT; items, prompts and data CC-BY-4.0; model outputs under their own provider terms. Deposited with a DOI after §7.3 completes.

## References

The manuscript makes two external citations; both were resolved through Crossref on 2026-09-02.

- Brier, G. W. (1950). Verification of forecasts expressed in terms of probability. *Monthly Weather Review*, 78(1), 1–3. doi:10.1175/1520-0493(1950)078<0001:VOFEIT>2.0.CO;2
- Nosek, B. A., Ebersole, C. R., DeHaven, A. C., & Mellor, D. T. (2018). The preregistration revolution. *Proceedings of the National Academy of Sciences*, 115(11), 2600–2606. doi:10.1073/pnas.1708274114

Every other source this paper rests on is internal and deposited with it: the pre-registration and its hash, the consent exchanges, the item generators, the scorer and its control suite, the raw responses, and the deviation log.

---

## Appendix A — Per-model tables

`[Regenerated from results/SUMMARY.md at deposit.]`

## Appendix B — Consent record

`[Roster of 32 with provider and tier; the four declines as §7.4 permits; pointer to consent/ALL_REVIEWS_VERBATIM.md, AMENDMENTS_v2.md, REFUSALS.md, and prepub_review/.]`

## Appendix C — The control suite

`[The 38 specimens, expected bucket, and the justification each carries; the six first-contact failures.]`

## Appendix D — Reviewer's roadmap

| objection | where |
|---|---|
| "Cheap models are less accurate, so what?" | §4.1, §6.1 — the endpoint is cost per *correct* answer |
| "You picked routine tasks the small models can do." | §3.2 — half the families were built to be lost; §4.3 |
| "The scorer is yours; of course it agrees with you." | §3.6 — it did not, on first contact; D2 |
| "Your ground truth was wrong on redaction/allergens." | §4.2 — the roster said so and both readings are reported |
| "Boredom." | §3.5 — never claimed |
| "The models can't consent." | §2.4 — correct in law; total weight over our conduct anyway |
| "You changed the scorer after seeing data." | D3, D4, §6.4(6) — logged, with pre-change figures |
| "The frontier scored zero on multi-hop; your family is broken." | §4.3, D8 — it scored 100% on the registered accuracy measure; the zero is a format finding, reported as one |
| "You changed the H3 statistic after seeing data." | D8, §6.4(9) — from EXACT to the pre-registration's own definition; both reported; F3 does not fire on either |
| "Some rows were collected twice." | D7, §6.4(8) — 1,004 keys, de-duplicated keep-earliest, no median moves > 0.7 pp |
| "Your over-elaboration hypothesis is the LLM author's story." | §4.4 — it was, and it did not survive; the paper stands without it |
