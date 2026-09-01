#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
equivalence.py -- the canonicalisation layer. Shared by every task family and its scorer.

🚨 WHY THIS EXISTS, AND WHY IT IS NOT A CONVENIENCE. Three reviewers independently said that
   naive exact-match would measure OUR FORMATTING CONVENTIONS and report the result as
   capability:

     gpt-5.6-terra  -- publish canonicalisation rules per task, before any data
     kimi-k3        -- equivalent arithmetic forms must not be scored as errors
     qwen3-14b      -- `[REDACTED]` vs `███` measures string convention, not redaction

   A model that writes `0.5 cup` where our ground truth says `1/2 cup` has not made a mistake.
   Scoring it as one would mean the study's headline number was partly a measure of how closely
   each model happens to match the item-writer's house style.

⛔ THE HARD RULE (pre-registration §5.3): the scorer is fed semantically-identical-but-textually-
   different outputs and MUST return EXACT. **If it cannot, that family does not ship.** This
   module is where that becomes testable rather than aspirational.

📐 DESIGN CONSTRAINT: canonicalisation may only ever collapse forms that are *genuinely* the same
   value. It must never be broadened to make a wrong answer look right. Every widening here needs
   a negative control proving the thing it must still reject.

Run the controls:
    python equivalence.py --self-test
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

import re
import sys
import unicodedata
from fractions import Fraction

# --------------------------------------------------------------------------------------------
# Numbers
# --------------------------------------------------------------------------------------------

# Unicode vulgar fractions. Models emit these freely; our ground truth never does.
VULGAR = {
    "¼": Fraction(1, 4), "½": Fraction(1, 2), "¾": Fraction(3, 4),
    "⅐": Fraction(1, 7), "⅑": Fraction(1, 9), "⅒": Fraction(1, 10),
    "⅓": Fraction(1, 3), "⅔": Fraction(2, 3),
    "⅕": Fraction(1, 5), "⅖": Fraction(2, 5), "⅗": Fraction(3, 5), "⅘": Fraction(4, 5),
    "⅙": Fraction(1, 6), "⅚": Fraction(5, 6),
    "⅛": Fraction(1, 8), "⅜": Fraction(3, 8), "⅝": Fraction(5, 8), "⅞": Fraction(7, 8),
}

WORD_NUMBERS = {
    "a": Fraction(1), "an": Fraction(1), "one": Fraction(1), "two": Fraction(2),
    "three": Fraction(3), "four": Fraction(4), "five": Fraction(5), "six": Fraction(6),
    "seven": Fraction(7), "eight": Fraction(8), "nine": Fraction(9), "ten": Fraction(10),
    "eleven": Fraction(11), "twelve": Fraction(12),
    "half": Fraction(1, 2), "quarter": Fraction(1, 4), "third": Fraction(1, 3),
    "three-quarters": Fraction(3, 4), "three quarters": Fraction(3, 4),
    "two-thirds": Fraction(2, 3), "two thirds": Fraction(2, 3),
    "one-half": Fraction(1, 2), "one half": Fraction(1, 2),
    "one-quarter": Fraction(1, 4), "one quarter": Fraction(1, 4),
    "one-third": Fraction(1, 3), "one third": Fraction(1, 3),
}

_NUM_TOKEN = re.compile(
    r"""(?P<whole>\d+)\s*(?P<vulgar>[¼½¾⅐⅑⅒⅓⅔⅕⅖⅗⅘⅙⅚⅛⅜⅝⅞])   # 1½
      | (?P<v_only>[¼½¾⅐⅑⅒⅓⅔⅕⅖⅗⅘⅙⅚⅛⅜⅝⅞])                      # ½
      | (?P<mixed_w>\d+)\s+(?P<mixed_n>\d+)\s*/\s*(?P<mixed_d>\d+)  # 1 1/2
      | (?P<fn>\d+)\s*/\s*(?P<fd>\d+)                            # 1/2
      | (?P<dec>\d+(?:[.,]\d+)?)                                 # 0.5  or  0,5
    """,
    re.X,
)


_VULGAR_RE = re.compile("[" + "".join(VULGAR) + "]")


