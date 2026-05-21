# Component Direction Audit

## 목적

현재 composite score의 최신월 성장 라벨 기준 성능이 낮게 나왔기 때문에, 가중치 최적화가 아니라 각 component의 방향성이 성장 라벨과 같은 방향인지 점검했다.

## Component별 방향성 요약

| component | ROC-AUC | PR-AUC | Spearman | Pearson | Top100 lift | 성장 평균 | 비성장 평균 | 판단 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| probability_score | 0.5066 | 0.2521 | 0.0101 | 0.0299 | 0.84 | 60.76 | 58.69 | 예측 방향성 약함 |
| growth_alpha_score | 0.2728 | 0.1809 | -0.3461 | -0.3281 | 0.50 | 21.87 | 42.82 | 현재 방향성 반대 가능성 높음 |
| review_growth_score | 0.4226 | 0.2257 | -0.1114 | -0.0974 | 0.92 | 34.66 | 39.83 | 현재 방향성 반대 가능성 높음 |
| operation_score | 0.4977 | 0.2788 | -0.0047 | -0.0244 | 1.19 | 63.58 | 65.20 | 현재 방향성 반대 가능성 높음 |
| stability_score | 0.4056 | 0.2089 | -0.1441 | -0.1097 | 0.00 | 75.15 | 81.40 | 현재 방향성 반대 가능성 높음 |
| gromong_score | 0.4056 | 0.2112 | -0.1435 | -0.1539 | 0.46 | 49.09 | 55.21 | 현재 방향성 반대 가능성 높음 |

## Score band별 실제 성장률

아래 표는 각 component를 높은 점수 순서로 5개 band로 나누었을 때 실제 성장률이다. band 1이 가장 높은 점수 구간이다.

| component | band | rows | score mean | actual growth rate |
| --- | ---: | ---: | ---: | ---: |
| probability_score | 1 | 250 | 94.24 | 0.2240 |
| probability_score | 2 | 249 | 83.58 | 0.2731 |
| probability_score | 3 | 249 | 67.74 | 0.3414 |
| probability_score | 4 | 249 | 35.94 | 0.2249 |
| probability_score | 5 | 249 | 14.52 | 0.2410 |
| growth_alpha_score | 1 | 250 | 81.27 | 0.0960 |
| growth_alpha_score | 2 | 249 | 45.81 | 0.1325 |
| growth_alpha_score | 3 | 249 | 36.99 | 0.1727 |
| growth_alpha_score | 4 | 249 | 21.55 | 0.3936 |
| growth_alpha_score | 5 | 249 | 0.98 | 0.5100 |
| review_growth_score | 1 | 250 | 70.16 | 0.1840 |
| review_growth_score | 2 | 249 | 50.00 | 0.2008 |
| review_growth_score | 3 | 249 | 39.41 | 0.2610 |
| review_growth_score | 4 | 249 | 24.01 | 0.3614 |
| review_growth_score | 5 | 249 | 8.68 | 0.2972 |
| operation_score | 1 | 250 | 98.35 | 0.2760 |
| operation_score | 2 | 249 | 93.35 | 0.2651 |
| operation_score | 3 | 249 | 60.18 | 0.2932 |
| operation_score | 4 | 249 | 50.00 | 0.1004 |
| operation_score | 5 | 249 | 21.88 | 0.3695 |
| stability_score | 1 | 250 | 99.89 | 0.0600 |
| stability_score | 2 | 249 | 96.45 | 0.3815 |
| stability_score | 3 | 249 | 90.41 | 0.2851 |
| stability_score | 4 | 249 | 76.00 | 0.2369 |
| stability_score | 5 | 249 | 36.02 | 0.3414 |
| gromong_score | 1 | 250 | 78.91 | 0.1160 |
| gromong_score | 2 | 249 | 63.78 | 0.2731 |
| gromong_score | 3 | 249 | 53.52 | 0.3614 |
| gromong_score | 4 | 249 | 41.18 | 0.2008 |
| gromong_score | 5 | 249 | 30.57 | 0.3534 |

## 결론

현재 composite score는 최신월 성장 예측 ranking 점수로 쓰기에는 방어력이 약하다. Growth Alpha, 리뷰 성장, 안정성 등 일부 component는 성장 라벨과 반대 방향으로 정렬되어 risk/상태 설명 지표로 분리하는 것이 안전하다.