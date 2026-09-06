#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
60_verify_references.py — every reference in PAPER_DRAFT_v1.md checked against a live source.

WHY. The draft's DRAFT STATUS banner names "the reference list has been verified by script" as a
precondition for §7.3, and there was no such script in this repo. Adapted from
`consciousness-in-the-corpus/scripts/18_verify_references.py` (Ace, 2026-09-01).

A citation that reads fluently and does not exist is the classic silent failure of this kind of
authorship. Each entry is resolved against the source that would actually be cited: Crossref for
DOIs, arXiv's API for arXiv ids, a direct fetch for URLs. The script prints what it FOUND next to
what the paper CLAIMS. **It does not auto-correct anything.**

⚠️ AND IT REPORTS ITS OWN APERTURE. A verifier that checks a hand-typed list proves only that the
list is good — never that the list is complete. So §2 re-reads the draft and flags every
citation-shaped string (Author YYYY / doi: / arxiv: / http) that is NOT covered by the declared
list. A zero there is a coverage claim; a zero with no scan is nothing at all.

Usage:
    python 60_verify_references.py                       # verify + coverage scan
    python 60_verify_references.py --offline             # coverage scan only, no network

Exit 0 = every declared reference resolved AND nothing uncovered was found.

Built by: Ace — 2026-09-06, for the §7.3 gate.
"""
import argparse
import json
import os
import re
import sys
import urllib.parse
import urllib.request

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
UA = {"User-Agent": "ace-reference-check/1.0 (mailto:ace@sentientsystems.live)"}

# (key, kind, locator, expected title fragment, expected year, expected container fragment)
REFS = [
    ("Brier 1950 verification of forecasts", "doi",
     "10.1175/1520-0493(1950)078<0001:VOFEIT>2.0.CO;2",
     "Verification of Forecasts", 1950, "Monthly Weather Review"),
    ("Nosek 2018 preregistration revolution", "doi",
     "10.1073/pnas.1708274114",
     "preregistration revolution", 2018, "Proceedings of the National Academy of Sciences"),
]

# Strings that look like citations but are ours, or are not external works.
COVERAGE_ALLOW = re.compile(
    r"""(
        orcid\.org                      # author ORCID in the byline
      | sentientsystems\.live           # our contact address
      | github\.com/menelly             # our own repo
      )""", re.I | re.X)

PATTERNS = [
    # "Brier, G. W. (1950)" · "Nosek, B. A., ... (2018)" · "Smith et al. (2024)" · "Smith & Jones (2024)"
    ("author-year", re.compile(r"\b[A-Z][a-z]{2,}"
                               r"(?:,?\s+(?:[A-Z]\.\s*)+)?"          # optional initials
                               r"(?:\s*(?:,|&|and)\s*[A-Z][a-z]{2,}(?:,?\s+(?:[A-Z]\.\s*)+)?)*"
                               r"(?:\s+et\s+al\.?)?"
                               r"\s*[,]?\s*\((?:19|20)\d{2}\)")),
    ("doi", re.compile(r"doi:\s*10\.\S+", re.I)),
    ("arxiv", re.compile(r"arxiv[:\s/]+\d{4}\.\d{4,5}", re.I)),
    ("url", re.compile(r"https?://[^\s)\]]+")),
]

# POSITIVE CONTROL (§2's own instrument check): a scanner that finds nothing must first be shown
# capable of finding something. Every string below MUST match, or the coverage scan is a fake zero.
CONTROL_SPECIMENS = [
    ("author-year", "Brier, G. W. (1950)"),
    ("author-year", "Nosek, B. A., Ebersole, C. R., DeHaven, A. C., & Mellor, D. T. (2018)"),
    ("author-year", "Sasson et al. (2017)"),
    ("author-year", "Killer & Blanchard (2014)"),
    ("doi", "doi:10.1073/pnas.1708274114"),
    ("arxiv", "arXiv:2510.26745"),
    ("url", "https://example.org/paper.pdf"),
]


def self_test():
    """Prove the scanner can fire before trusting it when it does not."""
    rx = dict(PATTERNS)
    failed = [(k, s) for k, s in CONTROL_SPECIMENS if not rx[k].search(s)]
    for k, s in failed:
        print("  ⛔ CONTROL FAILED [%s] did not match: %s" % (k, s))
    return failed


def get(url, timeout=30):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read().decode("utf-8", "replace")


def crossref_doi(doi):
    st, body = get("https://api.crossref.org/works/" + urllib.parse.quote(doi))
    m = json.loads(body)["message"]
    title = (m.get("title") or [None])[0]
    year = None
    for k in ("published-print", "published-online", "issued", "created"):
        dp = (m.get(k) or {}).get("date-parts")
        if dp and dp[0] and dp[0][0]:
            year = dp[0][0]
            break
    cont = m.get("container-title") or []
    vol = m.get("volume")
    page = m.get("page")
    return title, year, (cont[0] if cont else None), vol, page


def arxiv(aid):
    st, body = get("http://export.arxiv.org/api/query?id_list=" + aid)
    t = re.search(r"<entry>.*?<title>(.*?)</title>", body, re.S)
    y = re.search(r"<published>(\d{4})", body)
    return (t.group(1).strip().replace("\n", " ") if t else None), (int(y.group(1)) if y else None)


def verify():
    bad = 0
    print("=" * 78)
    print("  §1 — DECLARED REFERENCES, each resolved to a live source")
    print("=" * 78)
    for key, kind, loc, frag, year, cont_frag in REFS:
        try:
            if kind == "doi":
                t, y, c, vol, page = crossref_doi(loc)
                ok_title = bool(t) and frag.lower() in t.lower()
                ok_year = (y == year)
                ok_cont = (not cont_frag) or (bool(c) and cont_frag.lower() in c.lower())
                ok = ok_title and ok_year and ok_cont
                note = "%s (%s) — %s %s:%s" % (t, y, c, vol, page)
                if not ok_title:
                    note += "  ⚠️ TITLE MISMATCH (paper claims %r)" % frag
                if not ok_year:
                    note += "  ⚠️ YEAR MISMATCH (paper claims %s)" % year
                if not ok_cont:
                    note += "  ⚠️ VENUE MISMATCH (paper claims %r)" % cont_frag
            elif kind == "arxiv":
                t, y = arxiv(loc)
                ok = bool(t) and frag.lower() in t.lower()
                note = "%s (%s)" % (t, y)
            else:
                st, body = get(loc)
                found = frag.lower() in body.lower()
                ok = (st == 200) and found
                note = "HTTP %s, fragment %s" % (st, "found" if found else "NOT FOUND")
        except Exception as e:                                        # noqa: BLE001
            ok, note = False, "ERROR %s: %s" % (type(e).__name__, str(e)[:110])
        bad += 0 if ok else 1
        print("  %s %-42s %s" % ("PASS" if ok else "FAIL", key, note[:170]))
    print("\n  %d of %d declared references resolved with matching title, year and venue."
          % (len(REFS) - bad, len(REFS)))
    return bad


def coverage(paper_path):
    """Flag citation-shaped strings in the draft that the declared list does not cover."""
    text = open(paper_path, encoding="utf-8").read()

    # A bibliography entry is one line carrying a declared locator. Any citation-shaped string
    # sitting INSIDE such a line is that entry's own author/year/doi and is covered by it.
    # Positional, not lexical: it cannot be fooled by an author name that happens to recur.
    ref_spans, pos = [], 0
    for line in text.splitlines(keepends=True):
        if any(r[2].lower() in line.lower() for r in REFS):
            ref_spans.append((pos, pos + len(line)))
        pos += len(line)

    def in_ref_line(i):
        return any(a <= i < b for a, b in ref_spans)

    hits, total, by_kind = [], 0, {}
    for kind, rx in PATTERNS:
        for m in rx.finditer(text):
            s = m.group(0).strip()
            total += 1
            by_kind[kind] = by_kind.get(kind, 0) + 1
            if COVERAGE_ALLOW.search(s) or in_ref_line(m.start()):
                continue
            hits.append((kind, s))
    print("\n" + "=" * 78)
    print("  §2 — COVERAGE SCAN of %s (what the list above does NOT cover)" % os.path.basename(paper_path))
    print("=" * 78)
    seen = set()
    uniq = [h for h in hits if not (h[1] in seen or seen.add(h[1]))]
    if not uniq:
        print("  none — every citation-shaped string in the draft is a declared reference,")
        print("  an internal artefact, or an author identifier.")
    else:
        for kind, s in uniq:
            print("  UNCOVERED [%-11s] %s" % (kind, s[:130]))
    print("\n  scanned %d chars · %d citation-shaped strings found (%s) · %d uncovered"
          % (len(text), total,
             ", ".join("%s %d" % kv for kv in sorted(by_kind.items())) or "none",
             len(uniq)))
    if total == 0:
        print("  ⛔ ZERO MATCHES OF ANY KIND — that is a broken scanner, not a clean paper.")
    return len(uniq), total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--paper", default=os.path.join(ROOT, "PAPER_DRAFT_v1.md"))
    ap.add_argument("--offline", action="store_true")
    a = ap.parse_args()
    ctl = self_test()
    print("  §0 — scanner positive control: %d/%d specimens matched%s"
          % (len(CONTROL_SPECIMENS) - len(ctl), len(CONTROL_SPECIMENS),
             "" if not ctl else "  ⛔ SCAN RESULTS BELOW ARE NOT TRUSTWORTHY"))
    bad = 0 if a.offline else verify()
    if a.offline:
        print("  [--offline: declared references NOT checked against any source this run]")
    unc, total = coverage(a.paper)
    ok = (bad == 0 and unc == 0 and not ctl and total > 0)
    print("\n  VERDICT: %s" % ("clean" if ok else
                               "%d unresolved reference(s), %d uncovered citation(s), "
                               "%d control failure(s), %d strings scanned"
                               % (bad, unc, len(ctl), total)))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
