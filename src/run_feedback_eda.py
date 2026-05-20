from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


OUT_DIR = Path("analysis_outputs/feedback_eda")
CHART_DIR = OUT_DIR / "charts"
OUT_DIR.mkdir(parents=True, exist_ok=True)
CHART_DIR.mkdir(parents=True, exist_ok=True)

EDA_DIR = Path("analysis_outputs/eda")
NLP_DIR = Path("analysis_outputs/nlp")
MODEL_DIR = Path("analysis_outputs/modeling")
ROI_DIR = Path("analysis_outputs/roi")
SCORING_DIR = Path("analysis_outputs/scoring")

plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["svg.fonttype"] = "none"
plt.rcParams["figure.dpi"] = 120
plt.rcParams["savefig.dpi"] = 120

PALETTES = {
    "blue": ["#4E79A7", "#A0CBE8", "#F28E2B", "#E15759"],
    "green": ["#59A14F", "#8CD17D", "#B6992D", "#F1CE63"],
    "purple": ["#79706E", "#BAB0AC", "#B07AA1", "#D4A6C8"],
    "brown": ["#9C755F", "#D7B5A6", "#EDC948", "#F2CF5B"],
    "teal": ["#499894", "#86BCB6", "#E15759", "#FF9D9A"],
}

LABELS = {
    "order_count": "주문수",
    "sales_amount": "매출",
    "review_count": "리뷰수",
    "reply_rate": "답글률",
    "avg_reply_delay_hours": "응답 지연",
    "internal_growth_alpha": "성장 알파",
    "historical_internal_growth_alpha": "과거 알파",
    "avg_text_sentiment": "텍스트 감성",
    "positive_text_rate": "긍정 리뷰율",
    "negative_text_rate": "부정 리뷰율",
    "delivery_rate": "배달 언급률",
    "reorder_rate": "재주문 언급률",
    "market_q4_avg_ticket": "상권 객단가",
    "store_vs_market_ticket_ratio": "매장/상권 객단가",
    "baseline": "기본 모델",
    "growth_alpha": "성장 알파",
    "growth_alpha_nlp": "알파+텍스트",
}


def safe_read(path):
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path, encoding="utf-8-sig")


def write_csv(df, name):
    df.to_csv(OUT_DIR / name, index=False, encoding="utf-8-sig")


def fmt(v, digits=4):
    if pd.isna(v):
        return ""
    return round(float(v), digits)


def k(label):
    return LABELS.get(str(label), str(label))


def save(fig, name):
    fig.tight_layout()
    fig.savefig(CHART_DIR / name, format="svg", bbox_inches="tight")
    plt.close(fig)


