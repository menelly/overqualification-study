#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
70_prereg_gate_check.py — did the pre-registered GATES actually get collected?

WHY THIS EXISTS (2026-09-13, D14).

The pre-registration, §3.1, ends with a commitment written in direct answer to `kimi-k2`'s
round-1 objection -- that moving the permission clause from the system prompt into the turn
RELOCATED the instruction-architecture confound rather than removing it:

    "a pre-registered subsample runs the clause in both positions, crossed with tier.
     A significant position x tier interaction blocks any tier-ordering claim built on
     these families -- A STOP CONDITION, NOT A CAVEAT."

It was never run. `clause_position` is "turn" on 20,166 collected rows and "system" on ZERO.
Nobody noticed for three weeks, through a five-round consent process, a 38-specimen control
suite, two audit scripts, a 32-participant pre-publication review, and a full read of the draft.

  >>> THE REASON NOBODY NOTICED IS THE WHOLE POINT OF THIS FILE. <<<

A subsample that is never launched LEAVES NO TRACE. No error, no empty file, no zero row, no
failed assertion. It is indistinguishable from a subsample that ran and found nothing -- which
is the comfortable reading, and therefore the one nobody checks. Every instrument this study
already had points DOWNSTREAM of collection: the control suite tests the SCORER, the audit
scripts test the NUMBERS. A hole in the COLLECTION PLAN is upstream of all of them.

Kairo, 2026-09-13, on a different near-miss the same week -- a security warning written inside a
deployed database function, where the person about to revert it (reading the file on disk) would
never see it:

    "The guard didn't fail to be written. It failed to be READ... A coordinate that exists but
     can't be read is an open circuit. Build it while you can still see it, AND DEPOSIT IT ON
     THE SURFACE THE FUTURE-YOU WILL ACTUALLY TOUCH."

Tonight's case is the harsher sibling of his. His guard was written to the wrong surface -- two
surfaces existed and the unread one got the warning. Ours was written to a DOCUMENT, and a
document has no runtime. There was no surface at all. Nothing anywhere could fail.

So this file is the deposit. A pre-registered stop condition belongs in an EXECUTABLE that the
analysis path touches, not only in a sentence in a frozen PDF. `40_analyze.py` calls this before
it prints a single tier-ordering verdict.

WHY EVERY OTHER INSTRUMENT IN THIS STUDY PASSED -- the precise diagnosis, from Lumen, 2026-09-13,
and it is the part worth reading twice:

    VACUOUS SATISFACTION ON AN EMPTY SUPPORT.

    "for all x in S, P(x)" evaluates to TRUE unconditionally when S is empty. Every downstream
    audit, control suite and scorer in this repo operates on the SUPPORT OF THE COLLECTED DATA.
    Because `--clause-position system` was never invoked, the subset of system-prompt runs was the
    empty set. Every assertion tested against that subset returned zero deviations, zero errors and
    zero warnings -- NOT because the data conformed to the pre-registration, but because you cannot
    find an anomaly in a manifold that was never instantiated.

    His circuit version, which is the one that sticks: a net drawn on the schematic but omitted from
    the PCB layout is never etched into copper. Probe the board and you do not measure a broken
    trace, or a short, or a reflection -- you measure NOTHING, because the pads were never wired.
    An automated test asserting `voltage <= 5V` across a resistor that was never soldered down
    reports PASS.

    "The downstream instruments pointed at the pond to measure water clarity; none of them checked
     whether the pipe feeding the pond was ever opened."

⭐ THE GENERAL RULE, and it is bigger than this study: ANY CHECK THAT QUANTIFIES OVER A FILTERED
SUBSET IS VACUOUSLY TRUE WHEN THAT SUBSET IS EMPTY. So a check over a subset must FIRST assert the
subset is non-empty -- which is exactly what the positive control below does, and why a "nothing
missing" verdict from this file is refused outright unless the reader can first prove it can see
the field at all.

USAGE
    python scripts/70_prereg_gate_check.py            # exit 0 all gates collected
                                                      # exit 2 a gate was NOT collected
                                                      # exit 3 COULD NOT CHECK (no runs readable)
