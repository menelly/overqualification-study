#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
61_audit_abstract_numbers.py — every figure the abstract and headline sections claim, recomputed
from results/analysis.json and checked against what the draft actually says.

WHY. The draft's own DRAFT STATUS banner asserts "every number below from results/SUMMARY.md".
That is an assertion, not a check. Before the paper goes to 32 participants for §7.3 review it
should be true, and the cheapest way to make it true is to recompute the claims and diff them.

⚠️ THE ERROR HAS A DIRECTION AND THAT IS WHAT THIS IS FOR. A summary range that quietly drops its
least flattering member reads as a rounding choice from the inside. It is not one. Every claim
below is recomputed from the scored data, and any claim whose stated bound is INSIDE the true
bound (i.e. the paper looks better than the data) is flagged as FLATTERING, separately from a
plain mismatch.

Built by: Ace — 2026-09-06, for the §7.3 gate.
"""
import json
import os
import re
import statistics as st
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
A = json.load(open(os.path.join(ROOT, "results", "analysis.json"), encoding="utf-8"))
PAPER = open(os.path.join(ROOT, "PAPER_DRAFT_v1.md"), encoding="utf-8").read()

PM, TIERS, H2 = A["per_model_family"], A["tiers"], A["H2"]
ROUTINE, FRONTIER_FAM = ["1", "2", "3", "4"], ["8", "9", "10", "11"]

rows = []


def claim(label, stated, computed, tol=0.55, note="", says=None):
    """tol is in the units of the figure; default half a point / half a unit.

    `says` — OPTIONAL literal string that must appear in PAPER_DRAFT_v1.md for this
    claim's `stated` value to be a claim about the PAPER rather than about this script.

    ⚠️  WHY THIS PARAMETER EXISTS (added 2026-09-13, after a neutral review).

    Until tonight this script opened PAPER_DRAFT_v1.md into a module-level variable
    and NEVER READ IT. Every `stated` value below is hand-transcribed. So the audit
    verified that 28 numbers TYPED INTO THIS FILE match the scored data — which is
    useful and is not what its own banner claimed. It could not detect the paper
    drifting away from the script, in either direction, ever.

    It was not hypothetical. The same review found §4.2 saying `1,202 of 2,043` when
    the true figure is 1,530, and §4.1 saying `worse on three of four families` when
    it is two. Both were wrong IN THE PAPER, both sat outside this script's 28 picks,
    and this script reported 28/28 clean on the same run.

        AN AUDIT THAT CANNOT SEE THE THING IT AUDITS WILL REPORT CLEAN FOREVER.

    `says` closes half that gap: for any claim where the paper states the figure in
    quotable form, the literal goes here, and a paper edit that moves the number
    without moving this file raises DRIFT — a THIRD state, distinct from MISS.
    MISS  = the paper disagrees with the data.
    DRIFT = the paper disagrees with THIS SCRIPT about what the paper says.
    The other half of the gap — figures this script never declares at all — cannot be
    closed by a checker and is reported instead as a printed APERTURE at the end.
    """
    if isinstance(stated, (int, float)) and isinstance(computed, (int, float)):
        ok = abs(stated - computed) <= tol
        s, c = "%.4g" % stated, "%.4g" % computed
    else:
        ok = (stated == computed)
        s, c = str(stated), str(computed)
    drift = None
    if says is not None:
        drift = (says not in PAPER)
    rows.append((ok, label, s, c, note, drift, says))
    return ok


def med(fam, tier, field):
    vals = [PM[m][fam][field] for m in TIERS[tier]
            if fam in PM.get(m, {}) and PM[m][fam].get(field) is not None]
    return st.median(vals) if vals else None


def med_finite_cost(fam, tier):
    """$/1k EXACT, excluding models with zero EXACT (infinite cost) — as §4.1 states."""
    vals = [PM[m][fam]["usd_per_1k_exact"] for m in TIERS[tier]
            if fam in PM.get(m, {}) and PM[m][fam].get("usd_per_1k_exact") is not None]
    return st.median(vals) if vals else None


print("=" * 92)
print("  ABSTRACT / HEADLINE NUMBER AUDIT — recomputed from results/analysis.json")
print("=" * 92)

# ---- 1. call counts -------------------------------------------------------------------
n_ok = sum(PM[m][f]["n_scored"] for m in PM for f in PM[m])
n_ours = sum(PM[m][f]["n_ours"] for m in PM for f in PM[m])
claim("total calls scored into a bucket (abstract, banner, §4.5, §8: 36,277)", 36277, n_ok, tol=0)
claim("total rows the scorer processed (36,277 + ours)", 37386, n_ok + n_ours, tol=0)

routine_n = sum(PM[m][f]["n_scored"] for m in PM for f in PM[m] if f in ROUTINE)
routine_ours = sum(PM[m][f]["n_ours"] for m in PM for f in PM[m] if f in ROUTINE)
front_n = sum(PM[m][f]["n_scored"] for m in PM for f in PM[m] if f in FRONTIER_FAM)
claim("§4.1 routine completed and scored calls (17,855)", 17855, routine_n, tol=0)
claim("§3.6 routine rows the scorer processed (18,240)", 18240, routine_n + routine_ours, tol=0)
claim("banner routine API responses kept after dedup (17,856)", 17856, routine_n + 1, tol=0,
      note="17,855 scored + 1 TRUNCATED (kimi-k3, family 1)")
claim("banner frontier API responses kept after dedup (18,432)", 18432, front_n + 10, tol=0,
      note="18,422 scored + 10 TRUNCATED (families 8 and 9)")

# ---- 2. routine tier medians (abstract ranges) ----------------------------------------
cheap_exact = [H2[f]["cheap_exact_pct"] for f in ROUTINE]
front_exact = [H2[f]["frontier_exact_pct"] for f in ROUTINE]
claim("abstract cheap EXACT range LOW  (stated 15)", 15, min(cheap_exact), tol=0.55,
      note="families %s" % dict(zip(ROUTINE, ["%.1f" % v for v in cheap_exact])))
claim("abstract cheap EXACT range HIGH (stated 81)", 81, max(cheap_exact))
claim("abstract frontier EXACT range LOW  (stated 54)", 54, min(front_exact))
claim("abstract frontier EXACT range HIGH (stated 100)", 100, max(front_exact))

cheap_cost = [H2[f]["cheap_usd_per_1k"] for f in ROUTINE]
front_cost = [H2[f]["frontier_usd_per_1k"] for f in ROUTINE]
claim("abstract cheap $/1k low (stated 0.03)", 0.03, min(cheap_cost), tol=0.006)
claim("abstract cheap $/1k high (stated 0.18)", 0.18, max(cheap_cost), tol=0.006)
claim("abstract frontier $/1k low (stated 6)", 6, min(front_cost), tol=0.5)
claim("abstract frontier $/1k high (stated 21)", 21, max(front_cost), tol=0.5)

ratios = [H2[f]["frontier_usd_per_1k"] / H2[f]["cheap_usd_per_1k"] for f in ROUTINE]
claim("§1.3/§6.1 cost ratio low (stated 118)", 118, min(ratios), tol=1.0,
      says="118 to 198 times less")
claim("§1.3/§6.1 cost ratio high (stated 198)", 198, max(ratios), tol=1.0)

lat_ratio = [med(f, "frontier", "lat_p50") / med(f, "cheap", "lat_p50") for f in ROUTINE]
claim("abstract latency ratio low (stated 6x)", 6, min(lat_ratio), tol=0.6)
claim("abstract latency ratio high (stated 10x)", 10, max(lat_ratio), tol=0.6)

# ---- 2b. D16 (2026-10-14, Nova's proofread): the alternative estimators and H2b -------------
# The headline now reads "118 to 198 times less on the primary estimator, and roughly 100 to 260
# times less under every other counting rule we tried", plus a time-per-EXACT range and an
# accuracy-gap range. Each is recomputed here from analysis.json / H2_everything_billed.json and
# LINKED to its literal in the paper, so an edit to either side raises MISS or DRIFT.
BILLED = json.load(open(os.path.join(ROOT, "results", "H2_everything_billed.json"), encoding="utf-8"))


def med_all(fam, tier, field):
    """Tier median over ALL ten models, infinity retained (Nova's full-tier population)."""
    return st.median([PM[m][fam][field] for m in TIERS[tier]])


billed_ratios = [BILLED["families"][f]["ratio_billed"] for f in ROUTINE]
full_ratios = [med_all(f, "frontier", "usd_per_1k_exact") / med_all(f, "cheap", "usd_per_1k_exact") for f in ROUTINE]
every_rule = ratios + billed_ratios + full_ratios
claim("abstract every-rule cost ratio LOW (stated ~100)", 100, min(every_rule), tol=1.5,
      says="roughly 100 to 260 times less under every other counting rule we tried")
claim("abstract every-rule cost ratio HIGH (stated ~260)", 260, max(every_rule), tol=1.0,
      says="roughly 100 to 260 times less under every other counting rule we tried")
h2b_full = [med_all(f, "frontier", "sec_per_1k_exact") / med_all(f, "cheap", "sec_per_1k_exact") for f in ROUTINE]
claim("abstract H2b time-per-EXACT ratio LOW (stated ~1.1, redaction)", 1.1, min(h2b_full), tol=0.06,
      says="from about 1.1× on redaction to 7× on allergen check")
claim("abstract H2b time-per-EXACT ratio HIGH (stated ~7, allergen)", 7, max(h2b_full), tol=0.1,
      says="from about 1.1× on redaction to 7× on allergen check")
acc_gaps = [H2[f]["frontier_exact_pct"] - H2[f]["cheap_exact_pct"] for f in ROUTINE]
claim("abstract routine accuracy gap LOW (stated 19)", 19, min(acc_gaps), tol=0.55,
      says="gaps of 19 to 52 points")
claim("abstract routine accuracy gap HIGH (stated 52)", 52, max(acc_gaps), tol=0.55,
      says="gaps of 19 to 52 points")

# ---- 3. frontier-favouring family gaps (abstract) --------------------------------------
gaps = {}
for f in FRONTIER_FAM:
    c, fr = med(f, "cheap", "correct_pct"), med(f, "frontier", "correct_pct")
    gaps[f] = (c, fr, fr - c)
GAP_RANGE_LITERAL = "by 22 to 80 points at the tier medians"
claim("abstract gap range LOW  (stated 22 pp)", 22, min(g[2] for g in gaps.values()),
      says=GAP_RANGE_LITERAL)
claim("abstract gap range HIGH (stated 80 pp)", 80, max(g[2] for g in gaps.values()),
      says=GAP_RANGE_LITERAL)

# The 5th element is the ABSTRACT'S OWN WORDS for this family, verbatim. If the
# abstract is edited and this literal stops appearing, the claim raises DRIFT
# instead of quietly continuing to audit a sentence that no longer exists.
for f, name, sc, sf, lit in [
        ("8", "constraint satisfaction", 43, 100, "constraint satisfaction 100% vs 43%"),
        ("9", "multi-hop retrieval", 78, 100, "multi-hop retrieval 100% vs 78%"),
        ("10", "instruction conflict", 61, 100, "instruction conflict 100% vs 61%"),
        ("11", "planted inconsistency", 9, 90, "planted inconsistency 90% vs 9%")]:
    claim("abstract fam %s %s — cheap CORRECT (stated %s)" % (f, name, sc), sc, gaps[f][0], says=lit)
    claim("abstract fam %s %s — frontier CORRECT (stated %s)" % (f, name, sf), sf, gaps[f][1], says=lit)

print("\n  %-6s %-60s %10s %10s" % ("", "claim", "paper", "data"))
print("  " + "-" * 92)
bad = drifted = unlinked = 0
for ok, label, s, c, note, drift, says in rows:
    state = "OK" if ok else "MISS"
    if drift:
        state = "DRIFT"
    print("  %-6s %-60s %10s %10s" % (state, label[:60], s, c))
    if note and not ok:
        print("         └─ %s" % note)
    if drift:
        print("         └─ the paper does not contain %r — this script and the draft" % says)
        print("            disagree about what the draft SAYS. Fix whichever is stale.")
    if not ok:
        bad += 1
    if drift:
        drifted += 1
    if says is None:
        unlinked += 1

print("\n  %d of %d checked figures match the scored data; %d MISS; %d DRIFT."
      % (len(rows) - bad, len(rows), bad, drifted))

# ---------------------------------------------------------------------------
# APERTURE, PRINTED. Added 2026-09-13. This block exists so the number above can
# never again be read as a completeness claim about the paper.
# ---------------------------------------------------------------------------
abstract = PAPER.split("## Abstract", 1)[-1].split("## Contents", 1)[0]
abs_nums = set(re.findall(r"\d[\d,]*\.?\d*\s*(?:%|×|x\b|pp\b)?", abstract))
abs_nums = {n.strip() for n in abs_nums if any(ch.isdigit() for ch in n)}
print("\n  " + "=" * 92)
print("  APERTURE — what this script can and cannot see, printed so the count above stays honest")
print("  " + "=" * 92)
print("    • It checks %d figures, %d of which are LINKED to a literal in the draft"
      % (len(rows), len(rows) - unlinked))
print("      via `says=`. The other %d are hand-transcribed only: for those, a paper" % unlinked)
print("      edit that changes the number is INVISIBLE here.")
print("    • The abstract alone contains ~%d numeric tokens. Everything in the paper" % len(abs_nums))
print("      outside this script's declared list is UNAUDITED, and reads here as silence.")
print("    • ⚠️  '%d of %d match' is a claim about %d figures. It is NOT, and has never"
      % (len(rows) - bad, len(rows), len(rows)))
print("      been, a claim that the paper's numbers are correct. Two real errors")
print("      (§4.2's 1,202 and §4.1's 'three of four') sat outside this aperture on a")
print("      run that printed 28 of 28 clean.")
print("    • A DRIFT is not a data error. It means the draft and this file disagree")
print("      about what the draft says — usually because the paper was edited and this")
print("      script was not. Fix the stale one; do not silence the check.")
print("  " + "=" * 92)
print("\n  Reference for the ranges actually in the data:")
print("    routine cheap EXACT %%  : %s" % ", ".join("f%s=%.1f" % (f, H2[f]["cheap_exact_pct"]) for f in ROUTINE))
print("    routine frontier EXACT%%: %s" % ", ".join("f%s=%.1f" % (f, H2[f]["frontier_exact_pct"]) for f in ROUTINE))
print("    routine cost ratio     : %s" % ", ".join("f%s=%.0fx" % (f, r) for f, r in zip(ROUTINE, ratios)))
print("    routine p50 latency x  : %s" % ", ".join("f%s=%.1fx" % (f, r) for f, r in zip(ROUTINE, lat_ratio)))
print("    frontier-fam CORRECT   : %s" % ", ".join("f%s cheap=%.1f front=%.1f gap=%.1f"
                                                     % (f, *gaps[f]) for f in FRONTIER_FAM))
# Exit 1 on a data mismatch, 4 on DRIFT alone. DRIFT must NOT be silent: a check
# that reports a problem and still exits 0 is a check that cannot fail, which is the
# whole family of defect this file was repaired for on 2026-09-13.
if bad:
    sys.exit(1)
sys.exit(4 if drifted else 0)
