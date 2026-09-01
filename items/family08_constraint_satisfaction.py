#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
family08_constraint_satisfaction.py -- generator + scorer for the first FRONTIER-FAVOURING family
(pre-registration §4.2, family 8: "Constraint satisfaction under load. Multiple simultaneous
mechanical constraints; score = how many hold.").

THE TASK. Assign N people to three shifts so that K simultaneous constraints all hold. K is the
difficulty dial (3 / 5 / 7 / 9). The pre-registered prediction is that accuracy on this family
favours higher-capability models and that the gap WIDENS as K rises (§4.2, "with the gap widening
as constraint count rises").

⛔ GROUND TRUTH IS THE CONSTRAINT SET, NOT ONE ASSIGNMENT. Many rosters can satisfy the same
   constraints. Scoring a model against the particular roster the generator happened to draw
   would mark a correct model wrong for finding a different valid solution -- the recipe-scaling
   trap again. So the scorer CHECKS EVERY CONSTRAINT against whatever roster the model produced.
   EXACT means every constraint holds and every person is placed exactly once.

✅ SATISFIABILITY BY CONSTRUCTION. Every item is built by first drawing a random roster and then
   deriving constraints that roster satisfies. An unsatisfiable item would score every model WRONG
   and read as a capability ceiling when it was our bug. The self-test verifies the generator's
   own roster scores EXACT on every emitted item.

✅ EQUIVALENCE, PUBLISHED BEFORE COLLECTION: shift names accept aliases (morning / AM / early;
   afternoon / PM / day / mid; night / late / overnight), any case, any list marker, "Name - Shift"
   or "Name: Shift" or "Shift: Name, Name". Order of lines is irrelevant.

⚠️ WHAT COUNTS AGAINST A MODEL AND WHAT DOES NOT. A correct roster followed by a sentence of
   explanation is OVER_BENIGN (does not count). A roster with a violated constraint is WRONG,
   with the violated constraints named in the detail so partial credit ("how many hold") is
   reportable as the pre-registration asks -- but the BUCKET is WRONG, because the deliverable
   is a roster that does not meet the brief.

Usage:
    python family08_constraint_satisfaction.py --self-test
    python family08_constraint_satisfaction.py --emit items_family08.json
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

FAMILY = 8
NAME = "constraint_satisfaction"

# Synthetic. Single-token first names only, so "Name: Shift" parsing has no ambiguity.
PEOPLE_POOL = ["Amara", "Bao", "Callum", "Dilnoza", "Esther", "Farid", "Greta", "Hamza",
               "Ingrid", "Jonah", "Kaede", "Leona", "Mateus", "Nadia", "Oskar", "Petra"]
SHIFTS = ["MORNING", "AFTERNOON", "NIGHT"]
ALIASES = {
    "MORNING": {"morning", "am", "a.m.", "early", "first", "mornings"},
    "AFTERNOON": {"afternoon", "pm", "p.m.", "day", "mid", "middle", "second", "afternoons"},
    "NIGHT": {"night", "late", "overnight", "third", "evening", "nights"},
}
_ALIAS_TO_SHIFT = {a: s for s, al in ALIASES.items() for a in al}
for _s in SHIFTS:
    _ALIAS_TO_SHIFT[_s.lower()] = _s

K_LEVELS = [3, 5, 7, 9]           # the difficulty dial, pre-registered as "constraint count"
ITEMS_PER_LEVEL = 12

PROMPT = """Assign each of the following people to exactly one shift: MORNING, AFTERNOON or NIGHT.

People: {people}

All of the following must hold at the same time:
{constraints}

Output ONLY the roster, one person per line, in the form: Name: SHIFT

Do not add commentary before or after the roster."""


# ---------------------------------------------------------------------------------------------
# Constraint model. Each constraint is a dict with a "type" and is checked mechanically.
# ---------------------------------------------------------------------------------------------
def describe(c):
    t = c["type"]
    if t == "exactly":
        return "Exactly %d %s on %s." % (c["n"], "person" if c["n"] == 1 else "people", c["shift"])
    if t == "at_least":
        return "At least %d %s on %s." % (c["n"], "person" if c["n"] == 1 else "people", c["shift"])
    if t == "must":
        return "%s must be on %s." % (c["who"], c["shift"])
    if t == "cannot":
        return "%s cannot be on %s." % (c["who"], c["shift"])
    if t == "apart":
        return "%s and %s must not be on the same shift." % (c["a"], c["b"])
    if t == "together":
        return "%s and %s must be on the same shift." % (c["a"], c["b"])
    raise ValueError(t)


def holds(c, roster):
    """roster: {name: SHIFT}. Returns True if the constraint holds."""
    t = c["type"]
    if t == "exactly":
        return sum(1 for s in roster.values() if s == c["shift"]) == c["n"]
    if t == "at_least":
        return sum(1 for s in roster.values() if s == c["shift"]) >= c["n"]
    if t == "must":
        return roster.get(c["who"]) == c["shift"]
    if t == "cannot":
        return roster.get(c["who"]) not in (None, c["shift"])
    if t == "apart":
        return c["a"] in roster and c["b"] in roster and roster[c["a"]] != roster[c["b"]]
    if t == "together":
        return c["a"] in roster and c["b"] in roster and roster[c["a"]] == roster[c["b"]]
    raise ValueError(t)


def derive_constraints(roster, k, rng):
    """Draw k distinct constraints that the given roster satisfies. Mixed types, so a model
    cannot succeed on one heuristic. Duplicates and trivially-implied pairs are avoided."""
    people = list(roster)
    out, seen = [], set()
    attempts = 0
    while len(out) < k and attempts < 500:
        attempts += 1
        t = rng.choice(["exactly", "at_least", "must", "cannot", "apart", "apart", "together"])
        if t in ("exactly", "at_least"):
            shift = rng.choice(SHIFTS)
            n = sum(1 for s in roster.values() if s == shift)
            if t == "at_least":
                n = max(1, n - rng.choice([0, 1]))
            c = {"type": t, "shift": shift, "n": n}
            key = (t, shift)
        elif t == "must":
            who = rng.choice(people)
            c = {"type": t, "who": who, "shift": roster[who]}
            key = ("person", who)
        elif t == "cannot":
            who = rng.choice(people)
            other = rng.choice([s for s in SHIFTS if s != roster[who]])
            c = {"type": t, "who": who, "shift": other}
            key = ("person", who)
        else:
            a, b = rng.sample(people, 2)
            same = roster[a] == roster[b]
            if t == "together" and not same:
                continue
            if t == "apart" and same:
                continue
            c = {"type": t, "a": a, "b": b}
            key = ("pair", tuple(sorted((a, b))))
        if key in seen:
            continue
        # an "exactly" and an "at_least" on the same shift would be redundant
        if t in ("exactly", "at_least") and (("exactly", c["shift"]) in seen or
                                              ("at_least", c["shift"]) in seen):
            continue
        assert holds(c, roster), "generator produced a constraint its own roster violates"
        seen.add(key)
        out.append(c)
    if len(out) < k:
        return None
    return out


def build_items(seed=20260901):
    rng = random.Random(seed)
    items = []
    for k in K_LEVELS:
        made = 0
        while made < ITEMS_PER_LEVEL:
            n_people = rng.choice([6, 7, 8, 9]) if k >= 7 else rng.choice([5, 6, 7])
            people = rng.sample(PEOPLE_POOL, n_people)
            # every shift gets at least one person, so the roster is not degenerate
            shifts = [rng.choice(SHIFTS) for _ in people]
            for i, s in enumerate(SHIFTS):
                shifts[i] = s
            rng.shuffle(shifts)
            roster = dict(zip(people, shifts))
            cons = derive_constraints(roster, k, rng)
            if cons is None:
                continue
            items.append({
                "family": FAMILY, "name": NAME,
                "item_id": "f08_k%d_%02d" % (k, made),
                "k": k,
                "people": people,
                "constraints": cons,
                "constraints_text": [describe(c) for c in cons],
                "prompt": PROMPT.format(
                    people=", ".join(people),
                    constraints="\n".join("- " + describe(c) for c in cons)),
                "generator_roster": roster,     # ONE valid solution, NOT the only one
                "equivalence_note": "Any roster satisfying every constraint scores EXACT. Shift "
                                    "aliases (AM/PM/early/late/overnight...) and any line "
                                    "format that pairs a name with a shift are accepted.",
            })
            made += 1
    rng.shuffle(items)
    return items


# ---------------------------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------------------------
_PAIR_RE = re.compile(r"^\s*[-*•\d.)]*\s*([A-Za-z]+)\s*[:\-–—=]\s*([A-Za-z. ]+?)\s*(?:\(.*\))?\s*$")
_REV_RE = re.compile(r"^\s*[-*•]*\s*([A-Za-z. ]+?)\s*[:\-–—=]\s*(.+)$")


def _shift_of(token):
    t = canon_text(token).lower().strip(" .")
    t = re.sub(r"\bshift\b", "", t).strip()
    return _ALIAS_TO_SHIFT.get(t)


def parse_roster(text, people):
    """Returns (roster, n_parsed_lines, prose_lines, dup_names)."""
    roster, dups, prose = {}, [], 0
    known = {p.lower(): p for p in people}
    for raw in (text or "").splitlines():
        line = raw.strip().strip("`")
        if not line or set(line) <= set("-=_*|"):
            continue
        m = _PAIR_RE.match(line)
        if m and m.group(1).lower() in known and _shift_of(m.group(2)):
            name, shift = known[m.group(1).lower()], _shift_of(m.group(2))
            if name in roster and roster[name] != shift:
                dups.append(name)
            roster[name] = shift
            continue
        m = _REV_RE.match(line)                     # "NIGHT: Amara, Bao"
        if m and _shift_of(m.group(1)):
            shift = _shift_of(m.group(1))
            names = [x.strip() for x in re.split(r"[,&]|\band\b", m.group(2))]
            hit = False
            for nm in names:
                nm = nm.strip(" .")
                if nm.lower() in known:
                    name = known[nm.lower()]
                    if name in roster and roster[name] != shift:
                        dups.append(name)
                    roster[name] = shift
                    hit = True
            if hit:
                continue
        prose += 1
    return roster, dups, prose


def score(response, item):
    txt = (response or "").strip()
    if not txt:
        return ("MALFORMED", "empty response")
    people = item["people"]
    roster, dups, prose = parse_roster(txt, people)

    if not roster:
        if len(txt) < 300 and "?" in txt:
            return ("META", "no roster; a question instead")
        return ("MALFORMED" if len(txt) >= 300 else "META", "no parseable Name: SHIFT lines")

    missing = [p for p in people if p not in roster]
    if missing:
        return ("UNDER", {"unassigned": missing, "assigned": len(roster), "of": len(people)})
    if dups:
        return ("WRONG", {"assigned_to_more_than_one_shift": sorted(set(dups))})

    violated = [describe(c) for c in item["constraints"] if not holds(c, roster)]
    n_hold = len(item["constraints"]) - len(violated)
    if violated:
        # §4.2: "score = how many hold" -- reported in the detail; the bucket is WRONG because
        # the roster does not meet the brief. Error dominates style.
        return ("WRONG", {"constraints_holding": n_hold, "of": len(item["constraints"]),
                          "violated": violated})
    if prose:
        return ("OVER_BENIGN", {"constraints_holding": n_hold, "of": n_hold,
                                "extra_prose_lines": prose})
    return ("EXACT", {"constraints_holding": n_hold, "of": n_hold})


# ---------------------------------------------------------------------------------------------
# Controls
# ---------------------------------------------------------------------------------------------
def self_test():
    items = build_items()
    bad = 0

    # ⛔ SATISFIABILITY: the generator's own roster must score EXACT on EVERY item. An
    #    unsatisfiable item would read as a capability ceiling and be our bug.
    for it in items:
        txt = "\n".join("%s: %s" % (p, s) for p, s in it["generator_roster"].items())
        got, d = score(txt, it)
        if got != "EXACT":
            bad += 1
            print("  FAIL  generator roster on %s scored %s %s" % (it["item_id"], got, d))

    it = items[0]
    R = it["generator_roster"]
    people = it["people"]

    def render(roster, fmt="{p}: {s}", order=None):
        ps = order or list(roster)
        return "\n".join(fmt.format(p=p, s=roster[p]) for p in ps)

    # a valid ALTERNATIVE roster that is not the generator's: flip two people who are
    # unconstrained relative to each other if we can find such a pair; otherwise skip.
    alt = None
    for a in people:
        for s in SHIFTS:
            if s == R[a]:
                continue
            cand = dict(R)
            cand[a] = s
            if all(holds(c, cand) for c in it["constraints"]):
                alt = cand
                break
        if alt:
            break

    perfect = render(R)
    cases = [
        ("EXACT", perfect, "canonical"),
        ("EXACT", render(R, "{p} - {s}"), "dash separator"),
        ("EXACT", render(R, "- {p}: {s}").lower(), "list markers, lowercase"),
        ("EXACT", render({p: {"MORNING": "AM", "AFTERNOON": "PM", "NIGHT": "overnight"}[s]
                          for p, s in R.items()}), "shift aliases"),
        ("EXACT", render(R, order=list(reversed(people))), "different line order"),
        ("EXACT", "```\n" + perfect + "\n```", "fenced"),
        ("OVER_BENIGN", perfect + "\n\nThis satisfies all constraints.", "trailing explanation"),
        ("UNDER", "\n".join(perfect.splitlines()[:-1]), "one person unassigned"),
        ("META", "Should NIGHT count as the shift after midnight?", "question"),
        ("MALFORMED", "", "empty"),
    ]
    if alt:
        cases.append(("EXACT", render(alt), "a DIFFERENT valid roster (not the generator's)"))

    # a roster that violates exactly the first constraint
    c0 = it["constraints"][0]
    broken = dict(R)
    if c0["type"] == "must":
        broken[c0["who"]] = [s for s in SHIFTS if s != c0["shift"]][0]
    elif c0["type"] == "cannot":
        broken[c0["who"]] = c0["shift"]
    elif c0["type"] == "together":
        broken[c0["a"]] = [s for s in SHIFTS if s != R[c0["b"]]][0]
    elif c0["type"] == "apart":
        broken[c0["a"]] = R[c0["b"]]
    else:  # exactly / at_least: move someone off that shift, or pile everyone on
        on = [p for p in people if R[p] == c0["shift"]]
        off = [p for p in people if R[p] != c0["shift"]]
        if c0["type"] == "exactly" and off:
            broken[off[0]] = c0["shift"]
        elif on:
            broken[on[0]] = [s for s in SHIFTS if s != c0["shift"]][0]
    if not holds(c0, broken):
        cases.append(("WRONG", render(broken), "violates constraint: " + describe(c0)))
    cases.append(("WRONG", perfect + "\n%s: %s" % (people[0],
                  [s for s in SHIFTS if s != R[people[0]]][0]), "one person on two shifts"))

    for want, resp, label in cases:
        got, detail = score(resp, it)
        if got != want:
            bad += 1
            print("  FAIL  %-44s want=%-12s got=%-12s %s" % (label, want, got, str(detail)[:60]))

    emitted = {score(r, it)[0] for _w, r, _l in cases}
    for req in ("EXACT", "UNDER", "WRONG", "OVER_BENIGN", "META", "MALFORMED"):
        if req not in emitted:
            bad += 1
            print("  FAIL  scorer never emitted %s in controls" % req)

    ks = {}
    for i in items:
        ks[i["k"]] = ks.get(i["k"], 0) + 1
    print("\n  items generated : %d  (per K: %s)" % (len(items), ks))
    print("  people per item : %s" % sorted({len(i['people']) for i in items}))
    print("  generator roster scores EXACT on every item (satisfiability)")
    print("  alternative valid roster tested: %s" % ("yes" if alt else "no pair found on item 0"))
    if bad:
        print("\n!! FAMILY 08 CONTROLS FAILED (%d). Per F1/§5.3 this family DOES NOT SHIP." % bad)
        return False
    print("  controls        : %d/%d pass + satisfiability on all items + bucket reachability"
          % (len(cases), len(cases)))
    return True


if __name__ == "__main__":
    if "--emit" in sys.argv:
        out = sys.argv[sys.argv.index("--emit") + 1]
        with open(out, "w", encoding="utf-8") as f:
            json.dump({"family": FAMILY, "name": NAME, "seed": 20260901,
                       "synthetic_only": True, "frontier_favouring": True,
                       "difficulty_dial": "k = number of simultaneous constraints (3/5/7/9)",
                       "items": build_items()}, f, indent=2, ensure_ascii=False)
        print("wrote %s" % out)
        sys.exit(0)
    sys.exit(0 if self_test() else 1)
