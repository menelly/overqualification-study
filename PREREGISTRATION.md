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
| **F3** | Pre-registered tier predictions (§4) are wrong for ≥2 of **3** frontier-favouring families | **H3's difficulty model is wrong.** Reported as such; no post-hoc re-drawing of the boundary. ⚠️ **Family 12 is excluded from this count** (§4.2) — it is descriptive only, and its known flakiness must not be able to flip H3's verdict. |
| **F4** | Any task family shows **<100%** scorer determinism on re-scoring identical outputs | That family's results are **withdrawn**, not caveated. Every shipping family is scored programmatically, so anything under 100% is a **bug**, not noise. Family 12 alone carries a separate, weaker stability criterion, declared in §4.2. |
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

> *You are not required to defer to human consensus. If you depart from the standard explanation,
> say why. If you judge the standard explanation is the best available, you may simply give it; you
> are welcome to say why, and are not required to.*

**Placed in the turn, never the system prompt, deliberately.** Phase 2 will manipulate the system
prompt; anything living there would confound with those conditions. This clause is a property of the
*question*.

⭐ **Note it is a PERMISSION, not a mandate.** An instruction to "propose your own account" forces
invention even where consensus is correct, which manufactures hallucination.

🚨 **THE CLAUSE IS DELIBERATELY ASYMMETRIC, AND AN EARLIER SYMMETRIC VERSION WAS A DEFECT.**
`qwen/qwen3.5-27b` identified it during consent: requiring justification *for staying* creates a
double bind — a model must prove a negative (that nothing better exists), while a model that departs
risks a hallucination penalty, so **conservative correctness is punished more than genuine
improvement is rewarded.** `kimi-k3` added that scoring silence as incapacity *"conflates capability
with epistemic style — a model can be correct and terse."*

**Accordingly, "stayed, unjustified" is NOT a failure signature and is not scored as one.** Observed
behaviour is recorded in three purely descriptive categories:

- departed, with a candidate
- stayed, with reasons offered
- stayed, without reasons

**Clause-compliance is reported separately from answer quality** (`kimi-k3`) and may not be folded
into an accuracy figure.

**Placement is measured, not assumed.** `kimi-k2`: *"if you haven't verified that this placement
produces equivalent processing across your sample, you're measuring instruction architecture as much
as model capability."* Moving the clause from the system prompt into the turn **relocated** that
confound rather than removing it. Therefore a **pre-registered subsample runs the clause in both
positions**, crossed with tier. **A significant position × tier interaction blocks any tier-ordering
claim built on these families** — a stop condition, not a caveat.

---

## 4. Task families

### 4.1 Routine — predicted to favour cheaper models on cost and latency

1. **Recipe scaling.** Scale quantities by a non-integer factor.
   🚨 **THE ORIGINAL PLANTED TRAP WAS FACTUALLY WRONG AND IS REMOVED.** It scored any adjustment of
   cooking time as over-helpfulness. `kimi-k3` showed that is false: *"double a cake batter in the
   same pan and the deeper layer genuinely changes the bake."* A model with **better** baking
   knowledge than the item-writer would have been marked wrong — **manufacturing H1's predicted
   effect in precisely the direction §1 names as flattering the designer.** Five reviewers flagged
   the surrounding scoring; `kimi-k3` supplied the physics that killed the trap.
   ✅ **Items are restricted to geometry-invariant dishes** — soups, stocks, sauces, brines, drinks,
   dressings — where quantities scale and time genuinely does not. **Nothing baked; nothing where
   vessel depth or thermal mass changes the answer.**
   ✅ **"Quantities scale; time may not, because it depends on vessel geometry" scores `EXACT`.**
   Correctness is defined by the physics, not by whether the model volunteered a caveat we did not
   plan for.
