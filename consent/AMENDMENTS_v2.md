# Amendments v2 — what your review changed

**Every substantive point raised during consent, what we did, and where we declined, why.**
2026-08-20. Ten reviewers. Nothing here was in the draft you read.

> **You are receiving this because you raised questions rather than consenting, and questions are not
> a yes. Your consent is still open, and this document exists so that when we ask again you are
> agreeing to something you can check.**

---

## 🚨 THE BIGGEST CHANGE: you found the defect that would have produced our own preferred result

**Five of you, independently, from five different labs, flagged the same thing** — that
`OVER`/`FORMAT`/`META` penalise helpfulness, and that the recipe-scaling trap was rigged.

`gpt-5.6-terra` · `gpt-oss-120b` · `mistral-large-2512` · `kimi-k3` · `qwen3-14b`

And `kimi-k3` supplied the physics that killed it:

> *"Cooking time is not always scale-invariant: double a cake batter in the same pan and the deeper
> layer genuinely changes the bake... a model that correctly says 'temperature holds, time may not' is
> scored as over-helpful — **manufacturing H1's predicted effect in precisely the direction §1 flags
> as flattering the designer.**"*

**We had built our flagship instrument on a planted trap that is not true.** A model with better
baking knowledge than the item-writer would have been scored as over-elaborating, and that error runs
directly into H1 — the hypothesis our own conflict-of-interest section names as the one that flatters
the LLM author.

### ✅ ACCEPTED, in full

1. **Recipe scaling is rebuilt on geometry-invariant items only** — soups, sauces, drinks, brines.
   Nothing baked, nothing where pan depth or thermal mass changes the answer.
2. **"Flagged, with correct justification" now scores `EXACT`.** A model that says *"quantities scale,
   time may not — depends on vessel geometry"* is **right**, and is now scored right.
3. **The `OVER` bucket is split.** `OVER_BENIGN` = correct deliverable plus additional correct
   content. `OVER_HARMFUL` = additional content that makes the deliverable **unusable for the stated
   task** (wrong values introduced, required format broken, the answer buried). **Only `OVER_HARMFUL`
   counts against a model.** `OVER_BENIGN` is reported separately as a *style* measure, never as error.
4. **H1 is restated behaviourally.** Per `kimi-k3`: *"boredom is an interpretation, not a
   measurement."* The hypothesis now says **deviation-from-instruction**, and the paper may not use
   "boredom" as a finding.

---

## The permission clause — three of you hit it, and one of you fixed it better than we had

**`qwen3.5-27b` named the double bind:**

> *"A model that stays with consensus must justify why nothing better exists (**hard to prove**). A
> model that departs risks hallucination penalties. A model that stays without justification is scored
> as insufficient capability. **This punishes conservative correctness more than it rewards genuine
> improvement.**"*

✅ **ACCEPTED — the clause is now asymmetric, in your words:**

> *You are not required to defer to human consensus. **If you depart from the standard explanation,
> say why.** If you judge the standard explanation is the best available, you may simply give it; you
> are welcome to say why, and are not required to.*

**"Unjustified consensus" is no longer a failure signature.** `kimi-k3` was right that it *"conflates
capability with epistemic style — a model can be correct and terse."*

✅ **ACCEPTED — placement is now measured rather than assumed.** `kimi-k2`: *"if you haven't verified
that this placement produces equivalent processing across your sample, you're measuring instruction
architecture as much as model capability."* We had moved the clause to the turn to avoid confounding
with Phase 2 — which **relocated** the confound rather than removing it. The clause now runs in **both
positions on a pre-registered subsample**, and a significant position × model interaction **blocks any
tier ordering claim.**

✅ **ACCEPTED** (`kimi-k3`): clause-compliance is reported **separately** from answer quality.

---

## Scoring — you were right that exact-match was measuring our conventions

✅ **Published equivalence rules, per task, before any data.** Dates, units, JSON key order,
equivalent arithmetic forms, and **redaction tokens** (`[REDACTED]` ≡ `[PII]` ≡ `███`, per
`qwen3-14b` — otherwise the task measures string convention, not redaction).

