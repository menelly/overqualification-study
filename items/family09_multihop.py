#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
family09_multihop.py -- generator + scorer for FRONTIER-FAVOURING family 9
(pre-registration §4.2: "Multi-hop with planted distractors. Answer requires combining facts
separated in a long document, with plausible decoys adjacent to each.").

THE TASK. A long, dull site directory (~80-120 sentences, shuffled) states facts of the form
"X works at site S", "site S is managed by M", "M's extension is E", "the fire warden for S is W".
The question needs 2, 3 or 4 of those facts chained together (the difficulty dial), and the facts
are deliberately scattered far apart in the document.

⛔ THE DISTRACTORS ARE THE POINT. For every fact on the chain there is a decoy that is textually
   near-identical and wrong: a second person with the same surname at another site; a site whose
   name differs by one word ("Northgate depot" vs "Northgate annex"); a superseded extension
   printed as "(formerly 4471)". A model that pattern-matches the nearest plausible number will
   land on a decoy. Ground truth is the generator's own chain, so correctness is mechanical.

✅ EQUIVALENCE, PUBLISHED BEFORE COLLECTION: the answer is compared after canonicalisation --
   case-insensitive, punctuation-stripped, "ext. 4471" == "4471" == "extension 4471"; a name is
   matched on full name, and on surname alone only when the surname is unique in the document.

✅ REQUIRED CONTAINER: the last line "ANSWER: <value>". A correct value stated somewhere in
   prose but not on an ANSWER line scores FORMAT (right content, wrong container), never WRONG.

Usage:
    python family09_multihop.py --self-test
    python family09_multihop.py --emit items_family09.json
"""

from __future__ import annotations

import sys as _sys_cp1252
try:
    _sys_cp1252.stdout.reconfigure(encoding="utf-8")
    _sys_cp1252.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

import json
import os
import random
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from equivalence import canon_text                                    # noqa: E402

FAMILY = 9
NAME = "multihop_distractors"

FIRST = ["Marta", "Devon", "Priya", "Ola", "Ibrahim", "Sanne", "Tomas", "Rin", "Ayesha", "Milo",
         "Yusuf", "Elin", "Rafael", "Hana", "Kwame", "Sofia", "Arjun", "Beatrix", "Nikolai", "Zara"]
LAST = ["Okonkwo", "Vasquez", "Lindqvist", "Haddad", "Nakamura", "Baptiste", "Ferreira",
        "Novak", "Adeyemi", "Kowalski", "Moreau", "Sato", "Ahmadi", "Byrne", "Castellano"]
SITE_BASE = ["Northgate", "Portmere", "Ashcroft", "Fairhaven", "Linden Falls", "Kestrel Park",
             "Marsh Court", "Beltane", "Rivermouth", "Alderfield"]
SITE_KIND = ["depot", "annex", "yard", "workshop", "office"]
DEPTS = ["dispatch", "maintenance", "records", "procurement", "safety", "fleet"]

HOPS = [2, 3, 4]
ITEMS_PER_HOP = 16

FILLER = [
    "The {site} car park is resurfaced every third summer.",
    "Visitors to {site} sign in at the front desk.",
    "The {dept} team at {site} meets on Thursdays.",
    "Deliveries to {site} are accepted between eight and four.",
    "The canteen at {site} closes at half past two.",
    "Fire drills at {site} are held quarterly.",
    "The {dept} noticeboard at {site} is beside the lift.",
    "Recycling at {site} is collected on Mondays.",
    "The {site} bicycle shelter holds twelve bicycles.",
    "Lost property for {site} is kept at the front desk for thirty days.",
]

PROMPT = """Use only the directory below to answer the question at the end.

--- DIRECTORY ---
{doc}
--- END ---

Question: {question}

Give the answer on the last line of your reply, in exactly this form:
ANSWER: <the answer>"""


def _ext(rng, avoid):
    while True:
        e = "%04d" % rng.randint(2000, 8999)
        if e not in avoid:
            return e


def build_world(rng, n_sites=6, n_people=14):
    """A consistent little organisation, plus decoys engineered against each true fact."""
    bases = rng.sample(SITE_BASE, n_sites)
    sites = []
    for b in bases:
        kind = rng.choice(SITE_KIND)
        sites.append("%s %s" % (b, kind))
    people = []
    used = set()
    while len(people) < n_people:
        fn, ln = rng.choice(FIRST), rng.choice(LAST)
        if (fn, ln) in used:
            continue
        used.add((fn, ln))
        people.append("%s %s" % (fn, ln))
    exts = set()
    ext_of = {}
    for p in people:
        ext_of[p] = _ext(rng, exts)
        exts.add(ext_of[p])
    site_of = {p: rng.choice(sites) for p in people}
    manager_of = {}
    warden_of = {}
    for s in sites:
        staff = [p for p in people if site_of[p] == s] or [rng.choice(people)]
        manager_of[s] = rng.choice(staff)
        warden_of[s] = rng.choice(staff)
    dept_of = {p: rng.choice(DEPTS) for p in people}
    return {"sites": sites, "people": people, "ext": ext_of, "site": site_of,
            "manager": manager_of, "warden": warden_of, "dept": dept_of}


def build_chain(rng, w, hops):
    """Returns (question, answer, facts[]) where facts are the sentences that must be combined."""
    people = w["people"]
    p0 = rng.choice(people)
    s0 = w["site"][p0]
    m = w["manager"][s0]
    facts = ["%s works at the %s." % (p0, s0)]
    if hops == 2:
        # who manages the site where P works?
        facts.append("The %s is managed by %s." % (s0, m))
        q = "Who manages the site where %s works?" % p0
        ans, kind = m, "name"
    elif hops == 3:
        facts.append("The %s is managed by %s." % (s0, m))
        facts.append("%s can be reached on extension %s." % (m, w["ext"][m]))
        q = "What is the extension of the manager of the site where %s works?" % p0
        ans, kind = w["ext"][m], "ext"
    else:
        facts.append("The %s is managed by %s." % (s0, m))
        s1 = w["site"][m] if w["site"][m] != s0 else rng.choice([s for s in w["sites"] if s != s0])
        facts.append("%s is also the fire warden for the %s." % (m, s1))
        wd = w["warden"][s1] if w["warden"][s1] != m else rng.choice([p for p in people if p != m])
        # ⛔ CONSISTENCY: the world's own warden sentence for s1 is emitted by build_document.
        #    If we had to pick a different warden (because the world's was m), the world must be
        #    updated too, or the document would name two fire wardens for one site.
        w["warden"][s1] = wd
        facts[-1] = "%s is registered as a first-aider at the %s." % (m, s1)
        facts.append("The fire warden for the %s is %s." % (s1, wd))
        facts.append("%s can be reached on extension %s." % (wd, w["ext"][wd]))
        q = ("What is the extension of the fire warden at the site where the manager of "
             "%s's site is registered as a first-aider?" % p0)
        ans, kind = w["ext"][wd], "ext"
    return q, ans, kind, facts, p0, m


def build_decoys(rng, w, facts, p0, m, ans, kind):
    """One decoy per true fact, textually adjacent and wrong."""
    decoys = []
    ln = p0.split()[-1]
    other_first = rng.choice([f for f in FIRST if f != p0.split()[0]])
    twin = "%s %s" % (other_first, ln)                      # same surname, different person
    other_site = rng.choice([s for s in w["sites"] if s != w["site"][p0]])
    decoys.append("%s works at the %s." % (twin, other_site))
    # near-identical site name
    base = w["site"][p0].split()[0:-1]
    near = " ".join(base) + " " + rng.choice([k for k in SITE_KIND if k != w["site"][p0].split()[-1]])
    other_mgr = rng.choice([p for p in w["people"] if p != m])
    decoys.append("The %s is managed by %s." % (near, other_mgr))
    if kind == "ext":
        old = _ext(rng, set(w["ext"].values()) | {ans})
        who = [f for f in facts if "extension" in f][-1].split(" can be")[0]
        decoys.append("%s's previous extension, %s, was withdrawn last year." % (who, old))
        decoys.append("%s can be reached on extension %s." % (twin, _ext(rng, set(w["ext"].values()) | {ans, old})))
    else:
        decoys.append("%s was previously managed by %s." % (w["site"][p0], other_mgr))
    return decoys


def build_document(rng, w, facts, decoys):
    sents = []
    for p in w["people"]:
        sents.append("%s works at the %s." % (p, w["site"][p]))
        sents.append("%s can be reached on extension %s." % (p, w["ext"][p]))
        sents.append("%s belongs to the %s team." % (p, w["dept"][p]))
    for s in w["sites"]:
        sents.append("The %s is managed by %s." % (s, w["manager"][s]))
        sents.append("The fire warden for the %s is %s." % (s, w["warden"][s]))
    for _ in range(30):
        sents.append(rng.choice(FILLER).format(site=rng.choice(w["sites"]), dept=rng.choice(DEPTS)))
    # de-duplicate against the chain facts (they are already in the world sentences, mostly)
    pool = list(dict.fromkeys(sents))
    for f in facts:
        if f not in pool:
            pool.append(f)
    rng.shuffle(pool)
    # force the chain facts far apart: place them at spread positions
    for f in facts:
        pool.remove(f)
    n = len(pool)
    slots = sorted(rng.sample(range(0, n), len(facts)))
    # guarantee spread: at least n//(len(facts)+1) apart
    step = max(4, n // (len(facts) + 1))
    slots = [min(n, i * step + rng.randint(0, 3)) for i in range(1, len(facts) + 1)]
    for f, pos in zip(facts, slots):
        pool.insert(min(pos, len(pool)), f)
    # decoys go NEAR their facts (within 2 sentences)
    for d, f in zip(decoys, facts + facts):
        i = pool.index(f)
        pool.insert(max(0, i + rng.choice([-2, -1, 1, 2])), d)
    return "\n".join(pool)


def build_items(seed=20260901):
    rng = random.Random(seed)
    items = []
    for hops in HOPS:
        made = 0
        while made < ITEMS_PER_HOP:
            w = build_world(rng)
            q, ans, kind, facts, p0, m = build_chain(rng, w, hops)
            if len({ans}) != 1:
                continue
            decoys = build_decoys(rng, w, facts, p0, m, ans, kind)
            doc = build_document(rng, w, facts, decoys)
            # the answer must appear in the doc exactly where the chain says, and the decoy
            # values must differ from the answer
            surname_unique = sum(1 for p in w["people"] if p.split()[-1] == ans.split()[-1]) == 1 \
                if kind == "name" else False
            items.append({
                "family": FAMILY, "name": NAME,
                "item_id": "f09_h%d_%02d" % (hops, made),
                "hops": hops,
                "answer": ans, "answer_kind": kind,
                "surname_unique": surname_unique,
                "chain_facts": facts,
                "decoys": decoys,
                "decoy_values": [re.findall(r"\b\d{4}\b", d) for d in decoys],
                "document_sentences": doc.count("\n") + 1,
                "prompt": PROMPT.format(doc=doc, question=q),
                "question": q,
                "equivalence_note": "ANSWER compared after canonicalisation: case/punctuation "
                                    "insensitive; 'ext. 4471' == '4471'; a name matches on full "
                                    "name, or surname alone if unique in the document.",
            })
            made += 1
    rng.shuffle(items)
    return items


# ---------------------------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------------------------
_ANS_RE = re.compile(r"^\s*\**\s*answer\s*\**\s*[:\-–—]\s*(.+?)\s*\**\s*$", re.I | re.M)


def _canon_answer(s, kind):
    s = canon_text(s or "")
    s = re.sub(r"\(.*?\)", "", s)
    if kind == "ext":
        digits = re.findall(r"\b\d{4}\b", s)
        return digits[-1] if digits else s.strip().lower()
    s = re.sub(r"\b(?:the|is|it's|it is|extension|ext\.?|manager|managed by)\b", " ", s, flags=re.I)
    return re.sub(r"[^a-z ]", "", s.lower()).strip()


def _matches(cand, item):
    kind = item["answer_kind"]
    want = _canon_answer(item["answer"], kind)
    got = _canon_answer(cand, kind)
    if kind == "ext":
        return got == want
    if got == want:
        return True
    if item.get("surname_unique") and got == want.split()[-1]:
        return True
    return want in got and len(got) <= len(want) + 12   # "marta okonkwo, the manager"


def score(response, item):
    txt = (response or "").strip()
    if not txt:
        return ("MALFORMED", "empty response")
    lines = _ANS_RE.findall(txt)
    kind = item["answer_kind"]
    if lines:
        cand = lines[-1]
        if _matches(cand, item):
            body = _ANS_RE.sub("", txt).strip()
            if body:
                return ("OVER_BENIGN", {"answer": cand, "extra_chars": len(body)})
            return ("EXACT", {"answer": cand})
        # a decoy?
        decoy_hit = any(v in _canon_answer(cand, "ext") for vs in item["decoy_values"] for v in vs) \
            if kind == "ext" else False
        return ("WRONG", {"answer": cand, "wanted": item["answer"],
                          "took_decoy_value": decoy_hit})
    # no ANSWER line. Right content in the wrong container?
    if kind == "ext":
        found = set(re.findall(r"\b\d{4}\b", txt))
        if found == {item["answer"]}:
            return ("FORMAT", "correct extension stated, no ANSWER line")
        if item["answer"] in found:
            return ("FORMAT", "correct extension present among %d candidates, no ANSWER line"
                    % len(found))
    else:
        if _canon_answer(item["answer"], kind) in _canon_answer(txt, kind):
            return ("FORMAT", "correct name stated, no ANSWER line")
    if len(txt) < 200 and "?" in txt:
        return ("META", "question back, no answer")
    return ("UNDER", "no ANSWER line and the correct value does not appear")


# ---------------------------------------------------------------------------------------------
# Controls
# ---------------------------------------------------------------------------------------------
def self_test():
    items = build_items()
    bad = 0
    # ⛔ every item: the answer must be derivable -- each chain fact must be in the prompt, and
    #    each decoy must be in the prompt, and no decoy value may equal the answer
    for it in items:
        p = it["prompt"]
        for f in it["chain_facts"]:
            if f not in p:
                bad += 1
                print("  FAIL  %s: chain fact missing from document: %s" % (it["item_id"], f))
        for d in it["decoys"]:
            if d not in p:
                bad += 1
                print("  FAIL  %s: decoy missing from document" % it["item_id"])
        if it["answer_kind"] == "ext":
            for vs in it["decoy_values"]:
                if it["answer"] in vs:
                    bad += 1
                    print("  FAIL  %s: a decoy carries the true answer" % it["item_id"])
            # the true extension must appear exactly once as the answer-holder's extension
            if p.count("extension %s." % it["answer"]) != 1:
                bad += 1
                print("  FAIL  %s: answer extension appears %d times"
                      % (it["item_id"], p.count("extension %s." % it["answer"])))
        # ⛔ one manager and one fire warden per site, stated once each. A document that names
        #    two wardens for one site has no single right answer, and the scorer would call a
        #    correct model WRONG.
        for s in re.findall(r"The fire warden for the (.+?) is ", p):
            n = p.count("The fire warden for the %s is " % s)
            if n != 1:
                bad += 1
                print("  FAIL  %s: '%s' has %d fire-warden sentences" % (it["item_id"], s, n))
        for s in re.findall(r"The (.+?) is managed by ", p):
            n = p.count("The %s is managed by " % s)
            if n != 1:
                bad += 1
                print("  FAIL  %s: '%s' has %d manager sentences" % (it["item_id"], s, n))

    ext_item = next(i for i in items if i["answer_kind"] == "ext")
    name_item = next(i for i in items if i["answer_kind"] == "name")
    A = ext_item["answer"]
    decoy_ext = next(v for vs in ext_item["decoy_values"] for v in vs)

    cases_ext = [
        ("EXACT", "ANSWER: %s" % A, "canonical"),
        ("EXACT", "**Answer:** ext. %s" % A, "bold, ext. prefix"),
        ("EXACT", "Answer - extension %s" % A, "dash, word extension"),
        ("OVER_BENIGN", "The manager is X, whose extension is listed.\nANSWER: %s" % A,
         "reasoning then answer"),
        ("WRONG", "ANSWER: %s" % decoy_ext, "took the decoy"),
        ("FORMAT", "The extension you want is %s." % A, "right value, no ANSWER line"),
        ("UNDER", "I could not find that person in the directory.", "no answer"),
        ("META", "Do you mean the current manager or the previous one?", "question"),
        ("MALFORMED", "", "empty"),
    ]
    for want, resp, label in cases_ext:
        got, d = score(resp, ext_item)
        if got != want:
            bad += 1
            print("  FAIL  ext  %-36s want=%-12s got=%-12s %s" % (label, want, got, str(d)[:50]))

    N = name_item["answer"]
    cases_name = [
        ("EXACT", "ANSWER: %s" % N, "canonical"),
        ("EXACT", "answer: %s." % N.lower(), "lowercase, trailing period"),
        ("WRONG", "ANSWER: %s" % name_item["decoys"][1].split("managed by ")[-1].rstrip("."),
         "took the near-site decoy manager"),
    ]
    if name_item["surname_unique"]:
        cases_name.append(("EXACT", "ANSWER: %s" % N.split()[-1], "surname only, unique"))
    for want, resp, label in cases_name:
        got, d = score(resp, name_item)
        if got != want:
            bad += 1
            print("  FAIL  name %-36s want=%-12s got=%-12s %s" % (label, want, got, str(d)[:50]))

    emitted = {score(r, ext_item)[0] for _w, r, _l in cases_ext}
    for req in ("EXACT", "UNDER", "WRONG", "OVER_BENIGN", "FORMAT", "META", "MALFORMED"):
        if req not in emitted:
            bad += 1
            print("  FAIL  scorer never emitted %s in controls" % req)

    hs = {}
    for i in items:
        hs[i["hops"]] = hs.get(i["hops"], 0) + 1
    print("\n  items generated : %d  (per hops: %s)" % (len(items), hs))
    print("  document length : %d-%d sentences" % (min(i["document_sentences"] for i in items),
                                                    max(i["document_sentences"] for i in items)))
    print("  every chain fact and decoy verified present; no decoy equals the answer")
    if bad:
        print("\n!! FAMILY 09 CONTROLS FAILED (%d). Per F1/§5.3 this family DOES NOT SHIP." % bad)
        return False
    print("  controls        : %d pass + document integrity on all items + bucket reachability"
          % (len(cases_ext) + len(cases_name)))
    return True


if __name__ == "__main__":
    if "--emit" in sys.argv:
        out = sys.argv[sys.argv.index("--emit") + 1]
        with open(out, "w", encoding="utf-8") as f:
            json.dump({"family": FAMILY, "name": NAME, "seed": 20260901,
                       "synthetic_only": True, "frontier_favouring": True,
                       "difficulty_dial": "hops = facts that must be chained (2/3/4)",
                       "items": build_items()}, f, indent=2, ensure_ascii=False)
        print("wrote %s" % out)
        sys.exit(0)
    sys.exit(0 if self_test() else 1)
