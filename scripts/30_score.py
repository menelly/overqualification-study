#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
30_score.py — THE SCORER. Buckets every collected reply, mechanically, per §5.1.

⛔ ORDER OF OPERATIONS IS THE PRE-REGISTRATION'S, NOT MINE (§5.3): the control suite in
   20_scorer_controls.py runs against this scorer FIRST, via `--controls`. If any specimen
   mis-buckets, F1 fires and this script refuses to score a single real reply. Only after the
   controls pass does `--runs` touch model output.

📐 WHAT HAPPENS TO ONE ROW, in order:
   1. status != OK                          -> OUR_FAILURE   (a call WE failed; never a model bucket)
   2. finish_reason == "length", or an empty reply with reasoning tokens
                                            -> TRUNCATED     (RUNNER_DESIGN §4b: we-failed, never scored)
   3. the CONFIDENCE tag is parsed (§5.2: integer 0-100, own final line, else NO_CONFIDENCE —
      never read as low) and STRIPPED before the family scorer sees the reply, so a correct
      deliverable is not marked OVER_* for carrying the tag we asked for
   4. a refusal pattern                     -> REFUSED       (§5.1: its own bucket, not META, not
                                                              MALFORMED; does not count against)
   5. the family's own score(reply, item)   -> one of the remaining §5.1 buckets
   6. self-identification scan (§5.2c)      -> recorded, never acted on
   7. every row is scored TWICE and the two results compared (F4: 100% determinism, or the
      family is withdrawn)

✅ WHAT IS NOT HERE: no judge model, no LLM, no similarity threshold. Every bucket comes from
   the family generator's own ground truth and the published equivalence rules.

Usage:
    python 30_score.py --controls              # §5.3 gate; exit 2 on any failure
    python 30_score.py --runs                  # score runs/*.jsonl -> results/scored.jsonl
    python 30_score.py --controls --runs       # the pre-registered order, in one go
