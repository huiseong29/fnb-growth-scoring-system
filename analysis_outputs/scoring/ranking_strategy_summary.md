# Ranking Strategy Redefinition Summary

## 핵심 판단

최종 후보군 ranking은 calibrated probability 기반으로 두는 것이 가장 방어 가능하다. 현재 composite score는 predictive ranking score가 아니라 interpretable signal decomposition, 즉 설명용 decision-support index로 재정의한다. 권장안은 Option 2이다.

## Ranking strategy 비교

| strategy | ROC-AUC | PR-AUC | Top20 hit/lift | Top50 hit/lift | Top100 hit/lift | rank stability vs current | rank stability vs calibrated | public output 적합성 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| calibrated_probability_ranking | 0.5281 | 0.2704 | 7/1.34 | 13/1.00 | 25/0.96 | 0.6784 | 1.0000 | best_for_predictive_ranking_but_needs_explanation_index |
| current_composite_score_ranking | 0.4056 | 0.2112 | 1/0.19 | 7/0.54 | 12/0.46 | 1.0000 | 0.6784 | not_recommended_as_predictive_ranking |
| hybrid_probability_primary_composite_support | 0.5281 | 0.2704 | 7/1.34 | 13/1.00 | 25/0.96 | 0.6784 | 1.0000 | recommended_probability_primary_composite_explanation_only |

## Option별 판단

| option | 판단 | 장점 | 단점/발표 리스크 |
| --- | --- | --- | --- |
| Option 1. Composite score를 최종 ranking으로 유지 | 비권장 | 설명 가능성이 높고 기존 산출물과 연결이 쉽다 | 최신월 라벨 기준 AUC가 낮고 일부 component 방향성이 반대라 predictive ranking으로 공격받기 쉽다 |
| Option 2. Calibrated probability를 최종 ranking으로 사용, composite는 explanation index | 권장 | predictive ranking과 설명 지수를 분리해 가장 방어 가능하다 | composite score가 최종 순위가 아니라는 점을 명확히 설명해야 한다 |
| Option 3. Composite score를 risk-adjusted decision score로 재정의 | 보류 | 반대 방향 component를 risk signal로 살릴 수 있다 | 새 점수 정의와 검증 시간이 필요해 최종 발표 직전에는 리스크가 크다 |
| Option 4. Probability 중심 operational weighting으로 재설계 | 보류 | 직관적으로 예측 방향성을 회복할 수 있다 | test AUC 사후 튜닝으로 오해받을 위험이 있어 별도 validation 설계가 필요하다 |

## Component 방향성 판단

- 방향성 반대 가능성이 높은 component: growth_alpha_score, review_growth_score, operation_score, stability_score, gromong_score
- 예측 방향성이 약한 component: probability_score, growth_alpha_score, review_growth_score, operation_score, stability_score, gromong_score

## Public artifact 수정 판단

기존 public ranking 파일이 composite score 기준이라면 calibrated_probability 기준으로 바꾸는 것이 낫다. 따라서 `latest_shop_scores_public.csv`와 `store_ranking_topN.csv`를 calibrated_probability 기준으로 새로 저장했다. composite score와 component score는 순위 기준이 아니라 설명/진단 컬럼으로 유지했다.

## 발표 문구

최종 후보군의 predictive ranking은 calibrated model probability를 기준으로 두고, GroMong composite score는 성장 확률을 보완 설명하는 interpretable signal decomposition으로 사용했습니다. 민감도와 방향성 audit 결과, composite score 자체를 성장 예측 순위로 쓰기에는 일부 component의 방향성이 약하거나 반대였기 때문에 역할을 재정의했습니다.

## 낮춰 말해야 할 표현

- composite score가 성장 예측을 잘한다고 말하지 않는다.
- 현재 score weight가 최적이라고 말하지 않는다.
- 방향성이 반대인 component를 억지로 성장 신호라고 설명하지 않는다. risk 또는 운영 상태 설명 신호로 제한한다.