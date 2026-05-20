# EDA Summary

## 프로젝트 관점

이번 EDA의 목적은 AI 기반 F&B 성장 유망 매장 스코어링 시스템에서 핵심 차별점인 Growth Alpha가 실제로 의미 있는 신호인지 확인하는 것이다.

Growth Alpha는 단순 주문수나 리뷰수가 아니라 브랜드·카테고리 효과를 보정한 초과 성장 잠재력을 의미한다.

## 데이터 범위

- 전체 패널 행 수: 17,444
- 전체 매장 수: 1,246
- 분석 월 범위: 2024-11 ~ 2025-12
- 라벨 유효 행 수: 11,214
- 성장 라벨 1 비율: 30.01%
- 서울 외부 상권 결합 매장 수: 211

## 주요 관찰

- 성장 라벨 1 그룹의 평균 Growth Alpha는 2.9508, 라벨 0 그룹은 -1.2651이다.
- 예측 모델 입력으로 사용할 과거 기반 Growth Alpha는 성장 라벨 1 그룹 평균 -0.1884, 라벨 0 그룹 평균 0.1014이다.
- 성장 라벨 1 그룹의 평균 월 주문수는 169.17, 라벨 0 그룹은 68.18이다.
- 성장 라벨 1 그룹의 평균 월 리뷰수는 14.9, 라벨 0 그룹은 8.81이다.

## 해석

이 결과는 성장 유망 매장을 단순 규모가 큰 매장으로만 정의하지 않고, 브랜드·카테고리 평균 대비 초과 성장하는 매장으로 구분할 수 있음을 보여준다.

`internal_growth_alpha`는 미래 성장률에서 파생된 결과 설명용 변수다. 예측 모델 입력에는 과거 데이터만으로 계산한 `historical_internal_growth_alpha`를 사용해야 한다.

다음 단계에서는 내부 변수만 사용한 Baseline 모델과 Growth Alpha 변수를 포함한 모델을 비교하여, 이 차별점이 실제 예측 성능 개선으로 이어지는지 검증한다.
## 피드백 반영 보강 EDA

추가 목적:

- 기존 EDA가 성장 라벨과 Growth Alpha의 기본 타당성을 확인했다면, 보강 EDA는 받은 코멘트가 실제 분석에 반영되었는지 검증한다.
- 인과추론 중심 설명을 낮추고, 성장 유망 매장 분류, 리뷰 텍스트 신호, 외부 상권 변수, ROI 연결을 중심으로 재정렬한다.

추가 산출물:

- `analysis_outputs/feedback_eda/feedback_eda_report.md`
- `analysis_outputs/feedback_eda/comment_reflection_matrix.csv`
- `analysis_outputs/feedback_eda/eda_label_gap_summary.csv`
- `analysis_outputs/feedback_eda/eda_nlp_gap_summary.csv`
- `analysis_outputs/feedback_eda/eda_external_gap_summary.csv`
- `analysis_outputs/feedback_eda/eda_model_lift_summary.csv`
- `analysis_outputs/feedback_eda/eda_roi_by_grade_summary.csv`
- `analysis_outputs/feedback_eda/charts/`

핵심 보강 결과:

- 성장 그룹 평균 주문수는 비성장 그룹보다 148.13% 높다.
- 성장 그룹 평균 리뷰수는 비성장 그룹보다 69.12% 높다.
- 성장 그룹의 결과 설명용 Growth Alpha는 2.9508, 비성장 그룹은 -1.2651이다.
- 리뷰 텍스트 감성은 성장 그룹 0.6831, 비성장 그룹 0.6709로 성장 그룹이 높다.
- Growth Alpha + NLP 모델 AUC는 0.6148로, Growth Alpha 단독 모델 AUC 0.6078보다 개선되었다.
- 기본 ROI 시나리오에서 A등급 매장의 평균 기대 ROI는 150,409원이며, ROI 양수 비율은 100.0%이다.

발표용 정리:

```text
피드백을 반영해 인과추론은 평균 효과 검증 근거로 두고, 최종 의사결정은 성장 유망 매장 분류 모델로 재정렬했다.
리뷰 원문 NLP 피처, 외부 상권 변수, ROI 시뮬레이션을 추가해 왜 이 매장을 우선 검토해야 하는지 설명 가능한 구조로 보완했다.
```
