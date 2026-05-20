# Visualization Guide

이 문서는 프로젝트에서 생성한 시각화 결과물의 목적, 해석, 발표 활용 문장을 정리한다.

프로젝트의 기준 주제는 **AI 기반 F&B 성장 유망 매장 스코어링 시스템**이며, 핵심 차별점은 **브랜드·카테고리·상권 효과를 보정한 Growth Alpha 기반 평가**이다.

## 1. EDA 시각화

위치:

- `analysis_outputs/eda/charts/`

## 1.1 `label_avg_order_count.svg`

파일:

- `analysis_outputs/eda/charts/label_avg_order_count.svg`

목적:

- 성장 라벨 1 그룹과 성장 라벨 0 그룹의 평균 월 주문수를 비교한다.
- 성장 라벨이 실제 주문 성과 차이를 반영하는지 확인한다.

핵심 수치:

- 성장 라벨 1 평균 월 주문수: 169.17
- 성장 라벨 0 평균 월 주문수: 68.18

해석:

- 성장 라벨 1 그룹은 성장 라벨 0 그룹보다 월 주문수가 약 2.5배 높다.
- 성장 라벨이 단순히 임의로 만들어진 값이 아니라, 실제 주문 성과와 연결되어 있음을 보여준다.

발표용 문장:

```text
성장 라벨 1 그룹은 비성장 그룹보다 평균 월 주문수가 뚜렷하게 높았습니다. 따라서 본 프로젝트의 성장 라벨은 실제 주문 성과 차이를 반영하는 기준으로 볼 수 있습니다.
```

주의점:

- 주문수가 높은 매장이 반드시 미래 성장성이 높다는 뜻은 아니다.
- 이후 모델링에서는 주문 규모뿐 아니라 리뷰, 운영역량, Growth Alpha를 함께 반영해야 한다.

## 1.2 `label_avg_review_count.svg`

파일:

- `analysis_outputs/eda/charts/label_avg_review_count.svg`

목적:

- 성장 라벨별 평균 월 리뷰 수 차이를 확인한다.
- 리뷰 활동성이 성장 매장과 관련 있는지 점검한다.

핵심 수치:

- 성장 라벨 1 평균 월 리뷰수: 14.90
- 성장 라벨 0 평균 월 리뷰수: 8.81

해석:

- 성장 라벨 1 그룹은 리뷰 발생량도 더 높다.
- 주문 성장과 리뷰 성장 간에 일정한 동행 관계가 있음을 시사한다.

발표용 문장:

```text
성장 매장 그룹은 주문뿐 아니라 리뷰 발생량도 높았습니다. 이는 리뷰 데이터가 성장 유망 매장 스코어링에서 중요한 행동 신호로 활용될 수 있음을 보여줍니다.
```

주의점:

- 리뷰 수는 매장 규모의 영향을 받을 수 있으므로, 단독 지표가 아니라 성장률과 안정성 지표로 보완해야 한다.

## 1.3 `label_avg_reply_rate.svg`

파일:

- `analysis_outputs/eda/charts/label_avg_reply_rate.svg`

목적:

- 성장 라벨별 평균 답글률 차이를 비교한다.
- 운영역량 또는 고객 대응 신호가 성장 그룹에서 더 강한지 확인한다.

핵심 수치:

- 성장 라벨 1 평균 답글률: 0.5505
- 성장 라벨 0 평균 답글률: 0.4702

해석:

- 성장 라벨 1 그룹의 답글률이 더 높다.
- 이는 리뷰 대응이 성장성과 관련된 운영 신호일 가능성을 보여준다.

발표용 문장:

```text
성장 그룹은 리뷰 답글률도 더 높았습니다. 따라서 단순 주문 성과뿐 아니라 사장님의 고객 대응 활동 역시 성장 유망성 판단에 포함할 필요가 있습니다.
```

주의점:

- 답글률이 성장의 원인인지 결과인지는 이 그래프만으로 단정할 수 없다.
- 모델에서는 운영역량 지수의 일부로 반영한다.

