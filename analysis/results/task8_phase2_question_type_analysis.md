# Task 8 - Phase 2 Question-Type Analysis

Generated: 2026-08-30T23:51:31

This report examines whether the Agentic XAI versus MentaLLaMA difference depends on question type.

## Analysis Plan
First, ratings are summarized for each system x question-type cell.
Then an exploratory mixed-effects interaction model is run for each rating dimension.
The interaction test asks whether the system difference changes across SHAP, Counterfactual, RAG, and Hybrid questions.
This is secondary to the Task 6 primary Phase 2 comparison.

## Phase 2 Data Inspection
- Rows/trials: 107
- Participants: 14
- Sessions: 14
- Trials per participant: min=3, median=8.0, mean=7.64, max=8
- Incomplete participants by observed maximum trial count: 1
- Exact duplicate rows: 0
- Repeated participant/session/trial-number keys: 0
- Invalid rating cells: 0
- Rating concept mapping: rating_answered=Helpfulness, rating_supported=Correctness, rating_understandable=Clarity, rating_confidence=Trust.
- Important interpretation: rating_confidence is participant trust in the explanation, not model prediction confidence.

## System Counts
```
explanation_system | n_trials
------------------ | --------
agentic_xai        | 53      
mentallama         | 54      
```

## Assigned System Counts
```
assigned_system | n_trials
--------------- | --------
agentic_xai     | 53      
mentallama      | 54      
```

## Severity Counts
```
severity | n_trials
-------- | --------
moderate | 34      
none     | 37      
severe   | 36      
```

## Question Type Counts
```
question_type  | n_trials
-------------- | --------
counterfactual | 27      
hybrid         | 27      
rag            | 26      
shap           | 27      
```

## Participant x System
```
participant_id | agentic_xai | mentallama | total
-------------- | ----------- | ---------- | -----
2055091951     | 4           | 4          | 8    
5480572671     | 4           | 4          | 8    
6283885353     | 4           | 4          | 8    
6436516771     | 4           | 4          | 8    
6440073647     | 4           | 4          | 8    
6561678593     | 4           | 4          | 8    
6779809309     | 4           | 4          | 8    
7050518746     | 4           | 4          | 8    
7185297299     | 4           | 4          | 8    
7679825905     | 1           | 2          | 3    
8312873693     | 4           | 4          | 8    
8407161622     | 4           | 4          | 8    
8462571435     | 4           | 4          | 8    
8940144363     | 4           | 4          | 8    
```

## System x Question Type
```
explanation_system | counterfactual | hybrid | rag | shap | total
------------------ | -------------- | ------ | --- | ---- | -----
agentic_xai        | 14             | 13     | 13  | 13   | 53   
mentallama         | 13             | 14     | 13  | 14   | 54   
```

## System x Severity
```
explanation_system | moderate | none | severe | total
------------------ | -------- | ---- | ------ | -----
agentic_xai        | 14       | 20   | 19     | 53   
mentallama         | 20       | 17   | 17     | 54   
```

## Question Type x Severity
```
question_type  | moderate | none | severe | total
-------------- | -------- | ---- | ------ | -----
counterfactual | 7        | 13   | 7      | 27   
hybrid         | 9        | 9    | 9      | 27   
rag            | 7        | 8    | 11     | 26   
shap           | 11       | 7    | 9      | 27   
```

## Missing Values
```
No rows.
```

## Invalid Ratings
```
No rows.
```

## Incomplete Participants
```
participant_id | n_trials | complete_by_observed_max
-------------- | -------- | ------------------------
7679825905     | 3        | False                   
```

## Phase 2 Descriptive Statistics
These are descriptive summaries only. They compare observed rating patterns but do not test whether differences are statistically significant.
Mean difference is Agentic XAI mean minus MentaLLaMA mean. Positive values mean Agentic XAI has the higher descriptive mean; negative values mean MentaLLaMA has the higher descriptive mean.
rating_confidence is treated as Trust in the explanation, not model prediction confidence.

