from pathlib import Path

import numpy as np
import pandas as pd


PANEL_PATH = Path("analysis_outputs/store_month_panel.csv")
OUT_DIR = Path("analysis_outputs/modeling")
OUT_DIR.mkdir(parents=True, exist_ok=True)

TARGET = "growth_label_top30"
TIME_COL = "year_month"

BASE_NUMERIC = [
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
    "hidden_menu_count",
    "sold_out_menu_count",
    "avg_delivery_menu_price",
    "avg_pickup_menu_price",
    "is_post_treatment",
]

GROWTH_NUMERIC = [
    "historical_order_growth_3m",
    "historical_sales_growth_3m",
    "historical_review_growth_3m",
    "historical_composite_growth",
    "historical_brand_adjusted_growth",
    "historical_category_adjusted_growth",
    "historical_internal_growth_alpha",
]

CATEGORICAL = [
    "brand",
    "category",
    "sido",
    "experiment_group",
    "promo_phrase_enabled",
    "persona_tone_enabled",
]


def sigmoid(z):
    z = np.clip(z, -30, 30)
    return 1 / (1 + np.exp(-z))


def fit_preprocess(train, test, numeric_cols, categorical_cols):
    train_parts = []
    test_parts = []
    names = []

    for col in numeric_cols:
        tr = pd.to_numeric(train[col], errors="coerce")
        te = pd.to_numeric(test[col], errors="coerce")
        median = tr.median()
        if pd.isna(median):
            median = 0.0
        tr = tr.fillna(median).astype(float)
        te = te.fillna(median).astype(float)
        mean = tr.mean()
        std = tr.std()
        if pd.isna(std) or std == 0:
            std = 1.0
        train_parts.append(((tr - mean) / std).to_numpy().reshape(-1, 1))
        test_parts.append(((te - mean) / std).to_numpy().reshape(-1, 1))
        names.append(col)

    for col in categorical_cols:
        tr = train[col].fillna("__MISSING__").astype(str)
        te = test[col].fillna("__MISSING__").astype(str)
        levels = sorted(tr.unique().tolist())
        for level in levels:
            train_parts.append((tr == level).astype(float).to_numpy().reshape(-1, 1))
            test_parts.append((te == level).astype(float).to_numpy().reshape(-1, 1))
            names.append(f"{col}={level}")

    x_train = np.hstack(train_parts) if train_parts else np.empty((len(train), 0))
    x_test = np.hstack(test_parts) if test_parts else np.empty((len(test), 0))
    x_train = np.hstack([np.ones((x_train.shape[0], 1)), x_train])
    x_test = np.hstack([np.ones((x_test.shape[0], 1)), x_test])
    names = ["intercept"] + names
    return x_train, x_test, names


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
    order = np.argsort(score)
    ranks = np.empty_like(order, dtype=float)
    ranks[order] = np.arange(1, len(score) + 1)
    pos = y == 1
    n_pos = pos.sum()
    n_neg = len(y) - n_pos
    if n_pos == 0 or n_neg == 0:
        return np.nan
    return (ranks[pos].sum() - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg)


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
    return {
        "threshold": threshold,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
    }


def top_n_metrics(y, prob, ns=(50, 100, 200)):
    rows = []
    order = np.argsort(-prob)
    for n in ns:
        idx = order[: min(n, len(order))]
        rows.append(
            {
                "top_n": len(idx),
                "hits": int(y[idx].sum()),
                "precision_at_n": float(y[idx].mean()) if len(idx) else 0.0,
                "capture_rate": float(y[idx].sum() / y.sum()) if y.sum() else 0.0,
            }
        )
    return rows


def evaluate_model(name, train, test, numeric_cols, categorical_cols):
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
        "model": name,
        "train_rows": len(train),
        "test_rows": len(test),
        "features": len(feature_names),
        "train_positive_rate": train_positive_rate,
        "test_positive_rate": y_test.mean(),
        "auc": auc_score(y_test, test_prob),
        "threshold_train_rate": threshold,
        "precision": threshold_metrics["precision"],
        "recall": threshold_metrics["recall"],
        "f1": threshold_metrics["f1"],
        "accuracy": threshold_metrics["accuracy"],
        "precision_05": default_metrics["precision"],
        "recall_05": default_metrics["recall"],
        "f1_05": default_metrics["f1"],
    }

    pred = test[
        [
            "platform_shop_id",
            "year_month",
            "shop_name",
            "brand",
            "category",
            "sido",
            "sigungu",
            TARGET,
            "composite_growth_score",
            "historical_internal_growth_alpha",
        ]
    ].copy()
    pred["model"] = name
    pred["growth_probability"] = test_prob
    pred["predicted_label"] = (test_prob >= threshold).astype(int)

    coef = pd.DataFrame(
        {
            "model": name,
            "feature": feature_names,
            "coefficient": w,
            "abs_coefficient": np.abs(w),
        }
    ).sort_values("abs_coefficient", ascending=False)

    top = pd.DataFrame(top_rows)
    top.insert(0, "model", name)
    return metrics, pred, coef, top