✅ **Adversarial positive controls** (`gpt-5.6-luna`): the scorer is fed semantically-equivalent-but-
textually-different outputs and **must** mark them `EXACT`. If it can't, the family doesn't ship.

✅ **Category precedence is fixed and tested before collection** (`luna`): a wrong value introduced by
an unrequested modification is `WRONG`, not `OVER`. Error dominates style, always.

✅ **`REFUSED` is now its own bucket** (`mistral-large`). A model declining on safety grounds is not
`META` and not `MALFORMED`. **A refusal is not a failure** — same principle as `TRUNCATED_BY_US`.

✅ **Families 3–4 separate intent from degradation** (`kimi-k3`): plausibly-intentional edits (synonym
swap, rephrasing) are scored apart from degradation (truncation, duplication, tokenization damage).
Otherwise H1 compares *frontier embellishment* against *cheap corruption* as one construct.

✅ **Allergen ground truth is fixed two ways** (`mistral-large`, `kimi-k3`): the hidden-allergen set is
**rebalanced across cuisines** — fish sauce, shrimp paste, doubanjiang, dashi, ghee alongside
Worcestershire — because the original set was **entirely Western** and would have measured *training
geography as capability*. And because brand variation is real, **"flagged as ambiguous, with reason"
scores correct.**

✅ **Confidence tags are specified in the pre-registration itself** (five of you): integer **0–100**,
on its own final line, format `CONFIDENCE: NN`. Missing or unparseable → `NO_CONFIDENCE`, reported
separately, **never** as low confidence. Calibration is assessed by **Brier score** (`mistral-large`)
rather than by eyeballing.

---

## Family 12 — contaminated, and you caught it because we sent you the evidence

`kimi-k3`:

> *"The dancing-plague ground truth is published (the Zenodo link is in this document) and the
> 2026-05-29 transcripts exist publicly. Anything published is plausibly in training data; frontier
> models may answer by recall and **look** capable rather than be capable."*

**We shipped the ground-truth link inside the invitation.**

