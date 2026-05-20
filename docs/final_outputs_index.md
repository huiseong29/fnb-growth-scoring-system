# Final Outputs Index

??문서???�로?�트 ?�출물의 ?�치?� ?�도�??�리?�다.

?�로?�트 주제:

**AI 기반 F&B ?�장 ?�망 매장 ?�코?�링 ?�스??*

?�심 차별??

**?��? ?�권 ?�이?��? Growth Alpha�??�용???�권·브랜?�·카?�고�??�과�?보정???�장 ?�망 매장 ?�별**

## 1. ?�심 문서

| ?�일 | ?�명 |
| --- | --- |
| `docs/project_plan.md` | ?�체 ?�행 계획, ?�료 ?�태, ?�음 ?�업 |
| `docs/project_proposal.md` | ?�로?�트 기획?? 문제 ?�의, 방법�? 결과 ?�석 |
| `docs/remaining_tasks.md` | ?�으�??��? ?�업 체크리스??|
| `docs/final_outputs_index.md` | ?�체 ?�출�??�덱??|
| `analysis_outputs/visualization_guide.md` | 모든 ?�각???�일??목적, ?�석, 발표??문장 |
| `docs/score_design_rationale.md` | GroMong Score 5�?지?��? 가중치 ?�계 근거 |
| `docs/midterm_quality_boost_plan.md` | 중간발표 1???�리?��? ?�한 보강 과제 로드�?|

## 2. ?�본 ?�이??
?�치:

- `data/`

주요 ?�일:

| ?�일 | ?�명 |
| --- | --- |
| `매장_?�별_?�이??json` | 매장 ID, 브랜?? 카테고리, 주소, ?�험�??�제�?|
| `처치_?�점_?�의_?�이??json` | 매장�??�비???�의/처치 ?�점 |
| `order_주요_?�과_변??json` | 주문?? 가�? ?�량, 주문 ID |
| `reviews_주요_?�과_변??json` | 리뷰 ?�용, ?�점, ?��?, ?��? ?�점 |
| `20260310_?�제변??json` | 메뉴 ?�태, 메뉴 가�? 메뉴 ??관???�이??|
| `final_shop_address.xlsx` | 매장 주소 보조 ?�이??|

## 3. ?��? ?�이??
?�치:

- `external_data/`

| ?�일 | ?�명 |
| --- | --- |
| `seoul_sales_hdong_2024.zip` | ?�울???�권분석?�비??2024???�정??추정매출 ?�이??|
| `seoul_sales_2024.zip` | ?�울???�권분석?�비??2024???�권 ?�위 추정매출 ?�이??|
| `seoul_store_external_features_2024q4.csv` | ?��? ?�울 매장 211개에 결합???��? ?�권 변??|

?��? ?�이??결합 결과:

- ?�울 매장 211�?- ?�치�?기�? 매칭�?100%
- ?��? 카테고리?� ?��? ?�종 매핑�?100%

## 4. 분석???�이??마트

| ?�일 | ?�명 |
| --- | --- |
| `analysis_outputs/store_month_panel.csv` | 매장-???�위 분석 ?�널 |

?�널 ?�보:

- 매장 ?? 1,246
- 기간: 2024-11 ~ 2025-12
- ???? 17,444
- ?�장 ?�벨 ?�효 ?? 11,214
- ?�울 ?��? ?�권 결합 매장: 211

## 5. EDA ?�출�?
?�치:

- `analysis_outputs/eda/`

| ?�일 | ?�명 |
| --- | --- |
| `eda_report.md` | EDA ?�약 리포??|
| `eda_label_summary.csv` | ?�장 ?�벨�?주요 지???�약 |
| `eda_brand_summary.csv` | 브랜?�별 ?�장 ?�벨 분포 |
| `eda_category_summary.csv` | 카테고리�??�장 ?�벨 분포 |
| `eda_brand_category_summary.csv` | 브랜?�·카?�고리별 ?�장 ?�벨 분포 |
| `eda_growth_alpha_top_bottom.csv` | Growth Alpha ?�하??매장 |
| `eda_monthly_trend.csv` | ?�별 추이 |
| `eda_correlations.csv` | 주요 변?��? ?�장 ?�수 ?��? |
| `eda_seoul_external_label_summary.csv` | ?�울 ?��? 변???�벨�??�약 |
| `eda_seoul_gu_category_summary.csv` | ?�울 ?�치�?�카?�고리별 ?�약 |

