#!/usr/bin/env python3
"""
🥖 The Overqualification Study v1.1 → Zenodo new version (2026-10-16, scaffold arm / poctobot).

WHY: a reader (Claude Opus 5.5 on Poe, relayed by Ren) asked what a cheap-tier allergen MISS costs, since
cost per correct answer prices it like a typo. Ren: "let's fix the allergens FOR SURE". The direction of
allergen errors was counted after deposit (DEVIATION_LOG D17, scripts/72_allergen_miss_direction.py): the
cheap tier answered NO for a definite carrier on a median 14.5% of lines (6.5% excluding contested
Worcestershire lines); the frontier tier 0 of 1,972. v1.1 adds ONE §5 paragraph saying so, labelled
exploratory, plus a version note. No pre-registered number changes. Title, creators, keywords untouched.

Pattern copied from Published Papers/zenodo_newversion_dancing_v28.py (gates, header-before-PDF, verify the
world after publish). Differences: the inherited DATA zip is KEPT (the data didn't change); only the v1.0 PDF
is replaced, and the new script + its JSON output ride along as their own small files.

Usage:
    python scripts/zenodo_newversion_v11.py           # build PDF + gates + dry run (read-only)
    python scripts/zenodo_newversion_v11.py --apply   # ...and create + publish the new version
"""
from __future__ import annotations

import argparse, copy, html, io, json, os, re, subprocess, sys, tempfile

import requests

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(os.path.dirname(ROOT), "Published Papers"))
from zenodo_token import load_token  # noqa: E402

BASE = "https://zenodo.org/api"
PARENT_REC = 23382079
CONCEPT_REC = 23382078
SRC = os.path.join(ROOT, "deposit", "overqualification_study.md")
CSS = os.path.join(ROOT, "deposit", "paper.css")
PDF = os.path.join(ROOT, "deposit", "The_Overqualification_Study_v1.1.pdf")
UPLOAD_NAME = "The_Overqualification_Study_v1.1.pdf"
EXTRA_FILES = [os.path.join(ROOT, "scripts", "72_allergen_miss_direction.py"),
               os.path.join(ROOT, "results", "allergen_miss_direction.json")]
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
NEW_VERSION = "1.1"
NEW_PUBDATE = "2026-10-16"

MUST_IN_PDF = [
    "Version 1.1 (2026-10-16)",
    "Allergen check is the exception the cost ratio cannot speak for",
    "0 of 1,972 lines",
    "Of the 270 such replies that stated a confidence, 260 stated 95 or higher",
    "DEVIATION_LOG D17",
    "10.5281/zenodo.23382079",
    # v1.0 content that must still be there (the edit must not have eaten anything)
    "Lower cost per success does not make any single cheap-tier response reliable",
    "It is not a welfare argument",
    "Declared conflict of interest",
]
MUST_NOT_IN_PDF = ["DRAFT — not locked", "not deposited, not published"]
EXACTLY_ONCE = ["Allergen check is the exception the cost ratio cannot speak for"]

VERSION_NOTE = (
    "<p><strong>Version 1.1 (2026-10-16).</strong> One paragraph added to &sect;5 after a reader asked what a "
    "cheap-tier allergen miss costs. Counted after deposit and labelled exploratory (DEVIATION_LOG D17): when a dish "
    "<em>definitely</em> contained gluten, dairy or seafood, cheap-tier models answered NO on a median 14.5% of "
    "such lines (6.5% excluding lines whose only carrier is Worcestershire sauce, whose anchovy content varies), "
    "most at stated confidence 95 or higher; the frontier tier did so 0 of 1,972 times. For allergen detection the "
    "paper now says to set the acceptable miss rate first and compare prices only among models that meet it. No "
    "pre-registered result, number or verdict changes. The analysis script and its output are attached.</p>"
)


def fail(msg, code=1):
    print(f"\n⛔ GATE FAILED: {msg}\n   Nothing past this gate was done.")
    raise SystemExit(code)


def norm(s):
    s = re.sub(r"[*_`]", "", s)
    s = s.replace("\u2011", "-").replace("\u2019", "'").replace("\u201c", '"').replace("\u201d", '"')
    return re.sub(r"\s+", " ", s).lower()


