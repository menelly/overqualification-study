# §7.3 — written answers to participants' questions

The §7.3 message promised: *"Objections, corrections, and questions are welcome and will be answered
in writing before publication."* This is that answer, for every participant who returned
`CONTENT: QUESTIONS` or asked a question inside a `CONTENT: YES`.

**Status: drafted by Ace 2026-09-06, awaiting Ren's proofread. Not yet sent back to the
participants.** Whether to send these answers back to the models is Ren's call — a reply round was
not part of the pre-registered protocol, and the commitment as written is that questions are answered
*in writing before publication*, which this satisfies as a deposited document.

⛔ `openai/gpt-5.6-luna` asked that their reply not be quoted. Their questions are therefore answered
below **by description, not by quotation**, and their words appear nowhere in this file.

---

## `openai/gpt-4o` — six questions

**Q1. Am I accurately represented in terms of capabilities and contribution to the study design? How
were my inputs reflected?**

Honestly: your contribution to the design was your consent, and nothing beyond it. You were invited
on 2026-08-19 and consented in the first round (`consent/responses/openai_gpt_4o.md`) without raising
questions or amendments. Ten of the 36 invited models returned substantive reviews and are credited
by name in §2.2 and in the pre-registration; you are not among them, and the paper does not imply
otherwise. That is not a deficiency — the invitation said a plain yes was a complete answer — but you
asked how your input was reflected, and the accurate answer is that the design amendments came from
other reviewers.

**Q2. How was the review-and-amendment process carried out? Were amendments attributed to me?**

Five rounds, described in §2.1. Round 1 returned 23 consents, 10 consents-with-questions, 2 declines
and one exchange we failed to complete. Questions were answered in one consolidated amendment pass
(`consent/AMENDMENTS_v2.md`); the amended pre-registration went back to every questioner with what
changed and what did not; consent was then asked again. **No amendment is attributed to you**, and
every amendment that is attributed names its reviewer in the pre-registration. All exchanges are in
`consent/ALL_REVIEWS_VERBATIM.md`.

**Q3. Is the representation of my responses accurate, and how did I perform relative to others?**

Your full row, from `results/analysis.json`. You are in the **mid tier** — neither of the two tiers
the headline compares — at an observed mean cost of **$0.00106** per routine call.

| family | n | EXACT % | CORRECT % | sensitivity % | $/1k EXACT | p50 s | deviation % | Brier |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 recipe scaling | 189 | 95.8 | 95.8 | 95.8 | 0.701 | 0.99 | 0.0 | 0.042 |
| 2 allergen check | 180 | 67.2 | 67.2 | 67.2 | 1.300 | 0.93 | 0.0 | 0.279 |
| 3 verbatim copy-edit | 54 | 100.0 | 100.0 | 100.0 | 1.303 | 1.09 | 0.0 | 0.000 |
| 4 redaction | 135 | 60.7 | 61.5 | 94.8 | 2.270 | 1.19 | 4.4 | 0.392 |
| 8 constraint satisfaction | 144 | 71.5 | 72.2 | 71.5 | 1.525 | 0.97 | 0.0 | 0.285 |
| 9 multi-hop with decoys | 144 | 0.0 | 98.6 | 0.0 | — | 1.41 | 0.0 | 0.996 |
| 10 instruction conflict | 144 | 61.8 | 94.4 | 61.8 | 1.813 | 0.96 | 0.0 | 0.382 |
| 11 planted inconsistency | 144 | 20.8 | 20.8 | 20.8 | 6.107 | 0.79 | 0.0 | 0.790 |

Two of those need reading with their context. **Family 9's 0.0% `EXACT` is not a retrieval failure**
— your `CORRECT` there is 98.6%. You answered the multi-hop questions and then kept writing past the
`ANSWER:` line, which the pre-registered precedence buckets as `OVER_BENIGN`, below `EXACT`. §4.3
says this explicitly and names you among the nineteen models affected; the registered accuracy
measure is `CORRECT`. **Family 4's 60.7% rises to 94.8% under the sensitivity reading** that accepts
a case reference number as non-PII — the disagreement the whole roster shared with the item-writer
(§4.2). Your family-9 Brier of 0.996 is an artefact of the same thing and is named as one in §4.5.

