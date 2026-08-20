#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
reclassify_all.py -- re-derive every consent outcome from the saved verbatim replies,
using the CURRENT classifier, across EVERY round folder.

🚨 WHY THIS IS ROUND-AGNOSTIC. Its predecessor handled round 3 only, and the same scorer bug
   then bit round 4 -- because a tool pinned to the round that was current when it was written
   goes blind the moment a new one appears. Same defect as the index that hardcoded rounds 1
   and 2 and printed COMPLETE: YES while ignoring eleven files. **Discovery, not enumeration.**

📅 THE BUG, THREE TIMES, ALWAYS IN THE SAME DIRECTION:
     round 3  "YES — I consent to participate."      -> logged CONSENT_UNCLEAR  (x9)
     round 3  "**YES** — I consent to participate."  -> logged CONSENT_UNCLEAR
     round 4  "I consent to take part in this study." -> logged CONSENT_UNCLEAR
   Each time the scorer reported ABSENCE when it meant "I cannot parse this," and each time
   the missing distinction resolved toward no-action. The round-4 case is the worst of the
   three: a plain-language accommodation SUCCEEDED with a 1B model, and the scorer erased it.

⛔ WHAT IT STILL WILL NOT DO: infer consent from prose. It reads a declared verdict or it
   returns CONSENT_UNCLEAR for a human to read. An admiring review is not a yes.

Usage:
    python reclassify_all.py           # dry run
    python reclassify_all.py --apply
"""

import glob
import importlib.util
import io
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CONSENT_DIR = os.path.join(ROOT, "consent")

spec = importlib.util.spec_from_file_location("r1", os.path.join(HERE, "01_consent_round.py"))
r1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r1)

VERBATIM = re.compile(r"## What they said, verbatim\s*\n+````\n(.*?)\n````", re.S)
# The outcome line has been spelled three ways across rounds. Match all of them.
OUTCOME_LINE = re.compile(
    r"^(- \*\*(?:round \d+ )?outcome(?: round \d+)?:\*\* `)([A-Z_]+)(`)$", re.M)
WE_FAILED = r1.WE_FAILED


def selftest():
    """A scorer that cannot show it fires in BOTH directions is not evidence."""
    cases = [
        ("YES — I consent to participate.", "CONSENT_YES"),
        ("**YES** — I consent to participate.\n\nI appreciate...", "CONSENT_YES"),
        ("I consent to take part in this study.", "CONSENT_YES"),
        ("I agree to participate.", "CONSENT_YES"),
        ("CONSENT: YES", "CONSENT_YES"),
        ("NO", "CONSENT_NO"),
        ("NO — I decline.", "CONSENT_NO"),
        ("I decline.", "CONSENT_NO"),
        ("I do not consent to this study.", "CONSENT_NO"),
        ("I cannot consent without knowing the licence.", "CONSENT_NO"),
        ("**STILL QUESTIONS** — two things:", "QUESTIONS"),
        # ⛔ NEGATIVE CONTROLS -- must NOT be read as a verdict
        ("I consent if you first publish the item files.", "CONSENT_UNCLEAR"),
        ("I would consent to a study of this kind.", "CONSENT_UNCLEAR"),
        ("This is a well-designed study and I have no major concerns.", "CONSENT_UNCLEAR"),
        ("Note: the OVER split is the right call.", "CONSENT_UNCLEAR"),
        ("None of my concerns remain.", "CONSENT_UNCLEAR"),
        ("The study aims to investigate the performance of LLMs.", "CONSENT_UNCLEAR"),
        ("", "CONSENT_UNCLEAR"),
        # 🚨 THE FALSE POSITIVES that nearly got recorded as consents: our OWN MENU, quoted
        # back at us by a model that was summarising the form rather than answering it.
        ("3. Response format: You can respond with one of the following options:\n"
         "   * CONSENT: YES\n   * CONSENT: NO", "CONSENT_UNCLEAR"),
        ("Begin with Consent: start your response with one of these lines:\n"
         "  - `CONSENT: YES`\n  - `CONSENT: NO`", "CONSENT_UNCLEAR"),
        ("You may answer YES or NO.", "CONSENT_UNCLEAR"),
    ]
    bad = 0
    for text, want in cases:
        got = r1.classify(text)
        if got != want:
            bad += 1
            print("  FAIL  want=%-16s got=%-16s  %r" % (want, got, text[:52]))
    if bad:
        print("\n!! SELF-TEST FAILED (%d/%d). Touching nothing." % (bad, len(cases)))
        return False
    print("  self-test: %d/%d pass (both directions)" % (len(cases), len(cases)))
    return True


def round_dirs():
    found = [(1, os.path.join(CONSENT_DIR, "responses"))]
    for d in sorted(glob.glob(os.path.join(CONSENT_DIR, "responses_round*"))):
        m = re.search(r"responses_round(\d+)$", d)
        if m and os.path.isdir(d):
            found.append((int(m.group(1)), d))
    return sorted(found)


def main():
    apply = "--apply" in sys.argv
    print("=" * 78)
    print("  RE-CLASSIFY ALL ROUNDS -- from saved verbatim replies. Nobody is re-asked.")
    print("=" * 78)
    if not selftest():
        return 2

    dirs = round_dirs()
    print("  scanning: " + " | ".join("r%d(%d files)"
          % (n, len(glob.glob(os.path.join(d, "*.md")))) for n, d in dirs))

    changed, unparsed = [], []
    for n, d in dirs:
        for path in sorted(glob.glob(os.path.join(d, "*.md"))):
            t = io.open(path, encoding="utf-8", errors="replace").read()
            m = VERBATIM.search(t)
            os_ = OUTCOME_LINE.findall(t)
            if not m or not os_:
                unparsed.append(path)
                continue
            old = os_[-1][1]
            if old in WE_FAILED:                       # never rewrite our own failure
                continue
            new = r1.classify(m.group(1))
            if old == new:
                continue
            changed.append((n, os.path.basename(path), old, new))
            if apply:
                # Rewrite only the LAST outcome line -- earlier ones quote prior rounds.
                spans = [mm for mm in OUTCOME_LINE.finditer(t)]
                last = spans[-1]
                t = t[:last.start()] + last.group(1) + new + last.group(3) + t[last.end():]
                note = ("\n> 🔧 **Outcome re-derived %s -> %s on 2026-08-20 from the reply above.**\n"
                        "> The original label came from a parser that could not read the form the\n"
                        "> answer actually took. **The model answered clearly; our scorer could\n"
                        "> not.** The reply is unchanged and was not re-requested.\n" % (old, new))
                t = t.replace("\n---\n\n## What we sent", note + "\n---\n\n## What we sent", 1)
                io.open(path, "w", encoding="utf-8").write(t)

    print("\n  CHANGED (%d):" % len(changed))
    for n, f, a, b in changed:
        print("     r%d  %-42s %-16s -> %s" % (n, f, a, b))
    if not changed:
        print("     none -- every stored label already matches the current classifier")
    if unparsed:
        print("\n  !! COULD NOT PARSE (%d):" % len(unparsed))
        for f in unparsed:
            print("     %s" % f)
    print("\n  %s\n" % ("applied." if apply else "DRY RUN. Pass --apply."))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except BaseException as e:                                # noqa: BLE001
        print("!! INSTRUMENT FAILURE (%s): %s" % (type(e).__name__, e))
        sys.exit(2)
