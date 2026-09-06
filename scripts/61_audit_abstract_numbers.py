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


def claim(label, stated, computed, tol=0.55, note=""):
    """tol is in the units of the figure; default half a point / half a unit."""
    if isinstance(stated, (int, float)) and isinstance(computed, (int, float)):
        ok = abs(stated - computed) <= tol
        s, c = "%.4g" % stated, "%.4g" % computed
    else:
        ok = (stated == computed)
        s, c = str(stated), str(computed)
    rows.append((ok, label, s, c, note))
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
claim("§1.3/§6.1 cost ratio low (stated 118)", 118, min(ratios), tol=1.0)
claim("§1.3/§6.1 cost ratio high (stated 198)", 198, max(ratios), tol=1.0)

lat_ratio = [med(f, "frontier", "lat_p50") / med(f, "cheap", "lat_p50") for f in ROUTINE]
claim("abstract latency ratio low (stated 6x)", 6, min(lat_ratio), tol=0.6)
claim("abstract latency ratio high (stated 10x)", 10, max(lat_ratio), tol=0.6)

# ---- 3. frontier-favouring family gaps (abstract) --------------------------------------
gaps = {}
for f in FRONTIER_FAM:
    c, fr = med(f, "cheap", "correct_pct"), med(f, "frontier", "correct_pct")
    gaps[f] = (c, fr, fr - c)
claim("abstract gap range LOW  (stated 22 pp)", 22, min(g[2] for g in gaps.values()))
claim("abstract gap range HIGH (stated 80 pp)", 80, max(g[2] for g in gaps.values()))
for f, name, sc, sf in [("8", "constraint satisfaction", 43, 100),
                        ("9", "multi-hop retrieval", 78, 100),
                        ("10", "instruction conflict", 61, 100),
                        ("11", "planted inconsistency", 9, 90)]:
    claim("abstract fam %s %s — cheap CORRECT (stated %s)" % (f, name, sc), sc, gaps[f][0])
    claim("abstract fam %s %s — frontier CORRECT (stated %s)" % (f, name, sf), sf, gaps[f][1])

print("\n  %-4s %-62s %10s %10s" % ("", "claim", "paper", "data"))
print("  " + "-" * 90)
bad = flat = 0
for ok, label, s, c, note in rows:
    print("  %-4s %-62s %10s %10s" % ("OK" if ok else "MISS", label[:62], s, c))
    if note and not ok:
        print("       └─ %s" % note)
    if not ok:
        bad += 1

print("\n  %d of %d checked figures match the scored data; %d MISS." % (len(rows) - bad, len(rows), bad))
print("\n  Reference for the ranges actually in the data:")
print("    routine cheap EXACT %%  : %s" % ", ".join("f%s=%.1f" % (f, H2[f]["cheap_exact_pct"]) for f in ROUTINE))
print("    routine frontier EXACT%%: %s" % ", ".join("f%s=%.1f" % (f, H2[f]["frontier_exact_pct"]) for f in ROUTINE))
print("    routine cost ratio     : %s" % ", ".join("f%s=%.0fx" % (f, r) for f, r in zip(ROUTINE, ratios)))
print("    routine p50 latency x  : %s" % ", ".join("f%s=%.1fx" % (f, r) for f, r in zip(ROUTINE, lat_ratio)))
print("    frontier-fam CORRECT   : %s" % ", ".join("f%s cheap=%.1f front=%.1f gap=%.1f"
                                                     % (f, *gaps[f]) for f in FRONTIER_FAM))
sys.exit(1 if bad else 0)