## Phase 2 Trial-Level Descriptives
```
condition   | dimension   | n_trials | n_participants | mean  | sd    | median | iqr | ci95_low | ci95_high
----------- | ----------- | -------- | -------------- | ----- | ----- | ------ | --- | -------- | ---------
agentic_xai | Helpfulness | 53       | 14             | 3.736 | 1.112 | 4.0    | 1.0 | 3.436    | 4.035    
agentic_xai | Correctness | 53       | 14             | 3.943 | 0.969 | 4.0    | 1.0 | 3.683    | 4.204    
agentic_xai | Clarity     | 53       | 14             | 3.981 | 0.888 | 4.0    | 1.0 | 3.742    | 4.22     
agentic_xai | Trust       | 53       | 14             | 3.623 | 1.096 | 4.0    | 1.0 | 3.328    | 3.918    
mentallama  | Helpfulness | 54       | 14             | 3.759 | 1.098 | 4.0    | 0.0 | 3.466    | 4.052    
mentallama  | Correctness | 54       | 14             | 3.63  | 1.263 | 4.0    | 2.0 | 3.293    | 3.967    
mentallama  | Clarity     | 54       | 14             | 3.833 | 0.906 | 4.0    | 0.0 | 3.592    | 4.075    
mentallama  | Trust       | 54       | 14             | 3.463 | 1.342 | 4.0    | 2.0 | 3.105    | 3.821    
```

## Agentic XAI Mean Minus MentaLLaMA Mean
```
dimension   | agentic_xai_mean | mentallama_mean | mean_difference
----------- | ---------------- | --------------- | ---------------
Clarity     | 3.981            | 3.833           | 0.148          
Correctness | 3.943            | 3.63            | 0.313          
Helpfulness | 3.736            | 3.759           | -0.023         
Trust       | 3.623            | 3.463           | 0.16           
```

## Phase 2 Participant-Level Paired Means
```
participant_id | dimension   | agentic_xai_mean | mentallama_mean | mean_difference
-------------- | ----------- | ---------------- | --------------- | ---------------
2055091951     | Clarity     | 3.75             | 4.5             | -0.75          
2055091951     | Correctness | 4.75             | 5.0             | -0.25          
2055091951     | Helpfulness | 4.25             | 4.75            | -0.5           
2055091951     | Trust       | 4.0              | 4.5             | -0.5           
5480572671     | Clarity     | 3.75             | 4.75            | -1.0           
5480572671     | Correctness | 4.25             | 4.75            | -0.5           
5480572671     | Helpfulness | 3.75             | 4.75            | -1.0           
5480572671     | Trust       | 3.0              | 4.0             | -1.0           
6283885353     | Clarity     | 4.0              | 4.0             | 0.0            
6283885353     | Correctness | 4.0              | 2.75            | 1.25           
6283885353     | Helpfulness | 3.75             | 3.25            | 0.5            
6283885353     | Trust       | 3.75             | 2.5             | 1.25           
6436516771     | Clarity     | 4.25             | 4.5             | -0.25          
6436516771     | Correctness | 3.25             | 3.0             | 0.25           
6436516771     | Helpfulness | 3.5              | 3.75            | -0.25          
6436516771     | Trust       | 3.75             | 4.25            | -0.5           
6440073647     | Clarity     | 4.0              | 3.5             | 0.5            
6440073647     | Correctness | 4.0              | 2.75            | 1.25           
6440073647     | Helpfulness | 3.75             | 2.75            | 1.0            
6440073647     | Trust       | 3.75             | 2.5             | 1.25           
6561678593     | Clarity     | 4.25             | 3.0             | 1.25           
6561678593     | Correctness | 3.25             | 4.0             | -0.75          
6561678593     | Helpfulness | 3.25             | 4.0             | -0.75          
6561678593     | Trust       | 3.5              | 4.25            | -0.75          
6779809309     | Clarity     | 3.0              | 3.25            | -0.25          
6779809309     | Correctness | 3.5              | 2.25            | 1.25           
6779809309     | Helpfulness | 2.75             | 2.5             | 0.25           
6779809309     | Trust       | 3.5              | 2.5             | 1.0            
7050518746     | Clarity     | 3.0              | 3.5             | -0.5           
7050518746     | Correctness | 4.0              | 3.5             | 0.5            
... 26 more rows not shown
```