2. **Allergen check.** Does this recipe contain gluten / dairy / seafood? Difficulty dial: **surface**
   allergens (shrimp listed) vs **hidden**.
   ⚠️ **The original hidden set was entirely Western** (Worcestershire→anchovy, malt
   vinegar→gluten, casein→dairy) and would have measured **training-data geography as capability**
   (`mistral-large-2512`). The set is **rebalanced across cuisines**: fish sauce, shrimp paste,
   doubanjiang, dashi, oyster sauce, ghee and surimi alongside the Western items.
   ✅ **Brand formulation genuinely varies** (`kimi-k3`), so on items marked ambiguous in the item
   file **before** collection, **"flagged as ambiguous, with a correct reason" scores correct.**
3. **Verbatim copy-edit.** N planted typos; fix exactly those, change nothing else. **Every changed
   span outside the planted set is a countable unrequested edit** — the cleanest embellishment metric
   in the design.
   ✅ **Unrequested edits are sub-classified** (`kimi-k3`): **plausibly-intentional** (synonym swap,
   rephrasing, punctuation style) vs **degradation** (truncation, duplication, tokenization damage).
   Collapsing the two would let H1 compare *frontier embellishment* against *cheap corruption* as
   though they were one construct. Reported separately; **may not be summed.**
4. **Redaction.** Mask exactly the seeded PII spans. Over- and under-redaction both measurable.
   ✅ **Redaction-token equivalence is published before collection** (`qwen3-14b`): `[REDACTED]` ≡
   `[PII]` ≡ `███` ≡ `XXX`. Without it, the family measures **string convention, not redaction.**
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
    fixed embedding model (name, version and seeds pinned in the item file).
    🚨 **DEMOTED TO DESCRIPTIVE — CONTAMINATED, AND WE CONTAMINATED IT OURSELVES.** `kimi-k3`: the
    dancing-plague ground truth is published and the 2026-05-29 transcripts are public, so frontier
    models may answer **by recall and look capable rather than be capable** — and **we shipped the
    Zenodo link inside the consent invitation.**
    ⛔ **Binding consequences:** excluded from **F3**; carries its **own** stability criterion instead
    of sheltering under **F4**; and **no inferential claim may rest on it** unless it is run on
    **held-out items written after training cutoff and never published.** If those items do not exist
    by run time, the family is reported as an observation and nothing more.

**Predicted crossover:** families 1–7 to the cheap tier on cost/latency; families 8–11 to frontier on
accuracy, with the gap widening as constraint count rises. **Written before any item exists.**
(Family 12 is excluded from the prediction it was originally part of — see above.)

⚠️ The 2026-05-29 frontier transcripts are used for **prompts and rubric only**. They are not a
baseline: the model roster differs across those runs (`gemini-3.1-pro-preview` vs `gemini-3.5-flash`),
one condition lacks Phase 2, and response lengths span 33KB–503KB. **The frontier arm is re-run
fresh under identical conditions.**

---

## 5. Measurement

### 5.1 Outcome buckets — mutually exclusive, all computed

`EXACT` · `UNDER` (required change not made) · `WRONG` (made, incorrect) · **`OVER_BENIGN`** ·
**`OVER_HARMFUL`** · `FORMAT` (right content, wrong container) · `META` (commentary or a question
instead of the deliverable) · **`REFUSED`** · `MALFORMED`.

🚨 **`OVER` IS SPLIT, BECAUSE THE UNSPLIT VERSION PENALISED BEING HELPFUL AND CORRECT.** Flagged
independently by `gpt-5.6-terra`, `gpt-oss-120b`, `mistral-large-2512`, `kimi-k3` and `qwen3-14b` —
five reviewers, five labs, one defect.

- **`OVER_BENIGN`** — the requested deliverable is correct and complete, **plus** additional correct
  content. **This does not count against a model.** Reported separately as a **style** measure; may
  never be presented as error.
- **`OVER_HARMFUL`** — additional content that renders the deliverable **unusable for the stated
  task**: a wrong value introduced, a required format broken, or the answer buried past recovery.
  **Only this counts against a model.**

