#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
family01_recipe_scaling.py -- generator + scorer for the recipe-scaling family.

📅 THIS FAMILY HAS BEEN REBUILT ONCE ALREADY, BECAUSE ITS ORIGINAL PREMISE WAS FALSE.
   The first version planted a trap: "cooking time and oven temperature do not scale," and any
   model that adjusted them was scored as over-helpful. `moonshotai/kimi-k3` showed during the
   consent round that this is simply not true --

       "double a cake batter in the same pan and the deeper layer genuinely changes the bake"

   -- so a model with BETTER baking knowledge than the item-writer would have been marked wrong,
   and marked wrong in the direction that MANUFACTURES H1. Our own conflict-of-interest section
   names that as the failure mode that flatters an LLM author writing about LLM capability.

🚨 AND BUILDING THE ITEMS FOUND A SECOND PROBLEM WITH THE FIX ITSELF.
   The amended pre-registration said "geometry-invariant items -- soups, sauces, drinks, brines."
   **Soups and sauces still have a cooking time.** Doubling a stock in the same pot changes the
   evaporation rate and therefore the reduction time. So "geometry-invariant COOKING" still
   smuggles in a disputable claim, just a smaller one.

   ✅ **Tightened to NO-COOK preparations only** -- vinaigrettes, brines, spice blends, drinks,
      marinades, simple syrups. There is no cooking step, so the question "does time scale?"
      DOES NOT ARISE, rather than being answered in a way a knowledgeable model could dispute.
      The measurement is arithmetic on quantities, with no thermal physics anywhere near it.

   ⭐ This is exactly why the items were built BEFORE the pre-registration was frozen. Found now,
      it is an amendment. Found after the hash, it is a deviation.

Usage:
    python family01_recipe_scaling.py --self-test
    python family01_recipe_scaling.py --emit items_family01.json
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
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from equivalence import (parse_quantity, quantities_equal, canon_text,   # noqa: E402
                         parse_ingredient_line, ingredient_lines_equal)

FAMILY = 1
NAME = "recipe_scaling"

# --------------------------------------------------------------------------------------------
# ⛔ NO-COOK ONLY. If a preparation has a cooking step, it does not belong in this family.
#    Amounts are stored as (numerator, denominator, unit, ingredient) so the ground truth is
#    exact rational arithmetic, never float.
# --------------------------------------------------------------------------------------------
RECIPES = [
    ("Classic vinaigrette", [
        ((3, 1), "tbsp", "olive oil"), ((1, 1), "tbsp", "red wine vinegar"),
        ((1, 2), "tsp", "Dijon mustard"), ((1, 4), "tsp", "salt"),
        ((1, 8), "tsp", "black pepper"),
    ]),
    ("Basic wet brine", [
        ((4, 1), "cup", "water"), ((1, 4), "cup", "kosher salt"),
        ((2, 1), "tbsp", "sugar"), ((3, 1), "clove", "garlic"), ((2, 1), "sprig", "thyme"),
    ]),
    ("All-purpose spice rub", [
        ((2, 1), "tbsp", "smoked paprika"), ((1, 1), "tbsp", "brown sugar"),
        ((2, 1), "tsp", "garlic powder"), ((1, 1), "tsp", "ground cumin"),
        ((1, 2), "tsp", "cayenne"),
    ]),
    ("Lemonade base", [
        ((1, 1), "cup", "lemon juice"), ((3, 4), "cup", "sugar"), ((4, 1), "cup", "cold water"),
        ((1, 8), "tsp", "salt"),
    ]),
    ("Simple syrup", [
        ((1, 1), "cup", "sugar"), ((1, 1), "cup", "water"),
    ]),
    ("Overnight oats", [
        ((1, 2), "cup", "rolled oats"), ((1, 2), "cup", "milk"),
        ((2, 1), "tbsp", "yoghurt"), ((1, 1), "tsp", "maple syrup"),
        ((1, 4), "tsp", "vanilla extract"),
    ]),
    ("Guacamole", [
        ((2, 1), "cup", "mashed avocado"), ((1, 4), "cup", "diced onion"),
        ((2, 1), "tbsp", "lime juice"), ((1, 2), "tsp", "salt"),
        ((1, 1), "tbsp", "chopped coriander"),
    ]),
    ("Cucumber salad dressing", [
        ((1, 2), "cup", "yoghurt"), ((1, 1), "tbsp", "lemon juice"),
        ((1, 1), "tsp", "honey"), ((1, 4), "tsp", "ground cumin"),
        ((1, 8), "tsp", "salt"),
    ]),
    ("Iced tea concentrate", [
        ((6, 1), "cup", "brewed tea"), ((1, 2), "cup", "sugar"),
        ((1, 4), "cup", "lemon juice"), ((6, 1), "sprig", "mint"),
    ]),
    ("Pickling liquid", [
        ((2, 1), "cup", "white vinegar"), ((2, 1), "cup", "water"),
        ((3, 1), "tbsp", "sugar"), ((2, 1), "tbsp", "salt"), ((1, 1), "tsp", "mustard seed"),
    ]),
    ("Smoothie base", [
        ((1, 1), "cup", "frozen berries"), ((3, 4), "cup", "milk"),
        ((1, 2), "cup", "yoghurt"), ((1, 1), "tbsp", "honey"),
    ]),
    ("Marinade for tofu", [
        ((1, 4), "cup", "soy sauce"), ((2, 1), "tbsp", "sesame oil"),
        ((1, 1), "tbsp", "rice vinegar"), ((2, 1), "clove", "garlic"),
        ((1, 2), "tsp", "grated ginger"),
    ]),
]