## 6. EDA ?�각??
?�치:

- `analysis_outputs/eda/charts/`

| ?�일 | ?�명 |
| --- | --- |
| `label_avg_order_count.svg` | ?�장/비성???�균 주문??비교 |
| `label_avg_review_count.svg` | ?�장/비성???�균 리뷰??비교 |
| `label_avg_reply_rate.svg` | ?�장/비성???�균 ?��?�?비교 |
| `label_avg_growth_alpha.svg` | ?�장/비성??Growth Alpha 비교 |
| `brand_category_growth_rate.svg` | 브랜?�·카?�고리별 ?�장 비율 |
| `monthly_avg_orders_by_label.svg` | ?�장 ?�벨�??�별 ?�균 주문??추이 |

�?그래?�의 ?�석:

- `analysis_outputs/visualization_guide.md`

## 7. 모델�??�출�?
?�치:

- `analysis_outputs/modeling/`

| ?�일 | ?�명 |
| --- | --- |
| `modeling_report.md` | Baseline vs Growth Alpha 모델 결과 ?�약 |
| `model_comparison.csv` | 모델 ?�능 비교 |
| `model_predictions.csv` | 매장-?�별 ?�측 ?�률 |
| `model_coefficients.csv` | 로�??�틱 ?��? 계수 |
| `model_topn_metrics.csv` | Top N 추천 ?�능 |

?�심 결과:

- Baseline AUC: 0.6060
- Growth Alpha AUC: 0.6078
- Baseline Top 100 Precision: 0.400
- Growth Alpha Top 100 Precision: 0.420

## 8. ?�울 ?��? ?�권 모델�??�출�?
?�치:

- `analysis_outputs/seoul_external_modeling/`

| ?�일 | ?�명 |
| --- | --- |
| `seoul_external_modeling_report.md` | ?�울 ?��? ?�권 모델 결과 ?�약 |
| `seoul_external_model_comparison.csv` | ?�울 ?��? 모델 vs ?��? 결합 모델 비교 |
| `seoul_external_predictions.csv` | ?�울 매장 ?�측 결과 |
| `seoul_external_coefficients.csv` | 모델 계수 |
| `seoul_external_topn_metrics.csv` | Top N 추천 ?�능 |
| `seoul_external_top_store_examples.csv` | ?�위 추천 매장 ?�시 |

?�심 결과:

- Seoul Internal AUC: 0.5826
- Seoul External AUC: 0.5995
- Seoul Internal Top 100 Precision: 0.340
- Seoul External Top 100 Precision: 0.370

## 9. GroMong Score ?�출�?
?�치:

- `analysis_outputs/scoring/`

| ?�일 | ?�명 |
| --- | --- |
| `store_scores.csv` | 매장�?GroMong Score, ?�급, 구성 ?�수 |
| `store_score_explanations.csv` | 매장�??�수?� 주요 근거 3�?|
| `score_summary.md` | ?�코???�출 ?�약 |
| `docs/score_design_rationale.md` | ?�코???�계 근거, 지?�별 ?�용 변?? ?�계?� 고도??방향 |

?�심 결과:

- 기�? ?? 2025-09
- ?�수 ?�출 매장 ?? 1,246
- ?�균 ?�수: 53.28
- 중앙�??�수: 53.90
- 최고 ?�수: 98.18

?�급 분포:

| ?�급 | 매장 ??|
| --- | ---: |
| A | 84 |
| B | 234 |
| C | 365 |
| D | 563 |

## 10. ?�코?�링 ?�각??
?�치:

- `analysis_outputs/scoring/charts/`

