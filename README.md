# 그로몽 스코어 — AI 기반 성장 유망 매장 스코어링

르몽 캡스톤 디자인 과제 · 2026 / F&B 마이크로펀드 × AI 알고리즘 연구개발

식당판 신용점수처럼 매장의 성장 가능성을 0-100점으로 수치화한다. 댓글몽 도입 효과를 인과추론으로 증명하고, ML로 어떤 매장이 도입 시 가장 큰 성장을 볼지 예측한다.

## 프로젝트 개요

그로몽 스코어는 F&B 매장의 주문, 리뷰, 운영 응답, 브랜드/카테고리, 외부 상권 데이터를 결합해 성장 가능성이 높은 매장을 선별하는 스코어링 시스템이다.

핵심 목표는 다음과 같다.

- 댓글몽 도입 이후 성장 효과를 데이터 기반으로 검증
- 매장별 성장 가능성을 예측하는 Growth Alpha 모델 구축
- 예측 확률과 운영/리뷰/시장 적합도 지표를 결합한 0-100점 스코어 산출
- 추천 대상 매장을 등급화하고, 점수 근거를 설명 가능한 형태로 제공

## 주요 산출물

- `analysis_outputs/store_month_panel.csv`: 매장-월 단위 분석 패널
- `analysis_outputs/modeling/`: Baseline vs Growth Alpha 모델링 결과
- `analysis_outputs/seoul_external_modeling/`: 서울 외부 상권 변수 결합 모델링 결과
- `analysis_outputs/scoring/`: 최종 GroMong Score 및 매장별 설명
- `analysis_outputs/demo/`: 데모 서버 검증 및 사용 가이드
- `docs/final_outputs_index.md`: 전체 산출물 위치와 설명
- `docs/score_design_rationale.md`: 스코어 설계 및 가중치 근거

## 프로젝트 구조

```text
.
+-- src/
|   +-- build_store_month_panel.py
|   +-- check_external_fit.py
|   +-- run_eda.py
|   +-- make_eda_charts.py
|   +-- run_modeling.py
|   +-- run_seoul_external_modeling.py
|   +-- build_scores.py
|   +-- make_score_charts.py
|   +-- run_review_nlp.py
|   +-- make_review_nlp_charts.py
|   +-- run_calibrated_score.py
|   +-- run_score_sensitivity.py
|   +-- run_imbalance_balanced_recommendations.py
|   +-- app.py
+-- analysis_outputs/
+-- docs/
+-- data/              # 원본 데이터, Git 제외
+-- external_data/     # 외부 상권 데이터, Git 제외
+-- README.md
```

`data/`와 `external_data/`는 개인정보 및 원천 데이터 보호를 위해 Git에 업로드하지 않는다.

## 실행 순서

프로젝트 루트에서 실행한다.

```bash
python src/build_store_month_panel.py
python src/run_eda.py
python src/run_modeling.py
python src/run_seoul_external_modeling.py
python src/build_scores.py
python src/make_score_charts.py
```

리뷰 NLP, 보정 점수, 민감도 분석, 불균형 보정 추천은 필요에 따라 추가 실행한다.

```bash
python src/run_review_nlp.py
python src/run_calibrated_score.py
python src/run_score_sensitivity.py
python src/run_imbalance_balanced_recommendations.py
```

## 데모 실행

최종 스코어 파일이 생성된 뒤 데모 서버를 실행한다.

```bash
python src/app.py
```

기본 주소:

```text
http://127.0.0.1:8765
```

## 스코어 구성

GroMong Score는 다음 지표를 결합한다.

- 성장 예측 확률
- 브랜드/카테고리 대비 Growth Alpha
- 최근 리뷰 성장성
- 응답률 및 응답 속도 기반 운영 역량
- 주문/리뷰 변동성 기반 안정성
- 서울 외부 상권 데이터 기반 시장 적합도

최종 결과는 매장별 점수, 등급, 주요 추천 근거를 함께 제공한다.

## 데이터 정책

이 저장소에는 코드와 문서, 일부 산출물만 포함한다. 원본 매장 데이터와 외부 상권 원천 데이터는 포함하지 않는다.

제외 항목:

- `data/`
- `external_data/`
- 로컬 환경 변수 파일
- Python 캐시 및 가상환경

## 문서

- `docs/project_plan.md`: 전체 실행 계획과 진행 상태
- `docs/project_proposal.md`: 문제 정의, 방법론, 결과 해석
- `docs/remaining_tasks.md`: 남은 작업 목록
- `docs/final_outputs_index.md`: 산출물 인덱스
- `docs/score_design_rationale.md`: 점수 설계 근거
- `docs/midterm_quality_boost_plan.md`: 중간 발표 보완 계획
