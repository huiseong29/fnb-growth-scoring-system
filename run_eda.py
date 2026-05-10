from pathlib import Path

import numpy as np
import pandas as pd


PANEL_PATH = Path("analysis_outputs/store_month_panel.csv")
OUT_DIR = Path("analysis_outputs/eda")
OUT_DIR.mkdir(parents=True, exist_ok=True)


NUMERIC_COLS = [
    "order_count",
    "sales_amount",
    "quantity_sum",
    "store_avg_ticket",
    "review_count",
    "avg_rating",
    "reply_count",
    "reply_rate",
    "avg_reply_delay_hours",
    "menu_count",
    "active_menu_count",
    "avg_delivery_menu_price",
    "avg_pickup_menu_price",
    "trailing_3m_order_avg",
    "future_3m_order_avg",
    "order_growth_3m_forward",
    "sales_growth_3m_forward",
    "review_growth_3m_forward",
    "composite_growth_score",
    "brand_adjusted_growth",
    "category_adjusted_growth",
    "internal_growth_alpha",
    "historical_order_growth_3m",
    "historical_sales_growth_3m",
    "historical_review_growth_3m",
    "historical_composite_growth",
    "historical_brand_adjusted_growth",
    "historical_category_adjusted_growth",
    "historical_internal_growth_alpha",
    "market_q4_sales_amount",
    "market_q4_sales_count",
    "market_q4_avg_ticket",
    "store_vs_market_ticket_ratio",
]


def pct(x):
    return round(float(x) * 100, 2)


def write_csv(df, name):
    path = OUT_DIR / name
    df.to_csv(path, index=False, encoding="utf-8-sig")
    return path


def summarize_by_label(df, cols):
    rows = []
    for label, g in df.groupby("growth_label_top30"):
        for col in cols:
            s = pd.to_numeric(g[col], errors="coerce").dropna()
            rows.append(
                {
                    "growth_label_top30": int(label),
                    "metric": col,
                    "count": int(s.shape[0]),
                    "mean": round(s.mean(), 6) if not s.empty else "",
                    "median": round(s.median(), 6) if not s.empty else "",
                    "std": round(s.std(), 6) if s.shape[0] > 1 else "",
                    "p25": round(s.quantile(0.25), 6) if not s.empty else "",
                    "p75": round(s.quantile(0.75), 6) if not s.empty else "",
                }
            )
    return pd.DataFrame(rows)


def top_bottom_alpha(df):
    latest = df[df["year_month"] == "2025-09"].copy()
    latest = latest[pd.to_numeric(latest["internal_growth_alpha"], errors="coerce").notna()]
    latest["internal_growth_alpha"] = pd.to_numeric(latest["internal_growth_alpha"], errors="coerce")
    cols = [
        "platform_shop_id",
        "shop_name",
        "brand",
        "category",
        "sido",
        "sigungu",
        "order_count",
        "sales_amount",
        "review_count",
        "reply_rate",
        "composite_growth_score",
        "internal_growth_alpha",
        "growth_label_top30",
    ]
    top = latest.sort_values("internal_growth_alpha", ascending=False).head(30)[cols].copy()
    bottom = latest.sort_values("internal_growth_alpha", ascending=True).head(30)[cols].copy()
    top["rank_type"] = "top"
    bottom["rank_type"] = "bottom"
    return pd.concat([top, bottom], ignore_index=True)


def monthly_trend(df):
    rows = []
    for (month, label), g in df.groupby(["year_month", "growth_label_top30"]):
        rows.append(
            {
                "year_month": month,
                "growth_label_top30": int(label),
                "stores": g["platform_shop_id"].nunique(),
                "avg_order_count": pd.to_numeric(g["order_count"], errors="coerce").mean(),
                "avg_sales_amount": pd.to_numeric(g["sales_amount"], errors="coerce").mean(),
                "avg_review_count": pd.to_numeric(g["review_count"], errors="coerce").mean(),
                "avg_reply_rate": pd.to_numeric(g["reply_rate"], errors="coerce").mean(),
                "avg_growth_alpha": pd.to_numeric(g["internal_growth_alpha"], errors="coerce").mean(),
            }
        )
    out = pd.DataFrame(rows)
    for col in out.columns:
        if col.startswith("avg_"):
            out[col] = out[col].round(6)
    return out.sort_values(["year_month", "growth_label_top30"])


