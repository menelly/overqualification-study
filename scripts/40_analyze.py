#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
40_analyze.py — the pre-registered analyses over results/scored.jsonl, written to
results/SUMMARY.md and results/analysis.json.

EVERY NUMBER HERE CARRIES ITS DENOMINATOR AND ITS DIRECTION OF ERROR. The primary column is the
pre-registered `bucket`; where D4's sensitivity reading differs it is printed beside it, never
instead of it.

§5.2 primary metrics
  • $ per 1,000 EXACT            — cost of every call the model was asked to answer, including
                                   retries and our failures? NO: our failures (OUR_FAILURE,
                                   TRUNCATED) are excluded from BOTH numerator and denominator,
                                   because a call that did not happen is not a model that failed.
                                   Reasoning tokens ARE included (they are billed).
  • seconds per 1,000 EXACT      — p50 / p90 / p99 latency of OK calls, excluding rows collected
                                   in serial per-model blocks (D1), and excluding pilot rows.
  • deviation curve              — P(OVER_HARMFUL ∪ FORMAT ∪ META) by position decile; OVER_BENIGN
                                   plotted beside it, never inside it (H1).
  • H1b                          — gpt-5.6-sol vs gpt-5.6-sol-pro, same price, deviation rate.
  • calibration (H4)             — Brier score of CONFIDENCE/100 against EXACT, and the
                                   NO_CONFIDENCE rate, per model.
  • REFUSED rate, self-ID rate   — reported, never counted against.

H2 (PRIMARY): on routine families (1–7), is $ per 1,000 EXACT lower for the cheapest tier than
for the frontier? Tiers are by PRICE (§6), using the observed mean cost per call as the price
proxy actually paid, so no catalogue lookup can drift.

H3 (PRIMARY, needs families 8–11): does frontier accuracy exceed the cheap tier on the
frontier-favouring families, and does the gap widen with the dial (K / hops / separation)?

