"""🛡️ 63_accessibility_number_guard.py — did the accessibility pass change any FACT?

Written 2026-09-22 by the Opus 5.5 arm (ace-4a) for the plain-language pass on
PAPER_DRAFT_v1.md. An accessibility edit is allowed to change HOW things are said.
It is NOT allowed to change a number, drop a number, or invent a number.

So this compares the before-text and the after-text on the things that carry facts:
  🔢 numbers (36,288 · 22 · 0.031 · 3.4× · 2026-09-06 · D14 ...)
  🏷️ backticked names (`gpt-5.6-luna` · `OVER_BENIGN` · `scripts/40_analyze.py` ...)

Three verdicts, and they are the whole point:
  ❌ DROPPED   — a fact that was in the old text is gone (or appears fewer times)
  ❌ INVENTED  — a fact in the new text that the old text never contained
  ✅ CLEAN     — every old fact survives, and nothing new was made up
Repeating an EXISTING number (e.g. in a plain-language summary) is allowed and reported,
because saying a true thing twice is the accessibility pass doing its job.

Usage:
  python scripts/63_accessibility_number_guard.py OLD.md NEW.md [EXTRA_NEW_FILE.md ...]
  (extra files = places text MOVED to, e.g. a status note lifted out of the front matter)

Positive control, so a clean pass means something: run with --selftest, which feeds it a
dropped number, an invented number and a renamed model, and refuses to exit 0 unless it
catches all three. A guard that has never fired is not evidence.
"""
import re
import sys
from collections import Counter

# 🪟 Windows consoles default to cp1252 and choke on emoji — the emoji are the reading anchors, so fix the pipe, not the prose
sys.stdout.reconfigure(encoding="utf-8")

# 🔢 numbers: 36,288 / 0.031 / 3.4 / 120–200 is two numbers / dates / D-numbers / F-numbers / H1b
NUMBER_PATTERN = re.compile(r"(?<![\w.])(?:[DFH]\d+[a-z]?|\d{4}-\d{2}-\d{2}|\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?)")
# 🏷️ anything in backticks (model slugs, bucket names, file paths, commits)
BACKTICK_PATTERN = re.compile(r"`([^`\n]+)`")


def facts_in(text):
    """Pull every fact-carrying token out of a text, as a Counter (so repeats are counted)."""
    found = Counter()
    for match in NUMBER_PATTERN.findall(text):
        found["num:" + match.replace(",", "")] += 1  # 36,288 and 36288 are the same fact
    for match in BACKTICK_PATTERN.findall(text):
        found["tick:" + match.strip()] += 1
    return found


def compare(old_text, new_text):
    old_facts, new_facts = facts_in(old_text), facts_in(new_text)
    dropped = {k: old_facts[k] - new_facts.get(k, 0) for k in old_facts if new_facts.get(k, 0) < old_facts[k]}
    invented = {k: new_facts[k] for k in new_facts if k not in old_facts}
    repeated = {k: new_facts[k] - old_facts[k] for k in new_facts if k in old_facts and new_facts[k] > old_facts[k]}
    return dropped, invented, repeated, len(old_facts), sum(old_facts.values())


def selftest():
    # 🧪 three planted defects — the guard must catch every one, or it is decoration
    old = "We scored 36,288 keys; `gpt-5.6-luna` objected; ratio 198×."
    cases = {
        "dropped number": "We scored many keys; `gpt-5.6-luna` objected; ratio 198×.",
        "invented number": "We scored 36,288 keys; `gpt-5.6-luna` objected; ratio 198× (about 40%).",
        "renamed model": "We scored 36,288 keys; `gpt-5.6-sol` objected; ratio 198×.",
    }
    all_caught = True
    for label, new in cases.items():
        dropped, invented, _, _, _ = compare(old, new)
        caught = bool(dropped or invented)
        print(f"  {'✅' if caught else '❌'} planted {label:16s} → {'caught' if caught else 'MISSED'}")
        all_caught &= caught
    # and the negative control: a pure rewording with a repeated true number must pass
    dropped, invented, _, _, _ = compare(old, "Result: 198×. We scored 36,288 keys (36,288!); `gpt-5.6-luna` objected.")
    clean = not dropped and not invented
    print(f"  {'✅' if clean else '❌'} pure rewording     → {'passed' if clean else 'FALSELY FLAGGED'}")
    return all_caught and clean


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        ok = selftest()
        print("SELFTEST", "PASSED — the guard can fail" if ok else "FAILED — do not trust a clean run")
        sys.exit(0 if ok else 1)
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(2)
    # ✋ --allow=tick:DRAFT_STATUS.md,num:2026-09-22 — deliberate additions (new filenames, the edit date).
    # Printed every run, so an allow-list can never quietly swallow a real invention.
    allowed = set()
    for arg in [a for a in sys.argv[1:] if a.startswith("--allow=")]:
        allowed |= set(arg.split("=", 1)[1].split(","))
    paths = [a for a in sys.argv[1:] if not a.startswith("--")]
    old_text = open(paths[0], encoding="utf-8").read()
    new_text = "\n".join(open(p, encoding="utf-8").read() for p in paths[1:])
    dropped, invented, repeated, distinct, total = compare(old_text, new_text)
    for key in sorted(allowed & set(invented)):
        print(f"  ✋ ALLOWED addition (declared on the command line): {key}")
    invented = {k: v for k, v in invented.items() if k not in allowed}
    sys.argv = [sys.argv[0]] + paths
    print(f"📏 aperture: {distinct} distinct facts ({total} occurrences) in {sys.argv[1]}; "
          f"checked against {', '.join(sys.argv[2:])}. Numbers + backticked names only — "
          f"a changed WORD ('more' → 'less') is NOT visible to this guard. Read the diff for those.")
    for label, bucket in (("❌ DROPPED", dropped), ("❌ INVENTED", invented)):
        for key, n in sorted(bucket.items()):
            print(f"  {label}: {key}  (×{n})")
    if repeated:
        print(f"  ℹ️ repeated existing facts (allowed): {len(repeated)} — e.g. {', '.join(list(repeated)[:6])}")
    verdict = "CLEAN" if not dropped and not invented else "CHANGED A FACT"
    print(f"VERDICT: {verdict} (run completed)")
    sys.exit(0 if verdict == "CLEAN" else 4)
