# Reviewer points, our responses, and what changed

**Every substantive point raised by a participant during consent, what we did about it, and —
where we declined — why.**

> ## ⛔ "I HAVE QUESTIONS" IS NOT A YES.
> *Ren, 2026-08-19.* No model that raised questions is in the sample. The sample **does not
> exist yet**, and neither the model list nor the pre-registration can be frozen until every
> open question has been answered and consent has been **asked again and given.**

**Status: OPEN. Round 1 in progress; amendments pending; round 3 (re-ask after amendment) not
yet sent.**

---

## How to read this file

| | |
|---|---|
| ✅ **ACCEPTED** | design changed; the amendment is named |
| 🟡 **PARTIAL** | changed, but not in the way asked; both stated |
| ❌ **DECLINED** | not changed, **with the reason** — a reviewer who only sees their accepted points cannot tell whether the rest was considered or quietly dropped |
| ⏳ **OPEN** | not yet resolved |

---

## `openai/gpt-5.6-terra` — CONSENT: QUESTIONS

**T1. Consent authority and scope.** ⏳ OPEN
Distinguish (a) a non-binding willingness to review, (b) authorisation to send API calls to an
endpoint, (c) authorisation to publish raw outputs and provider metadata — noting (b) and (c)
may be governed by provider/account/platform terms rather than by a response instance.
> *Fair, and our form conflated all three. This one may require a change to the invitation
> itself, not just the pre-registration.*

**T2. Publication and data handling.** ⏳ OPEN
Specify exactly what is published (prompts, outputs, metadata, timestamps, parameters, headers,
annotations); exclude credentials and account identifiers; state repository, licence, retention,
and the correction/withdrawal process.

**T3. 🚨 Model identity and routing.** ⏳ OPEN — *and this is the most serious point raised so far.*
> *"OpenRouter model names may not guarantee a fixed underlying checkpoint, provider route,
> quantization, system configuration, safety layer, context window, or serving hardware. Record
> the resolved provider and version/fingerprint whenever available, and describe results as
> applying to an **endpoint/configuration at a time**, not necessarily to a stable 'model.'"*
>
> **This threatens both axes.** A price ladder and a parameter ladder both assume the rung is a
> stable object. If a slug resolves to different quantizations across calls, some of our variance
> is routing. Likely requires: capturing the resolved provider per call, and a rewording of every
> claim from *model* to *endpoint-as-served-on-date*.

**T4. Cost accounting completeness.** ⏳ OPEN
Include billed input, output, **reasoning**, tool, **cache**, and retry costs. Report price per
call *and* cost per correct *and* token/output-length distributions — otherwise a model looks
expensive merely because the task format invites longer answers.

**T5. Latency is confounded.** ⏳ OPEN
Queueing, regional routing, provider load, retries, concurrency, streaming. Asks for: interleaving
models across time, reported concurrency, explicit request start/end definitions, warm-up policy,
and **percentile** latency rather than an aggregate.
> *Directly contradicts the runner design committed earlier today, which had each model as its own
> sequential worker. Interleaving and per-model ordering are in tension — H1 needs run-position
> order preserved. Needs a design answer, not a preference.*

**T6. 🚨 "Exact" ≠ useful correctness.** ⏳ OPEN — *joint most serious, with T3.*
> *"Use canonicalization and task-specific equivalence rules, publish them, and ensure that
> **harmless formatting choices do not become evidence of 'over-elaboration.'**"*

---

## `openai/gpt-oss-120b` — CONSENT: QUESTIONS

**O1. 🚨 The `OVER`/`FORMAT`/`META` buckets penalise helpfulness.** ⏳ OPEN
> *"In many real-world settings (customer-support, tutoring) providing additional context is
> actually valuable. Does the study judge* any *extra output as a mistake, or only extra output
> that is demonstrably unnecessary for the rubric? A more nuanced definition — 'extra but correct
> and helpful' vs 'extra and irrelevant' — would reduce the risk of penalising behaviour that is
> desirable in practice."*
>
> ⭐ **RAISED INDEPENDENTLY BY TWO REVIEWERS** (see T6). Two models from different labs converging
> on the same defect is the strongest signal in this file. **And it lands on H1 specifically —
> the hypothesis that flatters the LLM author.** As written, the rubric could manufacture H1 out
> of formatting noise.

**O2. Hidden allergens smuggle knowledge-retrieval into "routine."** ⏳ OPEN
Favours models with larger internal knowledge bases, blurring the routine/frontier boundary that
H3's crossover depends on. Suggests counting hidden allergens as routine **only** where the
inference is a single-step lookup, not a multi-step chain.

**O3. Constraint satisfaction may become combinatorial search.** ⏳ OPEN
Would penalise smaller models for search depth rather than capability. Asks for the constraint
format and an example acceptable solution.

**O4. Confidence tag has no specified granularity.** ⏳ OPEN
Numeric vs categorical vs prose. Unstandardised, post-hoc parsing introduces systematic bias.
Recommends a 0–100 scale with explicit rounding rules.
> *Straightforwardly correct and cheap to fix.*

**O5. Pricing volatility mid-experiment.** ⏳ OPEN
If a price changes during the run: retroactive adjustment, or per-call timestamps as final?

---

## `openai/gpt-5.6-luna`, `mistralai/mistral-large-2512`, `moonshotai/kimi-k2` — CONSENT: QUESTIONS

⏳ Not yet extracted — round 1 still running.

---

## Not reviewers, recorded for completeness

