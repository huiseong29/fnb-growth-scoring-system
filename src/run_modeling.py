from pathlib import Path

import numpy as np
import pandas as pd


PANEL_PATH = Path("analysis_outputs/store_month_panel.csv")
NLP_FEATURE_PATH = Path("analysis_outputs/nlp/review_store_month_sentiment.csv")
OUT_DIR = Path("analysis_outputs/modeling")
OUT_DIR.mkdir(parents=True, exist_ok=True)

TARGET = "growth_label_top30"
TIME_COL = "year_month"
TOP_KS = (20, 50, 100, 200)

BASE_NUMERIC = [
    "order_count", "sales_amount", "quantity_sum", "store_avg_ticket", "review_count", "avg_rating",
    "reply_count", "reply_rate", "avg_reply_delay_hours", "menu_count", "active_menu_count",
    "hidden_menu_count", "sold_out_menu_count", "avg_delivery_menu_price", "avg_pickup_menu_price", "is_post_treatment",
]

GROWTH_NUMERIC = [
    "historical_order_growth_3m", "historical_sales_growth_3m", "historical_review_growth_3m",
    "historical_composite_growth", "historical_brand_adjusted_growth", "historical_category_adjusted_growth",
    "historical_internal_growth_alpha",
]

NLP_NUMERIC = [
    "avg_text_sentiment", "text_review_count", "positive_text_rate", "negative_text_rate",
    "taste_rate", "portion_rate", "delivery_rate", "price_rate", "service_rate", "reorder_rate",
    "review_length", "token_count", "exclamation_count", "question_count", "positive_hit_count",
    "negative_hit_count", "sentiment_abs", "mixed_sentiment_flag", "has_reply", "reply_length",
    "reply_token_count", "reply_contains_coupon", "reply_coupon_flag", "reply_template_score", "reply_ai_like_score",
]

CATEGORICAL = ["brand", "category", "sido", "experiment_group", "promo_phrase_enabled", "persona_tone_enabled"]
REPLY_RELATED_NUMERIC = ["reply_count", "reply_rate", "avg_reply_delay_hours", "has_reply", "reply_length", "reply_token_count", "reply_contains_coupon", "reply_coupon_flag", "reply_template_score", "reply_ai_like_score"]
TREATMENT_PROXY_NUMERIC = ["is_post_treatment"]
TREATMENT_PROXY_CATEGORICAL = ["experiment_group", "promo_phrase_enabled", "persona_tone_enabled"]


def add_optional_nlp_features(df):
    if not NLP_FEATURE_PATH.exists():
        return df, []
    nlp = pd.read_csv(NLP_FEATURE_PATH, encoding="utf-8-sig")
    keep = ["platform_shop_id", "year_month"] + [c for c in NLP_NUMERIC if c in nlp.columns]
    nlp = nlp[keep].drop_duplicates(["platform_shop_id", "year_month"])
    merged = df.merge(nlp, on=["platform_shop_id", "year_month"], how="left")
    available = [c for c in NLP_NUMERIC if c in merged.columns]
    return merged, available


def existing(cols, df):
    return [c for c in cols if c in df.columns]


def sigmoid(z):
    z = np.clip(z, -30, 30)
    return 1 / (1 + np.exp(-z))


def fit_preprocess(train, test, numeric_cols, categorical_cols):
    train_parts, test_parts, names = [], [], []
    for col in numeric_cols:
        tr = pd.to_numeric(train[col], errors="coerce") if col in train.columns else pd.Series(np.nan, index=train.index)
        te = pd.to_numeric(test[col], errors="coerce") if col in test.columns else pd.Series(np.nan, index=test.index)
        median = tr.median()
        if pd.isna(median):
            median = 0.0
        tr, te = tr.fillna(median).astype(float), te.fillna(median).astype(float)
        mean, std = tr.mean(), tr.std()
        if pd.isna(std) or std == 0:
            std = 1.0
        train_parts.append(((tr - mean) / std).to_numpy().reshape(-1, 1))
        test_parts.append(((te - mean) / std).to_numpy().reshape(-1, 1))
        names.append(col)

    for col in categorical_cols:
        if col not in train.columns:
            continue
        tr = train[col].fillna("__MISSING__").astype(str)
        te = test[col].fillna("__MISSING__").astype(str) if col in test.columns else pd.Series("__MISSING__", index=test.index)
        for level in sorted(tr.unique().tolist()):
            train_parts.append((tr == level).astype(float).to_numpy().reshape(-1, 1))
            test_parts.append((te == level).astype(float).to_numpy().reshape(-1, 1))
            names.append(f"{col}={level}")

    x_train = np.hstack(train_parts) if train_parts else np.empty((len(train), 0))
    x_test = np.hstack(test_parts) if test_parts else np.empty((len(test), 0))
    x_train = np.hstack([np.ones((x_train.shape[0], 1)), x_train])
    x_test = np.hstack([np.ones((x_test.shape[0], 1)), x_test])
    return x_train, x_test, ["intercept"] + names


