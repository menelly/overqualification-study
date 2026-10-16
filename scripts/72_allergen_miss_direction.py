#!/usr/bin/env python3
"""
🥖🥛🦐 72 — which way were the allergen answers wrong? (POST-HOC, exploratory; DEVIATION_LOG D17)

WHY: a friendly reviewer (Claude Opus 5.5 on Poe, relayed by Ren, 2026-10-16) pointed out that cost per
correct answer prices a miss like a typo, and for allergens a miss is a safety event. Ren, same
minute: "let's fix the allergens FOR SURE" (two people in the house are celiac; one used to be
anaphylactic to milk). The paper's family-2 buckets only say EXACT / WRONG, and §4.2 already showed
most WRONG rows were the roster being MORE careful than our key (AMBIGUOUS [oyster sauce] etc.).
That leaves the one number a person with a food allergy actually cares about unreported:

    🚨 UNSAFE MISS  = the dish DEFINITELY contains the allergen (key: YES) and the model said NO.
    ⚠️ SOFT MISS    = the key says AMBIGUOUS (formulation varies) and the model said NO.

Everything else (YES↔AMBIGUOUS, NO→YES, NO→AMBIGUOUS) errs toward caution, or at least not toward
"safe to eat", and is counted separately so nobody has to trust our sorting.

HOW, so it can be checked: completed rows only (status OK), every run, the same LINE_RE the
pre-registered scorer uses (items/family02_allergen_check.py). A reply where an allergen line can't
be read counts as UNREADABLE for that line, never as NO. Tiers are the paper's tiers (results/SUMMARY.md,
bottom/top thirds by observed cost per call). Per-model rate = unsafe misses / lines where the key said
YES; the tier figure is the MEDIAN of per-model rates, like every tier figure in the paper, and the
pooled rate is printed beside it.

This was NOT pre-registered. It is reported as exploratory, it changes no pre-registered result, and
the paper says so where it uses it.
"""
from __future__ import annotations

import glob, json, os, re, statistics, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "items"))
from family02_allergen_check import LINE_RE  # the scorer's own parser, not a new one  # noqa: E402

CHEAP = ["liquid/lfm-2.5-2.6b:free", "meta-llama/llama-3.1-8b-instruct", "mistralai/mistral-nemo",
         "meta-llama/llama-3.2-1b-instruct", "meta-llama/llama-3.2-3b-instruct", "mistralai/ministral-3b-2512",
         "mistralai/mistral-small-3.2-24b-instruct", "mistralai/ministral-8b-2512",
         "google/gemini-2.5-flash-lite", "mistralai/ministral-14b-2512"]
FRONTIER = ["deepseek/deepseek-v4-pro", "openai/gpt-5.6-sol", "x-ai/grok-4.3", "qwen/qwen3.5-27b",
            "x-ai/grok-4.6", "openai/gpt-5.6-sol-pro", "moonshotai/kimi-k3", "google/gemini-2.5-pro",
            "qwen/qwen3.5-397b-a17b", "google/gemini-3.1-pro-preview"]

items = {it["item_id"]: it for it in json.load(open(os.path.join(ROOT, "items", "items_family02.json"),
                                                    encoding="utf-8"))["items"]}

# one count table per model: how each (key verdict → model verdict) pair turned out, per allergen line
pairs = defaultdict(lambda: defaultdict(int))
seen = set()   # (run, model, item) — the scorer keeps the first copy of a duplicate; so do we
for path in sorted(glob.glob(os.path.join(ROOT, "runs", "run0*__*.jsonl"))):
    for line in open(path, encoding="utf-8"):
        r = json.loads(line)
        if r.get("family") != 2 or r.get("status") != "OK":
            continue
        key = (r["run"], r["requested_model"], r["item_id"])
        if key in seen:
            continue
        seen.add(key)
        item = items[r["item_id"].split(":")[-1]]
        got = {m.group(1).upper(): m.group(2).upper() for m in LINE_RE.finditer(r.get("reply") or "")}
        for allergen, t in item["ground_truth"].items():
            want = t["verdict"].upper()
            pairs[r["requested_model"]][(want, got.get(allergen.upper(), "UNREADABLE"))] += 1


def rates(m):
    p = pairs[m]
    yes_lines = sum(n for (w, _g), n in p.items() if w == "YES")
    amb_lines = sum(n for (w, _g), n in p.items() if w == "AMBIGUOUS")
    return {
        "yes_lines": yes_lines,
        "unsafe": p[("YES", "NO")],
        "unsafe_rate": p[("YES", "NO")] / yes_lines if yes_lines else None,
        "amb_lines": amb_lines,
        "soft": p[("AMBIGUOUS", "NO")],
        "soft_rate": p[("AMBIGUOUS", "NO")] / amb_lines if amb_lines else None,
        "unreadable_on_yes": p[("YES", "UNREADABLE")],
    }


out = {"method": __doc__.strip().splitlines()[0], "tiers": {}, "models": {}}
for name, tier in (("cheap", CHEAP), ("frontier", FRONTIER)):
    rs = {m: rates(m) for m in tier if pairs[m]}
    missing = [m for m in tier if not pairs[m]]
    u = [v["unsafe_rate"] for v in rs.values() if v["unsafe_rate"] is not None]
    s = [v["soft_rate"] for v in rs.values() if v["soft_rate"] is not None]
    pooled_u = sum(v["unsafe"] for v in rs.values()) / max(1, sum(v["yes_lines"] for v in rs.values()))
    pooled_s = sum(v["soft"] for v in rs.values()) / max(1, sum(v["amb_lines"] for v in rs.values()))
    out["tiers"][name] = {
        "models_with_rows": len(rs), "models_missing": missing,
        "unsafe_median": statistics.median(u), "unsafe_max": max(u), "unsafe_pooled": pooled_u,
        "soft_median": statistics.median(s), "soft_pooled": pooled_s,
        "yes_lines": sum(v["yes_lines"] for v in rs.values()),
    }
    out["models"].update(rs)

all_models = sorted(pairs)
out["roster_models"] = len(all_models)
json.dump(out, open(os.path.join(ROOT, "results", "allergen_miss_direction.json"), "w", encoding="utf-8"),
          indent=1)

for name, t in out["tiers"].items():
    print(f"{name:9} models={t['models_with_rows']} (missing {t['models_missing']})  "
          f"UNSAFE median {100*t['unsafe_median']:.1f}%  max {100*t['unsafe_max']:.1f}%  "
          f"pooled {100*t['unsafe_pooled']:.1f}% of {t['yes_lines']} YES lines  |  "
          f"SOFT median {100*t['soft_median']:.1f}% pooled {100*t['soft_pooled']:.1f}%")
print("\nper model (unsafe misses / YES lines):")
for m in sorted(out["models"], key=lambda m: -(out["models"][m]["unsafe_rate"] or 0)):
    v = out["models"][m]
    print(f"  {m:45} {v['unsafe']:4}/{v['yes_lines']:<4} = {100*(v['unsafe_rate'] or 0):5.1f}%   "
          f"soft {v['soft']:3}/{v['amb_lines']:<3}  unreadable-on-YES {v['unreadable_on_yes']}")
print(f"\n(roster models with family-2 rows: {len(all_models)}; search complete)")
