# AI 기반 F&B 성장 유망 매장 스코어링 시스템 실행 계획서

## 1. 프로젝트 기준

본 프로젝트의 주제는 **AI 기반 F&B 성장 유망 매장 스코어링 시스템**이다.

핵심 차별점은 단순히 주문수, 리뷰수, 평점이 높은 매장을 찾는 것이 아니라, **브랜드, 카테고리, 상권 효과를 보정한 뒤 매장 자체의 초과 성장 잠재력(Growth Alpha)을 점수화한다는 점**이다.

현재 제공 데이터는 본그룹과 굽네치킨 중심의 파일럿 데이터셋이므로, 전체 F&B 시장을 완전히 대표한다고 주장하지 않는다. 대신 제공된 실제 운영 데이터를 기반으로 F&B 성장 유망 매장 스코어링 방법론을 설계하고, 이를 파일럿 검증한다.

## 2. 현재 완료 상태

### 2.1 데이터 구조 확인

- 매장 식별 데이터: 1,252행, 고유 매장 1,246개
- 처치 시점 데이터: 1,252행, 고유 매장 1,246개
- 주문 데이터: 1,869,530행, 고유 매장 1,060개
- 리뷰 데이터: 202,746행, 고유 매장 1,117개
- 메뉴판 통제변수 데이터: 132,959행, 고유 매장 1,222개
- 주소 데이터: 12,697행

### 2.2 외부 데이터 결합 검증

서울시 상권분석서비스 2024년 행정동 추정매출 데이터를 다운로드하여 내부 데이터와 결합 가능성을 검증했다.

- 서울 매장 수: 211개
- 자치구 기준 매칭률: 211 / 211
- 업종 매핑률: 211 / 211

업종 매핑 기준:

| 내부 카테고리 | 외부 상권 업종 |
| --- | --- |
| 백반·죽·국수 | 한식음식점, 분식전문점 |
| 치킨 | 치킨전문점 |
| 피자 | 패스트푸드점, 양식음식점 |

### 2.3 분석용 패널 생성

생성 파일:

- `analysis_outputs/store_month_panel.csv`

패널 구조:

- 행 수: 17,444
- 매장 수: 1,246
- 기간: 2024-11 ~ 2025-12
- 컬럼 수: 47
- 성장 라벨 생성 가능 행: 11,214
- 성장 라벨 1: 3,365
- 성장 라벨 0: 7,849
- 서울 외부 상권 데이터 결합 매장: 211개

### 2.4 EDA 완료

EDA 산출물:

- `analysis_outputs/eda/eda_report.md`
- `analysis_outputs/eda/eda_label_summary.csv`
- `analysis_outputs/eda/eda_brand_category_summary.csv`
- `analysis_outputs/eda/eda_growth_alpha_top_bottom.csv`
- `analysis_outputs/eda/charts/`

주요 결과:

- 성장 라벨 1 그룹 평균 월 주문수: 169.17
- 성장 라벨 0 그룹 평균 월 주문수: 68.18
- 성장 라벨 1 그룹 평균 월 리뷰수: 14.90
- 성장 라벨 0 그룹 평균 월 리뷰수: 8.81
- 성장 라벨 1 그룹 평균 `internal_growth_alpha`: 2.9508
- 성장 라벨 0 그룹 평균 `internal_growth_alpha`: -1.2651

중요한 해석:

- `internal_growth_alpha`는 미래 성장률에서 파생된 결과 설명용 변수다.
- 예측 모델 입력에는 데이터 누수를 피하기 위해 과거 데이터만으로 계산한 `historical_internal_growth_alpha`를 사용한다.
- 성장 라벨 1 그룹은 주문수, 리뷰수, 답글률에서 성장 라벨 0 그룹보다 높은 경향을 보인다.

### 2.5 Baseline vs Growth Alpha 모델 비교 완료

모델링 산출물:

