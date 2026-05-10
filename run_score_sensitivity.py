from __future__ import annotations

import csv
import math
from pathlib import Path
from statistics import mean


ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "analysis_outputs" / "scoring" / "store_scores.csv"
OUT_DIR = ROOT / "analysis_outputs" / "sensitivity"
CHART_DIR = OUT_DIR / "charts"

COMPONENTS = [
    "probability_score",
    "growth_alpha_score",
    "review_growth_score",
    "operation_score",
    "stability_score",
]

SCENARIOS = {
    "official_current": {
        "label": "현재 공식 가중치",
        "weights": {
            "probability_score": 0.35,
            "growth_alpha_score": 0.25,
            "review_growth_score": 0.15,
            "operation_score": 0.15,
            "stability_score": 0.10,
        },
        "market_weight": 0.10,
    },
    "growth_probability_focus": {
        "label": "성장확률 강화",
        "weights": {
            "probability_score": 0.45,
            "growth_alpha_score": 0.20,
            "review_growth_score": 0.12,
            "operation_score": 0.13,
            "stability_score": 0.10,
        },
        "market_weight": 0.10,
    },
    "growth_alpha_focus": {
        "label": "Growth Alpha 강화",
        "weights": {
            "probability_score": 0.25,
            "growth_alpha_score": 0.40,
            "review_growth_score": 0.15,
            "operation_score": 0.10,
            "stability_score": 0.10,
        },
        "market_weight": 0.10,
    },
    "review_focus": {
        "label": "리뷰 성장 강화",
        "weights": {
            "probability_score": 0.30,
            "growth_alpha_score": 0.20,
            "review_growth_score": 0.30,
            "operation_score": 0.10,
            "stability_score": 0.10,
        },
        "market_weight": 0.10,
    },
    "operation_focus": {
        "label": "운영 역량 강화",
        "weights": {
            "probability_score": 0.28,
            "growth_alpha_score": 0.22,
            "review_growth_score": 0.12,
            "operation_score": 0.28,
            "stability_score": 0.10,
        },
        "market_weight": 0.10,
    },
    "stability_focus": {
        "label": "안정성 강화",
        "weights": {
            "probability_score": 0.30,
            "growth_alpha_score": 0.20,
            "review_growth_score": 0.12,
            "operation_score": 0.13,
            "stability_score": 0.25,
        },
        "market_weight": 0.10,
    },
    "market_fit_focus": {
        "label": "서울 상권 적합도 강화",
        "weights": {
            "probability_score": 0.35,
            "growth_alpha_score": 0.25,
            "review_growth_score": 0.15,
            "operation_score": 0.15,
            "stability_score": 0.10,
        },
        "market_weight": 0.20,
    },
}

COLORS = ["#6D5EF7", "#00A6ED", "#00C49A", "#FFB000", "#FF6B6B", "#D65DB1", "#2EC4B6"]


def to_float(value: str, default: float = 0.0) -> float:
    if value is None or value == "":
        return default
    try:
        return float(value)
    except ValueError:
        return default


def grade(score: float) -> str:
    if score >= 80:
        return "A"
    if score >= 65:
        return "B"
    if score >= 50:
        return "C"
    return "D"


def rank(values: dict[str, float]) -> dict[str, int]:
    ordered = sorted(values.items(), key=lambda item: (-item[1], item[0]))
    return {store_id: i + 1 for i, (store_id, _) in enumerate(ordered)}


