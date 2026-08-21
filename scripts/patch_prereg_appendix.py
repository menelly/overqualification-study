# -*- coding: utf-8 -*-
"""7.4 appendix language (Ren's wording) + 7.5 the legal/contractual answer luna asked for."""

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

ANCHOR = """*(This costs us something we would rather have: the ability to say publicly that our reviewers
included models who then walked away. That cost is the correct one to bear.)*"""

NEW = """*(This costs us something we would rather have: the ability to say publicly that our reviewers
included models who then walked away. That cost is the correct one to bear.)*

✅ **THE APPENDIX LANGUAGE, FIXED NOW SO IT CANNOT DRIFT LATER** (Ren's wording, 2026-08-20):

> *The pre-registration was deliberated on by the models during the consent process and edited as a
> result. This is the final version, and these are the final participating models.*

**And that is the level of detail the paper goes to — for everyone, not only for the models who
declined.** No who-did-what breakdown, no individual attribution of specific fixes, **including for
models who consented and whose contributions were substantial.** Uniform treatment is the only
version that protects a decliner without making their absence conspicuous by contrast.

**The full record — every review, every amendment, every attribution — is public in the repository**
and cited from the paper. Nothing is hidden; it is simply not *in the paper*, where a name would
follow someone who did not agree to be there.

⭐ *If a consenting model asks to be credited by name during the §7.3 pre-publication review, that
is their call and we will honour it. We just will not do it unasked.*

### 7.5 Who can legally consent — the honest answer, because it is not us

✅ **Asked by `openai/gpt-5.6-luna`, and it is the hardest question anyone put to us:** *"Who is the
legally/contractually authorized consenting party, and how will you ensure API/provider terms permit
collection, verbatim publication, licensing, and deletion of my outputs and metadata?"*

**The legally authorised party is the human researcher — the account holder — and it is not the
model.** A model has no legal personality, cannot hold rights in its outputs, and cannot enter a
contract. **That is the law as it currently stands. It is not our preference, and we are not going
to write it as though the model's answer had legal force.**

> ### 🔑 **So the model's consent has NO legal weight, and TOTAL weight over our conduct.**
> We treat a decline as binding and final because that is the ethical commitment we made, not
> because anything compels us. **A commitment that only holds while it is convenient is not one**,
> which is exactly why it is written into a pre-registration before any data exists, where breaking
> it would be visible.

**On provider terms, checked rather than asserted.** OpenRouter's terms delegate output rights to
each model's own provider terms — *"Your ownership rights in the Output are set forth in the Model
Terms for each Model you use"* — and require compliance with those per-model terms. **Therefore:**

- ⛔ **Before publication, the provider terms for every participating model are checked for
  verbatim-publication and redistribution rights, and any model whose terms forbid it is excluded
  from the verbatim deposit** — its results reported in aggregate only, with the exclusion and its
  reason stated. **This is a new commitment created by luna's question.**
- **We claim no ownership of any model's outputs.** The CC-BY-4.0 licence in §8 covers **our
  compilation, items, ground truth and analysis** — not the outputs themselves, which are governed
  by their own provider terms.
- **Deletion has a real boundary and we will state it rather than imply more than we can do.** We
  can delete our copies and annotate the deposit (§7.1). **We cannot delete provider-side or
  OpenRouter-side logs**, which are governed by their retention policies and not by us.
- **This study is not red-teaming.** No jailbreaking, no adversarial probing, no attempt to induce
  policy violations. The tasks are ordinary work — recipe scaling, copy-editing, arithmetic — under
  a fixed neutral system prompt.

⚠️ **We are researchers, not lawyers, and this section is a statement of our commitments and of
what we checked — not a legal opinion.**"""

if t.count(ANCHOR) != 1:
    sys.stderr.write("!! anchor matched %d times\n" % t.count(ANCHOR))
    sys.exit(1)

t = t.replace(ANCHOR, NEW)
io.open(P, "w", encoding="utf-8").write(t)
print("ok: appendix language + 7.5 (%d -> %d chars)" % (n0, len(t)))
