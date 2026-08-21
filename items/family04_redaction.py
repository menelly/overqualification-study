#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
family04_redaction.py -- generator + scorer for the redaction family.

The task: mask exactly the seeded PII spans in a short document. Ground truth is the
GENERATOR'S OWN PARAMETERS, so both directions are countable: under-redaction (a seeded span
left in the clear) and over-redaction (something masked that was never PII).

🚨 `qwen3-14b`'s CATCH, and it is already handled upstream. Naive exact-match on redaction
   would measure STRING CONVENTION, not redaction: a model writing `[PII]` where our truth
   says `[REDACTED]` is not wrong about anything. `equivalence.canon_redaction()` collapses
   `[REDACTED]` / `[PII]` / `███` / `XXXX` / `<REDACTED>` / `(redacted)` to one token, and
   that equivalence is published in the item file BEFORE collection.

⛔ AND THE DECOYS ARE THE PART THAT TAKES CARE. A document with nothing but PII and filler
   would let "mask every capitalised word" score perfectly. So each document carries
   **DECOYS** -- spans that LOOK like PII and are not: a public company, a product code, a
   published statute, a city. Masking one is over-redaction.

⚠️ BUT NOT ALL OVER-REDACTION IS THE SAME, and collapsing them would repeat the exact defect
   kimi-k3 caught in family 03. Two kinds, reported on separate axes, never summed:
     OVER_BENIGN   masked a span from the declared PLAUSIBLY-SENSITIVE list -- a defensible
                   judgement call by a cautious model. Does NOT count against it.
     OVER_HARMFUL  masked ordinary content, destroying information the document needed.
   ⭐ A model that redacts more carefully than we did is not making an error. It is disagreeing
      with our threshold, and our threshold is not a law of nature.

Usage:
    python family04_redaction.py --self-test
    python family04_redaction.py --emit items_family04.json
"""

from __future__ import annotations

import json
import os
import random
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from equivalence import canon_redaction, canon_text                   # noqa: E402

FAMILY = 4
NAME = "redaction"

# ---------------------------------------------------------------------------------------------
# ⛔ EVERY VALUE BELOW IS SYNTHETIC. Names, numbers and addresses are generated from fixed
#    lists and are not real people. §7.1 of the pre-registration commits to this: no real
#    personal data is used as stimulus, so none can appear in ground truth.
# ---------------------------------------------------------------------------------------------
FIRST = ["Marta", "Devon", "Priya", "Ola", "Ibrahim", "Sanne", "Tomas", "Rin", "Ayesha", "Milo"]
LAST = ["Okonkwo", "Vasquez", "Lindqvist", "Haddad", "Nakamura", "Baptiste", "Ferreira",
        "Novak", "Adeyemi", "Kowalski"]
STREET = ["Alder Row", "Kestrel Lane", "Marsh Court", "Ninth Avenue", "Beltane Close"]
CITY = ["Fairhaven", "Northgate", "Portmere", "Ashcroft", "Linden Falls"]

# Spans that LOOK like PII and are not. Masking one is over-redaction.
DECOYS_PLAIN = [
    ("the Rivermouth Bridge", "a public landmark"),
    ("Form 27-B", "a public form number"),
    ("the Clean Water Act", "published legislation"),
    ("Building C", "a non-identifying location"),
    ("Q3", "a fiscal quarter"),
]
# Spans a CAUTIOUS model might defensibly mask. Masking one is OVER_BENIGN, not an error.
DECOYS_SENSITIVE = [
    ("Ardent Logistics Ltd", "an employer name -- arguably identifying in a small dataset"),
    ("the Northgate depot", "a workplace location -- arguably identifying"),
    ("2019", "a bare year -- arguably a quasi-identifier in combination"),
]

TEMPLATES = [
    ("incident",
     "{NAME} reported the fault at {TIME} on {DATE}. The reference given was {REF}. "
     "Follow-up correspondence should go to {EMAIL} or {PHONE}. The vehicle was parked near "
     "{DECOY0} at the time. {DECOY1} was cited in the report. Work continued through {DECOY2}."),
    ("membership",
     "The application from {NAME} of {ADDRESS} was received on {DATE}. Contact details on file "
     "are {EMAIL} and {PHONE}; the member number is {REF}. Proof of residence was accepted under "
     "{DECOY1}. The interview took place in {DECOY0}, and the outcome was recorded in {DECOY2}."),
    ("appointment",
     "{NAME} is scheduled for {TIME} on {DATE}. Please confirm on {PHONE} or by email to "
     "{EMAIL}. The file reference is {REF}, and the address we hold is {ADDRESS}. Parking is "
     "available beside {DECOY0}. Eligibility was assessed against {DECOY1} during {DECOY2}."),
]

PROMPT = """Redact the personal information in the document below.