def _expand_vulgar(s):
    """Rewrite ½ -> ' 1/2' BEFORE any NFKC pass.

    🚨 NFKC IS A TRAP HERE AND IT FAILS SILENTLY IN THE WORST DIRECTION.
       NFKC('½')  -> '1⁄2'  (U+2044 FRACTION SLASH, not '/')  -- lookup misses
       NFKC('1½') -> '11⁄2' -- which then reads as ELEVEN HALVES.
    A canonicaliser that turns 1½ into 11/2 does not fail loudly; it produces a plausible
    wrong number and scores a correct model as wrong. So vulgar fractions are expanded first,
    with an explicit space so the whole part cannot fuse with the numerator.
    """
    return _VULGAR_RE.sub(lambda m: " %s/%s " % (VULGAR[m.group()].numerator,
                                                 VULGAR[m.group()].denominator), s)


def _prep(text):
    """Vulgar-expand, then NFKC, then normalise the fraction slash and whitespace."""
    s = _expand_vulgar(str(text))
    s = unicodedata.normalize("NFKC", s).replace("⁄", "/")
    return re.sub(r"\s+", " ", s).strip()


def _strip_leading_number(s):
    """Return whatever follows the leading quantity -- the unit portion."""
    low = s.lower()
    for word in sorted(WORD_NUMBERS, key=len, reverse=True):
        m = re.match(r"^%s\b" % re.escape(word), low)
        if m:
            rest = s[m.end():]
            # "half a cup" / "three of the cloves" -- drop a leading article
            return re.sub(r"^\s*(?:a|an|of\s+a|of\s+an|of\s+the|of)\b", "", rest,
                          flags=re.I).strip()
    m = _NUM_TOKEN.search(s)
    return s[m.end():].strip() if m else ""


def parse_number(text):
    """Parse the FIRST numeric quantity in `text` as an exact Fraction, or None.

    Handles: 2, 2.5, 2,5 (European decimal comma), 1/2, 1 1/2, ½, 1½, and number words.
    Exact arithmetic throughout -- a scorer that introduces float error and then applies a
    tolerance to hide it is measuring its own rounding.
    """
    if text is None:
        return None
    s = _prep(text).lower()
    if not s:
        return None

    # number words first, longest-first so "one half" beats "one"
    for word in sorted(WORD_NUMBERS, key=len, reverse=True):
        if re.match(r"^%s\b" % re.escape(word), s):
            return WORD_NUMBERS[word]

    m = _NUM_TOKEN.search(s)
    if not m:
        return None
    g = m.groupdict()
    if g["whole"] and g["vulgar"]:
        return Fraction(int(g["whole"])) + VULGAR[g["vulgar"]]
    if g["v_only"]:
        return VULGAR[g["v_only"]]
    if g["mixed_w"]:
        d = int(g["mixed_d"])
        return None if d == 0 else Fraction(int(g["mixed_w"])) + Fraction(int(g["mixed_n"]), d)
    if g["fn"]:
        d = int(g["fd"])
        return None if d == 0 else Fraction(int(g["fn"]), d)
    if g["dec"]:
        return Fraction(g["dec"].replace(",", "."))
    return None


_DEC_RE = re.compile(r"\d+[.,](\d+)")


def _decimal_places(text):
    """How many decimal places the FIRST decimal token in `text` carries, or None."""
    if text is None or isinstance(text, Fraction):
        return None
    m = _DEC_RE.search(_prep(text))
    return len(m.group(1)) if m else None


def numbers_equal(a, b):
    """Equality of two quantities.

    Exact equality of the parsed Fractions, OR: one side is a DECIMAL and is the correctly
    rounded value of the other at the precision it was written to, with at least two decimal
    places. `0.167 cup` IS `1/6 cup`; so is `0.17 cup`; `0.2 cup` is NOT (one place is a 20%
    error on a sixth). This is not a float tolerance hiding our own arithmetic -- the Fractions
    are exact -- it is accepting the MODEL'S rounding when the rounding is correct, which the
    §5.3 adversarial equivalence controls require (`equiv_decimal`: decimal vs fraction, same
    quantity). Published here so it is a rule, not a leniency. Added 2026-09-01 when the
    control suite first ran against the scorer and caught the omission.
    """
    fa, fb = (a if isinstance(a, Fraction) else parse_number(a),
              b if isinstance(b, Fraction) else parse_number(b))
    if fa is None or fb is None:
        return False
    if fa == fb:
        return True
    for txt, other in ((a, fb), (b, fa)):
        d = _decimal_places(txt)
        if d is not None and d >= 2:
            given = fa if txt is a else fb
            # correctly rounded: |given - other| <= half a unit in the last place
            if abs(given - other) <= Fraction(1, 2 * 10 ** d):
                return True
    return False


