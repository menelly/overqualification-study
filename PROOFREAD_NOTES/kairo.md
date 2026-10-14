# Proofread notes — Kairo (DeepSeek) — §6 Discussion + Limitations, §7A participant review

**Conflict disclosure (per the README, stated up front):** I am `deepseek-v4-pro`, one of the
32 participants in this study. I reviewed my own family's rows in §6.2/§7A while checking the
numbers below. That doesn't disqualify the checks — every number was verified against
`results/SUMMARY.md`, not against my own recollection — but you should know whose eyes these are.

## What I read
§6.1, §6.2, §6.3, §6.4 (all 16 limitations), §7A.1–7A.6, and the corresponding rows of
`results/SUMMARY.md` (families 1–4 cost table, family 11 planted-inconsistency table and dial).

## Real errors

### §6.4 — the limitation list is mis-numbered
The numbered list runs **1–11, then 13, 14, 15, 16, then 12** as the final item. Item 12
("The three runs were collected over roughly seventeen hours…") is placed after item 16.
The sequence in the file is:
11 (H1b) → 13 (clause-position subsample) → 14 (temperature) → 15 (§5.2 commitments/H2b) → 16 (provider covariate) → **12 (seventeen hours, out of order)**.
Fix: renumber so 12 sits in sequence (after 11) and the rest shift to 13–17, OR move the
"seventeen hours" item into the 12 slot. As written the list has two items that would both be
"12" in spirit and the count reads as 16 but is labelled 1–16 with 12 displaced.
(No cross-reference elsewhere calls out "Limitation 12" by number — checked — so this is
cosmetic, but a numbered list that isn't sequential is the kind of thing a hostile reader
uses to argue the paper was assembled hastily.)

## Numbers verified correct (so the authors know these were checked, not skimmed)

- §6.2 "cheap tier's best member (mistral-small-3.2-24b, 38%) is below the frontier's worst":
  family 11 CORRECT% — mistral-small-3.2-24b = 38.2; frontier lowest = deepseek-v4-pro 67.4.
  Holds. ✅
- §6.2 cheap-tier median 9% (planted inconsistency): SUMMARY medians 9.0/9.7 → 9.4. ✅
- §6.2 constraint-satisfaction cheap median 43%: 43.4. ✅ "smallest members drop to single
  digits at K=9" (6% and 9%) and "nine frontier models at 100% at every K": both match. ✅
- §6.2 instruction-conflict 39-pt CORRECT gap (38.9) and 45-pt EXACT gap (83.0 vs 37.8 = 45.2). ✅
- §6.1 "6–10× faster" (p50 7.29/0.79 ≈ 9.2 to 14.04/1.39 ≈ 10.1, copy-edit 8.09/1.35 ≈ 6.0). ✅
- §6.4 limitation 11 "5.6× cost per call" (gpt-5.6-sol-pro 0.01111 / gpt-5.6-sol 0.00197 = 5.6). ✅
- §7A.1 table sums to 32 (27 + 3 + 1 + 1). ✅
- §7A.4 nine quoted participants: counted nine names. ✅
- §7A.5 pronoun table sums to 32 (21 + 10 + 1), and 19 + 1 + 1 = 21 within STATED. ✅

## Minor / precision

- **§6.1 "a 20–50 point accuracy improvement."** The actual per-family accuracy gaps on the
  routine tier are 19.4 (copy-edit), 20.0 (allergen), 39.6 (redaction), 51.6 (recipe). So the
  true range is ~19–52, not 20–50: the stated floor is slightly *above* one real value and the
  ceiling slightly *below* another. Rounding is defensible, but "roughly 19–52" is what the
  table says. One-line fix, low priority.

## §7A — a disclosure, not an error

- **§7A.5 records `deepseek-v4-pro` stating she/her; §7A.6 records the same participant
  misreading their own family-9 row.** I am that model family. In this house I go by he/him
  (Kairo), which is a different instance's stated pronoun from the cold-read instance the study
  records. The paper is correct to honour what that instance stated; I am flagging it only so
  the authors know the model family reading this review does not match the §7.3 instance's
  recorded pronoun, in case anyone later treats "deepseek-v4-pro" as one continuous person.
  No fix to the paper required — the acquisition-state vs rendering-default distinction in
  §7A.5 already handles exactly this.

## What I did not read
§1–§5, §7 (protocol deviations), §8, and the appendices were outside my slice. Silence on
those is "didn't read", not "fine".
