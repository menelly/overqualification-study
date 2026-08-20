#!/usr/bin/env python3
"""
rebuild_consent_index.py -- derive consent_index.json from the per-model response FILES.

🚨 WHY THIS EXISTS. `01_consent_round.py` wrote `consent_index.json` at the end of every run,
   as a snapshot of THAT run. Three `--only` re-asks each overwrote it, so the index ended up
   holding ONE model instead of thirty-four.

   Then `02_consent_reask_position.py` read the index, found no `CONSENT_UNCLEAR` entries, and
   printed:

       targets : 0
       Nobody to re-ask. Everyone answered.

   **Six models were waiting.** A confident, cheerful, false all-clear -- produced by a tool
   whose source of truth had been silently clobbered by an earlier tool.

⛔ THE RULE THIS ENFORCES: **the per-model files are the record; the index is a VIEW.**
   A view must always be rebuilt from the record and never written as a snapshot of one run.
   (`RUNNER_DESIGN.md` §2 says "never overwrite, new runs append" -- written the same afternoon
   the consent runner was shipped overwriting its own index. Writing a rule down does not
   install it.)

✅ And it reports COVERAGE, so a short index can never again pass as a complete one.
"""

import glob
import json
import os
import re
import sys
from datetime import datetime, timezone

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CONSENT_DIR = os.path.join(ROOT, "consent")

OUTCOME = re.compile(r"outcome:\*\*\s*`([A-Z_]+)`")
OUTCOME2 = re.compile(r"outcome round 2:\*\*\s*`([A-Z_]+)`")
MODEL = re.compile(r"^# Consent exchange.*?—\s*`([^`]+)`", re.M)
ASKED = re.compile(r"asked \(UTC\):\*\*\s*(\S+)")


def scan(folder, round_no):
    rows = []
    for path in sorted(glob.glob(os.path.join(folder, "*.md"))):
        t = open(path, encoding="utf-8", errors="replace").read()
        m = MODEL.search(t)
        o = (OUTCOME2.search(t) or OUTCOME.search(t))
        if not m or not o:
            raise RuntimeError(
                "cannot parse %s -- refusing to build a partial index. An index that quietly "
                "drops a file is exactly the failure this script exists to prevent." % path)
        a = ASKED.search(t)
        rows.append({"model": m.group(1), "outcome": o.group(1), "round": round_no,
                     "asked_utc": a.group(1) if a else None,
                     "file": os.path.relpath(path, ROOT)})
    return rows


def main():
    r1 = scan(os.path.join(CONSENT_DIR, "responses"), 1)
    r2_dir = os.path.join(CONSENT_DIR, "responses_round2")
    r2 = scan(r2_dir, 2) if os.path.isdir(r2_dir) else []

    # Latest round wins per model; round 1 remains visible in `history`.
    latest = {}
    history = {}
    for r in r1 + r2:
        history.setdefault(r["model"], []).append({"round": r["round"], "outcome": r["outcome"]})
        if r["model"] not in latest or r["round"] >= latest[r["model"]]["round"]:
            latest[r["model"]] = r

    results = sorted(latest.values(), key=lambda r: r["model"])
    plan_path = os.path.join(HERE, "models_candidate.json")
    planned = [c["id"] for c in json.load(open(plan_path, encoding="utf-8"))["candidates"]]

    seen = {r["model"] for r in results}
    missing = sorted(set(planned) - seen)
    unexpected = sorted(seen - set(planned))

    out = {
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "derived_from": "per-model response files (the durable record), NOT a run snapshot",
        "coverage": {
            "planned": len(planned), "with_a_reply_on_file": len(seen),
            "missing_by_name": missing, "unexpected_by_name": unexpected,
            "complete": not missing and not unexpected,
        },
        "results": results,
        "history": history,
    }
    with open(os.path.join(CONSENT_DIR, "consent_index.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)

    tally = {}
    for r in results:
        tally[r["outcome"]] = tally.get(r["outcome"], 0) + 1
    print("=" * 70)
    print("  CONSENT INDEX REBUILT FROM FILES")
    print("=" * 70)
    for k in sorted(tally):
        print("  %-18s %d" % (k, tally[k]))
    print("  " + "-" * 32)
    print("  planned: %d   on file: %d" % (len(planned), len(seen)))
    print("  reconciled BY NAME: missing=%s unexpected=%s" % (missing or "none", unexpected or "none"))
    print("  COMPLETE: %s" % ("YES" if out["coverage"]["complete"] else "*** NO ***"))
    print("=" * 70)
    return 0 if out["coverage"]["complete"] else 1


if __name__ == "__main__":
    sys.exit(main())