def group_label_rate(df, group_cols):
    rows = []
    for keys, g in df.groupby(group_cols):
        if not isinstance(keys, tuple):
            keys = (keys,)
        labels = pd.to_numeric(g["growth_label_top30"], errors="coerce")
        row = {col: key for col, key in zip(group_cols, keys)}
        row.update(
            {
                "rows": int(g.shape[0]),
                "stores": int(g["platform_shop_id"].nunique()),
                "growth_label_1": int((labels == 1).sum()),
                "growth_label_0": int((labels == 0).sum()),
                "growth_rate": round(float((labels == 1).mean()), 6),
                "avg_growth_alpha": round(pd.to_numeric(g["internal_growth_alpha"], errors="coerce").mean(), 6),
                "avg_order_count": round(pd.to_numeric(g["order_count"], errors="coerce").mean(), 6),
                "avg_review_count": round(pd.to_numeric(g["review_count"], errors="coerce").mean(), 6),
            }
        )
        rows.append(row)
    return pd.DataFrame(rows).sort_values("growth_rate", ascending=False)


def correlation_table(df, target="composite_growth_score"):
    cols = [
        "order_count",
        "sales_amount",
        "store_avg_ticket",
        "review_count",
        "avg_rating",
        "reply_rate",
        "avg_reply_delay_hours",
        "menu_count",
        "avg_delivery_menu_price",
        "brand_adjusted_growth",
        "category_adjusted_growth",
        "internal_growth_alpha",
        "historical_composite_growth",
        "historical_internal_growth_alpha",
        "store_vs_market_ticket_ratio",
    ]
    rows = []
    target_s = pd.to_numeric(df[target], errors="coerce")
    for col in cols:
        s = pd.to_numeric(df[col], errors="coerce")
        mask = target_s.notna() & s.notna()
        corr = target_s[mask].corr(s[mask]) if mask.sum() > 2 else np.nan
        rows.append({"metric": col, "valid_pairs": int(mask.sum()), "corr_with_growth_score": round(corr, 6) if pd.notna(corr) else ""})
    return pd.DataFrame(rows).sort_values("corr_with_growth_score", ascending=False)


def write_report(stats):
    lines = [
        "# EDA Summary",
        "",
        "## 프로젝트 관점",
        "",
        "이번 EDA의 목적은 AI 기반 F&B 성장 유망 매장 스코어링 시스템에서 핵심 차별점인 Growth Alpha가 실제로 의미 있는 신호인지 확인하는 것이다.",
        "",
        "Growth Alpha는 단순 주문수나 리뷰수가 아니라 브랜드·카테고리 효과를 보정한 초과 성장 잠재력을 의미한다.",
        "",
        "## 데이터 범위",
        "",
        f"- 전체 패널 행 수: {stats['total_rows']:,}",
        f"- 전체 매장 수: {stats['stores']:,}",
        f"- 분석 월 범위: {stats['min_month']} ~ {stats['max_month']}",
        f"- 라벨 유효 행 수: {stats['valid_rows']:,}",
        f"- 성장 라벨 1 비율: {stats['growth_rate']}%",
        f"- 서울 외부 상권 결합 매장 수: {stats['external_stores']:,}",
        "",
        "## 주요 관찰",
        "",
        f"- 성장 라벨 1 그룹의 평균 Growth Alpha는 {stats['alpha_label1']}, 라벨 0 그룹은 {stats['alpha_label0']}이다.",
        f"- 예측 모델 입력으로 사용할 과거 기반 Growth Alpha는 성장 라벨 1 그룹 평균 {stats['hist_alpha_label1']}, 라벨 0 그룹 평균 {stats['hist_alpha_label0']}이다.",
        f"- 성장 라벨 1 그룹의 평균 월 주문수는 {stats['order_label1']}, 라벨 0 그룹은 {stats['order_label0']}이다.",
        f"- 성장 라벨 1 그룹의 평균 월 리뷰수는 {stats['review_label1']}, 라벨 0 그룹은 {stats['review_label0']}이다.",
        "",
        "## 해석",
        "",
        "이 결과는 성장 유망 매장을 단순 규모가 큰 매장으로만 정의하지 않고, 브랜드·카테고리 평균 대비 초과 성장하는 매장으로 구분할 수 있음을 보여준다.",
        "",
        "`internal_growth_alpha`는 미래 성장률에서 파생된 결과 설명용 변수다. 예측 모델 입력에는 과거 데이터만으로 계산한 `historical_internal_growth_alpha`를 사용해야 한다.",
        "",
        "다음 단계에서는 내부 변수만 사용한 Baseline 모델과 Growth Alpha 변수를 포함한 모델을 비교하여, 이 차별점이 실제 예측 성능 개선으로 이어지는지 검증한다.",
    ]
    (OUT_DIR / "eda_report.md").write_text("\n".join(lines), encoding="utf-8")