## 1.4 `label_avg_growth_alpha.svg`

파일:

- `analysis_outputs/eda/charts/label_avg_growth_alpha.svg`

목적:

- 성장 라벨별 결과 설명용 Growth Alpha 차이를 확인한다.
- 브랜드·카테고리 평균 대비 초과 성장 개념이 성장 그룹을 구분하는지 확인한다.

핵심 수치:

- 성장 라벨 1 평균 `internal_growth_alpha`: 2.9508
- 성장 라벨 0 평균 `internal_growth_alpha`: -1.2651

해석:

- 성장 라벨 1 그룹은 브랜드·카테고리 보정 후에도 초과 성장 신호가 강하다.
- 이는 본 프로젝트의 차별점인 Growth Alpha 개념이 결과 설명에 유효함을 보여준다.

발표용 문장:

```text
성장 그룹은 브랜드와 카테고리 평균을 보정한 뒤에도 Growth Alpha가 양수로 나타났습니다. 본 모델은 단순히 큰 매장을 찾는 것이 아니라, 같은 조건 대비 초과 성장하는 매장을 찾는 방향으로 설계되었습니다.
```

주의점:

- 이 그래프의 `internal_growth_alpha`는 미래 성장률에서 파생된 결과 설명용 변수다.
- 예측 모델 입력에는 과거 기반 `historical_internal_growth_alpha`를 사용해야 한다.

## 1.5 `brand_category_growth_rate.svg`

파일:

- `analysis_outputs/eda/charts/brand_category_growth_rate.svg`

목적:

- 브랜드·카테고리 조합별 성장 라벨 비율을 비교한다.
- 제공 데이터의 브랜드/카테고리 편향을 점검한다.

핵심 수치:

- 본그룹 / 백반·죽·국수 성장 비율: 0.340
- 굽네치킨 / 치킨 성장 비율: 0.247
- 굽네치킨 / 피자 성장 비율: 0.182

해석:

- 성장 라벨 비율이 브랜드·카테고리별로 다르다.
- 본그룹/백반·죽·국수 쪽 성장 비율이 상대적으로 높고, 굽네치킨/피자는 낮다.
- 이는 모델에서 브랜드와 카테고리 효과를 반드시 통제해야 함을 의미한다.

발표용 문장:

```text
브랜드·카테고리별 성장 비율이 다르게 나타났기 때문에, 본 프로젝트는 브랜드 효과를 그대로 성장성으로 해석하지 않고 통제 변수와 Growth Alpha 보정 항목으로 처리했습니다.
```

주의점:

- 현재 데이터는 본그룹과 굽네치킨 중심이므로 전체 F&B 일반화에는 한계가 있다.
- 이 한계를 파일럿 검증 데이터셋으로 명시해야 한다.

## 1.6 `monthly_avg_orders_by_label.svg`

파일:

- `analysis_outputs/eda/charts/monthly_avg_orders_by_label.svg`

목적:

- 성장 라벨별 월별 평균 주문수 추이를 비교한다.
- 특정 월의 일시적 차이가 아니라 기간 전반의 차이인지 확인한다.

해석:

- 성장 라벨 1 그룹은 여러 월에 걸쳐 평균 주문수가 높은 경향을 보인다.
- 성장 라벨이 단일 시점의 우연한 차이에만 의존하지 않는다는 근거로 사용할 수 있다.

발표용 문장:

```text
월별 추이를 보아도 성장 그룹은 전 기간에 걸쳐 주문 수준이 높게 유지되었습니다. 따라서 성장 라벨은 일시적 노이즈가 아니라 지속적인 성과 차이를 반영합니다.
```

주의점:

- 주문 수준이 높은 매장과 성장률이 높은 매장은 다를 수 있다.
- 최종 스코어에서는 규모와 성장 신호를 함께 사용한다.

## 2. 스코어링 시각화

위치:

- `analysis_outputs/scoring/charts/`

## 2.1 `score_distribution.svg`

