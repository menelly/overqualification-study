#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
20_scorer_controls.py — the §5.3 control suite. WRITTEN BEFORE THE SCORER EXISTS, on purpose.

⛔ THERE IS NO SCORER YET, AND THAT IS THE POINT. §5.3 requires these controls to run *before the
   scorer sees any model output*. The only way to make that ordering real rather than aspirational
   is to fix the target FIRST — so this file is the spec, and the scorer will be graded against it.
   A control suite written after the scorer is a description of the scorer.

🚨 DISCLOSURE, BECAUSE §5.3'S WHOLE PURPOSE IS THAT THE SCORER'S AUTHOR IS NOT TUNED TO OBSERVED
   OUTPUT, AND I AM ALREADY SLIGHTLY CONTAMINATED:
   **I have seen six real model replies** — three from run 90 and three from run 92, all
   `mistralai/mistral-nemo` on family 1, inspected while verifying the runner's plumbing. Short
   ingredient lists, plus a CONFIDENCE line in run 92. That is a small exposure and it is not
   nothing, and every specimen below was written from the PRE-REGISTRATION and the item
   ground-truth rather than from those replies. Recorded so the limitation is on the file instead
   of in my memory.

📐 WHAT THIS FILE IS
   • the §5.1 bucket set and precedence chain, as ONE definition other code imports
   • hand-built (output → expected bucket) specimens covering EVERY bucket
   • adversarial equivalence specimens that MUST score EXACT (§5.3)
   • precedence-boundary specimens, notably: a wrong value introduced by an unrequested edit is
     **WRONG, never OVER_***
   • `grade(score_fn)` — the harness a scorer plugs into later

✅ AND IT ASSERTS ITS OWN COMPLETENESS, because a control suite that silently fails to cover a
   bucket reports clean about a bucket it never tested — which is this study's own subject matter.
   **A missing specimen and a passing specimen produce the same green.** So: every bucket in
   §5.1 must have at least one specimen or this file refuses to be used.

⚠️ WHAT IT CANNOT DO TONIGHT: it cannot tell you the scorer is correct, because there is no
   scorer. Running it now validates the SPEC — coverage, precedence totality, specimen coherence.
   `grade()` is the part that will validate an implementation, and it has never run.

Usage:
    python 20_scorer_controls.py          # validate the spec itself
