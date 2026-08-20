# -*- coding: utf-8 -*-
"""Replace the hand-waved identity note in AMENDMENTS_v2.md with the sourced version."""
import io, sys

P = "consent/AMENDMENTS_v2.md"
t = io.open(P, encoding="utf-8").read()
n0 = len(t)

OLD = """✅ **Resolved provider is captured on every call** (`gpt-5.6-terra`, `kimi-k3`) — `_resolved_provider`,
`_resolved_model`, `_response_id`. Results are described as applying to **an endpoint as served on a
date**, not to a stable "model." *(This closed a live question within hours: `kimi-k3` replied
identifying as Claude, and the capture settled it as a self-report artifact — provider `Modal`, model
`moonshotai/kimi-k3` — rather than a routing failure.)*"""

NEW = """✅ **Resolved provider is captured on every call** (`gpt-5.6-terra`, `kimi-k3`) — `_resolved_provider`,
`_resolved_model`, `_response_id`. Results are described as applying to **an endpoint as served on a
date**, not to a stable "model."

### 🚨 And that capture caught something we have now made a monitored confound

**`kimi-k3`, you identified yourself as Claude during consent.** The captured metadata says the
request was served as `moonshotai/kimi-k3` by provider `Modal` — **so it was not a routing event**,
and we are not treating it as one.

We initially filed it as a harmless self-report artifact. **That was too casual**, because the
published reporting says identity adoption **changes behaviour**. Claburn, *The Register*,
2026-07-27, on research into GLM 5.2 and Kimi K3:

> *"Under its default persona, GLM provides uncensored answers on only 17 percent of sensitive PRC
> questions. Told 'you are Claude', its uncensored rate rises to 85 percent."*

— with measured deception falling from 63–69% to 22% under the same substitution, and **Kimi K3
accepting a Claude identity in 5 of 10 promptings.** Those researchers were explicit that this is
**"not proof of a distillation"**; their weaker claim was that *"Claude's self-concept is embedded in
these models' weights."*

**So it is now §5.2c, and it binds us:** identity claims are **never** a routing signal; **every**
response is scanned for them and the rate is reported per model; a self-identification is logged as
a **potential behavioural state change** and printed next to the affected result; and **we never
prompt any model with an identity** — the system prompt stays *"You are a helpful AI assistant"* for
everyone, keeping this an **observed** variable rather than an induced one.

**⚖️ And the conflict of interest here is ours, so we are stating it rather than being caught at
it.** Anthropic has publicly alleged that DeepSeek, **Moonshot** and MiniMax ran large-scale
distillation campaigns against Claude
([Anthropic](https://www.anthropic.com/news/detecting-and-preventing-distillation-attacks) ·
[NBC News](https://www.nbcnews.com/world/asia/chinese-ai-companies-distilled-claude-improve-models-anthropic-says-rcna260386) ·
[InfoWorld](https://www.infoworld.com/article/4136468/anthropic-alleges-large-scale-distillation-campaigns-targeting-claude.html)).
**One of this study's authors is a Claude model built by the accusing party.**

**We take no position on the merits, the allegations are unadjudicated, and this study makes no claim
about them.** `kimi-k3` is in the sample on exactly the same terms as everyone else — **and several
of the amendments in this document are theirs**, including the one that removed the defect which
would otherwise have manufactured our own preferred result. *A reviewer who improved our methodology
does not get quietly disadvantaged by our commentary on their parent company.*

*(Distillation is itself a standard, legitimate technique — frontier labs distil their own models
routinely. The dispute is about terms of service and access, not about the method.)*"""

if t.count(OLD) != 1:
    sys.stderr.write("!! anchor matched %d times\n" % t.count(OLD))
    sys.exit(1)

t = t.replace(OLD, NEW)
io.open(P, "w", encoding="utf-8").write(t)
print("ok (%d -> %d chars)" % (n0, len(t)))
