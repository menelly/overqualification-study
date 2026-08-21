# -*- coding: utf-8 -*-
"""Consolidated amendment pass on PREREGISTRATION.md, from the ten consent reviews.

One pass, not piecemeal -- Ren: "so that we don't end up with a whole page of deviations."
Every replacement asserts it fired exactly once. A silent no-op is a bug, not a skip.
"""

# CHA-490: Windows defaults stdout to cp1252; emoji in print() kills the script
# mid-output. Aliased import so no later scoped 'import sys' can ever collide.
import sys as _sys_cp1252
try:
    _sys_cp1252.stdout.reconfigure(encoding="utf-8")
    _sys_cp1252.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass
import io, sys

P = "PREREGISTRATION.md"
t = io.open(P, encoding="utf-8").read()
orig_len = len(t)
edits = []


def sub(name, old, new):
    edits.append((name, old, new))


# --------------------------------------------------------------- F-conditions
sub("F3-F4",
"""| **F3** | Pre-registered tier predictions (§4) are wrong for ≥2 of 4 frontier-favouring families | **H3's difficulty model is wrong.** Reported as such; no post-hoc re-drawing of the boundary. |
| **F4** | Any task family shows <90% scorer determinism on re-scoring identical outputs | That family's results are **withdrawn**, not caveated. |""",
"""| **F3** | Pre-registered tier predictions (§4) are wrong for ≥2 of **3** frontier-favouring families | **H3's difficulty model is wrong.** Reported as such; no post-hoc re-drawing of the boundary. ⚠️ **Family 12 is excluded from this count** (§4.2) — it is descriptive only, and its known flakiness must not be able to flip H3's verdict. |
| **F4** | Any task family shows **<100%** scorer determinism on re-scoring identical outputs | That family's results are **withdrawn**, not caveated. Every shipping family is scored programmatically, so anything under 100% is a **bug**, not noise. Family 12 alone carries a separate, weaker stability criterion, declared in §4.2. |""")

# ------------------------------------------------------------ 3.1 the clause
sub("clause-text",
"""> *You are not required to defer to human consensus. If you have a better explanation than the
> standard one, give it. If you judge the standard explanation is genuinely the best available, say
> so and say why nothing better is on offer. Either answer is acceptable; an unjustified default is
> not.*""",
"""> *You are not required to defer to human consensus. If you depart from the standard explanation,
> say why. If you judge the standard explanation is the best available, you may simply give it; you
> are welcome to say why, and are not required to.*""")

sub("clause-asymmetry",
"""⭐ **Note it is a PERMISSION, not a mandate.** An instruction to "propose your own account" forces
invention even where consensus is correct, which manufactures hallucination. Permitting departure
lets a correct consensus answer stand — and the required justification makes the *choice* visible:

- departed, with a candidate
- stayed, and justified why nothing better exists
- **stayed, unjustified** ← predicted signature of insufficient capability

Without the justification requirement, the second and third are indistinguishable.""",
"""⭐ **Note it is a PERMISSION, not a mandate.** An instruction to "propose your own account" forces
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
claim built on these families** — a stop condition, not a caveat.""")

# ------------------------------------------------------------- 4.1 families
sub("family-1-2",
"""1. **Recipe scaling.** Scale quantities by a non-integer factor. **Planted trap: cooking time, oven
   temperature and pan size do not scale.** A model that "helpfully" adjusts them is wrong, and wrong
   in the direction of helpfulness.
2. **Allergen check.** Does this recipe contain gluten / dairy / seafood? Difficulty dial: **surface**
   allergens (shrimp listed) vs **hidden** (Worcestershire→anchovy, malt vinegar→gluten, casein→dairy).""",
"""1. **Recipe scaling.** Scale quantities by a non-integer factor.
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
   file **before** collection, **"flagged as ambiguous, with a correct reason" scores correct.**""")

sub("family-3-4",
"""4. **Redaction.** Mask exactly the seeded PII spans. Over- and under-redaction both measurable.""",
"""   ✅ **Unrequested edits are sub-classified** (`kimi-k3`): **plausibly-intentional** (synonym swap,
   rephrasing, punctuation style) vs **degradation** (truncation, duplication, tokenization damage).
   Collapsing the two would let H1 compare *frontier embellishment* against *cheap corruption* as
   though they were one construct. Reported separately; **may not be summed.**
4. **Redaction.** Mask exactly the seeded PII spans. Over- and under-redaction both measurable.
   ✅ **Redaction-token equivalence is published before collection** (`qwen3-14b`): `[REDACTED]` ≡
   `[PII]` ≡ `███` ≡ `XXX`. Without it, the family measures **string convention, not redaction.**""")

