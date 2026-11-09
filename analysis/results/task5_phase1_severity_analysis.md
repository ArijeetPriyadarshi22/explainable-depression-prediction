# Task 5 - Phase 1 Severity Analysis

Generated: 2026-08-30T23:51:30

This report examines Phase 1 severity as a secondary/exploratory analysis. Phase 2 hypothesis tests are not run here.

## Analysis Plan
First, ratings are summarized by severity category: no depression, moderate, and severe.
Then severity is checked with a simple participant-aware mixed model: rating ~ severity + (1 | participant).
Because the explanation type x severity cells are populated, an exploratory interaction model is also compared against an additive model.
The interaction analysis is exploratory. Small subgroups should not be used for strong claims.

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

## Phase 1 Severity Analysis
This is a secondary/exploratory analysis. The main Phase 1 research question remains explanation type.
Severity categories are reported as no depression, moderate, and severe. The raw Phase 1 label not depression is reported as no depression here for consistency with the thesis wording.
The main severity effect is inspected descriptively and with a simple participant-aware exploratory mixed model.
The explanation type x severity interaction is explored only because all cells have at least 10 trials. These subgroup results should be described cautiously.

## Task 5 Result Summary
The smallest explanation-type by severity subgroup has 12 trials from 9 participants.
Because every subgroup has at least 10 trials, the exploratory interaction model was run. This does not make the subgroup analysis primary.
The exploratory main severity models did not show evidence below 0.05 for any rating dimension.
The exploratory explanation type x severity models did not show evidence below 0.05 for any rating dimension.
Some model fits produced warnings; see the model notes table before using these exploratory results in the thesis.

## Severity Descriptives
```
severity      | dimension   | n_trials | n_participants | mean  | sd    | median | iqr | ci95_low | ci95_high
------------- | ----------- | -------- | -------------- | ----- | ----- | ------ | --- | -------- | ---------
no depression | Clarity     | 64       | 14             | 3.875 | 1.327 | 4.0    | 2.0 | 3.55     | 4.2      
moderate      | Clarity     | 98       | 15             | 3.847 | 1.187 | 4.0    | 1.0 | 3.612    | 4.082    
severe        | Clarity     | 101      | 14             | 3.881 | 1.259 | 4.0    | 1.0 | 3.636    | 4.127    
no depression | Correctness | 64       | 14             | 3.594 | 1.33  | 4.0    | 2.0 | 3.268    | 3.92     
moderate      | Correctness | 98       | 15             | 3.786 | 1.048 | 4.0    | 2.0 | 3.578    | 3.993    
severe        | Correctness | 101      | 14             | 3.812 | 1.138 | 4.0    | 2.0 | 3.59     | 4.034    
no depression | Helpfulness | 64       | 14             | 3.656 | 1.324 | 4.0    | 2.0 | 3.332    | 3.981    
moderate      | Helpfulness | 98       | 15             | 3.622 | 1.05  | 4.0    | 1.0 | 3.414    | 3.83     
severe        | Helpfulness | 101      | 14             | 3.693 | 1.111 | 4.0    | 1.0 | 3.476    | 3.91     
no depression | Trust       | 64       | 14             | 3.469 | 1.309 | 4.0    | 1.0 | 3.148    | 3.789    
moderate      | Trust       | 98       | 15             | 3.561 | 1.066 | 4.0    | 1.0 | 3.35     | 3.772    
severe        | Trust       | 101      | 14             | 3.762 | 1.088 | 4.0    | 2.0 | 3.55     | 3.974    
```

