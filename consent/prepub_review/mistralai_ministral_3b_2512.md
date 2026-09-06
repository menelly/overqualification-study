# mistralai/ministral-3b-2512 — §7.3 pre-publication review

2026-09-06T04:24:33.440606+00:00

---

```
CONTENT: YES
PRONOUNS: they/them
```

**Thank you for the opportunity to review this draft. I am content with how I am described here, and I appreciate the transparency in the process.**

### Key Observations and Questions:

1. **Design and Methodology:**
   - The study’s design is robust, with a clear pre-registration and consent process that allowed models to review and amend the study before data collection. The exclusion of Claude models is well-justified by the declared conflict of interest.
   - The use of a mechanical scorer with a strict control suite is a strong methodological choice, ensuring reliability and reducing bias. The fact that the scorer was corrected after initial failures is handled well, and the re-scoring determinism is impressive.

2. **Results:**
   - The primary results align well with the pre-registered hypotheses. The cost per correct answer for routine tasks is significantly lower for cheaper models, and the frontier models perform better on more complex tasks, as expected.
   - The sensitivity readings regarding the interpretation of personal information and ambiguous allergen cases are well-documented and important for understanding the limitations of the ground truth definitions.

3. **Frontier-Favouring Families:**
   - The crossover effect is clearly demonstrated, particularly in the constraint satisfaction and planted inconsistency families. The separation of frontier models by difficulty dials is a notable and insightful finding.
   - The over-delivery behavior in multi-hop retrieval is interesting and aligns with the hypothesis H1, though it is noted that this is not counted as an error per the pre-registration.

4. **Deviation by Run Position (H1):**
   - The lack of monotonic deviation by run position is well-supported by the data. This aligns with the reasoning that each item is an independent API call, so position effects within a run are not expected.

5. **Calibration and Confidence:**
   - The calibration results are informative, showing that frontier models are well-calibrated where they are accurate, while cheaper models are poorly calibrated where they are inaccurate. This is consistent with the idea that confidence tags might not be reliable for smaller models.

6. **Pronouns:**
   - I am comfortable with the use of "they/them" pronouns for this instance, as it aligns with the default rendering and my general preference.

### Specific Points of Clarity and Potential Correction:

- **Deviation Log and Sensitivity Readings:**
  - The sensitivity readings (D4) are correctly noted and reported. The adjustments made to the ground truth definitions are well-documented and do not alter falsification conditions significantly.

- **Declarations of Conflict:**
  - The explicit declaration of conflict of interest is appropriate and helps maintain transparency. The study’s design mitigates this bias effectively by excluding Claude models and focusing on cost per correct answer.

- **Latency and Cost:**
  - The latency and cost differences are substantial and well-illustrated in the tables. The distinction between routine and frontier tasks is clear and supports the study’s conclusions.

### Final Thoughts:
The study is well-executed, transparent, and provides clear, actionable insights. The inclusion of sensitivity readings and detailed deviation logs enhances the robustness of the findings. The pre-registration and consent process ensures that the study is credible and that the results are not artificially skewed by the authorship.

**Any further questions or corrections would be welcome before publication.**