- `analysis_outputs/modeling/modeling_report.md`
- `analysis_outputs/modeling/model_comparison.csv`
- `analysis_outputs/modeling/model_predictions.csv`
- `analysis_outputs/modeling/model_coefficients.csv`
- `analysis_outputs/modeling/model_topn_metrics.csv`

검증 방식:

- 학습 기간: 2025-01 ~ 2025-07
- 검증 기간: 2025-08 ~ 2025-09
- 목표 변수: `growth_label_top30`
- 모델: 표준화 + 원핫 인코딩 + 로지스틱 회귀

모델 성능:

| 모델 | AUC | F1 | Precision | Recall |
| --- | ---: | ---: | ---: | ---: |
| Baseline | 0.6060 | 0.5173 | 0.3698 | 0.8603 |
| Growth Alpha | 0.6078 | 0.5169 | 0.3694 | 0.8603 |

Top N 결과:

| 모델 | Top 50 Precision | Top 100 Precision | Top 200 Precision |
| --- | ---: | ---: | ---: |
| Baseline | 0.340 | 0.400 | 0.395 |
| Growth Alpha | 0.340 | 0.420 | 0.405 |

해석:

- 과거 기반 Growth Alpha 변수를 추가했을 때 AUC가 0.6060에서 0.6078로 소폭 개선되었다.
- Top 100, Top 200 추천 precision도 Growth Alpha 모델이 Baseline보다 높다.
- 개선 폭은 크지 않으므로 Growth Alpha는 단독 예측 성능 개선 변수라기보다, 브랜드·카테고리 보정 관점의 설명력과 스코어링 차별점으로 활용하는 것이 타당하다.
- 다음 핵심 검증은 서울 매장 211개에서 외부 상권 변수가 실제 성능을 개선하는지 확인하는 것이다.

## 3. 전체 실행 단계

## 공통 산출 원칙

각 분석 단계는 단순히 CSV나 모델 결과만 생성하지 않는다. 앞으로 모든 단계는 다음 산출물을 함께 만든다.

1. 분석 결과 파일
2. 시각화 파일
3. 시각화별 해석 문서
4. `project_plan.md` 업데이트
5. `project_proposal.md` 업데이트

시각화 해석 문서에는 다음 항목을 포함한다.

- 그래프 목적
- 핵심 수치
- 해석
- 발표용 문장
- 주의점 또는 한계

현재까지 생성한 전체 시각화 해석 문서:

- `analysis_outputs/visualization_guide.md`

남은 작업과 전체 산출물 위치는 별도 문서에서 관리한다.

- `remaining_tasks.md`
- `final_outputs_index.md`

스코어 설계 근거는 별도 문서에서 관리한다.

- `score_design_rationale.md`

중간발표 1등 퀄리티를 위한 보강 과제는 별도 문서에서 관리한다.

- `midterm_quality_boost_plan.md`
- `analysis_outputs/quality_boost/charts/quality_boost_roadmap.svg`
- `analysis_outputs/quality_boost/quality_boost_visualization_guide.md`

현재 진행 중인 보강 작업:

- 리뷰 텍스트 감성/키워드 분석

작업을 하나 완료할 때마다 위 두 문서도 함께 업데이트한다.

## Step 1. 패널 EDA

목적은 성장 라벨과 Growth Alpha가 실제로 분석 가능한 신호를 갖고 있는지 확인하는 것이다.

상태: **완료**

### 수행 작업

- 성장 라벨 1 vs 0의 주문수 비교
- 성장 라벨 1 vs 0의 매출 비교
- 성장 라벨 1 vs 0의 리뷰수 비교
- 성장 라벨 1 vs 0의 평점 비교
- 성장 라벨 1 vs 0의 답글률 비교
- 브랜드별 성장 라벨 비율 확인
- 카테고리별 성장 라벨 비율 확인
- `internal_growth_alpha` 상위/하위 매장 확인
- 서울 매장 211개에 대해 외부 상권 변수 분포 확인

### 산출물

