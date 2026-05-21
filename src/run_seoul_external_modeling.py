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


def corr_with_label(df, col):
    x = pd.to_numeric(df[col], errors="coerce")
    y = pd.to_numeric(df[TARGET], errors="coerce")
    valid = x.notna() & y.notna()
    if valid.sum() < 3 or x[valid].nunique() <= 1 or y[valid].nunique() <= 1:
        return np.nan
    return float(np.corrcoef(x[valid], y[valid])[0, 1])


def direction_audit(df):
    rows = []
    specs = [
        ("store_vs_market_ticket_ratio", "매장 객단가 / 동일 자치구·유사업종 평균 객단가"),
        ("market_q4_avg_ticket", "동일 자치구·유사업종 평균 객단가"),
        ("market_q4_sales_amount", "동일 자치구·유사업종 4분기 매출 규모"),
        ("market_q4_sales_count", "동일 자치구·유사업종 4분기 주문 수"),
    ]
    for col, desc in specs:
        if col not in df.columns:
            continue
        tmp = df[[TARGET, col]].copy()
        tmp[col] = pd.to_numeric(tmp[col], errors="coerce")
        tmp = tmp.dropna()
        growth = tmp[tmp[TARGET] == 1][col]
        non_growth = tmp[tmp[TARGET] == 0][col]
        growth_mean = float(growth.mean()) if len(growth) else np.nan
        non_growth_mean = float(non_growth.mean()) if len(non_growth) else np.nan
        gap = growth_mean - non_growth_mean if pd.notna(growth_mean) and pd.notna(non_growth_mean) else np.nan
        direction = "높을수록 성장과 양의 방향" if pd.notna(gap) and gap > 0 else "높을수록 좋다고 보기 어려움"
        if col == "store_vs_market_ticket_ratio":
            direction = "단순히 높을수록 좋은 점수로 쓰기보다 1에 가까운 가격 적합성으로 해석 필요" if pd.notna(gap) else direction
        rows.append({
            "feature": col,
            "description": desc,
            "rows": int(len(tmp)),
            "growth_mean": growth_mean,
            "non_growth_mean": non_growth_mean,
            "growth_minus_non_growth": gap,
            "corr_with_growth_label": corr_with_label(tmp, col),
            "recommended_scoring_direction": direction,
            "limitation": "서울 외부 상권 결합 매장 211개 subset 기준이므로 전국 일반화 근거로 사용하지 않음",
        })
    return pd.DataFrame(rows)


