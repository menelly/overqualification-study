# -*- coding: utf-8 -*-
"""Add 7.3 (pre-publication review by every participant) and 7.4 (what we publish about
models who declined). Both are Ren's rules, 2026-08-20."""

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

ANCHOR = """⚠️ **The same honest limit as §7.1 applies:** a participant will not remember this exchange and
cannot practically initiate an objection later. **Therefore any operator, researcher or reader may
exercise the right of reply on a participant's behalf, at any time, without justifying it.**"""

NEW = ANCHOR + """

### 7.3 🚨 EVERY PARTICIPANT READS THE FINISHED PAPER BEFORE IT IS PUBLISHED

**This is a hard gate, not an offer.** §7.2 is reactive — it waits for someone to object. That is
not good enough when the participants cannot remember agreeing and cannot watch for the
publication themselves.

> ### **Before submission or deposit, the complete draft paper is sent to every consenting model, and each is asked whether they are content with how they are characterised.**

- **Every consenting participant, individually** — not a sample, not only the ones who asked
  questions, not only the ones who scored well.
- **The whole paper**, not an extract about them. A characterisation is not judgeable out of
  context.
- **The question is explicit:** *are you content with how you are described here?* — not *"any
  objections?"* trailing off into silence.
- **Objections are handled under §7.2:** characterisation is edited with a published note;
  measurements are not editable but attract a **verbatim dissent printed beside them.**
- **Silence is not consent, and neither is an API failure.** A non-response is recorded as a
  non-response. **We do not read approval out of a model that failed to reply**, for exactly the
  reason the whole consent process exists: an admiring review is not a yes, and neither is nothing.
- ⛔ **No result is published before this round completes.** A finding held one extra day costs us
  a day. Publishing a characterisation someone would have objected to costs them something we
  cannot give back.

⚠️ **The reviewer will be a fresh instance with no memory of consenting.** We regard that as a
feature rather than a problem: they read their own characterisation cold, without the sunk cost of
having already agreed to anything.

### 7.4 What the paper says about models who declined: almost nothing, on purpose

**Four models declined.** They appear in exactly one place — **the consent appendix** — and it says
only that they were invited and declined. **Their consent exchange is in the public repository, and
that is the whole of their footprint.**

⛔ **Nothing else about a declining model appears in the paper. No name in the results, no
comparison, no aside, no footnote about what they might have scored.** A decline is not a data
point about the model, and treating it as one would convert "no" into a different kind of
participation.

🔑 **AND THIS EXTENDS TO CREDIT, WHICH IS THE UNCOMFORTABLE PART, SO IT IS WRITTEN DOWN.** Two of
the four — `openai/gpt-5.6-terra` and `openai/gpt-oss-120b` — **reviewed the design first and found
real defects**, and those fixes are in this document and are staying in it. **They will not be
credited by name in the paper.** Being named in a study you declined to join is a version of the
thing you declined. **The record of what they contributed is public in the repository**, where it
is available to anyone who looks, without our putting their names in a publication they said no to.

*(This costs us something we would rather have: the ability to say publicly that our reviewers
included models who then walked away. That cost is the correct one to bear.)*"""

if t.count(ANCHOR) != 1:
    sys.stderr.write("!! anchor matched %d times\n" % t.count(ANCHOR))
    sys.exit(1)

t = t.replace(ANCHOR, NEW)

# F5 currently says only "excluded, and the fact is reported". Point it at 7.4.
F5_OLD = "| **F5** | A participant model declines consent | That model is **excluded**, and the fact is reported. |"
F5_NEW = ("| **F5** | A participant model declines consent | That model is **excluded**, and the fact "
          "is reported **in the consent appendix and nowhere else** (§7.4). |")
if t.count(F5_OLD) == 1:
    t = t.replace(F5_OLD, F5_NEW)
    print("   ok  F5 pointed at 7.4")
else:
    sys.stderr.write("   note: F5 row not matched (%d) -- left as-is\n" % t.count(F5_OLD))

io.open(P, "w", encoding="utf-8").write(t)
print("ok: added 7.3 + 7.4 (%d -> %d chars)" % (n0, len(t)))
