# Task 9 - Phase 2 Severity Analysis

Generated: 2026-08-30T23:51:31

This report examines whether the Agentic XAI versus MentaLLaMA difference depends on passage severity.

## Analysis Plan
First, ratings are summarized for each system x severity cell.
Then an exploratory mixed-effects interaction model is run for each rating dimension.
The interaction test asks whether the system difference changes across no depression, moderate, and severe passages.
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

## Phase 2 Severity Analysis
This is a secondary analysis asking whether the Agentic XAI versus MentaLLaMA difference depends on passage severity.
Severity is reported as no depression, moderate, and severe. The raw Phase 2 label none is reported as no depression here for consistency with the thesis wording.
The interaction model compares an additive model with system and severity to a model that also includes system x severity.
Individual severity subgroups are small, so subgroup patterns should not be overstated.

## Task 9 Result Summary
The smallest system x severity subgroup has 14 trials from 9 participants.
Because every subgroup has at least 10 trials, the exploratory system x severity model was run.
The exploratory interaction model showed evidence below 0.05 for: Correctness (p=0.04198), Clarity (p=0.006404), Trust (p=0.000204). Interpret this cautiously because severity subgroups are small.
Descriptive Agentic XAI minus MentaLLaMA gaps for Helpfulness: no depression +0.665, moderate -0.064, severe -0.650.
Descriptive Agentic XAI minus MentaLLaMA gaps for Correctness: no depression +1.109, moderate +0.000, severe -0.093.
Descriptive Agentic XAI minus MentaLLaMA gaps for Clarity: no depression +0.897, moderate -0.086, severe -0.458.
Descriptive Agentic XAI minus MentaLLaMA gaps for Trust: no depression +1.371, moderate -0.807, severe -0.140.
Some model fits produced warnings; see the model notes table before using this exploratory analysis in the thesis.

## System x Severity Cell Support
```
system      | severity      | n_trials | n_participants
----------- | ------------- | -------- | --------------
mentallama  | no depression | 17       | 12            
mentallama  | moderate      | 20       | 12            
mentallama  | severe        | 17       | 10            
agentic_xai | no depression | 20       | 14            
agentic_xai | moderate      | 14       | 9             
agentic_xai | severe        | 19       | 10            
```

