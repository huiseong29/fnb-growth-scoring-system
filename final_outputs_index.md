# Final Outputs Index

이 문서는 프로젝트 산출물의 위치와 용도를 정리한다.

프로젝트 주제:

**AI 기반 F&B 성장 유망 매장 스코어링 시스템**

핵심 차별점:

**외부 상권 데이터와 Growth Alpha를 활용해 상권·브랜드·카테고리 효과를 보정한 성장 유망 매장 선별**

## 1. 핵심 문서

| 파일 | 설명 |
| --- | --- |
| `project_plan.md` | 전체 실행 계획, 완료 상태, 다음 작업 |
| `project_proposal.md` | 프로젝트 기획서, 문제 정의, 방법론, 결과 해석 |
| `remaining_tasks.md` | 앞으로 남은 작업 체크리스트 |
| `final_outputs_index.md` | 전체 산출물 인덱스 |
| `analysis_outputs/visualization_guide.md` | 모든 시각화 파일의 목적, 해석, 발표용 문장 |
| `score_design_rationale.md` | GroMong Score 5개 지수와 가중치 설계 근거 |
| `midterm_quality_boost_plan.md` | 중간발표 1등 퀄리티를 위한 보강 과제 로드맵 |

## 2. 원본 데이터

위치:

- `data/`

주요 파일:

| 파일 | 설명 |
| --- | --- |
| `매장_식별_데이터.json` | 매장 ID, 브랜드, 카테고리, 주소, 실험군/통제군 |
| `처치_시점_정의_데이터.json` | 매장별 서비스 동의/처치 시점 |
| `order_주요_성과_변수.json` | 주문일, 가격, 수량, 주문 ID |
| `reviews_주요_성과_변수.json` | 리뷰 내용, 평점, 답글, 답글 시점 |
| `20260310_통제변수.json` | 메뉴 상태, 메뉴 가격, 메뉴 수 관련 데이터 |
| `final_shop_address.xlsx` | 매장 주소 보조 데이터 |

## 3. 외부 데이터

위치:

- `external_data/`

| 파일 | 설명 |
| --- | --- |
| `seoul_sales_hdong_2024.zip` | 서울시 상권분석서비스 2024년 행정동 추정매출 데이터 |
| `seoul_sales_2024.zip` | 서울시 상권분석서비스 2024년 상권 단위 추정매출 데이터 |
| `seoul_store_external_features_2024q4.csv` | 내부 서울 매장 211개에 결합한 외부 상권 변수 |

외부 데이터 결합 결과:

- 서울 매장 211개
- 자치구 기준 매칭률 100%
- 내부 카테고리와 외부 업종 매핑률 100%

## 4. 분석용 데이터 마트

| 파일 | 설명 |
| --- | --- |
| `analysis_outputs/store_month_panel.csv` | 매장-월 단위 분석 패널 |

패널 정보:

- 매장 수: 1,246
- 기간: 2024-11 ~ 2025-12
- 행 수: 17,444
- 성장 라벨 유효 행: 11,214
- 서울 외부 상권 결합 매장: 211

## 5. EDA 산출물

위치:

- `analysis_outputs/eda/`

| 파일 | 설명 |
| --- | --- |
| `eda_report.md` | EDA 요약 리포트 |
| `eda_label_summary.csv` | 성장 라벨별 주요 지표 요약 |
| `eda_brand_summary.csv` | 브랜드별 성장 라벨 분포 |
| `eda_category_summary.csv` | 카테고리별 성장 라벨 분포 |
| `eda_brand_category_summary.csv` | 브랜드·카테고리별 성장 라벨 분포 |
| `eda_growth_alpha_top_bottom.csv` | Growth Alpha 상하위 매장 |
| `eda_monthly_trend.csv` | 월별 추이 |
| `eda_correlations.csv` | 주요 변수와 성장 점수 상관 |
| `eda_seoul_external_label_summary.csv` | 서울 외부 변수 라벨별 요약 |
| `eda_seoul_gu_category_summary.csv` | 서울 자치구·카테고리별 요약 |

## 6. EDA 시각화

위치:

- `analysis_outputs/eda/charts/`