def write_report(metrics_df):
    best = metrics_df.sort_values("auc", ascending=False).iloc[0]
    baseline = metrics_df[metrics_df["model"] == "baseline"].iloc[0]
    growth = metrics_df[metrics_df["model"] == "growth_alpha"].iloc[0]
    lines = [
        "# Modeling Summary",
        "",
        "## 목적",
        "",
        "이번 모델링의 목적은 내부 변수만 사용한 Baseline 모델과 과거 기반 Growth Alpha 변수를 추가한 모델을 비교하는 것이다.",
        "",
        "프로젝트 차별점은 단순 인기 매장 예측이 아니라 브랜드·카테고리 효과를 보정한 초과 성장 잠재력을 활용하는 데 있다.",
        "",
        "## 데이터 분할",
        "",
        "- 학습 기간: 2025-01 ~ 2025-07",
        "- 검증 기간: 2025-08 ~ 2025-09",
        "- 목표 변수: `growth_label_top30`",
        "- 주의: 미래 성장률에서 파생된 `internal_growth_alpha`는 입력 변수에서 제외했다.",
        "- Growth Alpha 모델에는 과거 데이터 기반 `historical_internal_growth_alpha`를 사용했다.",
        "",
        "## 주요 결과",
        "",
        f"- Baseline AUC: {baseline['auc']:.4f}",
        f"- Growth Alpha AUC: {growth['auc']:.4f}",
        f"- Baseline F1: {baseline['f1']:.4f}",
        f"- Growth Alpha F1: {growth['f1']:.4f}",
        f"- 더 높은 AUC 모델: {best['model']}",
        "",
        "## 해석",
        "",
    ]
    if growth["auc"] > baseline["auc"]:
        lines.append("과거 기반 Growth Alpha 변수를 추가했을 때 AUC가 개선되었다. 이는 브랜드·카테고리 보정 성장 신호가 성장 유망 매장 예측에 일부 기여한다는 근거로 사용할 수 있다.")
    else:
        lines.append("과거 기반 Growth Alpha 변수를 추가했을 때 AUC 개선은 확인되지 않았다. 이 경우 Growth Alpha는 예측 입력보다는 결과 해석과 스코어 설명 요소로 활용하고, 모델 성능은 주문·리뷰·운영 변수 중심으로 설명하는 편이 타당하다.")
    lines.extend(
        [
            "",
            "## 다음 작업",
            "",
            "서울 매장 211개 subset에서 외부 상권 변수 추가 전후 성능을 비교한다. 이 단계가 외부 데이터의 실질적 기여도를 검증하는 핵심이다.",
        ]
    )
    (OUT_DIR / "modeling_report.md").write_text("\n".join(lines), encoding="utf-8")


def main():
    df = pd.read_csv(PANEL_PATH, encoding="utf-8-sig")
    df = df[df["is_label_valid"] == 1].copy()
    df[TARGET] = pd.to_numeric(df[TARGET], errors="coerce").astype(int)

    train = df[(df[TIME_COL] >= "2025-01") & (df[TIME_COL] <= "2025-07")].copy()
    test = df[(df[TIME_COL] >= "2025-08") & (df[TIME_COL] <= "2025-09")].copy()

    results = []
    preds = []
    coefs = []
    tops = []
    for name, numeric_cols in [
        ("baseline", BASE_NUMERIC),
        ("growth_alpha", BASE_NUMERIC + GROWTH_NUMERIC),
    ]:
        metrics, pred, coef, top = evaluate_model(name, train, test, numeric_cols, CATEGORICAL)
        results.append(metrics)
        preds.append(pred)
        coefs.append(coef)
        tops.append(top)

    metrics_df = pd.DataFrame(results)
    metrics_df.to_csv(OUT_DIR / "model_comparison.csv", index=False, encoding="utf-8-sig")
    pd.concat(preds, ignore_index=True).to_csv(OUT_DIR / "model_predictions.csv", index=False, encoding="utf-8-sig")
    pd.concat(coefs, ignore_index=True).to_csv(OUT_DIR / "model_coefficients.csv", index=False, encoding="utf-8-sig")
    pd.concat(tops, ignore_index=True).to_csv(OUT_DIR / "model_topn_metrics.csv", index=False, encoding="utf-8-sig")
    write_report(metrics_df)

    print(metrics_df.to_string(index=False))
    print(f"WROTE {OUT_DIR}")


if __name__ == "__main__":
    main()
