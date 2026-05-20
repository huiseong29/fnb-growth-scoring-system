from pathlib import Path

import pandas as pd


SCORE_PATH = Path("analysis_outputs/scoring/store_scores.csv")
OUT_DIR = Path("analysis_outputs/roi")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Conservative scenario grid. Values are intentionally explicit so the
# presentation can explain assumptions instead of hiding them in the model.
SCENARIOS = [
    {"scenario": "conservative", "monthly_lift_orders": 50, "gross_margin_per_order": 3000, "monthly_program_cost": 120000},
    {"scenario": "base", "monthly_lift_orders": 100, "gross_margin_per_order": 3000, "monthly_program_cost": 120000},
    {"scenario": "causal_att_reference", "monthly_lift_orders": 114, "gross_margin_per_order": 3000, "monthly_program_cost": 120000},
]


def main():
    scores = pd.read_csv(SCORE_PATH, encoding="utf-8-sig")
    required = ["platform_shop_id", "shop_name", "brand", "category", "final_growth_probability", "gromong_score", "grade"]
    missing = [c for c in required if c not in scores.columns]
    if missing:
        raise RuntimeError(f"Missing score columns: {missing}")

    rows = []
    for scenario in SCENARIOS:
        tmp = scores[required].copy()
        tmp["scenario"] = scenario["scenario"]
        tmp["assumed_monthly_lift_orders"] = scenario["monthly_lift_orders"]
        tmp["gross_margin_per_order"] = scenario["gross_margin_per_order"]
        tmp["monthly_program_cost"] = scenario["monthly_program_cost"]
        tmp["expected_incremental_orders"] = tmp["final_growth_probability"] * scenario["monthly_lift_orders"]
        tmp["expected_monthly_margin"] = tmp["expected_incremental_orders"] * scenario["gross_margin_per_order"]
        tmp["expected_monthly_roi"] = tmp["expected_monthly_margin"] - scenario["monthly_program_cost"]
        tmp["roi_per_cost"] = tmp["expected_monthly_roi"] / scenario["monthly_program_cost"]
        rows.append(tmp)

    roi = pd.concat(rows, ignore_index=True)
    roi = roi.sort_values(["scenario", "expected_monthly_roi"], ascending=[True, False])
    roi.to_csv(OUT_DIR / "roi_simulation_by_store.csv", index=False, encoding="utf-8-sig")

    summary = (
        roi.groupby("scenario")
        .agg(
            stores=("platform_shop_id", "nunique"),
            positive_roi_stores=("expected_monthly_roi", lambda s: int((s > 0).sum())),
            avg_expected_roi=("expected_monthly_roi", "mean"),
            top_expected_roi=("expected_monthly_roi", "max"),
            avg_roi_per_cost=("roi_per_cost", "mean"),
        )
        .reset_index()
    )
    summary.to_csv(OUT_DIR / "roi_simulation_summary.csv", index=False, encoding="utf-8-sig")

    top_base = roi[roi["scenario"] == "base"].head(20)
    top_base.to_csv(OUT_DIR / "roi_top20_base.csv", index=False, encoding="utf-8-sig")

    lines = [
        "# ROI Simulation Summary",
        "",
        "## 목적",
        "",
        "분류 모델의 성장 확률을 투자 우선순위 판단에 연결하기 위해 매장별 기대 월간 ROI를 시뮬레이션했다.",
        "",
        "## 계산식",
        "",
        "```text",
        "expected_incremental_orders = final_growth_probability * assumed_monthly_lift_orders",
        "expected_monthly_margin = expected_incremental_orders * gross_margin_per_order",
        "expected_monthly_roi = expected_monthly_margin - monthly_program_cost",
        "```",
        "",
        "## 시나리오",
        "",
    ]
    for scenario in SCENARIOS:
        lines.append(
            f"- {scenario['scenario']}: 월 추가 주문 {scenario['monthly_lift_orders']}건, 주문당 공헌이익 {scenario['gross_margin_per_order']:,}원, 월 프로그램 비용 {scenario['monthly_program_cost']:,}원"
        )
    lines.extend(["", "## 주요 결과", ""])
    for row in summary.itertuples(index=False):
        lines.append(
            f"- {row.scenario}: ROI 양수 매장 {row.positive_roi_stores}/{row.stores}, 평균 기대 ROI {row.avg_expected_roi:,.0f}원, 최고 기대 ROI {row.top_expected_roi:,.0f}원"
        )
    lines.extend(
        [
            "",
            "## 해석",
            "",
            "이 결과는 실제 투자 확정 모델이 아니라 발표용 의사결정 프레임이다. 인과추론 ATT는 전체 평균 효과의 참고값으로 두고, 최종 선별은 분류 모델의 매장별 성장 확률과 비용 가정을 결합해 수행한다.",
            "",
            "따라서 피드백에서 지적된 예측과 투자효과의 분리를 줄이고, GroMong Score를 우선 검토 후보군 선정과 ROI 민감도 검토에 연결할 수 있다.",
        ]
    )
    (OUT_DIR / "roi_simulation_report.md").write_text("\n".join(lines), encoding="utf-8")

    print(summary.to_string(index=False))
    print(f"WROTE {OUT_DIR}")


if __name__ == "__main__":
    main()