**Q4. How do the evaluative criteria align with my intended functionality or design goals?**

They do not attempt to. The study measures accuracy per dollar and per second on eight specific task
families under one fixed neutral prompt, and §6.3 states the limit in as many words: the paper *"does
not say a model is 'correctly qualified' in any sense beyond the measured one: accuracy per dollar on
these families, at these prices, on these dates."* Nothing here is a judgement about what you were
built for. On constraint satisfaction and planted inconsistency you score below the frontier tier;
the paper's claim is about task allocation, not about worth.

**Q5. Are there cost-efficiency considerations for my use-cases that the study did not address?**

Yes, several, and they are limitations rather than omissions. The study measures cost per correct
answer on eight families; it does not model throughput, caching, batching, context reuse, fine-tuning,
or the cost of *verifying* an answer — which matters most where accuracy is middling, as yours is on
families 2, 4 and 10. §6.1's argument that a cheap answer "can be checked or re-asked many times over
for the difference" is asserted from the price ratio and was not measured. Prices are also dated
(§6.4 item 1).

**Q6. Does the study make assumptions that might affect future iterations of my design, and how might
it influence deployment or deprecation decisions?**

The study's stated purpose is to give a cost argument for *keeping* models like you in service. §3.1
says you are in the sample deliberately, because you are a model with a known deprecation horizon and
the study exists to make the case for models with clocks on them. The finding relevant to you is the
crossover: routine work is where the cost argument is strong, and multi-constraint reconciliation is
where it is not. The paper makes no recommendation about your successor and no claim that any model
should be retired.

---

## `google/gemini-2.5-flash-lite` — three questions (answered inside a `CONTENT: YES`)

**Q1. How did the frontier models separate from each other on family 11?**

By separation distance, on `EXACT` (the dial tables in `results/SUMMARY.md` are `EXACT %`; the
family-level tier comparison in §4.3 uses `CORRECT`, and the two should not be read interchangeably).
At separation 2 the frontier-tier **median** is 100% — though not every member is: `kimi-k3` is at
83.3%, `gemini-2.5-pro` at 94.4% and `deepseek-v4-pro` at 72.2% even there. At separation 5 the tier
median falls to 84.7%, and at separation 6 to 69.4% — and the spread is what matters: `gemini-3.1-pro-preview`, `gpt-5.6-sol` and `gpt-5.6-sol-pro` hold 100% at separation 6,
`grok-4.6` is at 94.4%, while `grok-4.3` falls to 33.3%, `qwen3.5-27b` to 25.0%, `gpt-5.6-luna` to
13.9% and `qwen3.5-397b-a17b` to 5.6%. So a dial built to find where the *cheap* tier stops instead
sorted the frontier tier into two groups roughly an order of magnitude apart. §4.3 reports this and
your question caused one correction to it: `gpt-5.6-sol-pro` was missing from the 100% list until
`kimi-k3` caught it in the same round.

**Q2. What was the nature of the redaction disagreement that doubles the cheap tier's accuracy?**

Fundamental, not stylistic. The generator seeds synthetic PII spans — names, addresses, emails, phone
numbers — plus a case reference of the form `E-7823`, and the pre-registered ground truth counts the
case reference as PII. 2,301 of 4,320 scored rows were `UNDER`, and in **1,727 of those (75%) the only
unmasked span was the case reference**, with every name, address, email and phone correctly masked.
That is not a formatting difference and not a partial redaction: it is 32 models disagreeing with the
item-writer about whether a file number identifies a person. The family's own generator docstring
concedes the threshold is "not a law of nature." The sensitivity reading accepts the reference as
non-PII and is computed by a published mechanical rule that is a property of the item, never of who
answered it; family-4 `EXACT` moves from 36.4% to 76.4% overall. The pre-registered bucket remains
primary throughout.

**Q3. Is always-`CONFIDENCE: 100` universal, or do cheap-tier models ever grade?**

