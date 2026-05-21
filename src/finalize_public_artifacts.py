from pathlib import Path
from datetime import datetime, timezone
import json
import re

import pandas as pd


ROOT = Path(".")
SCORING_DIR = Path("analysis_outputs/scoring")
OUT_DIR = Path("analysis_outputs")
PUBLIC_FILES = [
    SCORING_DIR / "latest_shop_scores_public.csv",
    SCORING_DIR / "store_ranking_topN.csv",
]
FORBIDDEN_COLUMNS = [
    "growth_label",
    "future_order_3m",
    "future_sales",
    "treated",
    "post_treatment",
    "treated_x_post",
    "is_post_treatment",
    "months_since_treatment",
    "service_term_agree_date",
    "treatment_date",
]
FORBIDDEN_PUBLIC_NAMES = [
    "investment_score",
    "success_probability",
    "final_growth_score",
    "composite_growth_score",
    "gromong_score",
]
GRADE_BINS = {
    "decision_band": {
        "Priority Review": "calibrated_probability >= 0.40",
        "Watch": "0.30 <= calibrated_probability < 0.40",
        "Monitor": "0.20 <= calibrated_probability < 0.30",
        "Low Priority": "calibrated_probability < 0.20",
    },
    "action_band": {
        "Immediate Review": "predicted_priority_rank <= 50",
        "Secondary Review": "51 <= predicted_priority_rank <= 100",
        "Monitor": "101 <= predicted_priority_rank <= 200",
        "Backlog": "predicted_priority_rank > 200",
    },
}


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


def risk_flag(row):
    flags = []
    if row.get("signal_decomposition_index", 50) < 40:
        flags.append("low_explanation_index")
    if row.get("growth_alpha_score", 50) < 25:
        flags.append("growth_alpha_direction_risk")
    if row.get("stability_score", 50) < 40:
        flags.append("stability_risk")
    return ";".join(flags) if flags else "none"


def signal_columns(row):
    signals = {
        "model_probability": row.get("probability_score", 0),
        "growth_alpha": row.get("growth_alpha_score", 0),
        "review_growth": row.get("review_growth_score", 0),
        "operation": row.get("operation_score", 0),
        "stability": row.get("stability_score", 0),
        "market_fit": row.get("market_fit_score", 0),
    }
    top_positive = max(signals, key=signals.get)
    top_negative = min(signals, key=signals.get)
    return top_positive, top_negative


def rebuild_public_outputs():
    source = SCORING_DIR / "latest_shop_scores_public.csv"
    if not source.exists():
        source = SCORING_DIR / "store_scores.csv"
    df = pd.read_csv(source, encoding="utf-8-sig")
    if "calibrated_probability" not in df.columns and "predictive_rank_score" in df.columns:
        df["calibrated_probability"] = pd.to_numeric(df["predictive_rank_score"], errors="coerce")
    if "calibrated_probability" not in df.columns:
        raise RuntimeError("calibrated_probability is required for frozen public ranking")
    if "explanation_index" not in df.columns:
        if "gromong_score" not in df.columns:
            raise RuntimeError("explanation_index or gromong_score is required")
        df["explanation_index"] = pd.to_numeric(df["gromong_score"], errors="coerce")
    df["calibrated_probability"] = pd.to_numeric(df["calibrated_probability"], errors="coerce").fillna(0).clip(0, 1)
    df["predictive_rank_score"] = df["calibrated_probability"]
    raw_prob_col = "final_growth_probability" if "final_growth_probability" in df.columns else None
    if raw_prob_col:
        df["model_probability_raw"] = pd.to_numeric(df[raw_prob_col], errors="coerce")
    else:
        df["model_probability_raw"] = df["calibrated_probability"]

    sort_cols = ["predictive_rank_score", "model_probability_raw", "explanation_index"]
    df = df.sort_values(sort_cols, ascending=[False, False, False]).reset_index(drop=True)
    df["predicted_priority_rank"] = range(1, len(df) + 1)
    df["decision_band"] = df["calibrated_probability"].apply(decision_band)
    df["signal_decomposition_index"] = pd.to_numeric(df["explanation_index"], errors="coerce").round(2)
    df["action_band"] = df["predicted_priority_rank"].apply(action_band)
    df["risk_flag"] = df.apply(risk_flag, axis=1)
    sigs = df.apply(signal_columns, axis=1, result_type="expand")
    df["top_positive_signal"] = sigs[0]
    df["top_negative_signal"] = sigs[1]
    df["ranking_basis"] = "calibrated_model_probability"
    df["score_role"] = "composite_is_explanation_index_not_predictive_rank"

    public_cols = [
        "predicted_priority_rank",
        "platform_shop_id",
        "year_month",
        "shop_name",
        "brand",
        "category",
        "sido",
        "sigungu",
        "predictive_rank_score",
        "decision_band",
        "explanation_index",
        "signal_decomposition_index",
        "action_band",
        "risk_flag",
        "top_positive_signal",
        "top_negative_signal",
        "model_probability_raw",
        "probability_band",
        "probability_score",
        "growth_alpha_score",
        "review_growth_score",
        "operation_score",
        "stability_score",
        "market_fit_score",
        "ranking_basis",
        "score_role",
    ]
    safe = df[[c for c in public_cols if c in df.columns]].copy()
    safe.to_csv(SCORING_DIR / "latest_shop_scores_public.csv", index=False, encoding="utf-8-sig")
    safe.head(200).to_csv(SCORING_DIR / "store_ranking_topN.csv", index=False, encoding="utf-8-sig")
    return safe