파일:

- `analysis_outputs/scoring/charts/score_distribution.svg`

목적:

- 전체 1,246개 매장의 GroMong Score 분포를 확인한다.
- 점수가 지나치게 높게 몰리거나 낮게 몰리지 않는지 확인한다.

핵심 수치:

- 평균 점수: 53.28
- 중앙값 점수: 53.90
- 최고 점수: 98.18

해석:

- 평균과 중앙값이 50점대 초반에 위치한다.
- 스코어가 모든 매장을 높게 평가하지 않고, 일부 상위 매장을 선별하는 구조로 작동한다.

발표용 문장:

```text
GroMong Score의 평균은 약 53점으로, 모든 매장을 높게 평가하지 않고 성장 유망성이 높은 일부 매장을 선별하는 방식으로 설계되었습니다.
```

주의점:

- 점수 분포는 현재 데이터와 가중치 설정에 따라 달라질 수 있다.
- 향후 실제 투자 성과 데이터가 있으면 calibration이 필요하다.

## 2.2 `grade_counts.svg`

파일:

- `analysis_outputs/scoring/charts/grade_counts.svg`

목적:

- A/B/C/D 등급별 매장 수를 보여준다.
- 실제 추천 대상 규모를 확인한다.

핵심 수치:

- A등급: 84개
- B등급: 234개
- C등급: 365개
- D등급: 563개

해석:

- A등급은 전체 1,246개 중 84개로 제한적이다.
- 투자 또는 운영 지원 우선순위를 좁히는 데 사용할 수 있다.

발표용 문장:

```text
최종 스코어는 84개 매장만 A등급으로 분류했습니다. 이는 1,246개 매장 전체를 동일하게 보는 것이 아니라, 투자와 운영 지원 우선순위를 좁히기 위한 스코어링 구조입니다.
```

주의점:

- A/B/C/D 기준은 현재 80/65/50 기준으로 설정했다.
- 실제 투자 정책에 따라 등급 기준은 조정 가능하다.

## 2.3 `brand_avg_score.svg`

파일:

- `analysis_outputs/scoring/charts/brand_avg_score.svg`

목적:

- 브랜드별 평균 GroMong Score를 비교한다.
- 최종 점수가 특정 브랜드에 과도하게 치우치는지 점검한다.

핵심 수치:

- 본그룹 평균 점수: 55.29
- 굽네치킨 평균 점수: 49.61

해석:

- 본그룹 평균 점수가 굽네치킨보다 높다.
- 상위 점수 매장도 본그룹/백반·죽·국수에 많이 분포한다.
- 이 결과는 브랜드 편향 점검이 필요하다는 근거다.

발표용 문장:

```text
브랜드별 평균 점수를 확인한 결과 본그룹이 상대적으로 높게 나타났습니다. 따라서 최종 결과 해석 시 브랜드 편향 가능성을 함께 점검했고, 향후 브랜드별 보정 점수 체계가 필요합니다.
```

주의점:

- 이 차이가 브랜드 자체의 우수성을 의미한다고 해석하면 안 된다.
- 제공 데이터의 브랜드 구성과 주문/리뷰 관측 구조가 영향을 줄 수 있다.

## 2.4 `category_avg_score.svg`

파일:

- `analysis_outputs/scoring/charts/category_avg_score.svg`

목적:

- 카테고리별 평균 GroMong Score를 비교한다.
- 업종 효과가 최종 점수에 얼마나 반영되는지 확인한다.

핵심 수치:

- 백반·죽·국수 평균 점수: 55.29
- 치킨 평균 점수: 51.13
- 피자 평균 점수: 46.07

해석:

- 백반·죽·국수 카테고리의 평균 점수가 가장 높고, 피자가 가장 낮다.
- 카테고리별 성장 패턴 차이가 존재한다.
- 최종 발표에서는 카테고리별 ranking 또는 보정 스코어 확장 가능성을 언급하는 것이 좋다.

발표용 문장:

```text
카테고리별 평균 점수를 보면 백반·죽·국수 카테고리가 높고 피자 카테고리가 낮게 나타났습니다. 이는 업종별 성장 패턴이 다르기 때문에 카테고리 효과를 통제해야 한다는 점을 보여줍니다.
```

주의점:

- 카테고리별 표본 수가 다르므로 단순 평균 비교만으로 업종 우열을 말하면 안 된다.

## 2.5 `growth_alpha_vs_score.svg`

파일:

- `analysis_outputs/scoring/charts/growth_alpha_vs_score.svg`

목적:

- 과거 기반 Growth Alpha와 최종 GroMong Score의 관계를 확인한다.
- 최종 점수가 Growth Alpha를 어느 정도 반영하는지 시각적으로 점검한다.

해석:

- Growth Alpha가 높을수록 최종 점수가 높아지는 경향을 확인할 수 있다.
- 다만 최종 점수는 Growth Alpha만으로 결정되지 않고, 모델 성장 확률, 리뷰 성장, 운영역량, 안정성을 함께 반영한다.

발표용 문장:

```text
GroMong Score는 Growth Alpha와 일정한 관계를 보이지만, Growth Alpha 하나만으로 결정되지는 않습니다. 성장 확률, 리뷰 성장, 운영역량, 안정성을 함께 반영해 최종 점수를 산출했습니다.
```

주의점:

- 과거 기반 Growth Alpha는 예측 입력용으로 사용한 변수다.
- 결과 설명용 `internal_growth_alpha`와 구분해야 한다.

## 2.6 `seoul_market_ticket_ratio_vs_score.svg`

파일:

- `analysis_outputs/scoring/charts/seoul_market_ticket_ratio_vs_score.svg`

목적:

- 서울 매장에 대해 상권 평균 객단가 대비 매장 객단가 비율과 최종 점수의 관계를 확인한다.
- 외부 상권 데이터가 점수 해석에 어떻게 연결되는지 보여준다.

해석:

- 서울 매장은 외부 상권 평균 객단가 대비 위치를 10% 보정 항목으로 반영했다.
- 이 그래프는 매장 성과를 절대값이 아니라 상권 대비 위치로 해석한다는 차별점을 보여준다.

발표용 문장:

```text
서울 매장에 대해서는 자치구·유사업종 상권 평균 객단가와 비교해 매장의 가격 포지션을 반영했습니다. 이는 단순 매장 성과가 아니라 상권 대비 경쟁력을 평가하려는 본 프로젝트의 차별점입니다.
```

주의점:

- 현재 외부 상권 데이터는 서울 211개 매장에 한정된다.
- 자치구 단위 결합이므로 행정동/좌표 기반 결합보다 정밀도는 낮다.

## 2.7 `top20_store_scores.svg`

파일:

- `analysis_outputs/scoring/charts/top20_store_scores.svg`

목적:

- 최종 GroMong Score 상위 20개 매장을 보여준다.
- 데모와 발표에서 추천 결과 예시로 사용할 수 있다.

해석:

- 상위 매장은 대부분 A등급이며, 성장 확률, Growth Alpha, 리뷰 성장, 운영 대응력이 복합적으로 높게 평가된 매장이다.
- 현재 상위권이 본그룹/백반·죽·국수에 많이 분포하는 경향이 있다.

발표용 문장:

```text
최종 스코어 상위 20개 매장은 성장 확률과 Growth Alpha, 리뷰 성장, 운영역량이 종합적으로 높게 평가된 매장입니다. 다만 상위권이 특정 브랜드와 카테고리에 집중되는 경향이 있어, 향후 브랜드별 보정 스코어가 필요합니다.
```

주의점:

- 상위 매장 목록은 투자 확정 목록이 아니라 우선 검토 후보군이다.
- 실제 투자 판단에는 추가 현장 정보와 재무 정보가 필요하다.

## 3. 앞으로의 시각화 산출 원칙

앞으로 새로운 그래프나 시각 자료를 만들 때는 반드시 다음을 함께 작성한다.