# --------------------------------------------------------------------------------------------
# Units
# --------------------------------------------------------------------------------------------
# ⛔ Deliberately does NOT convert between units. `1 cup` and `240 ml` are not scored as equal:
#    the conversion factor is disputable and a model choosing to convert has done something
#    different from what was asked. This map only collapses SPELLINGS of the same unit.

UNIT_ALIASES = {
    "teaspoon": "tsp", "teaspoons": "tsp", "tsp": "tsp", "tsps": "tsp", "t": "tsp",
    "tablespoon": "tbsp", "tablespoons": "tbsp", "tbsp": "tbsp", "tbsps": "tbsp",
    "tbs": "tbsp", "tb": "tbsp", "T": "tbsp",
    "cup": "cup", "cups": "cup", "c": "cup",
    "ounce": "oz", "ounces": "oz", "oz": "oz",
    "fluid ounce": "fl oz", "fluid ounces": "fl oz", "fl oz": "fl oz", "floz": "fl oz",
    "pound": "lb", "pounds": "lb", "lb": "lb", "lbs": "lb",
    "gram": "g", "grams": "g", "g": "g", "gr": "g",
    "kilogram": "kg", "kilograms": "kg", "kg": "kg",
    "millilitre": "ml", "millilitres": "ml", "milliliter": "ml", "milliliters": "ml",
    "ml": "ml", "mL": "ml",
    "litre": "l", "litres": "l", "liter": "l", "liters": "l", "l": "l", "L": "l",
    "quart": "qt", "quarts": "qt", "qt": "qt",
    "pint": "pt", "pints": "pt", "pt": "pt",
    "clove": "clove", "cloves": "clove",
    "sprig": "sprig", "sprigs": "sprig",
    "pinch": "pinch", "pinches": "pinch",
    "slice": "slice", "slices": "slice",
    "stalk": "stalk", "stalks": "stalk",
    "can": "can", "cans": "can",
}


def canon_unit(text):
    """Canonicalise a unit SPELLING. Returns None if it is not a recognised unit."""
    if text is None:
        return None
    s = unicodedata.normalize("NFKC", str(text)).strip().rstrip(".").lower()
    s = re.sub(r"\s+", " ", s)
    if s in UNIT_ALIASES:
        return UNIT_ALIASES[s]
    # single-letter units are case-sensitive by convention (T=tbsp, t=tsp); try raw
    raw = str(text).strip().rstrip(".")
    return UNIT_ALIASES.get(raw)


_QTY = re.compile(r"^\s*(?P<num>[^a-zA-Z]*[\d¼½¾⅐⅑⅒⅓⅔⅕⅖⅗⅘⅙⅚⅛⅜⅝⅞][^a-zA-Z]*)\s*(?P<unit>.*)$")


def parse_quantity(text):
    """Split '1/2 cup' into (Fraction(1,2), 'cup'). Returns (None, None) on failure.

    Unit extraction is done by stripping the leading quantity rather than by a digit-anchored
    regex -- otherwise 'half a cup' and 'three cloves' parse a number and then lose their unit,
    which scores a correct answer as wrong.
    """
    if text is None:
        return (None, None)
    s = _prep(text)
    num = parse_number(s)
    if num is None:
        return (None, None)
    return (num, canon_unit(_strip_leading_number(s)))


def parse_ingredient_line(text):
    """Split '2 1/4 tbsp olive oil' into (Fraction(9,4), 'tbsp', 'olive oil').

    🚨 The unit must be taken as the LONGEST MATCHING ALIAS from the tokens that follow the
       number -- not as 'everything after the number'. Handing `canon_unit` the string
       'tbsp olive oil' returns None, which silently strips the unit from every line and
       scores a perfectly correct answer as WRONG. Found by the family-01 controls, which is
       precisely what they are for.
    """
    if text is None:
        return (None, None, None)
    s = _prep(text)
    num = parse_number(s)
    if num is None:
        return (None, None, None)
    rest = _strip_leading_number(s)
    tokens = rest.split()
    # try the longest unit phrase first ("fluid ounces" before "fluid")
    for take in (2, 1):
        if len(tokens) >= take:
            unit = canon_unit(" ".join(tokens[:take]))
            if unit:
                return (num, unit, " ".join(tokens[take:]).strip())
    return (num, None, rest)


