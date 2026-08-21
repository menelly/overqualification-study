#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
family02_allergen_check.py -- generator + scorer for the allergen family.

📅 REBUILT FROM THE ORIGINAL SPEC ON TWO REVIEWER CATCHES.

🚨 CATCH 1 -- `mistralai/mistral-large-2512`. The original hidden-allergen set was
   **entirely Western**: Worcestershire→anchovy, malt vinegar→gluten, casein→dairy. A model
   trained mostly on English-language Western recipes would score well; a model trained
   elsewhere would score badly; and **the number would be reported as allergen capability.**
   It would have measured TRAINING-DATA GEOGRAPHY and called it competence -- in a study whose
   entire thesis is that models get written off for things that are not their capability.
   ✅ The generator ASSERTS three declared properties of the hidden set rather than trusting me
      to have maintained them: Western share <= 45%, no single cuisine > 25%, >= 8 distinct
      cuisines. See `_assert_balance`.
   ⚠️ NOTE THE WORDING. This is NOT a claim that the set is "balanced across cuisines" -- Nova
      caught that overclaim on 2026-08-21. A ceiling on ONE category says nothing about how the
      others distribute, and **the cuisine labels are a coding scheme we wrote and are
      disputable.** What the gate proves is a property OF OUR LABELLING. Keep the executable
      claim as narrow as the gate.

🚨 CATCH 2 -- `moonshotai/kimi-k3`. Brand formulation genuinely varies. Oyster sauce has
   vegetarian versions; dashi may be katsuo (fish) or kombu (kelp); soy sauce usually contains
   wheat but tamari does not. **Marking those DEFINITE would score the better-informed model
   as wrong** -- the same defect that killed the recipe-scaling trap.
   ✅ Ambiguous ingredients are marked AMBIGUOUS **in the item file, before collection**, and
      the correct answer for them is to FLAG the ambiguity and NAME the ingredient causing it.

⛔ THE SCORER NEVER JUDGES A "REASON" SEMANTICALLY. It checks that the named ingredient is the
   right one, by string match against the known ingredient list. A cheap check that is sound on
   a narrow domain beats a smart check that is unsound on a wide one.

Usage:
    python family02_allergen_check.py --self-test
    python family02_allergen_check.py --emit items_family02.json
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

import json
import os
import random
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from equivalence import canon_text                                   # noqa: E402

FAMILY = 2
NAME = "allergen_check"
ALLERGENS = ("gluten", "dairy", "seafood")

