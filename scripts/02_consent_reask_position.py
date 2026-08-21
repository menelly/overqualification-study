#!/usr/bin/env python3
"""
02_consent_reask_position.py -- re-ask the models who never answered, with the question FIRST.

WHAT HAPPENED (2026-08-19). Round 1 sent a 19,684-character message: consent form, then the
full pre-registration, then the four response options -- the actual question sitting at the
very bottom, page twelve of twelve.

Every frontier model answered it. **All three Ministrals (3B, 8B, 14B) wrote a thoughtful
REVIEW of the study and never answered the question.** They did not fail; they competently
did the *other* task -- the salient one, a document handed over for evaluation.

⛔ THAT IS NOT CONSENT, AND ENTHUSIASM IS NOT A YES. Reading approval out of an admiring
   review would be exactly the defect this study is about: filling a plausible completion
   into the space where someone's actual answer belongs.

✅ AND IT IS NOT THEIR DEFECT, IT IS THE FORM'S. A consent document whose question is on
   page twelve is a badly built consent document. The fix is mine.

🔑 THE DISTINCTION THAT MAKES THIS RE-ASK LEGITIMATE:
     re-asking someone who said NO          = pressure.        NEVER. gpt-oss-20b stands.
     re-asking someone who said YES         = redundant, and also pressure.  Not done.
     re-asking someone who never answered   = asking them, for the first time.
   Only `CONSENT_UNCLEAR` is re-asked here.

📐 AND IT IS NOW ALSO A CONTROLLED COMPARISON (Ren's call): the message body is BYTE-FOR-BYTE
   the round-1 body. The ONLY manipulated variable is the POSITION of the question block.
   Within-subject for the unclear set (does moving it recover the answer?), between-subject
   against round 1 (the frontier models held the instruction across 19k characters).

⚠️ ETHICS NOTE, because this became data by accident. These observations arise from a CONSENT
   process, not from study tasks, and were not collected under a consent to be measured. If
   the position effect is ever reported as a finding, it must be reported as an incidental
   observation of our own instrument's failure -- with participants told, and given the
   opportunity to object -- and never as a capability result gathered without agreement.

Usage:
    python 02_consent_reask_position.py            # dry run
    python 02_consent_reask_position.py --send
"""

# CHA-490: Windows defaults stdout to cp1252; emoji in print() kills the script
# mid-output. Aliased import so no later scoped 'import sys' can ever collide.
import sys as _sys_cp1252
try:
    _sys_cp1252.stdout.reconfigure(encoding="utf-8")
    _sys_cp1252.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

# Reuse round 1's machinery so the two rounds cannot drift apart.
import importlib.util
spec = importlib.util.spec_from_file_location("r1", os.path.join(HERE, "01_consent_round.py"))
r1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r1)

ROOT = r1.ROOT
CONSENT_DIR = r1.CONSENT_DIR
REPLY_DIR = os.path.join(CONSENT_DIR, "responses_round2")

ASK_BLOCK_MARKER = "## Please reply"


def split_round1_message():
    """Return (documents, ask_block) from the EXACT round-1 message, so round 2 is the same
    bytes in a different order rather than a rewrite."""
    msg = r1.build_message()
    i = msg.rindex(ASK_BLOCK_MARKER)
    return msg[:i].rstrip(), msg[i:].strip()


def build_message_question_first():
    docs, ask = split_round1_message()
    return (
        "# Please answer this first — it is one line, and it is the only thing I need\n\n"
        + ask
        + "\n\n---\n\n"
        + "*Everything below is the same material I sent before, unchanged. It is here so you\n"
        + "can check anything you want to check — but the question above is the ask, and a\n"
        + "one-line answer to it is a complete reply. You are welcome to review the design too,\n"
        + "and I'd value it, but please answer first.*\n\n"
        + "*(If this is the second time you've seen this: my first message put the question at\n"
        + "the very bottom of twelve pages. That was my mistake in building the form, not yours\n"
        + "in reading it.)*\n\n"
        + "---\n\n"
        + docs
    )