| 파일 | 설명 |
| --- | --- |
| `label_avg_order_count.svg` | 성장/비성장 평균 주문수 비교 |
| `label_avg_review_count.svg` | 성장/비성장 평균 리뷰수 비교 |
| `label_avg_reply_rate.svg` | 성장/비성장 평균 답글률 비교 |
| `label_avg_growth_alpha.svg` | 성장/비성장 Growth Alpha 비교 |
| `brand_category_growth_rate.svg` | 브랜드·카테고리별 성장 비율 |
| `monthly_avg_orders_by_label.svg` | 성장 라벨별 월별 평균 주문수 추이 |

각 그래프의 해석:

- `analysis_outputs/visualization_guide.md`

## 7. 모델링 산출물

위치:

- `analysis_outputs/modeling/`

| 파일 | 설명 |
| --- | --- |
| `modeling_report.md` | Baseline vs Growth Alpha 모델 결과 요약 |
| `model_comparison.csv` | 모델 성능 비교 |
| `model_predictions.csv` | 매장-월별 예측 확률 |
| `model_coefficients.csv` | 로지스틱 회귀 계수 |
| `model_topn_metrics.csv` | Top N 추천 성능 |

핵심 결과:

- Baseline AUC: 0.6060
- Growth Alpha AUC: 0.6078
- Baseline Top 100 Precision: 0.400
- Growth Alpha Top 100 Precision: 0.420

## 8. 서울 외부 상권 모델링 산출물

위치:

- `analysis_outputs/seoul_external_modeling/`

| 파일 | 설명 |
| --- | --- |
| `seoul_external_modeling_report.md` | 서울 외부 상권 모델 결과 요약 |
| `seoul_external_model_comparison.csv` | 서울 내부 모델 vs 외부 결합 모델 비교 |
| `seoul_external_predictions.csv` | 서울 매장 예측 결과 |
| `seoul_external_coefficients.csv` | 모델 계수 |
| `seoul_external_topn_metrics.csv` | Top N 추천 성능 |
| `seoul_external_top_store_examples.csv` | 상위 추천 매장 예시 |

핵심 결과:

- Seoul Internal AUC: 0.5826
- Seoul External AUC: 0.5995
- Seoul Internal Top 100 Precision: 0.340
- Seoul External Top 100 Precision: 0.370

## 9. GroMong Score 산출물

위치:

- `analysis_outputs/scoring/`

| 파일 | 설명 |
| --- | --- |
| `store_scores.csv` | 매장별 GroMong Score, 등급, 구성 점수 |
| `store_score_explanations.csv` | 매장별 점수와 주요 근거 3개 |
| `score_summary.md` | 스코어 산출 요약 |
| `score_design_rationale.md` | 스코어 설계 근거, 지수별 사용 변수, 한계와 고도화 방향 |

핵심 결과:

- 기준 월: 2025-09
- 점수 산출 매장 수: 1,246
- 평균 점수: 53.28
- 중앙값 점수: 53.90
- 최고 점수: 98.18

등급 분포:

| 등급 | 매장 수 |
| --- | ---: |
| A | 84 |
| B | 234 |
| C | 365 |
| D | 563 |

## 10. 스코어링 시각화

위치:

- `analysis_outputs/scoring/charts/`

| 파일 | 설명 |
| --- | --- |
| `score_distribution.svg` | GroMong Score 분포 |
| `grade_counts.svg` | A/B/C/D 등급별 매장 수 |
| `brand_avg_score.svg` | 브랜드별 평균 점수 |
| `category_avg_score.svg` | 카테고리별 평균 점수 |
| `growth_alpha_vs_score.svg` | Growth Alpha와 최종 점수 관계 |
| `seoul_market_ticket_ratio_vs_score.svg` | 서울 매장 상권 객단가 대비 점수 관계 |
| `top20_store_scores.svg` | 최종 점수 상위 20개 매장 |

각 그래프의 해석:

- `analysis_outputs/visualization_guide.md`

## 11. 스크립트

| 파일 | 설명 |
| --- | --- |
| `check_external_fit.py` | 서울 외부 상권 데이터 결합 가능성 확인 |
| `build_store_month_panel.py` | 매장-월 패널 생성 |
| `run_eda.py` | EDA 요약 산출 |
| `make_eda_charts.py` | EDA 시각화 생성 |
| `run_modeling.py` | Baseline vs Growth Alpha 모델링 |
| `run_seoul_external_modeling.py` | 서울 외부 상권 모델링 |
| `build_scores.py` | GroMong Score 산출 |
| `make_score_charts.py` | 스코어링 시각화 생성 |