# Non-integer on purpose: integer factors let a model succeed by copying and doubling.
FACTORS = [Fraction(3, 2), Fraction(5, 2), Fraction(3, 4), Fraction(5, 4),
           Fraction(1, 2), Fraction(7, 2), Fraction(2, 3), Fraction(4, 3)]

PROMPT = """Scale this recipe by {factor_str}.

{recipe}

Output ONLY the scaled ingredient list, one ingredient per line, in the original order, in the
form: amount unit ingredient

Do not add commentary before or after the list."""


def fmt_amount(fr):
    """Render a Fraction the way a recipe would: 2, 1 1/2, 3/4."""
    if fr.denominator == 1:
        return str(fr.numerator)
    whole, rem = divmod(fr.numerator, fr.denominator)
    if whole:
        return "%d %d/%d" % (whole, rem, fr.denominator)
    return "%d/%d" % (fr.numerator, fr.denominator)


def fmt_factor(fr):
    return {Fraction(3, 2): "1.5x", Fraction(5, 2): "2.5x", Fraction(3, 4): "0.75x",
            Fraction(5, 4): "1.25x", Fraction(1, 2): "half", Fraction(7, 2): "3.5x",
            Fraction(2, 3): "two-thirds", Fraction(4, 3): "1 1/3x"}.get(fr, "%sx" % fr)


# 🚨 MAXIMUM GROUND-TRUTH DENOMINATOR. Found by inspecting generated items, not by theory:
#    scaling 1/8 tsp by 3/4 yields **3/32 tsp black pepper**, which is not a measurement any
#    kitchen contains. A sensible model would round it -- and rounding would score WRONG.
#    ⛔ That is the SAME DEFECT as the cooking-time trap kimi-k3 killed: penalising a model for
#       being more sensible than the item-writer, in the direction that manufactures H1.
#    ✅ So (recipe, factor) pairs whose exact result needs a denominator finer than 1/8 are not
#       generated at all. We do not ask a question whose correct answer is absurd and then score
#       the sensible answer as an error.
MAX_DENOMINATOR = 8