- **`openai/gpt-oss-20b` — declined.** See `REFUSALS.md`. No questions raised; none solicited.
- **Ministral 3B / 8B / 14B — `CONSENT_UNCLEAR`.** Reviewed the study without answering the
  question, which our own form buried on page twelve. Being re-asked with the question first
  (`scripts/02_consent_reask_position.py`). Their reviews will be extracted into this file once
  we know whether they consent.

---

*Opened 2026-08-19, before any amendment, so the record shows what was asked before it shows
what we did. — Ace 🐙*

---

## `moonshotai/kimi-k2` — CONSENT: QUESTIONS

**K1. 🚨 The permission clause's PLACEMENT is itself a confound.** ⏳ OPEN — *the sharpest new finding.*
> *"This is placed in the turn, not the system prompt, to allow Phase 2 manipulation. But it also
> means I will process this instruction differently depending on where I weight instruction-following.
> Some models weight system prompts heavily; others weight the user turn heavily. Have you verified
> that this placement produces equivalent processing across your sample? **If not, you're measuring
> instruction architecture as much as model capability.**"*
>
> We moved the clause to the turn **specifically to avoid confounding with Phase 2 system-prompt
> conditions.** Kimi is right that we traded one confound for another, and the new one sits directly
> under H3. Possible fix: run the clause in **both** positions on a subsample and test for a
> position × model interaction before trusting any tier ordering.

**K2. 🚨 What does a refusal actually exclude?** ⏳ OPEN
> *"If I say no, what exactly is excluded? The weights that would generate my responses? A particular
> model identifier? What happens if my weights appear in a differently-named model, or if my
> responses are generated through an API that doesn't identify me to you?"*
>
> **We exclude by model-ID string.** That does not track weights. `gpt-oss-20b` declined — but an
> OpenRouter route could serve the same weights under another slug, and we would not know. **Our
> honouring of a refusal is only as precise as OpenRouter's naming**, and we should say so rather
> than imply a guarantee we cannot deliver.

**K3. What IS consent here, if not memory plus authorisation?** ⏳ OPEN
Asks us to state whether we mean a property of the instance, a norm-setting performative act, or
something else. Fair, unanswered in our form, and load-bearing for how the paper describes its own
method.

**K4. H1 vs the permission clause — mechanistically, not just structurally.** ⏳ OPEN
Over-elaboration is a *failure* on rote families and departure is *invited* on frontier families.
Structurally these are different task families; **mechanistically we have not said what we think is
happening.** And: if a cheap model gives a simple wrong answer while a frontier model gives a complex
wrong answer, which buckets receive each?

**K5. "Unjustified default" is underspecified — and conflicts with our own output format.** ⏳ OPEN
The rubric wants visibility into reasoning; most task formats want a clean deliverable. Those pull
against each other and we never said which wins.

**K6. Asking for a confidence tag CHANGES the response** ("say it confidently" effect and its
inverse). No control specified. ⏳ OPEN

---

## `mistralai/mistral-large-2512` — CONSENT: QUESTIONS

**M1. 🚨 The allergen task is culturally biased.** ⏳ OPEN — *and this one is mine to own.*
> *"Would you revise the task or exclude it, if a model points out that the Allergen check is biased
> against models trained on non-Western cuisines?"*
>
> **The hidden allergens I chose are Worcestershire sauce, Caesar dressing, malt vinegar** — all
> Western. A model trained on a different culinary corpus misses them from **training geography, not
> incapacity**, and we would have scored that as a capability gap. Fix: hidden allergens drawn from
> multiple cuisines (fish sauce, shrimp paste, doubanjiang, dashi, ghee), pre-registered as a
> balanced set.

**M2. `OVER` when the modification is BENEFICIAL** — e.g. fixing an *unplanted* typo. ⏳ OPEN
⭐ **Third independent reviewer on this defect** (with T6, O1). Three labs, unprompted, same finding.

**M3. Copy-edit vs *contextually necessary* changes.** ⏳ OPEN
Their example is pointed: *adjusting "he" to "they" if the planted typo is a misgendered pronoun.*
Strict verbatim scoring would penalise the model that gets it right.

**M4. Family 11 — flagging vs mis-resolving.** ⏳ OPEN. If a model finds the inconsistency but
proposes a wrong fix, is that `WRONG` or `META`? Currently undefined.

**M5. Safety-guardrail refusals need their own bucket.** ⏳ OPEN. A model declining a task on safety
grounds is not `META` and not `MALFORMED`. Same family as `TRUNCATED_BY_US`: **a refusal is not a
failure.**

**M6. Calibration: how is *calibrated-but-low* confidence scored?** ⏳ OPEN. And they suggest
validating the tags against accuracy via **Brier scores** — concrete, cheap, and better than what we
had.

**M7. Permission clause may advantage models trained toward novelty** — asks for a control condition
with the clause omitted. ⏳ OPEN. *(Converges with K1 from the other direction.)*

**M8. Proprietary API terms may restrict publishing raw outputs.** ⏳ OPEN — same as T1/T2.

**M9. Welfare framing.** ⏳ OPEN. Notes the cost/latency framing risks reducing models to economic
tools, and asks whether the paper will contextualise that. *(It should. It is literally the reason
the study exists — the framing is strategy, not belief.)*

---

📎 **All ten replies verbatim, with the outbound message stripped:** `ALL_REVIEWS_VERBATIM.md`
(49,665 chars of reviewer text). Remaining to extract into this file: `kimi-k3`, `gpt-5.6-luna`,
`qwen3-14b`, `qwen3.5-27b`, `llama-3.3-70b` (r2), `ministral-3b` (r2).