def style(ax):
    ax.set_facecolor("white")
    ax.grid(axis="y", color="#DDDDDD", linewidth=0.8, alpha=0.8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#BBBBBB")
    ax.spines["bottom"].set_color("#BBBBBB")
    ax.tick_params(colors="#333333", labelsize=10)
    ax.title.set_fontsize(13)
    ax.title.set_fontweight("bold")


def build_comment_matrix():
    rows = [
        ["모델 선택 근거가 체계적이라는 점은 강점", "기본 모델, 성장 알파 모델, 알파+텍스트 모델을 같은 시간 기준 분할로 비교", "완료"],
        ["리뷰 텍스트에서 더 깊은 정보를 추출할 필요", "감성, 긍정/부정 비율, 재주문 등 리뷰 텍스트 신호를 모델에 통합", "완료"],
        ["외부 상권 변수가 약함", "서울 매장에 상권 매출, 주문수, 객단가, 매장/상권 객단가 비율을 결합", "완료, 확장 필요"],
        ["인과추론보다 분류에 집중할 필요", "인과추론은 평균 효과 근거로 두고 최종 판단은 성장 라벨 분류 중심으로 재정렬", "완료"],
        ["예측과 투자효과가 분리되어 있음", "성장 확률을 기대 추가 주문, 기대 마진, 기대 월간 투자효과로 연결", "완료"],
    ]
    out = pd.DataFrame(rows, columns=["feedback_comment", "reflected_action", "status"])
    write_csv(out, "comment_reflection_matrix.csv")
    return out


def build_label_gap():
    label = safe_read(EDA_DIR / "eda_label_summary.csv")
    rows = []
    for metric in ["order_count", "sales_amount", "review_count", "reply_rate", "avg_reply_delay_hours", "internal_growth_alpha", "historical_internal_growth_alpha"]:
        sub = label[label["metric"] == metric]
        if sub.empty:
            continue
        by = {int(r.growth_label_top30): r for r in sub.itertuples()}
        if 0 not in by or 1 not in by:
            continue
        base, growth = float(by[0].mean), float(by[1].mean)
        std0 = float(by[0].std) if by[0].std != "" else np.nan
        std1 = float(by[1].std) if by[1].std != "" else np.nan
        pooled = np.sqrt((std0**2 + std1**2) / 2) if pd.notna(std0) and pd.notna(std1) else np.nan
        rows.append(
            {
                "metric": metric,
                "non_growth_mean": fmt(base),
                "growth_mean": fmt(growth),
                "absolute_gap": fmt(growth - base),
                "relative_gap_pct": fmt((growth / base - 1) * 100 if base else 0, 2),
                "cohens_d": fmt((growth - base) / pooled if pooled and pooled > 0 else np.nan, 4),
                "non_growth_p75": fmt(by[0].p75),
                "growth_p75": fmt(by[1].p75),
            }
        )
    out = pd.DataFrame(rows)
    write_csv(out, "eda_label_gap_summary.csv")
    return out


def build_nlp_gap():
    nlp = safe_read(NLP_DIR / "review_sentiment_summary.csv")
    rows = []
    for metric in ["avg_text_sentiment", "positive_text_rate", "negative_text_rate", "delivery_rate", "reorder_rate"]:
        values = {int(r.growth_label_top30): float(getattr(r, metric)) for r in nlp.itertuples() if hasattr(r, metric)}
        if 0 not in values or 1 not in values:
            continue
        rows.append(
            {
                "metric": metric,
                "non_growth_mean": fmt(values[0]),
                "growth_mean": fmt(values[1]),
                "absolute_gap": fmt(values[1] - values[0]),
                "relative_gap_pct": fmt((values[1] / values[0] - 1) * 100 if values[0] else 0, 2),
            }
        )
    out = pd.DataFrame(rows)
    write_csv(out, "eda_nlp_gap_summary.csv")
    return out


def build_external_gap():
    external = safe_read(EDA_DIR / "eda_seoul_external_label_summary.csv")
    rows = []
    for metric in ["market_q4_sales_amount", "market_q4_sales_count", "market_q4_avg_ticket", "store_vs_market_ticket_ratio"]:
        sub = external[external["metric"] == metric]
        values = {int(r.growth_label_top30): float(r.mean) for r in sub.itertuples()}
        if 0 not in values or 1 not in values:
            continue
        rows.append(
            {
                "metric": metric,
                "non_growth_mean": fmt(values[0]),
                "growth_mean": fmt(values[1]),
                "absolute_gap": fmt(values[1] - values[0]),
                "relative_gap_pct": fmt((values[1] / values[0] - 1) * 100 if values[0] else 0, 2),
            }
        )
    out = pd.DataFrame(rows)
    write_csv(out, "eda_external_gap_summary.csv")
    return out


def build_model_lift():
    model = safe_read(MODEL_DIR / "model_comparison.csv")
    baseline_auc = float(model.loc[model["model"] == "baseline", "auc"].iloc[0])
    rows = []
    for r in model.itertuples(index=False):
        rows.append({"model": r.model, "auc": fmt(r.auc), "f1": fmt(r.f1), "top100_precision": fmt(getattr(r, "top100_precision", 0)), "auc_lift_vs_baseline": fmt(float(r.auc) - baseline_auc)})
    out = pd.DataFrame(rows)
    write_csv(out, "eda_model_lift_summary.csv")
    return out


def build_model_deciles():
    pred = safe_read(MODEL_DIR / "model_predictions.csv")
    pred = pred[pred["model"] == "growth_alpha_nlp"].copy()
    pred["prob_decile"] = pd.qcut(pred["growth_probability"], 10, labels=False, duplicates="drop") + 1
    pred["prob_decile"] = 11 - pred["prob_decile"]
    out = pred.groupby("prob_decile").agg(rows=("platform_shop_id", "count"), avg_probability=("growth_probability", "mean"), actual_growth_rate=("growth_label_top30", "mean")).reset_index().sort_values("prob_decile")
    out["lift_vs_test_rate"] = out["actual_growth_rate"] / pred["growth_label_top30"].mean()
    out = out.round(4)
    write_csv(out, "eda_model_decile_lift.csv")
    return out


def build_roi_grade():
    roi = safe_read(ROI_DIR / "roi_simulation_by_store.csv")
    base = roi[roi["scenario"] == "base"].copy()
    out = base.groupby("grade").agg(stores=("platform_shop_id", "nunique"), avg_growth_probability=("final_growth_probability", "mean"), avg_expected_roi=("expected_monthly_roi", "mean"), median_expected_roi=("expected_monthly_roi", "median"), positive_roi_stores=("expected_monthly_roi", lambda s: int((s > 0).sum()))).reset_index()
    out["positive_roi_rate"] = out["positive_roi_stores"] / out["stores"]
    out = out.round(4)
    write_csv(out, "eda_roi_by_grade_summary.csv")
    return out


def build_score_deciles():
    scores = safe_read(SCORING_DIR / "store_scores.csv")
    scores["score_decile"] = pd.qcut(scores["gromong_score"], 10, labels=False, duplicates="drop") + 1
    scores["score_decile"] = 11 - scores["score_decile"]
    out = scores.groupby("score_decile").agg(stores=("platform_shop_id", "nunique"), avg_score=("gromong_score", "mean"), avg_probability=("final_growth_probability", "mean"), avg_growth_alpha=("growth_alpha_score", "mean"), seoul_share=("is_seoul_external", "mean")).reset_index().sort_values("score_decile").round(4)
    write_csv(out, "eda_score_decile_profile.csv")
    return out


def plot_label_relative(label_gap):
    data = label_gap[label_gap["metric"].isin(["order_count", "review_count", "reply_rate", "avg_reply_delay_hours"])]
    fig, ax = plt.subplots(figsize=(8, 4.8))
    colors = [PALETTES["blue"][0] if v >= 0 else PALETTES["blue"][3] for v in data["relative_gap_pct"]]
    ax.bar([k(x) for x in data["metric"]], data["relative_gap_pct"], color=colors)
    ax.axhline(0, color="#666666", linewidth=0.8)
    ax.set_title("성장 그룹 핵심 지표 차이")
    ax.set_ylabel("비성장 그룹 대비 차이(%)")
    style(ax)
    save(fig, "label_relative_gap.svg")


def plot_label_means(label_gap):
    data = label_gap[label_gap["metric"].isin(["order_count", "review_count", "reply_rate", "avg_reply_delay_hours"])]
    x = np.arange(len(data))
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    ax.bar(x - 0.18, data["non_growth_mean"], width=0.36, label="비성장", color=PALETTES["green"][0])
    ax.bar(x + 0.18, data["growth_mean"], width=0.36, label="성장", color=PALETTES["green"][1])
    ax.set_xticks(x, [k(v) for v in data["metric"]])
    ax.set_title("성장 라벨별 운영 지표 평균")
    ax.legend(frameon=False)
    style(ax)
    save(fig, "label_mean_comparison.svg")


def plot_effect_size(label_gap):
    data = label_gap.copy().iloc[::-1]
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    colors = [PALETTES["purple"][2] if v >= 0 else PALETTES["purple"][0] for v in data["cohens_d"]]
    ax.barh([k(x) for x in data["metric"]], data["cohens_d"], color=colors)
    ax.axvline(0, color="#666666", linewidth=0.8)
    ax.set_title("지표별 효과크기")
    ax.set_xlabel("효과크기(d)")
    style(ax)
    ax.grid(axis="x", color="#DDDDDD", linewidth=0.8, alpha=0.8)
    ax.grid(axis="y", visible=False)
    save(fig, "effect_size_heatmap.svg")


def plot_nlp_means(nlp_gap):
    data = nlp_gap[nlp_gap["metric"].isin(["avg_text_sentiment", "positive_text_rate", "negative_text_rate", "reorder_rate"])]
    x = np.arange(len(data))
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    ax.bar(x - 0.18, data["non_growth_mean"], width=0.36, label="비성장", color=PALETTES["brown"][0])
    ax.bar(x + 0.18, data["growth_mean"], width=0.36, label="성장", color=PALETTES["brown"][2])
    ax.set_xticks(x, [k(v) for v in data["metric"]])
    ax.set_title("성장 라벨별 리뷰 텍스트 신호")
    ax.legend(frameon=False)
    style(ax)
    save(fig, "nlp_mean_comparison.svg")


def plot_nlp_relative(nlp_gap):
    data = nlp_gap[nlp_gap["metric"].isin(["avg_text_sentiment", "positive_text_rate", "negative_text_rate", "reorder_rate"])]
    fig, ax = plt.subplots(figsize=(8, 4.8))
    colors = [PALETTES["teal"][0] if v >= 0 else PALETTES["teal"][2] for v in data["relative_gap_pct"]]
    ax.bar([k(x) for x in data["metric"]], data["relative_gap_pct"], color=colors)
    ax.axhline(0, color="#666666", linewidth=0.8)
    ax.set_title("리뷰 텍스트 지표 상대 차이")
    ax.set_ylabel("비성장 그룹 대비 차이(%)")
    style(ax)
    save(fig, "nlp_relative_gap.svg")


def plot_external(external_gap):
    data = external_gap[external_gap["metric"].isin(["market_q4_avg_ticket", "store_vs_market_ticket_ratio"])]
    x = np.arange(len(data))
    fig, ax = plt.subplots(figsize=(7.5, 4.6))
    ax.bar(x - 0.18, data["non_growth_mean"], width=0.36, label="비성장", color=PALETTES["blue"][1])
    ax.bar(x + 0.18, data["growth_mean"], width=0.36, label="성장", color=PALETTES["brown"][1])
    ax.set_xticks(x, [k(v) for v in data["metric"]])
    ax.set_title("외부 상권 지표 비교")
    ax.legend(frameon=False)
    style(ax)
    save(fig, "external_market_comparison.svg")


def plot_model_auc(model_lift):
    fig, ax = plt.subplots(figsize=(7.5, 4.6))
    ax.bar([k(x) for x in model_lift["model"]], model_lift["auc"], color=[PALETTES["green"][0], PALETTES["green"][2], PALETTES["green"][1]])
    ax.set_ylim(0.58, 0.625)
    ax.set_title("분류 모델 성능 비교")
    ax.set_ylabel("분류 성능")
    style(ax)
    save(fig, "model_auc_comparison.svg")


def plot_model_decile(model_deciles):
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    ax.bar(model_deciles["prob_decile"].astype(str), model_deciles["actual_growth_rate"] * 100, color=PALETTES["blue"][0])
    ax.set_title("예측 확률 구간별 실제 성장률")
    ax.set_xlabel("예측 확률 구간(1=상위)")
    ax.set_ylabel("실제 성장률(%)")
    style(ax)
    save(fig, "model_decile_lift.svg")


def plot_roi(roi_grade):
    order = ["A", "B", "C", "D"]
    data = roi_grade.set_index("grade").loc[order].reset_index()
    fig, ax = plt.subplots(figsize=(7.5, 4.6))
    ax.bar(["최상위", "상위", "중간", "주의"], data["avg_expected_roi"], color=[PALETTES["green"][0], PALETTES["green"][1], PALETTES["brown"][2], PALETTES["teal"][2]])
    ax.axhline(0, color="#666666", linewidth=0.8)
    ax.set_title("등급별 기대 월간 투자효과")
    ax.set_ylabel("원")
    style(ax)
    save(fig, "roi_by_grade_base.svg")


def plot_score_profile(score_deciles):
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    x = np.arange(len(score_deciles))
    ax.plot(x, score_deciles["avg_probability"], marker="o", label="성장 확률", color=PALETTES["blue"][0])
    ax.plot(x, score_deciles["avg_growth_alpha"] / 100, marker="o", label="알파 점수/100", color=PALETTES["brown"][0])
    ax.plot(x, score_deciles["seoul_share"], marker="o", label="서울 비중", color=PALETTES["green"][0])
    ax.set_xticks(x, score_deciles["score_decile"].astype(str))
    ax.set_xlabel("점수 구간(1=상위)")
    ax.set_title("그로몽 점수 구간별 구성")
    ax.legend(frameon=False)
    style(ax)
    save(fig, "score_decile_profile.svg")


def make_charts(label_gap, nlp_gap, external_gap, model_lift, model_deciles, roi_grade, score_deciles):
    plot_label_relative(label_gap)
    plot_label_means(label_gap)
    plot_effect_size(label_gap)
    plot_nlp_means(nlp_gap)
    plot_nlp_relative(nlp_gap)
    plot_external(external_gap)
    plot_model_auc(model_lift)
    plot_model_decile(model_deciles)
    plot_roi(roi_grade)
    plot_score_profile(score_deciles)


def main():
    build_comment_matrix()
    label_gap = build_label_gap()
    nlp_gap = build_nlp_gap()
    external_gap = build_external_gap()
    model_lift = build_model_lift()
    model_deciles = build_model_deciles()
    roi_grade = build_roi_grade()
    score_deciles = build_score_deciles()
    make_charts(label_gap, nlp_gap, external_gap, model_lift, model_deciles, roi_grade, score_deciles)
    print(f"WROTE {CHART_DIR} with matplotlib")


if __name__ == "__main__":
    main()