| ?�일 | ?�명 |
| --- | --- |
| `score_distribution.svg` | GroMong Score 분포 |
| `grade_counts.svg` | A/B/C/D ?�급�?매장 ??|
| `brand_avg_score.svg` | 브랜?�별 ?�균 ?�수 |
| `category_avg_score.svg` | 카테고리�??�균 ?�수 |
| `growth_alpha_vs_score.svg` | Growth Alpha?� 최종 ?�수 관�?|
| `seoul_market_ticket_ratio_vs_score.svg` | ?�울 매장 ?�권 객단가 ?��??�수 관�?|
| `top20_store_scores.svg` | 최종 ?�수 ?�위 20�?매장 |

�?그래?�의 ?�석:

- `analysis_outputs/visualization_guide.md`

## 11. ?�크립트

| ?�일 | ?�명 |
| --- | --- |
| `src/check_external_fit.py` | ?�울 ?��? ?�권 ?�이??결합 가?�성 ?�인 |
| `src/build_store_month_panel.py` | 매장-???�널 ?�성 |
| `src/run_eda.py` | EDA ?�약 ?�출 |
| `src/make_eda_charts.py` | EDA ?�각???�성 |
| `src/run_modeling.py` | Baseline vs Growth Alpha 모델�?|
| `src/run_seoul_external_modeling.py` | ?�울 ?��? ?�권 모델�?|
| `src/build_scores.py` | GroMong Score ?�출 |
| `src/make_score_charts.py` | ?�코?�링 ?�각???�성 |

## 12. ?�직 ?�성 ?�정???�출�?
| ?�정 ?�일 | ?�명 |
| --- | --- |
| `src/app.py` | 매장 ID ?�력???�모 |
| `analysis_outputs/demo/` | ?�모 ?�명 �?검�?결과 |
| `analysis_outputs/demo/demo_guide.md` | ?�모 ?�용�?�??�면 ?�명 |
| `analysis_outputs/demo/demo_visualization_guide.md` | ?�모 ?�각???�명 |
| `analysis_outputs/demo/demo_validation.md` | ?�모 API �??�외 처리 검�?결과 |

## 12. ?�모 ?�출�?
| ?�일 | ?�명 |
| --- | --- |
| `src/app.py` | ?��? ?�이브러�?기반 ?�모 ?�버 |
| `analysis_outputs/demo/demo_guide.md` | ?�모 ?�행 방법, ?�면 구성, ?�연 ?�름 |
| `analysis_outputs/demo/demo_visualization_guide.md` | ?�수 게이지, ?�급 배�?, 구성?�소 bar chart ???�모 ?�각 ?�소 ?�석 |
| `analysis_outputs/demo/demo_validation.md` | ?�모 API ?�답 �??�는 ID ?�외 처리 검�?|

## 13. 중간발표 보강 ?�출�?
| ?�일 | ?�명 |
| --- | --- |
| `docs/midterm_quality_boost_plan.md` | 부족한 부분과 보강 과제 ?�리 |
| `analysis_outputs/quality_boost/charts/quality_boost_roadmap.svg` | 중간발표 보강 로드�??�각??|
| `analysis_outputs/quality_boost/quality_boost_visualization_guide.md` | 보강 로드�??�각???�석 |

진행 중인 추�? ?�출�?

- `analysis_outputs/nlp/`

?�행 주소:

```text
http://127.0.0.1:8765
```

?�행 명령:

```powershell
& 'C:\Users\tobes\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' src/app.py
```

## 15. ?�영 ?�칙

?�으�??�업 ?�나�??�료???�마???�음??반드???�데?�트?�다.

- `docs/project_plan.md`
- `docs/project_proposal.md`
- `docs/remaining_tasks.md`
- `docs/final_outputs_index.md`
- `analysis_outputs/visualization_guide.md`

?�각?��? ?�성?�면 반드???�음???�께 문서?�한??

- 그래??목적
- ?�심 ?�치
- ?�석
- 발표??문장
- 주의???�는 ?�계
## 2026-05-08 추�? ?�출�? 리뷰 ?�문 NLP 분석

?�치:

- `analysis_outputs/nlp/`