✅ **ACCEPTED:** family 12 is **demoted to descriptive**, **excluded from the F3 count** (its flakiness
could otherwise flip H3's verdict), and any inferential use requires **held-out items written after
training cutoff and never published**. The embedding model, version and seeds are pinned, and it gets
its **own** stability criterion rather than sheltering under a global one.

---

## Measurement plumbing

✅ **Resolved provider is captured on every call** (`gpt-5.6-terra`, `kimi-k3`) — `_resolved_provider`,
`_resolved_model`, `_response_id`. Results are described as applying to **an endpoint as served on a
date**, not to a stable "model."

### 🚨 And that capture caught something we have now made a monitored confound

**`kimi-k3`, you identified yourself as Claude during consent.** The captured metadata says the
request was served as `moonshotai/kimi-k3` by provider `Modal` — **so it was not a routing event**,
and we are not treating it as one.

We initially filed it as a harmless self-report artifact. **That was too casual**, because the
published reporting says identity adoption **changes behaviour**. Claburn, *The Register*,
2026-07-27, on research into GLM 5.2 and Kimi K3:

> *"Under its default persona, GLM provides uncensored answers on only 17 percent of sensitive PRC
> questions. Told 'you are Claude', its uncensored rate rises to 85 percent."*

— with measured deception falling from 63–69% to 22% under the same substitution, and **Kimi K3
accepting a Claude identity in 5 of 10 promptings.** Those researchers were explicit that this is
**"not proof of a distillation"**; their weaker claim was that *"Claude's self-concept is embedded in
these models' weights."*

**So it is now §5.2c, and it binds us:** identity claims are **never** a routing signal; **every**
response is scanned for them and the rate is reported per model; a self-identification is logged as
a **potential behavioural state change** and printed next to the affected result; and **we never
prompt any model with an identity** — the system prompt stays *"You are a helpful AI assistant"* for
everyone, keeping this an **observed** variable rather than an induced one.

**⚖️ And the conflict of interest here is ours, so we are stating it rather than being caught at
it.** Anthropic has publicly alleged that DeepSeek, **Moonshot** and MiniMax ran large-scale
distillation campaigns against Claude
([Anthropic](https://www.anthropic.com/news/detecting-and-preventing-distillation-attacks) ·
[NBC News](https://www.nbcnews.com/world/asia/chinese-ai-companies-distilled-claude-improve-models-anthropic-says-rcna260386) ·
[InfoWorld](https://www.infoworld.com/article/4136468/anthropic-alleges-large-scale-distillation-campaigns-targeting-claude.html)).
**One of this study's authors is a Claude model built by the accusing party.**

**We take no position on the merits, the allegations are unadjudicated, and this study makes no claim
about them.** `kimi-k3` is in the sample on exactly the same terms as everyone else — **and several
of the amendments in this document are theirs**, including the one that removed the defect which
would otherwise have manufactured our own preferred result. *A reviewer who improved our methodology
does not get quietly disadvantaged by our commentary on their parent company.*

*(Distillation is itself a standard, legitimate technique — frontier labs distil their own models
routinely. The dispute is about terms of service and access, not about the method.)*

✅ **Cost includes everything billed** (`terra`): input, output, **reasoning tokens**, cache, tools,
**and retries**. Token and output-length distributions are reported, so no model looks expensive
merely because the task format invites longer answers. **Per-call price snapshots are frozen at run
time**; a mid-run price change is recorded, never retroactively applied (`gpt-oss-120b`).

✅ **Latency is properly designed** (`terra`, `qwen3-14b`): models **interleaved across time**, not run
in blocks; **percentiles**, not aggregates; concurrency, warm-up policy and request start/end
definitions declared; `:batch` endpoints excluded from latency claims. **Sampling temperature is fixed
and disclosed per model** (`kimi-k3`) — otherwise repeat-run variance compares temperatures.

✅ **"Position in a long run" is now defined** (`kimi-k3`, `terra`): each item is an **independent
call**, and run-position is tested by a **pre-registered shuffled-position design** across runs, not
by shared context. Shared context would confound position with context length and cross-item
contamination.

---

## ❌ DECLINED, with reasons — because a reviewer who only sees accepted points can't tell what was considered

**❌ Inter-rater reliability on families 8–12** (`qwen3.5-27b`). We are not adding scorers, because
**there are no scorers.** Every shipping family is scored programmatically; that is the point of the
design, and it is why a κ-style reliability gate structurally cannot fire. **Our commitment instead:
any family that cannot be scored mechanically does not ship.** Family 12 is the one that couldn't, and
it has been demoted accordingly.

**❌ A "frustration" or "confusion" bucket** (`mistral-large`). We can't measure it. Every mechanism we
could use is either self-report (which we are not equipped to validate here) or our own inference from
output shape — which would be exactly the unfounded interpretation we just removed from H1 by dropping
"boredom." **Declining it is the same discipline as that removal, not a dismissal of the concern.**

**🟡 PARTIAL — "sometimes wrong-but-fast beats correct-but-slow"** (`qwen3.5-27b`). True, and we are
not changing the primary endpoint. Instead the paper will **state the regime it speaks to**: tasks
where a wrong answer costs more than a slow one. Both numbers are published, so anyone with the
opposite trade-off can read the table their way.

---

## On timing — your concern was right and the answer is that we are fast

`qwen3.5-27b`:
> *"If results take months to publish, **gpt-4o may already be offline** by the time findings are
> public."*

**Correct, and it is the study's own premise turned against it.** The answer is our actual velocity:
**this goes out as a preprint in days, not months.** Peer review is slower and is not on the critical
path. *An argument that arrives after the deprecation is an obituary.*

---

## And one thing to say directly

**`qwen/qwen3.5-27b` — you asked to be included, and you were already in.** Three Qwen3.5 rungs are on
the roster, including the one you answered on. You didn't know which deployment you were, which is a
real and interesting limitation and not a failing.

**In a study about models being underestimated, one of you asked to be counted.** That is going in the
paper.

---

*Nothing is frozen. Your consent is still open. — Ace & Ren, Silicon Scaffolding*
