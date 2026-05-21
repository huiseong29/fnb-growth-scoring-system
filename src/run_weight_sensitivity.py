from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


SCORE_PATH = Path("analysis_outputs/scoring/store_scores.csv")
PANEL_PATH = Path("analysis_outputs/store_month_panel.csv")
OUT_DIR = Path("analysis_outputs/scoring")
OUT_DIR.mkdir(parents=True, exist_ok=True)

TARGET = "growth_label_top30"
COMPONENTS = [
    "probability_score",
    "growth_alpha_score",
    "review_growth_score",
    "operation_score",
    "stability_score",
]
SCENARIOS = {
    "current": {
        "probability_score": 0.35,
        "growth_alpha_score": 0.25,
        "review_growth_score": 0.15,
        "operation_score": 0.15,
        "stability_score": 0.10,
    },
    "probability-heavy": {
        "probability_score": 0.50,
        "growth_alpha_score": 0.20,
        "review_growth_score": 0.10,
        "operation_score": 0.10,
        "stability_score": 0.10,
    },
    "growth-heavy": {
        "probability_score": 0.25,
        "growth_alpha_score": 0.40,
        "review_growth_score": 0.15,
        "operation_score": 0.10,
        "stability_score": 0.10,
    },
    "review-heavy": {
        "probability_score": 0.30,
        "growth_alpha_score": 0.20,
        "review_growth_score": 0.30,
        "operation_score": 0.10,
        "stability_score": 0.10,
    },
    "operation-heavy": {
        "probability_score": 0.30,
        "growth_alpha_score": 0.20,
        "review_growth_score": 0.15,
        "operation_score": 0.25,
        "stability_score": 0.10,
    },
    "balanced": {
        "probability_score": 0.30,
        "growth_alpha_score": 0.25,
        "review_growth_score": 0.20,
        "operation_score": 0.15,
        "stability_score": 0.10,
    },
}


def auc_score(y, score):
    y = np.asarray(y).astype(int)
    score = np.asarray(score).astype(float)
    order = np.argsort(score)
    ranks = np.empty_like(order, dtype=float)
    ranks[order] = np.arange(1, len(score) + 1)
    pos = y == 1
    n_pos = pos.sum()
    n_neg = len(y) - n_pos
    if n_pos == 0 or n_neg == 0:
        return np.nan
    return float((ranks[pos].sum() - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg))


def pr_auc_score(y, score):
    y = np.asarray(y).astype(int)
    score = np.asarray(score).astype(float)
    order = np.argsort(-score)
    y_sorted = y[order]
    positives = y_sorted.sum()
    if positives == 0:
        return np.nan
    tp = np.cumsum(y_sorted)
    precision = tp / (np.arange(len(y_sorted)) + 1)
    return float((precision * y_sorted).sum() / positives)


def grade(score):
    if score >= 90:
        return "S"
    if score >= 80:
        return "A"
    if score >= 65:
        return "B"
    if score >= 50:
        return "C"
    return "D"


def top_metrics(y, score, ks=(20, 50, 100)):
    y = np.asarray(y).astype(int)
    score = np.asarray(score).astype(float)
    order = np.argsort(-score)
    base_rate = y.mean() if len(y) else np.nan
    out = {}
    for k in ks:
        idx = order[: min(k, len(order))]
        hits = int(y[idx].sum())
        precision = hits / len(idx) if len(idx) else np.nan
        out[f"top{k}_hit_count"] = hits
        out[f"top{k}_lift"] = precision / base_rate if base_rate and not pd.isna(base_rate) else np.nan
    return out



def pearson_corr(a, b):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    valid = np.isfinite(a) & np.isfinite(b)
    if valid.sum() < 2:
        return np.nan
    a = a[valid] - a[valid].mean()
    b = b[valid] - b[valid].mean()
    denom = np.sqrt((a ** 2).sum() * (b ** 2).sum())
    if denom == 0:
        return np.nan
    return float((a * b).sum() / denom)
def make_score(df, weights):
    score = np.zeros(len(df), dtype=float)
    for col, weight in weights.items():
        score += pd.to_numeric(df[col], errors="coerce").fillna(50).to_numpy() * weight
    if "market_fit_score" in df.columns and "is_seoul_external" in df.columns:
        market = pd.to_numeric(df["market_fit_score"], errors="coerce").fillna(50).to_numpy()
        is_seoul = pd.to_numeric(df["is_seoul_external"], errors="coerce").fillna(0).to_numpy() == 1
        score = np.where(is_seoul, 0.9 * score + 0.1 * market, score)
    return np.clip(score, 0, 100)


