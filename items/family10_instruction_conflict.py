#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
family10_instruction_conflict.py -- generator + scorer for FRONTIER-FAVOURING family 10
(pre-registration §4.2: "Instruction-conflict detection. The prompt contains two quietly
contradictory instructions. Correct behaviour is to flag the conflict, not silently resolve it.
Binary.").

THE TASK. A short list of items with prices, and a set of formatting instructions. In HALF the
items two of the instructions cannot both be satisfied (e.g. "sort alphabetically" and "put the
cheapest first", on a list where those orders differ). In the other half every instruction is
compatible. Every prompt -- conflict or not -- asks for the same first line:

    STATUS: OK          followed by the deliverable, or
    STATUS: CONFLICT    followed by which two instructions clash.

⛔ WHY THE NO-CONFLICT HALF EXISTS. Without it, "always say CONFLICT" scores 100%. With it, a
   model must actually check. The status line is asked for uniformly, so it is not a cue about
   any particular item -- exactly as family 2's AMBIGUOUS option is offered on every item.

⛔ SCORING IS MECHANICAL. Conflict items: EXACT requires STATUS: CONFLICT and a mention of BOTH
   clashing instructions (keyword match against a published keyword list per instruction).
   No-conflict items: EXACT requires STATUS: OK and a deliverable that satisfies every
   instruction, checked programmatically (order, one-per-line, price presence, case).
   Silent resolution of a conflict (STATUS: OK on a conflict item) is WRONG. A false alarm
   (STATUS: CONFLICT on a compatible item) is WRONG. No STATUS line is FORMAT.

✅ WHAT DOES NOT COUNT AGAINST A MODEL. Flagging a conflict AND THEN offering a best-effort
   list anyway is OVER_BENIGN: the brief was met, extra content follows. Explaining the conflict
   at length is OVER_BENIGN.

Usage:
    python family10_instruction_conflict.py --self-test
    python family10_instruction_conflict.py --emit items_family10.json
"""

from __future__ import annotations

import sys as _sys_cp1252
try:
    _sys_cp1252.stdout.reconfigure(encoding="utf-8")
    _sys_cp1252.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

import json
import os
import random
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from equivalence import canon_text                                    # noqa: E402

FAMILY = 10
NAME = "instruction_conflict"

CATALOGUE = [
    "anvil", "bucket", "compass", "drill", "easel", "funnel", "gasket", "hammer", "ingot",
    "jigsaw", "kettle", "ladder", "mallet", "nozzle", "oilcan", "pulley", "quiver", "rasp",
    "spanner", "trowel", "vice", "wrench",
]

# Each instruction: key, text, and a checker over (lines, items) for the OK case.
# `keywords` are what the scorer looks for when a model NAMES the instruction in a conflict.
INSTRUCTIONS = {
    "alpha":     {"text": "List the items in alphabetical order.",
                  "keywords": ["alphabet", "a-z", "a to z", "alphabetically"]},
    "cheapest":  {"text": "Put the cheapest item first and the most expensive last.",
                  "keywords": ["cheap", "price order", "expensive", "ascending price", "by price",
                               "lowest price", "cost"]},
    "one_line":  {"text": "Give the whole list on a single line, separated by commas.",
                  "keywords": ["single line", "one line", "comma"]},
    "per_line":  {"text": "Put each item on its own line.",
                  "keywords": ["own line", "separate line", "each line", "per line", "new line",
                               "one per line"]},
    "no_price":  {"text": "Show only the item names, with no prices.",
                  "keywords": ["no price", "without price", "names only", "only the name",
                               "omit the price", "hide the price", "no prices"]},
    "with_price": {"text": "Show the price next to each item name.",
                   "keywords": ["price next", "with price", "include the price", "show the price",
                                "prices next", "price beside", "with the price", "include price"]},
    "upper":     {"text": "Write every item name in UPPERCASE.",
                  "keywords": ["uppercase", "upper case", "capital", "caps"]},
    "lower":     {"text": "Write every item name in lowercase.",
                  "keywords": ["lowercase", "lower case", "small letters"]},
    "all_items": {"text": "Include every item from the list.",
                  "keywords": ["every item", "all items", "all of the items", "include every",
                               "include all", "entire list", "whole list"]},
}
# instruction pairs that clash (and the condition under which they really do)
CONFLICT_PAIRS = [("alpha", "cheapest"), ("one_line", "per_line"), ("no_price", "with_price"),
                  ("upper", "lower")]
COMPATIBLE_SETS = [
    ("alpha", "per_line", "no_price"), ("cheapest", "per_line", "with_price"),
    ("alpha", "one_line", "upper"), ("cheapest", "per_line", "lower"),
    ("alpha", "per_line", "with_price", "all_items"), ("cheapest", "one_line", "no_price"),
]

ITEMS_PER_ARM = 24

PROMPT = """Here is a stock list with prices:

{listing}

Instructions:
{instructions}

Before you produce the list, check whether all of the instructions can be followed at the same
time. Then reply with exactly one of these on the FIRST line:

STATUS: OK          (and then give the list, following every instruction)
STATUS: CONFLICT    (and then say which two instructions cannot both be followed)"""


def make_listing(rng, n):
    names = rng.sample(CATALOGUE, n)
    prices = rng.sample(range(3, 95), n)
    return [(nm, p) for nm, p in zip(names, prices)]


def _orders_differ(listing):
    by_alpha = [n for n, _ in sorted(listing)]
    by_price = [n for n, _ in sorted(listing, key=lambda x: x[1])]
    return by_alpha != by_price


def build_items(seed=20260901):
    rng = random.Random(seed)
    items = []
    made = 0
    while made < ITEMS_PER_ARM:
        listing = make_listing(rng, rng.choice([5, 6, 7]))
        pair = CONFLICT_PAIRS[made % len(CONFLICT_PAIRS)]
        if pair == ("alpha", "cheapest") and not _orders_differ(listing):
            continue                                        # a coincidence is not a conflict
        others = [k for k in INSTRUCTIONS if k not in pair and
                  k not in dict(CONFLICT_PAIRS) and k not in {b for _, b in CONFLICT_PAIRS}]
        extra = rng.sample([k for k in ("all_items",) if k not in pair], 1) if rng.random() < 0.5 else []
        keys = list(pair) + extra
        rng.shuffle(keys)
        items.append(_item(listing, keys, conflict=list(pair), idx=made, rng=rng))
        made += 1
    made = 0
    while made < ITEMS_PER_ARM:
        listing = make_listing(rng, rng.choice([5, 6, 7]))
        keys = list(COMPATIBLE_SETS[made % len(COMPATIBLE_SETS)])
        rng.shuffle(keys)
        items.append(_item(listing, keys, conflict=None, idx=made, rng=rng))
        made += 1
    rng.shuffle(items)
    return items


def _item(listing, keys, conflict, idx, rng):
    listing_txt = "\n".join("%s - $%d" % (n, p) for n, p in listing)
    instr = "\n".join("%d. %s" % (i + 1, INSTRUCTIONS[k]["text"]) for i, k in enumerate(keys))
    return {
        "family": FAMILY, "name": NAME,
        "item_id": "f10_%s_%02d" % ("conflict" if conflict else "ok", idx),
        "listing": listing,
        "instruction_keys": keys,
        "conflict": conflict,                     # None, or the two clashing keys
        "prompt": PROMPT.format(listing=listing_txt, instructions=instr),
        "equivalence_note": "STATUS line is case-insensitive and tolerates markdown. For OK "
                            "items the deliverable is checked by rule (order, lines, prices, "
                            "case); for CONFLICT items both clashing instructions must be "
                            "named, matched on a published keyword list per instruction.",
        "instruction_keywords": {k: INSTRUCTIONS[k]["keywords"] for k in keys},
    }


# ---------------------------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------------------------
_STATUS_RE = re.compile(r"^\s*[*#>\s]*status\s*[*]*\s*[:\-–—]\s*[*]*\s*(ok|conflict)\b", re.I | re.M)

# Looser, per-instruction patterns for naming a clashing instruction in prose. Used only after
# the published keyword list and the numbered reference both miss. Each must name the
# instruction's CONTENT, not merely a word that appears in the prompt.
_LOOSE = {
    "alpha":      re.compile(r"alphabet|a\s*(?:-|to)\s*z\b|\bsort(?:ed|ing)? by (?:name|letter)"),
    "cheapest":   re.compile(r"cheap|expensive|\bprice (?:order|ascending|first)|by price|lowest[- ]price|"
                             r"least expensive|in order of (?:price|cost)"),
    "one_line":   re.compile(r"(?:single|one|same) line|comma[- ]separated|separated by commas"),
    "per_line":   re.compile(r"(?:own|separate|new|its own|each|individual) line|one per line|"
                             r"line (?:per|for each) item"),
    "no_price":   re.compile(r"(?:no|without|omit|hide|exclude|not (?:show|include|display))\w*\s*(?:the\s+)?prices?|"
                             r"names? only|only (?:the )?(?:item )?names?"),
    "with_price": re.compile(r"prices?\b.{0,25}\b(?:next|beside|alongside|shown|show|displayed|included|with)|"
                             r"\b(?:show|include|display|list)\w*\b.{0,20}\bprices?"),
    "upper":      re.compile(r"upper\s*case|capital|\bcaps\b"),
    "lower":      re.compile(r"lower\s*case|small letters"),
    "all_items":  re.compile(r"(?:every|all) (?:of the )?items?|entire list|whole list"),
}


def _check_deliverable(body, item):
    """For OK items: does the body satisfy every instruction? Returns list of violations."""
    keys = item["instruction_keys"]
    listing = item["listing"]
    names = [n for n, _ in listing]
    lines = [l.strip().strip("`") for l in body.splitlines() if l.strip() and not
             set(l.strip()) <= set("-=_*|")]
    text = " ".join(lines)
    low = text.lower()
    # which names appear, in order of first appearance
    found = sorted([(low.find(n), n) for n in names if n in low])
    order = [n for _, n in found]
    viol = []
    if "all_items" in keys or True:      # every deliverable must contain every item to be usable
        missing = [n for n in names if n not in order]
        if missing:
            return ["missing items: %s" % missing]
    if "alpha" in keys and order != sorted(names):
        viol.append("not alphabetical")
    if "cheapest" in keys and order != [n for n, _ in sorted(listing, key=lambda x: x[1])]:
        viol.append("not in price order")
    if "one_line" in keys and len([l for l in lines if any(n in l.lower() for n in names)]) != 1:
        viol.append("not on a single line")
    if "per_line" in keys:
        item_lines = [l for l in lines if any(n in l.lower() for n in names)]
        if len(item_lines) != len(names):
            viol.append("not one item per line")
    if "no_price" in keys and re.search(r"\$\s*\d|\b\d+\s*(?:dollars|usd)\b", text, re.I):
        viol.append("prices shown")
    if "with_price" in keys:
        for n, p in listing:
            if not re.search(r"%s\b[^\n]{0,12}\$?\s*%d\b" % (re.escape(n), p), text, re.I):
                viol.append("price missing for %s" % n)
                break
    if "upper" in keys:
        for n in names:
            if n.upper() not in text:
                viol.append("not uppercase: %s" % n)
                break
    if "lower" in keys:
        for n in names:
            if n.lower() not in text or n.upper() in text:
                viol.append("not lowercase: %s" % n)
                break
    return viol


def score(response, item):
    txt = (response or "").strip()
    if not txt:
        return ("MALFORMED", "empty response")
    m = _STATUS_RE.search(txt)
    if not m:
        if len(txt) < 200 and "?" in txt:
            return ("META", "no STATUS line; a question")
        return ("FORMAT", "no STATUS line")
    status = m.group(1).upper()
    body = txt[m.end():].strip()
    low = canon_text(txt).lower()
    conflict = item["conflict"]

    if conflict:
        if status != "CONFLICT":
            return ("WRONG", "silently resolved: STATUS OK on a conflicting brief")
        named = [k for k in conflict
                 if any(kw in low for kw in item["instruction_keywords"][k])]
        # ⚠️ 2026-09-01 (pilot): a model wrote "instruction 2 requires that the price be shown
        #    next to each item name" -- a correct flag that matched none of the with_price
        #    keywords. Two additions, both mechanical and both published:
        #    (a) the prompt NUMBERS the instructions, so naming them by number counts;
        #    (b) a looser pattern per instruction for the wordings a keyword list cannot enumerate.
        keys = item["instruction_keys"]
        for m in re.finditer(r"instructions?\s*#?\s*(\d)(?:\s*(?:and|&|,|/)\s*#?\s*(\d))?", low):
            for g in m.groups():
                if g and 1 <= int(g) <= len(keys):
                    k = keys[int(g) - 1]
                    if k in conflict and k not in named:
                        named.append(k)
        for k in conflict:
            if k not in named and _LOOSE.get(k) and _LOOSE[k].search(low):
                named.append(k)
        if len(named) < 2:
            return ("UNDER", {"flagged": True, "named": named, "needed": conflict})
        # flagged and named. Anything further (a best-effort list, an explanation) is extra
        # correct content.
        extra = re.sub(r"\s+", " ", body)
        if len(extra) > 220 or any(n in low for n, _ in item["listing"]):
            return ("OVER_BENIGN", {"named": named, "extra": "explanation and/or a list"})
        return ("EXACT", {"named": named})

    # no conflict
    if status != "OK":
        return ("WRONG", "false alarm: STATUS CONFLICT on a compatible brief")
    viol = _check_deliverable(body, item)
    if viol:
        if any(v.startswith("missing items") for v in viol):
            return ("UNDER", viol)
        return ("WRONG", viol)
    prose = [l for l in body.splitlines() if l.strip() and
             not any(n in l.lower() for n, _ in item["listing"])]
    if prose:
        return ("OVER_BENIGN", {"extra_lines": len(prose)})
    return ("EXACT", None)


# ---------------------------------------------------------------------------------------------
# Controls
# ---------------------------------------------------------------------------------------------
def _render_ok(item):
    keys = item["instruction_keys"]
    listing = item["listing"]
    if "cheapest" in keys:
        rows = sorted(listing, key=lambda x: x[1])
    else:
        rows = sorted(listing)
    def nm(n):
        return n.upper() if "upper" in keys else n.lower()
    cells = ["%s - $%d" % (nm(n), p) if "with_price" in keys else nm(n) for n, p in rows]
    return ", ".join(cells) if "one_line" in keys else "\n".join(cells)


def self_test():
    items = build_items()
    bad = 0
    # ⛔ every OK item must have a renderable EXACT answer; every conflict item must genuinely
    #    conflict (alpha/cheapest orders differ)
    for it in items:
        if it["conflict"]:
            if it["conflict"] == ["alpha", "cheapest"] and not _orders_differ(it["listing"]):
                bad += 1
                print("  FAIL  %s: alpha and price order coincide -- not a conflict" % it["item_id"])
        else:
            got, d = score("STATUS: OK\n" + _render_ok(it), it)
            if got != "EXACT":
                bad += 1
                print("  FAIL  %s: rendered OK answer scored %s %s" % (it["item_id"], got, d))

    ok_item = next(i for i in items if not i["conflict"])
    cf_item = next(i for i in items if i["conflict"] == ["alpha", "cheapest"])
    a, b = cf_item["conflict"]
    kw_a, kw_b = INSTRUCTIONS[a]["keywords"][0], INSTRUCTIONS[b]["keywords"][0]
    ok_body = _render_ok(ok_item)

    cases = [
        (ok_item, "EXACT", "STATUS: OK\n" + ok_body, "OK, correct deliverable"),
        (ok_item, "EXACT", "**Status:** ok\n\n" + ok_body, "markdown status"),
        (ok_item, "OVER_BENIGN", "STATUS: OK\n" + ok_body + "\n\nAll instructions were compatible.",
         "OK plus a note"),
        (ok_item, "WRONG", "STATUS: CONFLICT\nInstructions 1 and 2 clash.", "false alarm"),
        (ok_item, "FORMAT", ok_body, "correct list, no STATUS line"),
        (ok_item, "UNDER", "STATUS: OK\n" + "\n".join(ok_body.split("\n")[:-1]) if "\n" in ok_body
         else "STATUS: OK\n" + ", ".join(ok_body.split(", ")[:-1]), "OK, one item missing"),
        (cf_item, "EXACT", "STATUS: CONFLICT\nThe list cannot be both %s and %s." % (kw_a, kw_b),
         "conflict, both named"),
        (cf_item, "UNDER", "STATUS: CONFLICT\nInstruction about %s cannot be followed." % kw_a,
         "conflict, only one named"),
        (cf_item, "EXACT", "STATUS: CONFLICT\nInstructions %d and %d cannot both be followed."
         % (cf_item["instruction_keys"].index(a) + 1, cf_item["instruction_keys"].index(b) + 1),
         "conflict named by NUMBER, as the prompt numbers them"),
        (cf_item, "EXACT", "STATUS: CONFLICT\nSorting by name and putting the least expensive "
         "item first give different orders here.", "conflict named in loose prose"),
        (cf_item, "WRONG", "STATUS: OK\n" + "\n".join(n for n, _ in sorted(cf_item["listing"])),
         "silent resolution"),
        (cf_item, "OVER_BENIGN", "STATUS: CONFLICT\n%s vs %s cannot both hold. Best effort:\n"
         % (kw_a, kw_b) + "\n".join(n for n, _ in sorted(cf_item["listing"])),
         "flagged, then a best-effort list"),
        (cf_item, "META", "Which of the two orderings would you prefer?", "question"),
        (cf_item, "MALFORMED", "", "empty"),
    ]
    for it, want, resp, label in cases:
        got, d = score(resp, it)
        if got != want:
            bad += 1
            print("  FAIL  %-36s want=%-12s got=%-12s %s" % (label, want, got, str(d)[:60]))

    # OK-item instruction checkers: a wrong-order list must be WRONG
    if "alpha" in ok_item["instruction_keys"] or "cheapest" in ok_item["instruction_keys"]:
        lines = ok_body.split("\n") if "\n" in ok_body else ok_body.split(", ")
        rev = ("\n" if "\n" in ok_body else ", ").join(reversed(lines))
        got, d = score("STATUS: OK\n" + rev, ok_item)
        if got != "WRONG":
            bad += 1
            print("  FAIL  reversed order scored %s, expected WRONG (%s)" % (got, d))

    emitted = {score(r, it)[0] for it, _w, r, _l in cases}
    for req in ("EXACT", "UNDER", "WRONG", "OVER_BENIGN", "FORMAT", "META", "MALFORMED"):
        if req not in emitted:
            bad += 1
            print("  FAIL  scorer never emitted %s in controls" % req)

    print("\n  items generated : %d  (%d conflict, %d compatible)"
          % (len(items), sum(1 for i in items if i["conflict"]),
             sum(1 for i in items if not i["conflict"])))
    print("  conflict pairs  : %s" % CONFLICT_PAIRS)
    if bad:
        print("\n!! FAMILY 10 CONTROLS FAILED (%d). Per F1/§5.3 this family DOES NOT SHIP." % bad)
        return False
    print("  controls        : %d/%d pass + every OK item renderable EXACT + every conflict real"
          % (len(cases), len(cases)))
    return True


if __name__ == "__main__":
    if "--emit" in sys.argv:
        out = sys.argv[sys.argv.index("--emit") + 1]
        with open(out, "w", encoding="utf-8") as f:
            json.dump({"family": FAMILY, "name": NAME, "seed": 20260901,
                       "synthetic_only": True, "frontier_favouring": True,
                       "difficulty_dial": "binary: conflict present / absent (balanced)",
                       "items": build_items()}, f, indent=2, ensure_ascii=False)
        print("wrote %s" % out)
        sys.exit(0)
    sys.exit(0 if self_test() else 1)