def validate_public_outputs():
    rows = []
    failures = []
    for path in PUBLIC_FILES:
        if not path.exists():
            failures.append(f"missing file: {path}")
            continue
        df = pd.read_csv(path, encoding="utf-8-sig", nrows=5)
        columns = list(df.columns)
        lowered = [c.lower() for c in columns]
        forbidden_hits = []
        for forbidden in FORBIDDEN_COLUMNS:
            if any(forbidden in c for c in lowered):
                forbidden_hits.append(forbidden)
        for forbidden in FORBIDDEN_PUBLIC_NAMES:
            if forbidden in lowered:
                forbidden_hits.append(forbidden)
        status = "PASS" if not forbidden_hits else "FAIL"
        if forbidden_hits:
            failures.append(f"{path}: {', '.join(sorted(set(forbidden_hits)))}")
        rows.append({"file": path.as_posix(), "columns": len(columns), "status": status, "forbidden_hits": ", ".join(sorted(set(forbidden_hits)))})
    report = [
        "# Final Public Artifact Gate Report",
        "",
        "## Gate Rule",
        "",
        "Public export must not expose label, future outcome, treatment, or misleading predictive-score column names. Predictive ranking is based on calibrated model probability; composite score is exported only as explanation_index/signal_decomposition_index.",
        "",
        "| file | columns | status | forbidden hits |",
        "| --- | ---: | --- | --- |",
    ]
    for row in rows:
        report.append(f"| {row['file']} | {row['columns']} | {row['status']} | {row['forbidden_hits'] or '-'} |")
    report.extend(["", "## Forbidden Column Patterns", ""])
    report.append(", ".join(FORBIDDEN_COLUMNS + FORBIDDEN_PUBLIC_NAMES))
    if failures:
        report.extend(["", "## Result", "", "FAIL", ""] + [f"- {f}" for f in failures])
    else:
        report.extend(["", "## Result", "", "PASS"])
    (OUT_DIR / "final_public_artifact_gate_report.md").write_text("\n".join(report), encoding="utf-8")
    if failures:
        raise RuntimeError("Public artifact gate failed: " + "; ".join(failures))
    return rows


def read_metric(path, selector_col=None, selector_value=None):
    if not Path(path).exists():
        return {}
    df = pd.read_csv(path, encoding="utf-8-sig")
    if selector_col and selector_col in df.columns:
        df = df[df[selector_col] == selector_value]
    if df.empty:
        return {}
    return df.iloc[0].to_dict()


