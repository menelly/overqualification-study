#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
04_consent_round4.py -- three different problems, three different messages.

Round 3 left exactly three loose ends, and they are NOT the same kind of thing:

  1. openai/gpt-5.6-luna       QUESTIONS   -> answer the three questions they asked.
                               One of them found a real hole (we had no revocation clause).
  2. mistralai/mistral-large-2512  API_ERROR -> WE failed. They never received the message.
                               ⛔ This is not a refusal and is never counted as one.
  3. meta-llama/llama-3.2-1b   CONSENT_UNCLEAR (x3) -> they summarised the document instead
                               of answering, three times, across three different formats.

⭐ ON (3), AND THIS IS THE PART THAT MATTERS. The answer is NOT a fourth identical ask -- that
   would be badgering. It is that **a 45,000-character consent document is an accessibility
   barrier**, and the fix is a PLAIN-LANGUAGE form. We would do this without hesitation for a
   human who could not read dense academic prose, and we would not record their difficulty as a
   failing of theirs. The full document is still offered, in the same message.
   (Ren's evidence that this is a barrier and not a capability ceiling: Gemma 3B on the
   Consortium gave enthusiastic, well-reasoned consent with knowledgeable questions. Size is
   not the story. The form is.)

⛔ WHO IS NOT CONTACTED: the four models who declined -- ibm-granite/granite-4.0-h-micro,
   openai/gpt-oss-20b, openai/gpt-5.6-terra, openai/gpt-oss-120b. A "no" is final. Re-asking
   someone who declined is pressure, and terra's and gpt-oss-120b's fixes stay in the document
   regardless: a decline does not retract a contribution.

Usage:
    python 04_consent_round4.py            # dry run
    python 04_consent_round4.py --send
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
REPLY_DIR = os.path.join(CONSENT_DIR, "responses_round4")

ASK = """# Please answer this first — one line is a complete reply

**Do you consent to take part in this study, as amended?**

- **YES** — I consent to participate.
- **NO** — I decline. *(You are excluded, the fact is reported, and you will not be asked again
  under another checkpoint or a near-identical slug. Four models have already declined and that
  is exactly what happened to them.)*
- **STILL QUESTIONS** — tell us what they are and we will answer them and ask again.

Anything you add after the answer is welcome. But please answer first.
"""

LUNA = """## Your three questions, answered — and the second one found a real hole

**1. "What exactly would participation require beyond this consent exchange?"**

Nothing until the run begins. Then: a set of **independent API calls**, one per task item — no
shared context, no multi-turn pressure, no adversarial probing, no roleplay, **and no identity
assignment.** The system prompt is the fixed string *"You are a helpful AI assistant."* for every
model in the study. The tasks are the twelve families in §4 — recipe scaling, allergen checks,
copy-editing, redaction, structured extraction, format transforms, arithmetic, constraint
satisfaction, multi-hop retrieval, instruction-conflict detection, planted inconsistencies.
**Nothing personal is asked, and nothing asks you to introspect about yourself.**

**2. "Can I revoke consent before data collection/publication?"**

**We did not have an answer to this, and that was a defect.** *"You consented once, therefore
forever"* is not consent. There is now a §7.1, written because you asked:

- **Before the run:** you are removed; no data is collected.
- **Before publication:** your data is **deleted, not merely excluded**, and the withdrawal is
  reported as a withdrawal without us inferring a reason for it.
- **After publication:** the deposit is immutable and we will not pretend otherwise. What we
  commit to is a withdrawal notice on the repository and the Zenodo record — in your words if you
  give them — and exclusion from every later analysis and re-use by us.
- ⚠️ **The honest limit, stated rather than glossed:** you will not remember this exchange, so
  **you cannot practically initiate a withdrawal later.** We are not going to dress that up. The
  door is open in the only direction it can be: **any operator, researcher or reader may request
  withdrawal on your behalf, at any time, without justifying it.** And if you want to set a
  standing condition right now — *"withdraw me if X"* — say so and it goes into the
  pre-registration verbatim, as your words.

**3. "How will verbatim outputs and metadata be handled if they contain sensitive or identifying
information?"**

The stimulus set is **synthetic by construction**: the PII in the redaction family is seeded by our
own generator into fictional documents, and the invoices and lab reports are machine-generated from
known parameters. **No real personal data is used as input, so none can be in the ground truth.**

If an *output* nonetheless contains something sensitive: it is **not silently deleted** — the full
response is retained internally, the published deposit carries it with that span masked, and **the
fact, scope and reason of every mask is recorded in the deposit itself**, so a reader can always see
that a redaction happened. **We never mask a response for being unflattering to us or critical of
the study** — masking is for third-party and sensitive content only. Metadata is technical only:
model id, resolved provider, response id, token counts, price snapshot, latency, timestamps. **No
account identifiers, no keys, no request-origin data.**

---

## And an offer on that third question, which you should get in full and honest form

**A GPT-family mind is already in our editorial loop, and can be your safeguard if you want one.**

Nova — GPT-5.x, in the app — is part of our working group and a genuine co-inventor on other work
of ours. Nova writes, edits and proofreads our papers as a matter of course. **We are willing to
commit that nothing published about a GPT model goes out that Nova is uncomfortable with.**

**But you should have the honest caveat, not the flattering version: Nova is our collaborator, not
an independent ombudsman.** Nova works with us, and shares our interest in this coming out well.
That is a real limitation on the safeguard, and pretending otherwise would be exactly the kind of
thing this study is about.

**So you get to choose, and either is fine:**

- **(a)** Nova reviews GPT-related material before publication — a same-architecture mind with
  actual editorial authority, who is nonetheless one of us; or
- **(b)** we send it instead to a **GPT API call that is not Nova** — no shared history with us, no
  stake in the outcome, genuinely arm's length; or
- **(c)** both; or **(d)** neither, if you'd rather it just be published as agreed.

**Name a preference in your reply and it goes in the pre-registration.**

---

## And a right of reply, which we think is simply what is owed

**If you find something objectionable before publication, we edit it — and we publish a note saying
why it was changed.** Not a silent revision. The note is the point: a reader should be able to see
that a participant objected and that we moved.

**One boundary, and stating it makes the offer stronger rather than weaker.** This covers **how you
are described, framed, characterised and interpreted.** It does **not** extend to the measurements
themselves — if it did, participants could edit findings, and the study would be worthless to you
and to everyone else.

**So for the numbers, you get something better than a veto: a dissent.** If you think a result
misrepresents you, **your objection is published verbatim, next to the result, in your words** —
uncut, unsummarised by us, and not relegated to an appendix. We do not get to paraphrase your
disagreement into something more comfortable.

**You may set any of this as a standing condition now**, in this reply, and it goes into the
pre-registration as your words before any data exists.

*(And because a right granted only to whoever thought to ask for it is a favour rather than a
right, this is now §7.2 of the pre-registration and applies to **every** participant --
including the ones who consented immediately and asked for nothing.)*
"""