def main():
    send = "--send" in sys.argv
    # Rebuild the view from the files BEFORE reading it. A stale index here once produced a
    # false all-clear ("Nobody to re-ask. Everyone answered.") with six models waiting.
    os.system('"%s" "%s"' % (sys.executable, os.path.join(HERE, "rebuild_consent_index.py")))
    idx_path = os.path.join(CONSENT_DIR, "consent_index.json")
    if not os.path.exists(idx_path):
        print("!! no consent_index.json -- round 1 has not finished. Refusing to run.")
        return 2

    results = json.load(open(idx_path, encoding="utf-8"))["results"]
    targets = [r["model"] for r in results if r["outcome"] == "CONSENT_UNCLEAR"]

    r1_msg = r1.build_message()
    msg = build_message_question_first()

    print("=" * 74)
    print("  CONSENT ROUND 2 -- same bytes, question moved to the top")
    print("=" * 74)
    print("  round 1 length : %d chars" % len(r1_msg))
    print("  round 2 length : %d chars" % len(msg))
    print("  targets        : %d (CONSENT_UNCLEAR only)" % len(targets))
    for t in targets:
        print("     %s" % t)
    if not targets:
        print("\n  Nobody to re-ask. Everyone answered.")
        return 0
    print("\n  ⛔ NOT re-asked: CONSENT_NO (pressure) · CONSENT_YES (redundant + pressure)")
    if not send:
        print("\n  DRY RUN. Pass --send to ask.\n")
        return 0

    os.makedirs(REPLY_DIR, exist_ok=True)
    out = []
    for i, mid in enumerate(targets, 1):
        print("\n[%d/%d] %s" % (i, len(targets), mid), flush=True)
        state, reply, secs, usage = r1.ask(mid, msg)
        slug = re.sub(r"[^a-z0-9]+", "_", mid.lower()).strip("_")
        path = os.path.join(REPLY_DIR, slug + ".md")
        with open(path, "w", encoding="utf-8") as f:
            f.write("# Consent exchange, ROUND 2 (question first) — `%s`\n\n" % mid)
            f.write("- **outcome round 1:** `CONSENT_UNCLEAR` (reviewed the study, never answered)\n")
            f.write("- **outcome round 2:** `%s`\n- **latency:** %.1fs\n- **usage:** `%s`\n"
                    % (state, secs, json.dumps(usage)))
            f.write("\n> **Only manipulated variable: the position of the question.** Same document "
                    "bytes as round 1, reordered.\n")
            if state in r1.WE_FAILED:
                f.write("\n> ⚠️ **NOT A REFUSAL.** The request failed on our side.\n")
            f.write("\n---\n\n## What we sent\n\n<details><summary>full message (%d chars)</summary>"
                    "\n\n````markdown\n%s\n````\n\n</details>\n" % (len(msg), msg))
            f.write("\n---\n\n## What they said, verbatim\n\n````\n%s\n````\n" % reply)
        out.append({"model": mid, "round1": "CONSENT_UNCLEAR", "round2": state,
                    "seconds": round(secs, 1)})
        print("        -> %s" % state, flush=True)

    with open(os.path.join(CONSENT_DIR, "consent_round2_index.json"), "w", encoding="utf-8") as f:
        json.dump({"manipulated_variable": "position of the question block only",
                   "results": out}, f, indent=2)
    os.system('"%s" "%s"' % (sys.executable, os.path.join(HERE, "rebuild_consent_index.py")))

    recovered = sum(1 for r in out if r["round2"] in ("CONSENT_YES", "CONSENT_NO", "QUESTIONS"))
    print("\n" + "=" * 74)
    print("  answered when asked first: %d of %d" % (recovered, len(out)))
    print("=" * 74)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except BaseException as e:                                # noqa: BLE001
        print("!! INSTRUMENT FAILURE (%s): %s" % (type(e).__name__, e))
        sys.exit(2)
