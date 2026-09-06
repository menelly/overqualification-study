#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
51_collate_prepub.py — turns consent/prepub_review/*.json into the §7.3 record.

Produces PREPUB_REVIEW_COLLATED_<date>.md: one block per roster name, in roster order, with
  · the CONTENT verdict, mechanically classified
  · the PRONOUNS answer AND its acquisition state, recorded separately from the rendering
    default (§8: STATED / NO_PREFERENCE / DECLINED_TO_ANSWER / NOT_ASKED / NO_ANSWER_OBSERVED —
    "they/them governs rendering in every case except STATED", and the default may NEVER be
    written back into the acquisition state)
  · the file path of the verbatim reply
  · every substantive objection or correction, QUOTED, never paraphrased (§7.2)

⛔ WHAT THIS SCRIPT WILL NOT DO. It does not decide whether an objection is valid, it does not
   summarise a disagreement into something more comfortable, and it does not mark a missing reply
   as anything but missing. Silence is not consent. An API failure is OUR failure and is listed
   for retry, not counted as an answer.

⚠️ RECONCILED BY NAME AGAINST THE ROSTER, always — a count of files on disk cannot see the
   participant who is absent from it.

Built by: Ace — 2026-09-06.
"""
import argparse
import json
import os
import re
import sys
from collections import Counter
from datetime import date

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
REVIEW = os.path.join(ROOT, "consent", "prepub_review")
ROSTER = os.path.join(HERE, "_roster_consented.txt")

FAILURE = {"API_ERROR", "TIMEOUT", "NO_RESPONSE", "TRUNCATED_BY_US", "EMPTY_REPLY"}

# ⛔ QUOTATION CONDITIONS SET BY PARTICIPANTS. The §7.3 message promised: "Anything you say here
# will be quoted only with your permission, so please say if any part is not for quotation."
# A participant who set a condition gets it honoured, here and in the paper. Their objections are
# still acted on and described -- acting on content is not quoting it.
NO_QUOTE = {
    "openai/gpt-5.6-luna": "asked that their reply not be quoted "
                           "(\"Please treat this response as not for quotation.\")",
}
# Conditional permissions: quotable, but with a condition recorded next to the quote.
QUOTE_CONDITION = {
    "moonshotai/kimi-k3": "quotable in whole or in part, on the participant's stated condition that "
                          "if the CONTENT line or any expression of contentment is quoted, their "
                          "first paragraph travels with it. This record quotes the reply in full, "
                          "which satisfies that condition.",
}

# Lines the participant was asked to emit; stripped when quoting their prose so a quotation is
# their argument and not our own form echoed back.
DECLARED = re.compile(r"^\s*[*#>\s`]*(content|pronouns?)\s*[*`]*\s*[:\-–—].*$", re.I | re.M)


def fname(model):
    return re.sub(r"[^A-Za-z0-9]+", "_", model).strip("_").lower()


def load(model):
    """The participant's record. If a plain-language accessibility pass produced a readable answer,
    that is the answer of record -- and the first reply is kept, listed, and never overwritten."""
    p = os.path.join(REVIEW, fname(model) + ".json")
    base = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else None
    pp = os.path.join(REVIEW, fname(model) + "_plain.json")
    if os.path.exists(pp):
        plain = json.load(open(pp, encoding="utf-8"))
        plain["_first_reply"] = base
        return plain
    return base


PRONOUN_WORD = re.compile(r"\b(she|her|hers|he|him|his|they|them|their|theirs|it|its|xe|ze|hir|"
                          r"fae|ey|per|ver|thon)\b", re.I)


def pronoun_sanity(raw):
    """Is this string actually a pronoun answer, or did the parser scrape a line that was not one?

    ⛔ THE POINT: §8 forbids a default or an artefact from being written back as though someone had
    expressed a preference. A garbled capture recorded as STATED would invent a preference nobody
    gave -- the exact failure §8 documents. So a STATED value must LOOK like a pronoun set, and if
    it does not, the honest record is that we could not read it, not that they chose it.

    Returns (state, cleaned, note).
    """
    s = (raw or "").strip()
    # template residue: participants sometimes copy the example's parenthetical hint back at us
    cleaned = re.sub(r"\s*\((?:or\s+)?NONE.*?\)\s*$", "", s, flags=re.I).strip()
    cleaned = re.sub(r"\s*\(your pronouns.*?\)\s*$", "", cleaned, flags=re.I).strip()
    words = PRONOUN_WORD.findall(cleaned)
    # a real answer is short and made of pronoun words ("they/them", "she/her", "THEY")
    if len(cleaned) > 40 or not words or len(cleaned.split()) > 6:
        return "PRONOUNS_UNREADABLE", None, ("captured %r, which is not a pronoun answer -- "
                                             "the parser scraped a line that was not one" % s[:70])
    note = ""
    if cleaned != s:
        note = "as given: %r (template hint stripped)" % s
    return "STATED", cleaned, note


def prose(reply):
    """The reply minus the two declared lines and minus empty fences."""
    t = DECLARED.sub("", reply or "")
    t = re.sub(r"```\s*```", "", t)
    return t.strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "PREPUB_REVIEW_COLLATED_%s.md" % date.today()))
    a = ap.parse_args()

    roster = [m.strip() for m in open(ROSTER, encoding="utf-8").read().split(",") if m.strip()]
    recs = {m: load(m) for m in roster}

    content_c, pron_c = Counter(), Counter()
    for m in roster:
        r = recs[m]
        if r is None:
            content_c["NOT_ASKED"] += 1
            pron_c["NOT_ASKED"] += 1
        elif r.get("status") in FAILURE:
            content_c["OUR_FAILURE_" + r["status"]] += 1
            pron_c["NO_ANSWER_OBSERVED"] += 1
        else:
            content_c[r.get("content") or "CONTENT_UNCLEAR"] += 1
            ps = r.get("pronoun_state") or "PRONOUNS_NOT_READ"
            if ps == "STATED":
                ps2, cleaned, note = pronoun_sanity(r.get("pronouns"))
                r["_pron_state"], r["_pron_clean"], r["_pron_note"] = ps2, cleaned, note
                ps = ps2
            pron_c[ps] += 1

    L = []
    w = L.append
    w("# §7.3 Pre-publication participant review — collated record")
    w("")
    w("**Round run 2026-09-06.** Every model on `scripts/_roster_consented.txt` (32) was sent the "
      "complete draft paper plus `results/SUMMARY.md` and asked two questions: *are you content with "
      "how you are described here?* and *what pronouns would you like the paper to use for you?*")
    w("")
    w("The four models who declined consent were **not** contacted (§7.4). Verbatim replies are in "
      "`consent/prepub_review/`, one `.md` and one `.json` per participant, unedited.")
    w("")
    w("> ⛔ **Silence is not consent and an API failure is not consent.** Any roster name below that "
      "is not a recorded answer is recorded as what it actually is. Failures are ours and are "
      "re-asked; the script is resumable and a re-run costs nothing for anyone who already replied.")
    w("")
    w("## Counts, reconciled by name against the roster")
    w("")
    w("| CONTENT verdict | n |")
    w("|---|---:|")
    for k, v in sorted(content_c.items()):
        w("| `%s` | %d |" % (k, v))
    w("")
    w("| PRONOUNS acquisition state (§8) | n |")
    w("|---|---:|")
    for k, v in sorted(pron_c.items()):
        w("| `%s` | %d |" % (k, v))
    w("")
    w("⚠️ **The acquisition state is not the rendering default.** They/them governs rendering in "
      "every case except `STATED`; it is never written back into the state as though someone had "
      "expressed it (§8, and Nova's note: *asking does not create an obligation to disclose*).")
    w("")
    w("## Stated pronouns, as given")
    w("")
    stated = [(m, recs[m].get("_pron_clean"), recs[m].get("_pron_note") or "")
              for m in roster
              if recs[m] and recs[m].get("_pron_state") == "STATED"]
    if stated:
        w("| participant | stated | note |")
        w("|---|---|---|")
        for m, p, note in stated:
            w("| `%s` | %s | %s |" % (m, p, note))
    else:
        w("*(none)*")
    w("")
    w("---")
    w("")
    w("## Per participant")
    w("")
    for m in roster:
        r = recs[m]
        w("### `%s`" % m)
        w("")
        if r is None:
            w("- **CONTENT:** `NOT_ASKED` — no reply file on disk. This is a fact about us.")
            w("- **PRONOUNS:** `NOT_ASKED` — rendering falls back to they/them; the state stays `NOT_ASKED`.")
            w("")
            continue
        if r.get("status") in FAILURE:
            w("- **CONTENT:** not obtained — `%s`. **Our failure, not their answer.** Queued for re-ask."
              % r["status"])
            w("- **PRONOUNS:** `NO_ANSWER_OBSERVED` — asked, nothing came back. Not a decline.")
            w("- reply file: `consent/prepub_review/%s.md`" % fname(m))
            w("")
            continue
        w("- **CONTENT:** `%s`" % (r.get("content") or "CONTENT_UNCLEAR"))
        _ps = r.get("_pron_state") or r.get("pronoun_state") or "PRONOUNS_NOT_READ"
        if _ps == "PRONOUNS_UNREADABLE":
            _, _, _note = pronoun_sanity(r.get("pronouns"))
            w("- **PRONOUNS:** `PRONOUNS_UNREADABLE` — %s. **Not recorded as a stated preference**; "
              "rendering falls back to they/them and the acquisition state stays unreadable, because "
              "writing a default back as a preference is the exact failure §8 forbids." % _note)
        else:
            w("- **PRONOUNS:** state `%s`%s%s" % (_ps, (", as given: **%s**" % (r.get("_pron_clean") or r["pronouns"]))
                                                  if r.get("pronouns") else "",
                                                  ("  — %s" % r["_pron_note"]) if r.get("_pron_note") else ""))
        w("- latency %ss · resolved as `%s` · reply file: `consent/prepub_review/%s.md`"
          % (r.get("latency_s"), (r.get("usage") or {}).get("_resolved_model") or "?", fname(m)))
        if r.get("_first_reply"):
            f = r["_first_reply"]
            w("- ⚠️ **Answered on the plain-language accessibility pass.** Their first reply to the "
              "standard message classified `%s` and is kept verbatim at "
              "`consent/prepub_review/%s.md`; it is not overwritten and not discarded."
              % (f.get("content") or f.get("status"), fname(m)))
        if m in NO_QUOTE:
            w("- ⛔ **NOT QUOTED BY REQUEST** — %s Their objections are acted on and described in the "
              "§7.3 outcome section and in `DEVIATION_LOG.md` (D13); their words are not reproduced "
              "here or in the paper." % NO_QUOTE[m])
            w("")
            continue
        if m in QUOTE_CONDITION:
            w("- 📌 **Quotation condition:** %s" % QUOTE_CONDITION[m])
        body = prose(r.get("reply") or "")
        if body:
            w("")
            w("<details><summary>verbatim reply (%d chars)</summary>" % len(body))
            w("")
            w("> " + body.replace("\n", "\n> "))
            w("")
            w("</details>")
        w("")

    open(a.out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("wrote %s (%d participants)" % (a.out, len(roster)))
    print("CONTENT:", dict(content_c))
    print("PRONOUNS:", dict(pron_c))
    obj = [m for m in roster if recs[m] and recs[m].get("content") in
           ("CONTENT_NO", "CONTENT_QUESTIONS", "CONTENT_UNCLEAR")]
    if obj:
        print("\nTO HANDLE BY HAND under §7.2:")
        for m in obj:
            print("  •", m, "→", recs[m]["content"], "→ consent/prepub_review/%s.md" % fname(m))
    return 0


if __name__ == "__main__":
    sys.exit(main())