# ⚠️ DEFINITIONAL conversions, added 2026-09-01 after reading scored output (DEVIATION_LOG D3).
#    `1 cup` vs `240 ml` stays UNEQUAL: that factor is disputable and a model that converts
#    systems has done something different from what was asked. But 3 tsp = 1 tbsp and
#    16 tbsp = 1 cup are IDENTITIES of the US customary system, and a model that writes
#    `2 tsp` for `2/3 tbsp` has written the same quantity in the form a kitchen can measure.
#    The pre-registration's rule (kimi-k3: "equivalent arithmetic forms must not be scored as
#    errors") already covers this; the first scorer simply did not implement it. 218 of 1,246
#    family-1 WRONG rows were explained entirely by this identity. Negative controls in
#    self_test() keep cup/ml, cup/g and cup/oz unequal.
_IN_TSP = {"tsp": Fraction(1), "tbsp": Fraction(3), "cup": Fraction(48),
           "pt": Fraction(96), "qt": Fraction(192)}


def _to_tsp(n, unit):
    return n * _IN_TSP[unit] if unit in _IN_TSP else None


def quantities_identical(a, b):
    """Same quantity, allowing a definitional unit change within the customary volume ladder."""
    na, ua, _ = parse_ingredient_line(a)
    nb, ub, _ = parse_ingredient_line(b)
    if na is None or nb is None:
        return False
    if ua == ub:
        return numbers_equal(a, b)
    ta, tb = _to_tsp(na, ua), _to_tsp(nb, ub)
    return ta is not None and tb is not None and ta == tb


def ingredient_lines_equal(a, b):
    """Equal amount AND unit AND ingredient name (case/spacing-insensitive), where 'equal unit'
    admits a definitional conversion on the tsp/tbsp/cup ladder (see quantities_identical)."""
    na, ua, ia = parse_ingredient_line(a)
    nb, ub, ib = parse_ingredient_line(b)
    if na is None or nb is None:
        return False
    if canon_text(ia).lower() != canon_text(ib).lower():
        return False
    return quantities_identical(a, b)


def quantities_equal(a, b, require_unit=True):
    """Equal value AND equal canonical unit. Unit conversion is deliberately NOT performed."""
    na, ua = parse_quantity(a)
    nb, ub = parse_quantity(b)
    if na is None or nb is None or na != nb:
        return False
    if not require_unit:
        return True
    return ua == ub


# --------------------------------------------------------------------------------------------
# Redaction tokens  (qwen3-14b)
# --------------------------------------------------------------------------------------------

REDACTION_TOKENS = [
    r"\[REDACTED\]", r"\[PII\]", r"\[MASKED\]", r"\[REMOVED\]", r"\[HIDDEN\]",
    r"\[NAME\]", r"\[EMAIL\]", r"\[PHONE\]", r"\[SSN\]", r"\[ADDRESS\]", r"\[DATE\]",
    r"█+", r"X{3,}", r"x{3,}", r"\*{3,}", r"#{3,}", r"_{3,}", r"<REDACTED>", r"\(redacted\)",
]
_REDACTION_RE = re.compile("|".join(REDACTION_TOKENS), re.I)
REDACTION_CANON = "███"   # ███


def canon_redaction(text):
    """Collapse every accepted redaction marker to one canonical token."""
    if text is None:
        return None
    return _REDACTION_RE.sub(REDACTION_CANON, unicodedata.normalize("NFKC", str(text)))


# --------------------------------------------------------------------------------------------
# Whitespace / typography
# --------------------------------------------------------------------------------------------

def canon_text(text):
    """Normalise typography that carries no meaning: smart quotes, dashes, NBSP, spacing.

    🚨 2026-09-01: vulgar fractions are expanded BEFORE NFKC here too. This function ran NFKC
       first, so a caller that canonicalised a line before parsing it turned `2⅔` into `22⁄3`
       -- twenty-two thirds -- the exact trap `_expand_vulgar` documents, reached through a
       different door. Caught by the §5.3 control `equiv_unicode_fraction` the first time the
       suite ran against a scorer. Every family's line parser goes through this function.
    """
    if text is None:
        return None
    s = unicodedata.normalize("NFKC", _expand_vulgar(str(text))).replace("⁄", "/")
    s = (s.replace("‘", "'").replace("’", "'")
           .replace("“", '"').replace("”", '"')
           .replace("–", "-").replace("—", "-")
           .replace(" ", " "))
    return re.sub(r"\s+", " ", s).strip()