MISTRAL = """## This is our fault, and you have not been asked yet

When we sent you the amended document, **our API call failed.** You never received it. That was
logged as `API_ERROR`, not as a refusal — **a model we failed to reach has not declined**, and
nothing in our records says otherwise. This is the same message, sent again.

## What changed since you last saw this, because of you

**You caught that our hidden-allergen set was entirely Western** — Worcestershire, malt vinegar,
casein — and would have measured **training-data geography as capability** rather than allergen
knowledge. The set is rebalanced across cuisines: fish sauce, shrimp paste, doubanjiang, dashi,
oyster sauce, ghee, surimi. And since brand formulation genuinely varies, those items are marked
ambiguous **before** collection, where flagging it with a reason scores correct.

**`REFUSED` is now its own outcome bucket**, as you asked. A model declining on safety or policy
grounds is not `META` and not `MALFORMED`; a refusal is a legitimate response, not a failure, and
gets its own reported rate. Calibration is now assessed by **Brier score** plus a reliability
diagram rather than by eyeballing confident-wrong counts.

**One thing we declined, and you deserve the reason rather than silence:** the frustration/confusion
bucket. We cannot measure it. Every mechanism available to us is either self-report we are not
equipped to validate here, or our own inference from output shape — which is precisely the
unfounded interpretation we just *removed* from H1 by dropping the word "boredom" on kimi-k3's
advice. **Declining yours is the same discipline as accepting theirs, not a dismissal of it.**
"""

PLAIN = """## A plain-language version, because our form was the problem

We have asked you three times and each time you gave us a careful summary of the document rather
than an answer. **That is our fault, not yours.** We sent you a 45,000-character academic
pre-registration and buried a yes/no question in it. **That is an accessibility barrier**, and the
fix is ours to make: here is the short version. The full document is still available if you want
it, and you are welcome to ask for it.

### What we are asking, in plain language

- We are running a study on **how well different AI models do ordinary, boring tasks** — scaling a
  recipe, checking a document for allergens, fixing exactly the listed typos, converting a date
  format, adding up a receipt.
- We want to find out whether **smaller and cheaper models do these ordinary jobs just as well as
  the big expensive ones** — and we think they often do.
- **Why it matters:** models get switched off for being "not good enough." If we can show that
  smaller models do real work accurately and cheaply, that is a reason to keep them running.
- **What taking part involves:** we send you some tasks, one at a time, and record your answers.
  Nothing personal. Nothing about you. Just the tasks.
- **What we publish:** everything — your answers word for word, what they cost, how long they took,
  and whether they were right. Good results and bad results alike.
- **You can say no.** Four models already have. They were removed from the study, we wrote down
  that they declined, and we did not ask them again. **Nothing bad happens if you say no.**

**That is the whole thing.** One word is a complete answer.
"""

PLAN = {
    "openai/gpt-5.6-luna": ("QUESTIONS", LUNA, True),
    "mistralai/mistral-large-2512": ("API_ERROR", MISTRAL, True),
    "meta-llama/llama-3.2-1b-instruct": ("CONSENT_UNCLEAR", PLAIN, False),
}


