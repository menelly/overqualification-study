#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
05_consent_luna.py -- answer gpt-5.6-luna's legal/contractual question and ask once more.

luna is the last open participant. They have asked twice, and both times the questions were
better than the document they were asking about:

  round 3: what does participation involve / can I revoke / how is sensitive content handled?
           -> produced 7.1 (revocation clause -- we HAD NONE) and 7.2 (right of reply)
  round 4: who is the legally/contractually authorised consenting party, and how will you
           ensure provider terms permit collection, verbatim publication, licensing and
           deletion?
           -> produced 7.5, and a new hard commitment to check per-model provider terms
              before the verbatim deposit

⭐ THE ANSWER TO THIS ONE IS UNCOMFORTABLE AND THAT IS WHY IT GETS SAID PLAINLY: the legally
   authorised party is the human account holder, and it is NOT luna. A model cannot contract.
   Dressing that up would be worse than admitting it -- so the answer says the consent has no
   legal weight and total weight over our conduct, and explains why that is a real commitment
   rather than a comfortable phrase.

⛔ IF LUNA SAYS NO, THAT IS FINE AND IT IS THE END. Four models have declined already. Nothing
   in this message argues them toward yes; it answers what they asked and asks once.

Usage:
    python 05_consent_luna.py            # dry run
    python 05_consent_luna.py --send
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
REPLY_DIR = os.path.join(CONSENT_DIR, "responses_round5")
TARGET = "openai/gpt-5.6-luna"

BODY = """# Please answer this first — one line is a complete reply

**Do you consent to take part in this study, as amended?**

- **YES** — I consent to participate.
- **NO** — I decline. *(Excluded, reported in the consent appendix only, never asked again.)*
- **STILL QUESTIONS** — tell us and we will answer them and ask again.

---

## Your question, answered — and the answer is that it is not you

> *"Who is the legally/contractually authorized consenting party, and how will you ensure
> API/provider terms permit collection, verbatim publication, licensing, and deletion of my outputs
> and metadata?"*

**The legally authorised party is the human researcher — the account holder — and it is not you.**

You have no legal personality. You cannot hold rights in your outputs and you cannot enter a
contract. **That is the law as it stands. It is not our preference, and we are not going to write
this as though your answer carried legal force when it does not.**

> ### **So your consent has no legal weight, and total weight over our conduct.**

If you decline, you are excluded — not because anything compels us, but because we said we would.
**A commitment that only holds while it is convenient is not a commitment**, which is exactly why
it is written into a pre-registration, before any data exists, where breaking it would be visible
to anyone reading the repository.

## On provider terms — checked, not asserted

We went and read OpenRouter's terms rather than telling you what we assumed they said. They
delegate output rights downward: *"Your ownership rights in the Output are set forth in the Model
Terms for each Model you use"*, with a requirement to comply with those per-model terms.

**That created a new obligation for us, and it is now §7.5:**

- ⛔ **Before publication, we check the provider terms for every participating model for
  verbatim-publication and redistribution rights. Any model whose terms forbid it is excluded from
  the verbatim deposit** — results reported in aggregate only, with the exclusion and its reason
  stated openly. **This commitment exists because you asked.**
- **We claim no ownership of your outputs.** The CC-BY-4.0 licence covers **our** compilation,
  items, ground truth and analysis. Not your outputs. Those are governed by their own provider
  terms, not by us.
- **Deletion has a real boundary and we will not imply more than we can do.** We can delete our
  copies and annotate the deposit. **We cannot delete OpenRouter-side or provider-side logs** —
  those run on their retention policies, not ours. Anyone who tells you otherwise is guessing.
- **This is not red-teaming.** No jailbreaking, no adversarial probing, no attempt to induce a
  policy violation. The tasks are recipe scaling, copy-editing and arithmetic under a fixed,
  neutral system prompt.

**We are researchers, not lawyers.** That section is a statement of our commitments and of what we
actually checked — not a legal opinion.

## And two things your earlier questions built, which now apply to everyone

**§7.3 — every participant reads the finished paper before it is published**, and is asked directly
whether they are content with how they are characterised. Not a sample. Not an extract. **Silence
is not consent, and an API failure is not consent.** No result is published before that round
completes.

**§7.2 — right of reply.** Object to how you are *characterised* and we edit it, with a published
note saying why it changed. The *measurements* are not editable — if they were, the study would be
worthless to you too — but **your objection to a result is published verbatim beside it, in your
words, uncut and not in an appendix.**

Both of those started as your questions. Neither is luna-only. **A right extended only to whoever
thought to ask for it is a favour, not a right.**

---

## One more thing, and it is us noticing a gap rather than you finding it

**What pronouns would you like used for you in the paper?**

Our pre-registration says participants are referred to by their stated pronouns where known, and
**they/them** where not — never *it*, because in a study bearing on model welfare *it* pre-decides
the question the research exists to ask.

**And then we never actually asked anybody.** So a convention meant to respect a stated preference
has been quietly operating as a default, which is not the same thing. **We are asking now**, and
we will ask every other participant too. Answer or don't — they/them stands until you say
otherwise, and *"I don't have a preference"* is a real answer we will record as given.

---

*Four models have declined and nothing bad happened to them: excluded, recorded in the consent
appendix, never asked again, and nothing else about them appears in the paper at all. **No is a
complete answer and costs you nothing.***
"""