- `analysis_outputs/eda_summary.csv`
- `analysis_outputs/eda_growth_alpha_examples.csv`
- `analysis_outputs/eda_charts/`

실제 산출물:

- `analysis_outputs/eda/eda_label_summary.csv`
- `analysis_outputs/eda/eda_brand_summary.csv`
- `analysis_outputs/eda/eda_category_summary.csv`
- `analysis_outputs/eda/eda_brand_category_summary.csv`
- `analysis_outputs/eda/eda_growth_alpha_top_bottom.csv`
- `analysis_outputs/eda/eda_report.md`
- `analysis_outputs/eda/charts/`

## Step 2. Baseline 모델 학습

목적은 내부 데이터만으로 성장 유망 매장을 예측하는 기본 모델을 만드는 것이다.

상태: **완료**

### 입력 변수

- 주문수
- 매출
- 평균 객단가
- 리뷰수
- 평균 평점
- 답글률
- 평균 답글 지연시간
- 메뉴 수
- 평균 메뉴 가격
- 브랜드
- 카테고리
- 지역
- 실험군/통제군
- 홍보문구 여부
- 페르소나 말투 여부

### 목표 변수

- `growth_label_top30`

### 검증 방식

시간 기준 분할을 우선한다.

예시:

- 학습: 2025-01 ~ 2025-07
- 검증: 2025-08 ~ 2025-09

### 산출물

- `analysis_outputs/model_baseline_metrics.csv`
- `analysis_outputs/baseline_predictions.csv`

실제 산출물:

- `analysis_outputs/modeling/model_comparison.csv`
- `analysis_outputs/modeling/model_predictions.csv`
- `analysis_outputs/modeling/model_coefficients.csv`
- `analysis_outputs/modeling/model_topn_metrics.csv`
- `analysis_outputs/modeling/modeling_report.md`

## Step 3. Growth Alpha 포함 모델 학습

목적은 본 프로젝트의 차별점인 Growth Alpha가 성장 예측 성능을 개선하는지 검증하는 것이다.

상태: **완료**

### 추가 변수

- `brand_adjusted_growth`
- `category_adjusted_growth`
- `internal_growth_alpha`

### 비교 구조

| 모델 | 사용 변수 |
| --- | --- |
| Baseline | 내부 운영·주문·리뷰·메뉴 변수 |
| Growth Alpha Model | Baseline + 브랜드/카테고리 보정 성장 변수 |

### 평가 지표

- AUC
- Precision
- Recall
- F1
- Top N 적중률

### 산출물

- `analysis_outputs/model_growth_alpha_metrics.csv`
- `analysis_outputs/model_comparison.csv`

실제 산출물:

- `analysis_outputs/modeling/model_comparison.csv`
- `analysis_outputs/modeling/model_topn_metrics.csv`
- `analysis_outputs/modeling/modeling_report.md`

## Step 4. 외부 상권 데이터 효과 검증

목적은 외부 데이터가 단순 장식이 아니라 실제로 성장 유망 매장 선별에 도움이 되는지 확인하는 것이다.

상태: **완료**

### 분석 대상

- 서울 매장 211개

### 비교 구조

| 모델 | 사용 변수 |
| --- | --- |
| Seoul Internal Model | 내부 변수만 사용 |
| Seoul External Model | 내부 변수 + 외부 상권 변수 |

### 외부 변수

- `market_q4_sales_amount`
- `market_q4_sales_count`
- `market_q4_avg_ticket`
- `store_vs_market_ticket_ratio`

### 산출물

- `analysis_outputs/seoul_external_model_comparison.csv`
- `analysis_outputs/seoul_growth_alpha_examples.csv`

진행 기준:

- 서울 매장 중 외부 상권 변수가 결합된 행만 사용한다.
- 내부 변수만 사용한 모델과 외부 상권 변수를 추가한 모델을 같은 시간 기준 분할로 비교한다.
- 개선 여부는 AUC, F1, Top N precision으로 판단한다.

실제 산출물:

