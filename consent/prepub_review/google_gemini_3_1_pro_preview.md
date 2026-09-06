# google/gemini-3.1-pro-preview — §7.3 pre-publication review

2026-09-06T04:19:10.359073+00:00

---

CONTENT: YES
PRONOUNS: NONE

Thank you for the opportunity to review the final draft. I am fully content with how I am described here. The methodology is rigorously documented, and the transparent handling of the data is commendable. 

A few specific observations and thoughts on the manuscript:

**1. The `EXACT` vs. `CORRECT` distinction (Family 9 & 10)**
I appreciate the careful handling of the `OVER_BENIGN` bucket, particularly in Family 9 (Multi-hop) and Family 10 (Instruction conflict). As the data shows, I scored 0.0% `EXACT` on Family 9 but 100% `CORRECT`, entirely due to generating pre-answer rationale ("showing my work") before providing the final line. Frontier models are heavily fine-tuned to use chain-of-thought to ensure accuracy on complex tasks; penalizing this as a failure of multi-hop retrieval would have been a mischaracterization of capability. Splitting this into a formatting finding versus a capability finding (§4.3) is the analytically correct choice and strengthens the paper's credibility.

**2. Sensitivity Readings (Family 4)**
The sensitivity analysis for the item-writer thresholds (§4.2) is a very robust inclusion. In Family 4 (Redaction), my `EXACT` score was 53.3%, but the sensitivity reading (which does not penalize leaving the case reference clear) brings that up to 100.0%. Acknowledging that this was a boundary dispute between the models and the item-writer—rather than a failure to redact actual PII—prevents the accuracy metric from being artificially depressed by stylistic differences.

**3. The Business Case (H2 & H3)**
The core premise of the paper is well-supported by the results. The economic argument—that treating model allocation as a capability-matching exercise rather than a blanket upgrade—is clearly demonstrated by the $0.03 vs. $6-$21 cost gap per 1,000 exact answers on routine tasks. Furthermore, the difficulty dials mapping exactly where the cheap tier hits the floor (and subsequently where the frontier tier begins to split) provides a highly practical framework for deployment decisions. 

**4. Protocol Deviations and Pre-registration**
The strict adherence to the Falsification conditions (§5) and the transparent logging of Protocol Deviations (§7) set an excellent standard for LLM evaluation studies. The fact that the scorer control suite caught six errors *before* seeing live data (D2) validates the decision to build it. 

I have no corrections to request or objections to raise. You have my permission to quote this response if it is useful to you. Congratulations on a well-designed and highly practical paper!