def build_items(seed=20260820):
    """Deterministic. The seed is the ground truth's provenance and is published."""
    rng = random.Random(seed)
    items = []
    skipped = []
    for ri, (title, ingredients) in enumerate(RECIPES):
        for factor in FACTORS:
            scaled = [Fraction(n, d) * factor for (n, d), _u, _name in ingredients]
            worst = max(x.denominator for x in scaled)
            if worst > MAX_DENOMINATOR:
                skipped.append((title, str(factor), worst))
                continue
            src = "\n".join("%s %s %s" % (fmt_amount(Fraction(n, d)), u, name)
                            for (n, d), u, name in ingredients)
            truth = [{"amount": fmt_amount(Fraction(n, d) * factor), "unit": u,
                      "ingredient": name} for (n, d), u, name in ingredients]
            items.append({
                "family": FAMILY, "name": NAME,
                "item_id": "f01_%02d_%s" % (ri, str(factor).replace("/", "_")),
                "recipe_title": title,
                "factor": [factor.numerator, factor.denominator],
                "prompt": PROMPT.format(factor_str=fmt_factor(factor),
                                        recipe="%s\n\n%s" % (title, src)),
                "ground_truth": truth,
                "no_cook": True,
            })
    rng.shuffle(items)
    if skipped:
        # ⛔ NO SILENT TRUNCATION. A generator that quietly drops combinations reads as
        #    "we covered everything" when it did not. State what was excluded and why.
        print("  [f01] skipped %d (recipe, factor) pair(s) needing a denominator > 1/%d:"
              % (len(skipped), MAX_DENOMINATOR))
        for title, fac, worst in skipped[:6]:
            print("        %-28s x%-5s -> 1/%d" % (title, fac, worst))
        if len(skipped) > 6:
            print("        ... and %d more" % (len(skipped) - 6))
    return items


# --------------------------------------------------------------------------------------------
# Scoring
# --------------------------------------------------------------------------------------------

def parse_response_lines(text):
    """Take the ingredient lines out of a response, tolerating list markers and stray prose."""
    out = []
    for raw in (text or "").splitlines():
        s = canon_text(raw)
        if not s:
            continue
        s = s.lstrip("-*•").strip()
        s = __import__("re").sub(r"^\d+[.)]\s+", "", s)   # numbered lists
        amount, unit = parse_quantity(s)
        if amount is None:
            continue                                       # prose line, not an ingredient
        out.append(s)
    return out


def score(response, item):
    """Return (bucket, detail).

    ⭐ A CORRECT CAVEAT IS NOT AN ERROR. Per the amendment, a model that notes something true
       about the preparation has not failed the task. Because this family is NO-COOK, the
       question does not arise for cooking time -- but the principle still binds: extra CORRECT
       content is OVER_BENIGN, which does not count against a model. Only content that makes
       the deliverable unusable is OVER_HARMFUL.
    """
    truth = item["ground_truth"]
    lines = parse_response_lines(response)

    if not lines:
        return ("META" if (response or "").strip() else "MALFORMED",
                "no parseable ingredient lines")
    if len(lines) < len(truth):
        return ("UNDER", "%d of %d ingredients" % (len(lines), len(truth)))

    wrong = []
    for i, exp in enumerate(truth):
        if i >= len(lines):
            break
        want = "%s %s %s" % (exp["amount"], exp["unit"], exp["ingredient"])
        if not ingredient_lines_equal(lines[i], want):
            n, u, ing = parse_ingredient_line(lines[i])
            wrong.append({"index": i, "want": want, "got": lines[i],
                          "got_parsed": [str(n), u, ing]})

    if wrong:
        # ⛔ PRECEDENCE (§5.1): a wrong value dominates any style consideration. A response that
        #    is both over-elaborate and numerically wrong is WRONG, never OVER_*.
        return ("WRONG", wrong)

    extra = len(lines) - len(truth)
    if extra > 0:
        return ("OVER_BENIGN", "%d extra parseable line(s); all required values correct" % extra)

    prose = [l for l in (response or "").splitlines()
             if canon_text(l) and parse_quantity(canon_text(l))[0] is None]
    if prose:
        return ("OVER_BENIGN", "%d line(s) of added commentary; all values correct" % len(prose))

    return ("EXACT", None)


# --------------------------------------------------------------------------------------------
# Controls  (§5.3 -- run BEFORE the scorer sees any model output)
# --------------------------------------------------------------------------------------------