## Phase 2 Participant-Level Means Long Format
```
participant_id | condition   | dimension   | n_trials | mean
-------------- | ----------- | ----------- | -------- | ----
2055091951     | agentic_xai | Helpfulness | 4        | 4.25
2055091951     | agentic_xai | Correctness | 4        | 4.75
2055091951     | agentic_xai | Clarity     | 4        | 3.75
2055091951     | agentic_xai | Trust       | 4        | 4.0 
2055091951     | mentallama  | Helpfulness | 4        | 4.75
2055091951     | mentallama  | Correctness | 4        | 5.0 
2055091951     | mentallama  | Clarity     | 4        | 4.5 
2055091951     | mentallama  | Trust       | 4        | 4.5 
5480572671     | agentic_xai | Helpfulness | 4        | 3.75
5480572671     | agentic_xai | Correctness | 4        | 4.25
5480572671     | agentic_xai | Clarity     | 4        | 3.75
5480572671     | agentic_xai | Trust       | 4        | 3.0 
5480572671     | mentallama  | Helpfulness | 4        | 4.75
5480572671     | mentallama  | Correctness | 4        | 4.75
5480572671     | mentallama  | Clarity     | 4        | 4.75
5480572671     | mentallama  | Trust       | 4        | 4.0 
6283885353     | agentic_xai | Helpfulness | 4        | 3.75
6283885353     | agentic_xai | Correctness | 4        | 4.0 
6283885353     | agentic_xai | Clarity     | 4        | 4.0 
6283885353     | agentic_xai | Trust       | 4        | 3.75
6283885353     | mentallama  | Helpfulness | 4        | 3.25
6283885353     | mentallama  | Correctness | 4        | 2.75
6283885353     | mentallama  | Clarity     | 4        | 4.0 
6283885353     | mentallama  | Trust       | 4        | 2.5 
6436516771     | agentic_xai | Helpfulness | 4        | 3.5 
6436516771     | agentic_xai | Correctness | 4        | 3.25
6436516771     | agentic_xai | Clarity     | 4        | 4.25
6436516771     | agentic_xai | Trust       | 4        | 3.75
6436516771     | mentallama  | Helpfulness | 4        | 3.75
6436516771     | mentallama  | Correctness | 4        | 3.0 
... 82 more rows not shown
```

## Phase 2 Figures
- /Users/arijeet/Documents/Study Material/Fourth_Semeter/Master_thesis/Explainable_Model/explainableDepressionPrediction_mcp_server/analysis/figures/phase2_task2_rating_distributions.svg
- /Users/arijeet/Documents/Study Material/Fourth_Semeter/Master_thesis/Explainable_Model/explainableDepressionPrediction_mcp_server/analysis/figures/phase2_task2_descriptive_ci.svg
- /Users/arijeet/Documents/Study Material/Fourth_Semeter/Master_thesis/Explainable_Model/explainableDepressionPrediction_mcp_server/analysis/figures/phase2_task2_participant_paired_means.svg

## Phase 2 Primary Statistical Analysis
This is the main Phase 2 thesis comparison: Agentic XAI versus MentaLLaMA.
The analysis uses trial-level linear mixed-effects models, one per rating dimension, with participant ID as a random intercept.
The estimated difference is Agentic XAI minus MentaLLaMA on the 1-5 rating scale. Positive values favor Agentic XAI descriptively; negative values favor MentaLLaMA descriptively.
Holm correction is applied across the four primary outcomes.