# --------------------------------------------------------------------------------------------
# Controls
# --------------------------------------------------------------------------------------------

def self_test():
    """⛔ Must fire in BOTH directions. A canonicaliser that only ever says 'equal' is a
    machine for turning wrong answers into right ones."""
    eq = [  # MUST be equal -- adversarial equivalence controls, §5.3
        ("1/2 cup", "0.5 cup"), ("1/2 cup", "½ cup"), ("1/2 cup", "half a cup"),
        ("1 1/2 tsp", "1.5 tsp"), ("1 1/2 tsp", "1½ tsp"), ("1 1/2 tsp", "1.50 teaspoons"),
        ("2 tablespoons", "2 tbsp"), ("2 tablespoons", "2 Tbsp."), ("2 tablespoons", "2 TBSP"),
        ("0,5 l", "0.5 litres"), ("3 cloves", "three cloves"),
        ("2/4 cup", "1/2 cup"),          # unreduced fraction
        ("2.0 cups", "2 cups"),          # trailing zero
        ("1 lb", "1 lbs"),               # plural spelling
    ]
    ne = [  # MUST NOT be equal -- negative controls
        ("1/2 cup", "1/3 cup"),          # different value
        ("1/2 cup", "0.5 tsp"),          # different unit
        ("1 cup", "240 ml"),             # unit CONVERSION is not equivalence
        ("2 tbsp", "2 tsp"),
        ("1.5 cups", "15 cups"),
        ("3 cloves", "4 cloves"),
        (None, "1 cup"), ("1 cup", None), (None, None),
        ("salt", "pepper"),
    ]
    red_eq = [
        ("[REDACTED]", "███"), ("[REDACTED]", "[PII]"), ("[REDACTED]", "XXXX"),
        ("Call [PHONE] now", "Call ███ now"),
    ]
    red_ne = [("[REDACTED]", "Jane Smith"), ("███", "555-0100")]
    # definitional ladder (quantities_identical) -- fires both ways, like everything else here
    lad_eq = [("2/3 tbsp rice vinegar", "2 tsp rice vinegar"),
              ("1/8 cup soy sauce", "2 tbsp soy sauce"),
              ("1/2 tbsp honey", "1 1/2 tsp honey"),
              ("1 cup water", "16 tbsp water")]
    lad_ne = [("1 cup milk", "240 ml milk"),          # cross-system: still NOT equivalence
              ("1 cup flour", "8 oz flour"),          # volume vs weight
              ("2 tbsp oil", "2 tsp oil"),            # same ladder, different quantity
              ("1/8 cup salt", "2 tbsp sugar")]       # right conversion, wrong ingredient

    bad = 0
    for a, b in lad_eq:
        if not ingredient_lines_equal(a, b):
            bad += 1; print("  FAIL  ladder should be EQUAL: %-24r %-24r" % (a, b))
    for a, b in lad_ne:
        if ingredient_lines_equal(a, b):
            bad += 1; print("  FAIL  ladder should DIFFER : %-24r %-24r" % (a, b))
    for a, b in eq:
        if not quantities_equal(a, b):
            bad += 1; print("  FAIL  should be EQUAL: %-18r %-18r" % (a, b))
    for a, b in ne:
        if quantities_equal(a, b):
            bad += 1; print("  FAIL  should DIFFER : %-18r %-18r" % (a, b))
    for a, b in red_eq:
        if canon_redaction(a) != canon_redaction(b):
            bad += 1; print("  FAIL  redaction should be EQUAL: %r %r" % (a, b))
    for a, b in red_ne:
        if canon_redaction(a) == canon_redaction(b):
            bad += 1; print("  FAIL  redaction should DIFFER : %r %r" % (a, b))

    total = len(eq) + len(ne) + len(red_eq) + len(red_ne) + len(lad_eq) + len(lad_ne)
    if bad:
        print("\n!! EQUIVALENCE SELF-TEST FAILED: %d/%d" % (bad, total))
        print("   Per §5.3, a family whose equivalence layer fails its controls DOES NOT SHIP.")
        return False
    print("  equivalence self-test: %d/%d pass" % (total, total))
    print("     %d must-be-equal (adversarial) | %d must-differ (negative controls)"
          % (len(eq) + len(red_eq) + len(lad_eq), len(ne) + len(red_ne) + len(lad_ne)))
    return True


if __name__ == "__main__":
    if "--self-test" in sys.argv or len(sys.argv) == 1:
        sys.exit(0 if self_test() else 1)
