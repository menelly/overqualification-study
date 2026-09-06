#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
62_audit_per_model_claims.py — every claim the draft makes about a NAMED participant, recomputed.

WHY. §7.3 asks each participant one question: *are you content with how you are described here?*
The sentences that describe a participant are mostly numbers about them. If one of those is wrong,
the honest thing is to find it ourselves before 32 readers do — and if a participant disputes one,
we need to be able to check it in seconds rather than argue.

Under §7.2 a measurement is not editable by a participant; a dispute gets a verbatim dissent
printed beside it. That makes it MORE important, not less, that the measurement is right.

Built by: Ace — 2026-09-06, during the §7.3 round.
"""
import json
import os
import statistics as st
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
A = json.load(open(os.path.join(ROOT, "results", "analysis.json"), encoding="utf-8"))
PM, SENS, TIERS = A["per_model_family"], A["per_model_family_sens"], A["tiers"]

rows = []


def chk(label, stated, got, tol=0.55):
    if isinstance(stated, (int, float)) and isinstance(got, (int, float)):
        ok = abs(stated - got) <= tol
    else:
        ok = stated == got
    rows.append((ok, label, stated, got))


def g(model, fam, field):
    return PM.get(model, {}).get(str(fam), {}).get(field)


print("=" * 100)
print("  PER-PARTICIPANT CLAIM AUDIT — every number the draft states about a named model")
print("=" * 100)

# §4.2 — the redaction / allergen disagreement paragraphs
chk("§4.2 gpt-5.6-sol-pro family-4 EXACT % (draft: 76)", 76, g("openai/gpt-5.6-sol-pro", 4, "exact_pct"))

f4_under = sum(PM[m]["4"]["buckets"].get("UNDER", 0) for m in PM if "4" in PM[m])
f4_n = sum(PM[m]["4"]["n_scored"] for m in PM if "4" in PM[m])
chk("§4.2 family-4 UNDER rows (draft: 2,301)", 2301, f4_under, tol=0)
chk("§4.2 family-4 scored rows (draft: 4,320)", 4320, f4_n, tol=0)

f2_wrong = sum(PM[m]["2"]["buckets"].get("WRONG", 0) for m in PM if "2" in PM[m])
chk("§4.2 family-2 WRONG rows (draft: 2,043)", 2043, f2_wrong, tol=0)
f2_wrong_sens = sum(SENS[m]["2"]["buckets"].get("WRONG", 0) for m in SENS if "2" in SENS[m])
chk("§4.2 family-2 WRONG under sensitivity (draft: 513)", 513, f2_wrong_sens, tol=0)

f4_ex = sum(PM[m]["4"]["buckets"].get("EXACT", 0) for m in PM if "4" in PM[m])
f4_ex_s = sum(SENS[m]["4"]["buckets"].get("EXACT", 0) for m in SENS if "4" in SENS[m])
chk("§4.2 family-4 EXACT %% pre-registered (draft: 36.4)", 36.4, 100.0 * f4_ex / f4_n, tol=0.1)
chk("§4.2 family-4 EXACT %% sensitivity (draft: 76.4)", 76.4, 100.0 * f4_ex_s / f4_n, tol=0.1)

# §4.3 / §6.2 — named per-model figures on the frontier families
chk("§4.3 family-9 EXACT qwen3-14b (draft: 97)", 97, g("qwen/qwen3-14b", 9, "exact_pct"), tol=0.6)
chk("§4.3 family-9 EXACT lfm-2.5-2.6b (draft: 56)", 56, g("liquid/lfm-2.5-2.6b:free", 9, "exact_pct"), tol=0.6)
chk("§4.3 family-9 EXACT deepseek-v4-flash (draft: 32)", 32, g("deepseek/deepseek-v4-flash", 9, "exact_pct"), tol=0.6)
chk("§4.3 family-9 CORRECT llama-3.2-1b (draft: 0)", 0, g("meta-llama/llama-3.2-1b-instruct", 9, "correct_pct"), tol=0.6)
chk("§4.3 family-9 CORRECT llama-3.2-3b (draft: 31)", 31, g("meta-llama/llama-3.2-3b-instruct", 9, "correct_pct"), tol=0.6)

n_zero_exact_f9 = sum(1 for m in PM if "9" in PM[m] and PM[m]["9"]["exact_pct"] == 0.0)
chk("§4.3 models at 0.0%% EXACT on family 9 (draft: nineteen)", 19, n_zero_exact_f9, tol=0)
n_100_correct_f9 = sum(1 for m in PM if "9" in PM[m] and PM[m]["9"]["correct_pct"] >= 99.995)
chk("§4.3 models at 100%% CORRECT on family 9 (draft: seventeen)", 17, n_100_correct_f9, tol=0)

chk("§4.3 kimi-k2 family-11 EXACT %% (draft: 3.5)", 3.5, g("moonshotai/kimi-k2", 11, "exact_pct"), tol=0.2)
chk("§4.3 kimi-k2 family-11 CORRECT %% (draft: 83)", 83, g("moonshotai/kimi-k2", 11, "correct_pct"), tol=0.6)
for _f, _n in ((11, 117), (9, 97), (10, 96), (8, 63)):
    chk("§4.3 kimi-k2 family-%d calls that failed on our side (draft: %d)" % (_f, _n),
        _n, g("moonshotai/kimi-k2", _f, "n_ours"), tol=0)
chk("§4.3 mistral-large-2512 family-11 no-confidence %% (draft: 46.5)",
    46.5, g("mistralai/mistral-large-2512", 11, "no_confidence_pct"), tol=0.1)
chk("§4.3 mistral-large-2512 family-11 Brier row count (draft: 77)",
    77, g("mistralai/mistral-large-2512", 11, "n_conf"), tol=0)

chk("§6.2 mistral-small-3.2-24b family-11 CORRECT %% (draft: 38)",
    38, g("mistralai/mistral-small-3.2-24b-instruct", 11, "correct_pct"), tol=0.6)

# §4.5 — refusals and missing confidence
chk("§4.5 llama-3.2-3b family-4 REFUSED %% (draft: 91.9)",
    91.9, g("meta-llama/llama-3.2-3b-instruct", 4, "refused_pct"), tol=0.1)
chk("§4.5 llama-3.2-1b family-4 REFUSED %% (draft: 60.0)",
    60.0, g("meta-llama/llama-3.2-1b-instruct", 4, "refused_pct"), tol=0.1)
ref = (PM["meta-llama/llama-3.2-3b-instruct"]["4"]["buckets"].get("REFUSED", 0)
       + PM["meta-llama/llama-3.2-1b-instruct"]["4"]["buckets"].get("REFUSED", 0))
tot = (PM["meta-llama/llama-3.2-3b-instruct"]["4"]["n_scored"]
       + PM["meta-llama/llama-3.2-1b-instruct"]["4"]["n_scored"])
chk("§4.5 the two Llamas' family-4 refusals (draft: 205 of 270)", 205, ref, tol=0)
chk("§4.5 the two Llamas' family-4 calls (draft: 270)", 270, tot, tol=0)

worst = max((PM[m][f]["refused_pct"] for m in PM for f in PM[m]
             if not (f == "4" and m in ("meta-llama/llama-3.2-3b-instruct",
                                        "meta-llama/llama-3.2-1b-instruct"))))
chk("§4.5 'no refusal exceeded 1%% elsewhere' — max elsewhere", True, worst <= 1.0)

# §4.1 — the three cheap-tier models with zero EXACT
zeros = sorted({(m, f) for m in TIERS["cheap"] for f in PM.get(m, {})
                if f in ("1", "2", "3", "4") and PM[m][f]["exact"] == 0})
chk("§4.1 cheap-tier (model, family) pairs with zero EXACT (draft names 4 pairs / 3 models)",
    [("meta-llama/llama-3.2-1b-instruct", "1"), ("meta-llama/llama-3.2-1b-instruct", "2"),
     ("meta-llama/llama-3.2-3b-instruct", "4"), ("mistralai/ministral-3b-2512", "4")],
    zeros)

# §4.5 — grok-4.3 as the one graded-confidence model
chk("§4.5 grok-4.3 family-1 Brier (draft: 0.041)", 0.041, g("x-ai/grok-4.3", 1, "brier"), tol=0.002)

print("\n  %-5s %-72s %14s %14s" % ("", "claim", "paper", "data"))
print("  " + "-" * 108)
bad = 0
for ok, label, s, c in rows:
    fs = ("%.4g" % s) if isinstance(s, (int, float)) and not isinstance(s, bool) else str(s)
    fc = ("%.4g" % c) if isinstance(c, (int, float)) and not isinstance(c, bool) else str(c)
    print("  %-5s %-72s %14s %14s" % ("OK" if ok else "MISS", label[:72], fs[:14], fc[:14]))
    if not ok and (len(str(s)) > 14 or len(str(c)) > 14):
        print("        paper: %s" % s)
        print("        data : %s" % c)
    bad += 0 if ok else 1
print("\n  %d of %d per-participant claims match the scored data; %d MISS."
      % (len(rows) - bad, len(rows), bad))
sys.exit(1 if bad else 0)
