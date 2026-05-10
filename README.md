# 그로몽 스코어

> **AI 기반 F&B 성장 유망 매장 스코어링 시스템**  
> 르몽 캡스톤 디자인 과제 · 2026 / F&B 마이크로펀드 × AI 알고리즘 연구개발

식당판 신용점수처럼 매장의 성장 가능성을 0-100점으로 수치화한다. 댓글몽 도입 효과를 인과추론으로 증명하고, ML로 어떤 매장이 도입 시 가장 큰 성장을 볼지 예측한다.

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
| Outputs           | CSV, Markdown, SVG                                |

## Overview

그로몽 스코어는 주문, 리뷰, 운영 응답, 브랜드/카테고리, 외부 상권 데이터를 결합해 성장 가능성이 높은 F&B 매장을 선별하는 프로젝트다.

최종 결과는 매장별 점수, 등급, 추천 근거를 제공한다.

## Pipeline

```text
raw data
-> store-month panel
-> growth modeling
-> score calculation
-> recommendation explanation
-> demo
```

## Score Components

| Component          | Description                              |
| ------------------ | ---------------------------------------- |
| Growth Probability | 성장 매장으로 예측될 확률                |
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
python src/run_modeling.py
python src/run_seoul_external_modeling.py
python src/build_scores.py
```

Demo:

```bash
python src/app.py
```

```text
http://127.0.0.1:8765
```

## Key Files

| Path                                 | Description                |
| ------------------------------------ | -------------------------- |
| `src/build_store_month_panel.py`     | 매장-월 분석 패널 생성     |
| `src/run_modeling.py`                | Growth Alpha 모델링        |
| `src/run_seoul_external_modeling.py` | 외부 상권 변수 결합 모델링 |
| `src/build_scores.py`                | 최종 점수 산출             |
| `src/app.py`                         | 로컬 데모 서버             |
| `docs/final_outputs_index.md`        | 전체 산출물 인덱스         |
| `docs/score_design_rationale.md`     | 점수 설계 근거             |

## Data

원본 데이터는 저장소에 포함하지 않는다.

- `data/`
- `external_data/`
