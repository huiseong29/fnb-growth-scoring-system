# Final Submission Manifest

본 문서는 code freeze 이후 최종 제출/발표 패키지에 포함할 파일과 제외할 파일을 구분한다. 최종 발표 기준은 다음과 같다.

- Predictive ranking: calibrated model probability
- Composite score: explanation index / signal decomposition index
- Grade and bands: priority review bands, not automatic investment decisions
- ROI: scenario-based decision support

## A. 반드시 포함할 파일

| 파일명 | 용도 | 발표 사용 여부 | backup 여부 | public-safe 여부 | 주의사항 |
| --- | --- | --- | --- | --- | --- |
| `analysis_outputs/final_model_card.md` | 최종 모델 카드, 사용/금지 주장 정리 | 사용 | 아니오 | 예 | 발표 전 핵심 문구 확인 |
| `analysis_outputs/final_freeze_manifest.json` | freeze 기준과 산출물 고정 manifest | 사용 | 아니오 | 예 | as_of_date와 public output 파일 확인 |
| `analysis_outputs/final_public_artifact_gate_report.md` | public artifact 금지 컬럼 gate 결과 | 사용 | 아니오 | 예 | PASS 상태 유지 |
| `analysis_outputs/scoring/latest_shop_scores_public.csv` | public-safe 전체 매장 우선순위 | 사용 | 아니오 | 예 | predictive_rank_score 기준 정렬 |
| `analysis_outputs/scoring/store_ranking_topN.csv` | public-safe TopN 후보군 | 사용 | 아니오 | 예 | 내부 라벨/미래/treatment 컬럼 없음 |
| `analysis_outputs/scoring/ranking_strategy_summary.md` | ranking 기준 재정의 근거 | 사용 | 아니오 | 예 | composite는 explanation index로 설명 |
| `analysis_outputs/scoring/component_direction_audit.md` | component 방향성 audit 요약 | 사용 | 아니오 | 예 | 일부 component 방향성 반대/약함을 솔직히 인정 |
| `analysis_outputs/final_gap_closure_report.md` | 피드백 반영 보완 보고서 | 사용 | 아니오 | 예 | 성능 대폭 개선이 아니라 검증 신뢰도 보강으로 설명 |
| `analysis_outputs/modeling/model_validation_audit.csv` | 검증 audit 핵심 metrics | 사용 | 예 | 예 | 발표에는 집계 수치만 사용 |
| `analysis_outputs/roi/topk_roi_summary.csv` | TopK ROI scenario 요약 | 사용 | 예 | 예 | 보장 수익이 아니라 scenario layer |
| `README.md` | 프로젝트 정의 및 frozen semantics | 사용 | 아니오 | 예 | production-style PoC로 설명 |

## B. Backup 자료로만 둘 파일

| 파일명 | 용도 | 발표 사용 여부 | backup 여부 | public-safe 여부 | 주의사항 |
| --- | --- | --- | --- | --- | --- |
| `analysis_outputs/scoring/component_direction_audit.csv` | component별 수치 상세 | 필요 시 | 예 | 예 | raw label 컬럼 없음, 집계 결과 |
| `analysis_outputs/scoring/ranking_strategy_comparison.csv` | ranking strategy 비교 수치 | 필요 시 | 예 | 예 | calibrated probability 우선 결론 근거 |
| `analysis_outputs/scoring/weight_sensitivity_analysis.csv` | 가중치 민감도 분석 상세 | 필요 시 | 예 | 예 | best weight 주장 금지 |
| `analysis_outputs/modeling/treatment_proxy_ablation_report.md` | treatment proxy ablation 보고서 | 필요 시 | 예 | 예 | 인과효과 주장 금지 |
| `analysis_outputs/modeling/group_holdout_metrics.csv` | store-level holdout 검증 | 필요 시 | 예 | 예 | 집계 metrics로만 사용 |
| `analysis_outputs/modeling/calibration_lift_table.csv` | probability band calibration/lift | 필요 시 | 예 | 예 | ROI/calibration 근거 |
| `analysis_outputs/nlp/nlp_ablation_report.csv` | NLP feature ablation 요약 | 필요 시 | 예 | 예 | KoBERT 구현 주장 금지 |
| `analysis_outputs/seoul_external_modeling/external_direction_audit.csv` | 외부 상권 방향성 audit | 필요 시 | 예 | 예 | 서울 subset 한계 명시 |

## C. 제출/발표에서 제외할 파일

| 파일명/패턴 | 제외 사유 | 주의사항 |
| --- | --- | --- |
| `model_dataset_with_score.csv` | 내부 모델링 dataset 가능성 | label/future/treatment 포함 가능성 |
| `master_dataset.csv` | 원천/통합 내부 dataset 가능성 | public 제출 금지 |
| `analysis_outputs/store_month_panel.csv` | 내부 panel dataset | label/future/treatment 계열 컬럼 포함 |
| `analysis_outputs/modeling/model_predictions.csv` | 내부 검증 예측 파일 | growth label 포함 |
| `analysis_outputs/seoul_external_modeling/seoul_external_predictions.csv` | 내부 검증 예측 파일 | growth label 포함 |
| `analysis_outputs/seoul_external_modeling/seoul_external_top_store_examples.csv` | 내부 예시 파일 | growth label 포함 |
| `analysis_outputs/scoring/store_scores.csv` | 내부 scoring 원본 | public-safe alias 적용 전 파일 |
| `analysis_outputs/scoring/store_score_explanations.csv` | 내부 scoring 설명 파일 | experiment group 등 내부 컬럼 포함 |
| `analysis_outputs/eda/*.csv` | EDA 내부 상세 파일 | label 포함 가능성 |
| `analysis_outputs/nlp/review_text_features.csv` | 리뷰 텍스트 상세 feature | 내부 feature 상세, 크기 큼 |
| `analysis_outputs/nlp/reply_text_features.csv` | 답글 텍스트 상세 feature | 내부 feature 상세, 크기 큼 |
| `analysis_outputs/demo/*.log` | 실행 로그 | 제출 불필요 |
| 임시 클론/실험 중간 산출물 | 재현성/의미 불명확 | 제출 제외 |

## 제출 패키지 원칙

- 최종 후보군 ranking은 `predictive_rank_score` 기준이다.
- `explanation_index`는 ranking score가 아니라 설명 지수다.
- Public artifact에는 label/future/treatment 계열 컬럼을 포함하지 않는다.
- ROI는 scenario-based ROI로만 표현한다.
- SHAP은 predictive contribution으로만 표현한다.