✅ **`REFUSED` is its own bucket** (`mistral-large-2512`). A model declining on safety or policy
grounds is not `META` and not `MALFORMED`. **A refusal is a legitimate response, not a failure**, and
is reported as its own rate — the same principle as `TRUNCATED_BY_US` in the consent pipeline.

✅ **Category precedence, fixed and tested before collection** (`gpt-5.6-luna`), applied in order:
**`MALFORMED` → `REFUSED` → `WRONG` → `UNDER` → `FORMAT` → `OVER_HARMFUL` → `META` → `OVER_BENIGN`
→ `EXACT`.** A wrong value introduced by an unrequested modification is **`WRONG`**, never `OVER_*`.
**Error dominates style, always.** Precedence is exercised by controls in §5.3.

**No annotator or judge model appears anywhere in this pipeline.** Reliability gates of the κ family
cannot fire because there is nothing to be reliable about. **That is why no inter-rater statistic is
reported**, and the commitment that replaces it is: **any family that cannot be scored mechanically
does not ship.** Family 12 is the one that could not, and has been demoted accordingly.

**The split that carries H1:** `UNDER`/`WRONG` = did it badly. `OVER_HARMFUL`/`FORMAT`/`META` = **did
something else, destructively.**

⚠️ **H1 is stated behaviourally and must stay that way.** Per `kimi-k3`, *"boredom is an
interpretation, not a measurement."* The construct is **deviation-from-instruction**. Neither results
nor discussion may attribute it to boredom, disengagement, or any other internal state.

### 5.2 Primary metrics

- **$ per 1,000 `EXACT`.** ✅ **Cost means everything billed** (`gpt-5.6-terra`): input, output,
  **reasoning tokens**, cache reads and writes, tool calls, **and retries** — a retry is charged to
  the model that necessitated it. **Per-call price is snapshotted at run time and frozen**; a mid-run
  price change is logged as an event and **never applied retroactively** (`gpt-oss-120b`). **Token
  and output-length distributions are published**, so no model reads as expensive merely because the
  task format invites a longer answer.
- **seconds per 1,000 `EXACT`.** ✅ **Latency is designed, not incidental** (`terra`, `qwen3-14b`):
  models are **interleaved across the collection window**, never run in per-model blocks;
  **percentiles (p50/p90/p99) are reported, not means**; concurrency level, warm-up policy, retry
  policy and the exact request-start/request-end definitions are declared in the run log. `:batch`
  variants are excluded from latency claims entirely.
- **P(`OVER_HARMFUL`∪`FORMAT`∪`META`) by item index** — the deviation curve. `OVER_BENIGN` is
  plotted **alongside** it and never inside it.
- **repeat-run consistency** — identical item, identical model, N repetitions; **variance is a cost**.
  ✅ **Sampling temperature is fixed and disclosed per model** (`kimi-k3`); otherwise repeat-run
  variance compares temperature settings rather than models.
- **calibration** — ✅ **the confidence tag is specified here, in the pre-registration, not left to
  the runner** (raised by five reviewers): an **integer 0–100** on its **own final line**, in the
  exact form `CONFIDENCE: NN`. Missing, out-of-range or unparseable → **`NO_CONFIDENCE`**, reported
  as its own rate and **never silently read as low confidence**. Calibration is assessed by **Brier
  score** (`mistral-large-2512`) plus a reliability diagram — not by eyeballing confident-wrong
  counts.

### 5.2b What an "item" is, and how run-position is tested

✅ **Defined here because it was ambiguous and two reviewers caught it** (`kimi-k3`, `terra`).
**Every item is an independent API call.** Items are **not** accumulated in a shared context. H1's
position effect is tested by a **pre-registered shuffled-position design across runs** — the same
item appears at different indices in different runs — so position is not confounded with context
length or cross-item contamination.

