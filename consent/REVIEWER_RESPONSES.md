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