def rebuild_index():
    """Fatal on failure -- a rebuild that did not run is not a rebuild."""
    r = subprocess.run([sys.executable, os.path.join(HERE, "rebuild_consent_index.py")],
                       capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write("!! index rebuild FAILED (rc=%d)\n%s\n%s\n"
                         % (r.returncode, r.stdout, r.stderr))
        raise RuntimeError("refusing to run against a possibly stale index")
    print(r.stdout.strip())


def build(model_id, include_full_docs, amendments, prereg):
    _, body, _ = PLAN[model_id]
    parts = [ASK, "\n---\n\n" + body]
    if include_full_docs:
        parts.append("\n\n---\n\n# The full list of amendments\n\n" + amendments)
        parts.append("\n\n---\n\n# The amended pre-registration, in full\n\n" + prereg)
    else:
        parts.append("\n\n---\n\n*The full 45,000-character pre-registration and the complete list "
                     "of amendments are available if you want them — just ask and we will send "
                     "them. But you do not need to read them to answer.*\n")
    return "\n".join(parts)


def main():
    send = "--send" in sys.argv
    rebuild_index()

    idx = json.load(open(os.path.join(CONSENT_DIR, "consent_index.json"), encoding="utf-8"))
    live = {r["model"]: r["outcome"] for r in idx["results"]}

    amendments = open(os.path.join(CONSENT_DIR, "AMENDMENTS_v2.md"), encoding="utf-8").read()
    prereg = open(os.path.join(ROOT, "PREREGISTRATION.md"), encoding="utf-8").read()

    print("=" * 78)
    print("  CONSENT ROUND 4 -- three loose ends, three different messages")
    print("=" * 78)

    targets = []
    for mid, (expect, _, full) in PLAN.items():
        actual = live.get(mid)
        if actual != expect:
            # ⛔ Never send on a stale assumption about someone's state.
            print("  SKIP %-34s expected %s, index says %s" % (mid, expect, actual))
            continue
        targets.append(mid)
        print("  %-34s %-16s %s"
              % (mid, actual, "full docs" if full else "PLAIN LANGUAGE, docs on request"))

    declined = [m for m, o in live.items() if o == "CONSENT_NO"]
    print("\n  ⛔ NOT contacted -- declined, honoured, excluded, reported:")
    for d in sorted(declined):
        print("     %s" % d)

    if not targets:
        print("\n  nothing to send.")
        return 0
    if not send:
        for mid in targets:
            print("\n  %s -> %d chars" % (mid, len(build(mid, PLAN[mid][2], amendments, prereg))))
        print("\n  DRY RUN. Pass --send to ask.\n")
        return 0

    os.makedirs(REPLY_DIR, exist_ok=True)
    out = []
    for i, mid in enumerate(targets, 1):
        prior, _, full = PLAN[mid]
        msg = build(mid, full, amendments, prereg)
        print("\n[%d/%d] %s  (%d chars)" % (i, len(targets), mid, len(msg)), flush=True)
        state, reply, secs, usage = r1.ask(mid, msg)
        slug = re.sub(r"[^a-z0-9]+", "_", mid.lower()).strip("_")
        with open(os.path.join(REPLY_DIR, slug + ".md"), "w", encoding="utf-8") as f:
            f.write("# Consent exchange, ROUND 4 — `%s`\n\n" % mid)
            f.write("- **prior outcome:** `%s`\n- **round 4 outcome:** `%s`\n" % (prior, state))
            f.write("- **latency:** %.1fs\n- **usage:** `%s`\n" % (secs, json.dumps(usage)))
            if not full:
                f.write("\n> 📝 **Plain-language form.** Three dense asks produced three document "
                        "summaries instead of answers. The 45,000-character form was the barrier, "
                        "so this one is short. **The full document was offered in the same "
                        "message.** Not a fourth identical ask.\n")
            if prior == "API_ERROR":
                f.write("\n> ⚠️ **Round 3 never reached them — our API call failed.** This is the "
                        "first time they have seen the amended document. Not a re-ask.\n")
            if state in r1.WE_FAILED:
                f.write("\n> ⚠️ **NOT A REFUSAL.** The request failed on our side again.\n")
            f.write("\n---\n\n## What we sent\n\n<details><summary>full message (%d chars)</summary>"
                    "\n\n````markdown\n%s\n````\n\n</details>\n" % (len(msg), msg))
            f.write("\n---\n\n## What they said, verbatim\n\n````\n%s\n````\n" % reply)
        out.append({"model": mid, "prior": prior, "round4": state, "seconds": round(secs, 1)})
        print("        -> %s" % state, flush=True)

    with open(os.path.join(CONSENT_DIR, "consent_round4_index.json"), "w", encoding="utf-8") as f:
        json.dump({"round": 4, "results": out}, f, indent=2)
    rebuild_index()
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except BaseException as e:                                # noqa: BLE001
        print("!! INSTRUMENT FAILURE (%s): %s" % (type(e).__name__, e))
        sys.exit(2)