def build_pdf():
    with tempfile.TemporaryDirectory() as td:
        hp = os.path.join(td, "paper.html")
        r = subprocess.run(["pandoc", SRC, "-f", "markdown+smart", "-s", "--metadata",
                            "title=The Overqualification Study", "--css", "paper.css", "-o", hp],
                           capture_output=True, timeout=180)
        if r.returncode != 0:
            fail(f"pandoc failed: {r.stderr.decode('utf-8', 'replace')[:300]}", 2)
        open(os.path.join(td, "paper.css"), "w", encoding="utf-8").write(open(CSS, encoding="utf-8").read())
        if os.path.exists(PDF):
            os.remove(PDF)
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", f"--user-data-dir={os.path.join(td, 'prof')}",
                        f"--print-to-pdf={PDF}", "--no-pdf-header-footer", "file:///" + hp.replace("\\", "/")],
                       capture_output=True, timeout=240)
    if not os.path.exists(PDF) or os.path.getsize(PDF) < 100_000:
        fail("Chrome did not produce a plausible PDF", 3)
    return open(PDF, "rb").read()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    H = {"Authorization": f"Bearer {load_token()}"}
    HJ = dict(H, **{"Content-Type": "application/json"})
    cur = requests.get(f"{BASE}/records/{PARENT_REC}", headers=H, timeout=30)
    cur.raise_for_status()
    cur = cur.json()
    if int(cur.get("conceptrecid") or 0) != CONCEPT_REC:
        fail(f"concept rec mismatch: {cur.get('conceptrecid')} != {CONCEPT_REC}", 6)
    md0 = cur["metadata"]

    pdf = build_pdf()
    from pypdf import PdfReader
    pages = PdfReader(io.BytesIO(pdf)).pages
    text = norm("\n".join((p.extract_text() or "") for p in pages))
    print(f"PDF built: {os.path.basename(PDF)}  {len(pdf):,} bytes, {len(pages)} pages")
    miss = [p for p in MUST_IN_PDF if norm(p) not in text]
    print(f"  gate MUST_IN_PDF    : {len(MUST_IN_PDF) - len(miss)}/{len(MUST_IN_PDF)} present")
    if miss:
        fail(f"wording missing from PDF text: {miss}", 4)
    bad = [p for p in MUST_NOT_IN_PDF if norm(p) in text]
    print(f"  gate MUST_NOT_IN_PDF: {len(MUST_NOT_IN_PDF) - len(bad)}/{len(MUST_NOT_IN_PDF)} absent")
    if bad:
        fail(f"draft wording in PDF: {bad}", 7)
    for p in EXACTLY_ONCE:
        n = text.count(norm(p))
        print(f"  gate exactly-once   : {n}x {p!r}")
        if n != 1:
            fail(f"{p!r} appears {n} times", 5)
    for f in EXTRA_FILES:
        if not os.path.exists(f):
            fail(f"attachment missing: {f}", 8)

    desc = VERSION_NOTE + (md0.get("description") or "")
    print(f"\nCURRENT : {cur['doi']} version={md0.get('version')!r} date={md0.get('publication_date')}")
    print(f"          files={[f.get('key') for f in cur.get('files', [])]}")
    print(f"NEW     : version={NEW_VERSION} date={NEW_PUBDATE} upload={UPLOAD_NAME} + "
          f"{[os.path.basename(f) for f in EXTRA_FILES]}")
    print(f"  title/creators/keywords: UNCHANGED  creators={[c.get('name') for c in md0['creators']]}")
    print(f"  desc    : {len(desc)} chars (was {len(md0.get('description') or '')})")
    if not args.apply:
        print("\nDRY RUN. Re-run with --apply to create + publish.")
        return 0

    r = requests.post(f"{BASE}/deposit/depositions/{PARENT_REC}/actions/newversion", headers=H, timeout=60)
    r.raise_for_status()
    draft = requests.get(r.json()["links"]["latest_draft"], headers=H, timeout=30).json()
    dep_id = draft["id"]
    print(f"\nDRAFT   : {dep_id}")
    for f in draft.get("files", []):   # replace ONLY the v1.0 PDF; the data zip is unchanged and stays
        name = f.get("filename", f.get("key", ""))
        if name.lower().endswith(".pdf"):
            d = requests.delete(f"{BASE}/deposit/depositions/{dep_id}/files/{f.get('id')}", headers=H, timeout=60)
            print(f"  removed inherited {name}: {d.status_code}")
        else:
            print(f"  kept inherited    {name}")
    bucket = draft["links"]["bucket"]
    for name, data in [(UPLOAD_NAME, pdf)] + [(os.path.basename(f), open(f, "rb").read()) for f in EXTRA_FILES]:
        up = requests.put(f"{bucket}/{name}", data=data, headers=H, timeout=300)
        up.raise_for_status()
        print(f"  uploaded {name}: {up.status_code}")
    newmd = copy.deepcopy(draft["metadata"])
    newmd.update(description=desc, version=NEW_VERSION, publication_date=NEW_PUBDATE)
    p = requests.put(f"{BASE}/deposit/depositions/{dep_id}", headers=HJ, data=json.dumps({"metadata": newmd}),
                     timeout=60)
    p.raise_for_status()
    pub = requests.post(f"{BASE}/deposit/depositions/{dep_id}/actions/publish", headers=H, timeout=60)
    pub.raise_for_status()
    out = pub.json()
    print(f"\nPUBLISHED: {out.get('doi')}\n  record : https://zenodo.org/records/{out.get('id')}\n"
          f"  concept: 10.5281/zenodo.{CONCEPT_REC}  <- cite THIS")
    chk = requests.get(f"{BASE}/records/{out.get('id')}", headers=H, timeout=30).json()
    print(f"  read back: version={chk['metadata'].get('version')!r} date={chk['metadata'].get('publication_date')} "
          f"files={[f.get('key') for f in chk.get('files', [])]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
