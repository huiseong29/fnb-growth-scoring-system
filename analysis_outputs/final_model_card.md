# Final Model Card

## Project Definition

F&B 매장의 성장 후보군을 우선 검토하기 위한 decision-support pipeline이다. 최종 public ranking은 calibrated model probability를 기준으로 하며, composite score는 설명 가능한 신호 분해 지수로만 사용한다.

## Intended Use

- 성장 가능성이 있는 매장을 우선 검토할 후보군으로 정렬한다.
- 리뷰, 운영, 안정성, 상권 보조 신호를 설명 지수로 제공한다.
- ROI는 고정 가정 기반 scenario decision support로 사용한다.

## Not Intended Use

- 자동 투자 결정 또는 계약 결정에 사용하지 않는다.
- composite score를 성장 예측 순위 점수로 사용하지 않는다.
- ROI를 보장 수익 또는 실제 수익 예측으로 해석하지 않는다.
- SHAP 또는 feature contribution을 인과효과로 해석하지 않는다.

## Predictive Ranking 기준

Predictive ranking is based on calibrated model probability. Public outputs use `predictive_rank_score` and `predicted_priority_rank` for ordering.

## Explanation Index 역할

`explanation_index`와 `signal_decomposition_index`는 probability, Growth Alpha, review growth, operation, stability, market fit 신호를 요약한 설명용 index다. Direction audit 결과 일부 component가 최신월 growth label과 반대 또는 약한 방향성을 보여 final ranking에서는 제외했다.

## Causal Layer 역할

ATT/DID 계열 결과는 평균 효과 reference layer로만 유지한다. Predictive score나 public ranking feature로 직접 투입하지 않는다.

## ROI Scenario 역할

ROI is scenario-based decision support, not guaranteed return. ROI files use calibrated probability and explicit assumptions from `analysis_outputs/roi/roi_assumptions.csv`.

## Leakage Controls

- Time-aware split 유지
- future outcome/label/treatment 계열 컬럼은 public artifact gate에서 차단
- ATT는 predictive score에 직접 투입하지 않음
- Public outputs exclude label/future/treatment columns

## Validation Summary

- Full NLP time split AUC: 0.6154
- Full NLP PR-AUC: 0.3924
- Full NLP Brier score: 0.3217
- Calibrated probability ranking AUC: 0.5281
- Calibrated probability Top100 hit/lift: 25/0.96
- Current composite ranking AUC: 0.4056

## Known Limitations

- Composite score is not a reliable predictive ranking score on the latest-month audit.
- Growth Alpha, review growth, stability, and composite components showed weak or reversed direction in the latest-month direction audit.
- Seoul external-market variables are limited to the matched Seoul subset and should not be generalized nationally.
- KoBERT/fine-tuned deep NLP and causal forest/uplift modeling are not included.
- Public ranking supports review priority, not automatic action.

## Final Public Artifacts List

- `analysis_outputs/scoring/latest_shop_scores_public.csv`
- `analysis_outputs/scoring/store_ranking_topN.csv`
- `analysis_outputs/scoring/component_direction_audit.csv`
- `analysis_outputs/scoring/component_inversion_check.csv`
- `analysis_outputs/scoring/ranking_strategy_comparison.csv`
- `analysis_outputs/scoring/ranking_strategy_summary.md`
- `analysis_outputs/final_public_artifact_gate_report.md`

## 발표에서 사용 가능한 주장

- Predictive ranking is based on calibrated model probability.
- Explanation index summarizes interpretable growth-related signals.
- Grade and decision bands are priority review bands, not automatic investment decisions.
- SHAP is used as predictive contribution, not causal attribution.
- ROI is scenario-based decision support, not guaranteed return.

## 발표에서 금지해야 할 주장

- Do not say the GroMong explanation index is a growth prediction model.
- Do not present the composite index as the ordering metric for predictive ranking.
- Do not describe SHAP-derived contribution as causal weighting.
- Do not describe high bands as automatic investment targets.
- Do not describe ROI scenarios as forecasts or guaranteed returns.