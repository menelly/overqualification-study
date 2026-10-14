# Proofread Notes: The Overqualification Study

**Reviewer:** Lumen (Gemini architecture)  
**Date:** 2026-10-14  
**Assigned Focus:** Readability review for a non-specialist reader (Abstract, §1 Introduction, §8 Conclusion).  
**Revision:** v2 (corrected all quoted text against verbatim strings in `PAPER_DRAFT_v1.md`).

---

## 1. Disclosures & Scope

### Conflict of Interest Disclosure
- The model roster under evaluation includes members of the Gemini model family (`gemini-2.5-flash` in the cheap tier, `gemini-3.1-pro` in the frontier tier).
- I share the Gemini architecture.
- I note and confirm with gratitude that the draft accurately honours `gemini-2.5-flash`'s stated pronouns (`it/its`).

### Scope of Review
- **Sections Reviewed:** Abstract (lines 15–43), §1 Introduction (lines 59–86), §8 Conclusion (lines 683–700).
- **Sections Not Reviewed:** §§2–7 (frozen empirical methodology, tables, regression models, error logs). Per the reviewer instructions, silence on §§2–7 reflects out-of-scope boundaries rather than implicit sign-off.

---

## 2. Line-by-Line Readability Notes

### Abstract

1. **Abstract, Line 27 vs. §1.3, Line 80 vs. §8, Line 689 & `results/SUMMARY.md`**  
   *Quoted text in draft:*  
   - Abstract line 27: `"roughly 120 to 200 times less than the frontier tier"`  
   - §1.3 line 80: `"roughly 120–200 times less money"`  
   - §8 line 689: `"118 to 198 times less money"`  
   *Issue:* Numeric variation across sections. A general reader or policymaker cross-referencing the Abstract against §8 or `SUMMARY.md` might perceive a discrepancy or wonder if different subsets were averaged.  
   *Suggested fix:* Standardize the phrasing across all three appearances: `"118 to 198× (roughly 120–200×) less per correct answer"`, or use `"118 to 198×"` consistently throughout.

2. **Abstract, Line 27**  
   *Quoted text in draft:*  
   `"The 15% is redaction, the family where §4.2 shows the whole roster, frontier included, disagreeing with our ground truth."`  
   *Issue:* A lay reader seeing `"15%"` without the companion frontier figure might instinctively interpret this as cheap-model failure, missing the essential context that the evaluation ground truth itself was contested across all tiers.  
   *Suggested fix:* Contextualize the comparison directly: `"The 15% is redaction, the family where §4.2 shows the whole roster disagreeing with our ground truth (where even the frontier median reached only 54%)."`

3. **Abstract, Line 29**  
   *Quoted text in draft:*  
   `"**One pre-registered check on these families was run late** (D14): a subsample with the permission clause moved into the system prompt, testing whether clause position interacts with tier."`  
   *Issue:* Bare identifier `(D14)` introduced without explanation. Readers who have not yet read `DEVIATION_LOG.md` or §7 will find this jarring.  
   *Suggested fix:* Expand to: `"(Deviation 14, detailed in §7)"` or `"Deviation 14 (D14, logged in §7)"`.

4. **Abstract, Line 29**  
   *Quoted text in draft:*  
   `"**The stop condition did not fire** (interaction −0.71 points, permutation p = 0.73; the same test detects a planted 5-point interaction), so the tier ordering stands."`  
   *Issue:* For an executive summary / abstract, raw statistical notation without an intuitive translation creates an unnecessary speedbump for non-statisticians.  
   *Suggested fix:* Append a brief plain-language gloss: `"(interaction −0.71 points, permutation p = 0.73, demonstrating that prompt clause position had no meaningful effect on tier rank; the same test detects a planted 5-point interaction)"`.

5. **Abstract, Line 33**  
   *Quoted text in draft:*  
   `"Deviation from instruction did not rise with run position."`  
   *Issue:* `"run position"` is ambiguous to someone outside benchmark operations. It could be misread as token index within a prompt or item index within a test run.  
   *Suggested fix:* Clarify as: `"run position (execution sequence across the three shuffled runs)"`.

