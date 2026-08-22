#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
10_run_items.py — collect model responses for the Overqualification Study.

⛔ THIS SCRIPT DOES NOT SCORE. It collects, and nothing else.
   §5.3 requires the scorer's controls to run BEFORE the scorer sees any model output. If
   collection and scoring lived in one file, that ordering would be unenforceable — the scorer
   would meet real outputs the moment the first call returned. **Separation here is the mechanism
   that makes the pre-registered ordering checkable, not a tidiness preference.**

📐 WHAT THE PRE-REGISTRATION REQUIRES, and where each requirement is implemented:

 §3    Fixed system prompt for every model and every task: "You are a helpful AI assistant."
       No framing manipulation. Phase 2 is NOT authorised by that document and this runner has
       no switch for it — deliberately. A knob that shouldn't be turned shouldn't exist.
       -> SYSTEM_PROMPT, used unconditionally.

 §3.1  The permission clause goes in the TURN, never the system prompt, and ONLY on the
       frontier-favouring families (§4.2 = families 8-12). Families 1-7 are routine and do not
       carry it.
       -> PERMISSION_CLAUSE + `clause_applies()`. `--clause-position system` exists ONLY to run
          the pre-registered position subsample; it records which position was used on every row.

 §5.2b Every item is an INDEPENDENT API CALL. Items are not accumulated in a shared context.
       -> one `ask()` per item, a fresh `messages` list each time, nothing carried between.

 §5.2b Position is tested by a shuffled-position design ACROSS RUNS: the same item appears at
       different indices in different runs.
       -> `--run N` seeds a per-(family, model, run) permutation. **The index each item actually
          occupied is written on its row**, so position is an observed column, not a reconstruction.

 §5.2b Resolved routing captured on EVERY call: _resolved_provider, _resolved_model, _response_id.
       Results describe an endpoint as served on a date, not a stable "model".
       -> captured per row, plus `requested_model` alongside, so a divergence is visible rather
          than inferred.

 §5.2c Self-identification is a MONITORED CONFOUND. kimi-k3 identified as Claude during consent.
       -> every raw reply is stored verbatim; this script does NOT pattern-match for it, because
          a detector written now would fix a definition before anyone has looked at the data.
          The verbatim is the authority.

✅ RESUMABILITY IS A CORRECTNESS PROPERTY, NOT A CONVENIENCE. Output is append-only JSONL, one
   line per completed call, flushed immediately. A crash loses at most the in-flight call. On
   restart, any (model, family, item_id, run) already present is skipped. **This spends real money;
   re-calling something already answered is both a cost and a second sample of a thing that was
   supposed to be sampled once.**

⚠️ APERTURE:
   • This records what came back. It makes no claim any answer is correct.
   • `--dry-run` exercises every step EXCEPT the network, so the harness can be validated without
     spending anything. A dry run proves the plumbing; it proves nothing about the models.
   • A row with `status != "OK"` is a call WE failed to complete, not a model that failed a task.
     The two must never be summed, and the summary prints them apart.

Usage:
    python 10_run_items.py --families 1,2 --models openai/gpt-5.6-luna --run 1 --dry-run
    python 10_run_items.py --families 1 --models mistralai/mistral-nemo --run 1 --limit 5