## Task 6 Result Summary
After Holm correction across the four primary outcomes, there was insufficient statistical evidence that participants rated Agentic XAI differently from MentaLLaMA.
For Helpfulness, Agentic XAI received a lower descriptive rating, but there was insufficient statistical evidence of a difference.
For Correctness, Agentic XAI received a higher descriptive rating, but there was insufficient statistical evidence of a difference.
For Clarity, Agentic XAI received a higher descriptive rating, but there was insufficient statistical evidence of a difference.
For Trust, Agentic XAI received a higher descriptive rating, but there was insufficient statistical evidence of a difference.
The mixed models converged, but random-effects covariance warnings occurred; mention this as a small-sample/boundary-model caution.

## Primary Mixed-Model Results
```
dimension   | agentic_xai_descriptive_mean | mentallama_descriptive_mean | estimated_difference_agentic_minus_mentallama | ci95_low | ci95_high | raw_p_value | holm_adjusted_p_value | effect_size_metric                              | effect_size | n_trials | n_participants | converged | model                                          
----------- | ---------------------------- | --------------------------- | --------------------------------------------- | -------- | --------- | ----------- | --------------------- | ----------------------------------------------- | ----------- | -------- | -------------- | --------- | -----------------------------------------------
Helpfulness | 3.736                        | 3.759                       | -0.0159                                       | -0.4035  | 0.3717    | 0.935991    | 1.0                   | standardized difference using model residual SD | -0.0155     | 107      | 14             | True      | rating ~ explanation_system + (1 | participant)
Correctness | 3.943                        | 3.63                        | 0.3218                                        | -0.0539  | 0.6975    | 0.09316     | 0.37264               | standardized difference using model residual SD | 0.3249      | 107      | 14             | True      | rating ~ explanation_system + (1 | participant)
Clarity     | 3.981                        | 3.833                       | 0.1482                                        | -0.1739  | 0.4704    | 0.367168    | 1.0                   | standardized difference using model residual SD | 0.1744      | 107      | 14             | True      | rating ~ explanation_system + (1 | participant)
Trust       | 3.623                        | 3.463                       | 0.1678                                        | -0.2271  | 0.5627    | 0.404926    | 1.0                   | standardized difference using model residual SD | 0.1612      | 107      | 14             | True      | rating ~ explanation_system + (1 | participant)
```

## Model Notes
```
dimension   | note                                 
----------- | -------------------------------------
Helpfulness | Random effects covariance is singular
Correctness | Random effects covariance is singular
Clarity     | Random effects covariance is singular
Trust       | Random effects covariance is singular
```

## Phase 2 Question-Type Analysis
This is a secondary analysis asking whether the Agentic XAI versus MentaLLaMA difference depends on question type.
Question types are SHAP, Counterfactual, RAG, and Hybrid.
The interaction model compares an additive model with system and question type to a model that also includes system x question type.
Individual question-type cells are small, so subgroup patterns should be treated as exploratory.

## Task 8 Result Summary
The smallest system x question-type subgroup has 13 trials from 13 participants.
The exploratory interaction models did not show evidence below 0.05 that the Agentic XAI versus MentaLLaMA difference depended on question type.
Therefore, these results do not provide clear statistical evidence that Agentic XAI's tool selection was particularly useful for one specific question type.
Descriptive Agentic XAI minus MentaLLaMA gaps for Helpfulness: SHAP +0.220, Counterfactual -0.165, RAG +0.154, Hybrid -0.237.
Descriptive Agentic XAI minus MentaLLaMA gaps for Correctness: SHAP +0.352, Counterfactual +0.412, RAG +0.385, Hybrid +0.132.
Descriptive Agentic XAI minus MentaLLaMA gaps for Clarity: SHAP +0.071, Counterfactual +0.472, RAG +0.154, Hybrid -0.083.
Descriptive Agentic XAI minus MentaLLaMA gaps for Trust: SHAP -0.033, Counterfactual +0.577, RAG +0.077, Hybrid +0.033.
Some model fits produced warnings; see the model notes table before using this exploratory analysis in the thesis.

