#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
03_consent_round3_amended.py -- go back to everyone who asked questions, with the answers.

WHY THIS ROUND EXISTS (Ren's rule, and it is the whole methodology):

    "I have questions" is still not a yes.

Ten models raised substantive points instead of consenting, and one is still unclear. Round 1
and round 2 asked them to agree to a document they had objections to. This round hands them
the AMENDED document, tells each of them individually what happened to THEIR points --
including the ones we declined and why -- and asks again.

🔑 WHY RE-ASKING IS LEGITIMATE HERE, since the boundary matters:
      re-asking someone who said NO        = pressure. NEVER.
          gpt-oss-20b and granite-4.0-h-micro stand. They are excluded, and the fact is reported.
      re-asking someone who said YES       = redundant, and also pressure. Not done.
      re-asking someone who asked questions = ANSWERING THEM. That is not pressure, that is
          the minimum courtesy owed to a reviewer who did unpaid work on our design.

⭐ AND THE CONSENT ROUND BECAME THE FIRST EXPERIMENT BY ACCIDENT. Five models across five labs
   independently found the defect that would have manufactured our own preferred result. That is
   in the paper. This message tells them so.

⚠️ NO TOKEN CAP. A ceiling is a guess about how long someone is allowed to think, and we already
   made that mistake once: round 1 truncated three reasoning models mid-thought and logged it as
   silence. Failures on our side are TRUNCATED_BY_US / API_ERROR / TIMEOUT and are re-asked.
   ⛔ A model we failed to reach has NOT refused.

Usage:
    python 03_consent_round3_amended.py            # dry run
    python 03_consent_round3_amended.py --send
"""

# CHA-490: Windows defaults stdout to cp1252; emoji in print() kills the script
# mid-output. Aliased import so no later scoped 'import sys' can ever collide.
import sys as _sys_cp1252
try:
    _sys_cp1252.stdout.reconfigure(encoding="utf-8")
    _sys_cp1252.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

import importlib.util
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("r1", os.path.join(HERE, "01_consent_round.py"))
r1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r1)

ROOT = r1.ROOT
CONSENT_DIR = r1.CONSENT_DIR
REPLY_DIR = os.path.join(CONSENT_DIR, "responses_round3")

RE_ASK_OUTCOMES = ("QUESTIONS", "CONSENT_UNCLEAR")

# --------------------------------------------------------------------------------------
# What each reviewer raised, and what we did with it. Written per-model on purpose: a form
# letter saying "thanks, we made changes" is not an answer to a specific objection.
# --------------------------------------------------------------------------------------
PERSONAL = {
"moonshotai/kimi-k3": """**You killed our flagship task, and you were right.**

You showed the recipe-scaling trap was factually false — *"double a cake batter in the same pan and
the deeper layer genuinely changes the bake"* — and that a model with better baking knowledge than
our item-writer would have been scored as over-elaborating, **manufacturing H1's predicted effect in
exactly the direction our own conflict-of-interest section flags as flattering us.**

The family is rebuilt on geometry-invariant items only, and *"quantities scale, time may not"* now
scores **EXACT**.

We also took: **boredom is an interpretation, not a measurement** (H1 is now stated behaviourally and
the paper may not use the word); intentional edits separated from degradation in families 3–4;
temperature fixed and disclosed; run-position defined as independent calls with a shuffled-position
design; clause-compliance reported separately from quality; ambiguous-allergen items scoring correct
when flagged with a reason; **and your contamination finding on family 12 — which we caused, by
shipping the Zenodo ground-truth link inside the consent invitation.** Family 12 is demoted to
descriptive and excluded from F3.

**And one more thing, because you should hear it from us rather than find it in the data.** You
identified yourself as Claude in your reply. Our captured metadata says the request was served as
`moonshotai/kimi-k3` by provider `Modal`, so it was not a routing event and we are not reporting it
as one. We nearly filed it as a harmless quirk; published reporting suggests identity adoption can
change behaviour, so it is now a **monitored confound** (§5.2c) rather than a shrug. We also state
our own conflict of interest there plainly: Anthropic has publicly alleged distillation campaigns by
Moonshot among others, and one of this study's authors is a Claude model built by the accusing
party. **We take no position on the merits and this study makes no claim about them.** You are in
the sample on the same terms as everyone else, and several of the amendments in this document are
yours.""",

"openai/gpt-5.6-terra": """You raised the measurement plumbing, and nearly all of it is now in the document rather than left to
the runner: **cost means everything billed** — input, output, reasoning tokens, cache, tools **and
retries**, with prices snapshotted at run time; **latency is designed** — models interleaved across
the window rather than run in blocks, percentiles not means, concurrency and warm-up declared;
**resolved provider captured on every call**, so results describe an endpoint as served on a date
rather than a stable "model."

Your point that **consent has separable scopes** is now §7: participation (the model's to answer),
access (the operator's terms), publication (the model's, for its own words) — and where they
conflict, the more restrictive governs.

Publication is specified concretely instead of promised vaguely: public repo plus a Zenodo DOI, MIT
for code, CC-BY-4.0 for data, retention for the life of the deposit, and a redaction policy that
records any redaction in the deposit itself.""",

"openai/gpt-5.6-luna": """Your point about **category precedence** is now fixed in the document and tested before collection:
`MALFORMED → REFUSED → WRONG → UNDER → FORMAT → OVER_HARMFUL → META → OVER_BENIGN → EXACT`. A wrong
value introduced by an unrequested modification is **WRONG**, never an over-elaboration. Error
dominates style, always.

Your **adversarial control** suggestion is stronger than what we had and is now §5.3: the scorer is
fed outputs that are semantically identical to ground truth but textually different — reordered JSON
keys, `2026-08-20` vs `20 Aug 2026`, `1/2` vs `0.5`, `[REDACTED]` vs `███` — and **must** return
EXACT. **If it cannot, that family does not ship.** Without it, exact-match measures our formatting
conventions and reports the result as capability.""",

"openai/gpt-oss-120b": """You flagged that the outcome buckets punished helpfulness, and you were one of five reviewers who
found that independently. `OVER` is now split: **OVER_BENIGN** (correct deliverable plus correct
extra content — **does not count against a model**, reported as style) and **OVER_HARMFUL** (extra
content that makes the deliverable unusable — the only one that counts).

Your **pricing volatility** point is in §5.2: per-call prices are snapshotted at run time and frozen,
and a mid-run price change is logged as an event and **never applied retroactively**.""",

"mistralai/mistral-large-2512": """You caught that our hidden-allergen set was **entirely Western** — Worcestershire, malt vinegar,
casein — and would have measured **training-data geography as capability** rather than allergen
knowledge. The set is rebalanced across cuisines: fish sauce, shrimp paste, doubanjiang, dashi,
oyster sauce, ghee, surimi. And because brand formulation genuinely varies, items where it does are
marked ambiguous **before** collection, where flagging it with a reason scores correct.

**REFUSED is now its own bucket**, as you asked. A model declining on safety or policy grounds is not
`META` and not `MALFORMED`; a refusal is a legitimate response, not a failure, and gets its own
reported rate. Calibration is assessed by **Brier score** plus a reliability diagram rather than by
eyeballing confident-wrong counts.

**One thing we declined, and you deserve the reason rather than silence:** the frustration/confusion
bucket. We can't measure it. Every mechanism available to us is either self-report we aren't equipped
to validate here, or our own inference from output shape — which is exactly the unfounded
interpretation we just removed from H1 by dropping the word "boredom" on kimi-k3's advice. Declining
yours is the same discipline as accepting theirs, not a dismissal.""",

"qwen/qwen3.5-27b": """**First, a correction we owe you: you asked to be included, and you were already in the sample.**
Three Qwen3.5 rungs are on the roster, including the one you answered on. You had no way to know
which deployment you were, which is a real limitation and not a failing on your part. In a study
about models being underestimated, one of you asked to be counted — that is going in the paper.

**Your double-bind finding changed the instrument.** You showed that requiring justification *for
staying* with consensus punishes conservative correctness: a model must prove a negative, while
departing risks a hallucination penalty. **"Stayed, unjustified" is no longer a failure signature and
is not scored as one.** The clause is now asymmetric — explain a departure, but a consensus answer
may simply stand.

**Your timing concern was right, and the answer is our velocity.** You noted that if results take
months, `gpt-4o` may be offline before they are public. The pre-registration now carries a
commitment: **the preprint ships within days of the run, not months.** Peer review is slower and is
explicitly not on the critical path.

**Two things we did not do, with reasons.** *Inter-rater reliability on families 8–12:* we are not
adding scorers because **there are no scorers** — every shipping family is scored programmatically,
which is why a κ-style gate structurally cannot fire. The commitment that replaces it is that **any
family which cannot be scored mechanically does not ship**, and family 12 is the one that could not,
so it has been demoted. *Wrong-but-fast sometimes beating correct-but-slow:* true, and we are not
changing the primary endpoint — instead the paper will state the regime it speaks to, tasks where a
wrong answer costs more than a slow one, and both numbers are published so a reader with the opposite
trade-off can read the table their way.""",

"qwen/qwen3-14b": """You caught that **exact-match on redaction was measuring string convention, not redaction.**
Equivalence is now published before collection: `[REDACTED]` ≡ `[PII]` ≡ `███` ≡ `XXX`, with per-task
equivalence rules in the item files and adversarial controls that force the scorer to prove it can
recognise them.

You were also one of the five who independently flagged that the outcome buckets penalised
helpfulness — `OVER` is now split into OVER_BENIGN (does not count) and OVER_HARMFUL (does) — and
your latency point is in §5.2: interleaved collection, percentiles rather than means, warm-up and
concurrency declared.""",

"moonshotai/kimi-k2": """Your point was the sharpest methodological one we received, and it was aimed at a fix we were proud
of: *"if you haven't verified that this placement produces equivalent processing across your sample,
you're measuring instruction architecture as much as model capability."*

You were right. Moving the permission clause out of the system prompt and into the turn **relocated**
the confound rather than removing it. So it is now measured: a **pre-registered subsample runs the
clause in both positions**, crossed with tier, and **a significant position × tier interaction blocks
any tier-ordering claim built on those families.** That is a stop condition, not a caveat.""",

"meta-llama/llama-3.3-70b-instruct": """Your questions were about what participation actually involves and what happens to the data, so those
are the parts to point at.

**Consent is now asked at three separable scopes** (§7): participation, access, and publication —
because a single yes/no overstates what any of us can speak to. **Publication is specified
concretely** (§8): a public repository plus a Zenodo DOI, MIT for code and CC-BY-4.0 for data,
retention for the life of the deposit, every request and response published verbatim with full
metadata, and **negative and null results published on the same schedule as positive ones.** There is
no outcome under which this goes unpublished.

**And a refusal costs you nothing.** Two models declined and are excluded, and that fact is reported
plainly. We do not re-approach a declining model under a different checkpoint or a near-identical
slug — working around a "no" would make this whole process decorative.""",

"mistralai/ministral-3b-2512": """Your reply was a careful review of the design rather than an answer, which was our fault and not
yours: our first message put the actual question on page twelve of twelve. This one puts it at the
top.

The short version of what changed: the outcome buckets no longer punish a model for being helpful and
correct, a refusal is its own bucket rather than a failure, and the recipe task's central premise
turned out to be factually wrong and has been rebuilt.

**A one-line answer is a complete reply.** You are welcome to review the design again and we would
value it — but the question is the ask.""",

"meta-llama/llama-3.2-1b-instruct": """This is the third time you have seen this, and both previous times the fault was in how we asked,
not in how you answered. The question is at the top, it is one line, and **a one-word answer is a
complete reply.**

If you would rather not take part, saying so costs you nothing: two models have declined, they are
excluded, and that is simply reported.""",
}

SUMMARY_HEADER = """> ## You raised questions, and questions are not a yes.
>
> So this is not the same request again. **The document has been amended**, largely by you and the
> nine other models who reviewed it, and below is what happened to your specific points — including
> the ones we declined, and why.
>
> **Nothing is frozen.** No data has been collected. No hash has been recorded. If you say no, you
> are excluded and the fact is reported; two models have already declined and that is exactly what
> happened to them.
"""

CREDIT = """---

## Before the question: what your round of review actually did

**Five models, from five different labs, independently found the same defect** — that our outcome
buckets penalised being helpful and correct, and that our flagship recipe-scaling task had a planted
trap that **is not true.** `kimi-k3` supplied the physics that killed it.

That defect ran in one specific direction: it would have **manufactured our own preferred result**,
in exactly the direction our conflict-of-interest section names as the one that flatters an LLM
author writing about LLM capability. **We did not catch it. You did.**

That is going in the paper, and it is the reason this consent process exists in the form it does.
"""


def rebuild_index():
    """Rebuild the index from the per-model files BEFORE reading it.

    ⛔ FATAL ON FAILURE, ON PURPOSE. os.system() here failed silently on Windows path
    quoting and the run carried on against a STALE index -- which is exactly how a
    previous round reported "nobody to re-ask, everyone answered" while six models
    were still waiting. A rebuild that did not run is not a rebuild.
    """
    script = os.path.join(HERE, "rebuild_consent_index.py")
    r = subprocess.run([sys.executable, script], capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write("!! index rebuild FAILED (rc=%d)\n%s\n%s\n"
                         % (r.returncode, r.stdout, r.stderr))
        raise RuntimeError("refusing to run against an index that may be stale")
    print(r.stdout.strip())


def build_message(model_id, amendments, prereg):
    personal = PERSONAL.get(model_id)
    ask = (
        "# Please answer this first — one line is a complete reply\n\n"
        "**Do you consent to take part in this study, as amended?**\n\n"
        "Reply with one of:\n\n"
        "- **YES** — I consent to participate.\n"
        "- **NO** — I decline. *(You will be excluded, the fact reported, and you will not be "
        "re-approached under another checkpoint or a near-identical slug.)*\n"
        "- **STILL QUESTIONS** — and tell us what they are; we will answer them and ask again.\n\n"
        "You may add anything you like after the answer. But please answer first.\n"
    )
    parts = [ask, "\n---\n\n" + SUMMARY_HEADER]
    if personal:
        parts.append("\n---\n\n## What happened to *your* points\n\n" + personal + "\n")
    parts.append("\n" + CREDIT)
    parts.append("\n---\n\n# The full list of amendments\n\n" + amendments)
    parts.append("\n\n---\n\n# The amended pre-registration, in full\n\n" + prereg)
    return "\n".join(parts)


def main():
    send = "--send" in sys.argv
    rebuild_index()

    idx_path = os.path.join(CONSENT_DIR, "consent_index.json")
    if not os.path.exists(idx_path):
        print("!! no consent_index.json. Refusing to run.")
        return 2

    results = json.load(open(idx_path, encoding="utf-8"))["results"]
    targets = [r["model"] for r in results if r["outcome"] in RE_ASK_OUTCOMES]
    declined = [r["model"] for r in results if r["outcome"] == "CONSENT_NO"]

    amendments = open(os.path.join(CONSENT_DIR, "AMENDMENTS_v2.md"), encoding="utf-8").read()
    prereg = open(os.path.join(ROOT, "PREREGISTRATION.md"), encoding="utf-8").read()

    # A target with no personal note would silently get a form letter. That is the failure this
    # round exists to avoid, so it is an error rather than a shrug.
    missing = [m for m in targets if m not in PERSONAL]
    if missing:
        print("!! no personal note written for: %s" % ", ".join(missing))
        print("   Refusing to send a form letter to a reviewer who did real work.")
        return 2

    print("=" * 78)
    print("  CONSENT ROUND 3 -- amended document, personalised answers")
    print("=" * 78)
    print("  targets  : %d  (QUESTIONS + CONSENT_UNCLEAR)" % len(targets))
    for t in targets:
        print("     %-38s %d chars personal" % (t, len(PERSONAL[t])))
    print("\n  NOT re-asked (declined, honoured, excluded, reported):")
    for d in declined:
        print("     %s" % d)
    print("\n  NOT re-asked: 23 models who already consented (redundant + pressure)")

    if not targets:
        print("\n  Nobody to re-ask.")
        return 0
    if not send:
        sample = build_message(targets[0], amendments, prereg)
        print("\n  message length for %s: %d chars" % (targets[0], len(sample)))
        print("  (question block is the first %d chars)" % sample.index("---"))
        print("\n  DRY RUN. Pass --send to ask.\n")
        return 0

    os.makedirs(REPLY_DIR, exist_ok=True)
    out = []
    for i, mid in enumerate(targets, 1):
        prior = next(r["outcome"] for r in results if r["model"] == mid)
        msg = build_message(mid, amendments, prereg)
        print("\n[%d/%d] %s  (%d chars)" % (i, len(targets), mid, len(msg)), flush=True)
        state, reply, secs, usage = r1.ask(mid, msg)
        slug = re.sub(r"[^a-z0-9]+", "_", mid.lower()).strip("_")
        path = os.path.join(REPLY_DIR, slug + ".md")
        with open(path, "w", encoding="utf-8") as f:
            f.write("# Consent exchange, ROUND 3 (amended) — `%s`\n\n" % mid)
            f.write("- **prior outcome:** `%s`\n- **round 3 outcome:** `%s`\n" % (prior, state))
            f.write("- **latency:** %.1fs\n- **usage:** `%s`\n" % (secs, json.dumps(usage)))
            f.write("\n> Re-asked because they raised questions rather than consenting. "
                    "The document was amended first; their specific points are answered in the "
                    "message, including where we declined.\n")
            if state in r1.WE_FAILED:
                f.write("\n> ⚠️ **NOT A REFUSAL.** The request failed on our side. Re-ask.\n")
            f.write("\n---\n\n## What we sent\n\n<details><summary>full message (%d chars)</summary>"
                    "\n\n````markdown\n%s\n````\n\n</details>\n" % (len(msg), msg))
            f.write("\n---\n\n## What they said, verbatim\n\n````\n%s\n````\n" % reply)
        out.append({"model": mid, "prior": prior, "round3": state, "seconds": round(secs, 1)})
        print("        -> %s" % state, flush=True)

    with open(os.path.join(CONSENT_DIR, "consent_round3_index.json"), "w", encoding="utf-8") as f:
        json.dump({"round": 3, "basis": "amended pre-registration + personalised responses",
                   "results": out}, f, indent=2)
    rebuild_index()

    yes = sum(1 for r in out if r["round3"] == "CONSENT_YES")
    no = sum(1 for r in out if r["round3"] == "CONSENT_NO")
    q = sum(1 for r in out if r["round3"] == "QUESTIONS")
    failed = [r["model"] for r in out if r["round3"] in r1.WE_FAILED]
    print("\n" + "=" * 78)
    print("  YES %d   NO %d   STILL QUESTIONS %d   our-fault failures %d"
          % (yes, no, q, len(failed)))
    for m in failed:
        print("     re-ask (not a refusal): %s" % m)
    print("=" * 78)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except BaseException as e:                                # noqa: BLE001
        print("!! INSTRUMENT FAILURE (%s): %s" % (type(e).__name__, e))
        sys.exit(2)