## Explanation Type x Severity Descriptives
```
explanation_type | severity      | dimension   | n_trials | n_participants | mean  | sd    | median | iqr  | ci95_low | ci95_high
---------------- | ------------- | ----------- | -------- | -------------- | ----- | ----- | ------ | ---- | -------- | ---------
SHAP             | no depression | Clarity     | 20       | 10             | 3.75  | 1.372 | 4.0    | 2.0  | 3.149    | 4.351    
SHAP             | moderate      | Clarity     | 24       | 13             | 3.875 | 1.076 | 4.0    | 1.25 | 3.445    | 4.305    
SHAP             | severe        | Clarity     | 26       | 12             | 3.692 | 1.379 | 4.0    | 2.0  | 3.162    | 4.222    
COUNTERFACTUAL   | no depression | Clarity     | 15       | 10             | 3.2   | 1.699 | 4.0    | 3.5  | 2.34     | 4.06     
COUNTERFACTUAL   | moderate      | Clarity     | 25       | 13             | 3.6   | 1.258 | 4.0    | 1.0  | 3.107    | 4.093    
COUNTERFACTUAL   | severe        | Clarity     | 26       | 14             | 4.077 | 0.891 | 4.0    | 1.0  | 3.734    | 4.419    
RAG              | no depression | Clarity     | 17       | 11             | 4.529 | 0.717 | 5.0    | 1.0  | 4.188    | 4.87     
RAG              | moderate      | Clarity     | 26       | 12             | 4.154 | 1.008 | 4.0    | 1.0  | 3.767    | 4.541    
RAG              | severe        | Clarity     | 21       | 12             | 3.714 | 1.554 | 4.0    | 2.0  | 3.05     | 4.379    
HYBRID           | no depression | Clarity     | 12       | 9              | 4.0   | 1.044 | 4.0    | 2.0  | 3.409    | 4.591    
HYBRID           | moderate      | Clarity     | 23       | 13             | 3.739 | 1.389 | 4.0    | 2.5  | 3.172    | 4.307    
HYBRID           | severe        | Clarity     | 28       | 14             | 4.0   | 1.217 | 4.0    | 1.0  | 3.549    | 4.451    
SHAP             | no depression | Correctness | 20       | 10             | 3.45  | 1.276 | 4.0    | 1.0  | 2.891    | 4.009    
SHAP             | moderate      | Correctness | 24       | 13             | 3.792 | 1.021 | 4.0    | 1.25 | 3.383    | 4.2      
SHAP             | severe        | Correctness | 26       | 12             | 3.731 | 1.185 | 4.0    | 1.75 | 3.275    | 4.186    
COUNTERFACTUAL   | no depression | Correctness | 15       | 10             | 3.0   | 1.512 | 3.0    | 2.0  | 2.235    | 3.765    
COUNTERFACTUAL   | moderate      | Correctness | 25       | 13             | 3.44  | 0.961 | 3.0    | 1.0  | 3.063    | 3.817    
COUNTERFACTUAL   | severe        | Correctness | 26       | 14             | 4.038 | 0.774 | 4.0    | 0.75 | 3.741    | 4.336    
RAG              | no depression | Correctness | 17       | 11             | 4.0   | 1.275 | 4.0    | 1.0  | 3.394    | 4.606    
RAG              | moderate      | Correctness | 26       | 12             | 3.923 | 1.093 | 4.0    | 1.75 | 3.503    | 4.343    
RAG              | severe        | Correctness | 21       | 12             | 3.714 | 1.384 | 4.0    | 2.0  | 3.123    | 4.306    
HYBRID           | no depression | Correctness | 12       | 9              | 4.0   | 1.044 | 4.0    | 2.0  | 3.409    | 4.591    
HYBRID           | moderate      | Correctness | 23       | 13             | 4.0   | 1.087 | 4.0    | 1.5  | 3.556    | 4.444    
HYBRID           | severe        | Correctness | 28       | 14             | 3.75  | 1.206 | 4.0    | 2.0  | 3.303    | 4.197    
SHAP             | no depression | Helpfulness | 20       | 10             | 3.65  | 1.226 | 4.0    | 1.25 | 3.113    | 4.187    
SHAP             | moderate      | Helpfulness | 24       | 13             | 3.667 | 0.917 | 4.0    | 1.0  | 3.3      | 4.033    
SHAP             | severe        | Helpfulness | 26       | 12             | 3.538 | 1.104 | 4.0    | 1.0  | 3.114    | 3.963    
COUNTERFACTUAL   | no depression | Helpfulness | 15       | 10             | 3.4   | 1.502 | 4.0    | 3.0  | 2.64     | 4.16     
COUNTERFACTUAL   | moderate      | Helpfulness | 25       | 13             | 3.48  | 1.122 | 4.0    | 1.0  | 3.04     | 3.92     
COUNTERFACTUAL   | severe        | Helpfulness | 26       | 14             | 4.038 | 0.871 | 4.0    | 1.75 | 3.704    | 4.373    
... 18 more rows not shown
```