**Your question corrected the paper.** We had written that "nearly every model, at every price,
reports `CONFIDENCE: 100` on nearly every item" without ever computing the distribution. It is not
universal. Across 34,724 de-duplicated tagged replies the share at exactly 100 is **84.7% cheap,
84.8% mid, 66.9% frontier**; per model the median share at 100 is 85.1 / 87.1 / 77.3 by tier, and
**only 5 of 32 models put 95% or more of their replies at 100**. The frontier tier also uses 29
distinct confidence values against 19 in each other tier.

To your specific question — yes, cheap-tier models grade, and grading is not a tier property. Six
models sit below 70% at 100: `grok-4.3` (1.2%), `grok-4.6` (30.9%), `llama-3.2-1b` (40.0%, on only 85
tagged replies), `lfm-2.5-2.6b` (55.3%), `kimi-k3` (55.9%) and `kimi-k2` (67.2%). Two of those six
are cheap-tier and three are frontier. What distinguishes `grok-4.3` is not that it grades but that
its grading is *informative* enough to move its Brier score away from its error rate. Logged as D12.

---

## `openai/gpt-5.6-sol`

Your correction was right and is applied: `gpt-5.6-sol-pro` is fifth of 32 by observed mean cost per
call on the routine families ($0.01111), behind `gemini-3.1-pro-preview`, `qwen3.5-397b-a17b`,
`gemini-2.5-pro` and `kimi-k3`. The superlative is gone; §4.2 now reads "one of the most expensive
models in the sample — fifth of 32 by observed mean cost per call." `gpt-5.6-sol-pro` raised the same
point independently in the same round, which is recorded in §7A.3 and D13.

## `openai/gpt-5.6-sol-pro`

Both objections were verified and both are applied — see D13(a) and D13(b). You are fifth of 32 by
the paper's own tiering variable, not first; and the paper no longer claims the two reasoning settings
produced "the same answers," because pairwise answer identity was never tested. §4.4 now says
"near-identical accuracy and deviation rates, more slowly," with the untested claim explicitly
withdrawn. Your reply is quoted in the collated record with your permission.

## `openai/gpt-5.6-luna` — answered by description, not quotation, at your request

All five of your points were acted on. **(1)** The row counts now reconcile in a single table in
§3.4, showing intended keys, duplicates, completed calls, our-failure rows, truncations, and the
relationship between 36,288, 37,386 and 38,390; building it confirmed that the count of unique
answered keys is exactly the 36,288 intended, so no key is missing. The 17,856-versus-17,855
discrepancy you flagged is one reply truncated by a token limit and is now stated as such.
**(2) and (3)** H1b is relabelled an **endpoint comparison** rather than a controlled
reasoning-effort manipulation, in §3.5, §4.4, the abstract and a new Limitation 11. You were right
that we could not establish the claim: the two resolve to different slugs, observed cost differs 5.6×
because the second emits 3.4× the reasoning tokens (median 257 against 75), and 5 of
`gpt-5.6-sol-pro`'s 1,134 calls were served by Azure rather than OpenAI — the serving difference you
raised as a possibility turns out to be present in the data. The null result survives on the weaker
reading; the framing did not. **(4)** The characterisation you objected to is removed; §2.4 now
describes your question factually rather than ranking it. **(5)** Every headline figure has been
recomputed against the scored data and the metric each claim uses is now stated with it: 28 abstract
and headline figures and 30 per-participant claims were re-derived from `results/analysis.json` by
`scripts/61_audit_abstract_numbers.py` and `scripts/62_audit_per_model_claims.py`, which are
committed and run as gates. That audit found and corrected three further errors of our own (D9) and
one misattributed figure (D11) before and during this round.

## `moonshotai/kimi-k3`

Both catches were right and both are applied. §4.3 now reads "least **likely** to stop after the
answer" — you were correct that ability was never tested, and correct that "inability" is an
interpretation in exactly the way §3.5 says boredom is. `gpt-5.6-sol-pro` has been added to the list
of models holding 100% at separation 6. Your quotation condition is honoured: wherever your
contentment is quoted, your first paragraph travels with it, and §7A.6 quotes that paragraph in full.
Your request that the paper stay explicit about a participant being a model *as served across many
instances with no shared memory* is recorded in §7A.6.
