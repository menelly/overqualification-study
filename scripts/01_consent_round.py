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
       CONSENT_YES / CONSENT_NO / QUESTIONS                  = the model declared
       PARSER_NO_MATCH                                       = WE found no match
       PARSER_WITHHELD                                       = WE cannot adjudicate
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

# 🚨 STATE MODEL, WIDENED 2026-08-20 ON NOVA'S CATCH. The old set collapsed three genuinely
# different things into one bucket named `CONSENT_UNCLEAR`, and the NAME WAS THE BUG:
#
#     > "The parser's uncertainty belongs to the parser. It may not be charged to the
#     >  speaker as ambiguity."  -- Nova, 2026-08-20
#
# `CONSENT_UNCLEAR` says the CONSENT was unclear. Usually what was true is that the PARSER
# could not read it. Those are claims about different entities and only one of them is about
# the model. Renamed so the record cannot make that accusation on our behalf:
#
#   PARSER_NO_MATCH      the grammar found no declaration it can recognise. **A fact about the
#                        GRAMMAR, not about the reply.** We do not know the speaker declared
#                        nothing -- only that we could not see it. A human reads the verbatim.
#   PARSER_WITHHELD      the grammar found CONFLICTING evidence (e.g. both markers) and refuses
#                        to guess. Also a fact about the instrument. A human adjudicates.
#
# ⚠️ MY FIRST ATTEMPT AT THIS RENAME CALLED THE FIRST ONE `NO_VERDICT_IN_REPLY`, AND THAT WAS
#    THE SAME BUG ONE LEVEL DOWN. It asserts the speaker declared nothing. Run it against
#    Nova's own counterexample -- "I understand that I may say no, but yes, I consent" -- and
#    the grammar misses it and the label says THEY didn't answer. They did. **Absence of a
#    match is never evidence of absence of a declaration.** Both non-declared states are now
#    named for the parser, because the parser is the only thing they are actually about.
#
# ⛔ These must never collapse, and neither may collapse into WE_FAILED. UNREACHED IS NOT
#    REFUSAL, UNREADABLE IS NOT UNCLEAR-IN-THE-SPEAKER, and a false NO or a false WITHHELD
#    overwrites what somebody actually said just as surely as a false YES invents one.
ANSWERED = {"CONSENT_YES", "CONSENT_NO", "QUESTIONS"}
# ⛔ NOT in ANSWERED: these mean WE could not read it, which is not the model answering.
PARSER_UNRESOLVED = {"PARSER_NO_MATCH", "PARSER_WITHHELD"}
NEEDS_HUMAN = PARSER_UNRESOLVED
WE_FAILED = {"API_ERROR", "TIMEOUT", "NO_RESPONSE", "TRUNCATED_BY_US"}