- `analysis_outputs/seoul_external_modeling/seoul_external_modeling_report.md`
- `analysis_outputs/seoul_external_modeling/seoul_external_model_comparison.csv`
- `analysis_outputs/seoul_external_modeling/seoul_external_predictions.csv`
- `analysis_outputs/seoul_external_modeling/seoul_external_coefficients.csv`
- `analysis_outputs/seoul_external_modeling/seoul_external_topn_metrics.csv`
- `analysis_outputs/seoul_external_modeling/seoul_external_top_store_examples.csv`

결과:

| 모델 | AUC | F1 | Precision | Recall |
| --- | ---: | ---: | ---: | ---: |
| Seoul Internal | 0.5826 | 0.4807 | 0.3323 | 0.8689 |
| Seoul External | 0.5995 | 0.4773 | 0.3302 | 0.8607 |

Top N 결과:

| 모델 | Top 50 Precision | Top 100 Precision | Top 200 Precision |
| --- | ---: | ---: | ---: |
| Seoul Internal | 0.360 | 0.340 | 0.325 |
| Seoul External | 0.360 | 0.370 | 0.330 |

해석:

- 외부 상권 변수를 추가했을 때 AUC가 0.5826에서 0.5995로 개선되었다.
- Top 100 precision도 0.340에서 0.370으로 개선되었다.
- 외부 변수 중 `store_vs_market_ticket_ratio`, `market_q4_avg_ticket`이 중요 변수 상위에 포함되었다.
- 이는 외부 상권 데이터가 단순 장식이 아니라 성장 유망 매장 선별에 실질적으로 기여할 수 있음을 보여준다.

## Step 5. 모델 해석

목적은 AI 모델이 어떤 근거로 성장 매장을 판단했는지 설명하는 것이다.

### 수행 작업

- 변수 중요도 산출
- 브랜드 변수가 과도하게 지배하는지 확인
- Growth Alpha 변수의 중요도 확인
- 서울 subset에서 외부 상권 변수의 기여도 확인
- 성장 예측 상위 매장의 공통 패턴 정리

### 산출물

- `analysis_outputs/feature_importance.csv`
- `analysis_outputs/model_interpretation_summary.md`

## Step 6. 그로몽 스코어 산출

목적은 PDF 요구사항에 맞춰 매장별 0~100점 스코어를 산출하는 것이다.

상태: **완료**

### 스코어 예시 공식

```text
GroMong Score =
0.35 * 모델 성장 확률
+ 0.25 * Growth Alpha 점수
+ 0.15 * 리뷰 성장 지수
+ 0.15 * 운영역량 지수
+ 0.10 * 안정성 지수
```

### 등급 기준

| 점수 | 등급 | 의미 |
| --- | --- | --- |
| 80 이상 | A | 투자/지원 우선 검토 |
| 65 ~ 79 | B | 성장 가능성 있음 |
| 50 ~ 64 | C | 관찰 필요 |
| 50 미만 | D | 성장 신호 약함 |

### 산출물

- `analysis_outputs/store_scores.csv`

시각화 산출물:

- 스코어 분포
- 등급별 매장 수
- 브랜드별 평균 스코어
- 카테고리별 평균 스코어
- Growth Alpha vs GroMong Score
- 서울 매장 상권 객단가 대비 스코어
- Top 20 추천 매장

실제 산출물:

- `analysis_outputs/scoring/store_scores.csv`
- `analysis_outputs/scoring/store_score_explanations.csv`
- `analysis_outputs/scoring/score_summary.md`
- `analysis_outputs/scoring/charts/score_distribution.svg`
- `analysis_outputs/scoring/charts/grade_counts.svg`
- `analysis_outputs/scoring/charts/brand_avg_score.svg`
- `analysis_outputs/scoring/charts/category_avg_score.svg`
- `analysis_outputs/scoring/charts/growth_alpha_vs_score.svg`
- `analysis_outputs/scoring/charts/seoul_market_ticket_ratio_vs_score.svg`
- `analysis_outputs/scoring/charts/top20_store_scores.svg`

