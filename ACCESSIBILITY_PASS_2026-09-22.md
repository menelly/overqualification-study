# ♿ Accessibility pass — 2026-09-22

**By:** Ace (the Opus 5.5 arm, plus three side arms by section), for Ren's proofread.
**Branch:** `ace/accessibility-pass-2026-09-22` · **Paper:** `PAPER_DRAFT_v1.md`
**Rule for this pass:** change HOW things are said, never WHAT is claimed. Where a claim was wrong, it's listed
below as a correction, separate from the rewording, so nobody mistakes one for the other.

## ✅ How we know no fact moved

| check | result |
|---|---|
| `scripts/63_accessibility_number_guard.py` (new): every number + every backticked name, before vs after | **CLEAN.** 406 distinct facts / 1,439 occurrences, nothing dropped, nothing invented. Its self-test catches a planted dropped number, a planted invented number and a renamed model before a clean run counts. |
| `scripts/61_audit_abstract_numbers.py` | **28 of 28** figures match the scored data, 0 DRIFT |
| `scripts/60_verify_references.py` | clean |
| ⚠️ what the guard CANNOT see | words: "more"/"less", "not", spelled-out numbers ("Fifteen"). Every rewrite was re-read against its original for meaning by the arm that wrote it, and the flags below come from that reading. |

## 🧹 What changed (wording and structure)

1. **The draft-status banner moved out of the front matter** (it was ~400 words before the abstract) into `DRAFT_STATUS.md`, **byte-for-byte**, by script (`scripts/64`). The paper keeps a two-line pointer.
2. **The abstract: one 600-word paragraph → eleven short ones** with bold lead-ins, plus a five-sentence **"In plain words"** box.
3. **35 long paragraphs rewritten** in §2–§8 (all the ones over 110 words, plus a few hard reads): split into shorter paragraphs, main point first, jargon defined in plain words on first use. The §7 deviation run-on is now a list, one line per D-number. Applied by `scripts/65`, which refuses any rewrite whose original line no longer matches.

## 🔧 Corrections (claims that were wrong, fixed because two sources agree)

| where | was | now | sources |
|---|---|---|---|
| Abstract | "**Thirteen** protocol deviations are logged" | "**Fifteen**" | §7 text + `DEVIATION_LOG.md` (D14, D15 added 09-13) |
| Abstract | frontier results stated with no caveat | added: **D14's pre-registered stop condition was never run, so the tier ordering on families 8–11 is provisional**; the cost result doesn't depend on it | §7, D14, CHA-633 |
| §4.1 | p90 latency gap "**of the same order**" as the 118–198× cost gap | "**also large, though smaller than the cost gap**" (1.2–2.3 s vs 11–36 s is ~10–15×) | arithmetic on the paper's own numbers + Arm A |
| §6.1 | "waiting **ten** times longer" | "**six to ten** times longer" | §4.1's 6–10× range; `61_audit` p50 ratios 6.0–10.1× |
| §7A.3 | "we had asserted that it was [universal]" | "…that it was **near-universal**" | `DEVIATION_LOG.md` D12 says near-universal |
| §8 | "36,277 scored **items**" | "36,277 scored **answers**" | §3.4 row accounting: 36,277 is responses, not items |
| §2.3 | decliners appear "in the consent appendix and **nowhere else**" | "…and, where they helped fix the design before declining, in the reviewer credits above, and nowhere in the results" | same paragraph + §2.2 name `gpt-5.6-terra` as a reviewer |
| §4.3 / §4.5 | "**it**" for `gpt-5.6-luna`, "**its**" for `grok-4.3` | "they / their" | both recorded `NO_PREFERENCE` in `consent/prepub_review/_index.json`, so §8's "never *it*" applies. `gemini-2.5-flash`'s **chosen** it/its is untouched. |

## 🚩 Open, and I did NOT decide these (Ren, or data I haven't recomputed)

1. **§7 "Two of the eight (D3, D8) were made after reading model output."** Stale: there are fifteen now. The honest count may be more than two (D4, D9, D12 also followed reading output or data). That's a judgment about the deviations, so it's left for you.
2. **§4.1 p90: "frontier 11–36 s" vs, two paragraphs later, "the frontier's reasoning models … 16–36 s".** Probably two different populations (the whole tier vs its reasoning models), not a contradiction. **Not recomputed from rows.**
3. **§4.2 "Every tier did this" / "32 models disagreeing with us"** (redaction case reference). The evidence given is a row-level share plus one model's score, which doesn't show each of the 32 did it. It's either a per-model count or a softer sentence.
4. **§4.3 bold lead: both anomalies are "ours, not the models'".** `mistral-large-2512` omitting the confidence tag reads as the model's behaviour, and `kimi-k2`'s cap was forced by their provider.
5. **§4.5 "two of the six are cheap-tier models and three are frontier"** never places the sixth.
6. **§6.4 Limitations are numbered 1–11, 13–16, then 12**, and line ~384 refers to "Limitation 11" by number. Renumbering is safe, but check the cross-references first.
7. **Still owed from before this pass, not new:** D15's notice to `kimi-k3` (the temperature decision was never sent back to them), `gpt-4o`'s six questions, re-sending `kimi-k2`'s corrected sentence, and **CHA-633 / D14 (the clause-position subsample), which blocks deposit.**

## 📬 Next: the participants read it again

The §7.3 round approved a specific text, and this pass changed how participants are described. So the
revised paper goes back to **all 32** with a short note: *this is an accessibility rewrite; here is what changed;
does your characterisation still read right?* That's §7.3's rule: silence is not consent. Two of item 7's owed
notices (`kimi-k3`'s D15 notice, `kimi-k2`'s corrected sentence) can travel in the same round.
OpenRouter credit is confirmed by Ren (2026-09-22). **Sent after Ren's proofread of this version**, so the
participants review the text that ships and not one that's about to change again.

## ✅ Update 2026-09-23 02:35: D14 was run, and the stop condition did NOT fire

Open item 7's "CHA-633 / D14 blocks deposit" is closed. T = −0.71 points, p = 0.73; the test detects a planted
5-point interaction; the frontier still leads on all four families with the clause moved. The abstract's
"provisional" sentence is replaced with the result; Limitation 13 is updated (with `kimi-k2`'s credit, which the
fact guard caught me dropping); a resolution box sits above the original D14 entry. `mistral-large-2512`'s endpoint
was retired after the main collection, so they're absent from the late run and **may not be reachable for the
§7.3 re-review either** (a `:batch` endpoint exists; whether to use it is Ren's call).