def main():
    df = pd.read_csv(PANEL_PATH, encoding="utf-8-sig")
    for col in NUMERIC_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    valid = df[df["is_label_valid"] == 1].copy()
    valid["growth_label_top30"] = pd.to_numeric(valid["growth_label_top30"], errors="coerce").astype(int)

    label_summary = summarize_by_label(
        valid,
        [
            "order_count",
            "sales_amount",
            "store_avg_ticket",
            "review_count",
            "avg_rating",
            "reply_rate",
            "avg_reply_delay_hours",
            "menu_count",
            "avg_delivery_menu_price",
            "composite_growth_score",
            "internal_growth_alpha",
            "historical_composite_growth",
            "historical_internal_growth_alpha",
        ],
    )
    write_csv(label_summary, "eda_label_summary.csv")

    write_csv(group_label_rate(valid, ["brand"]), "eda_brand_summary.csv")
    write_csv(group_label_rate(valid, ["category"]), "eda_category_summary.csv")
    write_csv(group_label_rate(valid, ["brand", "category"]), "eda_brand_category_summary.csv")
    write_csv(group_label_rate(valid, ["sido"]), "eda_sido_summary.csv")
    write_csv(monthly_trend(valid), "eda_monthly_trend.csv")
    write_csv(correlation_table(valid), "eda_correlations.csv")
    write_csv(top_bottom_alpha(valid), "eda_growth_alpha_top_bottom.csv")

    seoul = valid[valid["market_q4_sales_amount"].notna()].copy()
    if not seoul.empty:
        write_csv(group_label_rate(seoul, ["sigungu", "category"]), "eda_seoul_gu_category_summary.csv")
        seoul_cols = [
            "market_q4_sales_amount",
            "market_q4_sales_count",
            "market_q4_avg_ticket",
            "store_vs_market_ticket_ratio",
            "composite_growth_score",
            "internal_growth_alpha",
            "historical_internal_growth_alpha",
        ]
        write_csv(summarize_by_label(seoul, seoul_cols), "eda_seoul_external_label_summary.csv")

    l0 = valid[valid["growth_label_top30"] == 0]
    l1 = valid[valid["growth_label_top30"] == 1]
    stats = {
        "total_rows": df.shape[0],
        "stores": df["platform_shop_id"].nunique(),
        "min_month": df["year_month"].min(),
        "max_month": df["year_month"].max(),
        "valid_rows": valid.shape[0],
        "growth_rate": pct(valid["growth_label_top30"].mean()),
        "external_stores": df[df["market_q4_sales_amount"].notna()]["platform_shop_id"].nunique(),
        "alpha_label1": round(l1["internal_growth_alpha"].mean(), 4),
        "alpha_label0": round(l0["internal_growth_alpha"].mean(), 4),
        "hist_alpha_label1": round(l1["historical_internal_growth_alpha"].mean(), 4),
        "hist_alpha_label0": round(l0["historical_internal_growth_alpha"].mean(), 4),
        "order_label1": round(l1["order_count"].mean(), 2),
        "order_label0": round(l0["order_count"].mean(), 2),
        "review_label1": round(l1["review_count"].mean(), 2),
        "review_label0": round(l0["review_count"].mean(), 2),
    }
    write_report(stats)

    print("EDA complete")
    print(f"valid_rows={valid.shape[0]}")
    print(f"growth_rate={stats['growth_rate']}%")
    print(f"alpha_label1={stats['alpha_label1']} alpha_label0={stats['alpha_label0']}")
    print(f"output_dir={OUT_DIR}")


if __name__ == "__main__":
    main()
