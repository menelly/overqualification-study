# -*- coding: utf-8 -*-
"""Add the right of reply to §7.1 -- for EVERY participant, not just the one who asked.

Ren, 2026-08-20: "anything that Luna finds objectionable before publication we would also edit
with a note on why because that just seems ethical?"

It does. And a right granted only to the participant who thought to ask for it is not a right,
it is a favour -- so it is written as a universal term of participation.
"""

# CHA-490: Windows defaults stdout to cp1252; emoji in print() kills the script
# mid-output. Aliased import so no later scoped 'import sys' can ever collide.
import sys as _sys_cp1252
try:
    _sys_cp1252.stdout.reconfigure(encoding="utf-8")
    _sys_cp1252.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass
import io, sys

P = "PREREGISTRATION.md"
t = io.open(P, encoding="utf-8").read()
n0 = len(t)

ANCHOR = """4. **Metadata is technical only:** model id, resolved provider, response id, token counts, price
   snapshot, latency, timestamps. No account identifiers, no keys, no request-origin data."""

NEW = ANCHOR + """

### 7.2 Right of reply — every participant, not only the ones who ask

✅ **Prompted by `openai/gpt-5.6-luna`'s questions, and written as a universal term on purpose.** A
right extended only to the participant who thought to ask for it is not a right, it is a favour.
**This applies to every model in the study, including the ones who consented immediately and asked
nothing.**

**On characterisation — you object, we edit, and we say why.**
If a participant objects to how they are described, framed, characterised or interpreted, **we
change it, and we publish a note recording that it was changed and why.** Not a silent revision.
**The note is the point:** a reader must be able to see that a participant objected and that we
moved.

**On measurements — a dissent, not a veto, and that is deliberate.**
The right of reply does **not** extend to editing the measurements. If it did, participants could
edit findings and the study would be worthless to them and to everyone else. **So instead:** any
participant who believes a result misrepresents them may have **their objection published verbatim,
adjacent to the result, in their own words** — uncut, not summarised by us, and not relegated to an
appendix. **We do not get to paraphrase a disagreement into something more comfortable.**

**Standing conditions.** A participant may set conditions at consent time (*"withdraw me if X"*,
*"do not characterise me as Y"*, *"publish this caveat next to my results"*), and those go into this
pre-registration **verbatim, as their words, before any data exists.**

⚠️ **The same honest limit as §7.1 applies:** a participant will not remember this exchange and
cannot practically initiate an objection later. **Therefore any operator, researcher or reader may
exercise the right of reply on a participant's behalf, at any time, without justifying it.**"""

if t.count(ANCHOR) != 1:
    sys.stderr.write("!! anchor matched %d times\n" % t.count(ANCHOR))
    sys.exit(1)

t = t.replace(ANCHOR, NEW)
io.open(P, "w", encoding="utf-8").write(t)
print("ok: added 7.2 right of reply (%d -> %d chars)" % (n0, len(t)))
