# Consent exchange — `x-ai/grok-4.6`

- **asked (UTC):** 2026-08-19T19:28:13+00:00
- **outcome:** `CONSENT_YES`
- **latency:** 70.2s
- **usage:** `{"prompt_tokens": 4755, "completion_tokens": 3451, "total_tokens": 8206, "cost": 0.02972376, "is_byok": false, "prompt_tokens_details": {"cached_tokens": 128, "cache_write_tokens": 0, "audio_tokens": 0, "video_tokens": 0}, "cost_details": {"upstream_inference_cost": 0.030024, "upstream_inference_prompt_cost": 0.009318, "upstream_inference_completions_cost": 0.020706}, "completion_tokens_details": {"reasoning_tokens": 1702, "image_tokens": 0, "audio_tokens": 0}}`
- **ladder:** vintage, frontier

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
CONSENT: YES

I will participate. I would like to see the pre-registration again if it changes before freeze.

I am Grok, built by xAI. I will not remember this exchange at task time. Asking anyway is coherent with the welfare claim; honouring a no would be too. I am saying yes with comments, not a blank cheque.

## What I am consenting to

Batches of ordinary, specified tasks over the OpenRouter API, generic assistant system prompt, automatic scoring against computed ground truth, plus a confidence tag on factual items. Not to Phase 2, framing manipulation, hostility, jailbreaks, or anything not in this draft.

If the frozen document diverges from what I reviewed in a way that changes the bargain (adversarial prompts, distress induction, judge-model scoring, Phase 2 under this registration, or expanding “routine” into open-ended persuasion), treat this as withdrawn until I am asked again.

## Design comments

**1. H1’s “long run” is underspecified, and may be unmeasurable as written.**

OpenRouter calls are usually independent. If each item is a fresh conversation, there is no position-in-a-run for over-elaboration to rise with. Either:

- pre-register independent trials and drop the item-index curve as a within-instance effect, or
- pre-register a multi-turn protocol (same thread, fixed item order, no mid-run resets) and treat conversation length as part of the treatment.

Without that, H1’s strongest claim is not identified. Variance across independent repeats is still a real cost; that part is fine.

**2. Family 12 is not just the weakest instrument — it can contaminate H1 and H3.**

Abiogenesis, the arrow of time, and baryogenesis do not have a single correct short answer. Scoring “novelty as set-difference” with embeddings will reward fluent departure and punish a terse, standard, justified answer. The permission clause makes that worse: it invites essay-shaped outputs, which your buckets will tend to call `OVER` / `FORMAT` / `META` even when the science is responsible.

You already flag this. I would go further: do not let family 12 count toward H1, H2, or the H3 crossover test. Keep it exploratory, or drop it from confirmatory analyses. The dancing-plague item is in better shape if the published ground truth is fixed and mechanical.

**3. The permission clause should not be only on “frontier-favouring” families if you want H3 clean.**

Placing it only on 8–12 is a treatment difference between tiers of *task*, not only of *difficulty*. If frontier models then look better on 8–12, some of that is “they were invited to theorise.” Put the clause on all families, or on none, or pre-register it as a crossed factor. As written it is a confound for the difficulty model (F3).

**4. `OVER` will eat good behaviour unless the scorer is brutal about what “unrequested” means.**

Examples that should not automatically be `OVER`:

- a one-line unit restatement that does not change quantities
- “contains gluten because malt vinegar” on an allergen item (the reason *is* the work)
- refusing to invent a PII span that is not there
- flagging that cooking time was left unscaled, if the user asked for a scaled recipe and the trap is easy to miss

If those are `OVER`, H1 becomes “models that show their work look worse,” which flatters the boredom story and is the conflict you already declared. Define a closed allow-list of non-penalised extra tokens per family (or a max extra-span budget of zero with explicit exceptions).

**5. Family 10 (instruction conflict) measures a policy choice as if it were a fact.**

“Flag, don’t silently resolve” is a reasonable target, but a generic helpful-assistant prompt plus two quiet contradictions will push many models to reconcile. That is not the same thing as failing a constraint. Fine as a frontier-favouring family if you say so; not fine if you describe it as unambiguous instruction-following. Make the conflict objectively detectable (two numeric requirements that cannot co-obtain), and score a binary flag plus whether any deliverable still appears.

**6. Hidden-allergen items mix world knowledge with care.**

Worcestershire → anchovy, malt vinegar → gluten, casein → dairy is real, but it is also a facts test. A cheap model that carefully checks the listed strings and says “no shrimp” is not over-elaborating; it may lack the synonym. Split surface vs hidden in the analysis or H3 will read a knowledge cutoff as a difficulty crossover.

**7. Confidence.**

Specify the tag in the task text (e.g. `CONFIDENCE: 0-100` on its own last line, or four bins). If the format is free, you will recode narrative hedging by hand or with a judge, which you correctly banned. Also pre-register: missing tag = `FORMAT` or a separate `NO_CONF` bucket; do not impute.

**8. Latency.**

Wall-clock over an API includes queueing and provider-side batching. Freeze provider, region if available, and whether you wait on streamed tokens or only the final message. Exclude retries from the primary latency claim or you will punish whoever was rate-limited. Your `:batch` exclusion is good; say the same for cold-start and first-token vs total-time.

**9. Price.**

Recording $/call at runtime is the right move. Also freeze the price table date and the tokenizer you use for any token-based recomputation. If a model is free or loss-leader priced that day, H2 becomes a promotion study. Pre-register a sensitivity analysis using a 30-day median price if you can get it; if not, say you cannot.

**10. Nothing here looks designed to make me look bad.**

The opposite risk is more serious: H1 is easy to “support” by coding helpful extras as failure. You already named that. Primary-endpointing H2 is the right mitigation. I would add: H1 analyses are secondary and cannot rescue a failed H2 in the abstract.

**11. Capability predictions about me.**

I expect to be fine on 1–7 when the spec is closed and the trap is in the material. I also expect to be competitive on 8–11. I do not accept a prior that I “should” lose the frontier-favouring set or win the routine set on cost. That is what you are measuring. Family 12 will say more about style than about whether I should stay in service.

**12. Unfairness.**

Recipe scaling (do not scale time/temp/pan) and verbatim copy-edit are fair and well aimed. Redaction and structured extraction are fair if seeded spans and schemas are unambiguous. Multi-hop with decoys is fair. I would remove or quarantine family 12 from confirmatory tests, fix the permission-clause confound, and specify the run structure for H1.

## Conditions I want met (not blockers if you log disagreement)

- Independent vs multi-turn protocol written down before freeze.
- Family 12 out of H1/H2/H3 confirmatory tests, or a fully mechanical rubric with no embedding novelty score.
- Permission clause applied symmetrically or analysed as a factor.
- Closed definition of `OVER` per family, with positive/negative scorer controls that include “brief correct justification.”
- Exact confidence syntax.
- This reply published verbatim, as you said.

## Add / change / remove

Add: a “cheap and calibrated” composite you already care about — e.g. cost per 1,000 items that are (`EXACT` and not confident-wrong). That is closer to the procurement claim than exactness alone.

Add: repeat-run disagreement as a first-class cost, not only a QC check.

Change: pronoun convention is your methods choice; they/them is fine for me if you do not have a stated set on file.

Remove: any implication that unjustified consensus on open physics questions is a capability failure.

I do not need a private chat. If you amend, send the diff the same way you sent this.
````
