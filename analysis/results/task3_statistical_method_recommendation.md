# Task 3 - Statistical Method Recommendation

Generated: 2026-08-30T23:51:28

This report chooses the simplest defensible statistical approach before hypothesis testing. It does not run tests or fit models.

## Data Features That Matter
Ratings are 1-5 Likert-style responses. They are ordered categories, but in small user studies it is common to summarize them with means and use simple participant-aware models when the goal is an interpretable thesis analysis.
Phase 1 has 263 trial rows from 16 participants. The design is repeated because each participant rated multiple explanations. It is also unbalanced: participants contributed between 2 and 20 trials, and not every participant rated every explanation type equally often.
Phase 2 has 107 trial rows from 14 participants. It is a within-participant comparison because participants rated both Agentic XAI and MentaLLaMA, with one incomplete participant in the current file.
Independent-samples tests are not appropriate as the primary analysis because rows from the same participant are related.

## Plain-English Concepts
Repeated measures means the same participant gives more than one rating. Their ratings are connected because the same person may consistently rate higher, lower, more cautiously, or more generously than another person.
Participant ID must be accounted for because otherwise the analysis treats repeated rows from one participant as if they came from different people. That would overstate the amount of independent evidence.
Row-level analysis is useful because it keeps every valid trial. This preserves information about explanation type or system, passage, severity, question type, and trial-to-trial variation.
Participant-level analysis is also useful because it averages each participant within each condition. This gives an easy-to-explain robustness check and directly shows whether the pattern is consistent across people.
A p-value answers this kind of question: if there were really no difference between conditions, how surprising would data like this be under the model? It is not the probability that the hypothesis is true.
A confidence interval gives a plausible range for an estimated quantity, such as a mean difference. Narrow intervals mean the estimate is more precise; wide intervals mean more uncertainty.
An effect size describes how large a difference is, not just whether it is detectable. For thesis reporting, effect sizes help explain practical importance.

## Recommended Primary Method
Use a simple linear mixed-effects model for each rating dimension separately.
Phase 1 primary model: rating ~ explanation_type + (1 | participant). In Python/statsmodels wording, this is a mixed model with explanation type as a fixed effect and a random participant intercept.
Phase 2 primary model: rating ~ explanation_system + (1 | participant). The main fixed effect is Agentic XAI vs MentaLLaMA, with a random participant intercept.
The random participant intercept lets each participant have their own baseline rating level. This directly handles repeated ratings without making the model complicated.
This approach is simpler and more defensible for the current data than a large model with many interactions.

## Why This Is Defensible With Likert Ratings
The ratings are ordinal, so an ordinal mixed model would be theoretically attractive. In practice, ordinal mixed models are harder to explain, less available in the requested Python stack, and can be unstable with small samples.
A linear mixed-effects model treats the 1-5 scale approximately as numeric. That is a pragmatic and common choice when the scale has several ordered points, the thesis needs clear interpretation, and results are reported cautiously.
To avoid overclaiming, report means, confidence intervals, effect sizes, and robustness checks. Avoid claiming that a one-point change has exactly equal meaning everywhere on the scale.

## Secondary Variables
Severity and question type should be treated as secondary variables, not automatically added into the main model.
For Phase 1, severity can be inspected descriptively and optionally added in a sensitivity model: rating ~ explanation_type + severity + (1 | participant).
For Phase 2, question type and severity can be inspected descriptively and optionally added in sensitivity models. The primary research question should remain Agentic XAI vs MentaLLaMA.
Avoid high-order interactions unless there is a strong thesis reason and enough data in every cell. The current sample is small, so complicated models would be fragile.

## Recommended Secondary Checks
Participant-level Phase 1 check: average each participant within each explanation type and rating dimension, then run a repeated-measures comparison only where participants have data for all explanation types. If too much data is missing, report it mainly as descriptive.
Participant-level Phase 2 check: average each participant's Agentic XAI and MentaLLaMA ratings, calculate paired differences, and use a paired test as a robustness check.
For Phase 2 participant-level robustness, a paired t-test is easy to explain if differences are reasonably symmetric. A Wilcoxon signed-rank test is a non-parametric alternative for the small Likert-scale sample.
These checks should support interpretation. They should not replace the primary mixed-effects model or be selected only because they give a more favorable p-value.

## What To Report Later
For each rating dimension, report the estimated condition means or mean differences, 95% confidence intervals, p-values, and effect sizes.
For Phase 1, report the overall explanation-type test first, then pairwise comparisons between explanation types with multiplicity correction.
For Phase 2, report the Agentic XAI minus MentaLLaMA estimate for each dimension.
Use careful language: evidence of a difference, no clear evidence of a difference, higher estimated rating, lower estimated rating. Do not imply clinical conclusions from explanation-quality ratings.

## Stop Point
Task 3 is complete. The next phase should run hypothesis tests only after explicit confirmation.