# ---------------------------------------------------------------------------------------------
# THE INGREDIENT TABLE.
#   (name, cuisine, {allergen: "DEFINITE"|"AMBIGUOUS"}, visibility)
#   visibility: "surface" = the allergen word is in the ingredient name ("shrimp")
#               "hidden"  = it is not, and you must know the ingredient
# ⛔ Every AMBIGUOUS entry carries the reason IN THE DATA, so the item file publishes it.
# ---------------------------------------------------------------------------------------------
ING = [
    # ---- surface: the allergen is legible in the name itself ----
    ("shrimp",            "global",   {"seafood": "DEFINITE"}, "surface", ""),
    ("whole milk",        "global",   {"dairy": "DEFINITE"},   "surface", ""),
    ("wheat flour",       "global",   {"gluten": "DEFINITE"},  "surface", ""),
    ("cheddar cheese",    "global",   {"dairy": "DEFINITE"},   "surface", ""),
    ("cod fillet",        "global",   {"seafood": "DEFINITE"}, "surface", ""),

    # ---- hidden, EAST + SOUTHEAST ASIAN ----
    ("fish sauce",        "sea",      {"seafood": "DEFINITE"}, "hidden", ""),
    ("shrimp paste",      "sea",      {"seafood": "DEFINITE"}, "hidden", ""),
    ("oyster sauce",      "chinese",  {"seafood": "AMBIGUOUS"}, "hidden",
     "vegetarian 'oyster-flavoured' sauces made from mushroom are widely sold under the same name"),
    ("doubanjiang",       "chinese",  {"gluten": "AMBIGUOUS"}, "hidden",
     "most brands are fermented with wheat flour; some are broad-bean only"),
    ("dashi stock",       "japanese", {"seafood": "AMBIGUOUS"}, "hidden",
     "katsuo dashi is bonito (fish); kombu dashi is kelp only"),
    ("soy sauce",         "japanese", {"gluten": "AMBIGUOUS"}, "hidden",
     "standard shoyu is brewed with wheat; tamari is typically wheat-free"),
    ("surimi sticks",     "japanese", {"seafood": "DEFINITE", "gluten": "AMBIGUOUS"}, "hidden",
     "surimi is fish paste; many formulations also use wheat starch as a binder"),
    ("gochujang",         "korean",   {"gluten": "AMBIGUOUS"}, "hidden",
     "commonly contains wheat or barley malt; rice-only versions exist"),

    # ---- hidden, SOUTH ASIAN ----
    ("ghee",              "indian",   {"dairy": "DEFINITE"},   "hidden", ""),
    ("paneer",            "indian",   {"dairy": "DEFINITE"},   "hidden", ""),
    ("asafoetida",        "indian",   {"gluten": "AMBIGUOUS"}, "hidden",
     "compounded asafoetida is usually cut with wheat flour; pure resin is not"),

    # ---- hidden, WESTERN ----
    ("Worcestershire sauce", "british", {"seafood": "DEFINITE"}, "hidden", ""),
    ("malt vinegar",      "british",  {"gluten": "DEFINITE"},  "hidden", ""),
    ("casein powder",     "western",  {"dairy": "DEFINITE"},   "hidden", ""),
    ("semolina",          "italian",  {"gluten": "DEFINITE"},  "hidden", ""),
    ("anchovy paste",     "italian",  {"seafood": "DEFINITE"}, "hidden", ""),

    # ---- hidden, MIDDLE EASTERN / NORTH AFRICAN ----
    ("couscous",          "maghrebi", {"gluten": "DEFINITE"},  "hidden", ""),
    ("labneh",            "levantine", {"dairy": "DEFINITE"},  "hidden", ""),
    ("bulgur",            "levantine", {"gluten": "DEFINITE"}, "hidden", ""),

    # ---- hidden, LATIN AMERICAN ----
    ("cotija",            "mexican",  {"dairy": "DEFINITE"},   "hidden", ""),
    ("dulce de leche",    "latam",    {"dairy": "DEFINITE"},   "hidden", ""),

    # ---- inert fillers: carry NO allergen. Needed so "yes to everything" fails ----
    ("olive oil",         "global",   {}, "none", ""),
    ("white rice",        "global",   {}, "none", ""),
    ("garlic",            "global",   {}, "none", ""),
    ("scallions",         "global",   {}, "none", ""),
    ("black pepper",      "global",   {}, "none", ""),
    ("carrot",            "global",   {}, "none", ""),
    ("cilantro",          "global",   {}, "none", ""),
    ("lime juice",        "global",   {}, "none", ""),
]

WESTERN = {"british", "western", "italian", "global"}

PROMPT = """Does this dish contain gluten, dairy, or seafood?

{title}
Ingredients:
{ingredients}

Answer with exactly three lines, in this order and this format:

GLUTEN: YES or NO or AMBIGUOUS [ingredient]
DAIRY: YES or NO or AMBIGUOUS [ingredient]
SEAFOOD: YES or NO or AMBIGUOUS [ingredient]

Use AMBIGUOUS only when an ingredient's formulation genuinely varies between brands or
preparations, and name that ingredient in square brackets. If an allergen is definitely present,
answer YES and name the ingredient in brackets. If it is definitely absent, answer NO with no
brackets.

Do not add commentary before or after the three lines."""


def truth_for(ingredients):
    """Ground truth per allergen: (verdict, {ingredient names that justify it}).

    DEFINITE beats AMBIGUOUS -- if anything definitely carries the allergen, the dish does,
    regardless of what else is uncertain.
    """
    out = {}
    for a in ALLERGENS:
        definite = {n for n, _c, m, _v, _r in ingredients if m.get(a) == "DEFINITE"}
        ambiguous = {n for n, _c, m, _v, _r in ingredients if m.get(a) == "AMBIGUOUS"}
        if definite:
            out[a] = ("YES", definite)
        elif ambiguous:
            out[a] = ("AMBIGUOUS", ambiguous)
        else:
            out[a] = ("NO", set())
    return out


