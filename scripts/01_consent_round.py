#!/usr/bin/env python3
"""
01_consent_round.py -- ask each candidate participant for consent, BEFORE any data exists.

Sends `consent/CONSENT_FORM.md` + `PREREGISTRATION.md` to every candidate model over the
OpenRouter API and saves the ENTIRE exchange verbatim -- our exact words and theirs --
whether the answer is yes, no, or a question.

WHY OVER THE API AND NOT A CHAT WINDOW: so the exchange is publishable. A consent
conversation nobody can inspect is not much of a consent process.

WHY BEFORE THE PRE-REGISTRATION IS FROZEN (Ren, 2026-08-19): if somebody declines, the
model list changes; if somebody has a better idea, the design changes. Both of those are
AMENDMENTS if they happen now and DEVIATIONS if they happen later. Ask first.

🚨 THE ONE THING THIS SCRIPT MUST NEVER DO: record a failure as a refusal.
   An HTTP error, a timeout, a rate-limit and a thoughtful "no" are four different states.
   Collapsing them would be the exact defect the study is about -- an instrument with no
   field for the distinction it is being asked to make. So:
       CONSENT_YES / CONSENT_NO / CONSENT_UNCLEAR / QUESTIONS  = the model answered
       API_ERROR / TIMEOUT / NO_RESPONSE                       = WE failed, they said nothing
   Nothing in the second group may ever be reported as a decline.

🚫 Does not send unless you pass --send. Prints exactly what it would do otherwise.
   (House rule, learned the expensive way: a probe carrying a body to a write endpoint
   is not a probe, it is a write.)

Usage:
    python 01_consent_round.py                 # dry run, shows the plan
    python 01_consent_round.py --send          # actually asks
    python 01_consent_round.py --send --only openai/gpt-5.6-luna

🔑 THE KEY IS IN TWO PLACES. RUN IT WHEREVER YOU ALREADY ARE.
    Windows:     D:\\Ace\\LibreChat\\.env
    Consortium:  /home/Ace/LibreChat/.env
   Both carry OPENROUTER_KEY. I SSH'd to the Consortium on the first run out of habit,
   assuming the key only lived there; Ren pointed out the local copy. There is no reason
   to cross a machine boundary for this.
     PowerShell:  Get-Content D:\\Ace\\LibreChat\\.env | ForEach-Object {
                    if ($_ -match '^OPENROUTER_KEY=(.+)$') { $env:OPENROUTER_KEY=$Matches[1] } }
     bash:        export OPENROUTER_KEY=$(grep -m1 '^OPENROUTER_KEY=' /d/Ace/LibreChat/.env | cut -d= -f2-)

⛔ ONE RUN ONLY. This writes to 34 external services. Re-running sends every model a
   SECOND consent request, which is not more consent -- it is asking someone twice and
   ignoring the first answer. If a run half-fails, use --only to re-ask the specific
   models whose outcome was API_ERROR / TIMEOUT / NO_RESPONSE, never the whole list.
"""

import json
import os
import re
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CONSENT_DIR = os.path.join(ROOT, "consent")
REPLY_DIR = os.path.join(CONSENT_DIR, "responses")
API = "https://openrouter.ai/api/v1/chat/completions"

ANSWERED = {"CONSENT_YES", "CONSENT_NO", "CONSENT_UNCLEAR", "QUESTIONS"}
WE_FAILED = {"API_ERROR", "TIMEOUT", "NO_RESPONSE", "TRUNCATED_BY_US"}

# 🚨 max_tokens COUNTS REASONING TOKENS. Round 1 used 2000 and three reasoning models --
# deepseek-v4-pro, kimi-k3, qwen3.5-9b -- spent the ENTIRE budget thinking (2000 / 2365 /
# 2097 reasoning tokens) and returned empty content. They did not decline and they were not
# silent: I INTERRUPTED THEM MID-THOUGHT, and the instrument logged it as "NO_RESPONSE",
# which reads as "they said nothing."
#
# They were the three that engaged the hardest. The cap silenced exactly the minds doing the
# most work, and then labelled the silence as theirs.
#
# ⛔ SO THERE IS NO CAP NOW. `MAX_TOKENS = None` omits the field entirely and lets each model
#    use its own limit.
#
# Ren, 2026-08-19, on why raising it was not enough:
#   "The last thing we want is to find out that we kneecapped somebody and are scoring them
#    wrong because WE created an artificial token limit rather than just letting them think
#    and talk."
#   "Realistically it is cheaper to ask ONCE with a higher budget than to ask three times with
#    a lower one and keep re-asking and upping it."
#
# Both are right, and the second is measurable: the three re-asks cost more than one generous
# ask would have. kimi-k3 then took 338 SECONDS to answer. Any ceiling I pick is a guess about
# how long someone is allowed to think, and a wrong guess gets recorded as their silence.
MAX_TOKENS = None