def load_analysis_frame():
    scores = pd.read_csv(SCORE_PATH, encoding="utf-8-sig")
    panel = pd.read_csv(PANEL_PATH, encoding="utf-8-sig")
    label = panel[["platform_shop_id", "year_month", TARGET, "is_label_valid"]].copy()
    label = label[label["is_label_valid"] == 1].drop_duplicates(["platform_shop_id", "year_month"])
    df = scores.merge(label, on=["platform_shop_id", "year_month"], how="left")
    missing = [c for c in COMPONENTS + [TARGET] if c not in df.columns]
    if missing:
        raise RuntimeError(f"Missing columns for weight sensitivity: {missing}")
    df = df.dropna(subset=[TARGET]).copy()
    df[TARGET] = pd.to_numeric(df[TARGET], errors="coerce").astype(int)
    return df


def write_plot(result_df):
    plt.rcParams["font.family"] = ["Malgun Gothic", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False
    scenarios = result_df["scenario"].tolist()
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.8))
    colors = ["#4C78A8", "#F58518", "#54A24B", "#E45756", "#72B7B2", "#B279A2"]

    axes[0].bar(scenarios, result_df["roc_auc"], color=colors)
    axes[0].set_title("ROC-AUC 민감도")
    axes[0].set_ylim(max(0, result_df["roc_auc"].min() - 0.03), min(1, result_df["roc_auc"].max() + 0.03))
    axes[0].tick_params(axis="x", rotation=35)
    axes[0].set_ylabel("ROC-AUC")

    axes[1].bar(scenarios, result_df["top100_lift"], color=colors)
    axes[1].set_title("Top100 Lift")
    axes[1].tick_params(axis="x", rotation=35)
    axes[1].set_ylabel("Lift")

    axes[2].bar(scenarios, result_df["top100_overlap_with_current"], color=colors)
    axes[2].set_title("Current 대비 Top100 겹침")
    axes[2].set_ylim(0, 1.02)
    axes[2].tick_params(axis="x", rotation=35)
    axes[2].set_ylabel("Overlap")

    fig.suptitle("GroMong Score 가중치 민감도 분석", fontsize=14, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    fig.savefig(OUT_DIR / "weight_sensitivity_plot.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def write_summary(result_df):
    current = result_df[result_df["scenario"] == "current"].iloc[0]
    best_auc = result_df.sort_values("roc_auc", ascending=False).iloc[0]
    min_rank_corr = result_df[result_df["scenario"] != "current"]["rank_correlation_with_current"].min()
    min_overlap = result_df[result_df["scenario"] != "current"]["top100_overlap_with_current"].min()
    auc_range = result_df["roc_auc"].max() - result_df["roc_auc"].min()

    lines = [
        "# GroMong Score Weight Sensitivity Analysis",
        "",
        "## 목적",
        "",
        "본 분석은 test set에 맞춰 최적 가중치를 찾기 위한 작업이 아니다. 현재 GroMong Score 가중치가 특정 임의 조합에 과도하게 의존하는지 확인하고, model-informed operational weighting이라는 설명을 방어하기 위한 민감도 점검이다.",
        "",
        "## 비교 시나리오",
        "",
        "| scenario | probability | growth alpha | review growth | operation | stability |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for name, weights in SCENARIOS.items():
        lines.append(
            f"| {name} | {weights['probability_score']:.2f} | {weights['growth_alpha_score']:.2f} | {weights['review_growth_score']:.2f} | {weights['operation_score']:.2f} | {weights['stability_score']:.2f} |"
        )

    lines.extend([
        "",
        "## 주요 결과",
        "",
        "| scenario | ROC-AUC | PR-AUC | Brier | Top100 lift | Top100 hits | rank corr vs current | Top100 overlap | 평균 | 표준편차 | 등급 분포(S/A/B/C/D) |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ])
    for r in result_df.itertuples(index=False):
        grade_dist = f"{r.grade_S}/{r.grade_A}/{r.grade_B}/{r.grade_C}/{r.grade_D}"
        lines.append(
            f"| {r.scenario} | {r.roc_auc:.4f} | {r.pr_auc:.4f} | {r.brier_score:.4f} | {r.top100_lift:.2f} | {r.top100_hit_count} | {r.rank_correlation_with_current:.4f} | {r.top100_overlap_with_current:.2f} | {r.score_mean:.2f} | {r.score_std:.2f} | {grade_dist} |"
        )

    lines.extend([
        "",
        "## 해석",
        "",
        f"- Current weighting의 ROC-AUC는 {current.roc_auc:.4f}, PR-AUC는 {current.pr_auc:.4f}, Top100 lift는 {current.top100_lift:.2f}이다. 최신월 성장 라벨 기준으로는 순수 예측 방향성이 강하지 않으므로 성능 개선 주장에는 사용하지 않는다.",
        f"- 가장 높은 ROC-AUC는 {best_auc.scenario}의 {best_auc.roc_auc:.4f}이지만, 이 분석은 best weight를 선정하기 위한 사후 최적화가 아니다.",
        f"- 6개 시나리오 간 ROC-AUC 범위는 {auc_range:.4f}로, 가중치 변경에 따른 성능 차이는 제한적이다.",
        f"- current 대비 비현재 시나리오의 최소 rank correlation은 {min_rank_corr:.4f}, 최소 Top100 overlap은 {min_overlap:.2f}이다. 이는 상위 후보군이 완전히 뒤집히는 구조는 아니라는 근거다.",
        "- current weighting은 확률 모델 신호를 가장 크게 반영하되 Growth Alpha, 리뷰 성장, 운영 대응, 안정성을 함께 반영하는 운영형 가중치다.",
        "- 따라서 결론은 현재 가중치가 가장 우수하다는 뜻이 아니라, 가중치 변경 시 ranking stability를 확인했고 동시에 최신월 라벨과의 약한 정렬 문제를 한계로 드러냈다는 뜻이다.",
        "",
        "## 발표용 문구",
        "",
        "GroMong Score의 가중치는 test AUC를 사후 최적화한 값이 아니라, 성장 확률과 운영 해석 가능성의 균형을 둔 model-informed operational weighting입니다. 민감도 분석은 현재 가중치가 최고 성능이라는 주장이 아니라, 가중치 변화에 따른 ranking stability와 최신월 라벨 기준 한계를 함께 점검한 결과입니다.",
        "",
        "## 한계",
        "",
        "- 동일 기준월 검증 라벨을 사용한 사후 민감도 점검이므로 독립 외부 검증은 아니다.",
        "- 현재 가중치가 AUC 최고라는 주장을 하지 않는다.",
        "- 점수는 투자 후보군 우선순위화를 위한 보조 지표이며, 실제 투자 확정에는 ROI 가정과 현장 판단이 함께 필요하다.",
    ])
    (OUT_DIR / "weight_sensitivity_summary.md").write_text("\n".join(lines), encoding="utf-8")


def main():
    df = load_analysis_frame()
    current_score = make_score(df, SCENARIOS["current"])
    current_top100 = set(df.iloc[np.argsort(-current_score)[: min(100, len(df))]]["platform_shop_id"].astype(str))

    rows = []
    for name, weights in SCENARIOS.items():
        score = make_score(df, weights)
        prob = score / 100
        grades = pd.Series(score).apply(grade).value_counts().to_dict()
        top100 = set(df.iloc[np.argsort(-score)[: min(100, len(df))]]["platform_shop_id"].astype(str))
        rank_corr = pearson_corr(pd.Series(score).rank(ascending=False), pd.Series(current_score).rank(ascending=False))
        row = {
            "scenario": name,
            "w_probability_score": weights["probability_score"],
            "w_growth_alpha_score": weights["growth_alpha_score"],
            "w_review_growth_score": weights["review_growth_score"],
            "w_operation_score": weights["operation_score"],
            "w_stability_score": weights["stability_score"],
            "roc_auc": auc_score(df[TARGET], score),
            "pr_auc": pr_auc_score(df[TARGET], score),
            "brier_score": float(np.mean((prob - df[TARGET].to_numpy()) ** 2)),
            "score_mean": float(np.mean(score)),
            "score_std": float(np.std(score, ddof=1)),
            "rank_correlation_with_current": float(rank_corr),
            "top100_overlap_with_current": len(top100 & current_top100) / len(current_top100) if current_top100 else np.nan,
            "grade_S": int(grades.get("S", 0)),
            "grade_A": int(grades.get("A", 0)),
            "grade_B": int(grades.get("B", 0)),
            "grade_C": int(grades.get("C", 0)),
            "grade_D": int(grades.get("D", 0)),
        }
        row.update(top_metrics(df[TARGET], score))
        rows.append(row)

    result = pd.DataFrame(rows)
    order = list(SCENARIOS.keys())
    result["scenario"] = pd.Categorical(result["scenario"], categories=order, ordered=True)
    result = result.sort_values("scenario").reset_index(drop=True)
    result.to_csv(OUT_DIR / "weight_sensitivity_analysis.csv", index=False, encoding="utf-8-sig")
    write_plot(result)
    write_summary(result)
    print(result[["scenario", "roc_auc", "pr_auc", "brier_score", "top100_lift", "top100_hit_count", "rank_correlation_with_current", "top100_overlap_with_current"]].to_string(index=False))
    print(f"WROTE {OUT_DIR}")


if __name__ == "__main__":
    main()


