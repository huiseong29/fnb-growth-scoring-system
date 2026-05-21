# ROI Simulation Summary

## 목적

분류 모델의 성장 확률을 투자 우선순위 판단에 연결하기 위해 매장별 기대 월간 ROI를 시뮬레이션했다.

## 가정 파일

- 사용 파일: `analysis_outputs/roi/roi_assumptions.csv`

## 계산식

```text
expected_incremental_orders = probability * assumed_monthly_lift_orders
expected_monthly_roi = expected_incremental_orders * gross_margin_per_order - monthly_program_cost
band_calibrated_probability = time split 검증 decile별 actual growth rate 매핑값
```

## 시나리오

- conservative: 월 추가 주문 50건, 주문당 공헌이익 3,000원, 월 프로그램 비용 120,000원
- base: 월 추가 주문 100건, 주문당 공헌이익 3,000원, 월 프로그램 비용 120,000원
- causal_att_reference: 월 추가 주문 114건, 주문당 공헌이익 3,000원, 월 프로그램 비용 120,000원

## 주요 결과

- base: 보정 ROI 양수 매장 125/1246, 평균 보정 기대 ROI -22,592원
- causal_att_reference: 보정 ROI 양수 매장 872/1246, 평균 보정 기대 ROI -8,955원
- conservative: 보정 ROI 양수 매장 0/1246, 평균 보정 기대 ROI -71,296원

## 해석

ATT는 예측 점수에 직접 넣지 않고 causal_att_reference 시나리오의 참고 주문 증가량으로만 사용했다. 최종 선별은 분류 확률, band 보정 확률, 비용 가정을 결합한 TopK ROI 표로 판단한다.