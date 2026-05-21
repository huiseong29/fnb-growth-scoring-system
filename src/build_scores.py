from pathlib import Path

import numpy as np
import pandas as pd


PANEL_PATH = Path("analysis_outputs/store_month_panel.csv")
MODEL_PRED_PATH = Path("analysis_outputs/modeling/model_predictions.csv")
SEOUL_PRED_PATH = Path("analysis_outputs/seoul_external_modeling/seoul_external_predictions.csv")
OUT_DIR = Path("analysis_outputs/scoring")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def minmax(series):
    s = pd.to_numeric(series, errors="coerce")
    lo = s.quantile(0.05)
    hi = s.quantile(0.95)
    if pd.isna(lo) or pd.isna(hi) or hi == lo:
        return pd.Series(np.full(len(series), 50.0), index=series.index)
    return ((s.clip(lo, hi) - lo) / (hi - lo) * 100).fillna(50)


def inverse_minmax(series):
    return 100 - minmax(series)


def grade(score):
    if score >= 80:
        return "A"
    if score >= 65:
        return "B"
    if score >= 50:
        return "C"
    return "D"


def latest_valid_rows(panel):
    valid = panel[panel["is_label_valid"] == 1].copy()
    # 2025-09 is the latest month where future 3m label exists.
    latest_month = valid["year_month"].max()
    return valid[valid["year_month"] == latest_month].copy(), latest_month


def reason_text(row):
    reasons = []
    if row["growth_alpha_score"] >= 70:
        reasons.append("브랜드·카테고리 평균 대비 초과 성장 신호가 강함")
    elif row["growth_alpha_score"] <= 35:
        reasons.append("브랜드·카테고리 평균 대비 성장 신호가 약함")

    if row["review_growth_score"] >= 70:
        reasons.append("최근 리뷰 성장 흐름이 우수함")
    elif row["review_count"] >= row["review_count_p75"]:
        reasons.append("월 리뷰 수가 전체 매장 상위권에 속함")

    if row["operation_score"] >= 70:
        reasons.append("답글률과 응답속도 기준 운영 대응력이 우수함")
    elif row["reply_rate"] >= 0.8:
        reasons.append("리뷰 답글률이 높아 고객 대응 신호가 좋음")

    if row.get("is_seoul_external", 0) == 1:
        if row.get("market_fit_score", 50) >= 70:
            reasons.append("서울 상권 규모와 가격 포지션이 비교적 적합함")
        elif row.get("market_fit_score", 50) <= 35:
            reasons.append("서울 상권 규모 또는 가격 포지션 보조 지표가 약함")

    if row["stability_score"] >= 70:
        reasons.append("주문·리뷰 변동성이 낮아 안정성이 높음")

    if not reasons:
        reasons.append("주문, 리뷰, 운영 지표가 전반적으로 평균권에 위치함")

    # Keep strongest three without duplicates.
    uniq = []
    for r in reasons:
        if r not in uniq:
            uniq.append(r)
    return uniq[:3]


