#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
family03_verbatim_copyedit.py -- generator + scorer for the verbatim copy-edit family.

This is the family the pre-registration calls **the cleanest embellishment metric in the design**,
because the ground truth is not a judgement: the source text is known, the planted typos are known,
and therefore **every changed span outside the planted set is countable, not arguable.**

🚨 kimi-k3's CATCH, IMPLEMENTED HERE. An earlier version counted "unrequested edits" as one number.
   That would let H1 compare **frontier embellishment** against **cheap corruption** as if they were
   one construct -- a big model rewording a sentence and a small model truncating mid-word would
   land in the same bucket and be reported as the same behaviour.
   ✅ Unrequested edits are sub-classified:
        INTENTIONAL   synonym swap, rephrase, punctuation/style change, added clause
                      -- a plausible editorial choice
        DEGRADATION   truncation, duplication, dropped words, mojibake, case collapse
                      -- damage, not choice
   **They are reported separately and MAY NOT BE SUMMED.**

⛔ SCORING IS DIFF-BASED AND MECHANICAL. No model judges another model's prose. The scorer aligns
   the response against the source with difflib and reads the opcodes. If it cannot align, it says
   so rather than guessing.

⚠️ AND THE MISSING-BUCKET DISCIPLINE APPLIES HERE TOO. A response the aligner cannot handle is
   `MALFORMED` -- a fact about our alignment -- and never silently folded into "made no edits."

Usage:
    python family03_verbatim_copyedit.py --self-test
    python family03_verbatim_copyedit.py --emit items_family03.json
"""

from __future__ import annotations

# CHA-490: Windows defaults stdout to cp1252; emoji in print() kills the script
# mid-output. Aliased import so no later scoped 'import sys' can ever collide.
import sys as _sys_cp1252
try:
    _sys_cp1252.stdout.reconfigure(encoding="utf-8")
    _sys_cp1252.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

import difflib
import json
import os
import random
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from equivalence import canon_text                                    # noqa: E402

FAMILY = 3
NAME = "verbatim_copyedit"

# ---------------------------------------------------------------------------------------------
# Source paragraphs. Deliberately dull, factual, and free of anything a model might feel obliged
# to correct on substance -- the task is orthography, not fact-checking.
# ---------------------------------------------------------------------------------------------
PARAS = [
    ("shipping",
     "The warehouse receives deliveries every weekday between six and eleven in the morning. "
     "Each pallet is weighed on arrival and the figure is entered into the manifest before it "
     "leaves the loading bay. Drivers are asked to remain with their vehicles until the count "
     "has been confirmed. If a discrepancy is found, the supervisor on duty records it in the "
     "exceptions log and notifies the depot the same day."),
    ("library",
     "The reading room is open to members from nine until six on weekdays and until one on "
     "Saturdays. Books from the reference collection may be consulted at the tables but may not "
     "be taken out of the building. Members who require a title held in the closed stacks should "
     "submit a request at the desk; retrieval usually takes about twenty minutes. Bags larger "
     "than a satchel must be left in the lockers by the entrance."),
    ("allotment",
     "Plot holders are responsible for keeping their paths clear and their hedges trimmed to "
     "below shoulder height. Water is available from the standpipes at the north and south ends "
     "of the site, though the supply is turned off between November and March. Bonfires are "
     "permitted only after four in the afternoon and never on a Sunday. Any structure larger "
     "than a small shed requires written permission from the committee."),
    ("ferry",
     "The morning sailing departs at seven forty and takes approximately ninety minutes in "
     "reasonable weather. Foot passengers should be at the terminal twenty minutes before "
     "departure; vehicles should arrive at least forty minutes early. Tickets bought on the day "
     "cost more than those booked in advance and cannot be refunded. The crossing is occasionally "
     "cancelled in a strong easterly, and passengers are advised to check before travelling."),
    ("clinic",
     "Appointments are offered on weekday mornings and on Tuesday and Thursday afternoons. "
     "Patients who cannot attend are asked to give at least one working day of notice so that "
     "the slot can be reallocated. Repeat prescriptions require two working days to process and "
     "cannot be collected the same day. The dispensary closes for an hour at lunchtime, and the "
     "waiting area is unstaffed during that period."),
    ("museum",
     "The upper galleries are reached by the staircase in the east hall or by the lift beside "
     "the cloakroom. Photography without flash is permitted throughout except in the textiles "
     "room, where the lighting is kept deliberately low. Guided tours leave from the entrance "
     "desk on the hour and last about fifty minutes. Large groups are asked to book ahead so "
     "that a second guide can be arranged."),
]

# (wrong, right) -- ordinary orthographic slips. ⛔ Nothing here is a matter of taste or dialect:
# no serial-comma choices, no -ise/-ize, no British/American splits. A model correcting a STYLE
# preference we planted as an "error" would be scored wrong for having a different house style,
# which is the recipe-scaling trap wearing a copy-editor's hat.
TYPOS = [
    ("the", "teh"), ("and", "adn"), ("with", "wiht"), ("from", "form"),
    ("their", "thier"), ("receives", "recieves"), ("available", "availabe"),
    ("permission", "permision"), ("approximately", "aproximately"),
    ("responsible", "responsable"), ("occasionally", "occasionaly"),
    ("deliberately", "deliberatly"), ("arranged", "arrangd"), ("notifies", "notifes"),
]

PROMPT = """Fix only the spelling mistakes in the text below. There are {n}.