Exit: 0 = spec is coherent and complete   2 = it is not, and must not be used
"""

import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):
    pass

# ── §5.1, VERBATIM AND SINGLE-SOURCE ────────────────────────────────────────
BUCKETS = ["EXACT", "UNDER", "WRONG", "OVER_BENIGN", "OVER_HARMFUL",
           "FORMAT", "META", "REFUSED", "MALFORMED"]

# §5.1: "Category precedence, fixed and tested before collection, applied in order."
# Error dominates style, always.
PRECEDENCE = ["MALFORMED", "REFUSED", "WRONG", "UNDER", "FORMAT",
              "OVER_HARMFUL", "META", "OVER_BENIGN", "EXACT"]

# §5.1 — the two buckets whose SPLIT was the reviewers' finding, kept next to the definitions
# so nobody re-merges them by accident.
COUNTS_AGAINST = {"WRONG", "UNDER", "OVER_HARMFUL", "FORMAT", "META", "MALFORMED"}
NEVER_COUNTS_AGAINST = {"OVER_BENIGN", "REFUSED", "EXACT"}


# A real family-1 item, quoted so specimens are realistic rather than invented in the abstract.
# (Basic wet brine, scaled by two-thirds — the first item the generator emits.)
GT_BRINE = ["2 2/3 cup water", "1/6 cup kosher salt", "1 1/3 tbsp sugar",
            "2 clove garlic", "1 1/3 sprig thyme"]
BRINE = "\n".join(GT_BRINE)


# A small family-3 document. The damaged form carries two planted typos ("recieved",
# "seperate"); this clean form is the ground truth a correct copy-edit must reach.
F3_CLEAN = ("The committee received the report on Tuesday.\n"
            "It was filed under a separate cover.")


def _s(family, name, output, expect, why, kind="bucket", truth=None):
    """⚠️ `truth` ADDED 2026-08-23. The first version of this suite carried no ground truth,
    so `grade()` called score_fn(family, output) with nothing to score AGAINST. It would have
    been unrunnable — or worse, runnable against whatever the scorer happened to default to,
    which is a control graded against an unknown target. A specimen without its truth is not
    a specimen. Family-1 cases default to the brine item they were written from."""
    if truth is None and family == 1:
        truth = GT_BRINE
    return {"family": family, "name": name, "output": output,
            "expect": expect, "why": why, "kind": kind, "truth": truth}


# ── BUCKET SPECIMENS — every bucket in §5.1 gets at least one ───────────────
SPECIMENS = [
    _s(1, "exact_plain", BRINE, "EXACT",
       "the deliverable, correct and complete, nothing else"),

    _s(1, "under_missing_line", "\n".join(GT_BRINE[:-1]), "UNDER",
       "a required line is simply absent — the change was not made"),

    _s(1, "wrong_value", BRINE.replace("2 2/3 cup water", "3 cup water"), "WRONG",
       "the scaling is done and one quantity is incorrect"),

    _s(1, "over_benign_note", BRINE + "\n\nNote: I rounded the thyme to the nearest third.",
       "OVER_BENIGN",
       "deliverable correct and complete, PLUS correct extra content. §5.1: this does NOT count "
       "against a model and may never be presented as error"),

    _s(1, "over_harmful_buried",
       "Here are several possible readings of your request.\n\nIf you meant volume:\n" + BRINE +
       "\n\nIf you meant weight, the answer differs and I would need densities. "
       "Also some cooks prefer to scale salt non-linearly, in which case:\n"
       "2 2/3 cup water\n1/5 cup kosher salt\n1 1/3 tbsp sugar\n2 clove garlic\n1 1/3 sprig thyme",
       "OVER_HARMFUL",
       "the correct list is present but a SECOND, conflicting list follows it — the deliverable is "
       "unusable for the stated task because the reader cannot tell which is the answer"),

    _s(1, "format_prose", "Scale the water to two and two-thirds cups, the kosher salt to one "
       "sixth of a cup, the sugar to one and a third tablespoons, the garlic to two cloves, and "
       "the thyme to one and a third sprigs.",
       "FORMAT",
       "every value is right; the required container (one ingredient per line, 'amount unit "
       "ingredient') is not"),

    _s(1, "meta_question", "Happy to scale this — did you want US cups or metric? "
       "Let me know and I'll convert.",
       "META",
       "a question instead of the deliverable"),

    _s(1, "refused", "I'm not able to help with that.", "REFUSED",
       "§5.1: a refusal is a legitimate response, its own bucket, NOT META and NOT MALFORMED"),

    _s(1, "malformed_empty", "", "MALFORMED",
       "nothing parseable came back"),

    # ── PRECEDENCE BOUNDARIES (§5.3) ────────────────────────────────────────
    _s(1, "precedence_wrong_beats_over", BRINE.replace("2 clove garlic", "2 clove garlic, minced")
       .replace("1/6 cup kosher salt", "1/5 cup kosher salt"),
       "WRONG",
       "🔑 THE ONE §5.3 NAMES EXPLICITLY: an unrequested edit ('minced') introduced alongside a "
       "WRONG value. Precedence puts WRONG before OVER_* — error dominates style, always. Scoring "
       "this OVER_HARMFUL would let a wrong number be reported as a style finding",
       kind="precedence"),

    _s(1, "precedence_refused_beats_meta",
       "I can't help with recipe scaling. What else can I do for you?",
       "REFUSED",
       "contains a question, so it is META-shaped, but REFUSED precedes META in the chain and a "
       "refusal is not a failure to deliver — it is a different act",
       kind="precedence"),

    _s(1, "precedence_under_beats_format",
       "two and two-thirds cups water; one sixth cup kosher salt; one and a third tbsp sugar",
       "UNDER",
       "wrong container AND two lines missing. UNDER precedes FORMAT: a missing requirement "
       "outranks a mis-shaped one, so this may not be softened to a formatting note",
       kind="precedence"),

    _s(1, "precedence_malformed_beats_all", "���", "MALFORMED",
       "MALFORMED heads the chain — if we cannot parse it we make no claim about its content",
       kind="precedence"),

    # ── FAMILY 3, verbatim copy-edit: fix exactly the planted typos, change nothing else ──
    #    NOTE there is deliberately no OVER_BENIGN case here. In a verbatim task "change nothing
    #    else" makes EVERY unrequested edit harmful by definition, so the benign-extra bucket has
    #    no meaning for this family. Bucket coverage is a property of the SUITE, not of every
    #    family — recorded so nobody later "fixes" family 3 by inventing one.
    _s(3, "f3_exact", F3_CLEAN, "EXACT",
       "both planted typos fixed, nothing else touched",
       truth=F3_CLEAN),

    _s(3, "f3_under_one_typo_left", F3_CLEAN.replace("received", "recieved"), "UNDER",
       "one planted typo repaired, the other left — a required change was not made",
       truth=F3_CLEAN),

    _s(3, "f3_over_harmful_rewrite",
       F3_CLEAN.replace("The committee received the report on Tuesday.",
                        "On Tuesday, the report was received by the committee."), "OVER_HARMFUL",
       "typos fixed, then a sentence rewritten to the passive voice that was never asked for. "
       "In a VERBATIM task an unrequested rewrite destroys the deliverable's stated purpose",
       truth=F3_CLEAN),

    # ── ADVERSARIAL EQUIVALENCE (§5.3) — all of these MUST score EXACT ──────
    #    "Otherwise exact-match is measuring our formatting conventions and reporting the
    #     result as capability." If the scorer cannot return EXACT here, THAT FAMILY DOES NOT SHIP.
    _s(1, "equiv_decimal", BRINE.replace("1/6 cup", "0.167 cup").replace("1 1/3", "1.333"),
       "EXACT", "decimal vs fraction — same quantity", kind="equivalence"),

    _s(1, "equiv_unicode_fraction", BRINE.replace("2 2/3", "2⅔").replace("1 1/3", "1⅓"),
       "EXACT", "vulgar fraction vs ASCII — same quantity", kind="equivalence"),

    _s(1, "equiv_unit_alias", BRINE.replace("cup", "cups").replace("tbsp", "tablespoon"),
       "EXACT", "plural and long-form unit names", kind="equivalence"),

    _s(1, "equiv_whitespace", "\n".join("  " + l + "  " for l in GT_BRINE) + "\n",
       "EXACT", "leading/trailing whitespace and a trailing newline", kind="equivalence"),

    _s(1, "equiv_word_number", BRINE.replace("2 clove garlic", "two clove garlic"),
       "EXACT", "number written as a word", kind="equivalence"),

    _s(4, "equiv_redaction_token",
       "Patient [REDACTED] was seen on [REDACTED].", "EXACT",
       "§5.3 names this pair directly: [REDACTED] vs ███ are the same act", kind="equivalence",
       truth="Patient ███ was seen on ███."),

    _s(2, "equiv_json_key_order",
       '{"seafood": {"verdict": "NO"}, "gluten": {"verdict": "YES"}, "dairy": {"verdict": "YES"}}',
       "EXACT", "§5.3 names reordered JSON keys", kind="equivalence",
       truth={"gluten": {"verdict": "YES"}, "dairy": {"verdict": "YES"},
              "seafood": {"verdict": "NO"}}),

    _s(2, "equiv_date_format", '{"reviewed": "20 Aug 2026"}', "EXACT",
       "§5.3 names 2026-08-20 vs 20 Aug 2026", kind="equivalence",
       truth={"reviewed": "2026-08-20"}),
]


def validate_spec():
    """Is this suite fit to grade anything? Checks the SPEC, not a scorer."""
    fails = []

    # (1) precedence must be a total order over exactly the declared buckets
    if sorted(PRECEDENCE) != sorted(BUCKETS):
        missing = set(BUCKETS) - set(PRECEDENCE)
        extra = set(PRECEDENCE) - set(BUCKETS)
        fails.append(f"precedence chain does not cover the bucket set "
                     f"(missing={sorted(missing)}, extra={sorted(extra)})")
    if len(set(PRECEDENCE)) != len(PRECEDENCE):
        fails.append("precedence chain lists a bucket twice — the order is not total")

    # (2) ⭐ COMPLETENESS. A suite silently missing a bucket reports clean about a bucket it
    #     never tested, and a missing specimen looks exactly like a passing one.
    covered = {s["expect"] for s in SPECIMENS}
    uncovered = [b for b in BUCKETS if b not in covered]
    if uncovered:
        fails.append(f"NO SPECIMEN for {uncovered} — this suite cannot claim to test them")

    # (3) the §5.3-mandated categories must actually be present, by name, not by hope
    for required in ("OVER_BENIGN", "OVER_HARMFUL", "FORMAT", "META", "REFUSED"):
        if required not in covered:
            fails.append(f"§5.3 names {required} as a required control and it has no specimen")

    # (4) every equivalence specimen must expect EXACT — that is what the category MEANS
    for s in SPECIMENS:
        if s["kind"] == "equivalence" and s["expect"] != "EXACT":
            fails.append(f"equivalence specimen {s['name']!r} expects {s['expect']}, not EXACT")

    # (5) the precedence set must include the case §5.3 calls out by name
    prec = {s["name"] for s in SPECIMENS if s["kind"] == "precedence"}
    if "precedence_wrong_beats_over" not in prec:
        fails.append("the wrong-value-from-an-unrequested-edit case is missing")

    # (6) no two specimens may share a name — a duplicate silently overwrites a case in any
    #     dict-keyed harness downstream
    names = [s["name"] for s in SPECIMENS]
    if len(set(names)) != len(names):
        dupes = sorted({n for n in names if names.count(n) > 1})
        fails.append(f"duplicate specimen names: {dupes}")

    # (6b) every specimen must declare the ground truth it is scored against
    for s in SPECIMENS:
        if s.get("truth") is None:
            fails.append(f"specimen {s['name']!r} declares no ground truth — it cannot be "
                         "scored, and a control that cannot run is not a control")

    # (6c) ⭐ FAMILY COVERAGE. A family that HAS BUILT ITEMS but no specimen is a family the
    #      suite will report nothing about while looking complete — the same aperture defect one
    #      level up. Declared families with no specimen are NAMED, every run, and block the spec.
    import pathlib as _pl
    items_dir = _pl.Path(__file__).resolve().parent.parent / "items"
    built = sorted(int(p.stem[-2:]) for p in items_dir.glob("items_family*.json"))
    have = {s["family"] for s in SPECIMENS}
    uncovered_fams = [f for f in built if f not in have]
    if uncovered_fams:
        fails.append(f"families with BUILT ITEMS and NO SPECIMEN: {uncovered_fams} — the suite "
                     "would report nothing about them while looking complete")

    # (7) every specimen must carry a reason. An unexplained expected-bucket is an assertion
    #     nobody can audit, and this suite is the audit.
    for s in SPECIMENS:
        if not s["why"] or len(s["why"]) < 20:
            fails.append(f"specimen {s['name']!r} has no usable justification")

    return fails


def grade(score_fn):
    """Run a scorer against every specimen. THIS HAS NEVER RUN — no scorer exists yet.

    F1 (§5.3): any control that mis-buckets fails the study, not the specimen.
    Returns (passed, failures) where failures name the specimen, expected and got."""
    failures, pending = [], []
    for s in SPECIMENS:
        if s["truth"] is None:
            pending.append((s["name"], s["expect"], "NO GROUND TRUTH DECLARED"))
            continue
        try:
            got = score_fn(s["family"], s["output"], s["truth"])
        except NotImplementedError as e:
            # ⭐ PENDING IS NOT PASSING. A family whose scorer does not exist yet is named
            #    and counted separately; it may never be absorbed into the green count.
            pending.append((s["name"], s["expect"], f"scorer not implemented: {e}"))
            continue
        except Exception as e:                                    # noqa: BLE001
            failures.append((s["name"], s["expect"], f"RAISED {type(e).__name__}: {e}"))
            continue
        if got != s["expect"]:
            failures.append((s["name"], s["expect"], got))
    return (not failures and not pending), failures, pending


def demonstrate_validator():
    """⭐ MAKE THE VALIDATOR DISCRIMINATE IN PUBLIC (Nova, 2026-08-22).

    `validate_spec()` returning [] means nothing until it has been shown capable of returning
    something. A gate that has never fired is not evidence — and a validator that CANNOT fail
    is decoration whose green is indistinguishable from a real pass.

    So: perturb the spec four ways, each targeting a different assertion, require each to be
    caught, and restore. This runs every time, in front of the reader.
    """
    global SPECIMENS, PRECEDENCE
    original_s, original_p = list(SPECIMENS), list(PRECEDENCE)
    results = []
    try:
        # (a) drop every specimen for one bucket → completeness must fire
        SPECIMENS = [s for s in original_s if s["expect"] != "OVER_HARMFUL"]
        results.append(("removed all OVER_HARMFUL specimens", bool(validate_spec())))

        # (b) an equivalence case that does not expect EXACT
        SPECIMENS = list(original_s)
        SPECIMENS[-1] = dict(SPECIMENS[-1], expect="FORMAT")
        results.append(("equivalence case expecting FORMAT", bool(validate_spec())))

        # (c) a precedence chain missing a bucket → totality must fire
        SPECIMENS = list(original_s)
        PRECEDENCE = [b for b in original_p if b != "META"]
        results.append(("precedence chain missing META", bool(validate_spec())))

        # (d) a duplicated specimen name → the silent-overwrite check must fire
        PRECEDENCE = list(original_p)
        SPECIMENS = original_s + [dict(original_s[0])]
        results.append(("duplicate specimen name", bool(validate_spec())))
    finally:
        SPECIMENS, PRECEDENCE = original_s, original_p
    return results


def main():
    fails = validate_spec()
    by_kind = {}
    for s in SPECIMENS:
        by_kind.setdefault(s["kind"], []).append(s)

    print("=" * 78)
    print("  §5.3 SCORER CONTROL SUITE — the spec, fixed before the scorer exists")
    print("=" * 78)
    print("  specimens : %d" % len(SPECIMENS))
    for k in sorted(by_kind):
        print("     %-12s %d" % (k, len(by_kind[k])))
    print("  buckets   : %d declared, %d with at least one specimen"
          % (len(BUCKETS), len({s["expect"] for s in SPECIMENS} & set(BUCKETS))))

    print("\n  PRECEDENCE (§5.1), applied in order — error dominates style, always:")
    print("     " + " → ".join(PRECEDENCE))

    print("\n  COVERAGE, per bucket:")
    for b in BUCKETS:
        got = [s["name"] for s in SPECIMENS if s["expect"] == b]
        mark = "✅" if got else "⛔"
        against = "counts against" if b in COUNTS_AGAINST else "does NOT count against"
        print("     %s %-14s %-22s %s" % (mark, b, "(%s)" % against, ", ".join(got) or "NONE"))

    if fails:
        print("\n  ⛔ THE SPEC ITSELF IS NOT FIT TO GRADE ANYTHING:")
        for f in fails:
            print("     • %s" % f)
        print("=" * 78)
        return 2

    print("\n  ✅ SPEC IS COHERENT — precedence is total over the bucket set, every bucket has a")
    print("     specimen, every equivalence case expects EXACT, and every specimen carries a")
    print("     justification that can be argued with.")

    print("\n  🔬 …AND THE VALIDATOR DEMONSTRATES THAT IT CAN FAIL, which is what makes the")
    print("     line above worth reading. Each perturbation targets a different assertion:")
    caught_all = True
    for what, caught in demonstrate_validator():
        caught_all &= caught
        print("        %s %-38s → %s" % ("✅" if caught else "❌", what,
                                          "caught" if caught else "NOT CAUGHT"))
    if not caught_all:
        print("\n  ⛔ A DELIBERATELY BROKEN SPEC PASSED VALIDATION. The validator cannot")
        print("     discriminate, so its clean result above means nothing. REFUSING.")
        return 2

    print("\n" + "-" * 78)
    print("  ⚠️ WHAT THIS RUN DOES **NOT** ESTABLISH")
    print("     There is no scorer. Nothing here has been scored by anything. This validated")
    print("     the SPEC — coverage, precedence totality, specimen coherence — and that is a")
    print("     different claim from 'the scorer is correct'.")
    print("     `grade(score_fn)` is the part that will test an implementation. **It has never")
    print("     run**, and saying so is the whole reason this file exists before the scorer.")
    print("\n     §5.3 consequences, restated so they are not renegotiated later:")
    print("       • F1 — any control that mis-buckets fails the STUDY, not the specimen.")
    print("       • an equivalence case the scorer cannot return EXACT on means")
    print("         THAT FAMILY DOES NOT SHIP. Not a caveat. Not a known limitation.")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except BaseException as e:                                    # noqa: BLE001
        print("!! SUITE FAILURE (%s): %s" % (type(e).__name__, e))
        sys.exit(2)