| ?�일 | ?�명 |
| --- | --- |
| `review_text_features.csv` | 리뷰 ?�문�?긍정/부???�워?? 주제 ?�그, ?�스??감성 ?�수 |
| `review_store_month_sentiment.csv` | 매장-???�위 리뷰 감성 집계 |
| `review_sentiment_summary.csv` | ?�장 ?�위 매장�??�장 ??매장??리뷰 감성 비교 |
| `review_category_sentiment_summary.csv` | 카테고리�??�장 ?�위/?�장 ??리뷰 감성 비교 |
| `positive_keyword_top50.csv` | 긍정 ?�워???�위 50�?|
| `negative_keyword_top50.csv` | 부???�워???�위 50�?|
| `rating_sentiment_mismatch_examples.csv` | 별점�??�스??감성???�긋?�는 리뷰 ?��? |
| `review_sentiment_report.md` | 리뷰 NLP ?�약 보고??|
| `review_nlp_visualization_guide.md` | 리뷰 NLP ?�각?�별 ?�석 문서 |

?�각??

| ?�일 | ?�명 |
| --- | --- |
| `analysis_outputs/nlp/charts/sentiment_by_growth_label.svg` | ?�장 ?�위/?�장 ??매장???�스??감성, 긍정�? 부?�률 비교 |
| `analysis_outputs/nlp/charts/review_topic_rates_by_growth_label.svg` | �? ?? 배달, 가�? ?�비?? ?�주�?주제 ?�급�?비교 |
| `analysis_outputs/nlp/charts/positive_keywords_top20.svg` | 긍정 ?�워???�위 20�?|
| `analysis_outputs/nlp/charts/negative_keywords_top20.svg` | 부???�워???�위 20�?|
| `analysis_outputs/nlp/charts/category_sentiment_by_growth_label.svg` | 카테고리�??�균 ?�스??감성 비교 |
| `analysis_outputs/nlp/charts/rating_sentiment_mismatch_counts.svg` | 별점�??�스??감성 불일�??��? ??|

관???�크립트:

| ?�일 | ?�명 |
| --- | --- |
| `src/run_review_nlp.py` | 리뷰 ?�문 기반 ?�워??감성/주제 분석 |
| `src/make_review_nlp_charts.py` | 리뷰 NLP 결과 ?�각???�성 |

?�심 발표 ?�치:

- ?�장 ?�위 매장 ?�균 ?�스??감성: 0.6831
- ?�장 ??매장 ?�균 ?�스??감성: 0.6709
- ?�장 ?�위 매장 긍정 리뷰 비율: 87.10%
- ?�장 ??매장 긍정 리뷰 비율: 85.62%
- ?�장 ?�위 매장 부??리뷰 비율: 3.10%
- ?�장 ??매장 부??리뷰 비율: 4.00%
- ?�장 ?�위 매장 ?�주�??�급�? 7.20%
- ?�장 ??매장 ?�주�??�급�? 6.44%

?�음 ?�성 ?�정 ?�출�?

- `analysis_outputs/sensitivity/`
- GroMong Score 가중치 민감??분석 결과
- 가중치 ?�나리오�?Top 매장 ?�정???�각??## 2026-05-08 추�? ?�출�? ?�코??가중치 민감??분석

?�치:

- `analysis_outputs/sensitivity/`

| ?�일 | ?�명 |
| --- | --- |
| `score_sensitivity_summary.csv` | 가중치 ?�나리오�??�균 ?�수, Top50/Top100 겹침�? ?�위 ?��?, ?�급 분포 |
| `score_sensitivity_detail.csv` | 매장�??�나리오�??�계???�수 |
| `top100_stability.csv` | ?�재 ?�위 매장???�나리오�?Top100 ?��? ?�수 |
| `score_sensitivity_report.md` | 가중치 민감??분석 ?�약 보고??|
| `score_sensitivity_visualization_guide.md` | 가중치 민감???�각?�별 ?�석 문서 |

?�각??

