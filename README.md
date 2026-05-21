# GroMong Growth Candidate Decision-Support PoC

GroMong Score는 F&B 매장의 성장 후보군을 calibrated model probability로 우선순위화하고, 리뷰·운영·안정성 신호를 explanation index로 분해해 투자 검토를 보조하는 ML decision-support PoC입니다.

## Current Freeze Definition

- Predictive ranking is based on calibrated model probability.
- Composite score is an explanation index, not the final predictive ranking score.
- Grade and decision bands are priority review bands, not automatic investment decisions.
- ROI is scenario-based decision support, not guaranteed return.
- This is a production-style PoC, not a production system.

## Final Public Artifacts

| File | Role |
| --- | --- |
| `analysis_outputs/final_model_card.md` | Final model card and allowed/forbidden claims |
| `analysis_outputs/final_freeze_manifest.json` | Frozen artifact manifest |
| `analysis_outputs/final_public_artifact_gate_report.md` | Public artifact safety gate result |
| `analysis_outputs/scoring/latest_shop_scores_public.csv` | Public-safe latest store priority ranking |
| `analysis_outputs/scoring/store_ranking_topN.csv` | Public-safe TopN priority ranking |
| `analysis_outputs/scoring/ranking_strategy_summary.md` | Ranking role redefinition summary |
| `analysis_outputs/scoring/component_direction_audit.md` | Component direction audit summary |
| `analysis_outputs/final_gap_closure_report.md` | Feedback gap closure report |

## Pipeline Summary

```text
raw/store-month data
-> feature engineering
-> growth classification model
-> calibration and validation audit
-> calibrated probability ranking
-> explanation index and decision-support artifacts
```

## Score Semantics

| Public field | Meaning |
| --- | --- |
| `predictive_rank_score` | Calibrated model probability used for predictive ranking |
| `predicted_priority_rank` | Final priority order for review |
| `decision_band` | Priority review band |
| `explanation_index` | Interpretable signal decomposition index |
| `signal_decomposition_index` | Same role as explanation index, exported for clarity |
| `action_band` | Operational review band by rank |
| `risk_flag` | Direction/risk signal from component audit |
| `top_positive_signal` | Strongest explanatory component |
| `top_negative_signal` | Weakest explanatory component |

## Key Components

| Component | Role |
| --- | --- |
| Calibrated model probability | Predictive ranking basis |
| Growth Alpha | Explanation/risk signal after direction audit |
| Review growth | Explanation/risk signal after direction audit |
| Operation score | Explanation signal |
| Stability score | Explanation/risk signal after direction audit |
| Market fit | Seoul subset external-market support signal |

## Important Limitations

- Composite score is not used as the predictive ranking score.
- Some component scores were weakly or inversely aligned with the latest-month growth label, so they are used as explanation/risk signals only.
- ROI is a scenario-based support layer and does not guarantee returns.
- SHAP or model contribution should not be interpreted as causal attribution.
- Public artifacts exclude label, future outcome, and treatment-related columns.

## Reproducibility Note

The project is frozen for final presentation. Do not add new models, change metrics, retune score weights, or change the ranking basis before submission.
