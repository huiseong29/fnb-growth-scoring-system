# Modeling Summary

## 목적

성장 유망 매장 분류 모델을 시간 기준 검증, store-level holdout, TopK/lift/calibration 관점에서 보완 검증했다.

## 주요 결과

- baseline: AUC 0.6060, PR-AUC 0.3886, Brier 0.3255, F1 0.5173
- growth_alpha: AUC 0.6078, PR-AUC 0.3912, Brier 0.3245, F1 0.5169
- growth_alpha_nlp: AUC 0.6154, PR-AUC 0.3924, Brier 0.3217, F1 0.5284
- growth_alpha_nlp_without_text_count: AUC 0.6133, PR-AUC 0.3917, Brier 0.3218, F1 0.5249

## 해석

성능 개선폭은 크지 않으므로 정확한 예측 모델이 아니라 후보군 우선순위화와 피드백 반영 검증으로 해석한다.