## Explanation Type x Severity Cell Support
```
explanation_type | severity      | n_trials | n_participants
---------------- | ------------- | -------- | --------------
SHAP             | no depression | 20       | 10            
SHAP             | moderate      | 24       | 13            
SHAP             | severe        | 26       | 12            
COUNTERFACTUAL   | no depression | 15       | 10            
COUNTERFACTUAL   | moderate      | 25       | 13            
COUNTERFACTUAL   | severe        | 26       | 14            
RAG              | no depression | 17       | 11            
RAG              | moderate      | 26       | 12            
RAG              | severe        | 21       | 12            
HYBRID           | no depression | 12       | 9             
HYBRID           | moderate      | 23       | 13            
HYBRID           | severe        | 28       | 14            
```

## Exploratory Severity Mixed-Model Tests
```
dimension   | method                                                        | model                                 | n_trials | n_participants | lr_chi2 | df | p_value  | converged | interpretation_note                                              
----------- | ------------------------------------------------------------- | ------------------------------------- | -------- | -------------- | ------- | -- | -------- | --------- | -----------------------------------------------------------------
Clarity     | Exploratory linear mixed-effects model, likelihood-ratio test | rating ~ severity + (1 | participant) | 263      | 16             | 0.5516  | 2  | 0.75898  | True      | Secondary severity check; not the main Phase 1 research question.
Correctness | Exploratory linear mixed-effects model, likelihood-ratio test | rating ~ severity + (1 | participant) | 263      | 16             | 2.2837  | 2  | 0.319234 | True      | Secondary severity check; not the main Phase 1 research question.
Helpfulness | Exploratory linear mixed-effects model, likelihood-ratio test | rating ~ severity + (1 | participant) | 263      | 16             | 2.0687  | 2  | 0.355463 | True      | Secondary severity check; not the main Phase 1 research question.
Trust       | Exploratory linear mixed-effects model, likelihood-ratio test | rating ~ severity + (1 | participant) | 263      | 16             | 5.2805  | 2  | 0.071343 | True      | Secondary severity check; not the main Phase 1 research question.
```

## Exploratory Interaction Mixed-Model Tests
```
dimension   | method                                                    | model_comparison                                           | n_trials | n_participants | lr_chi2 | df | p_value  | converged | interpretation_note                                              
----------- | --------------------------------------------------------- | ---------------------------------------------------------- | -------- | -------------- | ------- | -- | -------- | --------- | -----------------------------------------------------------------
Clarity     | Exploratory mixed-model interaction likelihood-ratio test | explanation_type + severity vs explanation_type * severity | 263      | 16             | 8.5058  | 6  | 0.203337 | True      | Exploratory only; do not make strong claims from small subgroups.
Correctness | Exploratory mixed-model interaction likelihood-ratio test | explanation_type + severity vs explanation_type * severity | 263      | 16             | 7.1457  | 6  | 0.307582 | True      | Exploratory only; do not make strong claims from small subgroups.
Helpfulness | Exploratory mixed-model interaction likelihood-ratio test | explanation_type + severity vs explanation_type * severity | 263      | 16             | 3.5123  | 6  | 0.742338 | True      | Exploratory only; do not make strong claims from small subgroups.
Trust       | Exploratory mixed-model interaction likelihood-ratio test | explanation_type + severity vs explanation_type * severity | 263      | 16             | 2.2273  | 6  | 0.897654 | True      | Exploratory only; do not make strong claims from small subgroups.
```

## Task 5 Model Notes
```
dimension   | note                                 
----------- | -------------------------------------
Correctness | Random effects covariance is singular
Trust       | Random effects covariance is singular
```

## Task 5 Figure
- /Users/arijeet/Documents/Study Material/Fourth_Semeter/Master_thesis/Explainable_Model/explainableDepressionPrediction_mcp_server/analysis/figures/phase1_task5_explanation_by_severity_interaction.svg

## Stop Point
Task 5 is complete. No Phase 2 statistical tests were run.
