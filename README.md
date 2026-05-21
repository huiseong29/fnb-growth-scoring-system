# 洹몃줈紐??ㅼ퐫??

> **AI 湲곕컲 F&B ?깆옣 ?좊쭩 留ㅼ옣 ?ㅼ퐫?대쭅 ?쒖뒪??*  
> 瑜대そ 罹≪뒪???붿옄??怨쇱젣 쨌 2026 / F&B 留덉씠?щ줈???횞 AI ?뚭퀬由ъ쬁 ?곌뎄媛쒕컻

?앸떦???좎슜?먯닔泥섎읆 留ㅼ옣???깆옣 媛?μ꽦??0-100?먯쑝濡??섏튂?뷀븳?? ?볤?紐??꾩엯 ?④낵瑜??멸낵異붾줎?쇰줈 利앸챸?섍퀬, ML濡??대뼡 留ㅼ옣???꾩엯 ??媛?????깆옣??蹂쇱? ?덉륫?쒕떎.

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

洹몃줈紐??ㅼ퐫?대뒗 二쇰Ц, 由щ럭, ?댁쁺 ?묐떟, 釉뚮옖??移댄뀒怨좊━, ?몃? ?곴텒 ?곗씠?곕? 寃고빀???깆옣 媛?μ꽦???믪? F&B 留ㅼ옣???좊퀎?섎뒗 ?꾨줈?앺듃??

理쒖쥌 寃곌낵??留ㅼ옣蹂??먯닔, ?깃툒, 異붿쿇 洹쇨굅瑜??쒓났?쒕떎.

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
| Growth Probability | ?깆옣 留ㅼ옣?쇰줈 ?덉륫???뺣쪧                |
| Growth Alpha       | 釉뚮옖??移댄뀒怨좊━ ?됯퇏 ?鍮?珥덇낵 ?깆옣 ?좏샇 |
| Review Growth      | 理쒓렐 由щ럭 利앷? ?먮쫫                      |
| Operation Quality  | ?묐떟瑜좉낵 ?묐떟 ?띾룄 湲곕컲 ?댁쁺 ??웾        |
| Stability          | 二쇰Ц/由щ럭 蹂?숈꽦 湲곕컲 ?덉젙??            |
| Market Fit         | ?몃? ?곴텒 ?곗씠??湲곕컲 ?쒖옣 ?곹빀??       |

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
| `src/build_store_month_panel.py`     | 留ㅼ옣-??遺꾩꽍 ?⑤꼸 ?앹꽦     |
| `src/run_modeling.py`                | Growth Alpha 紐⑤뜽留?       |
| `src/run_seoul_external_modeling.py` | ?몃? ?곴텒 蹂??寃고빀 紐⑤뜽留?|
| `src/build_scores.py`                | 理쒖쥌 ?먯닔 ?곗텧             |
| `src/app.py`                         | 濡쒖뺄 ?곕え ?쒕쾭             |
| `docs/final_outputs_index.md`        | ?꾩껜 ?곗텧臾??몃뜳??        |
| `docs/score_design_rationale.md`     | ?먯닔 ?ㅺ퀎 洹쇨굅             |

## Data

?먮낯 ?곗씠?곕뒗 ??μ냼???ы븿?섏? ?딅뒗??

- `data/`
- `external_data/`

## Final Semantic Freeze Note

- Predictive ranking is based on calibrated model probability.
- Explanation index summarizes interpretable growth-related signals and is not the final predictive ranking score.
- Grade bands are priority review bands, not automatic investment decisions.
- SHAP is used as predictive contribution, not causal attribution.
- ROI is scenario-based decision support, not guaranteed return.
- Direction audit showed that some component scores, including Growth Alpha and stability, are weakly or inversely aligned with the latest-month growth label; this is why public ranking was redefined around calibrated probability.
