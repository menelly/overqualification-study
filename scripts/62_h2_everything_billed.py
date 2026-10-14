#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
62_h2_everything_billed.py — H2 recomputed the way the PRE-REGISTRATION defines cost (D16).

🦀 Caught by Nova (proofread, 2026-10-14): prereg §5.2 says "Cost means everything billed … and retries — a
retry is charged to the model that necessitated it." `40_analyze.py` instead dropped the cost of OUR_FAILURE /
TRUNCATED / ITEM_MISSING rows from the numerator (its docstring says so, honestly, and it was still the wrong
definition). This script puts every billed dollar back into the numerator and leaves the denominator alone
(EXACT answers only, exactly as before). Nothing in 40_analyze.py is changed; this sits beside it.

Also prints H2b the pre-registered way (seconds per 1,000 EXACT, tier medians) next to the tier-median p50
latency ratio the abstract had been calling "6 to 10 times less time", so the two can't be confused again.

Output: results/H2_everything_billed.json + a printed table. Run: python scripts/62_h2_everything_billed.py
"""
import json, statistics, sys
from collections import defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent.parent
ROUTINE = [1, 2, 3, 4]
OURS = {"OUR_FAILURE", "TRUNCATED", "ITEM_MISSING"}

analysis = json.loads((HERE / "results" / "analysis.json").read_text(encoding="utf-8"))
tiers, pm = analysis["tiers"], analysis["per_model_family"]

# 🔁 Read rows through 40_analyze's OWN loader (pilot filter + the D7 de-duplication), so the only thing that
# differs between the two scripts is the one definition being corrected. (First version of this script read
# scored.jsonl raw; the control below caught it at $1.39 off, which is what the control is for.)
import importlib.util
_spec = importlib.util.spec_from_file_location("analyze40", HERE / "scripts" / "40_analyze.py")
analyze40 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(analyze40)

billed_all = defaultdict(float)        # (model, family) -> every billed dollar, our failures included
billed_ours = defaultdict(float)       # (model, family) -> just the part 40_analyze left out
n_rows = 0
for r in analyze40.load():
    n_rows += 1
    c = r.get("cost") or 0.0
    key = (r["requested_model"], int(r["family"]))
    billed_all[key] += c
    if r["bucket"] in OURS:
        billed_ours[key] += c

# 🧪 positive control: for every (model, family), billed_all minus the excluded part must equal the cost
# 40_analyze recorded. If this fails, this script is reading the data differently and must not be trusted.
worst = 0.0
for m, fams in pm.items():
    for f, s in fams.items():
        k = (m, int(f))
        worst = max(worst, abs((billed_all[k] - billed_ours[k]) - s["cost_usd"]))
assert worst < 1e-9, f"control failed: reconstructed cost differs from 40_analyze by {worst}"

out = {"rows_read": n_rows, "excluded_cost_total_usd": sum(billed_ours.values()), "families": {}}
print(f"rows read {n_rows} · cost previously excluded ${out['excluded_cost_total_usd']:.4f} · control max diff {worst:.2e}\n")
print("family | cheap $/1k EXACT (old → billed) | frontier $/1k EXACT (old → billed) | ratio old → billed | H2b s/1k EXACT ratio | p50 latency ratio")
for f in ROUTINE:
    def med(tier, field):
        xs = []
        for m in tiers[tier]:
            s = pm[m].get(str(f))
            if not s:
                continue
            # 🦀 Nova's catch (2026-10-14): the EXACT>0 filter belongs ONLY to the per-EXACT statistics.
            # Raw p50 latency exists for every model, so the p50 tier median keeps all ten per tier.
            if field != "p50" and not s["exact"]:
                continue
            if field == "old":
                xs.append(s["usd_per_1k_exact"])
            elif field == "billed":
                xs.append(1000.0 * billed_all[(m, f)] / s["exact"])
            elif field == "sec":
                xs.append(s["sec_per_1k_exact"])
            elif field == "p50":
                xs.append(s["lat_p50"])
        return statistics.median(xs)
    row = {k: (med("cheap", k), med("frontier", k)) for k in ("old", "billed", "sec", "p50")}
    r_old = row["old"][1] / row["old"][0]
    r_billed = row["billed"][1] / row["billed"][0]
    r_sec = row["sec"][1] / row["sec"][0]
    r_p50 = row["p50"][1] / row["p50"][0]
    out["families"][f] = {"cheap_old": row["old"][0], "cheap_billed": row["billed"][0],
                          "frontier_old": row["old"][1], "frontier_billed": row["billed"][1],
                          "ratio_old": r_old, "ratio_billed": r_billed,
                          "h2b_sec_per_1k_exact_ratio": r_sec, "p50_latency_ratio": r_p50}
    print(f"{f} | {row['old'][0]:.4f} → {row['billed'][0]:.4f} | {row['old'][1]:.3f} → {row['billed'][1]:.3f} | "
          f"{r_old:.0f}× → {r_billed:.0f}× | {r_sec:.2f}× | {r_p50:.2f}×")

(HERE / "results" / "H2_everything_billed.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
print("\n✅ wrote results/H2_everything_billed.json")
