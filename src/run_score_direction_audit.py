from pathlib import Path

import numpy as np
import pandas as pd


SCORE_PATH = Path("analysis_outputs/scoring/store_scores.csv")
PANEL_PATH = Path("analysis_outputs/store_month_panel.csv")
CALIBRATION_PATH = Path("analysis_outputs/modeling/calibration_lift_table.csv")
OUT_DIR = Path("analysis_outputs/scoring")
OUT_DIR.mkdir(parents=True, exist_ok=True)

TARGET = "growth_label_top30"
COMPONENTS = [
    "probability_score",
    "growth_alpha_score",
    "review_growth_score",
    "operation_score",
    "stability_score",
    "gromong_score",
]
COMPONENT_LABELS = {
    "probability_score": "모델 성장확률 점수",
    "growth_alpha_score": "Growth Alpha 점수",
    "review_growth_score": "리뷰 성장 점수",
    "operation_score": "운영 대응 점수",
    "stability_score": "안정성 점수",
    "gromong_score": "현재 composite score",
}


def auc_score(y, score):
    y = np.asarray(y).astype(int)
    score = np.asarray(score).astype(float)
    valid = np.isfinite(score)
    y, score = y[valid], score[valid]
    order = np.argsort(score)
    ranks = np.empty_like(order, dtype=float)
    ranks[order] = np.arange(1, len(score) + 1)
    pos = y == 1
    n_pos, n_neg = pos.sum(), len(y) - pos.sum()
    if n_pos == 0 or n_neg == 0:
        return np.nan
    return float((ranks[pos].sum() - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg))


def pr_auc_score(y, score):
    y = np.asarray(y).astype(int)
    score = np.asarray(score).astype(float)
    valid = np.isfinite(score)
    y, score = y[valid], score[valid]
    order = np.argsort(-score)
    y_sorted = y[order]
    positives = y_sorted.sum()
    if positives == 0:
        return np.nan
    tp = np.cumsum(y_sorted)
    precision = tp / (np.arange(len(y_sorted)) + 1)
    return float((precision * y_sorted).sum() / positives)


def pearson_corr(a, b):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    valid = np.isfinite(a) & np.isfinite(b)
    if valid.sum() < 2:
        return np.nan
    a = a[valid] - a[valid].mean()
    b = b[valid] - b[valid].mean()
    denom = np.sqrt((a ** 2).sum() * (b ** 2).sum())
    return float((a * b).sum() / denom) if denom else np.nan


def rank_corr(a, b):
    return pearson_corr(pd.Series(a).rank(), pd.Series(b).rank())


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


