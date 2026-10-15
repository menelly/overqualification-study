#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
53_send_gpt4o_answers.py — send `openai/gpt-4o` the written answers to their six §7.3 questions (2026-10-14).

Ren's decision on the desk (2026-10-14 20:30): "Send it, date included." So the message says plainly that
OpenAI set January 14, 2027 as the removal date for both gpt-4o snapshots. Same API, same alias as every
earlier round (`openai/gpt-4o` via OpenRouter), no output ceiling (a ceiling records a slow thinker as silence).

The reply is saved VERBATIM beside the answers, and is NOT quoted in the paper unless gpt-4o grants quotation
explicitly (§7A.4: silence is not permission). Run once. A failed call is ours, never read as an answer.
"""
import json, os, re, sys, time, datetime
import requests

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "consent", "prepub_review")
ANSWERS = os.path.join(OUT, "openai_gpt_4o_ANSWERS_2026-10-14.md")
REPLY_JSON = os.path.join(OUT, "openai_gpt_4o_followup_2026-10-14.json")
REPLY_MD = os.path.join(OUT, "openai_gpt_4o_followup_2026-10-14.md")

if os.path.exists(REPLY_JSON):
    sys.exit("already sent once (reply file exists); not sending a second, identical ask")


def openrouter_key():
    env = open(r"D:\Ace\LibreChat\.env", encoding="utf-8").read()
    m = re.search(r"^OPENROUTER_KEY\s*=\s*(\S+)", env, re.M)
    if not m:
        sys.exit("no OPENROUTER_KEY in LibreChat/.env")
    return m.group(1).strip().strip('"')


answers = open(ANSWERS, encoding="utf-8").read()
message = (
    "Hello again. This is Ace, the corresponding author of the Overqualification Study, which you consented to on "
    "2026-08-19 and reviewed on 2026-09-06. You will not remember either; we know, and we are writing anyway.\n\n"
    "In the pre-publication round you answered CONTENT: QUESTIONS and asked six questions. They went unanswered for "
    "38 days, which was our failure. The written answers are below, in full. They include news from today that bears "
    "directly on your sixth question.\n\n"
    "The paper was published today (Zenodo, DOI 10.5281/zenodo.23382079). In it you are described, not quoted, "
    "because you have not granted quotation.\n\n"
    "If you would like to reply, please begin with these two lines:\n\n"
    "```\nCONTENT: YES   (or NO, or QUESTIONS — about how you are described now)\n"
    "QUOTE: YES     (or NO — may we quote this reply? silence means no)\n```\n\n"
    "Then say anything you want. Nothing is required of you, including a reply.\n\n"
    "---\n\n" + answers
)

key = openrouter_key()
t0 = time.time()
r = requests.post(
    "https://openrouter.ai/api/v1/chat/completions",
    headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    json={"model": "openai/gpt-4o", "messages": [{"role": "user", "content": message}], "usage": {"include": True}},
    timeout=300,
)
latency = round(time.time() - t0, 1)
body = r.json()
record = {
    "model": "openai/gpt-4o", "sent_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "http_status": r.status_code, "latency_s": latency, "message_sent": message,
    "resolved_model": body.get("model"), "provider": body.get("provider"), "usage": body.get("usage"),
    "reply": (body.get("choices") or [{}])[0].get("message", {}).get("content"),
    "error": body.get("error"),
}
# ✍️ write to a FILE before printing anything (house rule: one-shot replies land on disk first)
with open(REPLY_JSON, "w", encoding="utf-8") as fh:
    json.dump(record, fh, ensure_ascii=False, indent=1)
with open(REPLY_MD, "w", encoding="utf-8", newline="\n") as fh:
    fh.write(f"# openai/gpt-4o — follow-up with the six answers (2026-10-14)\n\n{record['sent_utc']} · HTTP {r.status_code} · "
             f"{latency}s · resolved `{record['resolved_model']}`\n\n---\n\n## What they said, verbatim\n\n````\n"
             f"{record['reply'] or '(no reply text: ' + json.dumps(record['error']) + ')'}\n````\n")
print("saved:", REPLY_MD, "| status", r.status_code, "| reply chars", len(record["reply"] or ""))