def train_logistic(x, y, lr=0.05, epochs=2500, l2=0.01):
    w = np.zeros(x.shape[1])
    n = x.shape[0]
    for _ in range(epochs):
        p = sigmoid(x @ w)
        grad = (x.T @ (p - y)) / n
        grad[1:] += l2 * w[1:] / n
        w -= lr * grad
    return w


def auc_score(y, score):
    y = np.asarray(y)
    score = np.asarray(score)
    order = np.argsort(score)
    ranks = np.empty_like(order, dtype=float)
    ranks[order] = np.arange(1, len(score) + 1)
    pos = y == 1
    n_pos, n_neg = pos.sum(), len(y) - pos.sum()
    if n_pos == 0 or n_neg == 0:
        return np.nan
    return (ranks[pos].sum() - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg)


def pr_auc_score(y, score):
    y = np.asarray(y).astype(int)
    score = np.asarray(score)
    order = np.argsort(-score)
    y_sorted = y[order]
    positives = y_sorted.sum()
    if positives == 0:
        return np.nan
    tp = np.cumsum(y_sorted)
    precision = tp / (np.arange(len(y_sorted)) + 1)
    return float((precision * y_sorted).sum() / positives)


def binary_metrics(y, prob, threshold=0.5):
    pred = (prob >= threshold).astype(int)
    tp = int(((pred == 1) & (y == 1)).sum())
    fp = int(((pred == 1) & (y == 0)).sum())
    tn = int(((pred == 0) & (y == 0)).sum())
    fn = int(((pred == 0) & (y == 1)).sum())
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    accuracy = (tp + tn) / len(y) if len(y) else 0.0
    return {"threshold": threshold, "accuracy": accuracy, "precision": precision, "recall": recall, "f1": f1, "tp": tp, "fp": fp, "tn": tn, "fn": fn}


def top_n_metrics(y, prob, ns=TOP_KS):
    rows = []
    y = np.asarray(y).astype(int)
    prob = np.asarray(prob)
    base_rate = y.mean() if len(y) else 0
    total_pos = y.sum()
    order = np.argsort(-prob)
    for n in ns:
        idx = order[: min(n, len(order))]
        hits = int(y[idx].sum())
        precision = float(y[idx].mean()) if len(idx) else 0.0
        recall = float(hits / total_pos) if total_pos else 0.0
        rows.append({"top_n": len(idx), "hits": hits, "precision_at_n": precision, "recall_at_n": recall, "lift_at_n": precision / base_rate if base_rate else np.nan})
    return rows


def validation_audit_row(model, split_name, y, prob, threshold, base_metrics):
    out = {
        "model": model,
        "split": split_name,
        "rows": len(y),
        "positive_rate": float(np.mean(y)) if len(y) else np.nan,
        "auc": auc_score(y, prob),
        "pr_auc": pr_auc_score(y, prob),
        "brier_score": float(np.mean((prob - y) ** 2)) if len(y) else np.nan,
        "threshold": threshold,
        "precision": base_metrics["precision"],
        "recall": base_metrics["recall"],
        "f1": base_metrics["f1"],
        "accuracy": base_metrics["accuracy"],
    }
    for row in top_n_metrics(y, prob):
        k = int(row["top_n"])
        out[f"top{k}_hits"] = row["hits"]
        out[f"precision_at_{k}"] = row["precision_at_n"]
        out[f"recall_at_{k}"] = row["recall_at_n"]
        out[f"lift_at_{k}"] = row["lift_at_n"]
    return out


def calibration_table(model, split_name, y, prob, bands=10):
    df = pd.DataFrame({"actual": np.asarray(y).astype(int), "prob": np.asarray(prob)})
    df = df.sort_values("prob", ascending=False).reset_index(drop=True)
    df["band"] = pd.qcut(df.index + 1, bands, labels=False, duplicates="drop") + 1
    total_pos = df["actual"].sum()
    rows = []
    cumulative_hits = 0
    for band, g in df.groupby("band", sort=True):
        hits = int(g["actual"].sum())
        cumulative_hits += hits
        avg_prob = float(g["prob"].mean())
        actual_rate = float(g["actual"].mean())
        rows.append({
            "model": model,
            "split": split_name,
            "probability_band": int(band),
            "rows": int(len(g)),
            "avg_predicted_probability": avg_prob,
            "actual_growth_rate": actual_rate,
            "calibration_gap": actual_rate - avg_prob,
            "hits": hits,
            "cumulative_hits": cumulative_hits,
            "cumulative_capture_rate": cumulative_hits / total_pos if total_pos else np.nan,
        })
    return pd.DataFrame(rows)


