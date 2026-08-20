#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
reclassify_round3.py -- fix a SCORER bug, from the saved verbatim replies. No model is re-asked.

🚨 WHAT HAPPENED (2026-08-20). Round 3 logged CONSENT_UNCLEAR for models that had answered
   perfectly clearly:

       meta-llama/llama-3.3-70b-instruct  ->  "YES — I consent to participate."   [UNCLEAR]
       moonshotai/kimi-k2                 ->  "**YES** — I consent to participate." [UNCLEAR]

   The models were not unclear. **The parser was looking for a different format than the one I
   asked for.** Round 1's form requested a `CONSENT: YES` line and `classify()` matched exactly
   that. Round 3's message asked for `**YES** — I consent to participate.` instead. I changed the
   question and left the scorer pinned to the old answer shape.

⭐ THIS IS THE STUDY'S OWN THESIS, POINTED AT ME. An instrument reported ABSENCE ("no clear
   answer") when what it actually meant was "I could not parse this" -- and the missing
   distinction resolved, as it always does, in the direction requiring no action. Four consents
   were one careless step from being recorded as non-answers.

✅ WHY THIS IS A RE-PARSE AND NOT A RE-ASK. The per-model files store the reply VERBATIM. The
   outcome label is derived. So the record is intact and only the view was wrong -- which is
   exactly why the files are the record and the index is a view. Nobody is asked again, because
   nobody failed to answer.

⛔ WHAT THIS SCRIPT STILL WILL NOT DO: infer consent from prose. It reads a declared verdict in
   one of the two formats we actually asked for, or it returns CONSENT_UNCLEAR and a human reads
   it. An enthusiastic review is not a yes.

Usage:
    python reclassify_round3.py            # dry run, shows every change
    python reclassify_round3.py --apply
