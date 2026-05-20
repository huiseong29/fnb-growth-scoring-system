# 피드백 기반 코드 보완 계획 및 반영 내역

## 1. 피드백 요약

이번 피드백의 핵심은 다음 다섯 가지다.

1. 모델 선택 근거와 SHAP/보정 논리는 강점이다.
2. 댓글 주체 분리와 리뷰 데이터 정제는 좋지만, 텍스트 자체에서 더 깊은 정보를 끌어내는 모델링 단계가 필요하다.
3. 매장 내부 신호 중심이라 외부 상권 데이터, 경쟁 밀도, 유동인구, 임대료 같은 외부 환경 변수가 약하다.
4. DID/PSM/Event Study는 유의미하지만, 이번 과제의 기대 의도는 수치 예측이나 처치효과 추정보다는 성장 유망 매장 **분류**에 더 가깝다.
5. 예측 결과와 실제 투자효과가 분리되어 있으므로 ROI 시뮬레이션이 필요하다.

## 2. 코드 보완 방향

| 피드백 | 코드 반영 | 산출물 |
| --- | --- | --- |
| 분류 중심으로 전환 | `growth_label_top30` 분류 모델을 중심으로 Baseline, Growth Alpha, Growth Alpha + NLP 모델 비교 | `analysis_outputs/modeling/model_comparison.csv` |
| 리뷰 텍스트 심화 | 리뷰 감성/주제 집계 피처를 모델 입력에 병합 | `src/run_modeling.py`, `analysis_outputs/nlp/review_store_month_sentiment.csv` |
| 외부 상권 변수 보강 | 서울 매장 subset에서 내부 모델과 외부 상권 결합 모델 비교 유지 | `src/run_seoul_external_modeling.py` |
| 인과추론 위치 조정 | ATT는 평균 처치효과 참고값으로 사용하고, 최종 선별은 분류 확률 중심으로 설명 | `analysis_outputs/roi/roi_simulation_report.md` |
| ROI 연결 | 성장 확률 × 기대 추가 주문 × 주문당 공헌이익 - 프로그램 비용 구조로 ROI 시뮬레이션 추가 | `src/run_roi_simulation.py` |

## 3. 이번 코드 변경 상세

### 3.1 리뷰 NLP 피처의 분류 모델 통합

`src/run_modeling.py`에 다음 피처를 선택적으로 병합했다.

- `avg_text_sentiment`
- `text_review_count`
- `positive_text_rate`
- `negative_text_rate`
- `taste_rate`
- `portion_rate`
- `delivery_rate`
- `price_rate`
- `service_rate`
- `reorder_rate`

기존 모델 비교는 다음 3개 축으로 확장된다.

```text
baseline
→ growth_alpha
→ growth_alpha_nlp
```

이 변경으로 “리뷰 원문에서 더 깊은 정보를 끌어내는 모델링 단계가 필요하다”는 피드백을 코드 레벨에서 반영했다.

### 3.2 최종 스코어의 예측 모델 우선순위 변경

`src/build_scores.py`는 모델 예측 파일에 `growth_alpha_nlp`가 있으면 이를 우선 사용하고, 없으면 기존 `growth_alpha` 예측을 사용한다.

```text
growth_alpha_nlp 우선
fallback: growth_alpha
```

따라서 리뷰 NLP 피처가 생성된 실행 환경에서는 최종 GroMong Score가 텍스트 신호를 포함한 분류 확률을 사용한다.

### 3.3 ROI 시뮬레이션 추가

`src/run_roi_simulation.py`를 추가했다.

계산식은 다음과 같다.

```text
expected_incremental_orders = final_growth_probability * assumed_monthly_lift_orders
expected_monthly_margin = expected_incremental_orders * gross_margin_per_order
expected_monthly_roi = expected_monthly_margin - monthly_program_cost
```

시나리오는 보수/기본/인과추론 ATT 참고값 3개로 둔다.

- conservative: 월 추가 주문 50건
- base: 월 추가 주문 100건
- causal_att_reference: 월 추가 주문 114건

여기서 ATT는 매장별 효과 예측값이 아니라 평균 처치효과 참고값이다. 최종 우선순위는 매장별 분류 확률과 비용 가정을 결합해 계산한다.

## 4. 발표에서의 포지셔닝 변경

기존 설명은 “인과추론으로 도입 효과를 증명하고 ML로 성장 매장을 예측한다”에 가까웠다. 피드백 반영 후에는 다음처럼 정리하는 것이 더 적합하다.

```text
인과추론은 댓글몽 도입의 평균 효과를 검증하는 보조 근거로 사용한다.
최종 의사결정 모델은 성장 유망 매장 분류 모델이며,
분류 확률을 GroMong Score와 ROI 시뮬레이션으로 연결해 투자 우선순위를 제안한다.
```

## 5. 실행 순서

```powershell
python src/run_review_nlp.py
python src/run_modeling.py
python src/run_seoul_external_modeling.py
python src/build_scores.py
python src/run_roi_simulation.py
```

## 6. 남은 고도화 과제

- 사전 기반 감성분석을 KoBERT/문장 임베딩 기반 텍스트 피처로 교체
- 댓글 주체별 텍스트 피처를 별도 집계해 AI/마케팅/사장님 응답 효과를 분리
- 외부 상권 데이터를 행정동/좌표 단위로 확장
- 경쟁 밀도, 유동인구, 임대료, 배달 수요 지표 추가
- 실제 투자 집행 비용과 매장별 마진율을 반영한 ROI 시나리오 정교화
