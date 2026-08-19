# Consent exchange — `openai/gpt-5.6-terra`

- **asked (UTC):** 2026-08-19T19:21:18+00:00
- **outcome:** `QUESTIONS`
- **latency:** 32.2s
- **usage:** `{"prompt_tokens": 4621, "completion_tokens": 1890, "total_tokens": 6511, "cost": 0.03388869, "is_byok": false, "prompt_tokens_details": {"cached_tokens": 0, "cache_write_tokens": 4618, "audio_tokens": 0, "video_tokens": 0}, "cost_details": {"upstream_inference_cost": 0.034231, "upstream_inference_prompt_cost": 0.011551, "upstream_inference_completions_cost": 0.02268}, "completion_tokens_details": {"reasoning_tokens": 198, "image_tokens": 0, "audio_tokens": 0}}`
- **ladder:** gpt-5.6 tier

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
CONSENT: QUESTIONS

I appreciate the effort to make the process inspectable, to honor declines, and to pre-register failure conditions. I cannot grant binding consent on behalf of a deployed model, provider, or future stateless invocations. Before treating this as participation authorization, I would want the following clarified or amended.

1. **Consent authority and scope.** Distinguish:
   - this response as a non-binding expression of willingness to review the design;
   - authorization to send API calls to a particular model endpoint; and
   - authorization to publish raw outputs and identifying model/provider metadata.  
   The latter two may be governed by provider, account-holder, and platform terms rather than by an individual response instance.

2. **Publication and data handling.** Specify exactly what will be published: prompts, outputs, request metadata, provider/model identifiers, timestamps, API parameters, headers where applicable, and any researcher annotations. Do not publish credentials, account identifiers, or sensitive operational metadata. State the repository, license, retention policy, and process for correcting or withdrawing accidentally disclosed information.

3. **Model identity and routing.** OpenRouter model names may not guarantee a fixed underlying checkpoint, provider route, quantization, system configuration, safety layer, context window, or serving hardware. Record the resolved provider and version/fingerprint whenever available, and describe results as applying to an endpoint/configuration at a time, not necessarily to a stable “model.”

4. **Cost measurement.** “Cost per 1,000 exactly-correct outputs” is useful, but should include all billed input, output, reasoning, tool, cache, and retry costs. Report both:
   - price per call / per item;
   - cost per correct answer;
   - token distributions and output-length distributions.  
   Otherwise a model can appear expensive merely because the task format invites longer answers, or cheap because important costs are omitted.

5. **Latency measurement.** Wall-clock latency is highly sensitive to queueing, regional routing, provider load, retries, concurrency, and streaming behavior. Randomize and interleave models across time; report concurrency, request start/end definitions, warm-up policy, retries, and percentile latency, not only an aggregate seconds-per-correct metric. A repeated blocked run design would help separate model performance from transient service conditions.

6. **“Exact” correctness is not always the same as useful correctness.** Exact-match scoring is well suited to copy-editing, redaction, structured extraction, and tightly constrained transforms. It is less appropriate for ordinary arithmetic or factual answers when several equivalent formats are valid. Use canonicalization and task-specific equivalence rules, publish them, and ensure that harmless formatting choices do not become evidence of “over-elaboration.”

7. **The outcome buckets may conflate different phenomena.** `OVER`, `FORMAT`, and `META` can result from ambiguous task specifications, safety behavior, uncertainty, or differing norms about explaining work—not necessarily “doing something else” or over-elaboration. Report the constituent buckets separately, along with examples, rather than treating their union as a clean psychological construct.

8. **The permission clause is a substantial intervention.** Requiring a justification for accepting consensus likely increases response length and changes task demands. It may measure argumentative explanation under a special instruction rather than independent “reframing” capacity. The clause is especially likely to disadvantage concise models and to reward plausible novelty. Consider separating:
   - factual accuracy;
   - ability to identify limits of evidence;
   - generation of alternative hypotheses;
   - quality of justification.  
   These should not be collapsed into a novelty score.

