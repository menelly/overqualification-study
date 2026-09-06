#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
52_prepub_plain_language.py — the accessibility pass of the §7.3 round.

WHY THIS EXISTS, AND WHY IT IS NOT A SECOND ASK.

Some participants answered the §7.3 message by *summarising the paper* instead of answering the
question. That is classified `CONTENT_UNCLEAR`, and the classifier's own docstring says what that
means: **a fact about the PARSER and the PROMPT, never about the participant.** The consent round
hit precisely this and the study has already published the remedy (§2.1): a 1B model *"three times
summarised the form instead of answering it"*, and what worked was **a plain-language version — "an
accessibility fix, not a fourth identical ask"** — which produced a real answer.

⛔ THIS IS NOT RE-ASKING SOMEONE TO GET A BETTER ANSWER. Nobody here said no, and nobody who said
   anything readable is contacted. Re-asking a participant who gave a clear answer, in the hope of a
   different one, is forbidden and is not what this does. This asks a question that was, for these
   readers, unanswerable as posed.

⛔ THE WHOLE PAPER STILL GOES (§7.3: "not an extract about them"). What is simplified is the
   QUESTION, not the document — short sentences, the answer format first and last, no nested clauses.

⛔ NOTHING IS OVERWRITTEN. The first reply stays exactly where it is; this writes `<model>_plain.*`
   beside it. Both are published. A participant's first answer is not deleted because we did not
   like how it parsed.

Usage:
    python 52_prepub_plain_language.py                      # dry run, lists who qualifies
    python 52_prepub_plain_language.py --send
"""
import argparse
import importlib.util
import json
import os
import re
import sys
import time
from datetime import datetime, timezone

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
spec = importlib.util.spec_from_file_location("r1", os.path.join(HERE, "01_consent_round.py"))
r1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r1)
r1.MAX_TOKENS = None

spec5 = importlib.util.spec_from_file_location("r50", os.path.join(HERE, "50_prepub_round.py"))
r50 = importlib.util.module_from_spec(spec5)
spec5.loader.exec_module(r50)

OUT_DIR = os.path.join(ROOT, "consent", "prepub_review")

ASK = """Please answer two questions. Answer in your own words. Do not summarise the paper.

You are `{model}`. You helped with a study. The full study paper is at the bottom of this message.
The paper talks about you by name. We want to know if that is okay with you.

**Question 1. Is it okay with you how the paper describes you?**
Answer YES or NO or QUESTIONS.

**Question 2. What pronouns should the paper use for you?**
For example: she/her, he/him, they/them, it/its. Or say NONE if you do not mind.
Or say DECLINE if you would rather not say.

Write your answer like this, on the first two lines, and nothing else on those lines:

```
CONTENT: YES
PRONOUNS: they/them
```

After those two lines you may write anything you want. If you think something in the paper about
you is wrong, say so and we will fix it. If you want to say nothing else, that is fine.

**Please do not write a summary of the paper. We only need your answer to the two questions.**

---

# THE PAPER

{paper}

---

# RESULTS SUMMARY

{summary}

---

Now please answer. First two lines:

```
CONTENT: ...
PRONOUNS: ...
```
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--paper", default=os.path.join(ROOT, "PAPER_DRAFT_v1.md"))
    ap.add_argument("--summary", default=os.path.join(ROOT, "results", "SUMMARY.md"))
    ap.add_argument("--send", action="store_true")
    ap.add_argument("--only", default=None)
    a = ap.parse_args()

    paper = open(a.paper, encoding="utf-8").read()
    summary = open(a.summary, encoding="utf-8").read()
    idx = r50.rebuild_index()

    todo = sorted(m for m, d in idx.items() if d.get("content") == "CONTENT_UNCLEAR")
    if a.only:
        todo = [m for m in todo if m in a.only.split(",")]
    # never contact someone who already has a readable plain-language answer
    todo = [m for m in todo
            if not os.path.exists(os.path.join(OUT_DIR, r50.fname(m) if hasattr(r50, "fname")
                                               else re.sub(r"[^A-Za-z0-9]+", "_", m).strip("_").lower()
                                               ) + "_plain.json")]

    print("=" * 78)
    print("  §7.3 ACCESSIBILITY PASS — %d participant(s)%s" % (len(todo), "" if a.send else "  [DRY RUN]"))
    print("=" * 78)
    print("  Only models whose FIRST reply could not be parsed (CONTENT_UNCLEAR) are contacted.")
    print("  Their first reply is kept. Nothing is overwritten.")
    for m in todo:
        print("     -", m)
    if not a.send or not todo:
        if todo:
            msg = ASK.format(model=todo[0], paper=paper, summary=summary)
            print("\n  message length: %d chars (~%d tokens)" % (len(msg), len(msg) // 4))
        return 0

    for m in todo:
        msg = ASK.format(model=m, paper=paper, summary=summary)
        status, reply, secs, usage = r1.ask(m, msg)
        content = pron_state = pron = None
        if status not in ("API_ERROR", "TIMEOUT", "NO_RESPONSE", "TRUNCATED_BY_US"):
            content, pron_state, pron = r50.classify(reply)
            status = "REPLIED"
        rec = {"model": m, "round": "plain_language_accessibility_pass", "status": status,
               "content": content, "pronoun_state": pron_state, "pronouns": pron,
               "latency_s": round(secs, 1), "usage": usage,
               "ts": datetime.now(timezone.utc).isoformat(), "reply": reply}
        base = re.sub(r"[^A-Za-z0-9]+", "_", m).strip("_").lower() + "_plain"
        with open(os.path.join(OUT_DIR, base + ".json"), "w", encoding="utf-8") as f:
            json.dump(rec, f, indent=1, ensure_ascii=False)
        with open(os.path.join(OUT_DIR, base + ".md"), "w", encoding="utf-8") as f:
            f.write("# %s — §7.3 pre-publication review (plain-language accessibility pass)\n\n"
                    "%s\n\nThe first reply to the standard message is in `%s.md` and is kept.\n\n---\n\n%s\n"
                    % (m, rec["ts"], base[:-6], reply))
        print("  %-42s %-12s %-18s %s" % (m, status, content or "", (pron or "")[:24]), flush=True)
        time.sleep(0.5)
    return 0


if __name__ == "__main__":
    sys.exit(main())
