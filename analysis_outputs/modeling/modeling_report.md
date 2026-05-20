# Modeling Summary

## 목적

이번 모델링의 목적은 성장/비성장 **분류**에 집중해 내부 변수만 사용한 Baseline, 과거 기반 Growth Alpha 모델, 리뷰 원문 NLP 피처 결합 모델을 비교하는 것이다.

프로젝트 차별점은 단순 인기 매장 예측이 아니라 브랜드·카테고리 효과를 보정한 초과 성장 잠재력과 고객 리뷰 텍스트 신호를 함께 활용하는 데 있다.

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
- 더 높은 AUC 모델: growth_alpha_nlp

## 리뷰 텍스트 피처 통합

- Growth Alpha + NLP AUC: 0.6148
- Growth Alpha + NLP F1: 0.5250
- Growth Alpha + NLP Top100 Precision: 0.4000
- 사용 피처: 평균 텍스트 감성, 긍정/부정 리뷰율, 맛·양·배달·가격·서비스·재주문 주제 언급률

## 해석

과거 기반 Growth Alpha 변수를 추가했을 때 AUC가 개선되었다. 이는 브랜드·카테고리 보정 성장 신호가 성장 유망 매장 예측에 일부 기여한다는 근거로 사용할 수 있다.
리뷰 텍스트 피처를 결합한 모델이 Growth Alpha 단독 모델보다 AUC가 높거나 같았다. 댓글 주체 분리와 함께 리뷰 원문의 고객 반응을 분류 모델에 직접 넣는 보완 방향이 타당하다.

## 다음 작업

서울 매장 211개 subset에서 외부 상권 변수 추가 전후 성능을 비교하고, 최종 점수에서는 분류 확률과 기대 투자효과를 ROI 시뮬레이션으로 연결한다.