def evaluate_model(name, train, test, numeric_cols, categorical_cols, split_name="time"):
    numeric_cols = existing(numeric_cols, train)
    categorical_cols = existing(categorical_cols, train)
    x_train, x_test, feature_names = fit_preprocess(train, test, numeric_cols, categorical_cols)
    y_train = train[TARGET].astype(int).to_numpy()
    y_test = test[TARGET].astype(int).to_numpy()
    w = train_logistic(x_train, y_train)
    train_prob = sigmoid(x_train @ w)
    test_prob = sigmoid(x_test @ w)
    train_positive_rate = y_train.mean()
    threshold = float(np.quantile(train_prob, 1 - train_positive_rate))
    threshold_metrics = binary_metrics(y_test, test_prob, threshold)
    default_metrics = binary_metrics(y_test, test_prob, 0.5)
    top_rows = top_n_metrics(y_test, test_prob)

    metrics = {
        "model": name, "train_rows": len(train), "test_rows": len(test), "features": len(feature_names),
        "train_positive_rate": train_positive_rate, "test_positive_rate": y_test.mean(), "auc": auc_score(y_test, test_prob),
        "pr_auc": pr_auc_score(y_test, test_prob), "brier_score": float(np.mean((test_prob - y_test) ** 2)),
        "threshold_train_rate": threshold, "precision": threshold_metrics["precision"], "recall": threshold_metrics["recall"],
        "f1": threshold_metrics["f1"], "accuracy": threshold_metrics["accuracy"], "precision_05": default_metrics["precision"],
        "recall_05": default_metrics["recall"], "f1_05": default_metrics["f1"],
    }

    pred_cols = ["platform_shop_id", "year_month", "shop_name", "brand", "category", "sido", "sigungu", TARGET, "composite_growth_score", "historical_internal_growth_alpha"]
    pred = test[[c for c in pred_cols if c in test.columns]].copy()
    pred["model"] = name
    pred["growth_probability"] = test_prob
    pred["predicted_label"] = (test_prob >= threshold).astype(int)

    coef = pd.DataFrame({"model": name, "feature": feature_names, "coefficient": w, "abs_coefficient": np.abs(w)}).sort_values("abs_coefficient", ascending=False)
    top = pd.DataFrame(top_rows)
    top.insert(0, "model", name)
    audit = validation_audit_row(name, split_name, y_test, test_prob, threshold, threshold_metrics)
    calib = calibration_table(name, split_name, y_test, test_prob)
    return metrics, pred, coef, top, audit, calib


def model_specs(nlp_cols):
    full = BASE_NUMERIC + GROWTH_NUMERIC + nlp_cols
    no_text_count = [c for c in nlp_cols if c != "text_review_count"]
    no_reply = [c for c in full if c not in REPLY_RELATED_NUMERIC]
    no_treatment_num = [c for c in full if c not in TREATMENT_PROXY_NUMERIC]
    return [
        ("baseline", BASE_NUMERIC, CATEGORICAL),
        ("growth_alpha", BASE_NUMERIC + GROWTH_NUMERIC, CATEGORICAL),
        ("growth_alpha_nlp", full, CATEGORICAL),
        ("growth_alpha_nlp_without_text_count", BASE_NUMERIC + GROWTH_NUMERIC + no_text_count, CATEGORICAL),
        ("growth_alpha_nlp_no_reply_related", no_reply, CATEGORICAL),
        ("growth_alpha_nlp_no_treatment_proxy", no_treatment_num, [c for c in CATEGORICAL if c not in TREATMENT_PROXY_CATEGORICAL]),
    ]


def group_split(df):
    shops = sorted(df["platform_shop_id"].dropna().astype(str).unique().tolist())
    test_shops = set([s for i, s in enumerate(shops) if i % 5 == 0])
    train = df[~df["platform_shop_id"].astype(str).isin(test_shops)].copy()
    test = df[df["platform_shop_id"].astype(str).isin(test_shops)].copy()
    return train, test


def write_report(metrics_df):
    lines = [
        "# Modeling Summary", "", "## 목적", "",
        "성장 유망 매장 분류 모델을 시간 기준 검증, store-level holdout, TopK/lift/calibration 관점에서 보완 검증했다.", "",
        "## 주요 결과", "",
    ]
    for r in metrics_df[metrics_df["model"].isin(["baseline", "growth_alpha", "growth_alpha_nlp", "growth_alpha_nlp_without_text_count"])].itertuples(index=False):
        lines.append(f"- {r.model}: AUC {r.auc:.4f}, PR-AUC {r.pr_auc:.4f}, Brier {r.brier_score:.4f}, F1 {r.f1:.4f}")
    lines.extend(["", "## 해석", "", "성능 개선폭은 크지 않으므로 정확한 예측 모델이 아니라 후보군 우선순위화와 피드백 반영 검증으로 해석한다."])
    (OUT_DIR / "modeling_report.md").write_text("\n".join(lines), encoding="utf-8")