## System x Severity Descriptives
```
system      | severity      | dimension   | n_trials | n_participants | mean  | sd    | median | iqr  | ci95_low | ci95_high
----------- | ------------- | ----------- | -------- | -------------- | ----- | ----- | ------ | ---- | -------- | ---------
mentallama  | no depression | Helpfulness | 17       | 12             | 3.235 | 1.437 | 4.0    | 2.0  | 2.552    | 3.919    
mentallama  | no depression | Correctness | 17       | 12             | 2.941 | 1.6   | 4.0    | 3.0  | 2.181    | 3.702    
mentallama  | no depression | Clarity     | 17       | 12             | 3.353 | 0.996 | 4.0    | 1.0  | 2.879    | 3.827    
mentallama  | no depression | Trust       | 17       | 12             | 2.529 | 1.546 | 2.0    | 3.0  | 1.795    | 3.264    
mentallama  | moderate      | Helpfulness | 20       | 12             | 3.85  | 0.671 | 4.0    | 0.0  | 3.556    | 4.144    
mentallama  | moderate      | Correctness | 20       | 12             | 4.0   | 0.725 | 4.0    | 0.5  | 3.682    | 4.318    
mentallama  | moderate      | Clarity     | 20       | 12             | 3.8   | 0.894 | 4.0    | 0.0  | 3.408    | 4.192    
mentallama  | moderate      | Trust       | 20       | 12             | 3.95  | 0.826 | 4.0    | 0.0  | 3.588    | 4.312    
mentallama  | severe        | Helpfulness | 17       | 10             | 4.176 | 0.951 | 4.0    | 1.0  | 3.724    | 4.629    
mentallama  | severe        | Correctness | 17       | 10             | 3.882 | 1.166 | 4.0    | 2.0  | 3.328    | 4.437    
mentallama  | severe        | Clarity     | 17       | 10             | 4.353 | 0.493 | 4.0    | 1.0  | 4.119    | 4.587    
mentallama  | severe        | Trust       | 17       | 10             | 3.824 | 1.185 | 4.0    | 2.0  | 3.26     | 4.387    
agentic_xai | no depression | Helpfulness | 20       | 14             | 3.9   | 1.21  | 4.0    | 2.0  | 3.37     | 4.43     
agentic_xai | no depression | Correctness | 20       | 14             | 4.05  | 0.945 | 4.0    | 1.0  | 3.636    | 4.464    
agentic_xai | no depression | Clarity     | 20       | 14             | 4.25  | 0.639 | 4.0    | 1.0  | 3.97     | 4.53     
agentic_xai | no depression | Trust       | 20       | 14             | 3.9   | 1.165 | 4.0    | 1.25 | 3.389    | 4.411    
agentic_xai | moderate      | Helpfulness | 14       | 9              | 3.786 | 0.975 | 4.0    | 0.75 | 3.275    | 4.296    
agentic_xai | moderate      | Correctness | 14       | 9              | 4.0   | 0.961 | 4.0    | 0.75 | 3.497    | 4.503    
agentic_xai | moderate      | Clarity     | 14       | 9              | 3.714 | 1.069 | 4.0    | 0.75 | 3.154    | 4.274    
agentic_xai | moderate      | Trust       | 14       | 9              | 3.143 | 1.099 | 3.5    | 2.0  | 2.567    | 3.719    
agentic_xai | severe        | Helpfulness | 19       | 10             | 3.526 | 1.124 | 4.0    | 1.0  | 3.021    | 4.032    
agentic_xai | severe        | Correctness | 19       | 10             | 3.789 | 1.032 | 4.0    | 1.5  | 3.326    | 4.253    
agentic_xai | severe        | Clarity     | 19       | 10             | 3.895 | 0.937 | 4.0    | 1.0  | 3.474    | 4.316    
agentic_xai | severe        | Trust       | 19       | 10             | 3.684 | 0.946 | 4.0    | 1.0  | 3.259    | 4.11     
```

## Exploratory System x Severity Interaction Tests
```
dimension   | method                                                    | model_comparison                       | n_trials | n_participants | lr_chi2 | df | p_value  | converged | interpretation_note                                       
----------- | --------------------------------------------------------- | -------------------------------------- | -------- | -------------- | ------- | -- | -------- | --------- | ----------------------------------------------------------
Helpfulness | Exploratory mixed-model interaction likelihood-ratio test | system + severity vs system * severity | 107      | 14             | 5.2859  | 2  | 0.07115  | True      | Secondary/exploratory; do not overstate subgroup findings.
Correctness | Exploratory mixed-model interaction likelihood-ratio test | system + severity vs system * severity | 107      | 14             | 6.3411  | 2  | 0.04198  | True      | Secondary/exploratory; do not overstate subgroup findings.
Clarity     | Exploratory mixed-model interaction likelihood-ratio test | system + severity vs system * severity | 107      | 14             | 10.1018 | 2  | 0.006404 | True      | Secondary/exploratory; do not overstate subgroup findings.
Trust       | Exploratory mixed-model interaction likelihood-ratio test | system + severity vs system * severity | 107      | 14             | 16.9938 | 2  | 0.000204 | True      | Secondary/exploratory; do not overstate subgroup findings.
```

## Task 9 Model Notes
```
dimension   | note                                 
----------- | -------------------------------------
Helpfulness | Random effects covariance is singular
Correctness | Random effects covariance is singular
Clarity     | Random effects covariance is singular
Trust       | Random effects covariance is singular
```

## Task 9 Figure
- /Users/arijeet/Documents/Study Material/Fourth_Semeter/Master_thesis/Explainable_Model/explainableDepressionPrediction_mcp_server/analysis/figures/phase2_task9_system_by_severity_interaction.svg

## Stop Point
Task 9 is complete. No further analyses were run.
