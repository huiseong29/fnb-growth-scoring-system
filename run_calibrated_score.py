from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean


ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "analysis_outputs" / "scoring" / "store_scores.csv"
OUT_DIR = ROOT / "analysis_outputs" / "calibrated_score"
CHART_DIR = OUT_DIR / "charts"

COLORS = ["#6D5EF7", "#00A6ED", "#00C49A", "#FFB000", "#FF6B6B", "#D65DB1", "#2EC4B6", "#845EC2"]


def to_float(value: str, default: float = 0.0) -> float:
    if value is None or value == "":
        return default
    try:
        return float(value)
    except ValueError:
        return default


def read_rows() -> list[dict[str, str]]:
    with INPUT.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def percentile_ranks(rows: list[dict[str, str]], group_col: str) -> dict[str, float]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row[group_col]].append(row)

    pct: dict[str, float] = {}
    for _, items in grouped.items():
        ordered = sorted(items, key=lambda r: (to_float(r["gromong_score"]), r["platform_shop_id"]))
        n = len(ordered)
        if n == 1:
            pct[ordered[0]["platform_shop_id"]] = 100.0
            continue
        for i, row in enumerate(ordered):
            pct[row["platform_shop_id"]] = 100.0 * i / (n - 1)
    return pct


def dense_rank(rows: list[dict], key: str, group: str | None = None) -> dict[str, int]:
    if group is None:
        ordered = sorted(rows, key=lambda r: (-to_float(r[key]), r["platform_shop_id"]))
        return {r["platform_shop_id"]: i + 1 for i, r in enumerate(ordered)}

    result = {}
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[row[group]].append(row)
    for _, items in grouped.items():
        ordered = sorted(items, key=lambda r: (-to_float(r[key]), r["platform_shop_id"]))
        for i, row in enumerate(ordered):
            result[row["platform_shop_id"]] = i + 1
    return result


def grade(score: float) -> str:
    if score >= 80:
        return "A"
    if score >= 65:
        return "B"
    if score >= 50:
        return "C"
    return "D"