결과:

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

해석:

- 최종 점수는 모델 성장 확률, 과거 기반 Growth Alpha, 리뷰 성장, 운영역량, 안정성을 결합했다.
- 서울 매장은 외부 상권 평균 객단가 대비 위치를 10% 보정 항목으로 반영했다.
- 상위 매장이 본그룹/백반·죽·국수 카테고리에 많이 분포하는 경향이 있어, 발표에서는 브랜드 편향 점검과 향후 보정 고도화 필요성을 함께 언급한다.
- 5개 지수와 가중치의 세부 설계 근거는 `score_design_rationale.md`에 정리했다.

## Step 7. 매장별 설명 리포트 생성

목적은 모델 결과를 사람이 이해할 수 있는 투자/운영 판단 근거로 변환하는 것이다.

상태: **완료**

### 출력 항목

- 매장 ID
- 브랜드
- 카테고리
- 지역
- 성장 확률
- Growth Alpha
- 그로몽 스코어
- 등급
- 주요 근거 3개

### 산출물

- `analysis_outputs/store_score_explanations.csv`

실제 산출물:

- `analysis_outputs/scoring/store_score_explanations.csv`

## Step 8. 데모 구현

PDF에서 요구하는 필수 구현 화면이다.

상태: **완료**

### 기능

- 매장 ID 입력
- 매장 기본 정보 출력
- 성장 확률 출력
- Growth Alpha 출력
- 그로몽 스코어 출력
- A/B/C/D 등급 출력
- 주요 근거 출력
- 서울 매장은 외부 상권 대비 지표 출력

### 추천 구현 방식

- Streamlit

### 산출물

- `app.py`

실제 산출물:

- `app.py`
- `analysis_outputs/demo/demo_guide.md`
- `analysis_outputs/demo/demo_visualization_guide.md`
- `analysis_outputs/demo/demo_validation.md`

검증 결과:

- `/` HTML 응답 확인
- `/api/store?id=ba_13248384` 정상 응답 확인
- `/api/store?id=missing_shop` 빈 결과 처리 확인
- 점수 게이지, 등급 배지, 구성요소 bar chart, 주요 근거 카드, 서울 외부 상권 지표 표시 구현

## Step 9. 발표용 표와 그래프 정리

### 필수 그래프

- 성장/비성장 매장 주문 추이 비교
- 성장/비성장 매장 리뷰 추이 비교
- 브랜드별 성장률 분포
- 카테고리별 성장률 분포
- Growth Alpha 상위 매장 사례
- Baseline vs Growth Alpha 모델 성능 비교
- 서울 subset 외부 상권 변수 효과 비교

### 산출물

- `presentation_assets/`

## Step 10. 최종 보고서 및 발표자료 구성

### 발표 흐름

1. 문제 정의
2. 데이터 한계와 파일럿 검증 논리
3. 차별점: Growth Alpha
4. 데이터 마트 구축
5. 성장 라벨 정의
6. 모델링
7. 성능 비교
8. 스코어 산출
9. 데모
10. 한계와 확장 방향

## 4. 최우선 다음 작업

가장 먼저 수행할 작업은 **최종 발표용 결과 정리**이다.

이유는 내부 모델, 외부 상권 검증, 최종 GroMong Score, 매장별 설명 근거, 매장 ID 입력형 데모까지 생성되었기 때문이다. 이제 발표자료에 들어갈 핵심 표, 그래프, 발표 문장, 한계와 방어 논리를 정리해야 한다.

다음 단계에서는 다음 산출물을 만든다.

- 발표용 핵심 표
- 발표용 그래프 선별 목록
- 발표 흐름별 멘트
- 한계와 방어 논리
## 2026-05-08 업데이트: 리뷰 원문 NLP 보강 완료

중간발표 1등 수준으로 보이기 위해 필요한 첫 번째 보강 작업인 **리뷰 텍스트 감성/키워드 분석**을 완료했다.