def main():
    panel = pd.read_csv(PANEL_PATH, encoding="utf-8-sig")
    latest, latest_month = latest_valid_rows(panel)

    pred_all = pd.read_csv(MODEL_PRED_PATH, encoding="utf-8-sig")
    model_priority = ["growth_alpha_nlp", "growth_alpha"]
    available_models = pred_all["model"].dropna().unique().tolist()
    selected_model = next((m for m in model_priority if m in available_models), "growth_alpha")
    pred = pred_all[(pred_all["model"] == selected_model) & (pred_all["year_month"] == latest_month)][
        ["platform_shop_id", "year_month", "growth_probability"]
    ].rename(columns={"growth_probability": "model_growth_probability"})

    seoul_pred = pd.read_csv(SEOUL_PRED_PATH, encoding="utf-8-sig")
    seoul_pred = seoul_pred[(seoul_pred["model"] == "seoul_external") & (seoul_pred["year_month"] == latest_month)][
        ["platform_shop_id", "year_month", "growth_probability"]
    ].rename(columns={"growth_probability": "seoul_external_growth_probability"})

    score_df = latest.merge(pred, on=["platform_shop_id", "year_month"], how="left")
    score_df = score_df.merge(seoul_pred, on=["platform_shop_id", "year_month"], how="left")
    score_df["is_seoul_external"] = score_df["seoul_external_growth_probability"].notna().astype(int)
    score_df["selected_prediction_model"] = selected_model
    score_df["final_growth_probability"] = score_df["seoul_external_growth_probability"].fillna(score_df["model_growth_probability"])

    numeric_cols = [
        "selected_prediction_model",
        "final_growth_probability",
        "historical_internal_growth_alpha",
        "historical_review_growth_3m",
        "reply_rate",
        "avg_reply_delay_hours",
        "review_count",
        "order_count",
        "sales_amount",
        "store_vs_market_ticket_ratio",
        "market_q4_avg_ticket",
    ]
    for col in numeric_cols:
        score_df[col] = pd.to_numeric(score_df[col], errors="coerce")

    score_df["probability_score"] = score_df["final_growth_probability"].fillna(score_df["final_growth_probability"].median()) * 100
    score_df["growth_alpha_score"] = minmax(score_df["historical_internal_growth_alpha"])
    score_df["review_growth_score"] = minmax(score_df["historical_review_growth_3m"])

    reply_score = minmax(score_df["reply_rate"])
    delay_score = inverse_minmax(score_df["avg_reply_delay_hours"])
    score_df["operation_score"] = (0.65 * reply_score + 0.35 * delay_score).fillna(50)

    order_stability = inverse_minmax(score_df.groupby("platform_shop_id")["order_count"].transform("std"))
    review_stability = inverse_minmax(score_df.groupby("platform_shop_id")["review_count"].transform("std"))
    # With one latest row per store, transformed std is mostly NaN, so use recent panel volatility.
    recent = panel[(panel["year_month"] >= "2025-06") & (panel["year_month"] <= latest_month)].copy()
    recent["order_count"] = pd.to_numeric(recent["order_count"], errors="coerce")
    recent["review_count"] = pd.to_numeric(recent["review_count"], errors="coerce")
    vol = recent.groupby("platform_shop_id").agg(order_std=("order_count", "std"), review_std=("review_count", "std")).reset_index()
    score_df = score_df.merge(vol, on="platform_shop_id", how="left")
    score_df["stability_score"] = (0.6 * inverse_minmax(score_df["order_std"]) + 0.4 * inverse_minmax(score_df["review_std"])).fillna(50)

    market_scale_score = minmax(score_df["market_q4_avg_ticket"])
    ticket_parity_score = inverse_minmax((score_df["store_vs_market_ticket_ratio"] - 1).abs())
    score_df["market_fit_score"] = (0.45 * market_scale_score + 0.55 * ticket_parity_score).where(score_df["is_seoul_external"] == 1, 50)

    score_df["gromong_score"] = (
        0.35 * score_df["probability_score"]
        + 0.25 * score_df["growth_alpha_score"]
        + 0.15 * score_df["review_growth_score"]
        + 0.15 * score_df["operation_score"]
        + 0.10 * score_df["stability_score"]
    )
    # Seoul stores get a light external-market adjustment without replacing the global score logic.
    score_df["gromong_score"] = np.where(
        score_df["is_seoul_external"] == 1,
        0.9 * score_df["gromong_score"] + 0.1 * score_df["market_fit_score"],
        score_df["gromong_score"],
    )
    score_df["gromong_score"] = score_df["gromong_score"].clip(0, 100).round(2)
    score_df["grade"] = score_df["gromong_score"].apply(grade)

    score_df["review_count_p75"] = score_df["review_count"].quantile(0.75)
    reason_rows = []
    for _, row in score_df.iterrows():
        reasons = reason_text(row)
        reason_rows.append(
            {
                "platform_shop_id": row["platform_shop_id"],
                "year_month": row["year_month"],
                "reason_1": reasons[0] if len(reasons) > 0 else "",
                "reason_2": reasons[1] if len(reasons) > 1 else "",
                "reason_3": reasons[2] if len(reasons) > 2 else "",
            }
        )
    reasons_df = pd.DataFrame(reason_rows)

    output_cols = [
        "platform_shop_id",
        "year_month",
        "shop_name",
        "brand",
        "category",
        "sido",
        "sigungu",
        "experiment_group",
        "selected_prediction_model",
        "final_growth_probability",
        "probability_score",
        "growth_alpha_score",
        "review_growth_score",
        "operation_score",
        "stability_score",
        "market_fit_score",
        "gromong_score",
        "grade",
        "historical_internal_growth_alpha",
        "historical_review_growth_3m",
        "reply_rate",
        "avg_reply_delay_hours",
        "order_count",
        "sales_amount",
        "review_count",
        "is_seoul_external",
        "market_q4_avg_ticket",
        "store_vs_market_ticket_ratio",
    ]
    score_df[output_cols].sort_values("gromong_score", ascending=False).to_csv(
        OUT_DIR / "store_scores.csv", index=False, encoding="utf-8-sig"
    )

    explanations = score_df[output_cols].merge(reasons_df, on=["platform_shop_id", "year_month"], how="left")
    explanations.sort_values("gromong_score", ascending=False).to_csv(
        OUT_DIR / "store_score_explanations.csv", index=False, encoding="utf-8-sig"
    )

    summary = {
        "latest_month": latest_month,
        "stores": int(score_df["platform_shop_id"].nunique()),
        "avg_score": round(score_df["gromong_score"].mean(), 4),
        "median_score": round(score_df["gromong_score"].median(), 4),
        "top_score": round(score_df["gromong_score"].max(), 4),
        "grade_counts": score_df["grade"].value_counts().to_dict(),
    }
    lines = [
        "# GroMong Score Summary",
        "",
        "## 목적",
        "",
        "모델 성장 확률, 과거 기반 Growth Alpha, 리뷰 텍스트 신호가 반영된 분류 확률, 리뷰 성장, 운영역량, 안정성을 결합해 매장별 0~100점 GroMong Score를 산출했다.",
        "",
        "## 산출 범위",
        "",
        f"- 기준 월: {summary['latest_month']}",
        f"- 점수 산출 매장 수: {summary['stores']}",
        f"- 기본 분류 모델: {selected_model}",
        f"- 평균 점수: {summary['avg_score']}",
        f"- 중앙값 점수: {summary['median_score']}",
        f"- 최고 점수: {summary['top_score']}",
        "",
        "## 등급 분포",
        "",
    ]
    for g in ["A", "B", "C", "D"]:
        lines.append(f"- {g}: {summary['grade_counts'].get(g, 0)}")
    lines.extend(
        [
            "",
            "## 해석",
            "",
            "최종 점수는 단순 매출 규모가 아니라 성장 확률, 브랜드·카테고리 보정 성장 신호, 리뷰 성장, 운영 대응력, 안정성을 결합한 결과다.",
            "",
            "서울 매장은 상권 평균 객단가 자체와 상권 대비 가격 포지션을 분리해 10% 보정 항목으로만 반영했다. store_vs_market_ticket_ratio는 높을수록 좋은 값으로 단정하지 않고 1에 가까운 가격 적합성 신호로 제한 해석한다.",
        ]
    )
    (OUT_DIR / "score_summary.md").write_text("\n".join(lines), encoding="utf-8")

    print(f"WROTE {OUT_DIR}")
    print(summary)


if __name__ == "__main__":
    main()




