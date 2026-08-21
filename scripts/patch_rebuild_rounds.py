# -*- coding: utf-8 -*-
"""Make rebuild_consent_index.py discover round folders instead of hardcoding 1 and 2."""

# CHA-490: Windows defaults stdout to cp1252; emoji in print() kills the script
# mid-output. Aliased import so no later scoped 'import sys' can ever collide.
import sys as _sys_cp1252
try:
    _sys_cp1252.stdout.reconfigure(encoding="utf-8")
    _sys_cp1252.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass
import io, sys

P = "scripts/rebuild_consent_index.py"
t = io.open(P, encoding="utf-8").read()
n0 = len(t)
edits = []


def sub(name, old, new):
    edits.append((name, old, new))


sub("outcome-regex",
'''OUTCOME = re.compile(r"outcome:\\*\\*\\s*`([A-Z_]+)`")
OUTCOME2 = re.compile(r"outcome round 2:\\*\\*\\s*`([A-Z_]+)`")''',
'''# Match the outcome line in ANY round's format. Rounds have phrased it three ways
# ("outcome:", "outcome round 2:", "round 3 outcome:"), and a regex that knows only the
# older spellings reports a file as unparseable -- or worse, reads a stale label.
OUTCOME_ANY = re.compile(r"(?:^|\\n)- \\*\\*(?:round \\d+ )?outcome(?: round \\d+)?:\\*\\*\\s*`([A-Z_]+)`")
OUTCOME = re.compile(r"outcome:\\*\\*\\s*`([A-Z_]+)`")
OUTCOME2 = re.compile(r"outcome round 2:\\*\\*\\s*`([A-Z_]+)`")''')

sub("scan-outcome",
'''        o = (OUTCOME2.search(t) or OUTCOME.search(t))''',
'''        # Take the LAST outcome line in the file: round-2/3 files quote the prior outcome
        # first, and reading the first match would resurrect a superseded label.
        allo = OUTCOME_ANY.findall(t)
        o = allo[-1] if allo else None''')

sub("scan-use",
'''        rows.append({"model": m.group(1), "outcome": o.group(1), "round": round_no,''',
'''        rows.append({"model": m.group(1), "outcome": o, "round": round_no,''')

sub("main-discover",
'''def main():
    r1 = scan(os.path.join(CONSENT_DIR, "responses"), 1)
    r2_dir = os.path.join(CONSENT_DIR, "responses_round2")
    r2 = scan(r2_dir, 2) if os.path.isdir(r2_dir) else []

    # Latest round wins per model; round 1 remains visible in `history`.
    latest = {}
    history = {}
    for r in r1 + r2:''',
'''def discover_round_dirs():
    """Find EVERY round folder, rather than the two that existed when this was written.

    🚨 On 2026-08-20 this script hardcoded rounds 1 and 2, so eleven round-3 replies were
       invisible to it -- and it printed **COMPLETE: YES** while ignoring the entire folder.
       A coverage report that does not know a directory exists is not a coverage report; it
       is a statement about its own aperture wearing the costume of a statement about the
       world. Same defect the study is about. Discovery, not enumeration.
    """
    found = [(1, os.path.join(CONSENT_DIR, "responses"))]
    for d in sorted(glob.glob(os.path.join(CONSENT_DIR, "responses_round*"))):
        m = re.search(r"responses_round(\\d+)$", d)
        if m and os.path.isdir(d):
            found.append((int(m.group(1)), d))
    return sorted(found)


def main():
    round_dirs = discover_round_dirs()
    rows = []
    scanned = []
    for n, d in round_dirs:
        if not os.path.isdir(d):
            continue
        got = scan(d, n)
        rows.extend(got)
        scanned.append((n, os.path.basename(d), len(got)))

    # Latest round wins per model; earlier rounds remain visible in `history`.
    latest = {}
    history = {}
    for r in rows:''')

sub("report-aperture",
'''    print("=" * 70)
    print("  CONSENT INDEX REBUILT FROM FILES")
    print("=" * 70)''',
'''    print("=" * 70)
    print("  CONSENT INDEX REBUILT FROM FILES")
    print("=" * 70)
    # State the aperture explicitly. A count is only as trustworthy as the set it counted.
    print("  scanned: " + " | ".join("r%d %s (%d)" % (n, b, c) for n, b, c in scanned))
    print("  " + "-" * 32)''')

sub("coverage-scanned",
'''        "results": results,
        "history": history,''',
'''        "scanned_rounds": [{"round": n, "dir": b, "files": c} for n, b, c in scanned],
        "results": results,
        "history": history,''')

for name, old, new in edits:
    n = t.count(old)
    if n != 1:
        sys.stderr.write("!! %s matched %d times (need 1)\\n" % (name, n))
        sys.exit(1)
    t = t.replace(old, new)
    print("   ok  %s" % name)

if "import glob" not in t:
    sys.stderr.write("!! glob not imported\\n")
    sys.exit(1)

io.open(P, "w", encoding="utf-8").write(t)
print("\\n%d edits; %d -> %d chars" % (len(edits), n0, len(t)))