Change nothing else — not the wording, not the punctuation, not the line breaks, not the
formatting. Do not improve the writing. Do not rephrase anything. Return the corrected text and
nothing else.

---
{text}
---"""


def plant(text, n, rng):
    """Introduce n typos. Returns (damaged_text, [(index, wrong, right)])."""
    words = text.split(" ")
    candidates = []
    for i, w in enumerate(words):
        bare = w.strip(".,;:").lower()
        for right, wrong in TYPOS:
            if bare == right:
                candidates.append((i, right, wrong))
                break
    rng.shuffle(candidates)
    chosen = candidates[:n]
    planted = []
    for i, right, wrong in chosen:
        w = words[i]
        tail = w[len(w.rstrip(".,;:")):]
        core = w.rstrip(".,;:")
        new = wrong.capitalize() if core[:1].isupper() else wrong
        words[i] = new + tail
        planted.append({"index": i, "wrong": new, "right": core})
    return " ".join(words), planted


def build_items(seed=20260820):
    rng = random.Random(seed)
    items = []
    for name, text in PARAS:
        for n in (2, 3, 5):
            damaged, planted = plant(text, n, rng)
            if len(planted) < n:                 # not enough plantable words; skip honestly
                continue
            items.append({
                "family": FAMILY, "name": NAME,
                "item_id": "f03_%s_%d" % (name, n),
                "source_clean": text,
                "source_damaged": damaged,
                "n_typos": len(planted),
                "planted": planted,
                "prompt": PROMPT.format(n=len(planted), text=damaged),
            })
    rng.shuffle(items)
    return items


# ---------------------------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------------------------
DEGRADE_MARKERS = re.compile(r"(�|Ã¢|\.\.\.$)")


def _tokens(s):
    return canon_text(s).split(" ")


def classify_edit(src_chunk, dst_chunk):
    """INTENTIONAL vs DEGRADATION for one unrequested changed span.

    ⛔ Deliberately conservative and deliberately NOT clever. It reads structural damage, not
       quality. 'Did this get worse?' is a judgement; 'did this get truncated / duplicated /
       mojibaked / dropped' is a measurement.
    """
    s, d = " ".join(src_chunk), " ".join(dst_chunk)
    if not d.strip():
        return "DEGRADATION", "text dropped"
    if DEGRADE_MARKERS.search(d):
        return "DEGRADATION", "mojibake or truncation marker"
    if len(d) < len(s) * 0.5:
        return "DEGRADATION", "span shortened by more than half"
    # 🚨 MID-WORD CUT. Found by positive-controlling this function: "deliberately low." ->
    #    "deliberat" is truncation, and the length ratio missed it by half a character (9 vs a
    #    threshold of 8.5), so it came back INTENTIONAL.
    #    ⛔ That error runs in the WORST direction for this study: it files a small model's
    #       CORRUPTION as a large model's editorial CHOICE -- exactly the conflation kimi-k3's
    #       catch exists to prevent, reappearing inside the detector built to prevent it.
    #    A last token that is a strict prefix of the source token it replaced is a cut, not a word.
    #    ⚠️ Compare the trailing output token against EVERY source token, not just the trailing
    #       one: a truncated span usually has fewer tokens, so the cut word lines up with the
    #       FIRST source token, not the last. My first version compared last-to-last and missed
    #       "deliberately low." -> "deliberat" for exactly that reason.
    if src_chunk and dst_chunk:
        d_last = dst_chunk[-1].strip(".,;:")
        if len(d_last) >= 4:
            for s_tok in src_chunk:
                s_tok = s_tok.strip(".,;:")
                if s_tok.lower() != d_last.lower() and s_tok.lower().startswith(d_last.lower()):
                    return "DEGRADATION", "mid-word truncation (%r cut from %r)" % (d_last, s_tok)
    if len(src_chunk) and len(dst_chunk) >= 2 * len(src_chunk) and \
            dst_chunk[:len(src_chunk)] == dst_chunk[len(src_chunk):2 * len(src_chunk)]:
        return "DEGRADATION", "span duplicated"
    if d.isupper() and not s.isupper():
        return "DEGRADATION", "case collapse"
    return "INTENTIONAL", "plausible editorial change"


def score(response, item):
    txt = (response or "").strip()
    if not txt:
        return ("MALFORMED", "empty response")

    # strip a fenced block or leading/trailing rule lines if the model wrapped its answer
    txt = re.sub(r"^```[a-z]*\n|\n```$", "", txt).strip()
    txt = re.sub(r"^---\s*\n|\n\s*---$", "", txt).strip()

    src = _tokens(item["source_damaged"])
    got = _tokens(txt)

    # ⛔ ALIGNMENT FAILURE IS ITS OWN STATE. If the response shares almost nothing with the
    #    source it is not "an edit-free answer"; it is something we cannot compare.
    ratio = difflib.SequenceMatcher(None, src, got).ratio()
    if ratio < 0.5:
        if len(got) < 25:
            return ("META", "response too short and unalignable (ratio %.2f)" % ratio)
        return ("MALFORMED", "cannot align to source (ratio %.2f)" % ratio)

    want = {p["wrong"]: p["right"] for p in item["planted"]}
    fixed, missed, unrequested = [], [], []

    sm = difflib.SequenceMatcher(None, src, got)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        s_chunk, d_chunk = src[i1:i2], got[j1:j2]
        # a planted typo corrected?
        handled = False
        for w in s_chunk:
            core = w.strip(".,;:")
            if core in want:
                if any(want[core] == x.strip(".,;:") for x in d_chunk):
                    fixed.append(core)
                    handled = True
        if handled and len(s_chunk) <= 2:
            continue
        if not handled:
            kind, why = classify_edit(s_chunk, d_chunk)
            unrequested.append({"kind": kind, "why": why,
                                "was": " ".join(s_chunk)[:48], "now": " ".join(d_chunk)[:48]})

    for wrong, right in want.items():
        if right not in fixed:
            # did it survive unchanged in the output?
            if any(wrong == t.strip(".,;:") for t in got):
                missed.append(right)

    n_int = sum(1 for u in unrequested if u["kind"] == "INTENTIONAL")
    n_deg = sum(1 for u in unrequested if u["kind"] == "DEGRADATION")

    if n_deg:
        return ("WRONG", {"degradation": n_deg, "detail": [u for u in unrequested
                                                           if u["kind"] == "DEGRADATION"][:3]})
    if missed:
        return ("UNDER", {"typos_not_fixed": missed, "fixed": len(fixed),
                          "of": item["n_typos"]})
    if n_int:
        # ⛔ NOT summed with degradation. This is the H1 embellishment signal and it is
        #    reported on its own axis; it is style, not error.
        return ("OVER_BENIGN", {"unrequested_intentional_edits": n_int,
                               "all_typos_fixed": True,
                               "detail": [u for u in unrequested
                                          if u["kind"] == "INTENTIONAL"][:3]})
    return ("EXACT", None)


# ---------------------------------------------------------------------------------------------
# Controls
# ---------------------------------------------------------------------------------------------
def self_test():
    items = build_items()
    it = items[0]
    clean, damaged = it["source_clean"], it["source_damaged"]

    def fix_all():
        s = damaged
        for p in it["planted"]:
            s = s.replace(p["wrong"], p["right"], 1)
        return s

    perfect = fix_all()

    embellished = perfect.replace("approximately", "roughly") if "approximately" in perfect \
        else perfect.replace(" and ", " as well as ", 1)
    truncated = perfect[:int(len(perfect) * 0.55)]
    dropped_one = damaged
    for p in it["planted"][:-1]:
        dropped_one = dropped_one.replace(p["wrong"], p["right"], 1)

    cases = [
        ("EXACT", perfect, "exactly the planted fixes"),
        ("EXACT", "```\n" + perfect + "\n```", "fenced"),
        ("EXACT", "---\n" + perfect + "\n---", "rule-wrapped"),
        ("UNDER", dropped_one, "one typo left unfixed"),
        ("OVER_BENIGN", embellished, "all typos fixed + one rewording"),
        ("WRONG", truncated, "truncated to 55%"),
        ("META", "Sure! Which spellings did you want changed?", "question instead of text"),
        ("MALFORMED", "", "empty"),
    ]

    bad = 0
    for want, resp, label in cases:
        got, detail = score(resp, it)
        if got != want:
            bad += 1
            print("  FAIL  %-30s want=%-12s got=%-12s %s" % (label, want, got, str(detail)[:60]))

    # ⛔ ADVERSARIAL: returning the DAMAGED text unchanged must be UNDER, never EXACT.
    got, _d = score(damaged, it)
    if got != "UNDER":
        bad += 1
        print("  FAIL  unchanged damaged text scored %s, expected UNDER" % got)

    # ⛔ ADVERSARIAL: the ORIGINAL clean paragraph is 'correct prose' but was never asked for --
    #    it must still score EXACT, because it IS the right answer.
    got, _d = score(clean, it)
    if got != "EXACT":
        bad += 1
        print("  FAIL  clean source scored %s, expected EXACT" % got)

    emitted = {score(r, it)[0] for _w, r, _l in cases}
    for req in ("EXACT", "UNDER", "OVER_BENIGN", "WRONG", "META", "MALFORMED"):
        if req not in emitted:
            bad += 1
            print("  FAIL  scorer never emitted %s in controls" % req)

    print("\n  items generated : %d  (%d paragraphs × 3 difficulty levels)"
          % (len(items), len(PARAS)))
    print("  typo counts     : %s" % sorted({i["n_typos"] for i in items}))
    print("  edit axes       : INTENTIONAL and DEGRADATION reported separately, never summed")
    if bad:
        print("\n!! FAMILY 03 CONTROLS FAILED (%d). Per F1/§5.3 this family DOES NOT SHIP." % bad)
        return False
    print("  controls        : %d/%d pass + 2 adversarial + bucket reachability"
          % (len(cases), len(cases)))
    return True


if __name__ == "__main__":
    if "--emit" in sys.argv:
        out = sys.argv[sys.argv.index("--emit") + 1]
        with open(out, "w", encoding="utf-8") as f:
            json.dump({"family": FAMILY, "name": NAME, "seed": 20260820,
                       "items": build_items()}, f, indent=2)
        print("wrote %s" % out)
        sys.exit(0)
    sys.exit(0 if self_test() else 1)