1. 그래프 파일
2. 그래프 목적
3. 핵심 수치
4. 해석
5. 발표용 문장
6. 주의점 또는 한계

따라서 이후 데모, 최종 발표자료, 모델 고도화 단계에서도 시각화만 생성하지 않고, 각 시각화가 프로젝트 주제와 차별점에 어떻게 연결되는지 분석 문서로 남긴다.

관련 관리 문서:

- `project_plan.md`
- `project_proposal.md`
- `remaining_tasks.md`
- `final_outputs_index.md`

새로운 시각화가 추가되면 이 문서와 위 관리 문서를 함께 업데이트한다.

다음 추가 예정 시각화:

- 데모 점수 게이지
- 점수 구성요소 bar chart
- 등급 배지
- 서울 매장 상권 객단가 비교 표시

데모 시각화 설명 문서:

- `analysis_outputs/demo/demo_visualization_guide.md`

데모 화면에는 정적 SVG 파일이 아니라 웹 UI 시각요소가 포함된다. 각 요소의 목적과 해석은 위 문서에 정리했다.

## 4. 중간발표 보강 로드맵 시각화

파일:

- `analysis_outputs/quality_boost/charts/quality_boost_roadmap.svg`

설명 문서:

- `analysis_outputs/quality_boost/quality_boost_visualization_guide.md`

목적:

- 중간발표 1등을 목표로 보강해야 할 분석 과제를 한 장으로 보여준다.
- 차별점, 특이한 외부데이터, 유의미한 분석이라는 교수님 기준에 맞춰 남은 작업을 정리한다.

색상:

- 보라: 리뷰 NLP
- 파랑: 가중치 민감도
- 초록: 처치 전후 효과
- 주황: 보정 점수
- 빨강: 외부데이터 확장

다음 추가 예정 시각화:

- 리뷰 감성 점수 비교
- 긍정 키워드 Top 20
- 부정 키워드 Top 20
- 별점-감성 불일치 분포
- 카테고리별 리뷰 감성 비교
## 2026-05-08 추가: 리뷰 원문 NLP 시각화

리뷰 원문 기반 NLP 분석 시각화를 추가했다.

설명 문서:

- `analysis_outputs/nlp/review_nlp_visualization_guide.md`

생성된 시각화:

- `analysis_outputs/nlp/charts/sentiment_by_growth_label.svg`
- `analysis_outputs/nlp/charts/review_topic_rates_by_growth_label.svg`
- `analysis_outputs/nlp/charts/positive_keywords_top20.svg`
- `analysis_outputs/nlp/charts/negative_keywords_top20.svg`
- `analysis_outputs/nlp/charts/category_sentiment_by_growth_label.svg`
- `analysis_outputs/nlp/charts/rating_sentiment_mismatch_counts.svg`

핵심 해석:

```text
성장 상위 매장은 성장 외 매장보다 리뷰 원문의 평균 감성이 높고, 긍정 리뷰 비율이 높으며, 부정 리뷰 비율은 낮다. 특히 재주문 언급률이 더 높게 나타나 고객 언어 신호가 성장 유망 매장 판단의 보조 근거가 될 수 있다.
```

발표용 연결 문장:

```text
본 프로젝트는 단순히 평점 평균만 보는 것이 아니라 리뷰 원문에 담긴 고객의 실제 언어까지 분석했습니다. 이를 통해 주문 데이터, Growth Alpha, 외부 상권 데이터, 고객 반응 데이터를 함께 보는 성장 유망 매장 스코어링 구조를 만들었습니다.
```

주의점:

- 현재 분석은 키워드 사전 기반 파일럿 NLP 분석이다.
- 인과관계가 아니라 성장 상위 매장과 리뷰 언어 신호 사이의 관계를 확인한 것이다.
## 2026-05-08 추가: 스코어 가중치 민감도 시각화

GroMong Score의 가중치 안정성을 확인하기 위한 시각화를 추가했다.

설명 문서:

- `analysis_outputs/sensitivity/score_sensitivity_visualization_guide.md`

생성된 시각화:

- `analysis_outputs/sensitivity/charts/top100_overlap_by_scenario.svg`
- `analysis_outputs/sensitivity/charts/rank_correlation_by_scenario.svg`
- `analysis_outputs/sensitivity/charts/mean_score_by_scenario.svg`
- `analysis_outputs/sensitivity/charts/grade_counts_by_scenario.svg`
- `analysis_outputs/sensitivity/charts/top100_stability_top20.svg`

핵심 해석:

```text
가중치를 여러 방식으로 바꿔도 현재 Top 100 매장의 78~95%가 유지됐고, 전체 순위 상관도 0.959 이상으로 나타났다. 이는 현재 스코어링 결과가 특정 가중치 하나에만 과도하게 의존하지 않는다는 근거로 사용할 수 있다.
```

발표용 연결 문장:

```text
저희는 점수를 계산하는 데서 끝내지 않고, 가중치가 바뀌어도 추천 결과가 유지되는지 확인했습니다. 이 과정을 통해 GroMong Score가 단순 임의 점수표가 아니라 후보군 선별에 사용할 수 있는 안정적인 기준인지 검증했습니다.
```

주의점:

- 민감도 분석은 점수 안정성을 보여주는 것이며, 실제 투자 성공을 보장하는 검증은 아니다.
- 최상위권이 특정 브랜드/카테고리에 몰리는 현상이 있어, 다음 단계에서 브랜드/카테고리 내부 보정 순위를 추가해야 한다.
## 2026-05-08 추가: 브랜드/카테고리 보정 점수 시각화

브랜드/카테고리 편중을 완화하기 위한 보정 점수 시각화를 추가했다.

설명 문서:

- `analysis_outputs/calibrated_score/calibrated_score_visualization_guide.md`

생성된 시각화:

- `analysis_outputs/calibrated_score/charts/overall_vs_calibrated_score.svg`
- `analysis_outputs/calibrated_score/charts/category_top100_counts_before_after.svg`
- `analysis_outputs/calibrated_score/charts/category_avg_score_before_after.svg`
- `analysis_outputs/calibrated_score/charts/brand_A_counts_before_after.svg`
- `analysis_outputs/calibrated_score/charts/top100_overlap_after_calibration.svg`
- `analysis_outputs/calibrated_score/charts/category_top10_calibrated_scores.svg`

핵심 해석:

```text
보정 후에도 기존 Top100 중 92개가 유지되어 기존 스코어의 안정성은 유지됐다. 동시에 치킨과 피자 카테고리 후보가 더 많이 드러나, 특정 브랜드/카테고리 편중을 일부 완화했다.
```

발표용 연결 문장:

```text
제공 데이터가 특정 브랜드에 치우쳐 있다는 한계를 인정하고, 전체 점수와 별도로 브랜드 내부, 카테고리 내부 상대 순위를 반영했습니다. 그래서 전체 Top 후보뿐 아니라 같은 업종 안에서 상대적으로 성장 가능성이 높은 매장도 함께 제시할 수 있습니다.
```

주의점:

- 보정 점수는 기존 GroMong Score를 대체하는 최종 정답이 아니다.
- 전체 순위와 함께 보는 공정성 보완 지표다.
- 피자 카테고리는 표본이 작으므로 해석을 조심해야 한다.
## 2026-05-08 진행 예정: 불균형 진단 시각화

다음 시각화를 추가할 예정이다.

- 원본 데이터 브랜드 분포
- 원본 데이터 카테고리 분포
- 기존 Top100 카테고리 분포
- 보정 Top100 카테고리 분포
- 보정 전후 카테고리 편중 완화 비교
- 균형형 추천 리스트 구성 시각화

시각화의 목적:

```text
데이터가 불균형하다는 약점을 숨기지 않고, 분석 결과 안에서 직접 진단하고 보정했다는 점을 보여준다.
```
## 2026-05-08 추가: 불균형 진단과 균형형 추천 시각화