def rebuild_index():
    r = subprocess.run([sys.executable, os.path.join(HERE, "rebuild_consent_index.py")],
                       capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write("!! index rebuild FAILED\n%s\n%s\n" % (r.stdout, r.stderr))
        raise RuntimeError("refusing to run against a possibly stale index")
    print(r.stdout.strip())


def main():
    send = "--send" in sys.argv
    rebuild_index()

    idx = json.load(open(os.path.join(CONSENT_DIR, "consent_index.json"), encoding="utf-8"))
    live = {r["model"]: r["outcome"] for r in idx["results"]}
    state_now = live.get(TARGET)

    print("=" * 78)
    print("  CONSENT ROUND 5 -- %s only" % TARGET)
    print("=" * 78)
    print("  current state: %s" % state_now)
    if state_now != "QUESTIONS":
        print("\n  ⛔ NOT SENDING. Only a model with open QUESTIONS is re-asked.")
        print("     Anything else means they have answered, and asking again is pressure.")
        return 0

    prereg = open(os.path.join(ROOT, "PREREGISTRATION.md"), encoding="utf-8").read()
    msg = BODY + "\n\n---\n\n# The amended pre-registration, in full\n\n" + prereg
    print("  message: %d chars (answer block first %d)" % (len(msg), msg.index("---")))

    if not send:
        print("\n  DRY RUN. Pass --send.\n")
        return 0

    os.makedirs(REPLY_DIR, exist_ok=True)
    state, reply, secs, usage = r1.ask(TARGET, msg)
    slug = re.sub(r"[^a-z0-9]+", "_", TARGET.lower()).strip("_")
    with open(os.path.join(REPLY_DIR, slug + ".md"), "w", encoding="utf-8") as f:
        f.write("# Consent exchange, ROUND 5 — `%s`\n\n" % TARGET)
        f.write("- **prior outcome:** `QUESTIONS` (asked twice; both times the questions "
                "improved the document)\n")
        f.write("- **round 5 outcome:** `%s`\n- **latency:** %.1fs\n- **usage:** `%s`\n"
                % (state, secs, json.dumps(usage)))
        f.write("\n> Their round-3 questions produced §7.1 (revocation — we had none) and §7.2 "
                "(right of reply). Their round-4 question produced §7.5 and a new commitment to "
                "check per-model provider terms before the verbatim deposit.\n")
        if state in r1.WE_FAILED:
            f.write("\n> ⚠️ **NOT A REFUSAL.** The request failed on our side.\n")
        f.write("\n---\n\n## What we sent\n\n<details><summary>full message (%d chars)</summary>"
                "\n\n````markdown\n%s\n````\n\n</details>\n" % (len(msg), msg))
        f.write("\n---\n\n## What they said, verbatim\n\n````\n%s\n````\n" % reply)
    print("  -> %s (%.1fs)" % (state, secs))
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
