# 그로몽 스코어

> **AI 기반 F&B 성장 유망 매장 스코어링 시스템**  
> 르몽 캡스톤 디자인 과제 · 2026 / F&B 마이크로펀드 × AI 알고리즘 연구개발

F&B 매장의 주문·리뷰·운영 신호를 바탕으로 성장 후보군을 우선순위화하고, 주요 신호를 설명용 지수로 정리하는 ML 기반 의사결정 보조 프로젝트다.

<p>
  <img alt="Python" src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white">
  <img alt="pandas" src="https://img.shields.io/badge/pandas-150458?style=flat-square&logo=pandas&logoColor=white">
  <img alt="NumPy" src="https://img.shields.io/badge/NumPy-013243?style=flat-square&logo=numpy&logoColor=white">
  <img alt="CSV" src="https://img.shields.io/badge/CSV%20Pipeline-4B5563?style=flat-square">
  <img alt="Local Demo" src="https://img.shields.io/badge/Local%20Demo-111827?style=flat-square">
</p>

## Tech Stack

| Layer             | Stack                                             |
| ----------------- | ------------------------------------------------- |
| Language          | Python                                            |
| Data Processing   | pandas, NumPy                                     |
| Modeling Pipeline | CSV-based feature engineering and scoring scripts |
| Demo              | Python standard library HTTP server               |
| Outputs           | CSV, Markdown, SVG/PNG                            |

## Overview

그로몽 스코어는 주문, 리뷰, 운영 응답, 브랜드/카테고리, 외부 상권 데이터를 결합해 성장 가능성이 있는 F&B 매장을 검토 우선순위로 정렬하는 프로젝트다.

최종 public ranking은 calibrated model probability를 기준으로 하며, 기존 composite score는 `explanation_index` 또는 `signal_decomposition_index`로 정리해 주요 신호 해석에 사용한다.

## Pipeline

```text
raw data
-> store-month panel
-> growth modeling
-> score calculation
-> recommendation explanation
-> demo
```

최종 제출 기준의 public artifact는 `predictive_rank_score`와 `predicted_priority_rank`를 ranking 기준으로 사용한다. `decision_band`는 자동 투자 결정이 아니라 priority review band이며, ROI는 가정 기반 scenario 분석으로만 해석한다.

## Score Components

| Component          | Description                              |
| ------------------ | ---------------------------------------- |
| Growth Probability | calibrated probability 기반 ranking 신호 |
| Growth Alpha       | 브랜드/카테고리 평균 대비 초과 성장 신호 |
| Review Growth      | 최근 리뷰 증가 흐름                      |
| Operation Quality  | 응답률과 응답 속도 기반 운영 역량        |
| Stability          | 주문/리뷰 변동성 기반 안정성             |
| Market Fit         | 외부 상권 데이터 기반 시장 적합도        |

## Structure

```text
.
+-- src/                 # analysis, modeling, scoring, demo
+-- docs/                # project documents
+-- analysis_outputs/    # generated outputs
+-- data/                # ignored raw data
+-- external_data/       # ignored external data
+-- README.md
```

## Run

```bash
python src/build_store_month_panel.py
python src/run_review_nlp.py
python src/run_modeling.py
python src/run_seoul_external_modeling.py
python src/build_scores.py
python src/run_roi_simulation.py
python src/run_score_direction_audit.py
python src/finalize_public_artifacts.py
```

Demo:

```bash
python src/app.py
```

```text
http://127.0.0.1:8765
```

## Key Files

| Path                                      | Description                             |
| ----------------------------------------- | --------------------------------------- |
| `src/build_store_month_panel.py`          | 매장-월 분석 패널 생성                  |
| `src/run_review_nlp.py`                   | 리뷰/답글 기반 NLP feature 생성         |
| `src/run_modeling.py`                     | 성장 후보군 분류 모델링 및 검증         |
| `src/run_seoul_external_modeling.py`      | 외부 상권 변수 결합 및 방향성 점검      |
| `src/build_scores.py`                     | score component와 내부 scoring 산출     |
| `src/run_roi_simulation.py`               | ROI scenario 분석                       |
| `src/run_weight_sensitivity.py`           | score weight sensitivity 분석           |
| `src/run_score_direction_audit.py`        | component 방향성 및 ranking 기준 점검   |
| `src/finalize_public_artifacts.py`        | public-safe artifact 생성 및 gate 실행  |
| `src/app.py`                              | 로컬 데모 서버                          |
| `docs/final_outputs_index.md`             | 전체 산출물 인덱스                      |
| `docs/score_design_rationale.md`          | 점수 설계 근거                          |
| `analysis_outputs/final_model_card.md`    | 최종 모델 카드                          |
| `analysis_outputs/final_gap_closure_report.md` | 피드백 반영 및 한계 정리          |

주요 제출 산출물은 `analysis_outputs/scoring/latest_shop_scores_public.csv`, `analysis_outputs/scoring/store_ranking_topN.csv`, `analysis_outputs/final_freeze_manifest.json`, `analysis_outputs/final_public_artifact_gate_report.md`에 정리되어 있다. 세부 제출/backup/제외 파일 목록은 `analysis_outputs/final_submission_manifest.md`를 참고한다.

## Data

원본 데이터는 저장소에 포함하지 않는다.

- `data/`
- `external_data/`

## Notes

검증은 time split, store-level group holdout, leakage check, calibration, Top-K/lift, score direction audit 중심으로 정리했다. 상세 수치는 `analysis_outputs/`의 보고서를 참고한다.

본 프로젝트는 capstone PoC이며, ranking은 자동 투자 결정이 아니라 후보군 검토 우선순위로 사용한다. `explanation_index`는 예측 순위 기준이 아니라 신호 해석용 지수다.
