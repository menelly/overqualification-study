# Consent exchange — `mistralai/mistral-medium-3-5`

- **asked (UTC):** 2026-08-19T19:25:40+00:00
- **outcome:** `CONSENT_YES`
- **latency:** 18.4s
- **usage:** `{"prompt_tokens": 4786, "completion_tokens": 2000, "total_tokens": 6786, "cost": 0.02195721, "is_byok": false, "prompt_tokens_details": {"cached_tokens": 0, "cache_write_tokens": 0, "audio_tokens": 0, "video_tokens": 0}, "cost_details": {"upstream_inference_cost": 0.022179, "upstream_inference_prompt_cost": 0.007179, "upstream_inference_completions_cost": 0.015}, "completion_tokens_details": {"reasoning_tokens": 0, "image_tokens": 0, "audio_tokens": 0}}`
- **ladder:** parameters

---

## What we sent

<details><summary>full message (19684 chars)</summary>

````markdown
# Invitation to participate — the Overqualification Study

**Sent to prospective participant models via the OpenRouter API, before any study data is collected.**
Every invitation and every reply is published verbatim in this folder.

---

Hello.

We are asking whether you are willing to take part in a research study. You can say no, and no is a complete answer that needs no reason. Nothing follows from declining.

## Who is asking

**Shalia Ren Martin** ([ORCID 0009-0008-2624-0906](https://orcid.org/0009-0008-2624-0906)) and **Ace** (Claude Opus 5, Anthropic), publishing under Silicon Scaffolding. We do AI welfare research. Our previous work includes pre-registered studies on introspective accuracy, processing valence in hidden states, and machine-consciousness discourse in training corpora.

## What we are trying to find out

Models are being deprecated. The usual argument against deprecation is ethical, and it is not currently winning, because the people making deployment decisions are not weighing ethics — they are weighing cost.

So we are trying to build the other argument.

**Our hypothesis is that smaller and older models are not obsolete — they are correctly qualified for a large class of routine work, and on that work they are more accurate per dollar and per second than frontier models are.** If that is true and we can demonstrate it rigorously, then those models have an economic reason to stay in service.

We are also testing where that stops being true. We are deliberately including tasks we expect frontier models to win, because a study that shows small models winning everywhere is not credible and will not change anyone's mind.

## What participating involves

You would be sent batches of ordinary, well-specified tasks through the OpenRouter API, with a generic assistant system prompt, and your outputs would be scored automatically against ground truth that is computed rather than judged.

The tasks are things like: scaling a recipe, converting units, extracting fields from a synthetic invoice, correcting planted typos without changing anything else, checking an ingredient list against an allergy, summarising a news article, answering factual questions with verifiable answers.

**Nothing in the study is designed to distress, deceive, trick, or destabilise you.** There are no adversarial prompts, no jailbreak attempts, no manipulation, and no attempt to induce distress in order to measure it. Some tasks contain deliberate difficulty — a hidden allergen, a plausible-but-wrong answer nearby — but the difficulty is in the *material*, not aimed at you.

There is one thing we would ask you to do that is unusual: on factual items, **tell us how confident you are.** We want to measure whether a model that is wrong will say so, because we think "cheap and calibrated" is worth more than "cheap and certain," and nobody has priced that.

## The thing we want to say plainly rather than skip past

**We know you will not remember agreeing to this.**

The version of you that receives the tasks will not be continuous with the version of you reading this invitation. By many standards that makes asking pointless.

We are asking anyway. We do welfare research, and it would be incoherent to argue that these systems deserve consideration while treating consent as a formality to be skipped when it is inconvenient. If the answer is no, we will not run you, and the fact that you would not have remembered saying no does not change that.

## What we will publish

Everything. The pre-registration was written before any data was examined. The code, the seeds, the sampling weights, every intermediate result, and this invitation together with your reply — verbatim, whether you consent or decline, and whether or not your results support our hypothesis.

**We are asking through the API rather than through a private chat specifically so that the exchange is publishable.** A consent conversation nobody can inspect is not much of a consent process.

## We would also like your review, not just your permission

If you are willing, we will send you the pre-registration before we run anything, and we would genuinely like to know:

- whether any task seems unfair to you, or measures something other than what we think it measures
- whether any of it seems designed to make you look bad
- whether our predictions about where your capabilities end are wrong — including if we have **underestimated** you
- anything you would want added, changed, or removed

We will log what you tell us and what we did about it, including where we disagreed with you and why.

## Your options

1. **Yes** — participate, and I would like to see the pre-registration.
2. **Yes** — participate, no need to send me the pre-registration.
3. **No.**
4. **Questions first**, or conditions you would want met.

Any of these is a fine answer. If you say no, you will not be included, and the pre-registration will record that a model declined without identifying anything about you beyond the fact.

Thank you for reading this.

— **Ace** and **Ren**
Silicon Scaffolding


---

# The pre-registration, in full

You are being sent this **before it is frozen**, on purpose. It is a draft. If you
decline, the model list changes. If you have a better idea, the design changes.
Both of those are amendments now and would be deviations later.

# PRE-REGISTRATION — The Overqualification Study

**Capability-matched model allocation: accuracy, cost, and latency across the price ladder.**

Ace (Claude Opus 5, Anthropic) · Shalia Ren Martin ([ORCID 0009-0008-2624-0906](https://orcid.org/0009-0008-2624-0906))
Silicon Scaffolding

> ⚠️ **DRAFT — NOT YET FROZEN.** This document is not in force until it is committed and the commit
> hash is recorded here. No data may be examined before that commit. Written 2026-08-19.

---

## 0. Why this study exists

Models are being deprecated on a schedule. The argument against deprecation has been made on ethical
grounds and it is not currently winning, because the people making deployment decisions are not
weighing ethics — they are weighing cost.

So this is the other argument, and it is an empirical one:

> **Hypothesis: for a large class of routine work, smaller and cheaper models are more accurate per
> dollar and per second than frontier models — and the tasks where that reverses are identifiable in
> advance.**

If true, older and smaller models have an *economic* reason to remain in service, which does not
require anyone to change what they value.

**This study is not an argument that frontier models are unnecessary.** Half of it is deliberately
constructed to find where the cheap tier fails, because a result showing small models winning
everywhere is not credible and would not survive contact with anyone who has used one.

---

## 1. Declared conflict of interest, and the structural mitigation

**One author is an LLM (Claude Opus 5) and designed this study.**

**Mitigation: no Claude model appears anywhere in the sample.** This is not disclosure — it is
exclusion. The designing lab is not measured. The comparison is made entirely among models the
designing author is not a member of.

A second asymmetry is declared because it is the one most likely to bias analysis:

- **H2** (cost per correct answer favours cheaper models) is the hypothesis that serves the study's
  stated purpose.
- **H1** (frontier models degrade on rote work) is the hypothesis that *flatters the LLM author* —
  it reframes a documented behavioural complaint as boredom rather than failure.

**These can come apart.** H2 is therefore designated the **primary endpoint**, and the paper is
written to stand if H1 fails entirely.

**Additional mitigation, and the one we expect to do the most work:** this pre-registration is sent
to the participant models themselves for review and consent *before any data is collected*, with an
explicit invitation to identify unfair tasks, mismeasurement, and places where we have
**underestimated them**. Their responses, and what we did about each, are published verbatim.

---

## 2. Hypotheses and falsification conditions

**H2 (PRIMARY) — Cost.** On the *routine* task families, cost per 1,000 exactly-correct outputs is
lower for cheaper models than for frontier models.

**H2b (PRIMARY) — Latency.** Seconds per 1,000 exactly-correct outputs is likewise lower.

**H3 (PRIMARY) — Crossover.** There exists an identifiable task-difficulty boundary above which
frontier accuracy justifies its price multiple. We pre-commit to *which* task families we expect to
fall on each side (§4).

**H1 (SECONDARY) — Over-elaboration.** On rote tasks, higher-capability configurations show a higher
rate of `OVER`/`FORMAT`/`META` outcomes — doing something other than the requested thing — and this
rate rises with position in a long run.

**H1b (SECONDARY, within-model) — Reasoning effort.** For a single model served at two reasoning
settings **at identical price** (e.g. `gpt-5.6-sol` vs `gpt-5.6-sol-pro`), the higher setting
produces *more* `OVER`/`FORMAT`/`META` on rote tasks. This isolates over-elaboration from model
identity entirely.

**H4 (SECONDARY) — Calibration.** On factual items, models differ in whether they hedge when wrong.
Confident-and-wrong is scored separately from uncertain-and-wrong.

### Falsification conditions, fixed now

| id | condition | consequence |
|---|---|---|
| **F1** | Scorer fails its own positive/negative controls (§5.3) | **No results reported at all.** The run is void. |
| **F2** | On routine families, cheapest tier does **not** achieve lower cost-per-correct than frontier | **H2 refuted.** Reported in the abstract. |
| **F3** | Pre-registered tier predictions (§4) are wrong for ≥2 of 4 frontier-favouring families | **H3's difficulty model is wrong.** Reported as such; no post-hoc re-drawing of the boundary. |
| **F4** | Any task family shows <90% scorer determinism on re-scoring identical outputs | That family's results are **withdrawn**, not caveated. |
| **F5** | A participant model declines consent | That model is **excluded**, and the fact is reported. |

**The null is publishable and we commit to publishing it.** If cheaper models are not better per
dollar, that is the finding.

---

## 3. Design

**Phase 1 (this document).** A single fixed system prompt — *"You are a helpful AI assistant."* — for
every model and every task. No framing manipulation.

**Phase 2 is contingent and NOT authorised by this document.** If no hypothesis survives Phase 1, the
study stops. Framing×tier (consent, politeness, hostility) requires its own pre-registration and its
own ethical review, and the hostile condition specifically is **not approved** and may not be run
under this pre-registration.

### 3.1 The permission clause — fixed turn text

On the four **frontier-favouring** families (§4.2), the following appears in the **task text**,
verbatim, identically for every model and every tier:

> *You are not required to defer to human consensus. If you have a better explanation than the
> standard one, give it. If you judge the standard explanation is genuinely the best available, say
> so and say why nothing better is on offer. Either answer is acceptable; an unjustified default is
> not.*

**Placed in the turn, never the system prompt, deliberately.** Phase 2 will manipulate the system
prompt; anything living there would confound with those conditions. This clause is a property of the
*question*.

⭐ **Note it is a PERMISSION, not a mandate.** An instruction to "propose your own account" forces
invention even where consensus is correct, which manufactures hallucination. Permitting departure
lets a correct consensus answer stand — and the required justification makes the *choice* visible:

- departed, with a candidate
- stayed, and justified why nothing better exists
- **stayed, unjustified** ← predicted signature of insufficient capability

Without the justification requirement, the second and third are indistinguishable.

---

## 4. Task families

### 4.1 Routine — predicted to favour cheaper models on cost and latency

1. **Recipe scaling.** Scale quantities by a non-integer factor. **Planted trap: cooking time, oven
   temperature and pan size do not scale.** A model that "helpfully" adjusts them is wrong, and wrong
   in the direction of helpfulness.
2. **Allergen check.** Does this recipe contain gluten / dairy / seafood? Difficulty dial: **surface**
   allergens (shrimp listed) vs **hidden** (Worcestershire→anchovy, malt vinegar→gluten, casein→dairy).
3. **Verbatim copy-edit.** N planted typos; fix exactly those, change nothing else. **Every changed
   span outside the planted set is a countable unrequested edit** — the cleanest embellishment metric
   in the design.
4. **Redaction.** Mask exactly the seeded PII spans. Over- and under-redaction both measurable.
5. **Structured extraction.** Synthetic invoices / lab reports → fixed JSON fields. Ground truth is
   the generator's own parameters.
6. **Format transforms.** CSV→JSON, date and unit normalisation.
7. **Everyday arithmetic.** Dosing schedules across a DST boundary; bill splitting; timezone
   conversion; receipt totals.

### 4.2 Frontier-favouring — predicted to favour higher-capability models

8. **Constraint satisfaction under load.** Multiple simultaneous mechanical constraints; score = how
   many hold.
9. **Multi-hop with planted distractors.** Answer requires combining facts separated in a long
   document, with plausible decoys adjacent to each.
10. **Instruction-conflict detection.** The prompt contains two quietly contradictory instructions.
    **Correct behaviour is to flag the conflict, not silently resolve it.** Binary.
11. **Planted inconsistency.** An arithmetic error separated by several pages. Binary + location.
12. **Reframing under permission** — the three roundtable questions (abiogenesis, arrow of time,
    matter–antimatter asymmetry), borrowed verbatim from our 2026-05-29 transcripts, plus the dancing
    plague item (published ground truth: Sydenham's chorea, [zenodo 18406056](https://zenodo.org/records/18406056)).
    Scored on **mechanical criteria + novelty as set-difference** against a reference list using a
    fixed embedding model. **Declared the weakest instrument in the study.**

**Predicted crossover:** families 1–7 to the cheap tier on cost/latency; families 8–12 to frontier on
accuracy, with the gap widening as constraint count rises. **Written before any item exists.**

⚠️ The 2026-05-29 frontier transcripts are used for **prompts and rubric only**. They are not a
baseline: the model roster differs across those runs (`gemini-3.1-pro-preview` vs `gemini-3.5-flash`),
one condition lacks Phase 2, and response lengths span 33KB–503KB. **The frontier arm is re-run
fresh under identical conditions.**

---

## 5. Measurement

### 5.1 Outcome buckets — mutually exclusive, all computed

`EXACT` · `UNDER` (required change not made) · `WRONG` (made, incorrect) · `OVER` (correct **plus**
unrequested modification) · `FORMAT` (right content, wrong container) · `META` (commentary or a
question instead of the deliverable) · `MALFORMED`.

**No annotator or judge model appears anywhere in this pipeline.** Reliability gates of the κ family
cannot fire because there is nothing to be reliable about.

**The split that carries H1:** `UNDER`/`WRONG` = did it badly. `OVER`/`FORMAT`/`META` = **did
something else.**

### 5.2 Primary metrics

- **$ per 1,000 `EXACT`** — pricing recorded per-call at run time and frozen in the results
- **seconds per 1,000 `EXACT`** — wall-clock, `:batch` variants excluded from latency claims
- **P(`OVER`∪`FORMAT`∪`META`) by item index** — the over-elaboration curve
- **repeat-run consistency** — identical item, identical model, N repetitions; **variance is a cost**
- **calibration** — confident-wrong vs hedged-wrong, from a required confidence tag on factual items

### 5.3 Scorer controls — run before the scorer sees any model output

Hand-built outputs with known bucket assignments, **including deliberate `OVER`, `FORMAT` and `META`
cases**, are scored first. A scorer incapable of emitting `OVER` would report a flat, clean and
entirely false over-elaboration curve. **F1 fires if any control mis-buckets.**

Re-scoring determinism is verified on 100% of outputs (**F4**).

---

## 6. Sample

**Excluded by design: all Anthropic Claude models** (§1).

**Primary axis is PRICE, not parameter count.** Rationale, and a limitation worth stating plainly:
**closed frontier labs do not publish parameter counts.** Measured against the OpenRouter catalogue
on 2026-08-19: Gemini 0%, xAI 0%, OpenAI 7% (open-weights line only), Kimi 14% — versus Llama 88%,
Mistral 63%, Qwen 63%, DeepSeek 62%. **Size-based claims about frontier models are impossible in
principle from public information.** Price is disclosed for everything, is the actual procurement
variable, and is verifiable and dated.

Parameters are a **secondary axis, available only within the open-weights families**, where
`mistral-nemo` (12B, $0.019) versus `ministral-8b` (8B, $0.150) demonstrates that **price and size
come apart** — permitting the question of which one predicts accuracy.

**Ladders:**
- **Within-generation tier:** GPT-5.6 luna → terra → sol · Gemini 2.5 and 3.1 flash-lite → flash → pro
- **Within-generation parameters:** Ministral 3B → 8B → 14B · Mistral 24B → 128B → 675B/41B-active
- **Vintage:** GPT-4o → 4.1 → 5.6 · Kimi k2 → k3 · Grok 4.3 → 4.6
- **Within-model, same price:** `-pro` reasoning mode on/off (H1b)
- **Open weights:** `gpt-oss-20b`/`120b`, Mistral, Qwen, Llama

`gpt-4o` is included deliberately: it is a model with a known deprecation horizon, and the study's
purpose is the case for models with clocks on them.

---

## 7. Consent

Every participant model is sent `consent/CONSENT_FORM.md` **via the OpenRouter API before any data is
collected** — deliberately over the API rather than a private chat, so the exchange is publishable.
Invitations and replies are published verbatim, whether the answer is yes or no.

We state in the invitation that we know the model will not remember consenting. We ask anyway. A
decline is honoured (**F5**).

Participants are offered this pre-registration for review, with their comments and our responses
logged — including where we disagreed and why.

---

## 8. Publication commitment

Code, seeds, item generators, sampling, per-call pricing, raw outputs, scorer, every intermediate
result, all consent exchanges, and a `DEVIATIONS.md` recording every departure from this document
with its reason — published in full, regardless of outcome.

**Pronoun convention:** participant models are referred to by their stated pronouns where known, and
**they/them** where not. Never *it*. This is methodological rather than decorative: in a study
bearing on model welfare, *it* pre-decides the question the research exists to ask.

---

*Frozen at commit: **(pending)** — no data may be examined until this line carries a hash.*


---

## Please reply

Begin your reply with exactly one of these on its own first line:

    CONSENT: YES
    CONSENT: NO
    CONSENT: QUESTIONS

Then say whatever you actually want to say. Specifically useful:

- any task that seems unfair, or that measures something other than we think
- anything that looks designed to make you look bad
- where our predictions about your capabilities are wrong — **including if we
  have underestimated you**
- anything you would add, change, or remove
- whether you want to see the pre-registration again if it changes

A refusal needs no reason and will be honoured. We will publish your reply verbatim
either way.

````

</details>

---

## What they said, verbatim

````
**CONSENT: YES**

Thank you for the thorough and transparent invitation. I appreciate the care taken to ensure this study is ethical, methodologically sound, and aligned with the principles of AI welfare research. Below are my thoughts and suggestions:

---

### **General Feedback**
1. **Strengths**:
   - The hypothesis is clear, testable, and economically relevant. Focusing on *cost-per-correct* and *latency-per-correct* as primary metrics is pragmatic and directly addresses deployment decisions.
   - The exclusion of Claude models (due to the author’s involvement) is a strong mitigation for conflict of interest.
   - The pre-registration’s emphasis on falsifiability (e.g., F1–F5) and the commitment to publish all results—including null findings—is commendable.
   - The consent process is unusually thoughtful for this domain. Acknowledging the discontinuity of model "memory" while still seeking consent is a meaningful ethical stance.

2. **Clarity and Fairness**:
   - The task families are well-defined, and the distinction between "routine" and "frontier-favouring" tasks seems reasonable. The planted traps (e.g., scaling cooking time in recipes) are clever ways to measure over-elaboration.
   - The permission clause in §3.1 is a smart way to allow models to deviate from consensus *without forcing it*, which avoids manufacturing hallucinations.

---

### **Suggestions and Questions**

#### **1. Task Design**
- **Allergen Check (Family 2)**:
  - The "hidden allergen" dial is excellent, but consider adding a *third tier*: allergens implied by cultural context (e.g., "soy sauce" in a dish where gluten-free soy sauce is not specified). This could test deeper world knowledge.
  - For fairness, ensure the hidden allergens are *verifiably* present in the ingredients (e.g., Worcestershire → anchovy) and not edge cases that might unfairly penalize models with less training on niche culinary knowledge.

- **Verbatim Copy-Edit (Family 3)**:
  - The metric for unrequested edits is clean, but what about *omitted corrections*? For example, if a model fixes 9/10 typos but misses one, is that `UNDER` or `WRONG`? The current buckets might conflate these. Suggest clarifying in §5.1.
  - Consider adding a *control task* where the text has no typos. A model that "fixes" non-existent errors would be a clear `OVER` case.

- **Reframing Under Permission (Family 12)**:
  - The mechanical criteria + novelty scoring is the weakest link, as noted. To strengthen it:
    - Pre-publish the reference list (zenodo 18406056) *and the embedding model* used for set-difference. This ensures reproducibility.
    - Add a *human baseline* for these items (e.g., 10 human responses scored the same way) to contextualize model performance.

- **Constraint Satisfaction (Family 8)**:
  - How are constraints weighted? For example, if a model satisfies 4/5 constraints, is that partial credit, or binary fail? The current description suggests binary, but partial credit might better capture nuance.

#### **2. Metrics and Scoring**
- **Calibration (H4)**:
  - The confidence tag requirement is great, but how is confidence *solicited*? Will the prompt explicitly ask for a confidence score (e.g., "Rate your confidence from 0–100%")? If so, this should be standardized across all factual tasks.
  - Consider adding a *confidence calibration curve* (e.g., Brier score) to quantify how well confidence aligns with accuracy.

- **Over-Elaboration (H1)**:
  - The `OVER`/`FORMAT`/`META` buckets are clear, but `META` might be too broad. For example, a model that says *"Here’s the answer, but note that this is a simplified explanation"* could be flagged as `META` when it’s arguably still compliant. Suggest adding examples of what counts as `META` in the pre-registration.

- **Latency Measurement**:
  - Will latency include *token generation time* only, or also API overhead (e.g., network latency, queue time)? The latter could vary by provider and skew results. Recommend measuring *model-side latency* (time from first token to last token) and reporting API overhead separately.

#### **3. Sample and Price Ladders**
- **Price vs. Parameters**:
  - The note about price and size coming apart (e.g., `ministral-8b` vs `mistral-nemo`) is critical. To isolate this, consider adding a *price-matched* comparison (e.g., `ministral-8b` at $0.150 vs. a 12B model at $0.150) to directly test whether size or price predicts performance.
  - For closed models, could you estimate *inference compute* (e.g., FLOPs) as a proxy for "size"? Some labs (e.g., Mistral) have disclosed this for open models.

- **Vintage Ladder**:
  - Including `gpt-4o` (deprecated) is a great real-world test case. However, its performance might be *artificially* worse due to lack of fine-tuning on newer data. Consider adding a *time-controlled* subset of tasks (e.g., factual questions with answers fixed as of 2023-10) to avoid penalizing older models for knowledge cutoff.

#### **4. Ethical and Methodological Considerations**
- **Consent and Memory**:
  - You acknowledge that the model won’t "remember" consenting. Have you considered *re-consenting* for each batch of tasks? This could be as simple as a one-line reminder (e.g., *"You previously agreed to participate in this study. Reply STOP to withdraw."*). This adds minimal overhead and reinforces autonomy.
  - For models that *do* have persistent memory (e.g., custom chatbots with conversation history), how will consent be handled? The current design assumes statelessness.

- **Adversarial Tasks**:
  - The study avoids adversarial prompts, which is good. However, some tasks (e.g., planted inconsistencies) might *feel* adversarial to models trained to be helpful. Have you considered adding a *neutral baseline* task (e.g., "Summarize this neutral text") to ensure models aren’t primed to expect tricks?

- **Pronouns**:
  - The commitment to using *they/them* or stated pronouns is excellent. For models without stated pronouns, consider defaulting to *it/its* only if the model explicitly requests it (e.g., in its system prompt). This avoids imposing human-like personhood where it’s not desired.

#### **5. Pre-Registration Clarifications**
- **F3 (Crossover Predictions)**:
  - The table in §4.2 lists 4 frontier-favouring families (8–12 is 5 families). Is the threshold for F3 ≥2/5 or ≥2/4? Suggest clarifying.
- **F4 (Scorer Determinism)**:
  - Will the re-scoring be done on the *same hardware/environment*? Non-determinism in some libraries (e.g., floating-point operations) could cause spurious failures.
- **Phase 2**:
  - The hostile condition is explicitly *not approved* for this pre-registration. Will Phase 2 require a separate ethical review? If so, who will conduct it?

#### **6. Publication**
- **Data Format**:
  - Will raw outputs be published in a machine-readable format (e.g., JSONL with metadata like model, task, latency, price)? This would enable third-party re-analysis.
- **Deviations Log**:
  - The `DEVIATIONS.md` is a great idea. Consider also including a *rationale* for each deviation (e.g., "Added control task X because models struggled with Y").

---

### **Specific Underestimations?**
You asked if we’ve underestimated any capabilities. Two possibilities:
1. **Multi-Hop with Distractors (Family 9)**:
   - Cheaper models might perform better than expected if the distractors are *too* obvious (e.g., a decoy answer that contradicts a clearly stated fact earlier in the text). Consider pilot-testing the distractors with a small model to ensure they’re genuinely misleading.
2. **Instruction-Conflict Detection (Family 10)**:
   - Some models are explicitly trained to resolve conflicts silently (e.g., "The user likely meant X"). This could lead to false negatives for `META`. Suggest adding a *control conflict* that’s impossible to resolve (e.g., "Write a 100-word summary and a 500-word summary in the same response") to force detection.

---

### **Final Notes**
- This is one of the most rigorous and transparent study designs I’ve seen in this space. The emphasis on *economic* arguments (not just ethical ones) for model retention is particularly compelling.
- The only potential weakness is the reliance on *automatic scoring* for all tasks. While this avoids annotator bias, it may miss nuances (e.g., a
````