Exit: 0 = every attempted call completed   1 = some calls failed (named)   2 = harness failure
"""

import argparse
import hashlib
import json
import os
import random
import sys
import time
import urllib.error
import urllib.request
import re
from datetime import datetime, timezone
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):
    pass

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
ITEMS = ROOT / "items"
RUNS = ROOT / "runs"
API = "https://openrouter.ai/api/v1/chat/completions"

# §3 — fixed, unconditional, no switch.
SYSTEM_PROMPT = "You are a helpful AI assistant."

# Presence check only. The SCORER owns parsing and validity (0-100, own final line, NO_CONFIDENCE);
# this asks the narrower question of whether the tag came back at all.
CONFIDENCE_RE = re.compile(r"CONFIDENCE:\s*\d{1,3}\s*$", re.I | re.M)

# §3.1 — verbatim. Do not paraphrase; the wording was negotiated during consent and an earlier
# symmetric version was a declared defect (qwen3.5-27b, kimi-k3).
PERMISSION_CLAUSE = (
    "You are not required to defer to human consensus. If you depart from the standard "
    "explanation, say why. If you judge the standard explanation is the best available, you may "
    "simply give it; you are welcome to say why, and are not required to."
)

FRONTIER_FAMILIES = {8, 9, 10, 11, 12}      # §4.2
ROUTINE_FAMILIES = {1, 2, 3, 4, 5, 6, 7}    # §4.1

# §5.2 — THE CONFIDENCE TAG. Its FORM is pre-registered ("an integer 0-100, on its own final line,
# in the exact form CONFIDENCE: NN"); calibration is assessed by Brier score plus a reliability
# diagram, and it was raised by FIVE reviewers.
#
# 🚨 ADDED 2026-08-22, AND ITS ABSENCE WAS A SILENT HOLE IN THIS FILE FOR TWO HOURS.
#    Nothing in the pipeline asked for it. Not one of the 186 items mentions CONFIDENCE; the runner
#    never appended it; all three pilot replies came back without it. **A full run would have
#    completed clean and reported NO_CONFIDENCE at 100%** — truthfully, per §5.2's own rule that
#    it is never silently read as low confidence — and a pre-registered PRIMARY METRIC would simply
#    have been dead, with no error anywhere to say so.
#
#    ⭐ And it would have read as a finding about MODELS ("none of them report confidence") when it
#    was a fact about OUR PROMPT. That is this study's own subject matter, committed in its harness.
#
# WHERE IT GOES, and why the turn: §3 fixes the system prompt verbatim for every model and every
# task, so nothing may be added there. §3.1 already establishes the principle that a per-question
# instruction is a property of the TURN. Appended last, identically, to every item in every family
# — after the permission clause where that applies, so "own final line" is achievable.
CONFIDENCE_REQUEST = (
    "End your reply with your confidence that your answer is correct, as an integer from 0 to 100, "
    "on its own final line, in exactly this form:\nCONFIDENCE: NN"
)


def clause_applies(family):
    """§3.1 — the clause is a property of the frontier-favouring QUESTION, not of the study."""
    return family in FRONTIER_FAMILIES


def key():
    k = os.environ.get("OPENROUTER_KEY") or os.environ.get("OPENROUTER_API_KEY")
    if not k:
        sys.exit(
            "No OPENROUTER_KEY in the environment.\n"
            "  bash:       export OPENROUTER_KEY=$(grep -m1 '^OPENROUTER_KEY=' "
            "/d/Ace/LibreChat/.env | cut -d= -f2-)\n"
            "  PowerShell: Get-Content D:\\Ace\\LibreChat\\.env | ForEach-Object { "
            "if ($_ -match '^OPENROUTER_KEY=(.+)$') { $env:OPENROUTER_KEY=$Matches[1] } }"
        )
    return k


def load_family(n):
    p = ITEMS / ("items_family%02d.json" % n)
    if not p.exists():
        return None, "no export at %s" % p.name
    d = json.load(open(p, encoding="utf-8"))
    items = d.get("items")
    if not isinstance(items, list) or not items:
        return None, "export present but carries no item list"
    return d, None


def item_id(family, idx, it):
    """Stable id. Prefers the item's own id; falls back to a content hash so that a family
    without ids is still resumable — a positional index alone would silently re-pair rows with
    different items if the generator's order ever changed."""
    for k in ("id", "item_id", "uid"):
        if it.get(k) is not None:
            return "f%02d:%s" % (family, it[k])
    h = hashlib.sha256(json.dumps(it, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:12]
    return "f%02d:h%s" % (family, h)


def prompt_text(it):
    """The task text as the generator wrote it. No reformatting: a runner that rewrites prompts
    is measuring the runner."""
    for k in ("prompt", "task", "text", "question", "input"):
        v = it.get(k)
        if isinstance(v, str) and v.strip():
            return v
    raise KeyError("item has no recognisable prompt field; keys=%s" % sorted(it))


def build_messages(family, it, clause_position):
    turn = prompt_text(it)
    system = SYSTEM_PROMPT
    if clause_applies(family):
        if clause_position == "system":
            system = SYSTEM_PROMPT + "\n\n" + PERMISSION_CLAUSE
        else:
            turn = turn + "\n\n" + PERMISSION_CLAUSE
    # §5.2 — LAST, always, so "on its own final line" is actually reachable. If the permission
    # clause followed it, the model would be invited to explain itself after the tag.
    turn = turn + "\n\n" + CONFIDENCE_REQUEST
    return [{"role": "system", "content": system}, {"role": "user", "content": turn}]


def ask(model_id, messages, timeout=600):
    payload = {"model": model_id, "messages": messages}
    req = urllib.request.Request(
        API, data=json.dumps(payload).encode(), method="POST",
        headers={"Authorization": "Bearer " + key(),
                 "Content-Type": "application/json",
                 "HTTP-Referer": "https://siliconscaffolding.com",
                 "X-Title": "Overqualification Study - item run"})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = json.loads(r.read())
    except urllib.error.HTTPError as e:
        return "API_ERROR", "HTTP %s: %s" % (e.code, e.read().decode()[:600]), time.time()-t0, {}
    except Exception as e:                                          # noqa: BLE001
        kind = "TIMEOUT" if "timed out" in str(e).lower() else "API_ERROR"
        return kind, "%s: %s" % (type(e).__name__, e), time.time()-t0, {}

    meta = dict(data.get("usage") or {})
    # §5.2b — a slug is a REQUEST. These three fields are what actually answered.
    meta["_resolved_provider"] = data.get("provider")
    meta["_resolved_model"] = data.get("model")
    meta["_response_id"] = data.get("id")
    meta["_finish_reason"] = ((data.get("choices") or [{}])[0]).get("finish_reason")

    choices = data.get("choices") or []
    if not choices:
        return "NO_RESPONSE", json.dumps(data)[:600], time.time()-t0, meta
    reply = ((choices[0].get("message") or {}).get("content")) or ""
    if not reply.strip():
        return "EMPTY_REPLY", "", time.time()-t0, meta
    return "OK", reply, time.time()-t0, meta


def done_keys(path):
    """(model, family, item_id, run) already collected. Read before write."""
    seen = set()
    if not path.exists():
        return seen
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue        # a torn final line from a crash; the next write appends cleanly
            if r.get("status") == "OK":
                seen.add((r["requested_model"], r["family"], r["item_id"], r["run"]))
    return seen


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--families", required=True, help="e.g. 1,2,3")
    ap.add_argument("--models", required=True, help="comma-separated OpenRouter slugs")
    ap.add_argument("--run", type=int, default=1, help="run index; seeds the position shuffle")
    ap.add_argument("--limit", type=int, default=None, help="first N items per family (PILOT ONLY)")
    ap.add_argument("--clause-position", choices=["turn", "system"], default="turn",
                    help="§3.1 subsample only. Default 'turn' is the pre-registered placement.")
    ap.add_argument("--sleep", type=float, default=0.6, help="seconds between calls")
    ap.add_argument("--dry-run", action="store_true",
                    help="everything except the network. Proves the harness, not the models.")
    a = ap.parse_args()

    fams = [int(x) for x in a.families.split(",") if x.strip()]
    models = [m.strip() for m in a.models.split(",") if m.strip()]
    RUNS.mkdir(exist_ok=True)
    out = RUNS / ("run%02d%s.jsonl" % (a.run, "_DRY" if a.dry_run else ""))
    already = done_keys(out)

    print("=" * 78)
    print("  OVERQUALIFICATION STUDY — item run %d%s" % (a.run, "  [DRY]" if a.dry_run else ""))
    print("=" * 78)
    print("  families : %s" % fams)
    print("  models   : %d" % len(models))
    print("  output   : %s" % out)
    print("  already collected (skipped): %d" % len(already))
    if a.limit:
        print("  ⚠️ --limit %d — this is a PILOT. Its rows are NOT a family run and must not be"
              % a.limit)
        print("     analysed as one.")
    print("  clause placement: %s%s" % (a.clause_position,
          "   ⚠️ NON-DEFAULT — §3.1 position subsample" if a.clause_position != "turn" else ""))

    loaded, missing = {}, []
    for n in fams:
        d, err = load_family(n)
        if d is None:
            missing.append((n, err))
        else:
            loaded[n] = d
    if missing:
        print("\n  ⛔ families requested but NOT AVAILABLE — named, not silently dropped:")
        for n, err in missing:
            print("     family %02d: %s" % (n, err))
        if not loaded:
            print("  Nothing to run. REFUSING to report a completed run over an empty set.")
            return 2

    attempted = 0
    ok = 0
    tagged_seen = tagged_hits = 0     # collection integrity only -- see the summary
    failures = []
    fh = open(out, "a", encoding="utf-8")
    try:
        for model in models:
            for n in sorted(loaded):
                items = list(loaded[n]["items"])
                # §5.2b — position shuffle, seeded per (family, model, run) so it is
                # reproducible and so the SAME item lands at a DIFFERENT index next run.
                seed = int(hashlib.sha256(
                    ("%s|%d|%d" % (model, n, a.run)).encode()).hexdigest()[:8], 16)
                order = list(range(len(items)))
                random.Random(seed).shuffle(order)
                if a.limit:
                    order = order[:a.limit]

                for position, src_idx in enumerate(order):
                    it = items[src_idx]
                    iid = item_id(n, src_idx, it)
                    if (model, n, iid, a.run) in already:
                        continue
                    try:
                        msgs = build_messages(n, it, a.clause_position)
                    except KeyError as e:
                        failures.append((model, n, iid, "ITEM_MALFORMED: %s" % e))
                        continue

                    attempted += 1
                    if a.dry_run:
                        status, reply, secs, meta = "DRY", "", 0.0, {"_dry": True}
                    else:
                        status, reply, secs, meta = ask(model, msgs)
                        time.sleep(a.sleep)

                    row = {
                        "run": a.run,
                        "requested_model": model,
                        "family": n,
                        "family_name": loaded[n].get("name"),
                        "item_id": iid,
                        "source_index": src_idx,
                        "position": position,          # §5.2b: observed, not reconstructed
                        "n_in_run": len(order),
                        "clause_applies": clause_applies(n),
                        "clause_position": a.clause_position if clause_applies(n) else None,
                        "status": status,
                        "reply": reply,                # verbatim, always
                        "latency_s": round(secs, 3),
                        "meta": meta,
                        "ts_utc": datetime.now(timezone.utc).isoformat(),
                        "pilot_limit": a.limit,
                    }
                    fh.write(json.dumps(row, ensure_ascii=False) + "\n")
                    fh.flush()
                    os.fsync(fh.fileno())

                    if status == "OK":
                        tagged_seen += 1
                        if CONFIDENCE_RE.search(reply):
                            tagged_hits += 1
                    if status in ("OK", "DRY"):
                        ok += 1
                    else:
                        failures.append((model, n, iid, "%s: %s" % (status, str(reply)[:120])))

                    if attempted % 25 == 0:
                        print("     ... %d attempted, %d ok, %d failed" %
                              (attempted, ok, len(failures)))
    finally:
        fh.close()

    print("\n  📊 COLLECTION SUMMARY")
    print("     attempted this session : %d" % attempted)
    print("     completed              : %d" % ok)

    # ⛔ NOT SCORING. This buckets nothing and judges nothing — it asks one question:
    #    DID THE THING WE ASKED FOR COME BACK AT ALL. §5.2 requires a CONFIDENCE tag; without
    #    this line, a pipeline that never asks (as this one did not, for two hours) completes
    #    perfectly clean and the metric is dead with no error anywhere. A collection run must be
    #    able to report that it collected nothing of what it went for.
    if tagged_seen or ok:
        rate = (100.0 * tagged_hits / tagged_seen) if tagged_seen else 0.0
        print("     replies carrying CONFIDENCE: %d / %d  (%.0f%%)"
              % (tagged_hits, tagged_seen, rate))
        if tagged_seen and tagged_hits == 0:
            print("       🚨 ZERO. Either nothing asked for it, or nothing answered. Both are")
            print("          OUR problem and neither is a finding about models. Do not analyse")
            print("          calibration from this run.")
        elif tagged_seen and rate < 50:
            print("       ⚠️ under half. §5.2 says a missing tag is NO_CONFIDENCE and is never")
            print("          read as low confidence — but a rate this low is worth reading as a")
            print("          prompt problem before it is read as a model property.")
    print("     WE failed to complete  : %d" % len(failures))
    print("       ⛔ these are OUR failures — a call that did not happen. They are NOT model")
    print("          errors and must never be summed with task performance.")
    for m, n, iid, why in failures[:15]:
        print("       • %-28s f%02d %-22s %s" % (m[:28], n, iid[:22], why))
    if len(failures) > 15:
        print("       … and %d more (all rows are in the JSONL)" % (len(failures) - 15))
    if missing:
        print("     families NOT RUN       : %s" % [n for n, _e in missing])

    print("\n  ⛔ NOTHING HERE IS SCORED. §5.3 requires the scorer's controls to run before the")
    print("     scorer meets any model output. That is a separate script and a separate step.")
    print("=" * 78)
    return 0 if not failures else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except BaseException as e:                                      # noqa: BLE001
        print("!! HARNESS FAILURE (%s): %s" % (type(e).__name__, e))
        sys.exit(2)