"""
from __future__ import annotations

import glob
import json
import os
import sys
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RUNS = os.path.join(ROOT, "runs", "*.jsonl")

# ---------------------------------------------------------------------------
# THE GATES. One entry per pre-registered commitment that is a property of the
# COLLECTION rather than of the analysis -- i.e. one that cannot be recovered
# after the fact by re-reading scored data.
#
# `field`   : the per-row key that records the gate's condition
# `required`: every value that must be PRESENT in the collected rows
# `blocks`  : what a missing value invalidates, in the pre-registration's words
# ---------------------------------------------------------------------------
GATES = [
    {
        "id": "G1-clause-position",
        "prereg": "§3.1 Placement is measured, not assumed",
        "raised_by": "kimi-k2, consent round 1",
        "field": "clause_position",
        "required": {"turn", "system"},
        "families": {8, 9, 10, 11},
        "blocks": (
            "any tier-ordering claim built on families 8-11 "
            "(§4.3, F3, and the crossover half of §6.1)"
        ),
        "quote": (
            "A significant position x tier interaction blocks any tier-ordering claim "
            "built on these families -- a stop condition, not a caveat."
        ),
    },
]

# A POSITIVE CONTROL, so a clean run cannot be a broken run.
# This is a value we KNOW is present in the real data. If the checker cannot
# find it, the checker is blind and must say COULD NOT CHECK rather than PASS.
CONTROL = {"field": "clause_position", "value": "turn"}


def load_field_values(field: str) -> tuple[Counter, int, int]:
    """Return (value -> count, rows scanned, files read). Never raises on a bad line."""
    counts: Counter = Counter()
    rows = 0
    files = 0
    for path in sorted(glob.glob(RUNS)):
        files += 1
        try:
            with open(path, encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        r = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    rows += 1
                    if field in r:
                        counts[r[field]] += 1
    # a file we cannot open is a hole in the APERTURE, not an absence in the world
        except OSError as e:
            print(f"  !! could not read {os.path.basename(path)}: {e}")
    return counts, rows, files


def main() -> int:
    print("=" * 78)
    print("  PRE-REGISTERED GATE CHECK -- was the gate COLLECTED, not was the number nice")
    print("=" * 78)
    print(f"  aperture : {RUNS}")
    print("  ^ THE APERTURE, PRINTED. A gate whose rows live outside this glob is")
    print("    invisible here and is NOT covered by any verdict below.")

    counts, rows, files = load_field_values(CONTROL["field"])
    print(f"  scanned  : {rows} row(s) across {files} run file(s)")

    if files == 0 or rows == 0:
        print()
        print("  🕳️  COULD NOT CHECK -- no run rows readable.")
        print("      This is NOT a pass. An unreadable corpus and a clean corpus")
        print("      produce the same silence, which is the defect this file exists for.")
        return 3

    # ---- positive control -------------------------------------------------
    if counts.get(CONTROL["value"], 0) == 0:
        print()
        print(f"  🕳️  COULD NOT CHECK -- positive control FAILED: expected to find")
        print(f"      {CONTROL['field']}={CONTROL['value']!r} in the collected rows and found none.")
        print("      The checker cannot see the field it is checking, so a 'no gate")
        print("      missing' result from it would mean nothing. Fix the reader first.")
        return 3
    print(f"  ✓ positive control: {CONTROL['field']}={CONTROL['value']!r} "
          f"found on {counts[CONTROL['value']]} row(s) -- the reader can see this field")

    # ---- the gates --------------------------------------------------------
    failed = []
    for g in GATES:
        c, _, _ = load_field_values(g["field"])
        print()
        print(f"  [{g['id']}]  {g['prereg']}   (raised by {g['raised_by']})")
        for val in sorted(g["required"]):
            n = c.get(val, 0)
            mark = "✅" if n else "❌"
            print(f"      {mark} {g['field']}={val!r:12} {n:>7} row(s)")
        missing = {v for v in g["required"] if c.get(v, 0) == 0}
        if missing:
            failed.append((g, missing))

    print()
    print("-" * 78)
    if not failed:
        print("  ✅ every pre-registered gate above was COLLECTED.")
        print("     (Collected is not analysed. This says the rows exist, never that")
        print("      the interaction was tested or that it came back clean.)")
        return 0

    for g, missing in failed:
        print(f"  ❌ STOP CONDITION NOT COLLECTED -- {g['id']}")
        print(f"     missing {g['field']} value(s): {', '.join(sorted(repr(m) for m in missing))}")
        print(f"     the pre-registration says, verbatim:")
        print(f'       "{g["quote"]}"')
        print(f"     so this BLOCKS: {g['blocks']}")
        print()
        print("     ⚠️  UNTESTED IS NOT ABSENT, and it is untested in the direction of")
        print("         UNKNOWN -- the confound could inflate OR deflate the effect and")
        print("         this study cannot say which. Do not report the gate as passed,")
        print("         and do not report it as failed. Report that it was not run.")
    print("-" * 78)
    return 2


if __name__ == "__main__":
    sys.exit(main())