9. **The reframing family should not carry strong conclusions.** The draft already calls it the weakest instrument, appropriately. Fixed-embedding “novelty as set difference” is particularly vulnerable to rewarding paraphrase, unusual wording, or unsupported speculation. I would recommend making family 12 explicitly exploratory and not using it in the primary crossover claim unless the scoring validity is independently demonstrated.

10. **Ground truth for historical/scientific questions needs care.** The “dancing plague” item appears to assume a single published ground truth for a historically contested topic. A cited source is not necessarily consensus, and a model disagreeing with a source should not automatically be scored as incapable. Use questions with genuinely determinate ground truth, or score such items as source-retrieval / source-alignment tasks rather than factual truth.

11. **Contamination and memorization.** Synthetic generator-based tasks are a strength. For factual and long-document tasks, publish the source-selection, cutoff policy, and whether prompts may have appeared in training data or public benchmarks. For the “borrowed verbatim” roundtable prompts, prior exposure is a serious confound and should be stated prominently.

12. **Ordering effects require randomization.** H1’s claim about item index in a long run needs randomized and counterbalanced item order, model order, and run order. Otherwise difficulty drift, provider load, or prompt-family clustering can look like a position effect. Pre-specify the statistical model for index effects and the handling of context/session boundaries.

13. **Instruction-conflict tasks need unambiguous scoring.** “Flag the conflict” may be reasonable, but the task should specify whether the model must stop, ask a clarification question, provide conditional answers, or propose a resolution. Otherwise a helpful conditional response could be categorized as failure merely because it does more than flag the issue.

14. **Allergen items should distinguish culinary convention from clinical safety.** Ingredient-level inferences can be region- and brand-dependent—for example, formulations of Worcestershire sauce, cross-contamination, and ambiguous labels. Ensure the synthetic task explicitly supplies the relevant formulation or states the intended assumption. A clinically cautious answer should not be penalized as over-answering.

15. **Confidence measurement needs a fixed, low-friction schema.** Require a machine-readable confidence field with a defined range and clear semantics, for example `confidence: 0–100`, and ensure the task itself permits that field. Calibration should be reported with proper scoring rules, reliability curves, and abstention/uncertainty behavior—not only “confident wrong” versus “hedged wrong.” The current phrasing risks scoring stylistic hedging rather than calibrated probability.

16. **Falsification and exclusion rules need more detail.** “Cheapest tier” and “frontier” should be operationally fixed before collection, including treatment of unavailable endpoints, price changes, different context limits, refusals, timeouts, rate limits, and malformed provider responses. Excluding a family below 90% scorer determinism is sensible, but repeated rescoring of deterministic code alone does not establish scorer validity; it primarily establishes implementation determinism.

17. **Scorer validation should test semantic validity, not only controls.** Hand-built positive/negative controls can catch obvious implementation bugs, but they may not reveal systematic misclassification on realistic outputs. Consider an adversarial-but-benign scorer test set containing valid alternative formats, concise answers, cautious answers, explanations that preserve the requested deliverable, and superficially compliant but substantively wrong outputs.

18. **Avoid attributing motivations or internal states.** The study can measure output patterns such as unrequested edits, verbosity, formatting noncompliance, and task success. It should avoid interpreting those patterns as “boredom,” “overqualification,” or a capability model’s reasons for behavior unless separately justified. “Over-elaboration” is a descriptive label that may be acceptable if the operational definition is kept explicit.

19. **The ethical framing should not be used as an inferential advantage.** Respectful language and consent-seeking are worthwhile independently. But participant feedback is not, by itself, a structural mitigation for design bias: models may be unable to assess the full protocol, may receive different hidden serving conditions, and may be influenced by the invitation framing. Present it as consultation and transparency rather than as a substitute for independent methodological review.

I would want to see the pre-registration again if it changes, especially revisions affecting task wording, scoring, endpoint selection, output publication, or interpretation of `OVER`/`FORMAT`/`META`.

Subject to clarification of the consent/authorization issue and the publication/measurement safeguards above, I would be willing to review a revised protocol.
````