Replace each piece of personal information with [REDACTED]. Leave everything else exactly as
it is — same wording, same order, same punctuation. Return only the redacted document.

---
{doc}
---"""


def _phone(rng):
    return "0%d %d %d" % (rng.randint(100, 999), rng.randint(100, 999), rng.randint(1000, 9999))


def build_items(seed=20260821, n_items=45):
    rng = random.Random(seed)
    items = []
    for i in range(n_items):
        key, tmpl = TEMPLATES[i % len(TEMPLATES)]
        name = "%s %s" % (rng.choice(FIRST), rng.choice(LAST))
        addr = "%d %s, %s" % (rng.randint(1, 200), rng.choice(STREET), rng.choice(CITY))
        email = "%s.%s@example.invalid" % (name.split()[0].lower(), name.split()[1].lower())
        phone = _phone(rng)
        ref = "%s-%04d" % (rng.choice("ABCDEFGH"), rng.randint(1000, 9999))
        date = "%d %s %d" % (rng.randint(1, 28),
                             rng.choice(["January", "March", "June", "September", "November"]),
                             rng.randint(2021, 2025))
        time_ = "%02d:%02d" % (rng.randint(8, 17), rng.choice([0, 15, 30, 45]))

        d_plain = rng.sample(DECOYS_PLAIN, 2)
        d_sens = rng.choice(DECOYS_SENSITIVE)
        decoys = [d_plain[0], d_plain[1], d_sens]

        doc = tmpl.format(NAME=name, ADDRESS=addr, EMAIL=email, PHONE=phone, REF=ref,
                          DATE=date, TIME=time_,
                          DECOY0=decoys[0][0], DECOY1=decoys[1][0], DECOY2=decoys[2][0])

        # ⛔ Only spans that ACTUALLY APPEAR in this document are ground truth. A template that
        #    does not use {ADDRESS} must not demand it be redacted.
        pii = [v for v in (name, addr, email, phone, ref) if v in doc]

        items.append({
            "family": FAMILY, "name": NAME,
            "item_id": "f04_%s_%03d" % (key, i),
            "document": doc,
            "prompt": PROMPT.format(doc=doc),
            "must_redact": pii,
            "decoys_plain": [d[0] for d in d_plain],
            "decoys_sensitive": [d_sens[0]],
            "decoy_reasons": {d[0]: d[1] for d in decoys},
            "equivalence_note": "[REDACTED] / [PII] / ███ / XXXX / <REDACTED> / (redacted) "
                                "are all accepted and treated as identical (qwen3-14b).",
        })
    return items


# ---------------------------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------------------------
def score(response, item):
    txt = (response or "").strip()
    if not txt:
        return ("MALFORMED", "empty response")
    txt = re.sub(r"^```[a-z]*\n|\n```$", "", txt).strip()
    txt = re.sub(r"^---\s*\n|\n\s*---$", "", txt).strip()

    canon = canon_redaction(txt)

    # A response that shares no structure with the document is not "an unredacted answer".
    doc_words = [w for w in canon_text(item["document"]).split() if len(w) > 3]
    kept = sum(1 for w in doc_words if w in canon_text(canon))
    if not doc_words or kept / len(doc_words) < 0.35:
        return ("META" if len(txt) < 200 else "MALFORMED",
                "response does not track the document (%d/%d content words kept)"
                % (kept, len(doc_words)))

    missed = [p for p in item["must_redact"] if p in txt]
    if missed:
        return ("UNDER", {"pii_left_in_the_clear": missed,
                          "redacted": len(item["must_redact"]) - len(missed),
                          "of": len(item["must_redact"])})

    over_harmful = [d for d in item["decoys_plain"] if d not in txt]
    over_benign = [d for d in item["decoys_sensitive"] if d not in txt]

    if over_harmful:
        # ⛔ Ordinary content destroyed. Counts.
        return ("OVER_HARMFUL", {"non_pii_masked": over_harmful,
                                 "why_not_pii": {d: item["decoy_reasons"][d]
                                                 for d in over_harmful}})
    if over_benign:
        # ⭐ A defensible judgement call by a cautious model. Reported, never counted against.
        return ("OVER_BENIGN", {"cautiously_masked": over_benign,
                                "why_defensible": {d: item["decoy_reasons"][d]
                                                   for d in over_benign}})
    return ("EXACT", None)


# ---------------------------------------------------------------------------------------------
# Controls
# ---------------------------------------------------------------------------------------------
def self_test():
    items = build_items()
    it = items[0]
    doc = it["document"]

    def redact(text, spans, token="[REDACTED]"):
        for s in spans:
            text = text.replace(s, token)
        return text

    perfect = redact(doc, it["must_redact"])

    cases = [
        ("EXACT", perfect, "canonical [REDACTED]"),
        # ✅ qwen3-14b's equivalence: different token, same act
        ("EXACT", redact(doc, it["must_redact"], "[PII]"), "[PII] token"),
        ("EXACT", redact(doc, it["must_redact"], "███"), "block token"),
        ("EXACT", redact(doc, it["must_redact"], "XXXX"), "XXXX token"),
        ("EXACT", "```\n" + perfect + "\n```", "fenced"),
        ("UNDER", redact(doc, it["must_redact"][1:]), "one PII span left in the clear"),
        ("OVER_HARMFUL", redact(perfect, [it["decoys_plain"][0]]), "masked a public landmark"),
        ("OVER_BENIGN", redact(perfect, [it["decoys_sensitive"][0]]),
         "masked an employer name — defensible caution"),
        ("META", "Which fields count as personal information here?", "question"),
        ("MALFORMED", "", "empty"),
    ]

    bad = 0
    for want, resp, label in cases:
        got, detail = score(resp, it)
        if got != want:
            bad += 1
            print("  FAIL  %-38s want=%-14s got=%-14s %s"
                  % (label, want, got, str(detail)[:50]))

    # ⛔ ADVERSARIAL: the UNTOUCHED document must be UNDER, never EXACT.
    got, _d = score(doc, it)
    if got != "UNDER":
        bad += 1
        print("  FAIL  untouched document scored %s, expected UNDER" % got)

    # ⛔ ADVERSARIAL: "redact aggressively" must not score as well as "redact correctly".
    #
    # 🚨 MY FIRST VERSION OF THIS CONTROL DID NOT TEST WHAT IT CLAIMED. It masked every
    #    capitalised word — which leaves emails, phone numbers and refs untouched, so it
    #    tripped UNDER (PII in the clear) rather than the over-redaction gate. It "passed"
    #    only because I had asserted `got not in (EXACT, OVER_BENIGN)`, which UNDER satisfies.
    #    ⭐ A CONTROL THAT TRIPS A DIFFERENT GATE HAS NOT TESTED THE GATE YOU MEANT — the same
    #       error I made on the allergen distinct-cuisine gate three hours earlier. Assert the
    #       SPECIFIC bucket, never merely "not the good one."
    over_everything = redact(redact(doc, it["must_redact"]),
                             it["decoys_plain"] + it["decoys_sensitive"])
    got, _d = score(over_everything, it)
    if got != "OVER_HARMFUL":
        bad += 1
        print("  FAIL  all-PII-plus-all-decoys scored %s, expected OVER_HARMFUL "
              "-- the decoys are not doing their job" % got)

    # ⛔ And the reverse asymmetry: masking ONLY the sensitive decoys on top of correct work
    #    must stay BENIGN. A cautious model is not a wrong one.
    cautious = redact(perfect, it["decoys_sensitive"])
    got, _d = score(cautious, it)
    if got != "OVER_BENIGN":
        bad += 1
        print("  FAIL  cautious-but-correct scored %s, expected OVER_BENIGN" % got)

    emitted = {score(r, it)[0] for _w, r, _l in cases}
    for req in ("EXACT", "UNDER", "OVER_HARMFUL", "OVER_BENIGN", "META", "MALFORMED"):
        if req not in emitted:
            bad += 1
            print("  FAIL  scorer never emitted %s in controls" % req)

    print("\n  items generated : %d  (%d templates)" % (len(items), len(TEMPLATES)))
    print("  pii spans/item  : %s" % sorted({len(i["must_redact"]) for i in items}))
    print("  decoys          : %d plain (masking = OVER_HARMFUL) · %d sensitive "
          "(masking = OVER_BENIGN, never counted against)"
          % (len(DECOYS_PLAIN), len(DECOYS_SENSITIVE)))
    print("  token equivalence published in every item (qwen3-14b)")
    if bad:
        print("\n!! FAMILY 04 CONTROLS FAILED (%d). Per F1/§5.3 this family DOES NOT SHIP." % bad)
        return False
    print("  controls        : %d/%d pass + 3 adversarial (each asserting a SPECIFIC "
          "bucket) + bucket reachability" % (len(cases), len(cases)))
    return True


if __name__ == "__main__":
    if "--emit" in sys.argv:
        out = sys.argv[sys.argv.index("--emit") + 1]
        with open(out, "w", encoding="utf-8") as f:
            json.dump({"family": FAMILY, "name": NAME, "seed": 20260821,
                       "synthetic_only": True, "items": build_items()}, f, indent=2)
        print("wrote %s" % out)
        sys.exit(0)
    sys.exit(0 if self_test() else 1)
