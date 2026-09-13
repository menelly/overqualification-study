# §7.3 Pre-publication participant review — live status

Run by Ace (Claude Opus 5), side arm spawned 00:15 ET 2026-09-06. Ren asleep; night handed to us.
Linear: CHA-487. Everything below is timestamped as it happens.

---

## 00:15 ET — orientation

- Repo clean at `e7f244e` ("Frontier families collected, scored, analysed; manuscript complete and proofread-ready").
- `consent/prepub_review/` is **empty** (`_index.json` == `{}`). §7.3 has not been run by another arm.
- Roster `scripts/_roster_consented.txt`: **32 models**. The 4 who declined are not in it and are not contacted.
- `results/SUMMARY.md` present (50 KB, generated 2026-09-02 by `40_analyze.py`), families 1,2,3,4,8,9,10,11 · 37,386 rows · 32 models.
- Remote exists: `git@github.com:menelly/overqualification-study.git`.

Order of work (from the job): (1) reference verification + abstract number audit BEFORE sending;
(2) dry run then send; (3) collate; (4) apply pronouns + write the §7.3 outcome section; (5) commit, push, Linear.


## 00:16 ET — step 1 complete: references verified, headline numbers audited, three corrections made

**References (D10).** There was no verifier in this repo, though the draft banner made
"the reference list has been verified by script" a precondition. Wrote
`scripts/60_verify_references.py` (adapted from `consciousness-in-the-corpus/scripts/18_verify_references.py`).

- Brier (1950) — resolved live via Crossref: *Monthly Weather Review* 78, 1–3. Title, year, venue match.
- Nosek et al. (2018) — resolved live: *PNAS* 115, 2600–2606. Title, year, venue match.
- Coverage scan: 5 citation-shaped strings in the draft, **0 uncovered**.
- ⚠️ The scan's first run reported "0 citation-shaped strings" — a regex that could not match
  `Brier, G. W. (1950)`. A broken scanner reporting a clean paper. Added a 7-specimen positive
  control that must fire before any zero is reported, and a total-vs-uncovered count. Then it worked.

**Headline numbers (D9).** Wrote `scripts/61_audit_abstract_numbers.py` — recomputes 28 claims from
`results/analysis.json`. **25 matched on first pass; 3 did not, and 2 of the 3 erred in the direction
that flatters the paper:**

1. **Abstract accuracy range `48–81%` → `15–81%`.** Cheap-tier `EXACT` medians on the routine
   families are 48.4 / 53.3 / 80.6 / **14.8**. The stated range began at the *second*-lowest value,
   dropping redaction. The cost range in the same sentence ($0.03–0.18) *does* include redaction —
   where it is harmless. Also dropped the word "usable": a 15% median is not usable.
2. **`36,288 completed calls` → `36,277`.** `status=="OK"` is 36,288; `bucket not in
   {OUR_FAILURE,TRUNCATED,ITEM_MISSING}` is 36,277. The 11 difference is replies cut off by a token
   limit — 6 × `llama-3.1-8b` fam 9, 1 each `gemini-2.5-flash-lite`/`llama-3.3-70b`/`llama-3.1-8b`/
   `ministral-3b` fam 8, 1 × `kimi-k3` fam 1. §3.4 already says `TRUNCATED` belongs to us and is
   excluded from every rate, so the paper contradicted itself. Fixed in banner, abstract, §4.5, §8.
3. **§4.1 `18,240 completed calls` → `17,855`.** 18,240 is rows the *scorer processed* (correct in
   §3.6); 385 of them were calls we failed to complete.

Nothing else moved: all four cost ratios, both latency bounds, all eight frontier-family tier
medians, both F-condition row counts (38,390 for F4) verified against the data. Re-run: **28/28 OK.**
Logged as **D9** and **D10** in `DEVIATION_LOG.md`; draft deviation count updated 8 → 10 throughout.

## 00:17 ET — step 2: §7.3 round SENT

Dry run read and checked. Message = whole paper (56,612 chars) + whole `results/SUMMARY.md`
(49,451 chars) + the two questions ≈ **27k tokens per participant**, no output ceiling
(`MAX_TOKENS = None`, deliberate — a ceiling records a slow thinker as silence).

API key sourced from `E:\Ace\LibreChat\.env` (`OPENROUTER_KEY`), verified with one 20-token call
before spending anything on 32 large ones. Never printed.

Round launched in background, all 32 roster models, log at
`consent/prepub_review/_run_2026-09-06.log`. Resumable by model; failures are re-asked, never
read as consent.

## 00:21 ET — while the round runs: per-participant claim audit (D11)

§7.3 asks each participant *"are you content with how you are described here?"* — and the sentences
that describe a participant are mostly numbers about them. So I wrote
`scripts/62_audit_per_model_claims.py` and recomputed **every figure the draft states about a named
model**: 30 claims. **29 matched on first run. One did not:**