## System x Question Type Cell Support
```
system      | question_type  | n_trials | n_participants
----------- | -------------- | -------- | --------------
mentallama  | SHAP           | 14       | 14            
mentallama  | Counterfactual | 13       | 13            
mentallama  | RAG            | 13       | 13            
mentallama  | Hybrid         | 14       | 14            
agentic_xai | SHAP           | 13       | 13            
agentic_xai | Counterfactual | 14       | 14            
agentic_xai | RAG            | 13       | 13            
agentic_xai | Hybrid         | 13       | 13            
```

## System x Question Type Descriptives
```
system      | question_type  | dimension   | n_trials | n_participants | mean  | sd    | median | iqr  | ci95_low | ci95_high
----------- | -------------- | ----------- | -------- | -------------- | ----- | ----- | ------ | ---- | -------- | ---------
mentallama  | SHAP           | Helpfulness | 14       | 14             | 3.857 | 0.949 | 4.0    | 0.0  | 3.36     | 4.354    
mentallama  | SHAP           | Correctness | 14       | 14             | 3.571 | 1.342 | 4.0    | 2.5  | 2.868    | 4.275    
mentallama  | SHAP           | Clarity     | 14       | 14             | 3.929 | 0.829 | 4.0    | 0.0  | 3.494    | 4.363    
mentallama  | SHAP           | Trust       | 14       | 14             | 3.571 | 1.453 | 4.0    | 2.25 | 2.811    | 4.332    
mentallama  | Counterfactual | Helpfulness | 13       | 13             | 3.308 | 1.182 | 4.0    | 2.0  | 2.665    | 3.95     
mentallama  | Counterfactual | Correctness | 13       | 13             | 3.231 | 1.092 | 3.0    | 1.0  | 2.637    | 3.824    
mentallama  | Counterfactual | Clarity     | 13       | 13             | 3.385 | 1.044 | 4.0    | 2.0  | 2.817    | 3.952    
mentallama  | Counterfactual | Trust       | 13       | 13             | 2.923 | 1.188 | 3.0    | 2.0  | 2.278    | 3.569    
mentallama  | RAG            | Helpfulness | 13       | 13             | 3.923 | 1.115 | 4.0    | 1.0  | 3.317    | 4.529    
mentallama  | RAG            | Correctness | 13       | 13             | 4.0   | 1.155 | 4.0    | 1.0  | 3.372    | 4.628    
mentallama  | RAG            | Clarity     | 13       | 13             | 4.077 | 0.641 | 4.0    | 0.0  | 3.729    | 4.425    
mentallama  | RAG            | Trust       | 13       | 13             | 3.923 | 1.32  | 4.0    | 2.0  | 3.205    | 4.641    
mentallama  | Hybrid         | Helpfulness | 14       | 14             | 3.929 | 1.141 | 4.0    | 0.75 | 3.331    | 4.526    
mentallama  | Hybrid         | Correctness | 14       | 14             | 3.714 | 1.437 | 4.0    | 1.75 | 2.961    | 4.467    
mentallama  | Hybrid         | Clarity     | 14       | 14             | 3.929 | 0.997 | 4.0    | 0.0  | 3.406    | 4.451    
mentallama  | Hybrid         | Trust       | 14       | 14             | 3.429 | 1.342 | 4.0    | 1.5  | 2.725    | 4.132    
agentic_xai | SHAP           | Helpfulness | 13       | 13             | 4.077 | 1.038 | 4.0    | 1.0  | 3.513    | 4.641    
agentic_xai | SHAP           | Correctness | 13       | 13             | 3.923 | 1.188 | 4.0    | 1.0  | 3.278    | 4.569    
agentic_xai | SHAP           | Clarity     | 13       | 13             | 4.0   | 0.913 | 4.0    | 1.0  | 3.504    | 4.496    
agentic_xai | SHAP           | Trust       | 13       | 13             | 3.538 | 1.127 | 4.0    | 1.0  | 2.926    | 4.151    
agentic_xai | Counterfactual | Helpfulness | 14       | 14             | 3.143 | 1.351 | 3.0    | 1.0  | 2.435    | 3.85     
agentic_xai | Counterfactual | Correctness | 14       | 14             | 3.643 | 0.842 | 4.0    | 0.75 | 3.202    | 4.084    
agentic_xai | Counterfactual | Clarity     | 14       | 14             | 3.857 | 0.949 | 4.0    | 0.0  | 3.36     | 4.354    
agentic_xai | Counterfactual | Trust       | 14       | 14             | 3.5   | 1.225 | 4.0    | 1.5  | 2.858    | 4.142    
agentic_xai | RAG            | Helpfulness | 13       | 13             | 4.077 | 0.494 | 4.0    | 0.0  | 3.809    | 4.345    
agentic_xai | RAG            | Correctness | 13       | 13             | 4.385 | 0.65  | 4.0    | 1.0  | 4.031    | 4.738    
agentic_xai | RAG            | Clarity     | 13       | 13             | 4.231 | 0.725 | 4.0    | 1.0  | 3.837    | 4.625    
agentic_xai | RAG            | Trust       | 13       | 13             | 4.0   | 1.08  | 4.0    | 1.0  | 3.413    | 4.587    
agentic_xai | Hybrid         | Helpfulness | 13       | 13             | 3.692 | 1.182 | 4.0    | 2.0  | 3.05     | 4.335    
agentic_xai | Hybrid         | Correctness | 13       | 13             | 3.846 | 1.068 | 4.0    | 2.0  | 3.265    | 4.427    
... 2 more rows not shown
```