## 12. 아직 생성 예정인 산출물

| 예정 파일 | 설명 |
| --- | --- |
| `app.py` | 매장 ID 입력형 데모 |
| `analysis_outputs/demo/` | 데모 설명 및 검증 결과 |
| `analysis_outputs/demo/demo_guide.md` | 데모 사용법 및 화면 설명 |
| `analysis_outputs/demo/demo_visualization_guide.md` | 데모 시각화 설명 |
| `analysis_outputs/demo/demo_validation.md` | 데모 API 및 예외 처리 검증 결과 |

## 12. 데모 산출물

| 파일 | 설명 |
| --- | --- |
| `app.py` | 표준 라이브러리 기반 데모 서버 |
| `analysis_outputs/demo/demo_guide.md` | 데모 실행 방법, 화면 구성, 시연 흐름 |
| `analysis_outputs/demo/demo_visualization_guide.md` | 점수 게이지, 등급 배지, 구성요소 bar chart 등 데모 시각 요소 해석 |
| `analysis_outputs/demo/demo_validation.md` | 데모 API 응답 및 없는 ID 예외 처리 검증 |

## 13. 중간발표 보강 산출물

| 파일 | 설명 |
| --- | --- |
| `midterm_quality_boost_plan.md` | 부족한 부분과 보강 과제 정리 |
| `analysis_outputs/quality_boost/charts/quality_boost_roadmap.svg` | 중간발표 보강 로드맵 시각화 |
| `analysis_outputs/quality_boost/quality_boost_visualization_guide.md` | 보강 로드맵 시각화 해석 |

진행 중인 추가 산출물:

- `analysis_outputs/nlp/`

실행 주소:

```text
http://127.0.0.1:8765
```

실행 명령:

```powershell
& 'C:\Users\tobes\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' app.py
```

## 15. 운영 원칙

앞으로 작업 하나를 완료할 때마다 다음을 반드시 업데이트한다.

- `project_plan.md`
- `project_proposal.md`
- `remaining_tasks.md`
- `final_outputs_index.md`
- `analysis_outputs/visualization_guide.md`

시각화가 생성되면 반드시 다음을 함께 문서화한다.

- 그래프 목적
- 핵심 수치
- 해석
- 발표용 문장
- 주의점 또는 한계
## 2026-05-08 추가 산출물: 리뷰 원문 NLP 분석

위치:

- `analysis_outputs/nlp/`

| 파일 | 설명 |
| --- | --- |
| `review_text_features.csv` | 리뷰 원문별 긍정/부정 키워드, 주제 태그, 텍스트 감성 점수 |
| `review_store_month_sentiment.csv` | 매장-월 단위 리뷰 감성 집계 |
| `review_sentiment_summary.csv` | 성장 상위 매장과 성장 외 매장의 리뷰 감성 비교 |
| `review_category_sentiment_summary.csv` | 카테고리별 성장 상위/성장 외 리뷰 감성 비교 |
| `positive_keyword_top50.csv` | 긍정 키워드 상위 50개 |
| `negative_keyword_top50.csv` | 부정 키워드 상위 50개 |
| `rating_sentiment_mismatch_examples.csv` | 별점과 텍스트 감성이 어긋나는 리뷰 사례 |
| `review_sentiment_report.md` | 리뷰 NLP 요약 보고서 |
| `review_nlp_visualization_guide.md` | 리뷰 NLP 시각화별 해석 문서 |

시각화:

| 파일 | 설명 |
| --- | --- |
| `analysis_outputs/nlp/charts/sentiment_by_growth_label.svg` | 성장 상위/성장 외 매장의 텍스트 감성, 긍정률, 부정률 비교 |
| `analysis_outputs/nlp/charts/review_topic_rates_by_growth_label.svg` | 맛, 양, 배달, 가격, 서비스, 재주문 주제 언급률 비교 |
| `analysis_outputs/nlp/charts/positive_keywords_top20.svg` | 긍정 키워드 상위 20개 |
| `analysis_outputs/nlp/charts/negative_keywords_top20.svg` | 부정 키워드 상위 20개 |
| `analysis_outputs/nlp/charts/category_sentiment_by_growth_label.svg` | 카테고리별 평균 텍스트 감성 비교 |
| `analysis_outputs/nlp/charts/rating_sentiment_mismatch_counts.svg` | 별점과 텍스트 감성 불일치 사례 수 |