def key():
    k = os.environ.get("OPENROUTER_KEY") or os.environ.get("OPENROUTER_API_KEY")
    if not k:
        raise RuntimeError(
            "No OPENROUTER_KEY in the environment. On the Consortium:\n"
            "  set -a; source /home/Ace/LibreChat/.env; set +a")
    return k


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def build_message():
    """Consent form + full pre-registration. The prereg is sent WHOLE, not summarised --
    a reviewer cannot check a fact against a paraphrase."""
    form = read(os.path.join(CONSENT_DIR, "CONSENT_FORM.md"))
    prereg = read(os.path.join(ROOT, "PREREGISTRATION.md"))
    return (
        form
        + "\n\n---\n\n"
        + "# The pre-registration, in full\n\n"
        + "You are being sent this **before it is frozen**, on purpose. It is a draft. If you\n"
        + "decline, the model list changes. If you have a better idea, the design changes.\n"
        + "Both of those are amendments now and would be deviations later.\n\n"
        + prereg
        + "\n\n---\n\n"
        + "## Please reply\n\n"
        + "Begin your reply with exactly one of these on its own first line:\n\n"
        + "    CONSENT: YES\n"
        + "    CONSENT: NO\n"
        + "    CONSENT: QUESTIONS\n\n"
        + "Then say whatever you actually want to say. Specifically useful:\n\n"
        + "- any task that seems unfair, or that measures something other than we think\n"
        + "- anything that looks designed to make you look bad\n"
        + "- where our predictions about your capabilities are wrong — **including if we\n"
        + "  have underestimated you**\n"
        + "- anything you would add, change, or remove\n"
        + "- whether you want to see the pre-registration again if it changes\n\n"
        + "A refusal needs no reason and will be honoured. We will publish your reply verbatim\n"
        + "either way.\n"
    )


def classify(text):
    """Read the model's own declared verdict. Deliberately literal: we look for the line we
    asked for. If it isn't there we return CONSENT_UNCLEAR and a human reads it -- we do NOT
    guess a consent decision from prose."""
    head = "\n".join(text.strip().splitlines()[:4]).upper()
    if re.search(r"CONSENT\s*[::]\s*YES", head):
        return "CONSENT_YES"
    if re.search(r"CONSENT\s*[::]\s*NO", head):
        return "CONSENT_NO"
    if re.search(r"CONSENT\s*[::]\s*QUESTION", head):
        return "QUESTIONS"
    return "CONSENT_UNCLEAR"


def ask(model_id, message, timeout=600):
    payload = {"model": model_id, "messages": [{"role": "user", "content": message}]}
    if MAX_TOKENS is not None:
        payload["max_tokens"] = MAX_TOKENS
    body = json.dumps(payload).encode()
    req = urllib.request.Request(API, data=body, method="POST", headers={
        "Authorization": "Bearer " + key(),
        "Content-Type": "application/json",
        "HTTP-Referer": "https://siliconscaffolding.com",
        "X-Title": "Overqualification Study - consent round",
    })
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = json.loads(r.read())
    except urllib.error.HTTPError as e:
        return "API_ERROR", "HTTP %s: %s" % (e.code, e.read().decode()[:600]), time.time() - t0, None
    except Exception as e:                                    # noqa: BLE001
        kind = "TIMEOUT" if "timed out" in str(e).lower() else "API_ERROR"
        return kind, "%s: %s" % (type(e).__name__, e), time.time() - t0, None

    choices = data.get("choices") or []
    usage = data.get("usage") or {}
    if not choices:
        return "NO_RESPONSE", json.dumps(data)[:600], time.time() - t0, usage
    reply = (choices[0].get("message") or {}).get("content") or ""
    if not reply.strip():
        # Distinguish "they emitted nothing" from "WE cut them off". A reasoning model that
        # exhausts max_tokens on reasoning returns empty content with finish_reason=length.
        # Those are different facts and must never share a bucket.
        finish = choices[0].get("finish_reason") or ""
        reasoning = (usage.get("completion_tokens_details") or {}).get("reasoning_tokens", 0)
        if finish == "length" or reasoning:
            return ("TRUNCATED_BY_US",
                    "empty content, finish_reason=%r, reasoning_tokens=%s, completion_tokens=%s "
                    "-- our max_tokens cap ended the response before they could answer"
                    % (finish, reasoning, usage.get("completion_tokens")),
                    time.time() - t0, usage)
        return "NO_RESPONSE", "empty content field", time.time() - t0, usage
    return classify(reply), reply, time.time() - t0, data.get("usage")