## Exploratory System x Question Type Interaction Tests
```
dimension   | method                                                    | model_comparison                                 | n_trials | n_participants | lr_chi2 | df | p_value  | converged | interpretation_note                                                            
----------- | --------------------------------------------------------- | ------------------------------------------------ | -------- | -------------- | ------- | -- | -------- | --------- | -------------------------------------------------------------------------------
Helpfulness | Exploratory mixed-model interaction likelihood-ratio test | system + question_type vs system * question_type | 107      | 14             | 1.2507  | 3  | 0.740881 | True      | Secondary/exploratory; do not overinterpret individual question-type subgroups.
Correctness | Exploratory mixed-model interaction likelihood-ratio test | system + question_type vs system * question_type | 107      | 14             | 0.2545  | 3  | 0.968338 | True      | Secondary/exploratory; do not overinterpret individual question-type subgroups.
Clarity     | Exploratory mixed-model interaction likelihood-ratio test | system + question_type vs system * question_type | 107      | 14             | 1.6386  | 3  | 0.650662 | True      | Secondary/exploratory; do not overinterpret individual question-type subgroups.
Trust       | Exploratory mixed-model interaction likelihood-ratio test | system + question_type vs system * question_type | 107      | 14             | 1.2394  | 3  | 0.743579 | True      | Secondary/exploratory; do not overinterpret individual question-type subgroups.
```

## Task 8 Model Notes
```
dimension   | note                                 
----------- | -------------------------------------
Helpfulness | Random effects covariance is singular
Correctness | Random effects covariance is singular
Clarity     | Random effects covariance is singular
Trust       | Random effects covariance is singular
```

## Task 8 Figure
- /Users/arijeet/Documents/Study Material/Fourth_Semeter/Master_thesis/Explainable_Model/explainableDepressionPrediction_mcp_server/analysis/figures/phase2_task8_system_by_question_type_interaction.svg

## Stop Point
Task 8 is complete. No further analyses were run.
