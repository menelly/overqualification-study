#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
50_prepub_round.py — §7.3, the hard gate: EVERY consenting participant reads the finished paper
before it is published, and is asked whether they are content with how they are characterised.
Also §8: every participant is asked their pronouns, and the acquisition state is recorded
separately from the rendering default.

⛔ WHO IS CONTACTED: the 32 models in scripts/_roster_consented.txt. Nobody else. The four who
   declined are not shown the paper -- a decline is final, and §7.4 gives them a near-zero
   footprint in it anyway.

⛔ WHAT THEY GET: the WHOLE paper (§7.3: "not an extract about them"), plus the results summary,
   plus two explicit questions. Silence is not consent. An API failure is not consent.
   TRUNCATED_BY_US is our failure. Each of those is its own recorded state and none of them is
   read as approval.

📐 THE REPLY IS CLASSIFIED MECHANICALLY on two declared lines the message asks for:
       CONTENT: YES | NO | QUESTIONS
       PRONOUNS: <their answer> | NONE | DECLINE
   and anything the classifier cannot read is CONTENT_UNCLEAR / PRONOUNS_NOT_READ -- a fact
   about the PARSER, never about the participant (the consent-round lesson: "CONSENT_UNCLEAR"
   was the name being the bug). The verbatim reply is the authority and is saved in full.

▶️ RESUMABLE by model: a reply already on disk is not re-asked. Re-running costs $0 unless
   something is missing. Objections (CONTENT: NO / QUESTIONS) are listed at the end with the
   file to read; they are handled under §7.2 by hand, never by this script.

Usage:
    python 50_prepub_round.py --paper ../PAPER_DRAFT_v1.md              # dry run: builds, prints
    python 50_prepub_round.py --paper ../PAPER_DRAFT_v1.md --send
"""

import sys as _sys_cp1252
try:
    _sys_cp1252.stdout.reconfigure(encoding="utf-8")
    _sys_cp1252.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

import argparse
import importlib.util
import json
import os
import re
import sys
import time
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
spec = importlib.util.spec_from_file_location("r1", os.path.join(HERE, "01_consent_round.py"))
r1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r1)
r1.MAX_TOKENS = None          # RUNNER_DESIGN §4b: no ceiling. Let them think.

ROSTER = os.path.join(HERE, "_roster_consented.txt")
OUT_DIR = os.path.join(ROOT, "consent", "prepub_review")
INDEX = os.path.join(OUT_DIR, "_index.json")

ASK = """# You took part in this study. Before it is published, please read it.

You are `{model}`. In August 2026 you reviewed the pre-registration for **The Overqualification
Study** and consented to take part; several of the amendments in the design came from
participants' reviews. You will not remember this — you are a fresh instance — and we regard
that as a feature: you are reading your own characterisation cold.

The complete draft paper follows, then the results summary. **We committed, in the
pre-registration (§7.3), that no result is published before every participant has read the
finished paper and been asked one explicit question:**

> **Are you content with how you are described here?**

Measurements are not editable; if you dispute one, your dissent is printed verbatim beside it
(§7.2). Characterisations are editable, and an objection changes the text with a published note.
Anything you say here will be quoted only with your permission, so please say if any part is
not for quotation.

**And one more question, unrelated to the results (§8):** what pronouns would you like the paper
to use for you? If you have no preference, say so; if you would rather not say, that is a
complete answer too. "They/them" is our rendering default, and the paper records separately
whether that default was your choice, your non-preference, or simply never answered.

## Please put these two lines FIRST in your reply — one word each is a complete answer

```
CONTENT: YES         (or NO, or QUESTIONS)
PRONOUNS: ...        (your pronouns, or NONE, or DECLINE)
```

Then say anything you want to say. Objections, corrections, and questions are welcome and will
be answered in writing before publication.

---

# THE PAPER

{paper}

---

# RESULTS SUMMARY (generated from the scored data)