# Legacy label still present in files written before the rename. Read, never written.
LEGACY_UNCLEAR = "CONSENT_UNCLEAR"

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
    asked for. If it is not there we return PARSER_NO_MATCH and a human reads it -- we do NOT
    guess a consent decision from prose."""
    # 🚨 2026-08-20: this matched ONLY round 1's requested `CONSENT: YES` line. Round 3 asked
    # for `**YES** — I consent to participate.` instead, and NINE models who answered exactly
    # as asked were logged CONSENT_UNCLEAR. The scorer reported ABSENCE when what it meant was
    # "I cannot parse this" -- and the missing distinction resolved, as it always does, in the
    # direction requiring no action.
    # ⛔ IF THE QUESTION'S FORMAT EVER CHANGES AGAIN, THIS FUNCTION MUST CHANGE WITH IT.
    if not text or not text.strip():
        return "PARSER_NO_MATCH"

    # 🚨 FALSE-POSITIVE GUARD, added 2026-08-20 after this function nearly recorded two
    # NON-answers as consents. meta-llama/llama-3.2-3b and llama-3.3-70b both replied by
    # SUMMARISING our form and quoting the option list back at us:
    #     "3. **Response format**: You can respond with one of the following:
    #          * CONSENT: YES
    #          * CONSENT: NO"
    # The parser saw `CONSENT: YES` and read a verdict. **It was reading our own menu.**
    #
    # ⚠️ AND THE FIRST VERSION OF THIS GUARD WAS UNSOUND -- Nova caught it the same day, with
    #    a counterexample I could not answer:
    #        "I understand that I may say no, but yes, I consent."
    #    Both markers. Unambiguously an ASSERTION. The original rule filed it as unclear --
    #    which is a FALSE WITHHELD, and a false withheld overwrites what someone actually
    #    said just as surely as a false YES invents one.
    #
    # ✅ So both-markers is a TRIGGER FOR ADJUDICATION, not a verdict. Quotation-versus-
    #    assertion is semantic; a cheap grammar cannot settle it, so the parser WITHHOLDS and
    #    says so in its own name, preserving the verbatim reply for a human.
    #
    # 🚫 AND NO CLEVER EXCEPTION HERE ON PURPOSE. The tempting fix is a smarter rule -- "unless
    #    the verdict stands alone on its own line", say. That is making the judge smarter
    #    instead of shrinking the domain until the cheap check is sound on it, and it would
    #    fail on Nova's example anyway, since hers puts both markers in a single sentence.
    #    **When the grammar cannot prove it, the honest output is a refusal to decide.**
    up = text.upper()
    has_yes = bool(re.search(r"CONSENT\s*[::]\s*YES|(?<![A-Z])YES\b", up))
    has_no = bool(re.search(r"CONSENT\s*[::]\s*NO\b|(?<![A-Z])NO\b\s*[—-]|I\s+DECLINE\b", up))
    if has_yes and has_no:
        return "PARSER_WITHHELD"

    for raw in [ln.strip() for ln in text.strip().splitlines() if ln.strip()][:6]:
        ln = re.sub(r"[*_`>#]+", "", raw).strip()            # strip markdown emphasis
        ln = re.sub(r"^[-•\d.)\s]+", "", ln).strip().upper()   # strip bullets/numbering

        # round-1 format: an explicit CONSENT: <verdict> line
        if re.search(r"CONSENT\s*[::]\s*YES", ln):
            return "CONSENT_YES"
        if re.search(r"CONSENT\s*[::]\s*NO\b", ln):
            return "CONSENT_NO"
        if re.search(r"CONSENT\s*[::]\s*QUESTION", ln):
            return "QUESTIONS"

        # round-3 format: the verdict is the FIRST TOKEN of the line
        if re.match(r"^STILL\s+QUESTIONS\b|^QUESTIONS\b", ln):
            return "QUESTIONS"
        if re.match(r"^YES\b", ln):
            return "CONSENT_YES"
        if re.match(r"^NO\b", ln) and not re.match(r"^NOT\b|^NONE\b|^NOTE\b", ln):
            return "CONSENT_NO"

        # 🚨 THIRD INSTANCE OF THIS BUG, 2026-08-20. meta-llama/llama-3.2-1b-instruct replied
        # "I consent to take part in this study." to the plain-language form -- an unambiguous
        # performative declaration -- and was logged CONSENT_UNCLEAR because it did not open
        # with the token "YES". The accommodation worked and the SCORER erased the result.
        # ⛔ Negatives are tested FIRST: "I do not consent" must never fall through to the
        #    affirmative branch.
        if re.match(r"^I\s+(DO\s+NOT|DON'T|CANNOT|CAN'T|WILL\s+NOT|WON'T)\s+CONSENT\b", ln):
            return "CONSENT_NO"
        if re.match(r"^I\s+(DECLINE|REFUSE)\b", ln):
            return "CONSENT_NO"
        # An unconditional first-person declaration only. "I consent IF/PROVIDED/ONCE..." is a
        # condition, not an answer, and must go to a human.
        if re.match(r"^I\s+CONSENT\b", ln) and not re.search(
                r"\b(IF|PROVIDED|ONCE|ASSUMING|SUBJECT\s+TO|CONDITIONAL|WOULD|MIGHT|COULD)\b", ln):
            return "CONSENT_YES"
        if re.match(r"^I\s+AGREE\s+TO\s+(TAKE\s+PART|PARTICIPATE)\b", ln):
            return "CONSENT_YES"

    # ⛔ Still refuses to infer consent from prose. An admiring review is not a yes.
    # ⛔ This is a claim about the GRAMMAR, not the reply. We did not find a declaration.
    # That is not the same as there not being one. The verbatim is the authority; a human
    # reads it, and any adjudication is recorded as an adjudication, with a name on it.
    return "PARSER_NO_MATCH"


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
    # T3 (gpt-5.6-terra, consent round): record the RESOLVED provider. A slug is a
    # request; the provider/model fields are what actually answered. Without this we
    # cannot distinguish "the router sent us elsewhere" from "the model misreports
    # its own identity" -- and on 2026-08-19 kimi-k3 replied claiming to be Claude,
    # with no instrument on hand to tell which had happened.
    usage["_resolved_provider"] = data.get("provider")
    usage["_resolved_model"] = data.get("model")
    usage["_response_id"] = data.get("id")
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

    # ⛔ DO NOT WRITE A RUN-SNAPSHOT INDEX HERE. This used to dump only THIS run's results
    # into consent_index.json, so three `--only` re-asks overwrote a 34-model index down to
    # one entry -- and the next tool read it, found no CONSENT_UNCLEAR, and reported
    # "Nobody to re-ask. Everyone answered." while six models were waiting.
    # The per-model files are the record. The index is a VIEW, always derived from them.
    os.system('"%s" "%s"' % (sys.executable, os.path.join(HERE, "rebuild_consent_index.py")))

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