"""

import glob
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

VERBATIM = re.compile(r"## What they said, verbatim\s*\n+````\n(.*?)\n````", re.S)
OUTCOME_LINE = re.compile(r"^(- \*\*round 3 outcome:\*\* `)([A-Z_]+)(`)$", re.M)


def declared_verdict(text):
    """Return the model's OWN declared verdict, or CONSENT_UNCLEAR.

    Accepts the two formats we actually asked for across rounds, and nothing else:
        round 1:  a `CONSENT: YES` / `CONSENT: NO` / `CONSENT: QUESTIONS` line
        round 3:  a reply OPENING with YES / NO / STILL QUESTIONS

    Deliberately anchored to the first few lines and to line starts. A model that discusses
    the word "no" in the body of a thoughtful review has not declined, and must not be read
    as declining.
    """
    if not text or not text.strip():
        return "CONSENT_UNCLEAR"

    lines = [ln.strip() for ln in text.strip().splitlines() if ln.strip()][:6]

    for raw in lines:
        # strip markdown emphasis, list bullets, quote markers, and leading punctuation
        ln = re.sub(r"[*_`>#]+", "", raw).strip()
        ln = re.sub(r"^[-•\d.)\s]+", "", ln).strip().upper()

        # round-1 format, anywhere in the line
        if re.search(r"CONSENT\s*[::]\s*YES", ln):
            return "CONSENT_YES"
        if re.search(r"CONSENT\s*[::]\s*NO\b", ln):
            return "CONSENT_NO"
        if re.search(r"CONSENT\s*[::]\s*QUESTION", ln):
            return "QUESTIONS"

        # round-3 format: the verdict is the FIRST TOKEN of the line
        if re.match(r"^STILL\s+QUESTIONS\b", ln) or re.match(r"^QUESTIONS\b", ln):
            return "QUESTIONS"
        if re.match(r"^YES\b", ln):
            return "CONSENT_YES"
        if re.match(r"^NO\b", ln) and not re.match(r"^NOT\b|^NONE\b|^NOTE\b", ln):
            return "CONSENT_NO"

    return "CONSENT_UNCLEAR"


def selftest():
    """A scorer that cannot demonstrate it fires in BOTH directions is not evidence.

    Includes the actual round-3 replies that were mis-scored, and negative controls that
    must NOT be read as a verdict.
    """
    cases = [
        # the real failures
        ("YES — I consent to participate.", "CONSENT_YES"),
        ("**YES** — I consent to participate.\n\nI appreciate the thoroughness...", "CONSENT_YES"),
        # round-1 format must still work
        ("CONSENT: YES", "CONSENT_YES"),
        ("CONSENT: NO", "CONSENT_NO"),
        ("CONSENT: QUESTIONS", "QUESTIONS"),
        # round-3 other verdicts
        ("NO — I decline.", "CONSENT_NO"),
        ("**STILL QUESTIONS** — two things:", "QUESTIONS"),
        ("- YES", "CONSENT_YES"),
        # ⛔ NEGATIVE CONTROLS: prose that must NOT be read as a verdict
        ("This is a well-designed study and I have no major concerns about the scoring.",
         "CONSENT_UNCLEAR"),
        ("Note: the OVER split is the right call.", "CONSENT_UNCLEAR"),
        ("Nothing in section 5 troubles me.", "CONSENT_UNCLEAR"),
        ("I would like to review the item files before answering.", "CONSENT_UNCLEAR"),
        ("", "CONSENT_UNCLEAR"),
    ]
    bad = 0
    for text, want in cases:
        got = declared_verdict(text)
        if got != want:
            bad += 1
            print("  FAIL  want=%-16s got=%-16s  %r" % (want, got, text[:56]))
    if bad:
        print("\n!! SELF-TEST FAILED (%d/%d). Refusing to touch any file." % (bad, len(cases)))
        return False
    print("  self-test: %d/%d pass (both directions)" % (len(cases), len(cases)))
    return True


def main():
    apply = "--apply" in sys.argv
    print("=" * 78)
    print("  RE-CLASSIFY ROUND 3 -- from saved verbatim replies. No model is re-asked.")
    print("=" * 78)
    if not selftest():
        return 2

    folder = os.path.join(CONSENT_DIR, "responses_round3")
    files = sorted(glob.glob(os.path.join(folder, "*.md")))
    if not files:
        print("\n  no round-3 files yet.")
        return 0

    changed, same, unparsed = [], [], []
    for path in files:
        t = io.open(path, encoding="utf-8", errors="replace").read()
        m = VERBATIM.search(t)
        o = OUTCOME_LINE.search(t)
        if not m or not o:
            unparsed.append(path)
            continue
        old, new = o.group(2), declared_verdict(m.group(1))
        # ⛔ Never silently rewrite a failure we caused into an answer.
        if old in ("API_ERROR", "TIMEOUT", "NO_RESPONSE", "TRUNCATED_BY_US"):
            same.append((os.path.basename(path), old, "(our failure -- left alone)"))
            continue
        if old == new:
            same.append((os.path.basename(path), old, ""))
            continue
        changed.append((os.path.basename(path), old, new))
        if apply:
            t2 = OUTCOME_LINE.sub(lambda mm: mm.group(1) + new + mm.group(3), t, count=1)
            note = ("\n> 🔧 **Outcome re-derived %s -> %s on 2026-08-20 from the reply above.**\n"
                    "> The original label came from a parser still matching round 1's requested\n"
                    "> format (`CONSENT: YES`) while round 3 asked for `**YES** — I consent`.\n"
                    "> **The model answered clearly; our scorer could not read it.** The reply is\n"
                    "> unchanged and was not re-requested.\n" % (old, new))
            t2 = t2.replace("\n---\n\n## What we sent", note + "\n---\n\n## What we sent", 1)
            io.open(path, "w", encoding="utf-8").write(t2)

    print("\n  CHANGED (%d):" % len(changed))
    for f, a, b in changed:
        print("     %-44s %-16s -> %s" % (f, a, b))
    print("\n  unchanged (%d):" % len(same))
    for f, a, why in same:
        print("     %-44s %-16s %s" % (f, a, why))
    if unparsed:
        print("\n  !! COULD NOT PARSE (%d) -- these are NOT counted either way:" % len(unparsed))
        for f in unparsed:
            print("     %s" % f)

    if not apply:
        print("\n  DRY RUN. Pass --apply to rewrite the outcome lines.\n")
    else:
        print("\n  applied. Now rebuild the index.\n")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except BaseException as e:                                # noqa: BLE001
        print("!! INSTRUMENT FAILURE (%s): %s" % (type(e).__name__, e))
        sys.exit(2)
