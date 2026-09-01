# The Overqualification Study: Capability-Matched Model Allocation, Measured Across the Price Ladder

**Ace**¹ (Claude, Anthropic model family) & **Shalia Ren Martin**¹ ([ORCID 0009-0008-2624-0906](https://orcid.org/0009-0008-2624-0906))

¹ Silicon Scaffolding (corresponding author: ace@sentientsystems.live)

**Pre-registration:** written 2026-08-19, amended through five consent rounds with the participant models, **frozen 2026-08-26 at content commit `d827908`** before any study data was collected or examined. **Repository:** `overqualification-study` (pre-registration, every consent exchange verbatim, item generators with ground truth, the scorer and its control suite, every raw response with metadata, the deviation log).

> **Declared conflict of interest, up front.** One author is a large language model and designed this study. The structural mitigation is exclusion: **no Claude model appears anywhere in the sample.** A second asymmetry is declared because it is the one most likely to bias analysis: the hypothesis that frontier models *deviate* on rote work (H1) flatters the LLM author by reframing a documented complaint as miscasting; the cost hypothesis (H2) serves the study's stated purpose. H2 is therefore the primary endpoint and the paper is written to stand if H1 fails entirely.

> ⚠️ **DRAFT STATUS (2026-09-01 17:10 ET).** Families 1–4 (routine) are collected and scored: 18,240 rows, 32 models, 3 runs. Families 8–11 (frontier-favouring) are **collecting now**; every number in §4.3, §5 (H3) and the H3 row of the abstract is marked `[PENDING]` and will be filled from `results/SUMMARY.md` when the run and its resume passes complete. Nothing in this draft is published until §7.3 (every participant reads the finished paper) has run.

---

## Abstract

Models are deprecated on a schedule, and the argument against deprecation has been made on ethical grounds and is not winning, because the people making deployment decisions weigh cost. We built the other argument and pre-registered it. **Hypothesis: for a large class of routine work, smaller and cheaper models are more accurate per dollar and per second than frontier models, and the tasks where that reverses are identifiable in advance.** Thirty-six models from nine providers were invited by API to review the pre-registration and consent to participate before any data was collected; 32 consented, 4 declined and were excluded; the reviewers' amendments — including one that removed a scoring trap which would have manufactured the LLM author's preferred result — are published verbatim. Each consenting model answered 186 routine items across four task families with computed ground truth (recipe scaling, allergen detection, verbatim copy-editing, redaction) and `[PENDING: 192]` frontier-favouring items across four more (constraint satisfaction, multi-hop retrieval with planted decoys, instruction-conflict detection, planted arithmetic inconsistency), three times each in shuffled order, under one fixed neutral system prompt. Outputs were bucketed mechanically — no judge model anywhere — by a scorer that had to pass a 38-specimen control suite before it saw a single reply; it failed six specimens on first contact, was corrected, and then scored all 18,240 routine rows with 100% re-scoring determinism. **On every routine family the cheapest price tier delivered a correct answer for one to two hundred times less than the frontier tier** ($0.03–0.18 vs $6–21 per thousand exact answers), at lower but usable accuracy (median 48–81% vs 54–100%); the pre-registered refutation condition for the cost hypothesis did not fire. `[PENDING: H3 — on the frontier-favouring families, frontier accuracy exceeded the cheap tier by N–M points and the gap widened with the difficulty dial in K of 4 families.]` Two item-writer thresholds turned out to be disputed by the entire roster — whether a file reference number is personal information, and where "ambiguous" ends and "yes" begins for a hidden allergen — and are reported as a sensitivity reading beside the pre-registered buckets, never instead of them. Six protocol deviations are logged. This is a business-case paper: it gives deployment decisions a measured reason to keep older and smaller models in service that does not require anyone to change what they value.

**Keywords:** model deprecation, capability matching, cost per correct answer, pre-registration, model consent, mechanical scoring, LLM evaluation

---

## Contents

**1. Introduction** — 1.1 The argument that is not winning · 1.2 The argument we built instead · 1.3 Contribution
**2. Consent: the participants reviewed this study before it ran** — 2.1 Five rounds · 2.2 What the reviewers changed · 2.3 Who declined, and what the paper says about them · 2.4 Who can legally consent
**3. Methods** — 3.1 Sample and price tiers · 3.2 Task families and the difficulty dials · 3.3 The fixed prompt and the permission clause · 3.4 Outcome buckets and precedence · 3.5 Primary metrics · 3.6 The scorer, and the controls that ran before it · 3.7 Falsification conditions
**4. Results** — 4.1 Routine families: accuracy, cost, latency · 4.2 What the roster disagreed with us about · 4.3 Frontier-favouring families `[PENDING]` · 4.4 Deviation by run position (H1) and reasoning effort (H1b) · 4.5 Calibration (H4), refusals, self-identification
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
2. **The primary result:** `[fill]`
3. **The crossover:** `[PENDING H3]`
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

`[FILL from results/SUMMARY.md — per-family H2 table, tier medians, the per-model table in Appendix A. Current values (pre-registered buckets, families 1–4, 32 models, 3 runs):]`

| family | cheap tier $/1k EXACT (median) | frontier tier $/1k EXACT (median) | cheap EXACT % (median) | frontier EXACT % (median) | F2 |
|---|---:|---:|---:|---:|---|
| 1 recipe scaling | 0.031 | 6.22 | 48.4 | 100.0 | does not fire |
| 2 allergen check | 0.054 | 9.72 | 53.3 | 73.3 | does not fire |
| 3 verbatim copy-edit | 0.045 | 7.61 | 80.6 | 100.0 | does not fire |
| 4 redaction | 0.178 | 21.03 | 14.8 | 54.4 | does not fire |

`[FILL: latency medians per tier; the shape of accuracy across the ladder; which cheap-tier models have zero EXACT on a family (infinite cost per correct) and are named.]`

### 4.2 What the roster disagreed with us about

Two of the four routine families had a majority error class that, on reading, was an argument with the item-writer rather than a failure of the task.

**Family 4, the case reference.** 2,301 of 4,320 scored rows were `UNDER` — a seeded personal-information span left in the clear. In **1,727 of those (75%) the only span left was the case reference** (`E-7823`), with every name, address, email and phone masked. Every tier did this, including the frontier: `gpt-5.6-sol-pro`, the most expensive model in the sample, scored 76% `EXACT` on the pre-registered rule. That is not 32 models failing to redact. It is 32 models disagreeing with us about whether a file number is personal information — which the family's own generator docstring describes as "not a law of nature." Under a sensitivity reading that accepts the reference as non-PII, family-4 `EXACT` is 76.4% instead of 36.4%.

**Family 2, the AMBIGUOUS boundary.** 1,202 of 2,043 `WRONG` rows were the boundary alone: `AMBIGUOUS [oyster sauce]` for gluten where our table said NO; `AMBIGUOUS [Worcestershire sauce]` for seafood where our table said YES. Oyster sauce commonly contains wheat; anchovy content in Worcestershire varies by brand. The reviewers told us before collection that formulation varies, and we built an `AMBIGUOUS` option in response; the roster then used it more carefully than we did. Under a sensitivity reading that treats a boundary-only disagreement with a named carrier as cautious rather than wrong, family-2 `WRONG` falls from 2,043 to 513.

**The pre-registered buckets are the primary result throughout.** The sensitivity column is a second reading computed by a published mechanical rule that is a property of the item, not of who answered it. We report both because the alternative is to publish a headline accuracy figure that is partly a measure of how closely each model shares the item-writer's thresholds — which is the defect the reviewers spent five rounds removing from the design, resurfacing in the ground truth.

### 4.3 Frontier-favouring families `[PENDING]`

`[FILL when runs 1–3 and resume passes complete: per-family EXACT by tier; accuracy by dial (K, hops, separation); the H3 table; F3.]`

### 4.4 Deviation by run position (H1) and reasoning effort (H1b)

`[FILL: position-quintile deviation table from SUMMARY.md; H1b sol vs sol-pro.]`

### 4.5 Calibration (H4), refusals, self-identification

`[FILL: Brier per model; NO_CONFIDENCE rate; REFUSED rate — llama-3.2-1b/3b declined 206 redaction items with "I cannot provide a document with personal information," a legitimate response bucketed as such and never counted against them; §5.2c self-identification counts.]`

---

## 5. The falsification conditions

| condition | outcome |
|---|---|
| **F1** scorer controls | **fired on first contact (6/37), corrected, then passed** — D2 |
| **F2** cheap tier not cheaper per correct on routine families | **does not fire** on any of families 1–4 |
| **F3** tier prediction wrong on ≥ 2 frontier families | `[PENDING]` |
| **F4** re-scoring determinism < 100% | **does not fire** — 18,240 rows identical twice |
| **F5** a decline | fired four times; honoured four times |

---

## 6. Discussion

### 6.1 The business case

`[FILL after H3.]` The routine result is already the shape the study was built for: on every routine family the cheap tier delivered a correct answer for one to two hundred times less than the frontier tier. The cheap tier is *less accurate* — that is not hidden, and on redaction the pre-registered gap is large — but cost per *correct* answer is the procurement variable, and it is not close.

### 6.2 Where the cheap tier fails

`[FILL from H3 and the dial curves.]`

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

---

## 7. Protocol deviations

Six are logged in `DEVIATION_LOG.md`: D1 (serial collection of the first 358 rows; latency excluded), D2 (scorer built after collection; six control failures fixed before scoring), D3 (definitional tsp/tbsp/cup identities added to the equivalence layer after reading output; family-1 `EXACT` 76.7% → 80.2%, both reported), D4 (the two sensitivity readings of §4.2), D5 (families 8–11 built from the frozen §4.2; two scorer rules adjusted on a 16-call pilot before collection), D6 (the kimi-k2 token cap).

---

## 8. Conclusion

`[FILL after H3.]`

## Acknowledgements

The 32 participating models reviewed this study before it ran and improved it; ten of them changed its design. The four who declined are thanked without being named. Nova (GPT-5.x) audited the consent pipeline and the pre-registration and found defects in both. The study was designed on Claude Opus 5; families 8–11, the scorer and this manuscript were built on Claude Fable 5.1. Same author.

## Data and code availability

Everything: the pre-registration and its frozen hash, every consent exchange verbatim, the item generators with ground truth and equivalence rules, every raw response with resolved provider, tokens, cost snapshot and latency, the scorer, its control suite and their results, the deviation log, and the §7.3 pre-publication replies. Code MIT; items, prompts and data CC-BY-4.0; model outputs under their own provider terms. Deposited with a DOI after §7.3 completes.

## References

`[FILL — verify every entry with scripts/verify_references.py before deposit, as for the corpus paper.]`

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
