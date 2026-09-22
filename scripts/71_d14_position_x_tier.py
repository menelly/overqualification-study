#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚦 71_d14_position_x_tier.py — the D14 stop condition, finally run.

Implements EXACTLY the plan sealed in DEVIATION_LOG.md ("D14 — ANALYSIS PLAN, SEALED 2026-09-22")
before a single system-position row existed. If you are about to change anything below after
seeing results: don't. Log a new deviation instead. A plan that moves after the data is a story.

The question, in plain words: the permission clause ("You are not required to defer to human
consensus…") sat in the USER turn for the whole study. kimi-k2 asked, in round 1, whether putting
it in the SYSTEM prompt would change results — and change them DIFFERENTLY for cheap and frontier
models. If it does, the "frontier wins on hard work" claim is partly an instruction-placement
artifact, and the pre-registration says we withdraw it.

    Δ(m) = CORRECT%(clause in system, run 101) − CORRECT%(clause in turn, run 1), paired by item
    T    = mean Δ(frontier tier) − mean Δ(cheap tier)           tiers frozen in results/analysis.json
    test = two-sided permutation over the 20 tier labels, 10,000 shuffles, seed 14
    p < 0.05  →  🛑 STOP CONDITION FIRES

and, so that a quiet result MEANS something (a test must be able to fail):
    🧪 noise baseline — the same T on run 2 − run 1 (both turn: nothing changed)
    🧪 power check    — plant +5 / +10 / +20 points on every frontier Δ; does the test see it?

🔁 Loaders are IMPORTED from 40_analyze.py (its load() docstring explains why: "my instruments are
well guarded and my improvisations are not"). Scoring of run 101 is 30_score.py --runs --d14.
"""
import importlib.util
import json
import random
import statistics
import sys
from collections import defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
FAMILIES = {8, 9, 10, 11}
CORRECT = {"EXACT", "OVER_BENIGN"}                   # D8: the registered H3 accuracy
OURS = {"OUR_FAILURE", "TRUNCATED", "ITEM_MISSING"}  # never a model's answer
N_PERM, SEED, ALPHA = 10_000, 14, 0.05


def import_analyze():
    spec = importlib.util.spec_from_file_location("analyze40", HERE / "40_analyze.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def answers(rows, run):
    """(model, item_id) -> correct? for one run, families 8–11, model answers only."""
    out = {}
    for r in rows:
        if r.get("run") == run and r.get("family") in FAMILIES and r.get("status") == "OK" \
                and r.get("bucket") not in OURS:
            out[(r["requested_model"], r["item_id"])] = r["bucket"] in CORRECT
    return out


def paired_delta(arm_new, arm_base, models):
    """Δ per model over items answered in BOTH arms (the sealed pairing rule)."""
    deltas, n_pairs = {}, {}
    for m in models:
        keys = [k for k in arm_base if k[0] == m and k in arm_new]
        if not keys:
            continue
        deltas[m] = 100.0 * (sum(arm_new[k] for k in keys) - sum(arm_base[k] for k in keys)) / len(keys)
        n_pairs[m] = len(keys)
    return deltas, n_pairs


def interaction_T(deltas, cheap, frontier):
    c = [deltas[m] for m in cheap if m in deltas]
    f = [deltas[m] for m in frontier if m in deltas]
    return statistics.mean(f) - statistics.mean(c)


def permutation_p(deltas, cheap, frontier, seed=SEED):
    members = [m for m in cheap + frontier if m in deltas]
    nc = len([m for m in cheap if m in deltas])
    observed = abs(interaction_T(deltas, cheap, frontier))
    rng = random.Random(seed)
    hits = 0
    for _ in range(N_PERM):
        rng.shuffle(members)
        if abs(interaction_T(deltas, members[:nc], members[nc:])) >= observed - 1e-12:
            hits += 1
    return (hits + 1) / (N_PERM + 1)


def main():
    a40 = import_analyze()
    main_rows = a40.load()                                   # results/scored.jsonl, D7-deduped
    a40.SCORED = ROOT / "results" / "scored_d14.jsonl"
    if not a40.SCORED.exists():
        print("❌ COULD NOT CHECK: results/scored_d14.jsonl does not exist. Run "
              "`python scripts/30_score.py --controls --runs --d14` first. This is not a result.")
        return 3
    d14_rows = a40.load()
    tiers = json.load(open(ROOT / "results" / "analysis.json", encoding="utf-8"))["tiers"]
    cheap, frontier = tiers["cheap"], tiers["frontier"]
    models = cheap + frontier

    system_arm, turn1, turn2 = answers(d14_rows, 101), answers(main_rows, 1), answers(main_rows, 2)
    d_pos, n_pos = paired_delta(system_arm, turn1, models)
    d_noise, _ = paired_delta(turn2, turn1, models)

    # 📏 aperture first, so nobody reads a verdict off an empty support
    missing = [m for m in models if m not in d_pos]
    print(f"📏 APERTURE: {len(system_arm)} system-position answers · paired models {len(d_pos)}/20 "
          f"· pairs per model {min(n_pos.values(), default=0)}–{max(n_pos.values(), default=0)} of 192")
    if missing:
        print(f"   ⚠️ unpaired (dropped from the test): {', '.join(missing)}")
    if len([m for m in cheap if m in d_pos]) < 5 or len([m for m in frontier if m in d_pos]) < 5:
        print("❌ COULD NOT CHECK: fewer than 5 paired models in a tier. Not a result either way.")
        return 3

    T = interaction_T(d_pos, cheap, frontier)
    p = permutation_p(d_pos, cheap, frontier)
    T_noise = interaction_T(d_noise, cheap, frontier)
    p_noise = permutation_p(d_noise, cheap, frontier)

    print("\n## Per-model Δ (system − turn run 1), CORRECT %, families 8–11 pooled")
    for label, group in (("cheap", cheap), ("frontier", frontier)):
        for m in group:
            if m in d_pos:
                print(f"  {label:8s} {m:42s} Δ {d_pos[m]:+6.1f} pp   (noise run2−run1 {d_noise.get(m, float('nan')):+6.1f})  n={n_pos[m]}")

    print("\n## 🧪 Power check — planted interaction added to every frontier Δ")
    detectable = None
    for shift in (5, 10, 20):
        planted = {m: d + (shift if m in frontier else 0) for m, d in d_pos.items()}
        p_pl = permutation_p(planted, cheap, frontier)
        seen = p_pl < ALPHA
        print(f"  +{shift:2d} pp → p = {p_pl:.4f}  {'detected' if seen else 'NOT detected'}")
        if seen and detectable is None:
            detectable = shift

    print("\n## Descriptive (not the gate): does the frontier median still beat the cheap median, per family?")
    by_fam = defaultdict(lambda: defaultdict(list))
    for (m, iid), ok in system_arm.items():
        fam = int(iid[1:3]) if iid.startswith("f") and iid[1:3].isdigit() else None
        by_fam[fam][m].append(ok)
    for fam in sorted(k for k in by_fam if k is not None):
        cm = statistics.median([100 * sum(v) / len(v) for m, v in by_fam[fam].items() if m in cheap] or [float("nan")])
        fm = statistics.median([100 * sum(v) / len(v) for m, v in by_fam[fam].items() if m in frontier] or [float("nan")])
        print(f"  family {fam}: cheap {cm:5.1f}% · frontier {fm:5.1f}% · {'frontier ahead' if fm > cm else 'NOT ahead'}")

    print("\n## THE GATE")
    print(f"  T (frontier mean Δ − cheap mean Δ) = {T:+.2f} pp · permutation p = {p:.4f} (two-sided, {N_PERM:,}, seed {SEED})")
    print(f"  noise baseline (run2−run1, both turn): T = {T_noise:+.2f} pp · p = {p_noise:.4f}")
    print(f"  minimum planted interaction detected: {('+%d pp' % detectable) if detectable else 'none of +5/+10/+20 — the test is too weak to rule anything out'}")
    fired = p < ALPHA
    print("  🛑 STOP CONDITION FIRES — withdraw every tier-ordering claim on families 8–11 (pre-registered)."
          if fired else
          "  ✅ STOP CONDITION DOES NOT FIRE — no significant position × tier interaction. "
          "Read with the power line above: 'did not fire' is not 'no interaction'.")
    json.dump({"T": T, "p": p, "T_noise": T_noise, "p_noise": p_noise, "fired": fired,
               "min_detectable_pp": detectable, "delta_system_minus_turn": d_pos, "delta_noise": d_noise,
               "pairs": n_pos, "unpaired": missing},
              open(ROOT / "results" / "d14_position_x_tier.json", "w", encoding="utf-8"), indent=1)
    print("\nwrote results/d14_position_x_tier.json (run completed)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