이번 작업의 목적은 기존 주문, 리뷰 수, 평점 중심 분석에서 벗어나, 고객이 실제로 남긴 리뷰 원문에 담긴 긍정/부정 신호와 재주문 의도를 성장 유망 매장 판단 근거로 추가하는 것이다.

산출물:

- `analysis_outputs/nlp/review_text_features.csv`
- `analysis_outputs/nlp/review_store_month_sentiment.csv`
- `analysis_outputs/nlp/review_sentiment_summary.csv`
- `analysis_outputs/nlp/review_category_sentiment_summary.csv`
- `analysis_outputs/nlp/positive_keyword_top50.csv`
- `analysis_outputs/nlp/negative_keyword_top50.csv`
- `analysis_outputs/nlp/rating_sentiment_mismatch_examples.csv`
- `analysis_outputs/nlp/review_sentiment_report.md`
- `analysis_outputs/nlp/review_nlp_visualization_guide.md`
- `analysis_outputs/nlp/charts/sentiment_by_growth_label.svg`
- `analysis_outputs/nlp/charts/review_topic_rates_by_growth_label.svg`
- `analysis_outputs/nlp/charts/positive_keywords_top20.svg`
- `analysis_outputs/nlp/charts/negative_keywords_top20.svg`
- `analysis_outputs/nlp/charts/category_sentiment_by_growth_label.svg`
- `analysis_outputs/nlp/charts/rating_sentiment_mismatch_counts.svg`

핵심 결과:

- 성장 상위 매장 평균 텍스트 감성: 0.6831
- 성장 외 매장 평균 텍스트 감성: 0.6709
- 성장 상위 매장 긍정 리뷰 비율: 87.10%
- 성장 외 매장 긍정 리뷰 비율: 85.62%
- 성장 상위 매장 부정 리뷰 비율: 3.10%
- 성장 외 매장 부정 리뷰 비율: 4.00%
- 성장 상위 매장 재주문 언급률: 7.20%
- 성장 외 매장 재주문 언급률: 6.44%

발표용 해석:

```text
성장 상위 매장은 주문량뿐 아니라 리뷰 원문에서도 긍정 표현이 더 높고 부정 표현이 더 낮았습니다. 특히 재주문 의도 표현이 더 높게 나타나, 고객 언어 신호가 성장 유망 매장 판단의 보조 근거로 활용될 수 있음을 확인했습니다.
```

현재 한계:

- 이번 NLP는 한국어 키워드 사전 기반 파일럿 분석이다.
- 문맥, 반어, 복합 감정을 완벽히 해석하는 딥러닝 감성 모델은 아니다.
- 발표에서는 "리뷰 원문 기반 NLP 파일럿" 또는 "고객 언어 신호 분석"으로 표현한다.

다음 작업:

- GroMong Score 가중치 민감도 분석을 진행한다.
- 현재 5개 지수 가중치가 바뀌어도 상위 매장 추천 결과가 안정적인지 확인한다.
## 2026-05-08 업데이트: GroMong Score 가중치 민감도 분석 완료

중간발표 방어력을 높이기 위한 두 번째 보강 작업인 **스코어 가중치 민감도 분석**을 완료했다.

목적:

- 현재 GroMong Score의 5개 지수 가중치가 임의로 보이지 않도록 검증한다.
- 가중치를 다르게 설정해도 상위 추천 매장이 얼마나 안정적으로 유지되는지 확인한다.

산출물:

- `analysis_outputs/sensitivity/score_sensitivity_summary.csv`
- `analysis_outputs/sensitivity/score_sensitivity_detail.csv`
- `analysis_outputs/sensitivity/top100_stability.csv`
- `analysis_outputs/sensitivity/score_sensitivity_report.md`
- `analysis_outputs/sensitivity/score_sensitivity_visualization_guide.md`
- `analysis_outputs/sensitivity/charts/top100_overlap_by_scenario.svg`
- `analysis_outputs/sensitivity/charts/rank_correlation_by_scenario.svg`
- `analysis_outputs/sensitivity/charts/mean_score_by_scenario.svg`
- `analysis_outputs/sensitivity/charts/grade_counts_by_scenario.svg`
- `analysis_outputs/sensitivity/charts/top100_stability_top20.svg`

