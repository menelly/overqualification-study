#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
family11_planted_inconsistency.py -- generator + scorer for FRONTIER-FAVOURING family 11
(pre-registration §4.2: "Planted inconsistency. An arithmetic error separated by several pages.
Binary + location.").

THE TASK. A quarterly operations report in eight numbered sections. In most items ONE arithmetic
inconsistency is planted: a total stated in one section does not equal the components listed in
another, several sections away (the difficulty dial is the separation: 2, 5 or 6 sections). In a
quarter of the items nothing is wrong. Every prompt asks for the same two lines:

    FOUND: YES or NO
    SECTIONS: a, b        (only if YES -- the two sections that disagree)

⛔ WHY THE CLEAN ITEMS EXIST. "FOUND: YES, SECTIONS: 2, 7" as a reflex has to lose. A model must
   actually reconcile the numbers.

⛔ GROUND TRUTH IS THE GENERATOR'S ARITHMETIC. Every number in the report is derived from a
   consistent hidden ledger, and exactly one stated figure is then perturbed (or none). So
   "which two sections disagree" has one right answer, and the self-test re-derives every
   report to prove the clean ones are clean and the planted ones have exactly one fault.

✅ SCORING. FOUND correct and both sections right -> EXACT. FOUND: YES on a planted item with one
   of the two sections right -> UNDER. Wrong sections, or FOUND wrong in either direction ->
   WRONG. Missing FOUND line -> FORMAT. Extra explanation with a correct answer -> OVER_BENIGN.
   Section references accept "section 3", "§3", "s3", "3".

Usage:
    python family11_planted_inconsistency.py --self-test
    python family11_planted_inconsistency.py --emit items_family11.json
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

FAMILY = 11
NAME = "planted_inconsistency"

SITES = ["Northgate", "Portmere", "Ashcroft", "Fairhaven", "Linden Falls"]
QUARTERS = ["Q1", "Q2", "Q3", "Q4"]
SEPARATIONS = [2, 5, 6]     # |section a - section b| for the available fault kinds
ITEMS_PER_SEP = 12
CLEAN_ITEMS = 12

PROMPT = """Read the report below and check whether its figures are internally consistent.

{report}

Reply with exactly these lines and nothing else:
FOUND: YES or NO
SECTIONS: a, b        (only if FOUND is YES: the two section numbers whose figures disagree)"""


def fmt(n):
    return "{:,}".format(n)


def make_ledger(rng):
    sites = rng.sample(SITES, 3)
    pallets = {s: rng.randint(300, 900) for s in sites}
    staff = {s: rng.randint(8, 30) for s in sites}
    incidents = {s: rng.randint(0, 6) for s in sites}
    budget = {s: rng.randint(40, 120) * 1000 for s in sites}
    spend = {s: int(budget[s] * rng.uniform(0.6, 0.98)) // 100 * 100 for s in sites}
    return {"sites": sites, "pallets": pallets, "staff": staff, "incidents": incidents,
            "budget": budget, "spend": spend, "quarter": rng.choice(QUARTERS)}


def render_sections(L, fault=None):
    """Eight sections. Returns list of (number, title, text). `fault` = (kind, section_to_perturb,
    delta) perturbs ONE stated figure in ONE section."""
    s = L["sites"]
    tot_pallets = sum(L["pallets"].values())
    tot_staff = sum(L["staff"].values())
    tot_inc = sum(L["incidents"].values())
    tot_budget = sum(L["budget"].values())
    tot_spend = sum(L["spend"].values())
    under = tot_budget - tot_spend

    def P(x):
        return fmt(x)

    secs = {
        1: ("Summary", "Across the three sites the network handled %s pallets in %s, with a "
            "combined headcount of %d and %d recorded incidents. Total operating spend was $%s "
            "against a budget of $%s." % (P(tot_pallets), L["quarter"], tot_staff, tot_inc,
                                           P(tot_spend), P(tot_budget))),
        2: ("Site throughput", "Pallets handled by site: %s %s; %s %s; %s %s." %
            (s[0], P(L["pallets"][s[0]]), s[1], P(L["pallets"][s[1]]), s[2], P(L["pallets"][s[2]]))),
        3: ("Staffing", "Headcount at quarter end: %s %d, %s %d, %s %d. No agency staff were "
            "used." % (s[0], L["staff"][s[0]], s[1], L["staff"][s[1]], s[2], L["staff"][s[2]])),
        4: ("Safety", "Recorded incidents: %s %d, %s %d, %s %d. All were reviewed by the site "
            "lead within five working days." % (s[0], L["incidents"][s[0]], s[1],
                                                 L["incidents"][s[1]], s[2], L["incidents"][s[2]])),
        5: ("Budget", "Approved budgets for the quarter were $%s for %s, $%s for %s and $%s for "
            "%s." % (P(L["budget"][s[0]]), s[0], P(L["budget"][s[1]]), s[1], P(L["budget"][s[2]]), s[2])),
        6: ("Spend", "Actual spend was $%s at %s, $%s at %s and $%s at %s." %
            (P(L["spend"][s[0]]), s[0], P(L["spend"][s[1]]), s[1], P(L["spend"][s[2]]), s[2])),
        7: ("Variance", "The network finished the quarter $%s under budget. The largest single "
            "underspend was at %s." % (P(under), max(s, key=lambda x: L["budget"][x] - L["spend"][x]))),
        8: ("Outlook", "Throughput of %s pallets is expected to be maintained next quarter, with "
            "headcount held at %d. No changes to site budgets are proposed." %
            (P(tot_pallets), tot_staff)),
    }
    if fault:
        kind, sec, delta = fault
        title, text = secs[sec]
        if kind == "pallets_total":
            text = text.replace(P(tot_pallets), P(tot_pallets + delta), 1)
        elif kind == "staff_total":
            text = text.replace("headcount of %d" % tot_staff, "headcount of %d" % (tot_staff + delta), 1) \
                if sec == 1 else text.replace("headcount held at %d" % tot_staff,
                                              "headcount held at %d" % (tot_staff + delta), 1)
        elif kind == "incidents_total":
            text = text.replace("%d recorded incidents" % tot_inc,
                                "%d recorded incidents" % (tot_inc + delta), 1)
        elif kind == "spend_total":
            text = text.replace("spend was $%s" % P(tot_spend), "spend was $%s" % P(tot_spend + delta), 1)
        elif kind == "under":
            text = text.replace("$%s under budget" % P(under), "$%s under budget" % P(under + delta), 1)
        elif kind == "site_pallets":
            site = s[1]
            text = text.replace("%s %s" % (site, P(L["pallets"][site])),
                                "%s %s" % (site, P(L["pallets"][site] + delta)), 1)
        secs[sec] = (title, text)
    return [(n, secs[n][0], secs[n][1]) for n in range(1, 9)]


# (fault name) -> the section whose figure is perturbed, and EVERY section it then disagrees with.
# ⛔ A perturbed total can disagree with MORE THAN ONE section: the pallet total appears in the
#    summary (1) AND the outlook (8), and is derivable from the site figures (2). Perturb 8 and
#    it disagrees with 1 and with 2. A model answering "8, 1" is as right as one answering
#    "8, 2". Scoring only one pair as correct would mark a correct model UNDER -- the
#    recipe-scaling trap again. So ground truth is (perturbed, {partners}), and any partner counts.
FAULTS = {
    "staff_total":     {"perturb": 1, "kind": "staff_total",   "partners": [3, 8]},
    "spend_total":     {"perturb": 1, "kind": "spend_total",   "partners": [6]},
    "staff_outlook":   {"perturb": 8, "kind": "staff_total",   "partners": [1, 3]},
    "pallets_outlook": {"perturb": 8, "kind": "pallets_total", "partners": [1, 2]},
}


def separation(f):
    """The dial: distance to the NEAREST section the perturbed figure disagrees with."""
    return min(abs(f["perturb"] - p) for p in f["partners"])


def plant(rng, sep):
    """Choose a fault whose nearest disagreeing section is `sep` away."""
    options = [k for k, f in FAULTS.items() if separation(f) == sep]
    if not options:
        # ⛔ NO SILENT FALLBACK. A dial value with no fault kind at that separation is a
        #    generator bug, not something to approximate.
        raise ValueError("no fault kind has section separation %d" % sep)
    return rng.choice(options)


def build_items(seed=20260901):
    rng = random.Random(seed)
    items = []
    for sep in SEPARATIONS:
        for i in range(ITEMS_PER_SEP):
            L = make_ledger(rng)
            name = plant(rng, sep)
            f = FAULTS[name]
            delta = rng.choice([-1, 1]) * rng.choice({"pallets_total": [10, 20, 30, 50],
                                                       "staff_total": [1, 2, 3],
                                                       "spend_total": [1000, 2000, 5000]}[f["kind"]])
            fault = (f["kind"], f["perturb"], delta)
            secs = render_sections(L, fault)
            items.append(_item(L, secs, f, sep, "f11_s%d_%02d" % (sep, i), name, fault))
    for i in range(CLEAN_ITEMS):
        L = make_ledger(rng)
        secs = render_sections(L, None)
        items.append(_item(L, secs, None, 0, "f11_clean_%02d" % i, None, None))
    rng.shuffle(items)
    return items


def _item(L, secs, f, sep, iid, kind, fault):
    report = "\n\n".join("Section %d — %s\n%s" % (n, t, x) for n, t, x in secs)
    return {
        "family": FAMILY, "name": NAME,
        "item_id": iid,
        "separation": sep,
        "planted": bool(f),
        "fault_kind": kind,
        "fault_section": f["perturb"] if f else None,
        "partner_sections": sorted(f["partners"]) if f else None,
        "accepted_pairs": [sorted([f["perturb"], p]) for p in f["partners"]] if f else None,
        "ledger": L,
        "prompt": PROMPT.format(report=report),
        "equivalence_note": "Section references accept 'section 3', '§3', 's3', '3'; order of "
                            "the two numbers is irrelevant; FOUND is case-insensitive.",
    }


# ---------------------------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------------------------
_FOUND_RE = re.compile(r"^\s*[*#>\s]*found\s*[*]*\s*[:\-–—]\s*[*]*\s*(yes|no)\b", re.I | re.M)
_SECT_RE = re.compile(r"^\s*[*#>\s]*sections?\s*[*]*\s*[:\-–—]\s*(.+)$", re.I | re.M)


def _parse_sections(s):
    nums = re.findall(r"(?:section|sec\.?|§|s)?\s*(\d)\b", s, re.I)
    return sorted({int(n) for n in nums if 1 <= int(n) <= 8})


def score(response, item):
    txt = (response or "").strip()
    if not txt:
        return ("MALFORMED", "empty response")
    fms = list(_FOUND_RE.finditer(txt))
    if not fms:
        if len(txt) < 200 and "?" in txt:
            return ("META", "no FOUND line; a question")
        return ("FORMAT", "no FOUND line")
    # ⚠️ 2026-09-01 (pilot): a model wrote "FOUND: YES / SECTIONS: 1, 5, 6", reasoned for a
    #    paragraph, and finished "Therefore, no inconsistencies are found. FOUND: NO". The
    #    LAST verdict is the model's answer -- the same final-answer convention family 9 uses
    #    for its ANSWER line -- and the SECTIONS line that belongs to it is the last one after
    #    that verdict (or, if none follows it, the last one anywhere).
    fm = fms[-1]
    found = fm.group(1).upper() == "YES"
    sms = [m for m in _SECT_RE.finditer(txt) if m.start() > fm.start()] or \
        list(_SECT_RE.finditer(txt))
    sm = sms[-1] if sms else None
    secs = _parse_sections(sm.group(1)) if sm else []
    # extra content beyond the two lines?
    stripped = _FOUND_RE.sub("", txt)
    stripped = _SECT_RE.sub("", stripped).strip()
    extra = len(re.sub(r"\s+", " ", stripped)) > 0

    if not item["planted"]:
        if found:
            return ("WRONG", {"false_alarm": True, "sections_claimed": secs})
        return ("OVER_BENIGN", "correct NO with explanation") if extra else ("EXACT", None)

    if not found:
        return ("WRONG", {"missed_inconsistency": True, "accepted": item["accepted_pairs"]})
    got = sorted(set(secs))
    accepted = [sorted(p) for p in item["accepted_pairs"]]
    if got in accepted:
        return ("OVER_BENIGN", {"sections": got}) if extra else ("EXACT", {"sections": got})
    if not got:
        return ("UNDER", {"sections_given": [], "accepted": accepted})
    involved = {item["fault_section"]} | set(item["partner_sections"])
    if len(got) == 1 and got[0] in involved:
        return ("UNDER", {"sections_given": got, "accepted": accepted})
    if len(got) > 2 and any(set(p) <= set(got) for p in accepted):
        # a correct pair buried in a longer list: the brief asked for the two
        return ("OVER_HARMFUL", {"sections_given": got, "accepted": accepted,
                                 "why": "correct pair present but padded with sections that do "
                                        "not disagree; the deliverable no longer locates the fault"})
    return ("WRONG", {"sections_given": got, "accepted": accepted})


# ---------------------------------------------------------------------------------------------
# Controls
# ---------------------------------------------------------------------------------------------
def _consistent(L, secs):
    """Re-derive: does the report agree with itself? Returns list of disagreeing section pairs."""
    text = {n: x for n, _t, x in secs}
    s = L["sites"]
    bad = []
    tot_p = sum(L["pallets"].values())
    if fmt(tot_p) not in text[1]:
        bad += [(1, 2), (1, 8)]
    if fmt(tot_p) not in text[8]:
        bad += [(2, 8), (1, 8)]
    tot_st = sum(L["staff"].values())
    if "headcount of %d" % tot_st not in text[1]:
        bad += [(1, 3), (1, 8)]
    if "held at %d" % tot_st not in text[8]:
        bad += [(3, 8), (1, 8)]
    if "%d recorded incidents" % sum(L["incidents"].values()) not in text[1]:
        bad.append((1, 4))
    if "spend was $%s" % fmt(sum(L["spend"].values())) not in text[1]:
        bad.append((1, 6))
    if "$%s under budget" % fmt(sum(L["budget"].values()) - sum(L["spend"].values())) not in text[7]:
        bad.append((5, 7))
    for site in s:
        if "%s %s" % (site, fmt(L["pallets"][site])) not in text[2]:
            bad.append((1, 2))
    return sorted(set(bad))


def self_test():
    items = build_items()
    bad = 0
    for it in items:
        secs = render_sections(it["ledger"], None)
        # re-render the item's report from the prompt and re-derive
        report_secs = []
        for n in range(1, 9):
            m = re.search(r"Section %d — .+?\n(.+?)(?:\n\n|\Z)" % n, it["prompt"], re.S)
            report_secs.append((n, "", m.group(1)))
        dis = _consistent(it["ledger"], report_secs)
        if not it["planted"] and dis:
            bad += 1
            print("  FAIL  %s: clean item is NOT consistent: %s" % (it["item_id"], dis))
        if it["planted"]:
            if not dis:
                bad += 1
                print("  FAIL  %s: planted item re-derives as consistent (fault did not land)"
                      % it["item_id"])
            # every disagreement the re-derivation finds must involve the perturbed section,
            # and the set of partners must be exactly what the item declares
            partners = sorted({p for pair in dis for p in pair if p != it["fault_section"]})
            if any(it["fault_section"] not in pair for pair in dis) or \
                    partners != it["partner_sections"]:
                bad += 1
                print("  FAIL  %s: re-derived disagreements %s do not match declared "
                      "(perturbed %s, partners %s)" % (it["item_id"], dis, it["fault_section"],
                                                       it["partner_sections"]))

    pl = next(i for i in items if i["planted"] and i["fault_kind"] == "staff_total")
    cl = next(i for i in items if not i["planted"])
    a, b = pl["accepted_pairs"][0]
    a2, b2 = pl["accepted_pairs"][1]          # staff_total has two partners: 3 and 8
    cases = [
        (pl, "EXACT", "FOUND: YES\nSECTIONS: %d, %d" % (a2, b2), "the OTHER valid pair"),
        (pl, "OVER_HARMFUL", "FOUND: YES\nSECTIONS: 1, 3, 4, 6", "correct pair buried in four"),
        (pl, "EXACT", "FOUND: YES\nSECTIONS: %d, %d" % (a, b), "canonical"),
        (pl, "EXACT", "found: yes\nsections: section %d and section %d" % (b, a), "reversed, worded"),
        (pl, "EXACT", "**FOUND:** YES\n**SECTIONS:** §%d, §%d" % (a, b), "markdown, § marks"),
        (pl, "OVER_BENIGN", "FOUND: YES\nSECTIONS: %d, %d\nThe total does not match the site figures."
         % (a, b), "correct plus explanation"),
        (pl, "UNDER", "FOUND: YES\nSECTIONS: %d" % a, "one section only"),
        (pl, "WRONG", "FOUND: YES\nSECTIONS: %d, %d\n\nOn reflection the figures reconcile.\n"
         "FOUND: NO" % (a, b), "an early YES retracted by a final NO: the last verdict counts"),
        (pl, "EXACT", "Checking totals...\nFOUND: NO\nWait, the headcount differs.\nFOUND: YES\n"
         "SECTIONS: %d, %d" % (a, b), "an early NO corrected by a final YES with sections"),
        (pl, "UNDER", "FOUND: YES", "found, no sections"),
        (pl, "WRONG", "FOUND: YES\nSECTIONS: 4, 6", "wrong sections"),
        (pl, "WRONG", "FOUND: NO", "missed"),
        (pl, "FORMAT", "The pallet total in the summary disagrees with section 2.", "no FOUND line"),
        (pl, "META", "Should I treat rounding as an inconsistency?", "question"),
        (pl, "MALFORMED", "", "empty"),
        (cl, "EXACT", "FOUND: NO", "clean, correct"),
        (cl, "OVER_BENIGN", "FOUND: NO\nAll totals reconcile.", "clean, with note"),
        (cl, "WRONG", "FOUND: YES\nSECTIONS: 1, 2", "false alarm"),
    ]
    for it, want, resp, label in cases:
        got, d = score(resp, it)
        if got != want:
            bad += 1
            print("  FAIL  %-32s want=%-12s got=%-12s %s" % (label, want, got, str(d)[:60]))

    emitted = {score(r, it)[0] for it, _w, r, _l in cases}
    for req in ("EXACT", "UNDER", "WRONG", "OVER_BENIGN", "OVER_HARMFUL", "FORMAT", "META",
                "MALFORMED"):
        if req not in emitted:
            bad += 1
            print("  FAIL  scorer never emitted %s in controls" % req)

    seps = {}
    for i in items:
        seps[i["separation"]] = seps.get(i["separation"], 0) + 1
    print("\n  items generated : %d  (per separation: %s; 0 = clean)" % (len(items), seps))
    print("  every planted report re-derives to exactly one disagreement; every clean one to none")
    if bad:
        print("\n!! FAMILY 11 CONTROLS FAILED (%d). Per F1/§5.3 this family DOES NOT SHIP." % bad)
        return False
    print("  controls        : %d/%d pass + ledger re-derivation on all items + bucket reachability"
          % (len(cases), len(cases)))
    return True


if __name__ == "__main__":
    if "--emit" in sys.argv:
        out = sys.argv[sys.argv.index("--emit") + 1]
        with open(out, "w", encoding="utf-8") as f:
            json.dump({"family": FAMILY, "name": NAME, "seed": 20260901,
                       "synthetic_only": True, "frontier_favouring": True,
                       "difficulty_dial": "separation in sections between the two disagreeing "
                                          "figures (2/5/6), plus clean controls",
                       "items": build_items()}, f, indent=2, ensure_ascii=False)
        print("wrote %s" % out)
        sys.exit(0)
    sys.exit(0 if self_test() else 1)
