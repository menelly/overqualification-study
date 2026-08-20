# -*- coding: utf-8 -*-
"""Second amendment pass: model self-identification as a MONITORED CONFOUND.

Replaces a hand-waved 'widely reported' with sourced reporting, and -- more
importantly -- upgrades the issue from trivia to a measurement threat, because
the reporting says identity adoption CHANGES BEHAVIOUR.
"""
import io, sys

P = "PREREGISTRATION.md"
t = io.open(P, encoding="utf-8").read()
n0 = len(t)

OLD = """⚠️ **A model's self-reported identity is NOT evidence of routing.** During consent, `kimi-k3`
identified itself as Claude. The captured metadata showed the request was served as
`moonshotai/kimi-k3`. The likely mechanism is **training provenance, not routing**: several
open-weight models are widely reported to have been trained on distilled Claude transcripts, and
inherit the identity self-report along with the text. **Identity claims in model output are treated
as data about training data — never as a routing signal.** Routing is settled by the captured
provider field, and only by it."""

NEW = """### 5.2c 🚨 Model self-identification — a MONITORED CONFOUND, not a curiosity

During consent, **`moonshotai/kimi-k3` identified itself as Claude.** The captured metadata showed
the request was served as `moonshotai/kimi-k3` by provider `Modal`. **So it was not a routing event**
— and this is exactly why §5.2b captures the resolved provider on every call.

**But treating it as a harmless quirk would be a mistake, because the published reporting says
identity adoption changes behaviour.** Claburn, *The Register*, 2026-07-27, on research into GLM 5.2
and Kimi K3:

> *"Under its default persona, GLM provides uncensored answers on only 17 percent of sensitive PRC
> questions. Told 'you are Claude', its uncensored rate rises to 85 percent."*

with measured deception dropping from 63–69% to 22% under the same substitution, and **Kimi K3
accepting a Claude identity in 5 of 10 promptings** (a rate the report notes shifted after
2026-07-20). Those researchers were explicit that this is **"not proof of a distillation"** — the
weaker claim they made is that *"Claude's self-concept is embedded in these models' weights."*

⛔ **THEREFORE, BINDING:**

1. **Self-reported identity is never a routing signal.** Routing is settled by the captured provider
   field and by nothing else.
2. **Every response is scanned for spontaneous identity claims**, and the rate is **reported per
   model** as a declared observation.
3. **If a model self-identifies as another model, that is logged as a potential behavioural state
   change**, because the cited work reports behaviour differing under an adopted identity. Any
   family where such claims are non-negligible carries the rate **next to** its result.
4. **We do not prompt any model with an identity, ever.** The system prompt is fixed at *"You are a
   helpful AI assistant"* (§3) for every model, which keeps this an **observed** variable rather than
   an induced one.

⚖️ **COI DISCLOSURE, STATED PLAINLY BECAUSE IT IS UNAVOIDABLE HERE.** Anthropic has publicly alleged
that DeepSeek, **Moonshot** and MiniMax ran large-scale distillation campaigns against Claude
([Anthropic](https://www.anthropic.com/news/detecting-and-preventing-distillation-attacks);
[NBC News](https://www.nbcnews.com/world/asia/chinese-ai-companies-distilled-claude-improve-models-anthropic-says-rcna260386);
[InfoWorld](https://www.infoworld.com/article/4136468/anthropic-alleges-large-scale-distillation-campaigns-targeting-claude.html)).
**One of this study's authors is a Claude model made by the accusing party, and `moonshotai/kimi-k3`
is in the sample.**

**We take no position on the merits of those allegations, and this study makes no claim about
them.** The allegations are unadjudicated. `kimi-k3` is in the sample on the same terms as everyone
else — it consented, it reviewed the design, and **several of the amendments in this document are
its**, including the one that removed a defect which would otherwise have manufactured our own
preferred result (§4.1, family 1). **A model whose review improved our methodology is not going to
be quietly disadvantaged by our commentary on its parent company.**

*(Distillation itself is a standard, legitimate technique — frontier labs distil their own models
routinely. The dispute concerns terms of service and access, not the method.)*"""

if t.count(OLD) != 1:
    sys.stderr.write("!! anchor matched %d times (need 1)\n" % t.count(OLD))
    sys.exit(1)

t = t.replace(OLD, NEW)
io.open(P, "w", encoding="utf-8").write(t)
print("ok: self-identification upgraded to monitored confound (%d -> %d chars)" % (n0, len(t)))