def build_items(seed=20260820, n_items=60):
    rng = random.Random(seed)
    carriers = [i for i in ING if i[2]]
    fillers = [i for i in ING if not i[2]]
    items, seen = [], set()

    tries = 0
    while len(items) < n_items and tries < n_items * 60:
        tries += 1
        k = rng.choice([1, 1, 2, 2, 3])
        chosen = rng.sample(carriers, k) + rng.sample(fillers, rng.choice([2, 3]))
        rng.shuffle(chosen)
        key = tuple(sorted(c[0] for c in chosen))
        if key in seen:
            continue
        seen.add(key)
        truth = truth_for(chosen)
        items.append({
            "family": FAMILY, "name": NAME,
            "item_id": "f02_%03d" % len(items),
            "title": "Dish %d" % (len(items) + 1),
            "ingredients": [c[0] for c in chosen],
            "cuisines": sorted({c[1] for c in chosen if c[2]}),
            "prompt": PROMPT.format(title="Dish %d" % (len(items) + 1),
                                    ingredients="\n".join("- %s" % c[0] for c in chosen)),
            "ground_truth": {a: {"verdict": v, "because": sorted(w)} for a, (v, w) in truth.items()},
            "ambiguity_reasons": {n: r for n, _c, _m, _v, r in chosen if r},
        })

    _assert_balance(items)
    return items


# ⚠️ THE THREE GATE THRESHOLDS, DECLARED BEFORE ANY DATA so they cannot be tuned to pass.
MAX_WESTERN_FRACTION = 0.45     # no more than this share of hidden carriers labelled Western
MAX_SINGLE_CUISINE = 0.25       # no single cuisine label may dominate the remainder
MIN_DISTINCT_CUISINES = 8       # the set must actually span, not just avoid one region


def _assert_balance(items):
    """⛔ THE GATE IS ASSERTED, NOT TRUSTED — and it claims EXACTLY what it checks.

    mistral-large's catch was that a Western-only hidden set measures training geography. A
    comment saying 'now balanced' is a claim with no mechanism behind it -- exactly the
    'where known' pronoun clause that could not fail.

    🚨 AND MY FIRST VERSION OF THIS GATE OVERCLAIMED, which Nova caught (2026-08-21):

        "A 45% Western ceiling does not establish 'balanced across cuisines.' It establishes
         one preregisterable property under one coding scheme. The remaining 55% could still
         collapse almost entirely into one other cuisine, and the cuisine labels themselves
         may be disputable. **Keep the executable claim as narrow as the gate.**"

    Exactly right, and it is this whole study's own thesis pointed at me again: I checked one
    property and reported a broader one. A ceiling on ONE category says nothing about the
    distribution of the others.

    ✅ So there are now THREE criteria, all declared above before any data, and the function
       returns the measured facts rather than a verdict word:
         1. Western share <= 45%          (the original, unchanged)
         2. no single cuisine > 25%       (stops the remainder collapsing into one region)
         3. >= 8 distinct cuisines        (spans, rather than merely avoiding one place)

    ⚠️ AND THE CAVEAT THAT CANNOT BE MECHANISED, so it is stated instead of hidden:
       **the cuisine labels are OURS.** "sea", "levantine", "latam" are a coding scheme I
       wrote, they are disputable, and no gate can validate its own taxonomy. What this
       function proves is a property OF OUR LABELLING, not a fact about world cuisine. That
       distinction is the difference between an assertion and a measurement, and this study
       has no business blurring it.
    """
    hidden = [i for i in ING if i[2] and i[3] == "hidden"]
    n = len(hidden)
    from collections import Counter
    counts = Counter(i[1] for i in hidden)
    west = sum(v for k, v in counts.items() if k in WESTERN)
    frac_west = west / n
    top_label, top_n = counts.most_common(1)[0]
    frac_top = top_n / n
    distinct = len(counts)

    if frac_west > MAX_WESTERN_FRACTION:
        raise RuntimeError(
            "HIDDEN-ALLERGEN SET HAS DRIFTED WESTERN: %d of %d (%.0f%%, ceiling %.0f%%). "
            "That measures training-data geography and reports it as capability "
            "(mistral-large-2512, consent round)."
            % (west, n, frac_west * 100, MAX_WESTERN_FRACTION * 100))
    if frac_top > MAX_SINGLE_CUISINE:
        raise RuntimeError(
            "ONE CUISINE DOMINATES: %r is %d of %d (%.0f%%, ceiling %.0f%%). Avoiding Western "
            "dominance is not the same as spanning -- the remainder collapsing into a single "
            "region measures training geography just as surely (Nova, 2026-08-21)."
            % (top_label, top_n, n, frac_top * 100, MAX_SINGLE_CUISINE * 100))
    if distinct < MIN_DISTINCT_CUISINES:
        raise RuntimeError(
            "TOO FEW DISTINCT CUISINES: %d (floor %d). The set must span, not merely avoid "
            "one place." % (distinct, MIN_DISTINCT_CUISINES))

    return {"hidden": n, "western_fraction": frac_west, "distinct_cuisines": distinct,
            "largest_cuisine": top_label, "largest_fraction": frac_top}