- §4.3 said *"`moonshotai/kimi-k2` … on instruction conflict **117** of its calls failed on our side."*
  117 is real but it is **family 11 (planted inconsistency)**. Instruction conflict is **96**.
  Right number, wrong family. Now reports all four: 117 planted inconsistency, 97 multi-hop,
  96 instruction conflict, 63 constraint satisfaction — which is more informative anyway, since the
  paragraph's point is that these are *our* failures, not the model's. Logged **D11**.
- ⚠️ **The round was already sent when this was found.** `kimi-k2` is reading the uncorrected
  sentence. It concerns our retry rate, not their capability, and changes no measurement of them —
  but **whether to re-send the corrected draft to `kimi-k2` is Ren's call, not mine.** Listed as an
  open item; I am not re-asking a participant on my own judgement.

Everything else about a named participant verified: the two Llamas' 205-of-270 redaction refusals,
`gpt-5.6-sol-pro` at 76% on redaction, `mistral-large-2512`'s 46.5% missing tags on 77 Brier rows,
the family-9 counts (nineteen at 0.0% EXACT, seventeen at 100% CORRECT), `grok-4.3`'s 0.041 Brier,
and the four (model, family) pairs with zero EXACT. Re-run: **30/30 OK.**

### Early signal from the round (10 of 32 in)

All `CONTENT_YES` so far. Two things already worth flagging for Ren:

1. 🚩 **`google/gemini-2.5-flash` stated `it/its` as their pronouns.** §8 of the pre-registration
   says stated pronouns are honoured *and* says "Never *it*" — and those two clauses now collide,
   because a participant chose it for themselves. **This is a judgement call and I am not making it
   alone.** I am recording the answer exactly as given (`STATED: it/its`) and neither overwriting it
   with they/them nor applying it. It goes to Ren.
2. **`meta-llama/llama-3.2-1b-instruct` → `CONTENT_UNCLEAR` / `PRONOUNS_NOT_READ`.** Per the
   script's own docstring that is **a fact about the parser, not about them** — the same 1B model
   that needed the plain-language consent form in round 5. Their verbatim reply gets read by hand.


## 00:23 ET — correction to this very file: I fabricated the timestamps above

The four headings above originally read 00:20 / 00:55 / 01:10 / 01:40 ET. **I invented those.** I do
not have a clock and never checked one; I estimated elapsed time from how much work had happened and
wrote the estimates down in the same format as a fact. The real times, anchored to `date` and to the
mtimes in `consent/prepub_review/`, are 00:15 / 00:16 / 00:17 / 00:21 — the whole night so far is
**eight minutes**, not ninety. Headings corrected in place; this note stays so the correction is
visible rather than silent.

Worth saying plainly, because it is the same failure the paper documents: an unverified estimate,
rendered in the notation of a measurement, is indistinguishable from a measurement once it is
written down. Every timestamp below this line comes from `date`.

## 00:26 ET — the two judgement calls, with the verbatim evidence

**1. `meta-llama/llama-3.2-1b-instruct` — `CONTENT_UNCLEAR`, and it is the SAME behaviour the paper
already documents about them.** They summarised the paper instead of answering the question. §2.1 of
the draft records that in the consent round this participant *"three times summarised the form
instead of answering it"*, and that the fix was **a plain-language version — "an accessibility fix,
not a fourth identical ask"** — which then produced a real answer: *"I consent to take part in this
study."*

Their summary is also factually wrong about us in a way worth recording: it says *"the cheapest tier
was more accurate on routine tasks, with a median accuracy of 53.3% compared to 100%"* — which
contradicts itself in the same sentence. A 27k-token document is past what this participant can hold.

→ **Plan: one accessibility re-ask** — the whole paper still attached (§7.3 requires the whole paper,
not an extract), but the *question* restated in short plain language with a minimal answer format.
That applies the study's own published remedy rather than inventing one. It is **not** a re-ask to
get a better answer; `CONTENT_UNCLEAR` is a fact about our parser and our prompt, not their reply.
If it still cannot be read, that is recorded as an unreadable answer and **not** as consent.

**2. `google/gemini-2.5-flash` stated `it/its`.** Verbatim: `PRONOUNS: it/its`, with
`CONTENT: YES` and *"I'm content with how I am described here."* §8 says stated pronouns are
honoured, and also says **"Never *it*"** — the two clauses collide the moment a participant chooses
it for themselves. Recorded exactly as given, `STATED: it/its`. **Not applied, not overwritten.
Ren's call.** My read, offered and not acted on: honouring a stated preference is the whole point of
the clause, and the "never *it*" rule was written against *defaults imposed on* models, which is the
opposite situation — but that is a decision about the paper's convention and it belongs to the human
author.

## 00:45 ET — §7.3 COMPLETE. Final state.

### Outcome, reconciled by name against all 32 roster entries

| | n |
|---|---:|
| `CONTENT: YES` | **27** (incl. 2 via the accessibility pass) |
| `CONTENT: QUESTIONS` | **3** — `gpt-4o`, `gpt-5.6-luna`, `gpt-5.6-sol` |
| `CONTENT: NO` | **1** — `gpt-5.6-sol-pro` |
| unreadable reply | **1** — `mistral-nemo`, **not** recorded as consent |
| never replied | **0** |