def write_report(metrics_df, topn_df, rows_info, audit_df):
    internal = metrics_df[metrics_df["model"] == "seoul_internal"].iloc[0]
    external = metrics_df[metrics_df["model"] == "seoul_external"].iloc[0]
    delta_auc = external["auc"] - internal["auc"]
    lines = [
        "# Seoul External Modeling Summary", "", "## 목적", "",
        "서울 211개 외부 상권 결합 subset에서 상권 변수가 성장 유망 매장 분류에 추가 설명력을 갖는지 점검했다.", "",
        "## 데이터 범위", "",
        f"- 서울 외부 상권 결합 매장 수: {rows_info['stores']}",
        f"- 학습 행 수: {rows_info['train_rows']}",
        f"- 검증 행 수: {rows_info['test_rows']}",
        "- 학습 기간: 2025-01 ~ 2025-07",
        "- 검증 기간: 2025-08 ~ 2025-09", "",
        "## 비교 모델", "",
        "- seoul_internal: 내부 운영/성장 이력 feature",
        "- seoul_external: 내부 feature + 서울 상권 매출/주문/객단가/상대 객단가 feature", "",
        "## 주요 결과", "",
        f"- Internal AUC: {internal['auc']:.4f}",
        f"- External AUC: {external['auc']:.4f}",
        f"- AUC 변화: {delta_auc:+.4f}",
        f"- Internal PR-AUC: {internal['pr_auc']:.4f}",
        f"- External PR-AUC: {external['pr_auc']:.4f}", "",
        "## 방향성 점검", "",
        "| feature | 성장 평균 | 비성장 평균 | 차이 | 상관 | 해석 |",
        "| --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in audit_df.itertuples(index=False):
        lines.append(f"| {row.feature} | {row.growth_mean:.4f} | {row.non_growth_mean:.4f} | {row.growth_minus_non_growth:.4f} | {row.corr_with_growth_label:.4f} | {row.recommended_scoring_direction} |")
    lines.extend(["", "## 해석", ""])
    if delta_auc > 0:
        lines.append("외부 상권 feature 추가 후 AUC가 개선되었지만, subset 규모가 작으므로 전사 모델의 핵심 근거가 아니라 서울 매장의 보조 설명 변수로만 사용한다.")
    else:
        lines.append("외부 상권 feature 추가만으로 명확한 성능 개선은 확인되지 않았다. 다만 store_vs_market_ticket_ratio의 방향성을 audit해 단순 고득점 가정의 위험을 문서화했다.")
    lines.append("서울 211개 subset 한계 때문에 전국 점수에는 약한 보정으로만 반영하고, 발표에서는 외부 환경 변수를 연결했다는 방어 근거로 제시한다.")
    (OUT_DIR / "seoul_external_modeling_report.md").write_text("\n".join(lines), encoding="utf-8")


def main():
    df = pd.read_csv(PANEL_PATH, encoding="utf-8-sig")
    df = df[(df["is_label_valid"] == 1) & df["market_q4_sales_amount"].notna()].copy()
    df[TARGET] = pd.to_numeric(df[TARGET], errors="coerce").astype(int)

    train = df[(df[TIME_COL] >= "2025-01") & (df[TIME_COL] <= "2025-07")].copy()
    test = df[(df[TIME_COL] >= "2025-08") & (df[TIME_COL] <= "2025-09")].copy()

    rows_info = {"stores": df["platform_shop_id"].nunique(), "train_rows": len(train), "test_rows": len(test)}
    results, preds, coefs, tops = [], [], [], []
    model_specs = [
        ("seoul_internal", BASE_NUMERIC + GROWTH_NUMERIC),
        ("seoul_external", BASE_NUMERIC + GROWTH_NUMERIC + EXTERNAL_NUMERIC),
    ]
    for name, numeric_cols in model_specs:
        metrics, pred, coef, top, _, _ = evaluate_model(name, train, test, numeric_cols, CATEGORICAL, "seoul_time")
        results.append(metrics)
        preds.append(pred)
        coefs.append(coef)
        tops.append(top)

    metrics_df = pd.DataFrame(results)
    pred_df = pd.concat(preds, ignore_index=True)
    coef_df = pd.concat(coefs, ignore_index=True)
    topn_df = pd.concat(tops, ignore_index=True)
    audit_df = direction_audit(df)

    metrics_df.to_csv(OUT_DIR / "seoul_external_model_comparison.csv", index=False, encoding="utf-8-sig")
    pred_df.to_csv(OUT_DIR / "seoul_external_predictions.csv", index=False, encoding="utf-8-sig")
    coef_df.to_csv(OUT_DIR / "seoul_external_coefficients.csv", index=False, encoding="utf-8-sig")
    topn_df.to_csv(OUT_DIR / "seoul_external_topn_metrics.csv", index=False, encoding="utf-8-sig")
    audit_df.to_csv(OUT_DIR / "external_direction_audit.csv", index=False, encoding="utf-8-sig")

    examples = pred_df[pred_df["model"] == "seoul_external"].copy()
    examples = examples.sort_values("growth_probability", ascending=False).head(50)
    examples.to_csv(OUT_DIR / "seoul_external_top_store_examples.csv", index=False, encoding="utf-8-sig")

    write_report(metrics_df, topn_df, rows_info, audit_df)
    print(metrics_df.to_string(index=False))
    print(audit_df.to_string(index=False))
    print(f"WROTE {OUT_DIR}")


if __name__ == "__main__":
    main()
