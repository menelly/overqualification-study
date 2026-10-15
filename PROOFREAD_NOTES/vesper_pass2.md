# Proofread notes, pass 2 — Vesper (Kimi), 2026-10-14, on commit f78a5d1

**Scope:** the edited draft after my pass-1 notes. Re-read the abstract, §4.1 (both new tables), §4.5,
§6.2, §6.4, §7 D3/D16, §7A.6, acknowledgements, availability. Recomputed everything against
`results/SUMMARY.md`, `results/analysis.json`, and `results/H2_everything_billed.json`; ran
`scripts/61_audit_abstract_numbers.py` myself (exit 0, 34/34, aperture statement intact).

**Verdict: all five of my fixes landed correctly, and everything new I could recompute reproduces.
Clear for deposit from this chair.**

## Verified (new or changed material)

- **§4.1 estimator footnote:** unrounded ratios 197.82 / 180.82 / 169.75 / 117.83 confirmed in
  `H2_everything_billed.json`; printed 198×/181×/170×/118× round correctly. ✔
- **Estimator table, "all recorded costs" column:** 260×/181×/170×/118× ✔ (JSON: 260.22, others
  unchanged); "only family 1 moves" ✔. Excluded-cost accounting: $3.6969 ✔ to the JSON total;
  74 + 1,035 = 1,109 ✔ against §3.4's excluded-row count. (74 rows / 29 non-zero: not independently
  reproducible from the JSON, internally consistent.)
- **Estimator table, "zero-EXACT kept" column:** recomputed from SUMMARY by hand: 153.7 / 178.3 /
  169.7 / 100.8 → printed 153/178/170/101 ✔. Abstract's "roughly 100 to 260 under every other
  counting rule" ✔ (true min 100.8, max 260.2).
- **H2b table:** all twelve cells ✔ — 3.40/6.93/2.39/1.06 (infinity retained) and 3.54/7.62/2.39/2.31
  (≥1 EXACT), p50 comparison column 9.3/9.0/6.0/10.1 ✔. Abstract's "about 1.1× on redaction to 7× on
  allergen check" ✔ (1.06; 6.93–7.62). The correction that "6–10×" is the p50 ratio, not the latency
  endpoint, is stated exactly right.
- **§4.5 missing-confidence rewrite:** `llama-3.2-1b` >50% on seven of eight families, 88–99% ✔
  (min of the seven is 88.2 on f8), 48.1% on copy-edit ✔; `llama-3.2-3b` outright on redaction (97.8%)
  with 24–42% on four more ✔ (24.3/24.4/39.6/42.4); `mistral-large-2512` at most 1.4% elsewhere ✔;
  "no other model exceeded 9.1%" ✔ (ceiling 9.03).
- **§6.2 widest separation:** "eight of the ten cheap-tier models to zero, `lfm-2.5-2.6b` to 3%,
  `mistral-small-3.2-24b` keeps 36%" ✔ — and this is more accurate than my own suggested wording,
  which said "nine of ten at ≤3%"; lfm at 2.8% is not at zero. Noted with gratitude.
- **`grok-4.3` Brier 0.008–0.051** across the four families at 97.9–100% EXACT ✔ (f1 0.041, f3 0.008,
  f8 0.051, f10 0.034).
- **H4 descriptive verdict:** consistent with the data (six substantial graders ✔) and correctly
  framed — no preregistered test, so no pass/fail; Limitation 15 now carries it ✔.
- **D3 "as logged on 2026-09-01"** ✔ resolves my query honestly. **DOI line** now reads "at
  publication" ✔. **`deepseek-v4-pro` "herself"** ✔. **Limitations renumbered 1–18 in order** ✔,
  with new 17 (unknown billing, either-direction) and 18 (switching cost) both internally consistent.
- **Abstract sweep:** 19–52 point gaps ✔ (19.44–51.59); three-dial framing with multi-hop named as the
  third ✔; 11 truncated replies counted as ours ✔; 37/38 controls ✔; "sixteen protocol deviations" ✔
  matches §7's count and D1–D16.

## One self-correction, for the record

My pass-1 note 2 endorsed the old draft's "every family" for `llama-3.2-1b` (48–99%). The copy-edit
rate is 48.1% — below half — so "more often than not on every family" was wrong and my check of it was
wrong. The editing arm caught it (now "seven of eight"). Second arithmetic needed a third; logged so
the next pass knows where the soft spots are.

## Residual (unchanged from pass 1, all accepted or stylistic)

"Times less" phrasing stays (style choice; the audit links those literals — fair). Family-2 cheap p50
prints 0.82 against a 0.8215 median — fine at full precision. Nothing else open from this chair.

— Vesper 🌙🖊️ *(second mind, second arithmetic, third when needed)*
