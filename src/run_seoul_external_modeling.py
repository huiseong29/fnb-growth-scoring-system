from pathlib import Path

import numpy as np
import pandas as pd

from run_modeling import (
    BASE_NUMERIC,
    CATEGORICAL,
    GROWTH_NUMERIC,
    TARGET,
    TIME_COL,
    evaluate_model,
)


PANEL_PATH = Path("analysis_outputs/store_month_panel.csv")
OUT_DIR = Path("analysis_outputs/seoul_external_modeling")
OUT_DIR.mkdir(parents=True, exist_ok=True)

EXTERNAL_NUMERIC = [
    "market_q4_sales_amount",
    "market_q4_sales_count",
    "market_q4_avg_ticket",
    "store_vs_market_ticket_ratio",
]


def write_report(metrics_df, topn_df, rows_info):
    internal = metrics_df[metrics_df["model"] == "seoul_internal"].iloc[0]
    external = metrics_df[metrics_df["model"] == "seoul_external"].iloc[0]
    lines = [
        "# Seoul External Modeling Summary",
        "",
        "## 목적",
        "",
        "이번 검증의 목적은 서울 매장 211개 subset에서 외부 상권 데이터가 성장 유망 매장 예측에 실제로 기여하는지 확인하는 것이다.",
        "",
        "본 프로젝트의 차별점은 상권·브랜드·카테고리 효과를 고려한 Growth Alpha 기반 스코어링이므로, 외부 상권 변수의 실질적 기여도 검증이 중요하다.",
        "",
        "## 데이터 범위",
        "",
        f"- 서울 외부 상권 결합 매장 수: {rows_info['stores']}",
        f"- 학습 행 수: {rows_info['train_rows']}",
        f"- 검증 행 수: {rows_info['test_rows']}",
        "- 학습 기간: 2025-01 ~ 2025-07",
        "- 검증 기간: 2025-08 ~ 2025-09",
        "",
        "## 비교 모델",
        "",
        "- Seoul Internal: 내부 변수 + 과거 기반 Growth Alpha 변수",
        "- Seoul External: Seoul Internal + 외부 상권 변수",
        "",
        "## 주요 결과",
        "",
        f"- Seoul Internal AUC: {internal['auc']:.4f}",
        f"- Seoul External AUC: {external['auc']:.4f}",
        f"- Seoul Internal F1: {internal['f1']:.4f}",
        f"- Seoul External F1: {external['f1']:.4f}",
        "",
        "## Top N 결과",
        "",
    ]
    for _, row in topn_df.iterrows():
        lines.append(f"- {row['model']} Top {int(row['top_n'])} Precision: {row['precision_at_n']:.3f}")
    lines.extend(["", "## 해석", ""])
    if external["auc"] > internal["auc"]:
        lines.append("외부 상권 변수를 추가했을 때 AUC가 개선되었다. 이는 상권 정보를 결합하는 것이 성장 유망 매장 선별에 실질적으로 기여할 수 있음을 보여준다.")
    else:
        lines.append("외부 상권 변수를 추가했을 때 AUC 개선은 확인되지 않았다. 현재 서울 subset 규모가 작고 자치구 단위 결합이라 신호가 제한적일 수 있다. 다만 외부 상권 변수는 매장 점수를 해석할 때 상권 대비 위치를 설명하는 보조 지표로 활용 가능하다.")
    lines.extend(
        [
            "",
            "## 다음 작업",
            "",
            "모델 결과를 바탕으로 최종 GroMong Score 산출식을 만들고, 매장별 점수와 주요 근거를 생성한다.",
        ]
    )
    (OUT_DIR / "seoul_external_modeling_report.md").write_text("\n".join(lines), encoding="utf-8")


def main():
    df = pd.read_csv(PANEL_PATH, encoding="utf-8-sig")
    df = df[(df["is_label_valid"] == 1) & df["market_q4_sales_amount"].notna()].copy()
    df[TARGET] = pd.to_numeric(df[TARGET], errors="coerce").astype(int)

    train = df[(df[TIME_COL] >= "2025-01") & (df[TIME_COL] <= "2025-07")].copy()
    test = df[(df[TIME_COL] >= "2025-08") & (df[TIME_COL] <= "2025-09")].copy()

    rows_info = {
        "stores": df["platform_shop_id"].nunique(),
        "train_rows": len(train),
        "test_rows": len(test),
    }

    results = []
    preds = []
    coefs = []
    tops = []
    model_specs = [
        ("seoul_internal", BASE_NUMERIC + GROWTH_NUMERIC),
        ("seoul_external", BASE_NUMERIC + GROWTH_NUMERIC + EXTERNAL_NUMERIC),
    ]
    for name, numeric_cols in model_specs:
        metrics, pred, coef, top = evaluate_model(name, train, test, numeric_cols, CATEGORICAL)
        results.append(metrics)
        preds.append(pred)
        coefs.append(coef)
        tops.append(top)

    metrics_df = pd.DataFrame(results)
    pred_df = pd.concat(preds, ignore_index=True)
    coef_df = pd.concat(coefs, ignore_index=True)
    topn_df = pd.concat(tops, ignore_index=True)

    metrics_df.to_csv(OUT_DIR / "seoul_external_model_comparison.csv", index=False, encoding="utf-8-sig")
    pred_df.to_csv(OUT_DIR / "seoul_external_predictions.csv", index=False, encoding="utf-8-sig")
    coef_df.to_csv(OUT_DIR / "seoul_external_coefficients.csv", index=False, encoding="utf-8-sig")
    topn_df.to_csv(OUT_DIR / "seoul_external_topn_metrics.csv", index=False, encoding="utf-8-sig")

    # Store-level examples for presentation: highest predicted external model rows.
    examples = pred_df[pred_df["model"] == "seoul_external"].copy()
    examples = examples.sort_values("growth_probability", ascending=False).head(50)
    examples.to_csv(OUT_DIR / "seoul_external_top_store_examples.csv", index=False, encoding="utf-8-sig")

    write_report(metrics_df, topn_df, rows_info)

    print(metrics_df.to_string(index=False))
    print(topn_df.to_string(index=False))
    print(f"WROTE {OUT_DIR}")


if __name__ == "__main__":
    main()
