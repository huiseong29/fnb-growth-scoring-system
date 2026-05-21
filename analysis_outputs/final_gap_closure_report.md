# 최종 피드백 반영 및 검증 보완 보고서

## 보고서 목적

본 보고서는 최종 발표 전 reviewer가 지적할 수 있는 검증 신뢰도, 텍스트 피처의 얕음, treatment proxy contamination, ROI 연결 부족, 외부 상권 변수 방향성 문제를 코드와 산출물 기준으로 보완한 결과를 정리한다.

이번 보완의 목표는 모델 성능을 대폭 끌어올리는 것이 아니라, 기존 분류 파이프라인이 어떤 기준으로 검증되었고 어떤 한계를 인정하는지 명확히 만드는 것이다.

## 핵심 결론

- Time split 기준 full NLP 모델 AUC는 0.6154, PR-AUC는 0.3924, Brier score는 0.3217이다. baseline AUC 0.6060 대비 개선폭은 작다.
- Store-level group holdout에서는 full NLP 모델 AUC 0.7132, PR-AUC 0.4834, Top100 lift 1.90로 시간 분할 외 검증을 추가했다.
- NLP 피처는 KoBERT 없이 사전 기반 텍스트 피처와 답글 피처를 확장했다. 성장 매장은 has_reply가 비성장 매장 대비 +0.0798, reply_template_score가 +0.0443 높다.
- ROI는 band-calibrated probability를 추가했다. base 시나리오 Top100의 보정 기대 hit는 40.86, 보정 기대 ROI 합계는 258,535원이다.
- 서울 외부 상권 모델은 AUC 0.5826에서 0.5995로 소폭 개선됐다. 다만 store_vs_market_ticket_ratio는 성장 매장 평균 0.8628, 비성장 매장 평균 0.9230로 단순히 높을수록 좋다고 보기 어렵다.

## 피드백별 반영 현황

| 피드백 | 기존 상태 | 보완 코드 | 생성 artifact | 핵심 수치 | 남은 한계 |
| --- | --- | --- | --- | --- | --- |
| 분류 검증 신뢰도 부족 | Time split 중심의 AUC/F1 비교에 가까웠음 | `src/run_modeling.py`에 PR-AUC, Brier, lift@K, recall@K, TopK hit, calibration band, store-level group holdout 추가 | `model_validation_audit.csv`, `group_holdout_metrics.csv`, `calibration_lift_table.csv` | Time full NLP AUC 0.6154, PR-AUC 0.3924, Brier 0.3217; group holdout AUC 0.7132 | 검증 방식은 늘었지만 외부 독립 데이터 검증은 아님 |
| 텍스트 분석이 얕음 | 감성/카테고리 사전 기반 요약 중심 | `src/run_review_nlp.py`에 review_length, token_count, 긍정/부정 hit, 혼합 감성, 답글 길이/쿠폰/템플릿/AI-like 피처 추가 | `review_text_features.csv`, `reply_text_features.csv`, `nlp_ablation_report.csv` | has_reply gap +0.0798, negative_hit_count gap -0.0162 | KoBERT fine-tuning은 시간 대비 효율이 낮아 future work로만 둠 |
| 댓글 주체/답글 feature가 treatment proxy일 수 있음 | 답글/AI/마케팅 proxy가 성능에 섞여도 분리 점검이 약했음 | reply-related 제거 모델, treatment proxy 제거 모델 추가 | `treatment_proxy_ablation_report.md` | no_reply AUC 0.6028; no_treatment_proxy AUC 0.6316; full AUC 0.6154 | proxy 제거 후 성능이 더 좋아지는 구간이 있어 인과효과가 아니라 예측 feature로 제한 해석 필요 |
| 예측과 ROI가 분리됨 | ROI 가정이 코드 내부 하드코딩, 확률 보정 연결 약함 | `src/run_roi_simulation.py`가 assumptions CSV를 읽고 raw/calibrated ROI를 함께 계산 | `roi_assumptions.csv`, `topk_roi_summary.csv`, `roi_simulation_by_store.csv` | base Top100 보정 expected hits 40.86, 보정 ROI 258,535원 | ROI는 실제 비용/마진 가정에 민감한 scenario layer임 |
| ATT를 예측 점수에 어떻게 연결할지 불명확 | 인과추론 결과와 score가 분리되어 보임 | ATT는 predictive score에 넣지 않고 causal_att_reference ROI 시나리오로만 유지 | `topk_roi_summary.csv`, `roi_simulation_report.md` | ATT reference Top100 보정 ROI 1,974,730원 | causal forest/uplift model은 구현하지 않았고 평균 효과 참고값으로 제한 |
| 외부 상권 변수가 약함 | 서울 상권 feature가 보조적으로만 존재 | `src/run_seoul_external_modeling.py`에 방향성 audit 추가, `build_scores.py`에서 가격비율 단순 고득점 방식을 가격 적합성으로 수정 | `external_direction_audit.csv`, `seoul_external_model_comparison.csv` | Seoul external AUC 변화 +0.0170; ratio 성장-비성장 평균 차이 -0.0602 | 서울 211개 결합 subset 기준이라 전국 일반화 근거로 쓰지 않음 |

## 성능 개선폭이 작은 문제에 대한 방어 논리

성능 개선폭은 크지 않다. 따라서 발표에서는 `모델 성능을 크게 개선했다`고 말하지 않는다. 대신 다음 세 가지를 중심으로 설명한다.

1. 검증 관점이 넓어졌다. AUC/F1만 보던 구조에서 PR-AUC, Brier, TopK hit, lift, calibration gap, store-level holdout까지 확인했다.
2. 의사결정 관점으로 연결했다. raw probability와 band-calibrated probability를 ROI로 연결해 Top20/50/100 후보군의 기대 효과를 산출했다.
3. reviewer가 공격할 수 있는 proxy와 외부 상권 방향성을 숨기지 않았다. reply proxy, treatment proxy, store_vs_market_ticket_ratio의 한계를 별도 artifact로 남겼다.

## 최종 발표에서 강하게 말해도 되는 표현

- 성장 예측 모델의 검증 신뢰도를 AUC 중심에서 PR-AUC, calibration, TopK lift, store-level holdout까지 확장했다.
- 텍스트는 대형 모델 없이도 사전 기반 리뷰/답글 feature와 ablation으로 분류 파이프라인에 연결했다.
- ATT는 예측 점수에 직접 넣지 않고 ROI scenario/reference layer로 분리해 인과추론과 예측 모델의 역할을 구분했다.
- 외부 상권 변수는 서울 subset의 보조 feature로 제한하고, 방향성 audit를 통해 단순 고득점 가정의 위험을 점검했다.

## 낮춰 말해야 할 표현

- `성능이 크게 개선되었다`는 표현은 부적절하다. 개선폭이 제한적이다.
- `인과효과를 개인 매장별 score에 반영했다`고 말하면 안 된다. ATT는 ROI reference로만 사용했다.
- `외부 상권 변수가 전국 모델을 설명한다`고 말하면 안 된다. 서울 211개 subset 한계가 있다.
- `KoBERT 수준의 텍스트 이해를 했다`고 말하면 안 된다. 현재는 사전 기반 feature engineering이다.

## 발표용 artifact 주의사항

발표용 표와 이미지에는 내부 학습 라벨, 미래 주문 파생값, treatment 계열 컬럼을 직접 노출하지 않는다. 필요한 경우 `성장 여부`, `검증 구간`, `운영 개입 proxy 제거 모델`처럼 추상화해서 설명한다.