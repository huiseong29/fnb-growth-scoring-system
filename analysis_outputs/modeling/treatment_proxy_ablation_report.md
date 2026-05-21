# Treatment Proxy Ablation Report

## 목적

답글 관련 feature와 실험/마케팅 상호작용 proxy가 분류 성능에 과도하게 기여하는지 점검했다.

## 결과

| 모델 | AUC | PR-AUC | Brier | F1 | 해석 |
| --- | ---: | ---: | ---: | ---: | --- |
| growth_alpha_nlp | 0.6154 | 0.3924 | 0.3217 | 0.5284 | 전체 텍스트/운영 proxy 포함 기준 모델 |
| growth_alpha_nlp_no_reply_related | 0.6028 | 0.3916 | 0.3146 | 0.4915 | 답글 관련 proxy 제거, AUC 변화 -0.0126 |
| growth_alpha_nlp_no_treatment_proxy | 0.6316 | 0.3974 | 0.2959 | 0.5377 | 실험/마케팅 proxy 제거, AUC 변화 +0.0163 |

## 결론

이 결과는 인과효과 검증이 아니라 treatment proxy contamination 가능성을 점검하기 위한 ablation이다. ATT는 예측 점수에 직접 투입하지 않고 ROI reference layer에만 유지한다.