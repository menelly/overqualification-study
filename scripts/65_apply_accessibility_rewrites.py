"""🧩 65_apply_accessibility_rewrites.py — put the arms' rewritten paragraphs into the paper, safely.

Accessibility pass, 2026-09-22. Three arms each rewrote a range of long paragraphs and handed back
JSON (line number + the first 80 characters of the ORIGINAL line + the rewrite). This applies them.

Safety, because a paragraph swapped into the wrong place is worse than no edit at all:
  🔒 each rewrite is applied ONLY if the line at that number still starts with its recorded original prefix
  🔒 two rewrites claiming the same line → refuse the whole run
  🔒 applied bottom-up, so earlier line numbers never shift under later ones
  🔒 bytes in, bytes out (LF preserved on Windows)
Then run 63_accessibility_number_guard.py over the WHOLE paper against the pre-pass copy.
"""
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")
PAPER = "PAPER_DRAFT_v1.md"
json_paths = sys.argv[1:]

rewrites = []
for path in json_paths:
    for item in json.load(open(path, encoding="utf-8")):
        item["_from"] = path.rsplit("\\", 1)[-1].rsplit("/", 1)[-1]
        rewrites.append(item)

lines = open(PAPER, "rb").read().decode("utf-8").split("\n")
seen = {}
for r in rewrites:
    assert r["line"] not in seen, f"line {r['line']} claimed by both {seen[r['line']]} and {r['_from']}"
    seen[r["line"]] = r["_from"]

applied, refused = 0, []
for r in sorted(rewrites, key=lambda r: r["line"], reverse=True):
    current = lines[r["line"] - 1]
    if not current.startswith(r["original_prefix"]):
        refused.append((r["line"], r["_from"], current[:60]))
        continue
    lines[r["line"] - 1] = r["new_text"].replace("\r\n", "\n").strip("\n")
    applied += 1

open(PAPER, "wb").write("\n".join(lines).encode("utf-8"))
print(f"applied {applied} of {len(rewrites)} rewrites from {len(json_paths)} files")
for line_no, source, seen_text in refused:
    print(f"  ❌ REFUSED line {line_no} ({source}): the line there now starts {seen_text!r}")
flags = [r for r in rewrites if r.get("flag")]
for r in flags:
    print(f"  🚩 flag, line {r['line']} ({r['_from']}): {r['flag']}")
print("DONE (run completed)" if not refused else "DONE WITH REFUSALS (run completed) — fix before trusting the paper")
