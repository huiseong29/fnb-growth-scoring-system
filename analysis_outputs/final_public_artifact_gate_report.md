# Final Public Artifact Gate Report

## Gate Rule

Public export must not expose label, future outcome, treatment, or misleading predictive-score column names. Predictive ranking is based on calibrated model probability; composite score is exported only as explanation_index/signal_decomposition_index.

| file | columns | status | forbidden hits |
| --- | ---: | --- | --- |
| analysis_outputs/scoring/latest_shop_scores_public.csv | 26 | PASS | - |
| analysis_outputs/scoring/store_ranking_topN.csv | 26 | PASS | - |

## Forbidden Column Patterns

growth_label, future_order_3m, future_sales, treated, post_treatment, treated_x_post, is_post_treatment, months_since_treatment, service_term_agree_date, treatment_date, investment_score, success_probability, final_growth_score, composite_growth_score, gromong_score

## Result

PASS