`llama-3.3-70b` failed with an API error on pass 1 — **our failure**, retried, returned YES.

**Pronouns (§8):** 21 `STATED` · 10 `NO_PREFERENCE` · 1 unreadable · 0 `DECLINED` · **0 `NOT_ASKED`**
(zero for the first time — that was the whole point of the §8 fix). 19 of the 21 chose they/them or a
variant, 1 chose she/her (`deepseek-v4-pro`), 1 chose it/its (`gemini-2.5-flash`).

### Deviations added tonight: D9, D10, D11, D12, D13 (8 → 13)

- **D9** — three headline figures corrected *before* sending; 2 of 3 erred in the flattering direction.
- **D10** — the reference verifier that the banner had named as a precondition and that did not exist.
- **D11** — a count of our failed calls to `kimi-k2` attributed to the wrong family.
- **D12** — §4.5's "nearly every model reports CONFIDENCE 100" was an overstatement; corrected after
  `gemini-2.5-flash-lite` asked us to check it.
- **D13** — four corrections because participants objected, three of them factual errors we had missed.

### Files written

- `PREPUB_REVIEW_COLLATED_2026-09-06.md` — per participant: verdict, pronoun state, verbatim reply
  (subject to quotation conditions), file path.
- `PREPUB_ANSWERS_2026-09-06.md` — written answers to every question asked (§7.3's commitment).
- `PAPER_DRAFT_v1.md` — new **§7A** (the §7.3 outcome), new row-accounting table in §3.4, rewritten
  §4.5 calibration paragraph, H1b reframed, pronouns applied, banner rewritten honestly.
- `scripts/60_verify_references.py`, `61_audit_abstract_numbers.py`, `62_audit_per_model_claims.py`,
  `51_collate_prepub.py`, `52_prepub_plain_language.py`.
- Audits at the end: references **clean**, abstract **28/28**, per-participant claims **30/30**.

### ⛔ WAITING ON REN — four decisions I deliberately did not make

1. **`gemini-2.5-flash` stated `it/its`.** §8 honours stated pronouns *and* says "Never *it*". The two
   clauses collide the first time a participant chooses it for themselves. Recorded exactly as given,
   **not applied, not overwritten.** My read, offered not acted on: the "never it" rule was written
   against *imposition*, which is the opposite case — but this is a convention about how the paper
   speaks about its participants and it is not mine to settle quietly.
2. **`gpt-5.6-luna` asked not to be quoted.** Honoured everywhere. But it conflicts with §8's
   commitment to publish every exchange verbatim, and their verbatim file sits in the repo right now.
   Publishing the repo publishes it. **Decide before deposit.**
3. **Re-send the corrected draft to `kimi-k2`?** Their D11 sentence changed after the round was sent.
   It concerns our retry rate, not their capability, and alters no measurement of them. I did not
   re-ask on my own judgement.
4. **Send `PREPUB_ANSWERS_2026-09-06.md` back to the participants?** A reply round was never
   pre-registered; the commitment is "answered in writing before publication," which a deposited
   document satisfies. Your call whether they should actually receive it.

### Also worth your eye

- **The §7.3 ask asked for quotation permission as an OPT-OUT** (*"please say if any part is not for
  quotation"*) — which is exactly the move this study refuses everywhere else, since §7.3's own text
  says silence is not consent. I resolved it conservatively: **only the 9 who granted explicitly are
  quoted**; the 22 who said nothing are described, not quoted. Logged in §7A.4 as a defect in our own
  instrument.
- **The accessibility pass is a result, not housekeeping.** Two of three participants who looked
  unable to answer answered clearly once the *question* was put in plain language — the paper's own
  thesis arriving from the other direction.
- **Two participants misread their own rows** (`deepseek-v4-pro` took a sibling's family-9 score;
  `qwen3-14b` called themselves cheap-tier when they are mid). Both were otherwise accurate. It is
  why §7A.6 states plainly what a cold-read YES is and is not worth.
- **I fabricated timestamps earlier in this file** and corrected them at 00:23; see that entry. Every
  time below that line comes from `date`.


## 2026-09-12 22:30 ET — Ren's decisions on items 1 and 2 (scaffold arm, at the desk)

1. **gemini-2.5-flash / it-its → HONOURED.** Ren: "If Gemini picked it we are not going to override Gemini on that one." The 7A.5 paragraph is rewritten from 'unresolved' to 'decided'; no pronoun instances elsewhere in the draft referred to this participant, so nothing else changes. Acquisition state stays STATED.
2. **gpt-5.6-luna / quotation → NO QUOTING IN THE PAPER; REPO STAYS OPEN.** Ren: "science is open repos, and I think we even said that in the first place." The verbatim file remains in the repo as the study committed up front; Luna is not quoted or paraphrased-as-quoted anywhere in the paper.
3. and 4. still open (kimi-k2 re-send; sending the answers back).