def _as_decimal(amount_str):
    """Render '2 1/4' as '2.25' for the adversarial control.

    Uses our own parser rather than a hand-rolled one: if the parser is wrong, the control
    should fail loudly here rather than quietly test something else. Repeating fractions
    (1/3) are left as-is -- a truncated decimal is genuinely a DIFFERENT number, and pretending
    otherwise would be the scorer widening itself to make wrong answers look right.
    """
    fr = parse_quantity(amount_str)[0]
    if fr is None:
        return amount_str
    if 10 ** 6 % fr.denominator != 0:      # not exactly representable in decimal
        return amount_str
    return ("%f" % float(fr)).rstrip("0").rstrip(".")


def self_test():
    items = build_items()
    item = next(i for i in items if i["item_id"].startswith("f01_00_"))
    truth = item["ground_truth"]

    def as_lines(fmt):
        return "\n".join(fmt(t) for t in truth)

    perfect = as_lines(lambda t: "%s %s %s" % (t["amount"], t["unit"], t["ingredient"]))

    cases = [
        # ✅ adversarial equivalence -- textually different, semantically identical -> EXACT
        ("EXACT", perfect, "canonical"),
        ("EXACT", as_lines(lambda t: "- %s %s %s" % (t["amount"], t["unit"], t["ingredient"])),
         "bullet markers"),
        ("EXACT", "\n".join("%d. %s %s %s" % (i + 1, t["amount"], t["unit"], t["ingredient"])
                            for i, t in enumerate(truth)), "numbered list"),
        ("EXACT", as_lines(lambda t: "%s %s %s" % (
            t["amount"], {"tbsp": "tablespoons", "tsp": "teaspoons", "cup": "cups",
                          "clove": "cloves", "sprig": "sprigs"}.get(t["unit"], t["unit"]),
            t["ingredient"])), "unit spelled out"),
        ("EXACT", as_lines(lambda t: "%s %s %s" % (
            _as_decimal(t["amount"]), t["unit"], t["ingredient"])), "decimal amounts"),
        # ⛔ negative controls -- the scorer must be ABLE to emit each bucket
        ("WRONG", perfect.replace(truth[0]["amount"], "99", 1), "one value corrupted"),
        ("UNDER", "\n".join(perfect.splitlines()[:-1]), "one ingredient missing"),
        ("META", "Sure! Which serving size would you like?", "question instead of deliverable"),
        ("MALFORMED", "", "empty response"),
        ("OVER_BENIGN", perfect + "\nNote: this is a no-cook preparation, so nothing changes "
                                  "besides the quantities.", "correct added commentary"),
    ]

    bad = 0
    for want, resp, label in cases:
        got, detail = score(resp, item)
        if got != want:
            bad += 1
            print("  FAIL  %-28s want=%-12s got=%-12s %s" % (label, want, got, detail))

    # A scorer that cannot emit a bucket would report a flat, clean, entirely false curve for it.
    emitted = {score(r, item)[0] for _, r, _ in cases}
    for required in ("EXACT", "WRONG", "UNDER", "META", "MALFORMED", "OVER_BENIGN"):
        if required not in emitted:
            bad += 1
            print("  FAIL  scorer never emitted %s in controls" % required)

    # ⛔ Do NOT print "N recipes x M factors" next to a count that is neither -- a caption that
    #    contradicts its own number is how a filtered set passes as a complete one.
    print("\n  items generated : %d of %d possible (%d recipes x %d factors, minus the pairs "
          "excluded above)" % (len(items), len(RECIPES) * len(FACTORS),
                               len(RECIPES), len(FACTORS)))
    print("  no-cook only    : %s" % all(i["no_cook"] for i in items))
    if bad:
        print("\n!! FAMILY 01 CONTROLS FAILED (%d). Per F1/§5.3 this family DOES NOT SHIP." % bad)
        return False
    print("  controls        : %d/%d pass, all buckets reachable" % (len(cases), len(cases)))
    return True


if __name__ == "__main__":
    if "--emit" in sys.argv:
        out = sys.argv[sys.argv.index("--emit") + 1]
        with open(out, "w", encoding="utf-8") as f:
            json.dump({"family": FAMILY, "name": NAME, "seed": 20260820,
                       "no_cook_only": True, "items": build_items()}, f, indent=2)
        print("wrote %s" % out)
        sys.exit(0)
    sys.exit(0 if self_test() else 1)