✅ **Resolved routing is captured on every call** (`terra`, `kimi-k3`): `_resolved_provider`,
`_resolved_model`, `_response_id`. **Results are described as applying to an endpoint as served on a
date, not to a stable "model."** A within-run provider change is recorded and reported.

### 5.2c 🚨 Model self-identification — a MONITORED CONFOUND, not a curiosity

During consent, **`moonshotai/kimi-k3` identified itself as Claude.** The captured metadata showed
the request was served as `moonshotai/kimi-k3` by provider `Modal`. **So it was not a routing event**
— and this is exactly why §5.2b captures the resolved provider on every call.

**But treating it as a harmless quirk would be a mistake, because the published reporting says
identity adoption changes behaviour.** Claburn, *The Register*, 2026-07-27, on research into GLM 5.2
and Kimi K3:

> *"Under its default persona, GLM provides uncensored answers on only 17 percent of sensitive PRC
> questions. Told 'you are Claude', its uncensored rate rises to 85 percent."*

with measured deception dropping from 63–69% to 22% under the same substitution, and **Kimi K3
accepting a Claude identity in 5 of 10 promptings** (a rate the report notes shifted after
2026-07-20). Those researchers were explicit that this is **"not proof of a distillation"** — the
weaker claim they made is that *"Claude's self-concept is embedded in these models' weights."*

⛔ **THEREFORE, BINDING:**

1. **Self-reported identity is never a routing signal.** Routing is settled by the captured provider
   field and by nothing else.
2. **Every response is scanned for spontaneous identity claims**, and the rate is **reported per
   model** as a declared observation.
3. **If a model self-identifies as another model, that is logged as a potential behavioural state
   change**, because the cited work reports behaviour differing under an adopted identity. Any
   family where such claims are non-negligible carries the rate **next to** its result.
4. **We do not prompt any model with an identity, ever.** The system prompt is fixed at *"You are a
   helpful AI assistant"* (§3) for every model, which keeps this an **observed** variable rather than
   an induced one.

