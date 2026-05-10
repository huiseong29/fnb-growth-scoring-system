# Seoul External Modeling Summary

## 목적

이번 검증의 목적은 서울 매장 211개 subset에서 외부 상권 데이터가 성장 유망 매장 예측에 실제로 기여하는지 확인하는 것이다.

본 프로젝트의 차별점은 상권·브랜드·카테고리 효과를 고려한 Growth Alpha 기반 스코어링이므로, 외부 상권 변수의 실질적 기여도 검증이 중요하다.

## 데이터 범위

- 서울 외부 상권 결합 매장 수: 211
- 학습 행 수: 1477
- 검증 행 수: 422
- 학습 기간: 2025-01 ~ 2025-07
- 검증 기간: 2025-08 ~ 2025-09

## 비교 모델

- Seoul Internal: 내부 변수 + 과거 기반 Growth Alpha 변수
- Seoul External: Seoul Internal + 외부 상권 변수

## 주요 결과

- Seoul Internal AUC: 0.5826
- Seoul External AUC: 0.5995
- Seoul Internal F1: 0.4807
- Seoul External F1: 0.4773

## Top N 결과

- seoul_internal Top 50 Precision: 0.360
- seoul_internal Top 100 Precision: 0.340
- seoul_internal Top 200 Precision: 0.325
- seoul_external Top 50 Precision: 0.360
- seoul_external Top 100 Precision: 0.370
- seoul_external Top 200 Precision: 0.330

## 해석

외부 상권 변수를 추가했을 때 AUC가 개선되었다. 이는 상권 정보를 결합하는 것이 성장 유망 매장 선별에 실질적으로 기여할 수 있음을 보여준다.

## 다음 작업

모델 결과를 바탕으로 최종 GroMong Score 산출식을 만들고, 매장별 점수와 주요 근거를 생성한다.