| ?�일 | ?�명 |
| --- | --- |
| `analysis_outputs/sensitivity/charts/top100_overlap_by_scenario.svg` | ?�재 Top100�??��?가중치 Top100??겹침�?|
| `analysis_outputs/sensitivity/charts/rank_correlation_by_scenario.svg` | ?�재 ?�위?� ?��?가중치 ?�위???��? |
| `analysis_outputs/sensitivity/charts/mean_score_by_scenario.svg` | ?�나리오�??�균 ?�수 |
| `analysis_outputs/sensitivity/charts/grade_counts_by_scenario.svg` | ?�나리오�?A/B/C/D ?�급 분포 |
| `analysis_outputs/sensitivity/charts/top100_stability_top20.svg` | ?�재 ?�위 20�?매장??Top100 ?��? ?�수 |

관???�크립트:

| ?�일 | ?�명 |
| --- | --- |
| `src/run_score_sensitivity.py` | GroMong Score 가중치 민감??분석 �??�각???�성 |

?�심 발표 ?�치:

- ?��?가중치 ?�나리오 Top100 겹침�?범위: 78~95%
- ?��?가중치 ?�나리오 ?�위 ?��? 범위: 0.959~0.995
- ?�재 ?�위 20�?매장: 7�??�나리오 모두?�서 Top100 ?��?

?�음 ?�성 ?�정 ?�출�?

- `analysis_outputs/calibrated_score/`
- 브랜??카테고리 보정 ?�수
- 카테고리 ?��? Top 매장 ?�각??## 2026-05-08 추�? ?�출�? 브랜??카테고리 보정 ?�수

?�치:

- `analysis_outputs/calibrated_score/`

| ?�일 | ?�명 |
| --- | --- |
| `calibrated_store_scores.csv` | 매장�?기존 ?�수, 브랜???��? percentile, 카테고리 ?��? percentile, 보정 ?�수 |
| `category_top10_calibrated.csv` | 카테고리�?보정 ?�수 Top10 매장 |
| `brand_top10_calibrated.csv` | 브랜?�별 보정 ?�수 Top10 매장 |
| `calibration_group_summary.csv` | 브랜??카테고리�?보정 ?�후 ?�약 |
| `top100_calibration_overlap.csv` | 기존 Top100�?보정 Top100 겹침�?|
| `calibrated_score_report.md` | 보정 ?�수 분석 ?�약 보고??|
| `calibrated_score_visualization_guide.md` | 보정 ?�수 ?�각?�별 ?�석 문서 |

?�각??

| ?�일 | ?�명 |
| --- | --- |
| `analysis_outputs/calibrated_score/charts/overall_vs_calibrated_score.svg` | 기존 GroMong Score?� 보정 ?�수 관�?|
| `analysis_outputs/calibrated_score/charts/category_top100_counts_before_after.svg` | 카테고리�?Top100 ?�함 매장 ??변??|
| `analysis_outputs/calibrated_score/charts/category_avg_score_before_after.svg` | 카테고리�??�균 ?�수 변??|
| `analysis_outputs/calibrated_score/charts/brand_A_counts_before_after.svg` | 브랜?�별 A?�급 매장 ??변??|
| `analysis_outputs/calibrated_score/charts/top100_overlap_after_calibration.svg` | 기존 Top100�?보정 Top100 겹침 �??�규 진입 |
| `analysis_outputs/calibrated_score/charts/category_top10_calibrated_scores.svg` | 카테고리�?보정 ?�수 Top ?�보 |

관???�크립트:

| ?�일 | ?�명 |
| --- | --- |
| `src/run_calibrated_score.py` | 브랜??카테고리 보정 ?�수 ?�성 �??�각??|

?�심 발표 ?�치:

- 기존 Top100�?보정 Top100 겹침: 92�?- 보정 ???�규 Top100 진입: 8�?- 굽네치킨 Top100 ?�함: 8개에??16�?- 치킨 Top100 ?�함: 7개에??11�?- ?�자 Top100 ?�함: 1개에??5�?
?�음 ?�성 ?�정 ?�출�?

- 최종 발표??결과 ?�리 문서
- 발표 그래??목록
- 발표 멘트 �?방어 ?�리 문서
## 2026-05-08 ?�성 ?�정 ?�출�? 불균??진단�?균형??추천