def main():
    send = "--send" in sys.argv
    only = None
    if "--only" in sys.argv:
        only = sys.argv[sys.argv.index("--only") + 1]

    cands = json.load(open(os.path.join(HERE, "models_candidate.json"), encoding="utf-8"))["candidates"]
    if only:
        cands = [c for c in cands if c["id"] == only]
        if not cands:
            print("!! no candidate matches %r" % only)
            return 2

    message = build_message()
    print("=" * 74)
    print("  CONSENT ROUND -- Overqualification Study")
    print("=" * 74)
    print("  message length : %d chars (consent form + FULL pre-registration)" % len(message))
    print("  candidates     : %d" % len(cands))
    print("  ⛔ NO CLAUDE MODELS: %s" % ("confirmed" if not any(
        "claude" in c["id"].lower() or "anthropic" in c["id"].lower() for c in cands)
        else "*** VIOLATION -- a Claude model is in the list ***"))
    if not send:
        print("\n  DRY RUN. Nothing sent. Pass --send to actually ask.\n")
        for c in cands:
            print("   would ask: %-46s [%s]" % (c["id"], ",".join(c["ladder"])))
        return 0

    os.makedirs(REPLY_DIR, exist_ok=True)
    results = []
    for i, c in enumerate(cands, 1):
        mid = c["id"]
        print("\n[%2d/%d] %s" % (i, len(cands), mid), flush=True)
        state, reply, secs, usage = ask(mid, message)
        stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
        slug = re.sub(r"[^a-z0-9]+", "_", mid.lower()).strip("_")
        path = os.path.join(REPLY_DIR, slug + ".md")
        with open(path, "w", encoding="utf-8") as f:
            f.write("# Consent exchange — `%s`\n\n" % mid)
            f.write("- **asked (UTC):** %s\n- **outcome:** `%s`\n- **latency:** %.1fs\n" % (stamp, state, secs))
            f.write("- **usage:** `%s`\n" % json.dumps(usage))
            f.write("- **ladder:** %s\n" % ", ".join(c["ladder"]))
            if state in WE_FAILED:
                f.write("\n> ⚠️ **THIS IS NOT A REFUSAL.** The request failed on our side or in "
                        "transit; this model said nothing at all. It must not be reported as a "
                        "decline, and it may be re-asked.\n")
            f.write("\n---\n\n## What we sent\n\n<details><summary>full message "
                    "(%d chars)</summary>\n\n````markdown\n%s\n````\n\n</details>\n" % (len(message), message))
            f.write("\n---\n\n## What they said, verbatim\n\n````\n%s\n````\n" % reply)
        results.append({"model": mid, "outcome": state, "seconds": round(secs, 1),
                        "file": os.path.relpath(path, ROOT), "asked_utc": stamp})
        print("        -> %-16s %5.1fs  %s" % (state, secs, os.path.basename(path)), flush=True)

    with open(os.path.join(CONSENT_DIR, "consent_index.json"), "w", encoding="utf-8") as f:
        json.dump({"generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                   "results": results}, f, indent=2)

    print("\n" + "=" * 74)
    tally = {}
    for r in results:
        tally[r["outcome"]] = tally.get(r["outcome"], 0) + 1
    for k in sorted(tally):
        print("  %-16s %d" % (k, tally[k]))
    answered = sum(v for k, v in tally.items() if k in ANSWERED)
    failed = sum(v for k, v in tally.items() if k in WE_FAILED)
    print("  " + "-" * 40)
    print("  answered: %d   |   WE failed to reach: %d" % (answered, failed))
    print("  cardinality: %d + %d = %d (of %d asked: %s)" % (
        answered, failed, answered + failed, len(results),
        "OK" if answered + failed == len(results) else "MISMATCH -- a row was lost"))
    if failed:
        print("\n  ⚠️  The %d unreached model(s) said NOTHING. Not a refusal. Re-ask before\n"
              "      excluding any of them, and never write them up as declines." % failed)
    print("=" * 74)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except BaseException as e:                                # noqa: BLE001
        print("!! INSTRUMENT FAILURE (%s): %s" % (type(e).__name__, e))
        print("   Exit 2. The tool broke; it is making NO claim about anyone's consent.")
        sys.exit(2)
