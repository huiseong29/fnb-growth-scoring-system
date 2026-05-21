from pathlib import Path

import numpy as np
import pandas as pd


SCORE_PATH = Path("analysis_outputs/scoring/store_scores.csv")
MODEL_PRED_PATH = Path("analysis_outputs/modeling/model_predictions.csv")
CALIBRATION_PATH = Path("analysis_outputs/modeling/calibration_lift_table.csv")
OUT_DIR = Path("analysis_outputs/roi")
OUT_DIR.mkdir(parents=True, exist_ok=True)
ASSUMPTION_PATH = OUT_DIR / "roi_assumptions.csv"

DEFAULT_ASSUMPTIONS = [
    {"scenario": "conservative", "monthly_lift_orders": 50, "gross_margin_per_order": 3000, "monthly_program_cost": 120000, "scenario_role": "stress"},
    {"scenario": "base", "monthly_lift_orders": 100, "gross_margin_per_order": 3000, "monthly_program_cost": 120000, "scenario_role": "main"},
    {"scenario": "causal_att_reference", "monthly_lift_orders": 114, "gross_margin_per_order": 3000, "monthly_program_cost": 120000, "scenario_role": "att_reference_only"},
]


def ensure_assumptions():
    if not ASSUMPTION_PATH.exists():
        pd.DataFrame(DEFAULT_ASSUMPTIONS).to_csv(ASSUMPTION_PATH, index=False, encoding="utf-8-sig")
    assumptions = pd.read_csv(ASSUMPTION_PATH, encoding="utf-8-sig")
    required = ["scenario", "monthly_lift_orders", "gross_margin_per_order", "monthly_program_cost"]
    missing = [c for c in required if c not in assumptions.columns]
    if missing:
        raise RuntimeError(f"Missing ROI assumption columns: {missing}")
    for col in ["monthly_lift_orders", "gross_margin_per_order", "monthly_program_cost"]:
        assumptions[col] = pd.to_numeric(assumptions[col], errors="coerce")
    return assumptions.dropna(subset=["scenario", "monthly_lift_orders", "gross_margin_per_order", "monthly_program_cost"])


def band_calibration_map():
    if not CALIBRATION_PATH.exists():
        return {}
    calib = pd.read_csv(CALIBRATION_PATH, encoding="utf-8-sig")
    calib = calib[(calib["model"] == "growth_alpha_nlp") & (calib["split"] == "time")].copy()
    if calib.empty:
        return {}
    return dict(zip(calib["probability_band"].astype(int), calib["actual_growth_rate"].astype(float)))


def add_rank_band_calibrated_probability(scores):
    scores = scores.copy()
    band_map = band_calibration_map()
    if band_map:
        rank = scores["final_growth_probability"].rank(method="first", ascending=False)
        band_count = max(band_map.keys())
        scores["probability_band"] = pd.qcut(rank, band_count, labels=False, duplicates="drop") + 1
        scores["probability_band"] = scores["probability_band"].astype(int)
        scores["band_calibrated_probability"] = scores["probability_band"].map(band_map).astype(float)
    else:
        scores["probability_band"] = np.nan
        scores["band_calibrated_probability"] = np.nan
    scores["band_calibrated_probability"] = scores["band_calibrated_probability"].fillna(scores["final_growth_probability"]).clip(0, 1)
    return scores


