# Modeling Summary

## 목적

이번 모델링의 목적은 내부 변수만 사용한 Baseline 모델과 과거 기반 Growth Alpha 변수를 추가한 모델을 비교하는 것이다.

프로젝트 차별점은 단순 인기 매장 예측이 아니라 브랜드·카테고리 효과를 보정한 초과 성장 잠재력을 활용하는 데 있다.

## 데이터 분할

- 학습 기간: 2025-01 ~ 2025-07
- 검증 기간: 2025-08 ~ 2025-09
- 목표 변수: `growth_label_top30`
- 주의: 미래 성장률에서 파생된 `internal_growth_alpha`는 입력 변수에서 제외했다.
- Growth Alpha 모델에는 과거 데이터 기반 `historical_internal_growth_alpha`를 사용했다.

## 주요 결과

- Baseline AUC: 0.6060
- Growth Alpha AUC: 0.6078
- Baseline F1: 0.5173
- Growth Alpha F1: 0.5169
- 더 높은 AUC 모델: growth_alpha

## 해석

과거 기반 Growth Alpha 변수를 추가했을 때 AUC가 개선되었다. 이는 브랜드·카테고리 보정 성장 신호가 성장 유망 매장 예측에 일부 기여한다는 근거로 사용할 수 있다.

## 다음 작업

서울 매장 211개 subset에서 외부 상권 변수 추가 전후 성능을 비교한다. 이 단계가 외부 데이터의 실질적 기여도를 검증하는 핵심이다.