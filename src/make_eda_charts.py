from pathlib import Path

import pandas as pd


EDA_DIR = Path("analysis_outputs/eda")
CHART_DIR = EDA_DIR / "charts"
CHART_DIR.mkdir(parents=True, exist_ok=True)


COLORS = {
    "blue": "#2563eb",
    "green": "#16a34a",
    "orange": "#f97316",
    "red": "#dc2626",
    "gray": "#64748b",
    "light": "#e2e8f0",
    "text": "#0f172a",
}


def svg_bar_chart(path, title, labels, values, color=COLORS["blue"], width=900, height=460):
    max_value = max(values) if values else 1
    max_value = max_value if max_value > 0 else 1
    margin = {"top": 70, "right": 40, "bottom": 120, "left": 90}
    plot_w = width - margin["left"] - margin["right"]
    plot_h = height - margin["top"] - margin["bottom"]
    bar_gap = 18
    bar_w = max(20, (plot_w - bar_gap * (len(values) - 1)) / len(values))
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f'<rect width="{width}" height="{height}" fill="white"/>',
        f'<text x="{width/2}" y="34" text-anchor="middle" font-family="Arial" font-size="22" font-weight="700" fill="{COLORS["text"]}">{title}</text>',
        f'<line x1="{margin["left"]}" y1="{height-margin["bottom"]}" x2="{width-margin["right"]}" y2="{height-margin["bottom"]}" stroke="{COLORS["light"]}" stroke-width="2"/>',
    ]
    for i, (label, value) in enumerate(zip(labels, values)):
        x = margin["left"] + i * (bar_w + bar_gap)
        h = plot_h * value / max_value
        y = height - margin["bottom"] - h
        lines.append(f'<rect x="{x:.2f}" y="{y:.2f}" width="{bar_w:.2f}" height="{h:.2f}" fill="{color}" rx="4"/>')
        lines.append(f'<text x="{x+bar_w/2:.2f}" y="{y-8:.2f}" text-anchor="middle" font-family="Arial" font-size="14" fill="{COLORS["text"]}">{value:,.2f}</text>')
        lines.append(f'<text x="{x+bar_w/2:.2f}" y="{height-margin["bottom"]+24}" text-anchor="middle" font-family="Arial" font-size="13" fill="{COLORS["text"]}">{label}</text>')
    lines.append("</svg>")
    path.write_text("\n".join(lines), encoding="utf-8")


def svg_line_chart(path, title, series, width=1000, height=480):
    margin = {"top": 70, "right": 80, "bottom": 70, "left": 90}
    plot_w = width - margin["left"] - margin["right"]
    plot_h = height - margin["top"] - margin["bottom"]
    xs = sorted({x for points in series.values() for x, _ in points})
    vals = [v for points in series.values() for _, v in points]
    min_v = min(vals) if vals else 0
    max_v = max(vals) if vals else 1
    if min_v == max_v:
        max_v += 1
    x_pos = {x: margin["left"] + i * plot_w / max(1, len(xs) - 1) for i, x in enumerate(xs)}

    def y_pos(v):
        return margin["top"] + plot_h - (v - min_v) / (max_v - min_v) * plot_h

    palette = [COLORS["blue"], COLORS["orange"], COLORS["green"], COLORS["red"]]
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f'<rect width="{width}" height="{height}" fill="white"/>',
        f'<text x="{width/2}" y="34" text-anchor="middle" font-family="Arial" font-size="22" font-weight="700" fill="{COLORS["text"]}">{title}</text>',
        f'<line x1="{margin["left"]}" y1="{height-margin["bottom"]}" x2="{width-margin["right"]}" y2="{height-margin["bottom"]}" stroke="{COLORS["light"]}" stroke-width="2"/>',
        f'<line x1="{margin["left"]}" y1="{margin["top"]}" x2="{margin["left"]}" y2="{height-margin["bottom"]}" stroke="{COLORS["light"]}" stroke-width="2"/>',
    ]
    for i, x in enumerate(xs):
        if i % 2 == 0 or len(xs) <= 9:
            lines.append(f'<text x="{x_pos[x]:.2f}" y="{height-margin["bottom"]+28}" text-anchor="middle" font-family="Arial" font-size="12" fill="{COLORS["text"]}">{x}</text>')

    for idx, (name, points) in enumerate(series.items()):
        color = palette[idx % len(palette)]
        d = " ".join([f'{x_pos[x]:.2f},{y_pos(v):.2f}' for x, v in points])
        lines.append(f'<polyline points="{d}" fill="none" stroke="{color}" stroke-width="3"/>')
        for x, v in points:
            lines.append(f'<circle cx="{x_pos[x]:.2f}" cy="{y_pos(v):.2f}" r="4" fill="{color}"/>')
        lx = width - margin["right"] - 120
        ly = margin["top"] + idx * 24
        lines.append(f'<rect x="{lx}" y="{ly-10}" width="14" height="14" fill="{color}"/>')
        lines.append(f'<text x="{lx+22}" y="{ly+2}" font-family="Arial" font-size="14" fill="{COLORS["text"]}">{name}</text>')
    lines.append("</svg>")
    path.write_text("\n".join(lines), encoding="utf-8")


def main():
    label = pd.read_csv(EDA_DIR / "eda_label_summary.csv")
    pivot = label.pivot(index="metric", columns="growth_label_top30", values="mean")

    svg_bar_chart(
        CHART_DIR / "label_avg_order_count.svg",
        "Average Monthly Orders by Growth Label",
        ["Non-growth", "Growth"],
        [pivot.loc["order_count", 0], pivot.loc["order_count", 1]],
        COLORS["blue"],
    )
    svg_bar_chart(
        CHART_DIR / "label_avg_review_count.svg",
        "Average Monthly Reviews by Growth Label",
        ["Non-growth", "Growth"],
        [pivot.loc["review_count", 0], pivot.loc["review_count", 1]],
        COLORS["green"],
    )
    svg_bar_chart(
        CHART_DIR / "label_avg_reply_rate.svg",
        "Average Reply Rate by Growth Label",
        ["Non-growth", "Growth"],
        [pivot.loc["reply_rate", 0], pivot.loc["reply_rate", 1]],
        COLORS["orange"],
    )
    svg_bar_chart(
        CHART_DIR / "label_avg_growth_alpha.svg",
        "Outcome Growth Alpha by Growth Label",
        ["Non-growth", "Growth"],
        [pivot.loc["internal_growth_alpha", 0], pivot.loc["internal_growth_alpha", 1]],
        COLORS["red"],
    )

    brand_cat = pd.read_csv(EDA_DIR / "eda_brand_category_summary.csv")
    labels = [f"{r.brand}/{r.category}" for r in brand_cat.itertuples()]
    values = [r.growth_rate * 100 for r in brand_cat.itertuples()]
    svg_bar_chart(
        CHART_DIR / "brand_category_growth_rate.svg",
        "Growth Label Rate by Brand and Category (%)",
        labels,
        values,
        COLORS["blue"],
        width=1000,
    )

    trend = pd.read_csv(EDA_DIR / "eda_monthly_trend.csv")
    series = {}
    for label_value, name in [(0, "Non-growth"), (1, "Growth")]:
        g = trend[trend["growth_label_top30"] == label_value]
        series[name] = list(zip(g["year_month"], g["avg_order_count"]))
    svg_line_chart(CHART_DIR / "monthly_avg_orders_by_label.svg", "Average Monthly Orders Trend", series)

    print(f"WROTE {CHART_DIR}")


if __name__ == "__main__":
    main()
