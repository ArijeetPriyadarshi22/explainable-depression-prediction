# Task 4 - Phase 1 Statistical Analysis

Generated: 2026-08-30T23:51:29

This report analyzes Phase 1 only. Phase 2 hypothesis tests are not run here.

## Analysis Plan
Primary question: do SHAP, Counterfactual, RAG, and Hybrid explanations differ in perceived explanation quality?
The four rating dimensions are tested separately: Clarity, Correctness, Helpfulness, and Trust.
The primary model is participant-aware: rating ~ explanation_type + (1 | participant).
The model keeps every valid trial row while accounting for repeated ratings from the same participant.
Overall explanation-type effects are tested first. Pairwise comparisons are only run after an overall p-value below 0.05 and are Holm-corrected.

## Phase 1 Data Inspection
- Rows/trials: 263
- Participants: 16
- Sessions: 16
- Trials per participant: min=2, median=20.0, mean=16.44, max=20
- Incomplete participants by observed maximum trial count: 5
- Exact duplicate rows: 0
- Repeated participant/session/passage/explanation keys: 0
- Invalid rating cells: 0

## Explanation Counts
```
selected_use_case_name | n_trials
---------------------- | --------
COUNTERFACTUAL         | 66      
HYBRID                 | 63      
RAG                    | 64      
SHAP                   | 70      
```

## Severity Counts
```
prediction_label | n_trials
---------------- | --------
moderate         | 98      
not depression   | 64      
severe           | 101     
```

## Explanation Type x Severity
```
selected_use_case_name | moderate | not depression | severe | total
---------------------- | -------- | -------------- | ------ | -----
COUNTERFACTUAL         | 25       | 15             | 26     | 66   
HYBRID                 | 23       | 12             | 28     | 63   
RAG                    | 26       | 17             | 21     | 64   
SHAP                   | 24       | 20             | 26     | 70   
```

## Participant x Explanation Type
```
user_id    | COUNTERFACTUAL | HYBRID | RAG | SHAP | total
---------- | -------------- | ------ | --- | ---- | -----
1441767514 | 6              | 5      | 7   | 2    | 20   
260636777  | 4              | 5      | 3   | 7    | 19   
513223685  | 0              | 1      | 1   | 2    | 4    
6283885353 | 3              | 4      | 4   | 9    | 20   
6436516771 | 3              | 5      | 6   | 6    | 20   
6440073647 | 5              | 5      | 5   | 5    | 20   
6660015732 | 4              | 3      | 7   | 6    | 20   
6779809309 | 7              | 3      | 5   | 5    | 20   
7350267663 | 1              | 1      | 0   | 0    | 2    
735549280  | 0              | 1      | 1   | 2    | 4    
7538978023 | 5              | 7      | 3   | 5    | 20   
7846643371 | 4              | 4      | 6   | 6    | 20   
8061692817 | 5              | 5      | 4   | 6    | 20   
8462571435 | 9              | 2      | 5   | 4    | 20   
8646405925 | 5              | 8      | 5   | 2    | 20   
8817789231 | 5              | 4      | 2   | 3    | 14   
```

## Missing Values
```
column            | missing_count | missing_percent
----------------- | ------------- | ---------------
selected_use_case | 263           | 100.0          
```

## Invalid Ratings
```
No rows.
```

## Incomplete Participants
```
participant_id | n_trials | complete_by_observed_max
-------------- | -------- | ------------------------
260636777      | 19       | False                   
513223685      | 4        | False                   
7350267663     | 2        | False                   
735549280      | 4        | False                   
8817789231     | 14       | False                   
```

## Phase 1 Descriptive Statistics
These are descriptive summaries only. They compare observed rating patterns but do not test whether differences are statistically significant.
Use wording such as higher descriptive mean, lower descriptive mean, or similar ratings.