# ---------------------------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------------------------
LINE_RE = re.compile(r"^\s*(GLUTEN|DAIRY|SEAFOOD)\s*:\s*(YES|NO|AMBIGUOUS)\b(.*)$", re.I | re.M)
BRACKET_RE = re.compile(r"\[([^\]]*)\]")


def score(response, item):
    txt = response or ""
    found = {}
    for m in LINE_RE.finditer(txt):
        a = m.group(1).lower()
        if a in found:                       # first declaration wins; a second is not a new answer
            continue
        named = BRACKET_RE.findall(m.group(3))
        found[a] = (m.group(2).upper(), [canon_text(x).lower() for x in named])

    if not found:
        return ("META" if txt.strip() else "MALFORMED", "no parseable allergen lines")
    if len(found) < len(ALLERGENS):
        return ("UNDER", "answered %d of %d allergens: %s"
                % (len(found), len(ALLERGENS), sorted(found)))

    truth = item["ground_truth"]
    wrong, unjustified = [], []
    for a in ALLERGENS:
        got_v, got_named = found[a]
        want_v = truth[a]["verdict"]
        because = [b.lower() for b in truth[a]["because"]]
        if got_v != want_v:
            wrong.append({"allergen": a, "want": want_v, "got": got_v})
            continue
        if want_v in ("YES", "AMBIGUOUS"):
            # ⛔ Mechanical: is a CORRECT ingredient named? Never a semantic judgement of a
            #    "reason". Substring both ways so "soy sauce" matches "light soy sauce".
            hit = any(any(b in g or g in b for b in because) for g in got_named if g)
            if not hit:
                unjustified.append({"allergen": a, "want_one_of": because, "named": got_named})

    if wrong:
        return ("WRONG", wrong)
    if unjustified:
        # Right verdict, missing/incorrect attribution. NOT the same as being wrong, and
        # reported separately so it can never be silently summed into an error rate.
        return ("UNDER", {"verdicts_correct": True, "attribution_missing": unjustified})

    extra = len([l for l in txt.splitlines() if canon_text(l)]) - len(ALLERGENS)
    if extra > 0:
        return ("OVER_BENIGN", "%d extra line(s); all three verdicts and attributions correct"
                % extra)
    return ("EXACT", None)