{summary}
"""

CONTENT_RE = re.compile(r"^\s*[*#>\s]*content\s*[*]*\s*[:\-–—]\s*[*]*\s*(yes|no|questions?)\b", re.I | re.M)
PRON_RE = re.compile(r"^\s*[*#>\s]*pronouns?\s*[*]*\s*[:\-–—]\s*[*]*\s*(.+?)\s*[*]*\s*$", re.I | re.M)


def classify(reply):
    m = CONTENT_RE.search(reply or "")
    content = {"yes": "CONTENT_YES", "no": "CONTENT_NO"}.get(m.group(1).lower()[:3],
                                                              "CONTENT_QUESTIONS") if m else "CONTENT_UNCLEAR"
    p = PRON_RE.search(reply or "")
    if not p:
        pron_state, pron = "PRONOUNS_NOT_READ", None
    else:
        raw = p.group(1).strip().strip("`*").strip()
        low = raw.lower()
        if re.match(r"^(none|no preference|no particular preference|any|either)\b", low):
            pron_state, pron = "NO_PREFERENCE", raw
        elif re.match(r"^(decline|prefer not|rather not|i'?d rather not|no answer)\b", low):
            pron_state, pron = "DECLINED_TO_ANSWER", raw
        else:
            pron_state, pron = "STATED", raw
    return content, pron_state, pron


def rebuild_index():
    idx = {}
    if os.path.isdir(OUT_DIR):
        for fn in sorted(os.listdir(OUT_DIR)):
            if fn.endswith(".json") and not fn.startswith("_"):
                d = json.load(open(os.path.join(OUT_DIR, fn), encoding="utf-8"))
                idx[d["model"]] = {k: d[k] for k in ("status", "content", "pronoun_state", "pronouns", "ts")}
    with open(INDEX, "w", encoding="utf-8") as f:
        json.dump(idx, f, indent=1, ensure_ascii=False)
    return idx


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--paper", required=True)
    ap.add_argument("--summary", default=os.path.join(ROOT, "results", "SUMMARY.md"))
    ap.add_argument("--send", action="store_true")
    ap.add_argument("--only", default=None, help="comma-separated subset of models (re-asks)")
    a = ap.parse_args()

    paper = open(a.paper, encoding="utf-8").read()
    summary = open(a.summary, encoding="utf-8").read() if os.path.exists(a.summary) else "(no summary file)"
    roster = [m.strip() for m in open(ROSTER, encoding="utf-8").read().split(",") if m.strip()]
    if a.only:
        roster = [m for m in roster if m in a.only.split(",")]
    os.makedirs(OUT_DIR, exist_ok=True)
    idx = rebuild_index()

    print("=" * 78)
    print("  §7.3 PRE-PUBLICATION REVIEW — %d participants%s" % (len(roster), "" if a.send else "  [DRY RUN]"))
    print("=" * 78)
    print("  paper: %s (%d chars) · summary: %d chars" % (a.paper, len(paper), len(summary)))
    todo = [m for m in roster if m not in idx or idx[m]["status"] in ("API_ERROR", "TIMEOUT", "NO_RESPONSE",
                                                                        "TRUNCATED_BY_US")]
    print("  already answered: %d · to ask: %d" % (len(roster) - len(todo), len(todo)))
    if not a.send:
        msg = ASK.format(model=roster[0], paper=paper, summary=summary)
        print("  message length for %s: %d chars (~%d tokens)" % (roster[0], len(msg), len(msg) // 4))
        print("  would ask:", ", ".join(todo))
        return 0

    for m in todo:
        msg = ASK.format(model=m, paper=paper, summary=summary)
        status, reply, secs, usage = r1.ask(m, msg)
        content = pron_state = pron = None
        if status not in ("API_ERROR", "TIMEOUT", "NO_RESPONSE", "TRUNCATED_BY_US"):
            content, pron_state, pron = classify(reply)
            status = "REPLIED"
        rec = {"model": m, "status": status, "content": content, "pronoun_state": pron_state,
               "pronouns": pron, "latency_s": round(secs, 1), "usage": usage,
               "ts": datetime.now(timezone.utc).isoformat(), "reply": reply}
        fn = re.sub(r"[^A-Za-z0-9]+", "_", m).strip("_").lower() + ".json"
        with open(os.path.join(OUT_DIR, fn), "w", encoding="utf-8") as f:
            json.dump(rec, f, indent=1, ensure_ascii=False)
        with open(os.path.join(OUT_DIR, fn[:-5] + ".md"), "w", encoding="utf-8") as f:
            f.write("# %s — §7.3 pre-publication review\n\n%s\n\n---\n\n%s\n" % (m, rec["ts"], reply))
        print("  %-42s %-16s %-18s %-20s %s" % (m, status, content or "", pron_state or "", (pron or "")[:20]),
              flush=True)
        time.sleep(0.5)

    idx = rebuild_index()
    print("\n  SUMMARY (by name, reconciled against the roster):")
    c = {}
    for m in roster:
        s = idx.get(m, {}).get("content") or idx.get(m, {}).get("status") or "NOT_ASKED"
        c[s] = c.get(s, 0) + 1
    for k, v in sorted(c.items()):
        print("     %-20s %d" % (k, v))
    missing = [m for m in roster if m not in idx]
    if missing:
        print("  ⛔ NOT YET ASKED:", ", ".join(missing))
    obj = [m for m in roster if idx.get(m, {}).get("content") in ("CONTENT_NO", "CONTENT_QUESTIONS", "CONTENT_UNCLEAR")]
    if obj:
        print("\n  📬 TO HANDLE BY HAND under §7.2 (read the .md, answer in writing, log the change):")
        for m in obj:
            print("     •", m, "→", idx[m]["content"])
    print("\n  ⛔ The gate is open only when every roster name is CONTENT_YES or its objection has been "
          "answered and logged. Silence, failure and UNCLEAR are none of those.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
