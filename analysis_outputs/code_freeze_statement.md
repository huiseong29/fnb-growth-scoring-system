# Code Freeze Statement

## Code Freeze 기준

이 프로젝트는 최종 제출/발표 기준으로 code freeze 상태다. 추가 모델, metric 변경, ranking 기준 변경, score weight 수정은 수행하지 않는다.

## Freeze된 Ranking 기준

- Predictive ranking = calibrated model probability
- Public ranking field = `predictive_rank_score`
- Public priority order = `predicted_priority_rank`
- Composite score는 final ranking 기준이 아니다.

## Freeze된 Public Artifact

| 파일 | 역할 |
| --- | --- |
| `analysis_outputs/scoring/latest_shop_scores_public.csv` | 전체 public-safe priority ranking |
| `analysis_outputs/scoring/store_ranking_topN.csv` | TopN public-safe priority ranking |
| `analysis_outputs/final_public_artifact_gate_report.md` | label/future/treatment 컬럼 차단 gate |
| `analysis_outputs/final_model_card.md` | 최종 model card |
| `analysis_outputs/final_freeze_manifest.json` | freeze manifest |
| `analysis_outputs/final_submission_manifest.md` | 제출 파일 분류 |

## 수정 금지 항목

- 새 모델 추가
- 성능 개선 목적의 feature 추가/삭제
- score weight 재조정
- predictive ranking 기준 변경
- calibrated probability 계산 방식 변경
- public output에 label/future/treatment 컬럼 추가
- composite score를 predictive ranking score로 재해석

## 남은 한계

- Composite score는 최신월 growth label 기준 predictive ranking으로 부적합하여 explanation index로만 사용한다.
- Growth Alpha, review growth, stability 등 일부 component는 direction audit에서 약하거나 반대 방향성을 보였다.
- ROI는 scenario-based decision support이며 보장 수익이 아니다.
- 외부 상권 변수는 서울 subset 중심의 보조 검증이다.
- KoBERT fine-tuning, causal forest/uplift model은 구현하지 않았다.

## 발표 시 금지 표현

- Composite score가 성장 예측 순위 점수라는 표현
- Grade 또는 decision band가 자동 투자 대상이라는 표현
- ROI scenario를 실제 수익 예측이나 확정 수익으로 해석하는 표현
- SHAP contribution을 인과적 중요도로 해석하는 표현
- ATT가 개별 매장 score에 직접 반영되었다는 표현

## 발표 시 권장 표현

- Predictive ranking is based on calibrated model probability.
- Explanation index summarizes interpretable growth-related signals.
- Grade bands are priority review bands, not automatic investment decisions.
- ROI is scenario-based decision support, not guaranteed return.
- SHAP is used as predictive contribution, not causal attribution.
- This is a production-style PoC for decision support, not a production system.