def write_model_card():
    validation = read_metric("analysis_outputs/modeling/model_validation_audit.csv", "model", "growth_alpha_nlp")
    strategy = read_metric("analysis_outputs/scoring/ranking_strategy_comparison.csv", "strategy", "calibrated_probability_ranking")
    composite = read_metric("analysis_outputs/scoring/ranking_strategy_comparison.csv", "strategy", "current_composite_score_ranking")
    lines = [
        "# Final Model Card",
        "",
        "## Project Definition",
        "",
        "F&B 매장의 성장 후보군을 우선 검토하기 위한 decision-support pipeline이다. 최종 public ranking은 calibrated model probability를 기준으로 하며, composite score는 설명 가능한 신호 분해 지수로만 사용한다.",
        "",
        "## Intended Use",
        "",
        "- 성장 가능성이 있는 매장을 우선 검토할 후보군으로 정렬한다.",
        "- 리뷰, 운영, 안정성, 상권 보조 신호를 설명 지수로 제공한다.",
        "- ROI는 고정 가정 기반 scenario decision support로 사용한다.",
        "",
        "## Not Intended Use",
        "",
        "- 자동 투자 결정 또는 계약 결정에 사용하지 않는다.",
        "- composite score를 성장 예측 순위 점수로 사용하지 않는다.",
        "- ROI를 보장 수익 또는 실제 수익 예측으로 해석하지 않는다.",
        "- SHAP 또는 feature contribution을 인과효과로 해석하지 않는다.",
        "",
        "## Predictive Ranking 기준",
        "",
        "Predictive ranking is based on calibrated model probability. Public outputs use `predictive_rank_score` and `predicted_priority_rank` for ordering.",
        "",
        "## Explanation Index 역할",
        "",
        "`explanation_index`와 `signal_decomposition_index`는 probability, Growth Alpha, review growth, operation, stability, market fit 신호를 요약한 설명용 index다. Direction audit 결과 일부 component가 최신월 growth label과 반대 또는 약한 방향성을 보여 final ranking에서는 제외했다.",
        "",
        "## Causal Layer 역할",
        "",
        "ATT/DID 계열 결과는 평균 효과 reference layer로만 유지한다. Predictive score나 public ranking feature로 직접 투입하지 않는다.",
        "",
        "## ROI Scenario 역할",
        "",
        "ROI is scenario-based decision support, not guaranteed return. ROI files use calibrated probability and explicit assumptions from `analysis_outputs/roi/roi_assumptions.csv`.",
        "",
        "## Leakage Controls",
        "",
        "- Time-aware split 유지",
        "- future outcome/label/treatment 계열 컬럼은 public artifact gate에서 차단",
        "- ATT는 predictive score에 직접 투입하지 않음",
        "- Public outputs exclude label/future/treatment columns",
        "",
        "## Validation Summary",
        "",
        f"- Full NLP time split AUC: {validation.get('auc', float('nan')):.4f}",
        f"- Full NLP PR-AUC: {validation.get('pr_auc', float('nan')):.4f}",
        f"- Full NLP Brier score: {validation.get('brier_score', float('nan')):.4f}",
        f"- Calibrated probability ranking AUC: {strategy.get('roc_auc', float('nan')):.4f}",
        f"- Calibrated probability Top100 hit/lift: {strategy.get('top100_hit_count', float('nan'))}/{strategy.get('top100_lift', float('nan')):.2f}",
        f"- Current composite ranking AUC: {composite.get('roc_auc', float('nan')):.4f}",
        "",
        "## Known Limitations",
        "",
        "- Composite score is not a reliable predictive ranking score on the latest-month audit.",
        "- Growth Alpha, review growth, stability, and composite components showed weak or reversed direction in the latest-month direction audit.",
        "- Seoul external-market variables are limited to the matched Seoul subset and should not be generalized nationally.",
        "- KoBERT/fine-tuned deep NLP and causal forest/uplift modeling are not included.",
        "- Public ranking supports review priority, not automatic action.",
        "",
        "## Final Public Artifacts List",
        "",
        "- `analysis_outputs/scoring/latest_shop_scores_public.csv`",
        "- `analysis_outputs/scoring/store_ranking_topN.csv`",
        "- `analysis_outputs/scoring/component_direction_audit.csv`",
        "- `analysis_outputs/scoring/component_inversion_check.csv`",
        "- `analysis_outputs/scoring/ranking_strategy_comparison.csv`",
        "- `analysis_outputs/scoring/ranking_strategy_summary.md`",
        "- `analysis_outputs/final_public_artifact_gate_report.md`",
        "",
        "## 발표에서 사용 가능한 주장",
        "",
        "- Predictive ranking is based on calibrated model probability.",
        "- Explanation index summarizes interpretable growth-related signals.",
        "- Grade and decision bands are priority review bands, not automatic investment decisions.",
        "- SHAP is used as predictive contribution, not causal attribution.",
        "- ROI is scenario-based decision support, not guaranteed return.",
        "",
        "## 발표에서 금지해야 할 주장",
        "",
        "- Do not say the GroMong explanation index is a growth prediction model.",
        "- Do not present the composite index as the ordering metric for predictive ranking.",
        "- Do not describe SHAP-derived contribution as causal weighting.",
        "- Do not describe high bands as automatic investment targets.",
        "- Do not describe ROI scenarios as forecasts or guaranteed returns.",
    ]
    (OUT_DIR / "final_model_card.md").write_text("\n".join(lines), encoding="utf-8")


