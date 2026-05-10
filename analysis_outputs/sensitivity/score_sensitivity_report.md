# Score Sensitivity Report

## 목적

GroMong Score의 5개 지수 가중치가 달라져도 상위 추천 매장이 얼마나 안정적으로 유지되는지 확인했다.

## 시나리오

- 현재 공식 가중치: probability_score 0.35, growth_alpha_score 0.25, review_growth_score 0.15, operation_score 0.15, stability_score 0.10, 서울 상권 보정 0.10
- 성장확률 강화: probability_score 0.45, growth_alpha_score 0.20, review_growth_score 0.12, operation_score 0.13, stability_score 0.10, 서울 상권 보정 0.10
- Growth Alpha 강화: probability_score 0.25, growth_alpha_score 0.40, review_growth_score 0.15, operation_score 0.10, stability_score 0.10, 서울 상권 보정 0.10
- 리뷰 성장 강화: probability_score 0.30, growth_alpha_score 0.20, review_growth_score 0.30, operation_score 0.10, stability_score 0.10, 서울 상권 보정 0.10
- 운영 역량 강화: probability_score 0.28, growth_alpha_score 0.22, review_growth_score 0.12, operation_score 0.28, stability_score 0.10, 서울 상권 보정 0.10
- 안정성 강화: probability_score 0.30, growth_alpha_score 0.20, review_growth_score 0.12, operation_score 0.13, stability_score 0.25, 서울 상권 보정 0.10
- 서울 상권 적합도 강화: probability_score 0.35, growth_alpha_score 0.25, review_growth_score 0.15, operation_score 0.15, stability_score 0.10, 서울 상권 보정 0.20

## 핵심 결과

- 현재 공식 가중치: Top100 겹침률 100%, 순위 상관 1.000, A등급 84개
- 성장확률 강화: Top100 겹침률 91%, 순위 상관 0.990, A등급 116개
- Growth Alpha 강화: Top100 겹침률 89%, 순위 상관 0.964, A등급 75개
- 리뷰 성장 강화: Top100 겹침률 78%, 순위 상관 0.976, A등급 56개
- 운영 역량 강화: Top100 겹침률 94%, 순위 상관 0.983, A등급 115개
- 안정성 강화: Top100 겹침률 82%, 순위 상관 0.959, A등급 83개
- 서울 상권 적합도 강화: Top100 겹침률 95%, 순위 상관 0.995, A등급 81개

## 해석

가중치를 바꿔도 현재 Top 100과 상당수 매장이 겹치면, 최종 추천 결과가 특정 가중치 하나에만 의존하지 않는다고 설명할 수 있다.
반대로 특정 시나리오에서 겹침률이 낮아지는 경우, 해당 지수의 영향력이 크다는 의미이므로 발표에서 보완 근거로 활용한다.