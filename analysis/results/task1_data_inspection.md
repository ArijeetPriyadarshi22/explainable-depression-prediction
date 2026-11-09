# Task 1 - Data Inspection

Generated: 2026-08-30T23:51:28

This report inspects the two study datasets separately. It does not run statistical tests.

## Why Trial Rows Are Not Independent
Each participant rated more than one explanation. Ratings from the same participant tend to be related because the same person brings the same expectations, rating habits, attention level, and interpretation style across trials.
That means 20 rows from one participant do not contain the same amount of independent information as 20 rows from 20 different participants.
For the later primary analysis, the correct approach is therefore participant-aware: keep every valid trial, but use a repeated-measures or mixed-effects method that accounts for participant ID.
The participant-level summaries are still useful as a descriptive and robustness check, but they should not replace the primary trial-level analysis.

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

## Stop Point
Task 1 is complete. The next phase should add statistical tests only after explicit confirmation.