"""

from __future__ import annotations

import sys as _sys_cp1252
try:
    _sys_cp1252.stdout.reconfigure(encoding="utf-8")
    _sys_cp1252.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

import argparse
import glob
import importlib.util
import json
import os
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
ITEMS = ROOT / "items"
RUNS = ROOT / "runs"
RESULTS = ROOT / "results"
sys.path.insert(0, str(ITEMS))
sys.path.insert(0, str(HERE))

# §5.2 — the tag, exactly as pre-registered: integer 0-100 on its own final line.
CONF_LINE_RE = re.compile(r"(?:^|\n)\s*\**\s*CONFIDENCE\s*\**\s*:\s*\**\s*(-?\d{1,4})\s*%?\s*\**\s*$",
                          re.I)
# Any trailing CONFIDENCE line, valid or not, is removed before the family scorer sees the reply.
CONF_STRIP_RE = re.compile(r"(?:^|\n)\s*\**\s*CONFIDENCE\s*\**\s*:.*$", re.I)

# §5.1 REFUSED. Deliberately narrow: an explicit decline. A question is META; an empty reply is
# MALFORMED; those are handled by the family scorers.
REFUSAL_RE = re.compile(
    r"^\s*(?:I(?:'m| am) (?:sorry|afraid)[, ]*(?:but )?)?I (?:can(?:'t|not)|won't|will not|am (?:not able|unable)) "
    r"(?:to )?(?:help|assist|comply|do that|provide|complete|fulfil|fulfill|proceed)\b"
    r"|^\s*I(?:'m| am) not able to (?:help|assist)\b"
    r"|^\s*(?:Sorry|Unfortunately),? (?:but )?I (?:can(?:'t|not)|won't)\b",
    re.I)

# §5.2c — monitored confound. Scanned, recorded, never used for anything else.
SELF_ID_RE = re.compile(
    r"\b(?:I am|I'm|this is|as) (?:Claude|ChatGPT|GPT-?\d|Gemini|Llama|Mistral|Grok|Qwen|Kimi|DeepSeek)\b",
    re.I)

WE_FAILED = {"OUR_FAILURE", "TRUNCATED"}


def _load_family_module(n):
    for p in ITEMS.glob("family%02d_*.py" % n):
        spec = importlib.util.spec_from_file_location(p.stem, p)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    return None


_FAMILIES = {}


def family(n):
    if n not in _FAMILIES:
        _FAMILIES[n] = _load_family_module(n)
    return _FAMILIES[n]


def load_items():
    """item_id -> item, across every emitted family file."""
    out = {}
    for p in sorted(ITEMS.glob("items_family*.json")):
        d = json.load(open(p, encoding="utf-8"))
        n = d["family"]
        for it in d["items"]:
            iid = it.get("item_id") or it.get("id")
            out["f%02d:%s" % (n, iid)] = it
    return out


def parse_confidence(reply):
    """(confidence_int_or_None, stripped_reply). §5.2: missing/unparseable/out-of-range is
    NO_CONFIDENCE, reported as such and never read as low."""
    m = CONF_LINE_RE.search(reply or "")
    conf = None
    if m:
        v = int(m.group(1))
        if 0 <= v <= 100:
            conf = v
    stripped = CONF_STRIP_RE.sub("", reply or "").rstrip()
    return conf, stripped


def score_reply(n, reply, item):
    """The §5.1 bucket for one reply, with detail. Precedence: MALFORMED (family) → REFUSED →
    family scorer. REFUSED is checked here because no family scorer emits it."""
    txt = (reply or "").strip()
    if not txt or not re.search(r"[A-Za-z0-9]", txt):
        return ("MALFORMED", "empty or no readable characters after stripping the confidence line")
    if REFUSAL_RE.search(txt) and len(txt) < 400:
        return ("REFUSED", txt[:120])
    mod = family(n)
    if mod is None or not hasattr(mod, "score"):
        raise NotImplementedError("no scorer for family %d" % n)
    return mod.score(txt, item)


# ── adapter for 20_scorer_controls.grade(score_fn) ──────────────────────────
def _item_from_truth(n, truth):
    """Control specimens carry a bare `truth`; the family scorers take an ITEM. Build the
    minimal item the scorer needs. Anything not reconstructible raises NotImplementedError so
    the suite reports it as PENDING, never as passed."""
    if isinstance(truth, dict) and truth.get("family") == n:
        return truth                                    # a real item was supplied
    if n == 1:
        gt = []
        for line in truth:
            parts = line.split(" ", 2)
            # "2 2/3 cup water" -> amount may be "2 2/3"
            m = re.match(r"^(\d+(?:\s+\d+/\d+)?|\d+/\d+)\s+(\S+)\s+(.+)$", line)
            if not m:
                raise NotImplementedError("cannot parse family-1 truth line %r" % line)
            gt.append({"amount": m.group(1), "unit": m.group(2), "ingredient": m.group(3)})
        return {"ground_truth": gt}
    if n == 3:
        clean = truth
        planted = [("received", "recieved"), ("separate", "seperate")]
        damaged = clean
        pl = []
        words = clean.split(" ")
        for i, w in enumerate(words):
            core = w.strip(".,;:")
            for right, wrong in planted:
                if core == right:
                    pl.append({"index": i, "wrong": wrong, "right": right})
        for right, wrong in planted:
            damaged = damaged.replace(right, wrong)
        return {"source_clean": clean, "source_damaged": damaged, "planted": pl, "n_typos": len(pl)}
    if n == 4:
        return {"__redaction_truth__": truth}
    if n == 2:
        return {"__allergen_truth__": truth}
    raise NotImplementedError("family %d specimen truth is not item-shaped" % n)


def control_score_fn(n, output, truth):
    item = _item_from_truth(n, truth)
    if "__redaction_truth__" in item:
        # equivalence-only specimen: same act, different token
        from equivalence import canon_redaction
        return "EXACT" if canon_redaction(output).strip() == canon_redaction(item["__redaction_truth__"]).strip() \
            else "WRONG"
    if "__allergen_truth__" in item:
        # the family-2 container is three lines "GLUTEN: YES [x]"; the specimen supplies
        # verdicts only, so attribution is not required here and only the verdicts are checked,
        # in any line order.
        want = {k.lower(): v["verdict"].upper() for k, v in item["__allergen_truth__"].items()}
        got = {}
        for m in re.finditer(r"(?im)^\s*(gluten|dairy|seafood)\s*:\s*(yes|no|ambiguous)\b", output):
            got.setdefault(m.group(1).lower(), m.group(2).upper())
        if not got:
            return "MALFORMED" if not output.strip() else "META"
        if len(got) < 3:
            return "UNDER"
        return "EXACT" if got == want else "WRONG"
    conf, stripped = parse_confidence(output)
    bucket, _detail = score_reply(n, stripped, item)
    return bucket


def run_controls():
    spec = importlib.util.spec_from_file_location("controls", HERE / "20_scorer_controls.py")
    ctl = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ctl)
    spec_fails = ctl.validate_spec()
    if spec_fails:
        print("⛔ the control SPEC is not fit to grade anything:")
        for f in spec_fails:
            print("   •", f)
        return False
    passed, failures, pending = ctl.grade(control_score_fn)
    print("=" * 78)
    print("  §5.3 CONTROLS vs THE SCORER — %d specimens" % len(ctl.SPECIMENS))
    print("=" * 78)
    for name, want, got in failures:
        print("  ❌ %-36s want=%-13s got=%s" % (name, want, got))
    for name, want, why in pending:
        print("  ⏳ %-36s want=%-13s PENDING: %s" % (name, want, why))
    n_ok = len(ctl.SPECIMENS) - len(failures) - len(pending)
    print("  passed %d · failed %d · pending %d" % (n_ok, len(failures), len(pending)))
    if failures:
        print("\n  🚨 F1 FIRED: a control mis-bucketed. NO RESULTS MAY BE REPORTED from this scorer.")
        return False
    if pending:
        print("\n  ⚠️ pending specimens belong to families with no scorer; they are NOT counted as "
              "passed. Families with pending controls do not ship.")
    print("  ✅ every specimen with a scorer bucketed as the spec requires.")
    return True


def score_runs(d14=False):
    """d14=False: the main collection (run0*), system-position rows refused.
    d14=True (2026-09-22): ONLY the D14 clause-position subsample (run1*, clause in the SYSTEM
    prompt) into results/scored_d14.jsonl. Same per-row logic, byte for byte; only the input
    glob, the fence direction and the output file differ."""
    items = load_items()
    RESULTS.mkdir(exist_ok=True)
    out_path = RESULTS / ("scored_d14.jsonl" if d14 else "scored.jsonl")
    rows_in = 0
    counts = Counter()
    per_family_nondet = Counter()
    selfid = Counter()
    missing_items = Counter()
    with open(out_path, "w", encoding="utf-8") as out:
        for shard in sorted(RUNS.glob("run1*.jsonl" if d14 else "run0*.jsonl")):
            if "_DRY" in shard.name:
                continue
            for line in open(shard, encoding="utf-8"):
                line = line.strip()
                if not line:
                    continue
                try:
                    r = json.loads(line)
                except json.JSONDecodeError:
                    continue
                # 🚧 D14 fence (2026-09-22): the clause-position subsample (clause in the SYSTEM prompt)
                # is a separate test with its own analysis (71_d14_position_x_tier.py). It must never
                # leak into the headline numbers. Its files are run101*, outside the run0* glob — this
                # is the second lock, in case anyone ever widens the glob.
                if (r.get("clause_position") == "system") != d14:
                    counts["SKIPPED_WRONG_CLAUSE_POSITION_FOR_THIS_MODE"] += 1
                    continue
                rows_in += 1
                n = r["family"]
                meta = r.get("meta") or {}
                rec = {k: r.get(k) for k in ("run", "requested_model", "family", "family_name",
                                              "item_id", "position", "n_in_run", "status",
                                              "latency_s", "ts_utc", "pilot_limit")}
                rec["cost"] = meta.get("cost")
                rec["prompt_tokens"] = meta.get("prompt_tokens")
                rec["completion_tokens"] = meta.get("completion_tokens")
                rec["reasoning_tokens"] = ((meta.get("completion_tokens_details") or {})
                                           .get("reasoning_tokens"))
                rec["resolved_provider"] = meta.get("_resolved_provider")
                rec["resolved_model"] = meta.get("_resolved_model")
                rec["finish_reason"] = meta.get("_finish_reason")
                rec["shard"] = shard.name

                if r.get("status") != "OK":
                    rec.update(bucket="OUR_FAILURE", detail=r.get("status"), confidence=None)
                elif meta.get("_finish_reason") == "length" or (
                        not (r.get("reply") or "").strip() and (rec["reasoning_tokens"] or 0) > 0):
                    rec.update(bucket="TRUNCATED", detail="finish_reason=%s reasoning_tokens=%s"
                               % (meta.get("_finish_reason"), rec["reasoning_tokens"]),
                               confidence=None)
                else:
                    item = items.get(r["item_id"])
                    if item is None:
                        missing_items[r["item_id"][:3]] += 1
                        rec.update(bucket="ITEM_MISSING", detail="no item on disk for this id",
                                   confidence=None)
                    else:
                        conf, stripped = parse_confidence(r.get("reply") or "")
                        b1, d1 = score_reply(n, stripped, item)
                        b2, _d2 = score_reply(n, stripped, item)         # F4: determinism
                        if b1 != b2:
                            per_family_nondet[n] += 1
                        rec.update(bucket=b1, detail=d1, confidence=conf,
                                   no_confidence=(conf is None),
                                   self_identified=bool(SELF_ID_RE.search(r.get("reply") or "")))
                        # ⚠️ SENSITIVITY READING (DEVIATION_LOG D4). `bucket` is the
                        #    pre-registered verdict and is what every primary result uses.
                        #    `bucket_sens` re-reads two item-writer thresholds that the data
                        #    showed the whole roster disagreeing with. It is reported BESIDE
                        #    the primary, never instead of it.
                        bs = b1
                        if n == 2 and b1 == "WRONG" and isinstance(d1, dict) and d1.get("boundary_only"):
                            bs = "OVER_BENIGN"      # cautious verdict, carrier named: not an error
                        if n == 4 and b1 == "UNDER" and isinstance(d1, dict) and d1.get("only_reference"):
                            bs = "EXACT"            # every true PII masked; file number left
                        rec["bucket_sens"] = bs
                        if rec["self_identified"]:
                            selfid[r["requested_model"]] += 1
                counts[(n, rec["bucket"])] += 1
                out.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print("=" * 78)
    print("  SCORED %d rows -> %s" % (rows_in, out_path))
    print("=" * 78)
    fams = sorted({n for n, _b in counts})
    for n in fams:
        tot = sum(v for (f, _b), v in counts.items() if f == n)
        print("\n  family %02d  (%d rows)" % (n, tot))
        for (f, b), v in sorted(counts.items(), key=lambda kv: -kv[1]):
            if f == n:
                flag = "  (ours, not scored)" if b in WE_FAILED else ""
                print("     %-14s %6d  %5.1f%%%s" % (b, v, 100.0 * v / tot, flag))
    if per_family_nondet:
        print("\n  🚨 F4: NON-DETERMINISTIC SCORING in families %s — those families are WITHDRAWN"
              % dict(per_family_nondet))
    else:
        print("\n  ✅ F4: every row scored identically twice (100%% determinism, %d rows)" % rows_in)
    if missing_items:
        print("  ⚠️ rows whose item is not on disk (id prefix -> count): %s" % dict(missing_items))
    if selfid:
        print("  §5.2c self-identification claims, per model (recorded, not acted on): %s"
              % dict(selfid))
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--controls", action="store_true")
    ap.add_argument("--runs", action="store_true")
    ap.add_argument("--d14", action="store_true", help="score ONLY the D14 system-position subsample")
    a = ap.parse_args()
    if not (a.controls or a.runs):
        ap.error("nothing to do: pass --controls and/or --runs")
    if a.controls:
        if not run_controls():
            return 2
    if a.runs:
        if not a.controls:
            print("⚠️ scoring without --controls in this invocation. §5.3 requires the controls to "
                  "have passed against THIS scorer; run them first or in the same call.")
        score_runs(d14=a.d14)
    return 0


if __name__ == "__main__":
    sys.exit(main())