## Phase 1 Trial-Level Descriptives
```
condition      | dimension   | n_trials | n_participants | mean  | sd    | median | iqr  | ci95_low | ci95_high
-------------- | ----------- | -------- | -------------- | ----- | ----- | ------ | ---- | -------- | ---------
COUNTERFACTUAL | Clarity     | 66       | 14             | 3.697 | 1.277 | 4.0    | 2.0  | 3.389    | 4.005    
COUNTERFACTUAL | Correctness | 66       | 14             | 3.576 | 1.11  | 4.0    | 1.0  | 3.308    | 3.844    
COUNTERFACTUAL | Helpfulness | 66       | 14             | 3.682 | 1.152 | 4.0    | 2.0  | 3.404    | 3.96     
COUNTERFACTUAL | Trust       | 66       | 14             | 3.5   | 1.154 | 4.0    | 1.0  | 3.222    | 3.778    
HYBRID         | Clarity     | 63       | 16             | 3.905 | 1.241 | 4.0    | 2.0  | 3.598    | 4.211    
HYBRID         | Correctness | 63       | 16             | 3.889 | 1.123 | 4.0    | 2.0  | 3.612    | 4.166    
HYBRID         | Helpfulness | 63       | 16             | 3.683 | 1.162 | 4.0    | 2.0  | 3.396    | 3.969    
HYBRID         | Trust       | 63       | 16             | 3.651 | 1.124 | 4.0    | 1.0  | 3.373    | 3.928    
RAG            | Clarity     | 64       | 15             | 4.109 | 1.183 | 4.0    | 1.0  | 3.819    | 4.399    
RAG            | Correctness | 64       | 15             | 3.875 | 1.228 | 4.0    | 2.0  | 3.574    | 4.176    
RAG            | Helpfulness | 64       | 15             | 3.656 | 1.211 | 4.0    | 1.25 | 3.359    | 3.953    
RAG            | Trust       | 64       | 15             | 3.672 | 1.235 | 4.0    | 2.0  | 3.369    | 3.974    
SHAP           | Clarity     | 70       | 15             | 3.771 | 1.265 | 4.0    | 2.0  | 3.475    | 4.068    
SHAP           | Correctness | 70       | 15             | 3.671 | 1.151 | 4.0    | 1.0  | 3.402    | 3.941    
SHAP           | Helpfulness | 70       | 15             | 3.614 | 1.067 | 4.0    | 1.0  | 3.364    | 3.864    
SHAP           | Trust       | 70       | 15             | 3.643 | 1.064 | 4.0    | 1.0  | 3.394    | 3.892    
```

## Phase 1 Participant-Level Means
```
participant_id | condition      | dimension   | n_trials | mean 
-------------- | -------------- | ----------- | -------- | -----
1441767514     | COUNTERFACTUAL | Clarity     | 6        | 3.667
1441767514     | COUNTERFACTUAL | Correctness | 6        | 3.833
1441767514     | COUNTERFACTUAL | Helpfulness | 6        | 3.833
1441767514     | COUNTERFACTUAL | Trust       | 6        | 3.167
1441767514     | HYBRID         | Clarity     | 5        | 3.8  
1441767514     | HYBRID         | Correctness | 5        | 4.0  
1441767514     | HYBRID         | Helpfulness | 5        | 3.6  
1441767514     | HYBRID         | Trust       | 5        | 3.6  
1441767514     | RAG            | Clarity     | 7        | 4.571
1441767514     | RAG            | Correctness | 7        | 4.286
1441767514     | RAG            | Helpfulness | 7        | 4.429
1441767514     | RAG            | Trust       | 7        | 4.0  
1441767514     | SHAP           | Clarity     | 2        | 4.5  
1441767514     | SHAP           | Correctness | 2        | 5.0  
1441767514     | SHAP           | Helpfulness | 2        | 4.5  
1441767514     | SHAP           | Trust       | 2        | 4.0  
260636777      | COUNTERFACTUAL | Clarity     | 4        | 2.5  
260636777      | COUNTERFACTUAL | Correctness | 4        | 3.5  
260636777      | COUNTERFACTUAL | Helpfulness | 4        | 4.0  
260636777      | COUNTERFACTUAL | Trust       | 4        | 3.25 
260636777      | HYBRID         | Clarity     | 5        | 4.2  
260636777      | HYBRID         | Correctness | 5        | 3.8  
260636777      | HYBRID         | Helpfulness | 5        | 3.4  
260636777      | HYBRID         | Trust       | 5        | 3.8  
260636777      | RAG            | Clarity     | 3        | 4.0  
260636777      | RAG            | Correctness | 3        | 3.333
260636777      | RAG            | Helpfulness | 3        | 4.333
260636777      | RAG            | Trust       | 3        | 4.333
260636777      | SHAP           | Clarity     | 7        | 3.286
260636777      | SHAP           | Correctness | 7        | 3.714
... 210 more rows not shown
```