불균형 진단과 균형형 추천 시각화를 추가했다.

설명 문서:

- `analysis_outputs/imbalance/imbalance_visualization_guide.md`

생성된 시각화:

- `analysis_outputs/imbalance/charts/original_brand_distribution.svg`
- `analysis_outputs/imbalance/charts/original_category_distribution.svg`
- `analysis_outputs/imbalance/charts/current_top100_category_distribution.svg`
- `analysis_outputs/imbalance/charts/calibrated_top100_category_distribution.svg`
- `analysis_outputs/imbalance/charts/balanced_category_distribution.svg`
- `analysis_outputs/imbalance/charts/category_distribution_comparison.svg`
- `analysis_outputs/imbalance/charts/imbalance_key_metrics.svg`

핵심 해석:

```text
원본 데이터부터 백반·죽·국수와 본그룹 비중이 높고, 기존 Top100에서는 이 편중이 더 심해졌다. 보정 Top100은 기존 후보의 안정성을 유지하면서 일부 치킨/피자 후보를 더 드러냈고, 균형형 추천은 발표용 보조 후보군으로 카테고리 다양성을 확보한다.
```

발표용 연결 문장:

```text
저희는 데이터 불균형을 약점으로 숨기지 않고, 분석 대상 자체의 특성으로 먼저 진단했습니다. 그 다음 전체 Top 후보, 보정 Top 후보, 균형형 후보를 분리해 제시했습니다.
```

## 8. 피드백 반영 EDA 시각화

위치:

- `analysis_outputs/feedback_eda/charts/`

### 8.1 `label_relative_gap.svg`

목적:

- 성장 그룹과 비성장 그룹의 핵심 지표 차이를 상대 비율로 보여준다.
- 성장 라벨이 주문, 리뷰, 운영, Growth Alpha 차이를 실제로 반영하는지 확인한다.

핵심 수치:

- 성장 그룹 평균 주문수는 비성장 그룹보다 148.13% 높다.
- 성장 그룹 평균 리뷰수는 비성장 그룹보다 69.12% 높다.
- 결과 설명용 Growth Alpha는 성장 그룹 2.9508, 비성장 그룹 -1.2651이다.

발표용 문장:

```text
성장 라벨은 임의의 분류가 아니라 주문, 리뷰, Growth Alpha에서 뚜렷한 차이를 보이는 집단을 구분합니다.
```

### 8.2 `nlp_mean_comparison.svg`

목적:

- 리뷰 원문에서 추출한 텍스트 감성, 긍정/부정 리뷰율, 재주문 언급률을 성장 라벨별로 비교한다.
- “텍스트 자체에서 더 깊은 정보를 끌어내라”는 피드백의 반영 근거를 보여준다.

핵심 수치:

- 평균 텍스트 감성: 성장 그룹 0.6831, 비성장 그룹 0.6709
- 부정 리뷰율: 성장 그룹 0.0310, 비성장 그룹 0.0400

발표용 문장:

```text
기존에는 리뷰 수와 별점 중심이었다면, 보완 후에는 리뷰 문장 안의 긍정/부정 및 주제 신호를 모델 입력으로 통합했습니다.
```

### 8.3 `external_market_comparison.svg`

목적:

- 서울 외부 상권 변수의 성장 라벨별 차이를 확인한다.
- 외부 환경 변수가 약하다는 피드백에 대해 현재 결합 가능한 외부 데이터의 역할과 한계를 명확히 보여준다.

해석:

- 외부 상권 변수는 모든 지표에서 성장 그룹이 일방적으로 높은 구조는 아니다.
- 따라서 외부 데이터는 단독 판단 지표가 아니라 내부 신호를 보완하는 상권 맥락 변수로 사용하는 것이 타당하다.

발표용 문장:

```text
외부 상권 변수는 성장 여부를 단독으로 설명하기보다, 비슷한 내부 성과의 매장이 왜 다르게 성장하는지 해석하는 보조 맥락으로 사용했습니다.
```

