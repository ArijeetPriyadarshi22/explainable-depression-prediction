# Task 10 - Reliability / Overall Score

Generated: 2026-08-30T23:51:31

This report checks whether the four rating dimensions are sufficiently related to justify an overall explanation-quality score as a secondary summary.

## Plain-Language Guide
Cronbach's alpha measures internal consistency: whether several rating items tend to behave like they are measuring the same broader concept.
A higher alpha means the four ratings move together more strongly. A common practical threshold is 0.70 for an acceptable secondary composite.
Alpha does not prove that the items are identical, and it does not mean the individual dimensions should be discarded.
The primary thesis results should still report Clarity, Correctness, Helpfulness, and Trust separately.
Any overall score created here is only a secondary summary.

## Phase 1 Reliability / Overall Score
Cronbach's alpha measures whether the four rating dimensions tend to move together as a set. Higher values mean the items are more internally consistent.
This does not automatically replace Clarity, Correctness, Helpfulness, and Trust. The primary results should still report the four dimensions separately.
An overall composite is created only as a secondary summary when alpha is at least 0.70.

## Phase 1 Reliability Summary
Cronbach's alpha was 0.9046 (excellent internal consistency).
Reliability is acceptable for a secondary overall explanation-quality composite, but this composite should not replace the four primary rating dimensions.
The existing rating_overall_avg column was checked in 263 rows: matches computed average.

## Phase 1 Cronbach's Alpha
```
n_items | n_complete_rows | cronbach_alpha | interpretation                 | composite_created
------- | --------------- | -------------- | ------------------------------ | -----------------
4       | 263             | 0.9046         | excellent internal consistency | True             
```

## Phase 1 Rating-Dimension Correlations
```
dimension_1 | dimension_2 | n_pairwise_rows | pearson_r
----------- | ----------- | --------------- | ---------
Clarity     | Correctness | 263             | 0.6906   
Clarity     | Helpfulness | 263             | 0.65     
Clarity     | Trust       | 263             | 0.6604   
Correctness | Helpfulness | 263             | 0.7571   
Correctness | Trust       | 263             | 0.7299   
Helpfulness | Trust       | 263             | 0.7497   
```

## Phase 1 Existing Overall Average Verification
```
checked_rows | mismatch_count | max_absolute_difference | verification_result     
------------ | -------------- | ----------------------- | ------------------------
263          | 0              | 0.0                     | matches computed average
```

## Phase 1 Secondary Composite Descriptives
```
condition      | dimension                   | n_trials | n_participants | mean  | sd    | median | iqr   | ci95_low | ci95_high
-------------- | --------------------------- | -------- | -------------- | ----- | ----- | ------ | ----- | -------- | ---------
COUNTERFACTUAL | Overall explanation quality | 66       | 14             | 3.614 | 1.056 | 4.0    | 1.5   | 3.359    | 3.868    
HYBRID         | Overall explanation quality | 63       | 16             | 3.782 | 1.025 | 4.0    | 1.25  | 3.529    | 4.035    
RAG            | Overall explanation quality | 64       | 15             | 3.828 | 1.066 | 4.0    | 1.062 | 3.567    | 4.089    
SHAP           | Overall explanation quality | 70       | 15             | 3.675 | 0.994 | 4.0    | 0.938 | 3.442    | 3.908    
```

## Phase 2 Reliability / Overall Score
Cronbach's alpha measures whether the four mapped rating dimensions tend to move together as a set.
The Phase 2 dimensions are Helpfulness, Correctness, Clarity, and Trust, where rating_confidence means participant trust in the explanation.
This does not automatically replace the four individual outcomes. The primary Phase 2 results should still report each dimension separately.
An overall composite is created only as a secondary summary when alpha is at least 0.70.

## Phase 2 Reliability Summary
Cronbach's alpha was 0.8419 (good internal consistency).
Reliability is acceptable for a secondary overall explanation-quality composite, but this composite should not replace Helpfulness, Correctness, Clarity, and Trust.
No existing overall-average column was present in Phase 2; any composite is computed from the four mapped rating dimensions.

## Phase 2 Cronbach's Alpha
```
n_items | n_complete_rows | cronbach_alpha | interpretation            | composite_created
------- | --------------- | -------------- | ------------------------- | -----------------
4       | 107             | 0.8419         | good internal consistency | True             
```

## Phase 2 Rating-Dimension Correlations
```
dimension_1 | dimension_2 | n_pairwise_rows | pearson_r
----------- | ----------- | --------------- | ---------
Helpfulness | Correctness | 107             | 0.7436   
Helpfulness | Clarity     | 107             | 0.4547   
Helpfulness | Trust       | 107             | 0.6778   
Correctness | Clarity     | 107             | 0.3518   
Correctness | Trust       | 107             | 0.6908   
Clarity     | Trust       | 107             | 0.46     
```

## Phase 2 Existing Overall Average Verification
```
existing_overall_column_present | checked_column | note                                                                                                                        
------------------------------- | -------------- | ----------------------------------------------------------------------------------------------------------------------------
False                           |                | No existing overall-average column was present in Phase 2; any composite is computed from the four mapped rating dimensions.
```

## Phase 2 Secondary Composite Descriptives
```
condition   | dimension                   | n_trials | n_participants | mean  | sd    | median | iqr   | ci95_low | ci95_high
----------- | --------------------------- | -------- | -------------- | ----- | ----- | ------ | ----- | -------- | ---------
agentic_xai | Overall explanation quality | 53       | 14             | 3.821 | 0.824 | 4.0    | 1.5   | 3.599    | 4.043    
mentallama  | Overall explanation quality | 54       | 14             | 3.671 | 0.973 | 4.0    | 1.375 | 3.412    | 3.931    
```

## Stop Point
Task 10 is complete. The four individual rating dimensions remain the primary outcomes.
