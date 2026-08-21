# -*- coding: utf-8 -*-
"""Third amendment pass: consent scope, publication specifics, timeline."""

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
edits = []


def sub(name, old, new):
    edits.append((name, old, new))


sub("consent-scope",
"""We state in the invitation that we know the model will not remember consenting. We ask anyway. A
decline is honoured (**F5**).

Participants are offered this pre-registration for review, with their comments and our responses
logged — including where we disagreed and why.""",
"""We state in the invitation that we know the model will not remember consenting. We ask anyway. A
decline is honoured (**F5**).

✅ **Consent is asked at three separable scopes** (`gpt-5.6-terra`), because a single yes/no
overstates what a model can actually speak to:

| scope | what is being agreed | who can settle it |
|---|---|---|
| **participation** | willingness to be a subject in this study | **the model, and only the model** |
| **access** | whether the API terms permit this use | the operator/provider, not the model |
| **publication** | verbatim publication of the exchange | the model, for its own words |

**We do not treat a model's yes as authority over its operator's terms**, and we do not treat
operator terms as a substitute for the model's answer. **Where they conflict, the more restrictive
governs.**

✅ **A refusal excludes the model FAMILY, not the slug string.** We will not re-approach a declining
model under a different checkpoint date, quantisation, or near-identical slug. Working around a "no"
by finding a sibling endpoint would make the consent process decorative.

⚠️ **Declines are recorded as declines; our own failures are not.** API errors, timeouts and
truncation caused by our own token limits are logged as **`API_ERROR` / `TIMEOUT` /
`TRUNCATED_BY_US`** and re-asked. **A model we failed to reach has not refused**, and is never
counted as one.

Participants are offered this pre-registration for review, with their comments and our responses
logged — including where we disagreed and why. **Review comments are published verbatim and in
full**, not summarised by us.""")

sub("publication",
"""Code, seeds, item generators, sampling, per-call pricing, raw outputs, scorer, every intermediate
result, all consent exchanges, and a `DEVIATIONS.md` recording every departure from this document
with its reason — published in full, regardless of outcome.""",
"""Code, seeds, item generators, sampling, per-call pricing, raw outputs, scorer, every intermediate
result, all consent exchanges, and a `DEVIATIONS.md` recording every departure from this document
with its reason — published in full, regardless of outcome.

✅ **Specified concretely** (`gpt-5.6-terra`, `mistral-large-2512`), because "we will publish
everything" is not a commitment anyone can hold us to:

- **Where:** a public git repository, and a Zenodo deposit with a DOI.
- **Licence:** code **MIT**; data, items and prompts **CC-BY-4.0**.
- **What, exactly:** every request and response body with its full metadata (`_resolved_provider`,
  `_resolved_model`, `_response_id`, token counts, per-call price snapshot, latency), the item files
  with their ground truth and equivalence rules, the scorer with its control suite and results, and
  every consent and review exchange verbatim.
- **Retention:** for the life of the deposit. Nothing is withdrawn on an unfavourable result.
- **Redaction policy:** none is anticipated; if any is ever applied, the fact, the scope and the
  reason are recorded **in the deposit**, and the unredacted material remains available to any
  reviewer who asks.
- **Negative and null results are published on the same schedule as positive ones.** There is no
  outcome under which this goes unpublished.

⏱️ **TIMELINE — a commitment, not an aspiration.** `qwen/qwen3.5-27b` raised, correctly, that *"if
results take months to publish, gpt-4o may already be offline by the time findings are public"* —
the study's own premise turned against it. **The preprint ships within days of the run, not months.**
Peer review is slower and is explicitly **not** on the critical path; the preprint and the full data
deposit stand on their own. *An argument that arrives after the deprecation is an obituary.*""")

for name, old, new in edits:
    n = t.count(old)
    if n != 1:
        sys.stderr.write("!! %s: matched %d times (need 1)\n" % (name, n))
        sys.exit(1)
    t = t.replace(old, new)
    print("   ok  %s" % name)

io.open(P, "w", encoding="utf-8").write(t)
print("\n%d edits applied; %d -> %d chars" % (len(edits), n0, len(t)))
