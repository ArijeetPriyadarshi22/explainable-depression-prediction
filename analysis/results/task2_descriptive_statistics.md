# Task 2 - Descriptive Statistics

Generated: 2026-08-30T23:51:28

This report includes Task 1 inspection context and Task 2 descriptive statistics. It does not run statistical tests and does not describe anything as statistically significant.

## Plain-Language Reading Guide
The trial-level tables summarize every valid row, so they preserve the full amount of observed rating information.
The participant-level tables first average ratings within each participant and condition. This is easier to explain and useful as a secondary descriptive view.
Confidence intervals here are descriptive intervals around observed means. They are not hypothesis tests.
Use cautious wording: higher descriptive mean, lower descriptive mean, or similar ratings.

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

## Stop Point
Task 2 is complete. The next phase should add statistical tests only after explicit confirmation.
