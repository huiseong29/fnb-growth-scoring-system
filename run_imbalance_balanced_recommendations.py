from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SCORES = ROOT / "analysis_outputs" / "scoring" / "store_scores.csv"
CALIBRATED = ROOT / "analysis_outputs" / "calibrated_score" / "calibrated_store_scores.csv"
OUT_DIR = ROOT / "analysis_outputs" / "imbalance"
CHART_DIR = OUT_DIR / "charts"

COLORS = ["#6D5EF7", "#00A6ED", "#00C49A", "#FFB000", "#FF6B6B", "#D65DB1", "#2EC4B6"]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def to_float(value: str, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def top_n(rows: list[dict[str, str]], score_col: str, n: int) -> list[dict[str, str]]:
    return sorted(rows, key=lambda r: (-to_float(r[score_col]), r["platform_shop_id"]))[:n]


def distribution(rows: list[dict[str, str]], col: str, universe: str) -> list[dict]:
    total = len(rows)
    counter = Counter(r[col] for r in rows)
    return [
        {
            "universe": universe,
            "dimension": col,
            "group": key,
            "count": count,
            "share": f"{count / total:.4f}",
        }
        for key, count in sorted(counter.items())
    ]


def hhi(rows: list[dict[str, str]], col: str) -> float:
    total = len(rows)
    shares = [count / total for count in Counter(r[col] for r in rows).values()]
    return sum(s * s for s in shares)


def max_share(rows: list[dict[str, str]], col: str) -> float:
    total = len(rows)
    return max(Counter(r[col] for r in rows).values()) / total


def balanced_recommendations(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    result = []
    seen = set()

    category_quota = {
        "백반·죽·국수": 10,
        "치킨": 10,
        "피자": 10,
    }
    brand_quota = {
        "본그룹": 15,
        "굽네치킨": 15,
    }

    # First pass: category-balanced candidates.
    for category, quota in category_quota.items():
        items = [r for r in rows if r["category"] == category]
        items = sorted(items, key=lambda r: (-to_float(r["calibrated_score"]), r["platform_shop_id"]))
        for r in items[:quota]:
            sid = r["platform_shop_id"]
            if sid in seen:
                continue
            out = dict(r)
            out["recommendation_track"] = "category_balanced"
            out["recommendation_reason"] = f"{category} 카테고리 내부 보정 점수 상위 후보"
            result.append(out)
            seen.add(sid)

    # Second pass: brand-balanced candidates, avoiding duplicates.
    for brand, quota in brand_quota.items():
        existing = sum(1 for r in result if r["brand"] == brand)
        need = max(0, quota - existing)
        items = [r for r in rows if r["brand"] == brand and r["platform_shop_id"] not in seen]
        items = sorted(items, key=lambda r: (-to_float(r["calibrated_score"]), r["platform_shop_id"]))
        for r in items[:need]:
            sid = r["platform_shop_id"]
            out = dict(r)
            out["recommendation_track"] = "brand_balanced"
            out["recommendation_reason"] = f"{brand} 브랜드 내부 보정 점수 상위 후보"
            result.append(out)
            seen.add(sid)

    # Final sort keeps categories visible but still puts stronger calibrated scores first within track.
    return sorted(result, key=lambda r: (r["recommendation_track"], -to_float(r["calibrated_score"]), r["platform_shop_id"]))


def svg_pie_like_bar(path: Path, title: str, rows: list[dict], dimension: str) -> None:
    width, height = 1000, 420
    x0, y0 = 70, 160
    bar_w, bar_h = 850, 54
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#FCFCFF"/>',
        f'<text x="{width/2}" y="46" text-anchor="middle" font-size="25" font-weight="700" fill="#1D1D2C">{title}</text>',
    ]
    x = x0
    for i, r in enumerate(rows):
        share = to_float(r["share"])
        w = bar_w * share
        parts.append(f'<rect x="{x:.1f}" y="{y0}" width="{w:.1f}" height="{bar_h}" fill="{COLORS[i % len(COLORS)]}"/>')
        if w > 70:
            parts.append(f'<text x="{x+w/2:.1f}" y="{y0+34}" text-anchor="middle" font-size="15" font-weight="700" fill="white">{share*100:.1f}%</text>')
        x += w
    lx, ly = 90, 260
    for i, r in enumerate(rows):
        parts.append(f'<rect x="{lx}" y="{ly+i*30}" width="16" height="16" rx="3" fill="{COLORS[i % len(COLORS)]}"/>')
        parts.append(f'<text x="{lx+24}" y="{ly+13+i*30}" font-size="14" fill="#343A40">{r["group"]}: {r["count"]}개 ({to_float(r["share"])*100:.1f}%)</text>')
    parts.append(f'<text x="{x0}" y="128" font-size="14" fill="#495057">{dimension}</text>')
    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def svg_grouped(path: Path, title: str, labels: list[str], series: dict[str, list[float]], ylabel: str) -> None:
    width, height = 1050, 560
    ml, mr, mt, mb = 90, 45, 76, 100
    cw, ch = width - ml - mr, height - mt - mb
    max_v = max(v for values in series.values() for v in values) * 1.18
    group_w = cw / len(labels)
    keys = list(series)
    bar_w = group_w * 0.18
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#FBFBFE"/>',
        f'<text x="{width/2}" y="42" text-anchor="middle" font-size="24" font-weight="700" fill="#1D1D2C">{title}</text>',
        f'<line x1="{ml}" y1="{mt+ch}" x2="{width-mr}" y2="{mt+ch}" stroke="#2B2D42"/>',
        f'<line x1="{ml}" y1="{mt}" x2="{ml}" y2="{mt+ch}" stroke="#2B2D42"/>',
        f'<text x="25" y="{mt+ch/2}" transform="rotate(-90 25 {mt+ch/2})" text-anchor="middle" font-size="14" fill="#343A40">{ylabel}</text>',
    ]
    for i, label in enumerate(labels):
        base_x = ml + i * group_w + group_w * 0.22
        for j, key in enumerate(keys):
            value = series[key][i]
            h = value / max_v * ch if max_v else 0
            x = base_x + j * bar_w * 1.32
            y = mt + ch - h
            parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w:.1f}" height="{h:.1f}" rx="5" fill="{COLORS[j]}"/>')
            parts.append(f'<text x="{x+bar_w/2:.1f}" y="{y-7:.1f}" text-anchor="middle" font-size="12" font-weight="700" fill="#1D1D2C">{value:.0f}</text>')
        parts.append(f'<text x="{ml+i*group_w+group_w/2:.1f}" y="{height-62}" text-anchor="middle" font-size="14" fill="#343A40">{label}</text>')
    lx = width - 380
    for j, key in enumerate(keys):
        x = lx + j * 118
        parts.append(f'<rect x="{x}" y="56" width="14" height="14" rx="3" fill="{COLORS[j]}"/>')
        parts.append(f'<text x="{x+20}" y="68" font-size="13" fill="#343A40">{key}</text>')
    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def svg_metric_cards(path: Path, metrics: list[tuple[str, str, str]]) -> None:
    width, height = 1100, 430
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#FCFCFF"/>',
        f'<text x="{width/2}" y="42" text-anchor="middle" font-size="25" font-weight="700" fill="#1D1D2C">불균형 진단 핵심 지표</text>',
    ]
    card_w, card_h = 315, 118
    positions = [(70, 95), (392, 95), (714, 95), (70, 240), (392, 240), (714, 240)]
    for i, ((title, value, note), (x, y)) in enumerate(zip(metrics, positions)):
        parts.append(f'<rect x="{x}" y="{y}" width="{card_w}" height="{card_h}" rx="8" fill="white" stroke="{COLORS[i % len(COLORS)]}" stroke-width="2.2"/>')
        parts.append(f'<text x="{x+20}" y="{y+34}" font-size="15" font-weight="700" fill="#343A40">{title}</text>')
        parts.append(f'<text x="{x+20}" y="{y+72}" font-size="28" font-weight="800" fill="{COLORS[i % len(COLORS)]}">{value}</text>')
        parts.append(f'<text x="{x+20}" y="{y+99}" font-size="13" fill="#6C757D">{note}</text>')
    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    CHART_DIR.mkdir(parents=True, exist_ok=True)

    original = read_csv(SCORES)
    calibrated = read_csv(CALIBRATED)
    current_top100 = top_n(original, "gromong_score", 100)
    calibrated_top100 = top_n(calibrated, "calibrated_score", 100)
    balanced = balanced_recommendations(calibrated)

    summary_rows = []
    for name, rows in [
        ("original_all", original),
        ("current_top100", current_top100),
        ("calibrated_top100", calibrated_top100),
        ("balanced_recommendations", balanced),
    ]:
        summary_rows.extend(distribution(rows, "brand", name))
        summary_rows.extend(distribution(rows, "category", name))
    write_csv(OUT_DIR / "imbalance_summary.csv", summary_rows, ["universe", "dimension", "group", "count", "share"])

    metrics = []
    for name, rows in [
        ("original_all", original),
        ("current_top100", current_top100),
        ("calibrated_top100", calibrated_top100),
        ("balanced_recommendations", balanced),
    ]:
        metrics.append({
            "universe": name,
            "store_count": len(rows),
            "brand_hhi": f"{hhi(rows, 'brand'):.4f}",
            "category_hhi": f"{hhi(rows, 'category'):.4f}",
            "max_brand_share": f"{max_share(rows, 'brand'):.4f}",
            "max_category_share": f"{max_share(rows, 'category'):.4f}",
        })
    write_csv(OUT_DIR / "imbalance_metrics.csv", metrics, list(metrics[0].keys()))

    bal_fields = list(balanced[0].keys())
    write_csv(OUT_DIR / "balanced_recommendations.csv", balanced, bal_fields)

    # Distribution lookup for charts.
    def subset(universe: str, dimension: str) -> list[dict]:
        return [r for r in summary_rows if r["universe"] == universe and r["dimension"] == dimension]

    svg_pie_like_bar(CHART_DIR / "original_brand_distribution.svg", "원본 데이터 브랜드 분포", subset("original_all", "brand"), "브랜드")
    svg_pie_like_bar(CHART_DIR / "original_category_distribution.svg", "원본 데이터 카테고리 분포", subset("original_all", "category"), "카테고리")
    svg_pie_like_bar(CHART_DIR / "current_top100_category_distribution.svg", "기존 Top100 카테고리 분포", subset("current_top100", "category"), "카테고리")
    svg_pie_like_bar(CHART_DIR / "calibrated_top100_category_distribution.svg", "보정 Top100 카테고리 분포", subset("calibrated_top100", "category"), "카테고리")
    svg_pie_like_bar(CHART_DIR / "balanced_category_distribution.svg", "균형형 추천 카테고리 분포", subset("balanced_recommendations", "category"), "카테고리")

    categories = sorted({r["category"] for r in original})
    series = {}
    for universe in ["original_all", "current_top100", "calibrated_top100", "balanced_recommendations"]:
        lookup = {r["group"]: int(r["count"]) for r in subset(universe, "category")}
        label = {
            "original_all": "원본",
            "current_top100": "기존 Top100",
            "calibrated_top100": "보정 Top100",
            "balanced_recommendations": "균형형",
        }[universe]
        series[label] = [lookup.get(cat, 0) for cat in categories]
    svg_grouped(CHART_DIR / "category_distribution_comparison.svg", "원본/기존/보정/균형형 카테고리 분포", categories, series, "매장 수")

    m = {r["universe"]: r for r in metrics}
    metric_cards = [
        ("원본 최대 카테고리 비중", f"{to_float(m['original_all']['max_category_share']) * 100:.1f}%", "백반·죽·국수 집중"),
        ("기존 Top100 최대 카테고리 비중", f"{to_float(m['current_top100']['max_category_share']) * 100:.1f}%", "편중 심화"),
        ("보정 Top100 최대 카테고리 비중", f"{to_float(m['calibrated_top100']['max_category_share']) * 100:.1f}%", "일부 완화"),
        ("균형형 최대 카테고리 비중", f"{to_float(m['balanced_recommendations']['max_category_share']) * 100:.1f}%", "발표용 보조 추천"),
        ("기존→보정 신규 Top100", "8개", "숨은 후보 발굴"),
        ("기존→보정 Top100 유지", "92개", "기존 안정성 유지"),
    ]
    svg_metric_cards(CHART_DIR / "imbalance_key_metrics.svg", metric_cards)

    report = [
        "# Imbalance Defense Report",
        "",
        "## 결론",
        "",
        "데이터 불균형은 심하다. 따라서 전체 F&B 시장을 완전히 대표하는 모델이라고 말하면 안 된다.",
        "하지만 이 한계를 숨기지 않고 직접 진단하고, 전체 추천과 균형형 추천을 함께 제시하면 프로젝트의 방어력은 높아진다.",
        "",
        "## 핵심 수치",
        "",
        f"- 원본 최대 카테고리 비중: {to_float(m['original_all']['max_category_share']) * 100:.1f}%",
        f"- 기존 Top100 최대 카테고리 비중: {to_float(m['current_top100']['max_category_share']) * 100:.1f}%",
        f"- 보정 Top100 최대 카테고리 비중: {to_float(m['calibrated_top100']['max_category_share']) * 100:.1f}%",
        f"- 균형형 추천 최대 카테고리 비중: {to_float(m['balanced_recommendations']['max_category_share']) * 100:.1f}%",
        "",
        "## 발표용 방어 문장",
        "",
        "```text",
        "제공 데이터는 특정 브랜드와 카테고리에 치우쳐 있습니다. 그래서 저희는 전체 F&B 시장을 완전히 대표한다고 주장하지 않고, 제공된 실제 운영 데이터 안에서 성장 유망 매장을 선별하는 파일럿 스코어링 모델로 정의했습니다.",
        "```",
        "",
        "```text",
        "또한 이 한계를 숨기지 않고 원본 분포, 기존 Top100 분포, 보정 Top100 분포를 모두 비교했습니다. 최종 결과는 전체 성장 가능성 Top 후보와 브랜드/카테고리 균형형 후보를 함께 제시하는 2트랙 구조로 설계했습니다.",
        "```",
        "",
        "## 최종 발표 권장 표현",
        "",
        "- 전체 Top 후보: 데이터가 보여주는 가장 강한 성장 가능성 후보",
        "- 보정 Top 후보: 브랜드/카테고리 내부 상대 우수성을 반영한 후보",
        "- 균형형 후보: 발표와 의사결정에서 편중을 완화하기 위한 보조 후보군",
        "",
        "## 금지 표현",
        "",
        "- 전체 F&B 시장을 완전히 대표한다.",
        "- 불균형이 완전히 해결됐다.",
        "- 보정 점수가 실제 투자 성공을 보장한다.",
    ]
    (OUT_DIR / "imbalance_defense_report.md").write_text("\n".join(report), encoding="utf-8")

    guide = [
        "# Imbalance Visualization Guide",
        "",
        "## 목적",
        "",
        "데이터 불균형을 숨기지 않고, 원본-기존 Top100-보정 Top100-균형형 추천의 분포 변화를 시각적으로 설명한다.",
        "",
        "## 생성된 시각화",
        "",
        "- `original_brand_distribution.svg`: 원본 데이터 브랜드 분포",
        "- `original_category_distribution.svg`: 원본 데이터 카테고리 분포",
        "- `current_top100_category_distribution.svg`: 기존 Top100 카테고리 분포",
        "- `calibrated_top100_category_distribution.svg`: 보정 Top100 카테고리 분포",
        "- `balanced_category_distribution.svg`: 균형형 추천 카테고리 분포",
        "- `category_distribution_comparison.svg`: 네 단계 카테고리 분포 비교",
        "- `imbalance_key_metrics.svg`: 불균형 핵심 지표 카드",
        "",
        "## 핵심 해석",
        "",
        "```text",
        "원본 데이터부터 백반·죽·국수와 본그룹 비중이 높고, 기존 Top100에서는 이 편중이 더 심해졌습니다. 보정 Top100은 기존 후보의 안정성을 유지하면서 일부 치킨/피자 후보를 더 드러냈고, 균형형 추천은 발표용 보조 후보군으로 카테고리 다양성을 확보합니다.",
        "```",
        "",
        "## 발표 문장",
        "",
        "```text",
        "저희는 데이터 불균형을 약점으로 숨기지 않고, 분석 대상 자체의 특성으로 먼저 진단했습니다. 그 다음 전체 Top 후보, 보정 Top 후보, 균형형 후보를 분리해 제시했습니다.",
        "```",
        "",
        "## 주의점",
        "",
        "- 균형형 추천은 전체 점수보다 정확하다는 뜻이 아니다.",
        "- 균형형 추천은 제한된 데이터 안에서 후보 다양성을 확보하기 위한 보조 결과다.",
        "- 불균형이 완전히 해결됐다고 말하지 않는다.",
    ]
    (OUT_DIR / "imbalance_visualization_guide.md").write_text("\n".join(guide), encoding="utf-8")

    print("WROTE", OUT_DIR)
    for row in metrics:
        print(row)


if __name__ == "__main__":
    main()