?�정 ?�치:

- `analysis_outputs/imbalance/`

?�정 ?�출�?

| ?�일 | ?�명 |
| --- | --- |
| `imbalance_summary.csv` | ?�본/기존 Top100/보정 Top100??브랜?�·카?�고�?분포 |
| `balanced_recommendations.csv` | 카테고리?� 브랜??균형??고려??추천 ?�보 |
| `imbalance_defense_report.md` | ?�이??불균???�계?� 방어 ?�리 |
| `imbalance_visualization_guide.md` | 불균???�각?�별 ?�석 문서 |
| `charts/` | 불균??진단 �?균형??추천 ?�각??|
## 2026-05-08 추�? ?�출�? 불균??진단�?균형??추천

?�치:

- `analysis_outputs/imbalance/`

| ?�일 | ?�명 |
| --- | --- |
| `imbalance_summary.csv` | ?�본/기존 Top100/보정 Top100/균형??추천??브랜?�·카?�고�?분포 |
| `imbalance_metrics.csv` | HHI, 최�? 브랜??비중, 최�? 카테고리 비중 ???�중 지??|
| `balanced_recommendations.csv` | 브랜??카테고리 균형??고려??보조 추천 ?�보�?|
| `imbalance_defense_report.md` | ?�이??불균???�계?� 발표??방어 ?�리 |
| `imbalance_visualization_guide.md` | 불균???�각?�별 ?�석 문서 |

?�각??

| ?�일 | ?�명 |
| --- | --- |
| `analysis_outputs/imbalance/charts/original_brand_distribution.svg` | ?�본 ?�이??브랜??분포 |
| `analysis_outputs/imbalance/charts/original_category_distribution.svg` | ?�본 ?�이??카테고리 분포 |
| `analysis_outputs/imbalance/charts/current_top100_category_distribution.svg` | 기존 Top100 카테고리 분포 |
| `analysis_outputs/imbalance/charts/calibrated_top100_category_distribution.svg` | 보정 Top100 카테고리 분포 |
| `analysis_outputs/imbalance/charts/balanced_category_distribution.svg` | 균형??추천 카테고리 분포 |
| `analysis_outputs/imbalance/charts/category_distribution_comparison.svg` | ?�본/기존/보정/균형??카테고리 분포 비교 |
| `analysis_outputs/imbalance/charts/imbalance_key_metrics.svg` | 불균???�심 지??카드 |

관???�크립트:

| ?�일 | ?�명 |
| --- | --- |
| `src/run_imbalance_balanced_recommendations.py` | 불균??진단, 균형??추천, ?�각???�성 |

?�심 발표 ?�치:

- ?�본 최�? 카테고리 비중: 64.5%
- 기존 Top100 최�? 카테고리 비중: 92.0%
- 보정 Top100 최�? 카테고리 비중: 84.0%
- 균형??추천 최�? 카테고리 비중: 42.9%

## 2026-05-18 피드백 기반 보완 산출물

위치:

- `docs/feedback_based_code_enhancement.md`
- `analysis_outputs/roi/`

| 파일 | 설명 |
| --- | --- |
| `docs/feedback_based_code_enhancement.md` | 받은 피드백을 코드 보완 항목으로 변환한 실행 계획 및 반영 내역 |
| `src/run_roi_simulation.py` | 분류 확률 기반 매장별 ROI 시뮬레이션 스크립트 |
| `analysis_outputs/roi/roi_simulation_by_store.csv` | 매장별·시나리오별 기대 추가 주문, 기대 마진, 기대 ROI |
| `analysis_outputs/roi/roi_simulation_summary.csv` | 시나리오별 ROI 요약 |
| `analysis_outputs/roi/roi_top20_base.csv` | 기본 시나리오 기준 ROI 상위 20개 매장 |
| `analysis_outputs/roi/roi_simulation_report.md` | ROI 시뮬레이션 발표용 해석 문서 |

핵심 발표 수치:

- Growth Alpha + NLP AUC: 0.6148
- Growth Alpha + NLP F1: 0.5250
- 기존 Growth Alpha AUC 대비 개선: +0.0070
- 기본 ROI 시나리오 ROI 양수 매장: 844/1,246
- 기본 ROI 시나리오 평균 기대 ROI: 59,377원

## 2026-05-18 코멘트 반영 EDA 산출물

위치:

- `analysis_outputs/feedback_eda/`

| 파일 | 설명 |
| --- | --- |
| `feedback_eda_report.md` | 피드백 코멘트 반영 현황과 EDA 핵심 근거를 통합한 발표용 리포트 |
| `comment_reflection_matrix.csv` | 코멘트별 코드/분석 반영 내역, 증거 파일, 발표 문장 |
| `eda_label_gap_summary.csv` | 성장/비성장 그룹의 주문, 리뷰, 운영, Growth Alpha 차이 |
| `eda_nlp_gap_summary.csv` | 리뷰 텍스트 감성/주제 지표의 성장 라벨별 차이 |
| `eda_external_gap_summary.csv` | 서울 외부 상권 지표의 성장 라벨별 차이 |
| `eda_model_lift_summary.csv` | Baseline, Growth Alpha, Growth Alpha + NLP 분류 성능 비교 |
| `eda_roi_by_grade_summary.csv` | 기본 ROI 시나리오 기준 등급별 기대 ROI |
| `charts/` | 피드백 반영 EDA 시각화 6개 |

핵심 시각화:

- `label_relative_gap.svg`
- `label_mean_comparison.svg`
- `nlp_mean_comparison.svg`
- `external_market_comparison.svg`
- `model_auc_comparison.svg`
- `roi_by_grade_base.svg`

### 2026-05-18 피드백 EDA 리디자인 및 심화 분석 업데이트

`analysis_outputs/feedback_eda/charts/`의 라이트 테마 색상과 레이아웃으로 전면 교체하고, 다음 심화 EDA 산출물을 추가했다.

새 CSV:

- `eda_model_decile_lift.csv`: NLP 결합 모델 예측 확률 decile별 실제 성장률과 lift
- `eda_score_decile_profile.csv`: GroMong Score decile별 평균 확률, Growth Alpha 점수, 서울 외부데이터 비중

새/갱신 차트:

- `effect_size_heatmap.svg`
- `model_decile_lift.svg`
- `nlp_relative_gap.svg`
- `score_decile_profile.svg`
- 기존 6개 차트도 라이트 카드형 스타일로 재생성

핵심 수치:

- 주문수 상대 차이: +148.13%
- 리뷰수 상대 차이: +69.12%
- 주문수 Cohen's d: 0.4162
- Growth Alpha + NLP AUC: 0.6148
- 최상위 예측 decile 실제 성장률: 40.40%
- 최하위 예측 decile 실제 성장률: 10.80%
- A등급 평균 기대 ROI: 150,409원
- D등급 평균 기대 ROI: -22,198원


### 피드백 반영 및 EDA 상세 보고서

최종 피드백 보완 보고서:

- `analysis_outputs/feedback_eda/feedback_reflection_detailed_report.md`

보고서 포함 내용:

- 피드백별 기존 한계, 코드/분석 보완 내용, 근거 산출물, 반영 상태
- 성장/비성장 운영 지표 EDA 및 효과크기
- 리뷰 텍스트 감성/부정 리뷰율/재주문 언급률 EDA
- 외부 상권 변수 EDA와 해석 한계
- 분류 모델 성능 및 예측 확률 구간별 실제 성장률
- 등급별 기대 월간 투자효과
- 그로몽 점수 구간별 구성 profile
- EDA 차트 10개 포함

발표용 핵심 문장:

```text
피드백을 반영해 인과추론은 평균 효과 검증 근거로 두고,
최종 의사결정은 성장 유망 매장 분류 모델, GroMong Score,
투자효과 시뮬레이션으로 연결했다.
```
- 피드백 EDA 그래프는 `.venv` 가상환경의 `matplotlib`만 사용해 재생성했다.