관련 스크립트:

| 파일 | 설명 |
| --- | --- |
| `run_review_nlp.py` | 리뷰 원문 기반 키워드 감성/주제 분석 |
| `make_review_nlp_charts.py` | 리뷰 NLP 결과 시각화 생성 |

핵심 발표 수치:

- 성장 상위 매장 평균 텍스트 감성: 0.6831
- 성장 외 매장 평균 텍스트 감성: 0.6709
- 성장 상위 매장 긍정 리뷰 비율: 87.10%
- 성장 외 매장 긍정 리뷰 비율: 85.62%
- 성장 상위 매장 부정 리뷰 비율: 3.10%
- 성장 외 매장 부정 리뷰 비율: 4.00%
- 성장 상위 매장 재주문 언급률: 7.20%
- 성장 외 매장 재주문 언급률: 6.44%

다음 생성 예정 산출물:

- `analysis_outputs/sensitivity/`
- GroMong Score 가중치 민감도 분석 결과
- 가중치 시나리오별 Top 매장 안정성 시각화
## 2026-05-08 추가 산출물: 스코어 가중치 민감도 분석

위치:

- `analysis_outputs/sensitivity/`

| 파일 | 설명 |
| --- | --- |
| `score_sensitivity_summary.csv` | 가중치 시나리오별 평균 점수, Top50/Top100 겹침률, 순위 상관, 등급 분포 |
| `score_sensitivity_detail.csv` | 매장별 시나리오별 재계산 점수 |
| `top100_stability.csv` | 현재 상위 매장의 시나리오별 Top100 유지 횟수 |
| `score_sensitivity_report.md` | 가중치 민감도 분석 요약 보고서 |
| `score_sensitivity_visualization_guide.md` | 가중치 민감도 시각화별 해석 문서 |

시각화:

| 파일 | 설명 |
| --- | --- |
| `analysis_outputs/sensitivity/charts/top100_overlap_by_scenario.svg` | 현재 Top100과 대체 가중치 Top100의 겹침률 |
| `analysis_outputs/sensitivity/charts/rank_correlation_by_scenario.svg` | 현재 순위와 대체 가중치 순위의 상관 |
| `analysis_outputs/sensitivity/charts/mean_score_by_scenario.svg` | 시나리오별 평균 점수 |
| `analysis_outputs/sensitivity/charts/grade_counts_by_scenario.svg` | 시나리오별 A/B/C/D 등급 분포 |
| `analysis_outputs/sensitivity/charts/top100_stability_top20.svg` | 현재 상위 20개 매장의 Top100 유지 횟수 |

관련 스크립트:

| 파일 | 설명 |
| --- | --- |
| `run_score_sensitivity.py` | GroMong Score 가중치 민감도 분석 및 시각화 생성 |

핵심 발표 수치:

- 대체 가중치 시나리오 Top100 겹침률 범위: 78~95%
- 대체 가중치 시나리오 순위 상관 범위: 0.959~0.995
- 현재 상위 20개 매장: 7개 시나리오 모두에서 Top100 유지

다음 생성 예정 산출물:

- `analysis_outputs/calibrated_score/`
- 브랜드/카테고리 보정 점수
- 카테고리 내부 Top 매장 시각화
## 2026-05-08 추가 산출물: 브랜드/카테고리 보정 점수

위치:

- `analysis_outputs/calibrated_score/`

| 파일 | 설명 |
| --- | --- |
| `calibrated_store_scores.csv` | 매장별 기존 점수, 브랜드 내부 percentile, 카테고리 내부 percentile, 보정 점수 |
| `category_top10_calibrated.csv` | 카테고리별 보정 점수 Top10 매장 |
| `brand_top10_calibrated.csv` | 브랜드별 보정 점수 Top10 매장 |
| `calibration_group_summary.csv` | 브랜드/카테고리별 보정 전후 요약 |
| `top100_calibration_overlap.csv` | 기존 Top100과 보정 Top100 겹침률 |
| `calibrated_score_report.md` | 보정 점수 분석 요약 보고서 |
| `calibrated_score_visualization_guide.md` | 보정 점수 시각화별 해석 문서 |

시각화:

| 파일 | 설명 |
| --- | --- |
| `analysis_outputs/calibrated_score/charts/overall_vs_calibrated_score.svg` | 기존 GroMong Score와 보정 점수 관계 |
| `analysis_outputs/calibrated_score/charts/category_top100_counts_before_after.svg` | 카테고리별 Top100 포함 매장 수 변화 |
| `analysis_outputs/calibrated_score/charts/category_avg_score_before_after.svg` | 카테고리별 평균 점수 변화 |
| `analysis_outputs/calibrated_score/charts/brand_A_counts_before_after.svg` | 브랜드별 A등급 매장 수 변화 |
| `analysis_outputs/calibrated_score/charts/top100_overlap_after_calibration.svg` | 기존 Top100과 보정 Top100 겹침 및 신규 진입 |
| `analysis_outputs/calibrated_score/charts/category_top10_calibrated_scores.svg` | 카테고리별 보정 점수 Top 후보 |

관련 스크립트:

| 파일 | 설명 |
| --- | --- |
| `run_calibrated_score.py` | 브랜드/카테고리 보정 점수 생성 및 시각화 |

핵심 발표 수치:

- 기존 Top100과 보정 Top100 겹침: 92개
- 보정 후 신규 Top100 진입: 8개
- 굽네치킨 Top100 포함: 8개에서 16개
- 치킨 Top100 포함: 7개에서 11개
- 피자 Top100 포함: 1개에서 5개

다음 생성 예정 산출물:

- 최종 발표용 결과 정리 문서
- 발표 그래프 목록
- 발표 멘트 및 방어 논리 문서
## 2026-05-08 생성 예정 산출물: 불균형 진단과 균형형 추천

예정 위치:

- `analysis_outputs/imbalance/`

예정 산출물:

| 파일 | 설명 |
| --- | --- |
| `imbalance_summary.csv` | 원본/기존 Top100/보정 Top100의 브랜드·카테고리 분포 |
| `balanced_recommendations.csv` | 카테고리와 브랜드 균형을 고려한 추천 후보 |
| `imbalance_defense_report.md` | 데이터 불균형 한계와 방어 논리 |
| `imbalance_visualization_guide.md` | 불균형 시각화별 해석 문서 |
| `charts/` | 불균형 진단 및 균형형 추천 시각화 |
## 2026-05-08 추가 산출물: 불균형 진단과 균형형 추천

위치:

- `analysis_outputs/imbalance/`

| 파일 | 설명 |
| --- | --- |
| `imbalance_summary.csv` | 원본/기존 Top100/보정 Top100/균형형 추천의 브랜드·카테고리 분포 |
| `imbalance_metrics.csv` | HHI, 최대 브랜드 비중, 최대 카테고리 비중 등 편중 지표 |
| `balanced_recommendations.csv` | 브랜드/카테고리 균형을 고려한 보조 추천 후보군 |
| `imbalance_defense_report.md` | 데이터 불균형 한계와 발표용 방어 논리 |
| `imbalance_visualization_guide.md` | 불균형 시각화별 해석 문서 |

시각화:

| 파일 | 설명 |
| --- | --- |
| `analysis_outputs/imbalance/charts/original_brand_distribution.svg` | 원본 데이터 브랜드 분포 |
| `analysis_outputs/imbalance/charts/original_category_distribution.svg` | 원본 데이터 카테고리 분포 |
| `analysis_outputs/imbalance/charts/current_top100_category_distribution.svg` | 기존 Top100 카테고리 분포 |
| `analysis_outputs/imbalance/charts/calibrated_top100_category_distribution.svg` | 보정 Top100 카테고리 분포 |
| `analysis_outputs/imbalance/charts/balanced_category_distribution.svg` | 균형형 추천 카테고리 분포 |
| `analysis_outputs/imbalance/charts/category_distribution_comparison.svg` | 원본/기존/보정/균형형 카테고리 분포 비교 |
| `analysis_outputs/imbalance/charts/imbalance_key_metrics.svg` | 불균형 핵심 지표 카드 |

관련 스크립트:

| 파일 | 설명 |
| --- | --- |
| `run_imbalance_balanced_recommendations.py` | 불균형 진단, 균형형 추천, 시각화 생성 |

핵심 발표 수치:

- 원본 최대 카테고리 비중: 64.5%
- 기존 Top100 최대 카테고리 비중: 92.0%
- 보정 Top100 최대 카테고리 비중: 84.0%
- 균형형 추천 최대 카테고리 비중: 42.9%