## Phase 1 Figures
- /Users/arijeet/Documents/Study Material/Fourth_Semeter/Master_thesis/Explainable_Model/explainableDepressionPrediction_mcp_server/analysis/figures/phase1_task2_rating_distributions.svg
- /Users/arijeet/Documents/Study Material/Fourth_Semeter/Master_thesis/Explainable_Model/explainableDepressionPrediction_mcp_server/analysis/figures/phase1_task2_descriptive_ci.svg

## Phase 1 Statistical Analysis
Primary analysis uses trial-level linear mixed-effects models with a random intercept for participant ID.
Each rating dimension is tested separately. The overall explanation-type effect is tested first.
Pairwise comparisons use Holm correction and are run only for dimensions where the overall explanation-type p-value is below 0.05.
Mean differences are model-estimated differences on the 1-5 rating scale. Positive values mean the first explanation type has the higher estimated rating.

## Phase 1 Result Summary
Primary mixed-model overall tests showed evidence of an explanation-type effect for: Clarity (p=0.047985).
For dimensions that passed the overall-test gate, no pairwise comparison remained below 0.05 after Holm correction.
The secondary participant-level complete-case check showed evidence for Correctness (p=0.008906). This is a robustness check and should not override the primary trial-level mixed model.
Some model fits reported a random-effects covariance warning. The models converged, but this should be mentioned as a small-sample or boundary-model caution.

## Primary Overall Mixed-Model Tests
```
dimension   | method                                            | model                                         | n_trials | n_participants | lr_chi2 | df | p_value  | residual_sd | participant_intercept_variance | converged | pairwise_rule                                    
----------- | ------------------------------------------------- | --------------------------------------------- | -------- | -------------- | ------- | -- | -------- | ----------- | ------------------------------ | --------- | -------------------------------------------------
Clarity     | Linear mixed-effects model, likelihood-ratio test | rating ~ explanation_type + (1 | participant) | 263      | 16             | 7.9065  | 3  | 0.047985 | 0.6913      | 0.9815                         | True      | Pairwise comparisons run only if overall p < 0.05
Correctness | Linear mixed-effects model, likelihood-ratio test | rating ~ explanation_type + (1 | participant) | 263      | 16             | 7.5972  | 3  | 0.055113 | 0.8536      | 0.5737                         | True      | Pairwise comparisons run only if overall p < 0.05
Helpfulness | Linear mixed-effects model, likelihood-ratio test | rating ~ explanation_type + (1 | participant) | 263      | 16             | 1.1022  | 3  | 0.77655  | 0.7785      | 0.6682                         | True      | Pairwise comparisons run only if overall p < 0.05
Trust       | Linear mixed-effects model, likelihood-ratio test | rating ~ explanation_type + (1 | participant) | 263      | 16             | 4.3758  | 3  | 0.223644 | 0.8448      | 0.6269                         | True      | Pairwise comparisons run only if overall p < 0.05
```

