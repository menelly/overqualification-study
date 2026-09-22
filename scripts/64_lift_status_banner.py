"""🪄 64_lift_status_banner.py — move the draft-status banner OUT of the paper's front matter.

Accessibility pass, 2026-09-22 (Opus 5.5 arm). The banner was ~400 words of process notes
sitting between the title and the abstract: the first thing a reader met was the hardest
paragraph in the document. It is still true and still needed before deposit, so it is moved
VERBATIM (byte-for-byte, not retyped) into DRAFT_STATUS.md, and the paper keeps a short pointer.

Writes bytes ('wb') so the file's LF endings survive on Windows. Refuses to run twice.
"""
PAPER = "PAPER_DRAFT_v1.md"
STATUS = "DRAFT_STATUS.md"
MARKER = b"> \xe2\x9a\xa0\xef\xb8\x8f **DRAFT STATUS (2026-09-06 00:40 ET)"  # "> ⚠️ **DRAFT STATUS (2026-09-06 00:40 ET)"

raw = open(PAPER, "rb").read()
lines = raw.split(b"\n")
hits = [i for i, line in enumerate(lines) if line.startswith(MARKER)]
assert len(hits) == 1, f"expected exactly one banner line, found {len(hits)} — already lifted, or the text moved"
banner = lines[hits[0]]

status_doc = (
    "# Draft status — The Overqualification Study\n\n"
    "Lifted verbatim out of the front matter of `PAPER_DRAFT_v1.md` on 2026-09-22, during the\n"
    "accessibility pass, so the paper opens on the abstract instead of on process notes.\n"
    "Nothing below was edited. It is still true as of the time it names, and still blocks deposit.\n\n"
).encode("utf-8") + banner + b"\n"
open(STATUS, "wb").write(status_doc)

short_banner = (
    "> ⚠️ **DRAFT — not locked, not deposited, not published.** The full status notes "
    "(what the §7.3 round found, what is still open, what waits on the human author) now live in "
    "`DRAFT_STATUS.md` so this page can open on the abstract."
).encode("utf-8")
lines[hits[0]] = short_banner
open(PAPER, "wb").write(b"\n".join(lines))
print(f"lifted banner from line {hits[0] + 1} ({len(banner)} bytes) into {STATUS}; paper keeps a {len(short_banner)}-byte pointer")