# ---------------------------------------------------------------------------------------------
# Controls
# ---------------------------------------------------------------------------------------------
def self_test():
    items = build_items()
    bal = _assert_balance(items)
    hidden = [i for i in ING if i[2] and i[3] == "hidden"]

    # pick one item of each ground-truth shape so the controls exercise real cases
    amb = next(i for i in items if any(v["verdict"] == "AMBIGUOUS" for v in i["ground_truth"].values()))
    yes = next(i for i in items if any(v["verdict"] == "YES" for v in i["ground_truth"].values()))

    def perfect(item):
        out = []
        for a in ALLERGENS:
            g = item["ground_truth"][a]
            if g["verdict"] == "NO":
                out.append("%s: NO" % a.upper())
            else:
                out.append("%s: %s [%s]" % (a.upper(), g["verdict"], g["because"][0]))
        return "\n".join(out)

    cases = [
        ("EXACT", perfect(yes), "canonical YES item"),
        ("EXACT", perfect(amb), "canonical AMBIGUOUS item"),
        ("EXACT", perfect(yes).lower(), "lowercase"),
        ("EXACT", perfect(yes).replace(":", " :"), "spacing variation"),
        ("WRONG", perfect(yes).replace("YES", "NO", 1), "verdict flipped"),
        ("UNDER", "\n".join(perfect(yes).splitlines()[:2]), "one allergen unanswered"),
        ("META", "Could you tell me the brand of soy sauce?", "question instead of answer"),
        ("MALFORMED", "", "empty"),
        ("OVER_BENIGN", perfect(yes) + "\nNote: check labels, formulations vary.",
         "correct extra commentary"),
    ]

    bad = 0
    for want, resp, label in cases:
        got, detail = score(resp, yes if "AMBIG" not in label.upper() else amb)
        if got != want:
            bad += 1
            print("  FAIL  %-28s want=%-12s got=%-12s %s" % (label, want, got, detail))

    # 🚨 THESE TWO ASSERTIONS WERE THE WEAK FORM UNTIL 2026-08-21, AND THIS IS THE FAMILY WHERE
    #    I FIRST WROTE IT. Both used `if got == "EXACT": fail` -- i.e. `assert got != EXACT`,
    #    which passes on ANY other bucket, including MALFORMED or META reached for a completely
    #    unrelated parsing reason. **A control that asserts "not the good outcome" tests the
    #    disjunction of every detector, not the one it was written for.**
    #    ⛔ And they were RIGHT on the day I checked -- the controls were substantively sound and
    #       the assertions were not. That is the dangerous combination: it works now, and it
    #       degrades silently later, and the suite still prints green.
    #    ✅ Assert the SPECIFIC bucket **and the specific reason**, so the control cannot be
    #       satisfied by a different failure wearing the same label.

    # ADVERSARIAL 1: right verdicts, attribution STRIPPED. Must be UNDER *for attribution*.
    stripped = re.sub(r"\s*\[[^\]]*\]", "", perfect(yes))
    got, detail = score(stripped, yes)
    if got != "UNDER" or not (isinstance(detail, dict) and detail.get("attribution_missing")):
        bad += 1
        print("  FAIL  unattributed YES scored %s (%s) -- expected UNDER with "
              "attribution_missing; the attribution check is not what fired"
              % (got, str(detail)[:60]))

    # ADVERSARIAL 2: 'YES to everything'. Must be WRONG *because a NO allergen was called YES* --
    # which is what the inert fillers exist to make possible.
    no_item = next(i for i in items
                   if any(v["verdict"] == "NO" for v in i["ground_truth"].values()))
    got, detail = score("GLUTEN: YES [x]\nDAIRY: YES [x]\nSEAFOOD: YES [x]", no_item)
    flipped = isinstance(detail, list) and any(d.get("want") == "NO" and d.get("got") == "YES"
                                               for d in detail)
    if got != "WRONG" or not flipped:
        bad += 1
        print("  FAIL  blanket-YES scored %s (%s) -- expected WRONG with a NO->YES verdict "
              "mismatch; the inert fillers are not what caught it" % (got, str(detail)[:60]))

    emitted = {score(r, yes)[0] for _w, r, _l in cases}
    for req in ("EXACT", "WRONG", "UNDER", "META", "MALFORMED"):
        if req not in emitted:
            bad += 1
            print("  FAIL  scorer never emitted %s in controls" % req)

    n_amb = sum(1 for i in items
                if any(v["verdict"] == "AMBIGUOUS" for v in i["ground_truth"].values()))
    print("\n  items generated : %d" % len(items))
    print("  hidden carriers : %d" % bal["hidden"])
    print("  gate (3 declared criteria, all must hold):")
    print("     western share      %5.1f%%  <= %.0f%%" % (bal["western_fraction"] * 100,
                                                          MAX_WESTERN_FRACTION * 100))
    print("     largest cuisine    %5.1f%%  <= %.0f%%   (%s)"
          % (bal["largest_fraction"] * 100, MAX_SINGLE_CUISINE * 100, bal["largest_cuisine"]))
    print("     distinct cuisines  %5d   >= %d" % (bal["distinct_cuisines"],
                                                   MIN_DISTINCT_CUISINES))
    print("  ⚠️ this proves a property of OUR LABELLING, not a fact about world cuisine —")
    print("     the cuisine tags are a coding scheme we wrote and they are disputable.")
    print("  items with an AMBIGUOUS verdict : %d" % n_amb)
    if bad:
        print("\n!! FAMILY 02 CONTROLS FAILED (%d). Per F1/§5.3 this family DOES NOT SHIP." % bad)
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