def load_scores_with_labels():
    scores = pd.read_csv(SCORE_PATH, encoding="utf-8-sig")
    panel = pd.read_csv(PANEL_PATH, encoding="utf-8-sig")
    label = panel[["platform_shop_id", "year_month", TARGET, "is_label_valid"]].copy()
    label = label[label["is_label_valid"] == 1].drop_duplicates(["platform_shop_id", "year_month"])
    df = scores.merge(label, on=["platform_shop_id", "year_month"], how="left")
    df = df.dropna(subset=[TARGET]).copy()
    df[TARGET] = pd.to_numeric(df[TARGET], errors="coerce").astype(int)
    for col in COMPONENTS + ["final_growth_probability", "market_fit_score"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return add_calibrated_probability(df)


def calibration_map():
    if not CALIBRATION_PATH.exists():
        return {}
    calib = pd.read_csv(CALIBRATION_PATH, encoding="utf-8-sig")
    calib = calib[(calib["model"] == "growth_alpha_nlp") & (calib["split"] == "time")].copy()
    if calib.empty:
        return {}
    return dict(zip(calib["probability_band"].astype(int), calib["actual_growth_rate"].astype(float)))


def add_calibrated_probability(df):
    df = df.copy()
    cmap = calibration_map()
    if cmap:
        bands = max(cmap.keys())
        rank = df["final_growth_probability"].rank(method="first", ascending=False)
        df["probability_band"] = pd.qcut(rank, bands, labels=False, duplicates="drop") + 1
        df["probability_band"] = df["probability_band"].astype(int)
        df["calibrated_probability"] = df["probability_band"].map(cmap)
    else:
        df["probability_band"] = np.nan
        df["calibrated_probability"] = np.nan
    df["calibrated_probability"] = pd.to_numeric(df["calibrated_probability"], errors="coerce").fillna(df["final_growth_probability"]).clip(0, 1)
    df["calibrated_probability_score"] = df["calibrated_probability"] * 100
    return df


def score_band_table(df, component, bands=5):
    temp = df[[TARGET, component]].dropna().copy()
    temp = temp.sort_values(component, ascending=False).reset_index(drop=True)
    temp["score_band"] = pd.qcut(temp.index + 1, bands, labels=False, duplicates="drop") + 1
    rows = []
    for band, g in temp.groupby("score_band", sort=True):
        rows.append({
            "component": component,
            "band": int(band),
            "band_rank_direction": "1=highest_score",
            "rows": int(len(g)),
            "score_min": float(g[component].min()),
            "score_max": float(g[component].max()),
            "score_mean": float(g[component].mean()),
            "actual_growth_rate": float(g[TARGET].mean()),
        })
    return rows


def component_direction_audit(df):
    rows, band_rows = [], []
    y = df[TARGET].to_numpy()
    for component in COMPONENTS:
        score = df[component].to_numpy(dtype=float)
        growth_mean = float(df[df[TARGET] == 1][component].mean())
        non_growth_mean = float(df[df[TARGET] == 0][component].mean())
        row = {
            "component": component,
            "component_label": COMPONENT_LABELS.get(component, component),
            "roc_auc": auc_score(y, score),
            "pr_auc": pr_auc_score(y, score),
            "spearman_correlation": rank_corr(score, y),
            "pearson_correlation": pearson_corr(score, y),
            "growth_mean_score": growth_mean,
            "non_growth_mean_score": non_growth_mean,
            "growth_minus_non_growth": growth_mean - non_growth_mean,
        }
        component_bands = score_band_table(df, component, bands=5)
        for band in component_bands:
            row[f"band{band['band']}_actual_growth_rate"] = band["actual_growth_rate"]
            row[f"band{band['band']}_score_mean"] = band["score_mean"]
        row.update(top_metrics(y, score, ks=(100,)))
        rows.append(row)
        band_rows.extend(component_bands)
    audit = pd.DataFrame(rows)
    bands = pd.DataFrame(band_rows)
    audit.to_csv(OUT_DIR / "component_direction_audit.csv", index=False, encoding="utf-8-sig")
    bands.to_csv(OUT_DIR / "component_score_band_actual_growth_rate.csv", index=False, encoding="utf-8-sig")
    return audit, bands


def inversion_check(df):
    y = df[TARGET].to_numpy()
    rows = []
    for component in COMPONENTS:
        score = df[component].to_numpy(dtype=float)
        inverted = 100 - score
        raw_auc = auc_score(y, score)
        inv_auc = auc_score(y, inverted)
        raw_pr = pr_auc_score(y, score)
        inv_pr = pr_auc_score(y, inverted)
        raw_top = top_metrics(y, score, ks=(100,))
        inv_top = top_metrics(y, inverted, ks=(100,))
        rows.append({
            "component": component,
            "raw_roc_auc": raw_auc,
            "inverted_roc_auc": inv_auc,
            "raw_pr_auc": raw_pr,
            "inverted_pr_auc": inv_pr,
            "raw_top100_lift": raw_top["top100_lift"],
            "inverted_top100_lift": inv_top["top100_lift"],
            "better_direction": "inverted" if inv_auc > raw_auc else "raw",
            "direction_flag": "likely_reversed" if inv_auc > raw_auc and raw_auc < 0.5 else "ok_or_weak",
        })
    out = pd.DataFrame(rows)
    out.to_csv(OUT_DIR / "component_inversion_check.csv", index=False, encoding="utf-8-sig")
    return out

def strategy_scores(df):
    composite = df["gromong_score"].to_numpy(dtype=float)
    calibrated = df["calibrated_probability_score"].to_numpy(dtype=float)
    # Hybrid uses the same predictive order as calibrated probability; composite is an explanation/support column only.
    hybrid = calibrated.copy()
    return {
        "calibrated_probability_ranking": calibrated,
        "current_composite_score_ranking": composite,
        "hybrid_probability_primary_composite_support": hybrid,
    }


def strategy_comparison(df):
    scores = strategy_scores(df)
    y = df[TARGET].to_numpy()
    current_rank = pd.Series(scores["current_composite_score_ranking"]).rank(ascending=False)
    calibrated_rank = pd.Series(scores["calibrated_probability_ranking"]).rank(ascending=False)
    rows = []
    for name, score in scores.items():
        rank = pd.Series(score).rank(ascending=False)
        grades = pd.Series(score if "composite" in name and "hybrid" not in name else df["gromong_score"]).apply(grade).value_counts().to_dict()
        row = {
            "strategy": name,
            "roc_auc": auc_score(y, score),
            "pr_auc": pr_auc_score(y, score),
            "rank_stability_vs_current_composite": pearson_corr(rank, current_rank),
            "rank_stability_vs_calibrated_probability": pearson_corr(rank, calibrated_rank),
            "grade_S": int(grades.get("S", 0)),
            "grade_A": int(grades.get("A", 0)),
            "grade_B": int(grades.get("B", 0)),
            "grade_C": int(grades.get("C", 0)),
            "grade_D": int(grades.get("D", 0)),
        }
        row.update(top_metrics(y, score, ks=(20, 50, 100)))
        if name == "calibrated_probability_ranking":
            row["public_output_fit"] = "best_for_predictive_ranking_but_needs_explanation_index"
        elif name == "current_composite_score_ranking":
            row["public_output_fit"] = "not_recommended_as_predictive_ranking"
        else:
            row["public_output_fit"] = "recommended_probability_primary_composite_explanation_only"
        rows.append(row)
    out = pd.DataFrame(rows)
    out.to_csv(OUT_DIR / "ranking_strategy_comparison.csv", index=False, encoding="utf-8-sig")
    return out


def write_component_report(audit, inversion, bands):
    lines = [
        "# Component Direction Audit",
        "",
        "## 목적",
        "",
        "현재 composite score의 최신월 성장 라벨 기준 성능이 낮게 나왔기 때문에, 가중치 최적화가 아니라 각 component의 방향성이 성장 라벨과 같은 방향인지 점검했다.",
        "",
        "## Component별 방향성 요약",
        "",
        "| component | ROC-AUC | PR-AUC | Spearman | Pearson | Top100 lift | 성장 평균 | 비성장 평균 | 판단 |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    inv_map = inversion.set_index("component").to_dict("index")
    for row in audit.itertuples(index=False):
        inv = inv_map[row.component]
        if inv["direction_flag"] == "likely_reversed":
            judgment = "현재 방향성 반대 가능성 높음"
        elif row.roc_auc < 0.53:
            judgment = "예측 방향성 약함"
        else:
            judgment = "성장 라벨과 같은 방향"
        lines.append(f"| {row.component} | {row.roc_auc:.4f} | {row.pr_auc:.4f} | {row.spearman_correlation:.4f} | {row.pearson_correlation:.4f} | {row.top100_lift:.2f} | {row.growth_mean_score:.2f} | {row.non_growth_mean_score:.2f} | {judgment} |")
    lines.extend([
        "",
        "## Score band별 실제 성장률",
        "",
        "아래 표는 각 component를 높은 점수 순서로 5개 band로 나누었을 때 실제 성장률이다. band 1이 가장 높은 점수 구간이다.",
        "",
        "| component | band | rows | score mean | actual growth rate |",
        "| --- | ---: | ---: | ---: | ---: |",
    ])
    for row in bands.itertuples(index=False):
        lines.append(f"| {row.component} | {row.band} | {row.rows} | {row.score_mean:.2f} | {row.actual_growth_rate:.4f} |")
    lines.extend([
        "",
        "## 결론",
        "",
        "현재 composite score는 최신월 성장 예측 ranking 점수로 쓰기에는 방어력이 약하다. Growth Alpha, 리뷰 성장, 안정성 등 일부 component는 성장 라벨과 반대 방향으로 정렬되어 risk/상태 설명 지표로 분리하는 것이 안전하다.",
    ])
    (OUT_DIR / "component_direction_audit.md").write_text("\n".join(lines), encoding="utf-8")


def write_strategy_summary(comp, audit, inversion):
    comp_map = comp.set_index("strategy").to_dict("index")
    cal = comp_map["calibrated_probability_ranking"]
    cur = comp_map["current_composite_score_ranking"]
    hyb = comp_map["hybrid_probability_primary_composite_support"]
    reversed_components = inversion[inversion["direction_flag"] == "likely_reversed"]["component"].tolist()
    weak_components = audit[audit["roc_auc"] < 0.53]["component"].tolist()
    recommendation = "Option 2"
    lines = [
        "# Ranking Strategy Redefinition Summary",
        "",
        "## 핵심 판단",
        "",
        f"최종 후보군 ranking은 calibrated probability 기반으로 두는 것이 가장 방어 가능하다. 현재 composite score는 predictive ranking score가 아니라 interpretable signal decomposition, 즉 설명용 decision-support index로 재정의한다. 권장안은 {recommendation}이다.",
        "",
        "## Ranking strategy 비교",
        "",
        "| strategy | ROC-AUC | PR-AUC | Top20 hit/lift | Top50 hit/lift | Top100 hit/lift | rank stability vs current | rank stability vs calibrated | public output 적합성 |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in comp.itertuples(index=False):
        lines.append(
            f"| {row.strategy} | {row.roc_auc:.4f} | {row.pr_auc:.4f} | {row.top20_hit_count}/{row.top20_lift:.2f} | {row.top50_hit_count}/{row.top50_lift:.2f} | {row.top100_hit_count}/{row.top100_lift:.2f} | {row.rank_stability_vs_current_composite:.4f} | {row.rank_stability_vs_calibrated_probability:.4f} | {row.public_output_fit} |"
        )
    lines.extend([
        "",
        "## Option별 판단",
        "",
        "| option | 판단 | 장점 | 단점/발표 리스크 |",
        "| --- | --- | --- | --- |",
        "| Option 1. Composite score를 최종 ranking으로 유지 | 비권장 | 설명 가능성이 높고 기존 산출물과 연결이 쉽다 | 최신월 라벨 기준 AUC가 낮고 일부 component 방향성이 반대라 predictive ranking으로 공격받기 쉽다 |",
        "| Option 2. Calibrated probability를 최종 ranking으로 사용, composite는 explanation index | 권장 | predictive ranking과 설명 지수를 분리해 가장 방어 가능하다 | composite score가 최종 순위가 아니라는 점을 명확히 설명해야 한다 |",
        "| Option 3. Composite score를 risk-adjusted decision score로 재정의 | 보류 | 반대 방향 component를 risk signal로 살릴 수 있다 | 새 점수 정의와 검증 시간이 필요해 최종 발표 직전에는 리스크가 크다 |",
        "| Option 4. Probability 중심 operational weighting으로 재설계 | 보류 | 직관적으로 예측 방향성을 회복할 수 있다 | test AUC 사후 튜닝으로 오해받을 위험이 있어 별도 validation 설계가 필요하다 |",
        "",
        "## Component 방향성 판단",
        "",
        f"- 방향성 반대 가능성이 높은 component: {', '.join(reversed_components) if reversed_components else '없음'}",
        f"- 예측 방향성이 약한 component: {', '.join(weak_components) if weak_components else '없음'}",
        "",
        "## Public artifact 수정 판단",
        "",
        "기존 public ranking 파일이 composite score 기준이라면 calibrated_probability 기준으로 바꾸는 것이 낫다. 따라서 `latest_shop_scores_public.csv`와 `store_ranking_topN.csv`를 calibrated_probability 기준으로 새로 저장했다. composite score와 component score는 순위 기준이 아니라 설명/진단 컬럼으로 유지했다.",
        "",
        "## 발표 문구",
        "",
        "최종 후보군의 predictive ranking은 calibrated model probability를 기준으로 두고, GroMong composite score는 성장 확률을 보완 설명하는 interpretable signal decomposition으로 사용했습니다. 민감도와 방향성 audit 결과, composite score 자체를 성장 예측 순위로 쓰기에는 일부 component의 방향성이 약하거나 반대였기 때문에 역할을 재정의했습니다.",
        "",
        "## 낮춰 말해야 할 표현",
        "",
        "- composite score가 성장 예측을 잘한다고 말하지 않는다.",
        "- 현재 score weight가 최적이라고 말하지 않는다.",
        "- 방향성이 반대인 component를 억지로 성장 신호라고 설명하지 않는다. risk 또는 운영 상태 설명 신호로 제한한다.",
    ])
    (OUT_DIR / "ranking_strategy_summary.md").write_text("\n".join(lines), encoding="utf-8")


def decision_band(p):
    if p >= 0.40:
        return "Priority Review"
    if p >= 0.30:
        return "Watch"
    if p >= 0.20:
        return "Monitor"
    return "Low Priority"


def action_band(rank):
    if rank <= 50:
        return "Immediate Review"
    if rank <= 100:
        return "Secondary Review"
    if rank <= 200:
        return "Monitor"
    return "Backlog"


def write_public_outputs(df):
    out = df.copy()
    out["predictive_rank_score"] = out["calibrated_probability"]
    out["model_probability_raw"] = out["final_growth_probability"]
    out["explanation_index"] = out["gromong_score"]
    out["signal_decomposition_index"] = out["gromong_score"].round(2)
    out = out.sort_values(["predictive_rank_score", "model_probability_raw", "explanation_index"], ascending=[False, False, False]).reset_index(drop=True)
    out["predicted_priority_rank"] = np.arange(1, len(out) + 1)
    out["decision_band"] = out["predictive_rank_score"].apply(decision_band)
    out["action_band"] = out["predicted_priority_rank"].apply(action_band)
    signal_cols = ["probability_score", "growth_alpha_score", "review_growth_score", "operation_score", "stability_score", "market_fit_score"]
    signal_names = {
        "probability_score": "model_probability",
        "growth_alpha_score": "growth_alpha",
        "review_growth_score": "review_growth",
        "operation_score": "operation",
        "stability_score": "stability",
        "market_fit_score": "market_fit",
    }
    available = [c for c in signal_cols if c in out.columns]
    out["top_positive_signal"] = out[available].idxmax(axis=1).map(signal_names)
    out["top_negative_signal"] = out[available].idxmin(axis=1).map(signal_names)
    flags = []
    for _, row in out.iterrows():
        row_flags = []
        if row.get("signal_decomposition_index", 50) < 40:
            row_flags.append("low_explanation_index")
        if row.get("growth_alpha_score", 50) < 25:
            row_flags.append("growth_alpha_direction_risk")
        if row.get("stability_score", 50) < 40:
            row_flags.append("stability_risk")
        flags.append(";".join(row_flags) if row_flags else "none")
    out["risk_flag"] = flags
    out["ranking_basis"] = "calibrated_model_probability"
    out["score_role"] = "composite_is_explanation_index_not_predictive_rank"
    public_cols = [
        "predicted_priority_rank", "platform_shop_id", "year_month", "shop_name", "brand", "category", "sido", "sigungu",
        "predictive_rank_score", "decision_band", "explanation_index", "signal_decomposition_index", "action_band", "risk_flag",
        "top_positive_signal", "top_negative_signal", "model_probability_raw", "probability_band", "probability_score", "growth_alpha_score",
        "review_growth_score", "operation_score", "stability_score", "market_fit_score", "ranking_basis", "score_role",
    ]
    safe = out[[c for c in public_cols if c in out.columns]].copy()
    safe.to_csv(OUT_DIR / "latest_shop_scores_public.csv", index=False, encoding="utf-8-sig")
    safe.head(200).to_csv(OUT_DIR / "store_ranking_topN.csv", index=False, encoding="utf-8-sig")

def main():
    df = load_scores_with_labels()
    audit, bands = component_direction_audit(df)
    inversion = inversion_check(df)
    comp = strategy_comparison(df)
    write_component_report(audit, inversion, bands)
    write_strategy_summary(comp, audit, inversion)
    write_public_outputs(df)
    print(audit.to_string(index=False))
    print(comp.to_string(index=False))
    print(f"WROTE {OUT_DIR}")


if __name__ == "__main__":
    main()