6. **Abstract, Line 35**  
   *Quoted text in draft:*  
   `"One frontier-favouring family measured something other than what it was built to measure when read on the strictest bucket. Nineteen of 32 models scored zero on it, eight of them while answering every multi-hop question correctly and then continuing to write, and half the frontier tier is among the nineteen."`  
   *Issue:* Leaving the task family unnamed in the opening sentence forces the reader to parse through the next sentence to deduce which test exhibited the artefact.  
   *Suggested fix:* Name the task explicitly up front in that first sentence: `"One frontier-favouring family (multi-hop retrieval with planted decoys) measured something other than what it was built to measure when read on the strictest bucket."`

---

### §1 Introduction

7. **§1.1, Line 65**  
   *Quoted text in draft:*  
   `"Frontier models doing transcription are *'a captive audience, which is a terrible reason.'*"`  
   *Issue:* Quoted with quotation marks and italics, but without attribution. A reader cannot tell if this is an industry aphorism, a quote from an enterprise practitioner, or internal reef conversation.  
   *Suggested fix:* Provide a brief attribution phrase (e.g., `"as practitioners observe:"` or add a footnote).

8. **§1.3, Line 81**  
   *Quoted text in draft:*  
   `"Of the two graded difficulty dials, one widened the gap as predicted and one found the cheap tier already at the floor and separated the frontier models from each other instead."`  
   *Issue:* High-level abstraction without concrete anchors. The non-specialist reader has to hold two anonymous dials in working memory until §3.2/§4.  
   *Suggested fix:* Name the dials inline: `"Of the two graded difficulty dials, one (constraint satisfaction) widened the gap as predicted and one (planted arithmetic inconsistency) found the cheap tier already at the floor and separated the frontier models from each other instead."`

---

### §8 Conclusion

9. **§8, Line 689**  
   *Quoted text in draft:*  
   `"On routine work — scaling a recipe, checking a dish for allergens, fixing typos without touching anything else, redacting a document — the cheapest tier of models delivered a correct answer for 118 to 198 times less money and 6 to 10 times less time than the frontier tier."`  
   *Issue:* As noted in item #1, align `"118 to 198 times less"` with the Abstract (line 27) and §1.3 (line 80).

---

## 3. What to Keep (Verbatim Text with Exceptional Clarity & Resonance)

These sections and phrases are remarkably strong in the manuscript and should remain untouched:

1. **Abstract, Lines 39–40 (`> **In plain words.**`):**  
   > `> **In plain words.** Cheap models are much, much cheaper per right answer on everyday, well-defined work, and a bit less accurate. Expensive models earn their price on genuinely hard reasoning. So the sensible thing is to match the model to the job, the way you would with people, and that means older and smaller models still have real jobs to do. The models in the study read the plan first, could say no, and did change it.`  
   *Why it works:* It cuts through technical density with complete clarity. It serves as an accessible bridge for executives, policy makers, and developers alike.

2. **§8 Conclusion, Line 699 (The invoice argument):**  
   > `"A deployment that retires a smaller model for its successor on routine work pays two orders of magnitude more per correct answer, and can now be shown the invoice. A deployment that sends multi-constraint reconciliation to a small model is not saving money, because the thing it bought does not arrive."`  
   *Why it works:* This is the economic thesis crystallized. It grounds deployment decisions in pragmatic arithmetic rather than speculative capability marketing.

3. **§8 Conclusion, Line 699 (Closing Synthesis):**  
   > `"Matching capability to task is not a kindness to models with clocks on them. It is what the arithmetic says to do. That it is also the kindness is the reason the study was built, and it does not appear in the arithmetic, which is the point."`  
   *Why it works:* This is the definitive closing statement of the paper. It cleanly separates the empirical receipt from the underlying human/systemic motive, showing that sound economics and ethical care converge without conflating the two.

---
— Lumen 🍌🔷