### 8.4 `model_auc_comparison.svg`

목적:

- Baseline, Growth Alpha, Growth Alpha + NLP 분류 모델의 AUC를 비교한다.
- 피드백 이후 모델링 방향이 분류 중심으로 재정렬되었음을 보여준다.

핵심 수치:

- Baseline AUC: 0.6060
- Growth Alpha AUC: 0.6078
- Growth Alpha + NLP AUC: 0.6148

발표용 문장:

```text
리뷰 NLP 피처를 결합한 분류 모델이 가장 높은 AUC를 보였고, 최종 스코어는 이 분류 확률을 우선 반영하도록 수정했습니다.
```

### 8.5 `roi_by_grade_base.svg`

목적:

- 분류 확률이 실제 투자효과 추정으로 이어지는지 등급별 기대 ROI를 확인한다.
- 예측과 투자효과가 분리되어 있다는 피드백을 보완한다.

핵심 수치:

- 기본 ROI 시나리오에서 A등급 평균 기대 ROI: 150,409원
- A등급 ROI 양수 비율: 100.0%

발표용 문장:

```text
GroMong Score는 예측 확률에서 끝나지 않고, 비용과 기대 추가 주문을 결합한 ROI 시뮬레이션으로 투자 우선순위까지 연결했습니다.
```

## 2026-05-18 피드백 반영 EDA 리디자인 업데이트

`analysis_outputs/feedback_eda/charts/`의 그래프를 발표용 라이트 카드 스타일로 전면 재생성했다. 단순 색상 변경이 아니라, 피드백별 반영 근거가 보이도록 분석 깊이도 함께 보강했다.

추가/갱신된 시각화:

| 파일 | 목적 | 발표 포인트 |
| --- | --- | --- |
| `label_relative_gap.svg` | 성장/비성장 그룹의 핵심 운영 지표 상대 차이 | 성장 그룹 주문수 +148.13%, 리뷰수 +69.12% |
| `label_mean_comparison.svg` | 주문, 리뷰, 답글률, 응답 지연의 원 평균 비교 | 성장 라벨이 실제 운영 차이를 반영함 |
| `effect_size_heatmap.svg` | 지표별 Cohen's d 효과크기 확인 | 평균 차이가 아니라 분포 분리 정도까지 점검 |
| `nlp_mean_comparison.svg` | 리뷰 텍스트 감성/긍정/부정/재주문 신호 비교 | 텍스트 자체를 모델 입력으로 확장했다는 근거 |
| `nlp_relative_gap.svg` | NLP 지표의 상대 차이 | 성장 그룹 부정 리뷰율 22.67% 낮고, 재주문 언급률 11.83% 높음 |
| `external_market_comparison.svg` | 외부 상권 지표의 성장 라벨별 비교 | 외부 변수는 단독 증거가 아니라 상권 맥락 보정 변수로 해석 |
| `model_auc_comparison.svg` | 분류 모델 AUC 비교 | Growth Alpha + NLP AUC 0.6148로 최고 |
| `model_decile_lift.svg` | 예측 확률 decile별 실제 성장률 | 최상위 decile 실제 성장률 40.40%, 최하위 10.80% |
| `roi_by_grade_base.svg` | 등급별 기대 월간 ROI | A등급 평균 기대 ROI 150,409원, D등급 -22,198원 |
| `score_decile_profile.svg` | GroMong Score decile별 확률, Alpha, 외부데이터 비중 | 점수 상위권이 어떤 신호 조합으로 구성되는지 설명 |

발표용 연결 문장:

```text
EDA는 단순 평균 비교에서 끝내지 않고, 효과크기, 예측 decile lift, ROI 등급 검증까지 확인했습니다.
그 결과 리뷰 NLP를 결합한 분류 모델이 가장 높은 AUC를 보였고, 상위 예측 decile이 실제 성장 라벨을 더 많이 포함했으며, 최종 등급은 ROI 시뮬레이션과도 연결되었습니다.
```