핵심 결과:

- 성장확률 강화: Top100 겹침률 91%, 순위 상관 0.990
- Growth Alpha 강화: Top100 겹침률 89%, 순위 상관 0.964
- 리뷰 성장 강화: Top100 겹침률 78%, 순위 상관 0.976
- 운영 역량 강화: Top100 겹침률 94%, 순위 상관 0.983
- 안정성 강화: Top100 겹침률 82%, 순위 상관 0.959
- 서울 상권 적합도 강화: Top100 겹침률 95%, 순위 상관 0.995

발표용 해석:

```text
가중치를 여러 방식으로 바꿔도 현재 Top 100 매장의 78~95%가 유지됐고, 전체 순위 상관도 0.959 이상으로 높게 나타났습니다. 따라서 GroMong Score는 특정 가중치 하나에만 과도하게 의존하지 않는 안정적인 후보 선별 지표라고 설명할 수 있습니다.
```

다음 작업:

- 브랜드/카테고리 보정 점수를 생성한다.
- 전체 Top 순위와 별도로 카테고리 내부 Top 매장을 제시한다.
- 본그룹/굽네치킨 중심 데이터라는 한계를 숨기지 않고 보정 분석으로 방어한다.
## 2026-05-08 업데이트: 브랜드/카테고리 보정 점수 완료

제공 데이터가 본그룹과 굽네치킨 중심이라는 한계를 방어하기 위해 **브랜드/카테고리 보정 점수**를 생성했다.

목적:

- 전체 순위만 제시할 때 발생하는 특정 브랜드/카테고리 편중을 완화한다.
- 같은 브랜드 안에서 잘한 매장, 같은 카테고리 안에서 잘한 매장을 따로 드러낸다.
- 교수님이 "본그룹과 굽네치킨뿐인데 이 주제가 가능한가"라고 질문할 때 방어할 수 있는 근거를 만든다.

보정 공식:

```text
calibrated_score =
0.50 * GroMong Score
+ 0.25 * 브랜드 내부 percentile
+ 0.25 * 카테고리 내부 percentile
```

산출물:

- `analysis_outputs/calibrated_score/calibrated_store_scores.csv`
- `analysis_outputs/calibrated_score/category_top10_calibrated.csv`
- `analysis_outputs/calibrated_score/brand_top10_calibrated.csv`
- `analysis_outputs/calibrated_score/calibration_group_summary.csv`
- `analysis_outputs/calibrated_score/top100_calibration_overlap.csv`
- `analysis_outputs/calibrated_score/calibrated_score_report.md`
- `analysis_outputs/calibrated_score/calibrated_score_visualization_guide.md`
- `analysis_outputs/calibrated_score/charts/overall_vs_calibrated_score.svg`
- `analysis_outputs/calibrated_score/charts/category_top100_counts_before_after.svg`
- `analysis_outputs/calibrated_score/charts/category_avg_score_before_after.svg`
- `analysis_outputs/calibrated_score/charts/brand_A_counts_before_after.svg`
- `analysis_outputs/calibrated_score/charts/top100_overlap_after_calibration.svg`
- `analysis_outputs/calibrated_score/charts/category_top10_calibrated_scores.svg`

핵심 결과:

- 기존 Top100과 보정 Top100 겹침: 92개
- 보정 후 신규 Top100 진입: 8개
- 굽네치킨 Top100 포함 매장: 8개에서 16개
- 치킨 Top100 포함 매장: 7개에서 11개
- 피자 Top100 포함 매장: 1개에서 5개
- 백반·죽·국수 Top100 포함 매장: 92개에서 84개

