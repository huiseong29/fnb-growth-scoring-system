# ROI Simulation Summary

## 목적

분류 모델의 성장 확률을 투자 우선순위 판단에 연결하기 위해 매장별 기대 월간 ROI를 시뮬레이션했다.

## 계산식

```text
expected_incremental_orders = final_growth_probability * assumed_monthly_lift_orders
expected_monthly_margin = expected_incremental_orders * gross_margin_per_order
expected_monthly_roi = expected_monthly_margin - monthly_program_cost
```

## 시나리오

- conservative: 월 추가 주문 50건, 주문당 공헌이익 3,000원, 월 프로그램 비용 120,000원
- base: 월 추가 주문 100건, 주문당 공헌이익 3,000원, 월 프로그램 비용 120,000원
- causal_att_reference: 월 추가 주문 114건, 주문당 공헌이익 3,000원, 월 프로그램 비용 120,000원

## 주요 결과

- base: ROI 양수 매장 844/1246, 평균 기대 ROI 59,377원, 최고 기대 ROI 179,514원
- causal_att_reference: ROI 양수 매장 885/1246, 평균 기대 ROI 84,490원, 최고 기대 ROI 221,446원
- conservative: ROI 양수 매장 465/1246, 평균 기대 ROI -30,311원, 최고 기대 ROI 29,757원

## 해석

이 결과는 실제 투자 확정 모델이 아니라 발표용 의사결정 프레임이다. 인과추론 ATT는 전체 평균 효과의 참고값으로 두고, 최종 선별은 분류 모델의 매장별 성장 확률과 비용 가정을 결합해 수행한다.

따라서 피드백에서 지적된 예측과 투자효과의 분리를 줄이고, GroMong Score를 우선 검토 후보군 선정과 ROI 민감도 검토에 연결할 수 있다.