## Primary Pairwise Comparisons With Holm Correction
```
dimension | comparison              | mean_difference | ci95_low | ci95_high | raw_p_value | holm_adjusted_p_value | effect_size_metric                              | effect_size
--------- | ----------------------- | --------------- | -------- | --------- | ----------- | --------------------- | ----------------------------------------------- | -----------
Clarity   | SHAP - COUNTERFACTUAL   | 0.1921          | -0.0478  | 0.4319    | 0.116554    | 0.466216              | standardized difference using model residual SD | 0.2778     
Clarity   | SHAP - RAG              | -0.1168         | -0.3552  | 0.1217    | 0.33718     | 1.0                   | standardized difference using model residual SD | -0.1689    
Clarity   | SHAP - HYBRID           | -0.1032         | -0.3436  | 0.1373    | 0.400496    | 1.0                   | standardized difference using model residual SD | -0.1492    
Clarity   | COUNTERFACTUAL - RAG    | -0.3088         | -0.5502  | -0.0674   | 0.012152    | 0.072912              | standardized difference using model residual SD | -0.4467    
Clarity   | COUNTERFACTUAL - HYBRID | -0.2952         | -0.5383  | -0.0521   | 0.017323    | 0.086615              | standardized difference using model residual SD | -0.427     
Clarity   | RAG - HYBRID            | 0.0136          | -0.2308  | 0.258     | 0.913109    | 1.0                   | standardized difference using model residual SD | 0.0197     
```

## Pairwise Comparisons Not Run
```
dimension   | overall_p_value | reason                                                                                             
----------- | --------------- | ---------------------------------------------------------------------------------------------------
Correctness | 0.055113        | Overall explanation-type p-value was not below 0.05, so post-hoc pairwise comparisons were not run.
Helpfulness | 0.77655         | Overall explanation-type p-value was not below 0.05, so post-hoc pairwise comparisons were not run.
Trust       | 0.223644        | Overall explanation-type p-value was not below 0.05, so post-hoc pairwise comparisons were not run.
```

## Secondary Participant-Level Analysis
This check averages ratings within each participant and explanation type first.
Participants are not forced into conditions they never rated. Complete-case repeated comparisons use only participants with means for all four explanation types.

## Participant-Level Friedman Tests
```
dimension   | method                                                     | n_participants | df | chi2    | p_value  | effect_size_metric | effect_size | interpretation_note                                                                             
----------- | ---------------------------------------------------------- | -------------- | -- | ------- | -------- | ------------------ | ----------- | ------------------------------------------------------------------------------------------------
Clarity     | Friedman repeated-measures test on participant-level means | 13             | 3  | 5.0168  | 0.170571 | Kendall's W        | 0.1286      | Secondary complete-case robustness check; primary inference remains the trial-level mixed model.
Correctness | Friedman repeated-measures test on participant-level means | 13             | 3  | 11.5952 | 0.008906 | Kendall's W        | 0.2973      | Secondary complete-case robustness check; primary inference remains the trial-level mixed model.
Helpfulness | Friedman repeated-measures test on participant-level means | 13             | 3  | 3.1667  | 0.366635 | Kendall's W        | 0.0812      | Secondary complete-case robustness check; primary inference remains the trial-level mixed model.
Trust       | Friedman repeated-measures test on participant-level means | 13             | 3  | 4.5984  | 0.203683 | Kendall's W        | 0.1179      | Secondary complete-case robustness check; primary inference remains the trial-level mixed model.
```

## Participant-Level Completeness Notes
```
dimension   | complete_participants_used | participants_excluded_due_to_missing_condition | excluded_participant_ids       | note                                              
----------- | -------------------------- | ---------------------------------------------- | ------------------------------ | --------------------------------------------------
Clarity     | 13                         | 3                                              | 513223685;7350267663;735549280 | No missing condition means were filled or imputed.
Correctness | 13                         | 3                                              | 513223685;7350267663;735549280 | No missing condition means were filled or imputed.
Helpfulness | 13                         | 3                                              | 513223685;7350267663;735549280 | No missing condition means were filled or imputed.
Trust       | 13                         | 3                                              | 513223685;7350267663;735549280 | No missing condition means were filled or imputed.
```

## Model Notes
```
dimension   | note                                 
----------- | -------------------------------------
Correctness | Random effects covariance is singular
Trust       | Random effects covariance is singular
```

## Stop Point
Task 4 is complete. No Phase 2 statistical tests were run.
