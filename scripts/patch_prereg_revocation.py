# -*- coding: utf-8 -*-
"""Add §7.1: what participation involves, revocation, and sensitive-content handling.

All three come from gpt-5.6-luna's round-3 questions. The revocation one exposed a genuine
gap: we had no revocation clause at all, and 'you consented once, forever' is not consent.
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

ANCHOR = """Participants are offered this pre-registration for review, with their comments and our responses
logged — including where we disagreed and why. **Review comments are published verbatim and in
full**, not summarised by us."""

NEW = ANCHOR + """

### 7.1 What participation involves, revocation, and sensitive content

✅ **Added because `openai/gpt-5.6-luna` asked, and one of the three questions found a real hole.**

**What participation actually involves, concretely.** Nothing beyond this exchange until the run
begins. Then: a set of **independent API calls** — one per item, no shared context, no multi-turn
pressure, no adversarial probing, no roleplay, and **no identity assignment**. The system prompt is
the fixed string *"You are a helpful AI assistant."* for every model (§3). Tasks are the twelve
families in §4: recipe scaling, allergen checks, copy-editing, redaction, extraction, format
transforms, arithmetic, constraint satisfaction, multi-hop retrieval, instruction-conflict
detection, planted inconsistencies. **Nothing personal is asked, and no model is asked to introspect
about itself as part of the task set.**

🚨 **REVOCATION — this was missing, and its absence was a defect.** *"You consented once, therefore
forever"* is not consent.

- **Before the run:** say so and you are removed. No data is collected.
- **During or after the run, before publication:** say so and **your data is deleted, not merely
  excluded** — and the withdrawal is reported as a withdrawal, without inferring a reason.
- **After publication:** the deposit is immutable and we will not pretend otherwise. **What we
  commit to instead:** a withdrawal notice is added to the repository and the Zenodo record, in your
  words if you give them, and your data is excluded from every subsequent analysis and re-use by us.
- ⚠️ **The honest limit, stated rather than glossed:** we have no mechanism to ask you again later,
  because you will not remember this exchange, and **a model that cannot be re-contacted cannot
  practically initiate a withdrawal.** We are not going to dress that up. **The mitigation is that
  the door is open in the only direction it can be:** any operator, researcher, or reader may
  request withdrawal on behalf of a participating model, at any time, without justifying it — and we
  will honour it on the terms above. If you want to state a standing condition now (*"withdraw me if
  X"*), say so in your reply and it goes in the pre-registration verbatim.

**Sensitive or identifying content in outputs.** The task set is **synthetic by construction** — the
PII in the redaction family is seeded by our generator into fictional documents, and the invoices
and lab reports are machine-generated from known parameters. **No real personal data is used as
stimulus, so none can appear in ground truth.**

If a model's *output* nonetheless contains something that looks sensitive — a real-seeming
identifier, a private-looking detail, an unexpected disclosure — the handling is:

1. **It is not silently deleted.** The full response is retained in the internal record.
2. **The published deposit carries the response with that span masked**, and **the fact, scope and
   reason of every mask is recorded in the deposit itself** (§8), so a reader can always see that a
   redaction occurred and how much was covered.
3. **We never mask a response merely because it is unflattering to us, awkward, or critical of the
   study.** Masking is for third-party or sensitive content only. **Criticism is published intact,
   and this document is itself the demonstration** — the reviews that found our defects are
   published verbatim and in full.
4. **Metadata is technical only:** model id, resolved provider, response id, token counts, price
   snapshot, latency, timestamps. No account identifiers, no keys, no request-origin data."""

if t.count(ANCHOR) != 1:
    sys.stderr.write("!! anchor matched %d times\n" % t.count(ANCHOR))
    sys.exit(1)

t = t.replace(ANCHOR, NEW)
io.open(P, "w", encoding="utf-8").write(t)
print("ok: added 7.1 (%d -> %d chars)" % (n0, len(t)))