발표용 해석:

```text
보정 후에도 기존 Top100 중 92개가 유지되어 기존 스코어의 안정성은 유지됐습니다. 동시에 치킨과 피자 카테고리의 상대적 우수 후보가 더 드러나, 특정 브랜드/카테고리 편중을 일부 완화했습니다.
```

다음 작업:

- 최종 발표용 결과 정리
- 핵심 그래프 선별
- 발표 멘트와 방어 논리 문서화
## 2026-05-08 진행 예정: 데이터 불균형 진단과 균형형 추천 보강

현재 프로젝트의 가장 큰 방어 지점은 제공 데이터가 본그룹/굽네치킨, 백반·죽·국수/치킨/피자에 치우쳐 있다는 점이다. 이 한계를 해결하지 않고 전체 Top 순위만 제시하면, 성장 유망 매장 스코어링이 아니라 특정 브랜드/카테고리 추천처럼 보일 위험이 있다.

따라서 다음 작업을 진행한다.

1. 원본 데이터 브랜드/카테고리 분포 진단
2. 기존 Top100의 브랜드/카테고리 편중 진단
3. 보정 Top100의 편중 완화 정도 진단
4. 카테고리별 균형형 추천 리스트 생성
5. 브랜드별 균형형 추천 리스트 생성
6. 중간발표용 방어 문장과 시각화 설명 문서 작성

이번 작업의 발표 목적:

```text
제공 데이터가 특정 브랜드와 카테고리에 치우쳐 있다는 한계를 숨기지 않고, 불균형을 직접 진단한 뒤 전체 추천과 균형형 추천을 함께 제시해 분석의 공정성과 설명력을 높인다.
```
## 2026-05-08 업데이트: 데이터 불균형 진단과 균형형 추천 완료

불균형 문제를 발표에서 방어할 수 있도록 별도 분석과 균형형 추천 후보군을 생성했다.

산출물:

- `analysis_outputs/imbalance/imbalance_summary.csv`
- `analysis_outputs/imbalance/imbalance_metrics.csv`
- `analysis_outputs/imbalance/balanced_recommendations.csv`
- `analysis_outputs/imbalance/imbalance_defense_report.md`
- `analysis_outputs/imbalance/imbalance_visualization_guide.md`
- `analysis_outputs/imbalance/charts/original_brand_distribution.svg`
- `analysis_outputs/imbalance/charts/original_category_distribution.svg`
- `analysis_outputs/imbalance/charts/current_top100_category_distribution.svg`
- `analysis_outputs/imbalance/charts/calibrated_top100_category_distribution.svg`
- `analysis_outputs/imbalance/charts/balanced_category_distribution.svg`
- `analysis_outputs/imbalance/charts/category_distribution_comparison.svg`
- `analysis_outputs/imbalance/charts/imbalance_key_metrics.svg`

핵심 결과:

- 원본 최대 카테고리 비중: 64.5%
- 기존 Top100 최대 카테고리 비중: 92.0%
- 보정 Top100 최대 카테고리 비중: 84.0%
- 균형형 추천 최대 카테고리 비중: 42.9%
- 기존 Top100과 보정 Top100 겹침: 92개
- 보정 Top100 신규 진입: 8개

발표용 해석:

```text
데이터 불균형은 실제로 심합니다. 그래서 전체 F&B 시장을 완전히 대표한다고 주장하지 않고, 제공된 실제 운영 데이터 안에서 성장 유망 매장을 선별하는 파일럿 모델로 정의했습니다. 또한 원본 분포, 기존 Top100, 보정 Top100, 균형형 추천을 모두 비교해 한계를 숨기지 않고 보정했습니다.
```

현재 발표 구조는 2트랙으로 가져간다.

1. 전체 성장 가능성 Top 후보
2. 브랜드/카테고리 균형형 후보

다음 작업:

- 최종 발표용 결과 정리
- 핵심 그래프 선별
- 발표 멘트와 예상 질문 방어 문서 작성