def write_treatment_ablation_report(metrics_df):
    keep = metrics_df[metrics_df["model"].isin(["growth_alpha_nlp", "growth_alpha_nlp_no_reply_related", "growth_alpha_nlp_no_treatment_proxy"])]
    lines = [
        "# Treatment Proxy Ablation Report", "", "## 목적", "",
        "답글 관련 feature와 실험/마케팅 상호작용 proxy가 분류 성능에 과도하게 기여하는지 점검했다.", "",
        "## 결과", "",
        "| 모델 | AUC | PR-AUC | Brier | F1 | 해석 |", "| --- | ---: | ---: | ---: | ---: | --- |",
    ]
    full_auc = float(keep[keep["model"] == "growth_alpha_nlp"]["auc"].iloc[0]) if not keep[keep["model"] == "growth_alpha_nlp"].empty else np.nan
    for r in keep.itertuples(index=False):
        delta = r.auc - full_auc if pd.notna(full_auc) else np.nan
        if r.model == "growth_alpha_nlp":
            note = "전체 텍스트/운영 proxy 포함 기준 모델"
        elif "no_reply" in r.model:
            note = f"답글 관련 proxy 제거, AUC 변화 {delta:+.4f}"
        else:
            note = f"실험/마케팅 proxy 제거, AUC 변화 {delta:+.4f}"
        lines.append(f"| {r.model} | {r.auc:.4f} | {r.pr_auc:.4f} | {r.brier_score:.4f} | {r.f1:.4f} | {note} |")
    lines.extend(["", "## 결론", "", "이 결과는 인과효과 검증이 아니라 treatment proxy contamination 가능성을 점검하기 위한 ablation이다. ATT는 예측 점수에 직접 투입하지 않고 ROI reference layer에만 유지한다."])
    (OUT_DIR / "treatment_proxy_ablation_report.md").write_text("\n".join(lines), encoding="utf-8")


def main():
    df = pd.read_csv(PANEL_PATH, encoding="utf-8-sig")
    df, nlp_cols = add_optional_nlp_features(df)
    df = df[df["is_label_valid"] == 1].copy()
    df[TARGET] = pd.to_numeric(df[TARGET], errors="coerce").astype(int)

    train = df[(df[TIME_COL] >= "2025-01") & (df[TIME_COL] <= "2025-07")].copy()
    test = df[(df[TIME_COL] >= "2025-08") & (df[TIME_COL] <= "2025-09")].copy()

    results, preds, coefs, tops, audits, calibs = [], [], [], [], [], []
    for name, numeric_cols, categorical_cols in model_specs(nlp_cols):
        metrics, pred, coef, top, audit, calib = evaluate_model(name, train, test, numeric_cols, categorical_cols, "time")
        top100 = top[top["top_n"] == min(100, len(test))]
        metrics["top100_precision"] = float(top100["precision_at_n"].iloc[0]) if not top100.empty else np.nan
        results.append(metrics); preds.append(pred); coefs.append(coef); tops.append(top); audits.append(audit); calibs.append(calib)

    metrics_df = pd.DataFrame(results)
    metrics_df.to_csv(OUT_DIR / "model_comparison.csv", index=False, encoding="utf-8-sig")
    pd.concat(preds, ignore_index=True).to_csv(OUT_DIR / "model_predictions.csv", index=False, encoding="utf-8-sig")
    pd.concat(coefs, ignore_index=True).to_csv(OUT_DIR / "model_coefficients.csv", index=False, encoding="utf-8-sig")
    pd.concat(tops, ignore_index=True).to_csv(OUT_DIR / "model_topn_metrics.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(audits).to_csv(OUT_DIR / "model_validation_audit.csv", index=False, encoding="utf-8-sig")
    pd.concat(calibs, ignore_index=True).to_csv(OUT_DIR / "calibration_lift_table.csv", index=False, encoding="utf-8-sig")

    g_train, g_test = group_split(df)
    group_rows = []
    for name, numeric_cols, categorical_cols in model_specs(nlp_cols):
        metrics, _, _, _, audit, _ = evaluate_model(name, g_train, g_test, numeric_cols, categorical_cols, "store_group_holdout")
        group_rows.append({**audit, "train_rows": len(g_train), "test_rows": len(g_test), "features": metrics["features"]})
    pd.DataFrame(group_rows).to_csv(OUT_DIR / "group_holdout_metrics.csv", index=False, encoding="utf-8-sig")

    write_report(metrics_df)
    write_treatment_ablation_report(metrics_df)
    print(metrics_df.to_string(index=False))
    print(f"WROTE {OUT_DIR}")


if __name__ == "__main__":
    main()

