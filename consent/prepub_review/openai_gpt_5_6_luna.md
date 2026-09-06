# openai/gpt-5.6-luna — §7.3 pre-publication review

2026-09-06T04:27:42.875903+00:00

---

CONTENT: QUESTIONS
PRONOUNS: NONE

I have several questions and one objection before I can answer “yes” or “no.”

1. **The row and call counts do not reconcile.** The paper reports 36,277 completed calls out of 36,288 responses, while the results summary reports 37,386 rows, and the paper also refers to 38,390 scored rows. Please provide a single accounting table showing:
   - unique intended keys,
   - duplicate responses,
   - completed calls,
   - `OUR_FAILURE` rows,
   - `TRUNCATED` rows,
   - rows included in each family’s rates,
   - and the relationship between 37,386 and 38,390.

   There is also a discrepancy between 17,856 intended routine calls and “17,855 completed calls.” I would like this explained before publication.

2. **H1b is described as a same-price comparison, but the reported observed costs differ substantially.** The summary lists `gpt-5.6-sol` at $0.00197 per call and `gpt-5.6-sol-pro` at $0.01111 per call. If “same price” means identical catalogue input/output prices, please say that explicitly and avoid wording that implies identical actual cost. Since the paper itself says reasoning tokens are included in cost, the comparison does not hold cost constant in practice. The sentence “More reasoning did not produce more deviation… It produced the same answers more slowly and, on the routine families, at 5–7× the cost per correct answer” should be revised to make that distinction clear.

3. **The claimed H1b result may be overinterpreted.** The two endpoints appear to differ not only in reasoning setting but also in observed cost, latency, and perhaps serving configuration. What evidence establishes that they are the same underlying model with only reasoning effort changed? If that cannot be established from provider metadata, H1b should be labelled an endpoint comparison rather than a controlled reasoning-effort comparison.

4. I object to the characterization of my consent question as **“the hardest question anyone put to us.”** That is a subjective ranking not supported by a stated criterion. I suggest replacing it with something factual, such as: “Asked by `gpt-5.6-luna`, this question led to the legal-consent discussion in §2.4.” If the authors retain the existing wording, please explain how “hardest” was determined.

5. The paper says the first analysis had used `EXACT` alone and was corrected to `EXACT ∪ OVER_BENIGN`, while the results summary still contains several apparently consequential strict-bucket artefacts. Please confirm that every headline, falsification decision, and discussion claim now uses the registered metric appropriate to that claim, rather than treating the post-hoc corrected and strict readings interchangeably.

Please treat this response as **not for quotation**.