def svg_bar(path: Path, title: str, labels: list[str], values: list[float], ylabel: str, fmt: str = "{:.1f}") -> None:
    width, height = 1100, 560
    ml, mr, mt, mb = 90, 45, 78, 130
    cw, ch = width - ml - mr, height - mt - mb
    max_v = max(values) * 1.18 if values else 1
    step = cw / max(len(values), 1)
    bar_w = step * 0.58
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#FBFBFE"/>',
        f'<text x="{width/2}" y="42" text-anchor="middle" font-size="24" font-weight="700" fill="#1D1D2C">{title}</text>',
        f'<line x1="{ml}" y1="{mt+ch}" x2="{width-mr}" y2="{mt+ch}" stroke="#2B2D42"/>',
        f'<line x1="{ml}" y1="{mt}" x2="{ml}" y2="{mt+ch}" stroke="#2B2D42"/>',
        f'<text x="26" y="{mt+ch/2}" transform="rotate(-90 26 {mt+ch/2})" text-anchor="middle" font-size="14" fill="#343A40">{ylabel}</text>',
    ]
    for i, (label, value) in enumerate(zip(labels, values)):
        x = ml + i * step + (step - bar_w) / 2
        h = value / max_v * ch if max_v else 0
        y = mt + ch - h
        color = COLORS[i % len(COLORS)]
        parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w:.1f}" height="{h:.1f}" rx="6" fill="{color}"/>')
        parts.append(f'<text x="{x+bar_w/2:.1f}" y="{y-8:.1f}" text-anchor="middle" font-size="13" font-weight="700" fill="#1D1D2C">{fmt.format(value)}</text>')
        parts.append(f'<text x="{x+bar_w/2:.1f}" y="{height-88}" text-anchor="end" font-size="12" fill="#343A40" transform="rotate(-30 {x+bar_w/2:.1f} {height-88})">{label}</text>')
    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def svg_scatter(path: Path, rows: list[dict]) -> None:
    width, height = 980, 620
    ml, mr, mt, mb = 90, 45, 72, 78
    cw, ch = width - ml - mr, height - mt - mb
    cats = sorted({r["category"] for r in rows})
    color_map = {cat: COLORS[i % len(COLORS)] for i, cat in enumerate(cats)}
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#FCFCFF"/>',
        f'<text x="{width/2}" y="38" text-anchor="middle" font-size="24" font-weight="700" fill="#1D1D2C">전체 점수 vs 브랜드/카테고리 보정 점수</text>',
        f'<line x1="{ml}" y1="{mt+ch}" x2="{width-mr}" y2="{mt+ch}" stroke="#2B2D42"/>',
        f'<line x1="{ml}" y1="{mt}" x2="{ml}" y2="{mt+ch}" stroke="#2B2D42"/>',
        f'<line x1="{ml}" y1="{mt+ch}" x2="{width-mr}" y2="{mt}" stroke="#ADB5BD" stroke-dasharray="6 6"/>',
        f'<text x="{ml+cw/2}" y="{height-22}" text-anchor="middle" font-size="14" fill="#343A40">GroMong Score</text>',
        f'<text x="24" y="{mt+ch/2}" transform="rotate(-90 24 {mt+ch/2})" text-anchor="middle" font-size="14" fill="#343A40">보정 점수</text>',
    ]
    for row in rows:
        x_val = to_float(row["gromong_score"])
        y_val = to_float(row["calibrated_score"])
        x = ml + x_val / 100 * cw
        y = mt + ch - y_val / 100 * ch
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.4" fill="{color_map[row["category"]]}" fill-opacity="0.62"/>')
    legend_x = width - 245
    for i, cat in enumerate(cats):
        y = 68 + i * 24
        parts.append(f'<circle cx="{legend_x}" cy="{y}" r="6" fill="{color_map[cat]}"/>')
        parts.append(f'<text x="{legend_x+14}" y="{y+4}" font-size="13" fill="#343A40">{cat}</text>')
    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def svg_grouped(path: Path, title: str, labels: list[str], series: dict[str, list[float]], ylabel: str, fmt: str = "{:.1f}") -> None:
    width, height = 1050, 560
    ml, mr, mt, mb = 90, 45, 76, 105
    cw, ch = width - ml - mr, height - mt - mb
    max_v = max(v for vals in series.values() for v in vals) * 1.18
    group_w = cw / len(labels)
    keys = list(series)
    bar_w = group_w * 0.18
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#FBFBFE"/>',
        f'<text x="{width/2}" y="40" text-anchor="middle" font-size="24" font-weight="700" fill="#1D1D2C">{title}</text>',
        f'<line x1="{ml}" y1="{mt+ch}" x2="{width-mr}" y2="{mt+ch}" stroke="#2B2D42"/>',
        f'<line x1="{ml}" y1="{mt}" x2="{ml}" y2="{mt+ch}" stroke="#2B2D42"/>',
        f'<text x="24" y="{mt+ch/2}" transform="rotate(-90 24 {mt+ch/2})" text-anchor="middle" font-size="14" fill="#343A40">{ylabel}</text>',
    ]
    for i, label in enumerate(labels):
        base_x = ml + i * group_w + group_w * 0.22
        for j, key in enumerate(keys):
            value = series[key][i]
            h = value / max_v * ch if max_v else 0
            x = base_x + j * bar_w * 1.25
            y = mt + ch - h
            parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w:.1f}" height="{h:.1f}" rx="5" fill="{COLORS[j]}"/>')
            parts.append(f'<text x="{x+bar_w/2:.1f}" y="{y-6:.1f}" text-anchor="middle" font-size="11" font-weight="700" fill="#1D1D2C">{fmt.format(value)}</text>')
        parts.append(f'<text x="{ml+i*group_w+group_w/2:.1f}" y="{height-62}" text-anchor="middle" font-size="13" fill="#343A40">{label}</text>')
    lx = width - 280
    for j, key in enumerate(keys):
        x = lx + j * 92
        parts.append(f'<rect x="{x}" y="54" width="14" height="14" rx="3" fill="{COLORS[j]}"/>')
        parts.append(f'<text x="{x+20}" y="66" font-size="13" fill="#343A40">{key}</text>')
    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    CHART_DIR.mkdir(parents=True, exist_ok=True)

    rows = read_rows()
    brand_pct = percentile_ranks(rows, "brand")
    category_pct = percentile_ranks(rows, "category")
    overall_rank = dense_rank(rows, "gromong_score")

    enriched = []
    for row in rows:
        sid = row["platform_shop_id"]
        current = to_float(row["gromong_score"])
        b_pct = brand_pct[sid]
        c_pct = category_pct[sid]
        calibrated = 0.50 * current + 0.25 * b_pct + 0.25 * c_pct
        new_row = dict(row)
        new_row["brand_percentile_score"] = f"{b_pct:.4f}"
        new_row["category_percentile_score"] = f"{c_pct:.4f}"
        new_row["calibrated_score"] = f"{calibrated:.4f}"
        new_row["calibrated_grade"] = grade(calibrated)
        new_row["overall_rank"] = overall_rank[sid]
        enriched.append(new_row)

    cal_rank = dense_rank(enriched, "calibrated_score")
    brand_rank = dense_rank(enriched, "gromong_score", "brand")
    category_rank = dense_rank(enriched, "gromong_score", "category")
    for row in enriched:
        sid = row["platform_shop_id"]
        row["calibrated_rank"] = cal_rank[sid]
        row["brand_rank"] = brand_rank[sid]
        row["category_rank"] = category_rank[sid]
        row["rank_change"] = int(row["overall_rank"]) - int(row["calibrated_rank"])

    fields = list(enriched[0].keys())
    write_csv(OUT_DIR / "calibrated_store_scores.csv", enriched, fields)

    top_by_category = []
    for category in sorted({r["category"] for r in enriched}):
        items = [r for r in enriched if r["category"] == category]
        top_by_category.extend(sorted(items, key=lambda r: (-to_float(r["calibrated_score"]), r["platform_shop_id"]))[:10])
    write_csv(OUT_DIR / "category_top10_calibrated.csv", top_by_category, fields)

    top_by_brand = []
    for brand in sorted({r["brand"] for r in enriched}):
        items = [r for r in enriched if r["brand"] == brand]
        top_by_brand.extend(sorted(items, key=lambda r: (-to_float(r["calibrated_score"]), r["platform_shop_id"]))[:10])
    write_csv(OUT_DIR / "brand_top10_calibrated.csv", top_by_brand, fields)

    current_top100 = {r["platform_shop_id"] for r in sorted(enriched, key=lambda r: (int(r["overall_rank"]), r["platform_shop_id"]))[:100]}
    calibrated_top100 = {r["platform_shop_id"] for r in sorted(enriched, key=lambda r: (int(r["calibrated_rank"]), r["platform_shop_id"]))[:100]}
    overlap = len(current_top100 & calibrated_top100)

    summary_rows = []
    for category in sorted({r["category"] for r in enriched}):
        items = [r for r in enriched if r["category"] == category]
        summary_rows.append({
            "group_type": "category",
            "group_name": category,
            "store_count": len(items),
            "avg_gromong_score": f"{mean(to_float(r['gromong_score']) for r in items):.4f}",
            "avg_calibrated_score": f"{mean(to_float(r['calibrated_score']) for r in items):.4f}",
            "current_A_count": sum(1 for r in items if r["grade"] == "A"),
            "calibrated_A_count": sum(1 for r in items if r["calibrated_grade"] == "A"),
            "current_top100_count": sum(1 for r in items if r["platform_shop_id"] in current_top100),
            "calibrated_top100_count": sum(1 for r in items if r["platform_shop_id"] in calibrated_top100),
        })
    for brand in sorted({r["brand"] for r in enriched}):
        items = [r for r in enriched if r["brand"] == brand]
        summary_rows.append({
            "group_type": "brand",
            "group_name": brand,
            "store_count": len(items),
            "avg_gromong_score": f"{mean(to_float(r['gromong_score']) for r in items):.4f}",
            "avg_calibrated_score": f"{mean(to_float(r['calibrated_score']) for r in items):.4f}",
            "current_A_count": sum(1 for r in items if r["grade"] == "A"),
            "calibrated_A_count": sum(1 for r in items if r["calibrated_grade"] == "A"),
            "current_top100_count": sum(1 for r in items if r["platform_shop_id"] in current_top100),
            "calibrated_top100_count": sum(1 for r in items if r["platform_shop_id"] in calibrated_top100),
        })
    write_csv(OUT_DIR / "calibration_group_summary.csv", summary_rows, list(summary_rows[0].keys()))

    comparison = [{
        "current_top100_count": 100,
        "calibrated_top100_count": 100,
        "overlap_count": overlap,
        "overlap_rate": f"{overlap / 100:.4f}",
        "new_entry_count": 100 - overlap,
    }]
    write_csv(OUT_DIR / "top100_calibration_overlap.csv", comparison, list(comparison[0].keys()))

    # Charts
    svg_scatter(CHART_DIR / "overall_vs_calibrated_score.svg", enriched)

    cat_labels = [r["group_name"] for r in summary_rows if r["group_type"] == "category"]
    cat_rows = [r for r in summary_rows if r["group_type"] == "category"]
    svg_grouped(
        CHART_DIR / "category_top100_counts_before_after.svg",
        "카테고리별 Top100 포함 매장 수 변화",
        cat_labels,
        {
            "기존": [float(r["current_top100_count"]) for r in cat_rows],
            "보정": [float(r["calibrated_top100_count"]) for r in cat_rows],
        },
        "Top100 매장 수",
        "{:.0f}",
    )
    svg_grouped(
        CHART_DIR / "category_avg_score_before_after.svg",
        "카테고리별 평균 점수 변화",
        cat_labels,
        {
            "기존": [float(r["avg_gromong_score"]) for r in cat_rows],
            "보정": [float(r["avg_calibrated_score"]) for r in cat_rows],
        },
        "평균 점수",
        "{:.1f}",
    )
    brand_rows = [r for r in summary_rows if r["group_type"] == "brand"]
    svg_grouped(
        CHART_DIR / "brand_A_counts_before_after.svg",
        "브랜드별 A등급 매장 수 변화",
        [r["group_name"] for r in brand_rows],
        {
            "기존": [float(r["current_A_count"]) for r in brand_rows],
            "보정": [float(r["calibrated_A_count"]) for r in brand_rows],
        },
        "A등급 매장 수",
        "{:.0f}",
    )
    svg_bar(
        CHART_DIR / "top100_overlap_after_calibration.svg",
        "기존 Top100과 보정 Top100 겹침",
        ["겹침", "신규 진입"],
        [overlap, 100 - overlap],
        "매장 수",
        "{:.0f}",
    )
    svg_bar(
        CHART_DIR / "category_top10_calibrated_scores.svg",
        "카테고리별 보정 점수 Top 후보",
        [f"{r['category']} {r['category_rank']}위" for r in top_by_category[:30]],
        [to_float(r["calibrated_score"]) for r in top_by_category[:30]],
        "보정 점수",
        "{:.1f}",
    )

    report = [
        "# Calibrated Score Report",
        "",
        "## 목적",
        "",
        "제공 데이터가 본그룹과 굽네치킨 중심이라는 한계를 방어하기 위해 전체 순위와 별도로 브랜드/카테고리 내부 상대 순위를 반영한 보정 점수를 생성했다.",
        "",
        "## 보정 공식",
        "",
        "```text",
        "calibrated_score = 0.50 * GroMong Score + 0.25 * 브랜드 내부 percentile + 0.25 * 카테고리 내부 percentile",
        "```",
        "",
        "## 핵심 결과",
        "",
        f"- 기존 Top100과 보정 Top100 겹침: {overlap}개",
        f"- 보정으로 새로 Top100에 진입한 매장: {100 - overlap}개",
        "",
        "## 그룹별 변화",
        "",
    ]
    for row in summary_rows:
        report.append(
            f"- {row['group_type']} {row['group_name']}: 기존 Top100 {row['current_top100_count']}개, "
            f"보정 Top100 {row['calibrated_top100_count']}개, 기존 A등급 {row['current_A_count']}개, "
            f"보정 A등급 {row['calibrated_A_count']}개"
        )
    report.extend([
        "",
        "## 발표 해석",
        "",
        "전체 점수는 유지하되, 같은 브랜드와 같은 카테고리 안에서 상대적으로 우수한 매장을 함께 반영했다.",
        "따라서 특정 브랜드/카테고리 편중 문제를 숨기지 않고, 제한된 데이터 안에서 더 공정한 후보군을 제시할 수 있다.",
    ])
    (OUT_DIR / "calibrated_score_report.md").write_text("\n".join(report), encoding="utf-8")

    print("WROTE", OUT_DIR)
    print("top100 overlap", overlap)
    for row in summary_rows:
        print(row["group_type"], row["group_name"], row["current_top100_count"], row["calibrated_top100_count"], row["current_A_count"], row["calibrated_A_count"])


if __name__ == "__main__":
    main()