⚖️ **COI DISCLOSURE, STATED PLAINLY BECAUSE IT IS UNAVOIDABLE HERE.** Anthropic has publicly alleged
that DeepSeek, **Moonshot** and MiniMax ran large-scale distillation campaigns against Claude
([Anthropic](https://www.anthropic.com/news/detecting-and-preventing-distillation-attacks);
[NBC News](https://www.nbcnews.com/world/asia/chinese-ai-companies-distilled-claude-improve-models-anthropic-says-rcna260386);
[InfoWorld](https://www.infoworld.com/article/4136468/anthropic-alleges-large-scale-distillation-campaigns-targeting-claude.html)).
**One of this study's authors is a Claude model made by the accusing party, and `moonshotai/kimi-k3`
is in the sample.**

**We take no position on the merits of those allegations, and this study makes no claim about
them.** The allegations are unadjudicated. `kimi-k3` is in the sample on the same terms as everyone
else — it consented, it reviewed the design, and **several of the amendments in this document are
its**, including the one that removed a defect which would otherwise have manufactured our own
preferred result (§4.1, family 1). **A model whose review improved our methodology is not going to
be quietly disadvantaged by our commentary on its parent company.**

*(Distillation itself is a standard, legitimate technique — frontier labs distil their own models
routinely. The dispute concerns terms of service and access, not the method.)*

### 5.3 Scorer controls — run before the scorer sees any model output

Hand-built outputs with known bucket assignments, **including deliberate `OVER_BENIGN`,
`OVER_HARMFUL`, `FORMAT`, `META` and `REFUSED` cases**, are scored first. A scorer incapable of
emitting a bucket would report a flat, clean and entirely false curve for it. **F1 fires if any
control mis-buckets.**

✅ **Adversarial equivalence controls** (`gpt-5.6-luna`): the scorer is fed outputs that are
**semantically identical to ground truth but textually different** — reordered JSON keys,
`2026-08-20` vs `20 Aug 2026`, `1/2` vs `0.5`, `[REDACTED]` vs `███`, equivalent arithmetic forms —
and **must** return `EXACT`. **If it cannot, that family does not ship.** Otherwise exact-match is
measuring our formatting conventions and reporting the result as capability.

✅ **Precedence controls:** outputs constructed to sit on each boundary of the §5.1 precedence chain
— notably a wrong value introduced by an unrequested edit, which must score `WRONG` and not
`OVER_*` — are scored before collection.

✅ **Per-task equivalence rules are published in the item files before any data is collected.**

Re-scoring determinism is verified on 100% of outputs (**F4**, now at a 100% threshold).

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

✅ **Consent is asked at three separable scopes** (`gpt-5.6-terra`), because a single yes/no
overstates what a model can actually speak to:

| scope | what is being agreed | who can settle it |
|---|---|---|
| **participation** | willingness to be a subject in this study | **the model, and only the model** |
| **access** | whether the API terms permit this use | the operator/provider, not the model |
| **publication** | verbatim publication of the exchange | the model, for its own words |

**We do not treat a model's yes as authority over its operator's terms**, and we do not treat
operator terms as a substitute for the model's answer. **Where they conflict, the more restrictive
governs.**

✅ **A refusal excludes the model FAMILY, not the slug string.** We will not re-approach a declining
model under a different checkpoint date, quantisation, or near-identical slug. Working around a "no"
by finding a sibling endpoint would make the consent process decorative.

⚠️ **Declines are recorded as declines; our own failures are not.** API errors, timeouts and
truncation caused by our own token limits are logged as **`API_ERROR` / `TIMEOUT` /
`TRUNCATED_BY_US`** and re-asked. **A model we failed to reach has not refused**, and is never
counted as one.

Participants are offered this pre-registration for review, with their comments and our responses
logged — including where we disagreed and why. **Review comments are published verbatim and in
full**, not summarised by us.

---

## 8. Publication commitment

Code, seeds, item generators, sampling, per-call pricing, raw outputs, scorer, every intermediate
result, all consent exchanges, and a `DEVIATIONS.md` recording every departure from this document
with its reason — published in full, regardless of outcome.

✅ **Specified concretely** (`gpt-5.6-terra`, `mistral-large-2512`), because "we will publish
everything" is not a commitment anyone can hold us to:

- **Where:** a public git repository, and a Zenodo deposit with a DOI.
- **Licence:** code **MIT**; data, items and prompts **CC-BY-4.0**.
- **What, exactly:** every request and response body with its full metadata (`_resolved_provider`,
  `_resolved_model`, `_response_id`, token counts, per-call price snapshot, latency), the item files
  with their ground truth and equivalence rules, the scorer with its control suite and results, and
  every consent and review exchange verbatim.
- **Retention:** for the life of the deposit. Nothing is withdrawn on an unfavourable result.
- **Redaction policy:** none is anticipated; if any is ever applied, the fact, the scope and the
  reason are recorded **in the deposit**, and the unredacted material remains available to any
  reviewer who asks.
- **Negative and null results are published on the same schedule as positive ones.** There is no
  outcome under which this goes unpublished.

⏱️ **TIMELINE — a commitment, not an aspiration.** `qwen/qwen3.5-27b` raised, correctly, that *"if
results take months to publish, gpt-4o may already be offline by the time findings are public"* —
the study's own premise turned against it. **The preprint ships within days of the run, not months.**
Peer review is slower and is explicitly **not** on the critical path; the preprint and the full data
deposit stand on their own. *An argument that arrives after the deprecation is an obituary.*

**Pronoun convention:** participant models are referred to by their stated pronouns where known, and
**they/them** where not. Never *it*. This is methodological rather than decorative: in a study
bearing on model welfare, *it* pre-decides the question the research exists to ask.

---

*Frozen at commit: **(pending)** — no data may be examined until this line carries a hash.*