def file_info(path):
    p = Path(path)
    return {"path": p.as_posix(), "exists": p.exists(), "bytes": p.stat().st_size if p.exists() else None}


def write_manifest():
    scores = pd.read_csv(SCORING_DIR / "latest_shop_scores_public.csv", encoding="utf-8-sig", nrows=1)
    manifest = {
        "run_date": datetime.now(timezone.utc).isoformat(),
        "as_of_date": str(scores["year_month"].iloc[0]) if "year_month" in scores.columns and len(scores) else None,
        "model_artifact": file_info("analysis_outputs/modeling/model_predictions.csv"),
        "calibration_artifact": file_info("analysis_outputs/modeling/calibration_lift_table.csv"),
        "feature_schema": {
            "predictive_rank_score": "calibrated model probability",
            "explanation_index": "composite signal decomposition index, not predictive ranking score",
            "signal_components": ["probability_score", "growth_alpha_score", "review_growth_score", "operation_score", "stability_score", "market_fit_score"],
        },
        "grade_bins": GRADE_BINS,
        "public_output_files": [file_info(p) for p in PUBLIC_FILES],
        "validation_reports": [
            file_info("analysis_outputs/modeling/model_validation_audit.csv"),
            file_info("analysis_outputs/modeling/group_holdout_metrics.csv"),
            file_info("analysis_outputs/modeling/calibration_lift_table.csv"),
            file_info("analysis_outputs/scoring/ranking_strategy_comparison.csv"),
        ],
        "score_direction_audit_files": [
            file_info("analysis_outputs/scoring/component_direction_audit.csv"),
            file_info("analysis_outputs/scoring/component_direction_audit.md"),
            file_info("analysis_outputs/scoring/component_inversion_check.csv"),
            file_info("analysis_outputs/scoring/ranking_strategy_summary.md"),
        ],
        "model_card": file_info("analysis_outputs/final_model_card.md"),
        "artifact_gate": file_info("analysis_outputs/final_public_artifact_gate_report.md"),
        "known_limitations": [
            "Composite score is explanation index, not predictive ranking score.",
            "Some component directions are weak or reversed in latest-month audit.",
            "ROI is scenario-based support, not guaranteed return.",
            "External market variables are limited to Seoul matched subset.",
            "No new model, weight retuning, or post-hoc AUC optimization in freeze step.",
        ],
    }
    (OUT_DIR / "final_freeze_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def semantic_cleanup_docs():
    replacements = {
        "GroMong Score predicts growth": "Predictive ranking is based on calibrated model probability",
        "composite score is the final ranking score": "composite score is an explanation index, not the final predictive ranking score",
        "SHAP-optimized causal weight": "SHAP-informed predictive contribution weight",
        "S/A grade means investment target": "S/A band means priority review band, not automatic investment decision",
        "ROI prediction": "scenario-based ROI decision support",
    }
    targets = [Path("README.md")] + list(Path("docs").glob("*.md")) + [
        Path("analysis_outputs/final_gap_closure_report.md"),
        Path("analysis_outputs/scoring/ranking_strategy_summary.md"),
        Path("analysis_outputs/scoring/weight_sensitivity_summary.md"),
    ]
    for path in targets:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        original = text
        for old, new in replacements.items():
            text = text.replace(old, new)
        if path.name in {"README.md", "score_design_rationale.md", "final_outputs_index.md"}:
            block = """

## Final Semantic Freeze Note

- Predictive ranking is based on calibrated model probability.
- Explanation index summarizes interpretable growth-related signals and is not the final predictive ranking score.
- Grade bands are priority review bands, not automatic investment decisions.
- SHAP is used as predictive contribution, not causal attribution.
- ROI is scenario-based decision support, not guaranteed return.
- Direction audit showed that some component scores, including Growth Alpha and stability, are weakly or inversely aligned with the latest-month growth label; this is why public ranking was redefined around calibrated probability.
"""
            if "## Final Semantic Freeze Note" not in text:
                text = text.rstrip() + block
        if text != original:
            path.write_text(text, encoding="utf-8")


def main():
    rebuild_public_outputs()
    semantic_cleanup_docs()
    validate_public_outputs()
    write_model_card()
    # Re-run gate after model card has been produced; public outputs are unchanged.
    validate_public_outputs()
    write_manifest()
    print("FINAL PUBLIC ARTIFACTS FROZEN")


if __name__ == "__main__":
    main()