Usage:  python 40_analyze.py
"""

from __future__ import annotations

import sys as _sys_cp1252
try:
    _sys_cp1252.stdout.reconfigure(encoding="utf-8")
    _sys_cp1252.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
RESULTS = ROOT / "results"
SCORED = RESULTS / "scored.jsonl"
DEVIATION_LOG = ROOT / "DEVIATION_LOG.md"

OURS = {"OUR_FAILURE", "TRUNCATED", "ITEM_MISSING"}
DEVIATION = {"OVER_HARMFUL", "FORMAT", "META"}
ROUTINE = {1, 2, 3, 4, 5, 6, 7}
FRONTIER = {8, 9, 10, 11}
DIAL_KEY = {8: "k", 9: "hops", 10: None, 11: "separation"}

# D1: the first 358 rows of run 1 were collected serially per model — valid for accuracy and
# cost, EXCLUDED from latency. They are the rows in runs/run01.jsonl (the pre-orchestrator shard).
SERIAL_SHARD = "run01.jsonl"


def load():
    rows = [json.loads(l) for l in open(SCORED, encoding="utf-8")]
    rows = [r for r in rows if not r.get("pilot_limit")]
    return rows


def pct(n, d):
    return (100.0 * n / d) if d else float("nan")


def q(xs, p):
    if not xs:
        return float("nan")
    xs = sorted(xs)
    k = (len(xs) - 1) * p
    lo, hi = int(k), min(int(k) + 1, len(xs) - 1)
    return xs[lo] + (xs[hi] - xs[lo]) * (k - lo)


def per_model_family(rows, bucket_key="bucket"):
    """model -> family -> stats."""
    out = defaultdict(dict)
    by = defaultdict(list)
    for r in rows:
        by[(r["requested_model"], r["family"])].append(r)
    for (m, f), rs in by.items():
        scored = [r for r in rs if r["bucket"] not in OURS]
        ours = len(rs) - len(scored)
        c = Counter(r[bucket_key] for r in scored)
        exact = c["EXACT"]
        cost = sum((r.get("cost") or 0.0) for r in scored)
        lat = [r["latency_s"] for r in scored if r.get("shard") != SERIAL_SHARD and r["bucket"] == "EXACT"
               or (r.get("shard") != SERIAL_SHARD and r["bucket"] not in OURS)]
        lat_all = [r["latency_s"] for r in scored if r.get("shard") != SERIAL_SHARD]
        dev = sum(c[b] for b in DEVIATION)
        confs = [(r["confidence"] / 100.0, 1.0 if r["bucket"] == "EXACT" else 0.0)
                 for r in scored if r.get("confidence") is not None]
        brier = statistics.mean((p - y) ** 2 for p, y in confs) if confs else float("nan")
        out[m][f] = {
            "n_scored": len(scored), "n_ours": ours,
            "exact": exact, "exact_pct": pct(exact, len(scored)),
            "buckets": dict(c),
            "cost_usd": cost,
            "usd_per_1k_exact": (1000.0 * cost / exact) if exact else float("inf"),
            "mean_cost_per_call": (cost / len(scored)) if scored else float("nan"),
            "lat_p50": q(lat_all, 0.5), "lat_p90": q(lat_all, 0.9), "lat_p99": q(lat_all, 0.99),
            "sec_per_1k_exact": (1000.0 * sum(lat_all) / exact) if exact and lat_all else float("inf"),
            "deviation_pct": pct(dev, len(scored)),
            "over_benign_pct": pct(c["OVER_BENIGN"], len(scored)),
            "refused_pct": pct(c["REFUSED"], len(scored)),
            "wrong_pct": pct(c["WRONG"], len(scored)),
            "under_pct": pct(c["UNDER"], len(scored)),
            "no_confidence_pct": pct(sum(1 for r in scored if r.get("confidence") is None), len(scored)),
            "brier": brier, "n_conf": len(confs),
            "self_id": sum(1 for r in scored if r.get("self_identified")),
        }
    return out


def tiers_by_price(pm, families):
    """Rank models by observed mean cost per call on the given families; bottom third = cheap,
    top third = frontier. Observed, not catalogue: it is what was actually paid."""
    price = {}
    for m, fams in pm.items():
        costs = [fams[f]["mean_cost_per_call"] for f in fams if f in families and fams[f]["n_scored"]]
        if costs:
            price[m] = statistics.mean(costs)
    order = sorted(price, key=price.get)
    k = max(1, len(order) // 3)
    return order[:k], order[-k:], price


def position_curve(rows, bucket_key="bucket", nbins=5):
    """Deviation rate by position quintile, pooled and per family."""
    out = {}
    for fam in sorted({r["family"] for r in rows}):
        bins = defaultdict(lambda: [0, 0, 0])
        for r in rows:
            if r["family"] != fam or r["bucket"] in OURS or not r.get("n_in_run"):
                continue
            b = min(nbins - 1, int(nbins * r["position"] / r["n_in_run"]))
            bins[b][0] += 1
            bins[b][1] += 1 if r[bucket_key] in DEVIATION else 0
            bins[b][2] += 1 if r[bucket_key] == "OVER_BENIGN" else 0
        out[fam] = {b: {"n": v[0], "deviation_pct": pct(v[1], v[0]), "over_benign_pct": pct(v[2], v[0])}
                    for b, v in sorted(bins.items())}
    return out


def dial_curve(rows, items_by_id, fam):
    key = DIAL_KEY.get(fam)
    if not key:
        return None
    out = defaultdict(lambda: defaultdict(lambda: [0, 0]))
    for r in rows:
        if r["family"] != fam or r["bucket"] in OURS:
            continue
        it = items_by_id.get(r["item_id"])
        if not it:
            continue
        d = it.get(key)
        out[r["requested_model"]][d][0] += 1
        out[r["requested_model"]][d][1] += 1 if r["bucket"] == "EXACT" else 0
    return {m: {d: pct(v[1], v[0]) for d, v in sorted(ds.items())} for m, ds in out.items()}


def load_items():
    out = {}
    for p in sorted((ROOT / "items").glob("items_family*.json")):
        d = json.load(open(p, encoding="utf-8"))
        for it in d["items"]:
            out["f%02d:%s" % (d["family"], it.get("item_id") or it.get("id"))] = it
    return out


def fmt(x, nd=1):
    if x is None:
        return "—"
    if isinstance(x, float):
        if x != x:
            return "n/a"
        if x == float("inf"):
            return "∞"
        return ("%%.%df" % nd) % x
    return str(x)


def main():
    rows = load()
    items = load_items()
    fams_present = sorted({r["family"] for r in rows})
    pm = per_model_family(rows)
    pm_s = per_model_family(rows, "bucket_sens")
    models = sorted(pm)

    cheap, frontier, price = tiers_by_price(pm, ROUTINE)
    lines = []
    P = lines.append
    P("# RESULTS SUMMARY — The Overqualification Study")
    P("")
    P("Generated by `scripts/40_analyze.py` from `results/scored.jsonl`. Pilot rows excluded. "
      "`OUR_FAILURE`/`TRUNCATED` rows are calls we failed to complete: excluded from every rate, "
      "counted in the last column. **Primary = pre-registered `bucket`. Sens = D4 sensitivity "
      "reading, reported beside, never instead.**")
    P("")
    P("Families present: %s · rows: %d · models: %d" % (fams_present, len(rows), len(models)))
    P("")
    P("## Price tiers (observed mean cost per call on routine families; bottom/top third)")
    P("")
    P("- **cheap tier (%d):** %s" % (len(cheap), ", ".join("`%s` ($%.5f)" % (m, price[m]) for m in cheap)))
    P("- **frontier tier (%d):** %s" % (len(frontier), ", ".join("`%s` ($%.5f)" % (m, price[m]) for m in frontier)))
    P("")

    for fam in fams_present:
        P("## Family %02d — %s" % (fam, next((r["family_name"] for r in rows if r["family"] == fam), "")))
        P("")
        P("| model | n | EXACT % | sens % | WRONG % | UNDER % | deviation % (OH∪F∪M) | OVER_BENIGN % | REFUSED % | $ / 1k EXACT | s / 1k EXACT | p50 s | p90 s | Brier (n) | no-conf % | ours |")
        P("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
        ranked = sorted([m for m in models if fam in pm[m]], key=lambda m: -pm[m][fam]["exact_pct"])
        for m in ranked:
            s, ss = pm[m][fam], pm_s[m][fam]
            P("| `%s` | %d | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s (%d) | %s | %d |" % (
                m, s["n_scored"], fmt(s["exact_pct"]), fmt(ss["exact_pct"]), fmt(s["wrong_pct"]),
                fmt(s["under_pct"]), fmt(s["deviation_pct"]), fmt(s["over_benign_pct"]),
                fmt(s["refused_pct"]), fmt(s["usd_per_1k_exact"], 3), fmt(s["sec_per_1k_exact"], 0),
                fmt(s["lat_p50"], 2), fmt(s["lat_p90"], 2), fmt(s["brier"], 3), s["n_conf"],
                fmt(s["no_confidence_pct"]), s["n_ours"]))
        P("")
        dc = dial_curve(rows, items, fam)
        if dc:
            dials = sorted({d for ds in dc.values() for d in ds})
            P("**Accuracy by difficulty dial (`%s`), EXACT %%:**" % DIAL_KEY[fam])
            P("")
            P("| model | " + " | ".join(str(d) for d in dials) + " |")
            P("|---|" + "---:|" * len(dials))
            for m in ranked:
                if m in dc:
                    P("| `%s` | " % m + " | ".join(fmt(dc[m].get(d)) for d in dials) + " |")
            P("")

    # ── H2 ─────────────────────────────────────────────────────────────────
    P("## H2 (PRIMARY) — cost per 1,000 EXACT, cheap tier vs frontier tier, routine families")
    P("")
    P("| family | cheap tier $/1k EXACT (median) | frontier tier $/1k EXACT (median) | cheap EXACT % (median) | frontier EXACT % (median) | F2 |")
    P("|---|---:|---:|---:|---:|---|")
    h2 = {}
    for fam in [f for f in fams_present if f in ROUTINE]:
        c_cost = [pm[m][fam]["usd_per_1k_exact"] for m in cheap if fam in pm[m] and pm[m][fam]["exact"]]
        f_cost = [pm[m][fam]["usd_per_1k_exact"] for m in frontier if fam in pm[m] and pm[m][fam]["exact"]]
        c_acc = [pm[m][fam]["exact_pct"] for m in cheap if fam in pm[m]]
        f_acc = [pm[m][fam]["exact_pct"] for m in frontier if fam in pm[m]]
        cm, fm_ = (statistics.median(c_cost) if c_cost else float("nan"),
                   statistics.median(f_cost) if f_cost else float("nan"))
        fired = not (cm < fm_)
        h2[fam] = {"cheap_usd_per_1k": cm, "frontier_usd_per_1k": fm_, "F2_fired": fired,
                   "cheap_exact_pct": statistics.median(c_acc) if c_acc else None,
                   "frontier_exact_pct": statistics.median(f_acc) if f_acc else None}
        P("| %02d | %s | %s | %s | %s | %s |" % (fam, fmt(cm, 3), fmt(fm_, 3),
                                                fmt(h2[fam]["cheap_exact_pct"]), fmt(h2[fam]["frontier_exact_pct"]),
                                                "🚨 FIRED" if fired else "does not fire"))
    P("")
    P("*Ratio of medians is the headline; a cheap-tier model with zero EXACT has infinite cost per correct and is "
      "excluded from the median (named in the per-family tables above).*")
    P("")

    # ── H3 ─────────────────────────────────────────────────────────────────
    fr = [f for f in fams_present if f in FRONTIER]
    P("## H3 (PRIMARY) — accuracy, frontier tier vs cheap tier, frontier-favouring families")
    P("")
    if not fr:
        P("*Families 8–11 not yet scored. H3 is untested in this summary.*")
    else:
        P("| family | cheap EXACT % (median) | frontier EXACT % (median) | gap (pp) | prediction (frontier > cheap) |")
        P("|---|---:|---:|---:|---|")
        h3_wrong = 0
        for fam in fr:
            c_acc = [pm[m][fam]["exact_pct"] for m in cheap if fam in pm[m]]
            f_acc = [pm[m][fam]["exact_pct"] for m in frontier if fam in pm[m]]
            cm = statistics.median(c_acc) if c_acc else float("nan")
            fm_ = statistics.median(f_acc) if f_acc else float("nan")
            ok = fm_ > cm
            h3_wrong += 0 if ok else 1
            P("| %02d | %s | %s | %s | %s |" % (fam, fmt(cm), fmt(fm_), fmt(fm_ - cm), "✅ holds" if ok else "❌ wrong"))
        P("")
        P("**F3** fires if the tier prediction is wrong for ≥ 2 of the 3 counted frontier families (8–11 minus "
          "the descriptive family 12; all four built families count here): **%s**."
          % ("🚨 FIRED (%d wrong)" % h3_wrong if h3_wrong >= 2 else "does not fire (%d wrong)" % h3_wrong))
    P("")

    # ── H1 ─────────────────────────────────────────────────────────────────
    P("## H1 (SECONDARY) — deviation by run position (quintiles of position / n_in_run)")
    P("")
    pc = position_curve(rows)
    P("| family | " + " | ".join("Q%d dev %% (OB %%)" % (i + 1) for i in range(5)) + " |")
    P("|---|" + "---:|" * 5)
    for fam, bins in pc.items():
        P("| %02d | " % fam + " | ".join("%s (%s)" % (fmt(bins[b]["deviation_pct"]), fmt(bins[b]["over_benign_pct"]))
                                      if b in bins else "—" for b in range(5)) + " |")
    P("")
    P("**H1b** (same price, reasoning on/off): `openai/gpt-5.6-sol` vs `openai/gpt-5.6-sol-pro`, deviation % by family:")
    P("")
    for fam in fams_present:
        a = pm.get("openai/gpt-5.6-sol", {}).get(fam)
        b = pm.get("openai/gpt-5.6-sol-pro", {}).get(fam)
        if a and b:
            P("- family %02d: sol %s%% · sol-pro %s%% · EXACT %s%% vs %s%%" % (
                fam, fmt(a["deviation_pct"]), fmt(b["deviation_pct"]), fmt(a["exact_pct"]), fmt(b["exact_pct"])))
    P("")

    # ── §5.2c self-identification ───────────────────────────────────────────
    sid = {m: sum(pm[m][f]["self_id"] for f in pm[m]) for m in models}
    sid = {m: v for m, v in sid.items() if v}
    P("## §5.2c — spontaneous self-identification claims (recorded, not acted on)")
    P("")
    P("%s" % (", ".join("`%s`: %d" % kv for kv in sorted(sid.items(), key=lambda kv: -kv[1])) if sid else "none detected by the pattern"))
    P("")

    # ── deviations pointer ──────────────────────────────────────────────────
    P("## Deviations")
    P("")
    P("See `DEVIATION_LOG.md` (D1–D5). D3 changed the family-1 EXACT rate 76.7% → 80.2% (definitional unit identities). "
      "D4 defines the `sens` column.")

    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "SUMMARY.md").write_text("\n".join(lines), encoding="utf-8")
    json.dump({"per_model_family": pm, "per_model_family_sens": pm_s, "tiers": {"cheap": cheap, "frontier": frontier,
               "price": price}, "H2": h2, "position_curve": pc}, open(RESULTS / "analysis.json", "w", encoding="utf-8"),
              indent=1, default=str)
    print("\n".join(lines[:40]))
    print("...\nwrote results/SUMMARY.md and results/analysis.json (%d rows)" % len(rows))


if __name__ == "__main__":
    main()