def main():
    assumptions = ensure_assumptions()
    scores = pd.read_csv(SCORE_PATH, encoding="utf-8-sig")
    required = ["platform_shop_id", "shop_name", "brand", "category", "final_growth_probability", "gromong_score", "grade"]
    missing = [c for c in required if c not in scores.columns]
    if missing:
        raise RuntimeError(f"Missing score columns: {missing}")
    scores["final_growth_probability"] = pd.to_numeric(scores["final_growth_probability"], errors="coerce").fillna(0).clip(0, 1)
    scores = add_rank_band_calibrated_probability(scores)

    rows = []
    for scenario in assumptions.to_dict("records"):
        tmp = scores[required + ["probability_band", "band_calibrated_probability"]].copy()
        tmp["scenario"] = scenario["scenario"]
        tmp["scenario_role"] = scenario.get("scenario_role", "")
        tmp["assumed_monthly_lift_orders"] = scenario["monthly_lift_orders"]
        tmp["gross_margin_per_order"] = scenario["gross_margin_per_order"]
        tmp["monthly_program_cost"] = scenario["monthly_program_cost"]
        tmp["break_even_probability"] = tmp["monthly_program_cost"] / (tmp["assumed_monthly_lift_orders"] * tmp["gross_margin_per_order"])
        tmp["expected_incremental_orders"] = tmp["final_growth_probability"] * tmp["assumed_monthly_lift_orders"]
        tmp["expected_incremental_orders_calibrated"] = tmp["band_calibrated_probability"] * tmp["assumed_monthly_lift_orders"]
        tmp["expected_monthly_margin"] = tmp["expected_incremental_orders"] * tmp["gross_margin_per_order"]
        tmp["expected_monthly_margin_calibrated"] = tmp["expected_incremental_orders_calibrated"] * tmp["gross_margin_per_order"]
        tmp["expected_monthly_roi"] = tmp["expected_monthly_margin"] - tmp["monthly_program_cost"]
        tmp["expected_monthly_roi_calibrated"] = tmp["expected_monthly_margin_calibrated"] - tmp["monthly_program_cost"]
        tmp["roi_per_cost"] = tmp["expected_monthly_roi"] / tmp["monthly_program_cost"]
        tmp["roi_per_cost_calibrated"] = tmp["expected_monthly_roi_calibrated"] / tmp["monthly_program_cost"]
        rows.append(tmp)

    roi = pd.concat(rows, ignore_index=True)
    roi = roi.sort_values(["scenario", "expected_monthly_roi_calibrated", "gromong_score"], ascending=[True, False, False])
    roi.to_csv(OUT_DIR / "roi_simulation_by_store.csv", index=False, encoding="utf-8-sig")

    summary = (
        roi.groupby("scenario")
        .agg(
            stores=("platform_shop_id", "nunique"),
            positive_roi_stores=("expected_monthly_roi", lambda s: int((s > 0).sum())),
            positive_roi_stores_calibrated=("expected_monthly_roi_calibrated", lambda s: int((s > 0).sum())),
            avg_expected_roi=("expected_monthly_roi", "mean"),
            avg_expected_roi_calibrated=("expected_monthly_roi_calibrated", "mean"),
            top_expected_roi_calibrated=("expected_monthly_roi_calibrated", "max"),
            avg_roi_per_cost_calibrated=("roi_per_cost_calibrated", "mean"),
        )
        .reset_index()
    )
    summary.to_csv(OUT_DIR / "roi_simulation_summary.csv", index=False, encoding="utf-8-sig")

    base = roi[roi["scenario"] == "base"].sort_values("gromong_score", ascending=False)
    base.head(20).to_csv(OUT_DIR / "roi_top20_base.csv", index=False, encoding="utf-8-sig")

    top_rows = []
    for scenario, group in roi.groupby("scenario"):
        ranked = group.sort_values("gromong_score", ascending=False).reset_index(drop=True)
        for top_n in [20, 50, 100]:
            top = ranked.head(min(top_n, len(ranked)))
            top_rows.append({
                "scenario": scenario,
                "top_n": len(top),
                "expected_hits_raw": top["final_growth_probability"].sum(),
                "expected_hits_calibrated": top["band_calibrated_probability"].sum(),
                "expected_incremental_orders_calibrated": top["expected_incremental_orders_calibrated"].sum(),
                "expected_roi_raw": top["expected_monthly_roi"].sum(),
                "expected_roi_calibrated": top["expected_monthly_roi_calibrated"].sum(),
                "positive_roi_stores_calibrated": int((top["expected_monthly_roi_calibrated"] > 0).sum()),
                "avg_break_even_probability": top["break_even_probability"].mean(),
                "avg_band_calibrated_probability": top["band_calibrated_probability"].mean(),
            })
    topk_summary = pd.DataFrame(top_rows)
    topk_summary.to_csv(OUT_DIR / "topk_roi_summary.csv", index=False, encoding="utf-8-sig")

    lines = [
        "# ROI Simulation Summary", "", "## 목적", "",
        "분류 모델의 성장 확률을 투자 우선순위 판단에 연결하기 위해 매장별 기대 월간 ROI를 시뮬레이션했다.", "",
        "## 가정 파일", "", f"- 사용 파일: `{ASSUMPTION_PATH.as_posix()}`", "",
        "## 계산식", "", "```text",
        "expected_incremental_orders = probability * assumed_monthly_lift_orders",
        "expected_monthly_roi = expected_incremental_orders * gross_margin_per_order - monthly_program_cost",
        "band_calibrated_probability = time split 검증 decile별 actual growth rate 매핑값",
        "```", "", "## 시나리오", "",
    ]
    for scenario in assumptions.to_dict("records"):
        lines.append(f"- {scenario['scenario']}: 월 추가 주문 {scenario['monthly_lift_orders']:.0f}건, 주문당 공헌이익 {scenario['gross_margin_per_order']:,.0f}원, 월 프로그램 비용 {scenario['monthly_program_cost']:,.0f}원")
    lines.extend(["", "## 주요 결과", ""])
    for row in summary.itertuples(index=False):
        lines.append(f"- {row.scenario}: 보정 ROI 양수 매장 {row.positive_roi_stores_calibrated}/{row.stores}, 평균 보정 기대 ROI {row.avg_expected_roi_calibrated:,.0f}원")
    lines.extend(["", "## 해석", "", "ATT는 예측 점수에 직접 넣지 않고 causal_att_reference 시나리오의 참고 주문 증가량으로만 사용했다. 최종 선별은 분류 확률, band 보정 확률, 비용 가정을 결합한 TopK ROI 표로 판단한다."])
    (OUT_DIR / "roi_simulation_report.md").write_text("\n".join(lines), encoding="utf-8")

    print(summary.to_string(index=False))
    print(topk_summary.to_string(index=False))
    print(f"WROTE {OUT_DIR}")


if __name__ == "__main__":
    main()