def pearson(xs: list[float], ys: list[float]) -> float:
    if len(xs) < 2:
        return 0.0
    mx, my = mean(xs), mean(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den_x = math.sqrt(sum((x - mx) ** 2 for x in xs))
    den_y = math.sqrt(sum((y - my) ** 2 for y in ys))
    if den_x == 0 or den_y == 0:
        return 0.0
    return num / (den_x * den_y)


def load_rows() -> list[dict[str, str]]:
    with INPUT.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def scenario_score(row: dict[str, str], scenario: dict) -> float:
    base = sum(to_float(row[col]) * weight for col, weight in scenario["weights"].items())
    market_weight = scenario["market_weight"]
    if to_float(row.get("is_seoul_external", "0")) >= 1:
        market = to_float(row.get("market_fit_score", ""), 50.0)
        final = (1 - market_weight) * base + market_weight * market
    else:
        final = base
    return round(final, 4)


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def svg_bar_chart(path: Path, title: str, labels: list[str], values: list[float], ylabel: str, fmt: str = "{:.1f}") -> None:
    width, height = 980, 520
    margin_left, margin_right, margin_top, margin_bottom = 90, 40, 80, 110
    chart_w = width - margin_left - margin_right
    chart_h = height - margin_top - margin_bottom
    max_v = max(values) if values else 1
    max_v = max_v * 1.15 if max_v > 0 else 1
    bar_w = chart_w / len(values) * 0.62
    gap = chart_w / len(values)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#FBFBFE"/>',
        f'<text x="{width/2}" y="42" text-anchor="middle" font-size="25" font-weight="700" fill="#1D1D2C">{title}</text>',
        f'<line x1="{margin_left}" y1="{margin_top+chart_h}" x2="{width-margin_right}" y2="{margin_top+chart_h}" stroke="#2B2D42" stroke-width="1.4"/>',
        f'<line x1="{margin_left}" y1="{margin_top}" x2="{margin_left}" y2="{margin_top+chart_h}" stroke="#2B2D42" stroke-width="1.4"/>',
        f'<text x="24" y="{margin_top+chart_h/2}" transform="rotate(-90 24 {margin_top+chart_h/2})" text-anchor="middle" font-size="14" fill="#343A40">{ylabel}</text>',
    ]
    for i, (label, value) in enumerate(zip(labels, values)):
        x = margin_left + i * gap + (gap - bar_w) / 2
        h = value / max_v * chart_h
        y = margin_top + chart_h - h
        color = COLORS[i % len(COLORS)]
        parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w:.1f}" height="{h:.1f}" rx="6" fill="{color}"/>')
        parts.append(f'<text x="{x+bar_w/2:.1f}" y="{y-8:.1f}" text-anchor="middle" font-size="13" font-weight="700" fill="#1D1D2C">{fmt.format(value)}</text>')
        parts.append(f'<text x="{x+bar_w/2:.1f}" y="{height-76}" text-anchor="end" font-size="12" fill="#343A40" transform="rotate(-32 {x+bar_w/2:.1f} {height-76})">{label}</text>')
    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def svg_grouped_grade_chart(path: Path, rows: list[dict]) -> None:
    width, height = 1100, 560
    ml, mr, mt, mb = 90, 40, 70, 115
    chart_w, chart_h = width - ml - mr, height - mt - mb
    labels = [r["scenario_label"] for r in rows]
    grades = ["A", "B", "C", "D"]
    max_v = max(int(r[f"grade_{g}_count"]) for r in rows for g in grades) * 1.18
    group_w = chart_w / len(rows)
    bar_w = group_w * 0.15
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#FCFCFF"/>',
        f'<text x="{width/2}" y="38" text-anchor="middle" font-size="24" font-weight="700" fill="#1D1D2C">가중치 시나리오별 등급 분포</text>',
        f'<line x1="{ml}" y1="{mt+chart_h}" x2="{width-mr}" y2="{mt+chart_h}" stroke="#2B2D42"/>',
        f'<line x1="{ml}" y1="{mt}" x2="{ml}" y2="{mt+chart_h}" stroke="#2B2D42"/>',
    ]
    grade_colors = {"A": "#6D5EF7", "B": "#00A6ED", "C": "#00C49A", "D": "#FF6B6B"}
    for i, r in enumerate(rows):
        base_x = ml + i * group_w + group_w * 0.18
        for j, g in enumerate(grades):
            v = int(r[f"grade_{g}_count"])
            h = v / max_v * chart_h
            x = base_x + j * bar_w * 1.25
            y = mt + chart_h - h
            parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w:.1f}" height="{h:.1f}" rx="4" fill="{grade_colors[g]}"/>')
        parts.append(f'<text x="{ml+i*group_w+group_w/2:.1f}" y="{height-76}" text-anchor="end" font-size="12" fill="#343A40" transform="rotate(-30 {ml+i*group_w+group_w/2:.1f} {height-76})">{labels[i]}</text>')
    legend_x = width - 310
    for k, g in enumerate(grades):
        x = legend_x + k * 70
        parts.append(f'<rect x="{x}" y="52" width="14" height="14" rx="3" fill="{grade_colors[g]}"/>')
        parts.append(f'<text x="{x+21}" y="64" font-size="13" fill="#343A40">{g}</text>')
    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    CHART_DIR.mkdir(parents=True, exist_ok=True)

    rows = load_rows()
    scenario_scores: dict[str, dict[str, float]] = {}
    detail_rows: list[dict] = []

    for key, scenario in SCENARIOS.items():
        scores = {}
        for row in rows:
            store_id = row["platform_shop_id"]
            score = scenario_score(row, scenario)
            scores[store_id] = score
            detail_rows.append({
                "scenario": key,
                "scenario_label": scenario["label"],
                "platform_shop_id": store_id,
                "shop_name": row["shop_name"],
                "brand": row["brand"],
                "category": row["category"],
                "sido": row["sido"],
                "sigungu": row["sigungu"],
                "score": f"{score:.4f}",
                "grade": grade(score),
            })
        scenario_scores[key] = scores

    current_scores = {row["platform_shop_id"]: to_float(row["gromong_score"]) for row in rows}
    current_rank = rank(current_scores)
    current_top50 = set(sorted(current_scores, key=lambda sid: (-current_scores[sid], sid))[:50])
    current_top100 = set(sorted(current_scores, key=lambda sid: (-current_scores[sid], sid))[:100])

    summary_rows: list[dict] = []
    stability_count = {sid: 0 for sid in current_scores}

    for key, scenario in SCENARIOS.items():
        scores = scenario_scores[key]
        ranked_ids = sorted(scores, key=lambda sid: (-scores[sid], sid))
        top50, top100 = set(ranked_ids[:50]), set(ranked_ids[:100])
        for sid in top100:
            stability_count[sid] += 1
        scenario_rank = rank(scores)
        common_ids = list(current_scores)
        corr = pearson([current_rank[sid] for sid in common_ids], [scenario_rank[sid] for sid in common_ids])
        grades = {g: 0 for g in ["A", "B", "C", "D"]}
        for score in scores.values():
            grades[grade(score)] += 1
        summary_rows.append({
            "scenario": key,
            "scenario_label": scenario["label"],
            "mean_score": f"{mean(scores.values()):.4f}",
            "median_score": f"{sorted(scores.values())[len(scores)//2]:.4f}",
            "top50_overlap_count": len(current_top50 & top50),
            "top50_overlap_rate": f"{len(current_top50 & top50) / 50:.4f}",
            "top100_overlap_count": len(current_top100 & top100),
            "top100_overlap_rate": f"{len(current_top100 & top100) / 100:.4f}",
            "rank_correlation_with_current": f"{corr:.4f}",
            "grade_A_count": grades["A"],
            "grade_B_count": grades["B"],
            "grade_C_count": grades["C"],
            "grade_D_count": grades["D"],
        })

    stable_rows = []
    current_order = sorted(current_scores, key=lambda sid: (-current_scores[sid], sid))
    meta = {r["platform_shop_id"]: r for r in rows}
    for sid in current_order[:150]:
        row = meta[sid]
        stable_rows.append({
            "platform_shop_id": sid,
            "shop_name": row["shop_name"],
            "brand": row["brand"],
            "category": row["category"],
            "current_score": f"{current_scores[sid]:.2f}",
            "current_rank": current_rank[sid],
            "top100_scenario_count": stability_count[sid],
            "top100_scenario_rate": f"{stability_count[sid] / len(SCENARIOS):.4f}",
        })

    write_csv(OUT_DIR / "score_sensitivity_summary.csv", summary_rows, list(summary_rows[0].keys()))
    write_csv(OUT_DIR / "score_sensitivity_detail.csv", detail_rows, list(detail_rows[0].keys()))
    write_csv(OUT_DIR / "top100_stability.csv", stable_rows, list(stable_rows[0].keys()))

    labels = [r["scenario_label"] for r in summary_rows]
    svg_bar_chart(
        CHART_DIR / "top100_overlap_by_scenario.svg",
        "현재 Top 100과 가중치 시나리오별 Top 100 겹침률",
        labels,
        [float(r["top100_overlap_rate"]) * 100 for r in summary_rows],
        "겹침률(%)",
        "{:.0f}%",
    )
    svg_bar_chart(
        CHART_DIR / "rank_correlation_by_scenario.svg",
        "현재 순위와 시나리오별 순위 상관",
        labels,
        [float(r["rank_correlation_with_current"]) for r in summary_rows],
        "순위 상관",
        "{:.3f}",
    )
    svg_bar_chart(
        CHART_DIR / "mean_score_by_scenario.svg",
        "가중치 시나리오별 평균 점수",
        labels,
        [float(r["mean_score"]) for r in summary_rows],
        "평균 점수",
        "{:.1f}",
    )
    svg_grouped_grade_chart(CHART_DIR / "grade_counts_by_scenario.svg", summary_rows)
    svg_bar_chart(
        CHART_DIR / "top100_stability_top20.svg",
        "현재 상위 20개 매장의 Top 100 유지 횟수",
        [r["shop_name"][:16] for r in stable_rows[:20]],
        [float(r["top100_scenario_count"]) for r in stable_rows[:20]],
        "7개 시나리오 중 유지 횟수",
        "{:.0f}",
    )

    report = [
        "# Score Sensitivity Report",
        "",
        "## 목적",
        "",
        "GroMong Score의 5개 지수 가중치가 달라져도 상위 추천 매장이 얼마나 안정적으로 유지되는지 확인했다.",
        "",
        "## 시나리오",
        "",
    ]
    for key, scenario in SCENARIOS.items():
        weights = ", ".join(f"{col} {weight:.2f}" for col, weight in scenario["weights"].items())
        report.append(f"- {scenario['label']}: {weights}, 서울 상권 보정 {scenario['market_weight']:.2f}")
    report.extend([
        "",
        "## 핵심 결과",
        "",
    ])
    for r in summary_rows:
        report.append(
            f"- {r['scenario_label']}: Top100 겹침률 {float(r['top100_overlap_rate']) * 100:.0f}%, "
            f"순위 상관 {float(r['rank_correlation_with_current']):.3f}, "
            f"A등급 {r['grade_A_count']}개"
        )
    report.extend([
        "",
        "## 해석",
        "",
        "가중치를 바꿔도 현재 Top 100과 상당수 매장이 겹치면, 최종 추천 결과가 특정 가중치 하나에만 의존하지 않는다고 설명할 수 있다.",
        "반대로 특정 시나리오에서 겹침률이 낮아지는 경우, 해당 지수의 영향력이 크다는 의미이므로 발표에서 보완 근거로 활용한다.",
    ])
    (OUT_DIR / "score_sensitivity_report.md").write_text("\n".join(report), encoding="utf-8")

    print("WROTE", OUT_DIR)
    print("SCENARIOS", len(SCENARIOS))
    for r in summary_rows:
        print(r["scenario_label"], r["top100_overlap_rate"], r["rank_correlation_with_current"], r["grade_A_count"])


if __name__ == "__main__":
    main()