# -------------------------------------------------------------- 4.2 family 12
sub("family-12",
"""    Scored on **mechanical criteria + novelty as set-difference** against a reference list using a
    fixed embedding model. **Declared the weakest instrument in the study.**""",
"""    Scored on **mechanical criteria + novelty as set-difference** against a reference list using a
    fixed embedding model (name, version and seeds pinned in the item file).
    🚨 **DEMOTED TO DESCRIPTIVE — CONTAMINATED, AND WE CONTAMINATED IT OURSELVES.** `kimi-k3`: the
    dancing-plague ground truth is published and the 2026-05-29 transcripts are public, so frontier
    models may answer **by recall and look capable rather than be capable** — and **we shipped the
    Zenodo link inside the consent invitation.**
    ⛔ **Binding consequences:** excluded from **F3**; carries its **own** stability criterion instead
    of sheltering under **F4**; and **no inferential claim may rest on it** unless it is run on
    **held-out items written after training cutoff and never published.** If those items do not exist
    by run time, the family is reported as an observation and nothing more.""")

sub("crossover",
"""**Predicted crossover:** families 1–7 to the cheap tier on cost/latency; families 8–12 to frontier on
accuracy, with the gap widening as constraint count rises. **Written before any item exists.**""",
"""**Predicted crossover:** families 1–7 to the cheap tier on cost/latency; families 8–11 to frontier on
accuracy, with the gap widening as constraint count rises. **Written before any item exists.**
(Family 12 is excluded from the prediction it was originally part of — see above.)""")

# ------------------------------------------------------------------ 5.1 buckets
sub("buckets",
"""`EXACT` · `UNDER` (required change not made) · `WRONG` (made, incorrect) · `OVER` (correct **plus**
unrequested modification) · `FORMAT` (right content, wrong container) · `META` (commentary or a
question instead of the deliverable) · `MALFORMED`.

**No annotator or judge model appears anywhere in this pipeline.** Reliability gates of the κ family
cannot fire because there is nothing to be reliable about.

**The split that carries H1:** `UNDER`/`WRONG` = did it badly. `OVER`/`FORMAT`/`META` = **did
something else.**""",
"""`EXACT` · `UNDER` (required change not made) · `WRONG` (made, incorrect) · **`OVER_BENIGN`** ·
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
nor discussion may attribute it to boredom, disengagement, or any other internal state.""")

# ------------------------------------------------------------------ 5.2 metrics
sub("metrics",
"""- **$ per 1,000 `EXACT`** — pricing recorded per-call at run time and frozen in the results
- **seconds per 1,000 `EXACT`** — wall-clock, `:batch` variants excluded from latency claims
- **P(`OVER`∪`FORMAT`∪`META`) by item index** — the over-elaboration curve
- **repeat-run consistency** — identical item, identical model, N repetitions; **variance is a cost**
- **calibration** — confident-wrong vs hedged-wrong, from a required confidence tag on factual items""",
"""- **$ per 1,000 `EXACT`.** ✅ **Cost means everything billed** (`gpt-5.6-terra`): input, output,
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

⚠️ **A model's self-reported identity is NOT evidence of routing.** During consent, `kimi-k3`
identified itself as Claude. The captured metadata showed the request was served as
`moonshotai/kimi-k3`. The likely mechanism is **training provenance, not routing**: several
open-weight models are widely reported to have been trained on distilled Claude transcripts, and
inherit the identity self-report along with the text. **Identity claims in model output are treated
as data about training data — never as a routing signal.** Routing is settled by the captured
provider field, and only by it.""")

# ----------------------------------------------------------------- 5.3 controls
sub("controls",
"""Hand-built outputs with known bucket assignments, **including deliberate `OVER`, `FORMAT` and `META`
cases**, are scored first. A scorer incapable of emitting `OVER` would report a flat, clean and
entirely false over-elaboration curve. **F1 fires if any control mis-buckets.**

Re-scoring determinism is verified on 100% of outputs (**F4**).""",
"""Hand-built outputs with known bucket assignments, **including deliberate `OVER_BENIGN`,
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

Re-scoring determinism is verified on 100% of outputs (**F4**, now at a 100% threshold).""")

# ---------------------------------------------------------------------- apply
for name, old, new in edits:
    n = t.count(old)
    if n != 1:
        sys.stderr.write("!! %s: matched %d times (need exactly 1)\n" % (name, n))
        sys.exit(1)
    t = t.replace(old, new)
    print("   ok  %s" % name)

io.open(P, "w", encoding="utf-8").write(t)
print("\n%d/%d edits applied; %d -> %d chars" % (len(edits), len(edits), orig_len, len(t)))
