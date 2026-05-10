from pathlib import Path

import pandas as pd


SCORE_PATH = Path("analysis_outputs/scoring/store_score_explanations.csv")
CHART_DIR = Path("analysis_outputs/scoring/charts")
CHART_DIR.mkdir(parents=True, exist_ok=True)

COLORS = {
    "blue": "#2563eb",
    "green": "#16a34a",
    "orange": "#f97316",
    "red": "#dc2626",
    "purple": "#7c3aed",
    "gray": "#64748b",
    "light": "#e2e8f0",
    "text": "#0f172a",
}


def bar_chart(path, title, labels, values, color=COLORS["blue"], width=1000, height=500):
    max_value = max(values) if values else 1
    max_value = max(max_value, 1)
    margin = {"top": 70, "right": 40, "bottom": 130, "left": 90}
    plot_w = width - margin["left"] - margin["right"]
    plot_h = height - margin["top"] - margin["bottom"]
    gap = 14
    bar_w = max(10, (plot_w - gap * (len(values) - 1)) / len(values))
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="{width/2}" y="34" text-anchor="middle" font-family="Arial" font-size="22" font-weight="700" fill="{COLORS["text"]}">{title}</text>',
        f'<line x1="{margin["left"]}" y1="{height-margin["bottom"]}" x2="{width-margin["right"]}" y2="{height-margin["bottom"]}" stroke="{COLORS["light"]}" stroke-width="2"/>',
    ]
    for i, (label, value) in enumerate(zip(labels, values)):
        x = margin["left"] + i * (bar_w + gap)
        h = plot_h * value / max_value
        y = height - margin["bottom"] - h
        lines.append(f'<rect x="{x:.2f}" y="{y:.2f}" width="{bar_w:.2f}" height="{h:.2f}" fill="{color}" rx="4"/>')
        lines.append(f'<text x="{x+bar_w/2:.2f}" y="{y-8:.2f}" text-anchor="middle" font-family="Arial" font-size="12" fill="{COLORS["text"]}">{value:,.1f}</text>')
        lines.append(f'<text x="{x+bar_w/2:.2f}" y="{height-margin["bottom"]+24}" text-anchor="middle" font-family="Arial" font-size="12" fill="{COLORS["text"]}">{label}</text>')
    lines.append("</svg>")
    path.write_text("\n".join(lines), encoding="utf-8")


def histogram(path, title, values, bins, width=1000, height=500):
    counts = []
    labels = []
    for lo, hi in zip(bins[:-1], bins[1:]):
        counts.append(int(((values >= lo) & (values < hi)).sum()))
        labels.append(f"{lo}-{hi}")
    counts[-1] += int((values == bins[-1]).sum())
    bar_chart(path, title, labels, counts, COLORS["purple"], width, height)


def scatter(path, title, x, y, labels=None, width=900, height=600):
    margin = {"top": 70, "right": 50, "bottom": 80, "left": 90}
    plot_w = width - margin["left"] - margin["right"]
    plot_h = height - margin["top"] - margin["bottom"]
    x_min, x_max = x.quantile(0.02), x.quantile(0.98)
    y_min, y_max = y.quantile(0.02), y.quantile(0.98)
    if x_min == x_max:
        x_max += 1
    if y_min == y_max:
        y_max += 1

    def sx(v):
        v = min(max(v, x_min), x_max)
        return margin["left"] + (v - x_min) / (x_max - x_min) * plot_w

    def sy(v):
        v = min(max(v, y_min), y_max)
        return margin["top"] + plot_h - (v - y_min) / (y_max - y_min) * plot_h

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="{width/2}" y="34" text-anchor="middle" font-family="Arial" font-size="22" font-weight="700" fill="{COLORS["text"]}">{title}</text>',
        f'<line x1="{margin["left"]}" y1="{height-margin["bottom"]}" x2="{width-margin["right"]}" y2="{height-margin["bottom"]}" stroke="{COLORS["light"]}" stroke-width="2"/>',
        f'<line x1="{margin["left"]}" y1="{margin["top"]}" x2="{margin["left"]}" y2="{height-margin["bottom"]}" stroke="{COLORS["light"]}" stroke-width="2"/>',
        f'<text x="{margin["left"]}" y="{height-30}" font-family="Arial" font-size="13" fill="{COLORS["text"]}">x: {x.name}</text>',
        f'<text x="{margin["left"]}" y="{height-12}" font-family="Arial" font-size="13" fill="{COLORS["text"]}">y: {y.name}</text>',
    ]
    for xv, yv in zip(x, y):
        if pd.notna(xv) and pd.notna(yv):
            lines.append(f'<circle cx="{sx(float(xv)):.2f}" cy="{sy(float(yv)):.2f}" r="4" fill="{COLORS["blue"]}" opacity="0.45"/>')
    lines.append("</svg>")
    path.write_text("\n".join(lines), encoding="utf-8")


def main():
    df = pd.read_csv(SCORE_PATH, encoding="utf-8-sig")

    histogram(
        CHART_DIR / "score_distribution.svg",
        "GroMong Score Distribution",
        df["gromong_score"],
        [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
    )

    grade_counts = df["grade"].value_counts().reindex(["A", "B", "C", "D"]).fillna(0)
    bar_chart(CHART_DIR / "grade_counts.svg", "Store Count by Grade", grade_counts.index.tolist(), grade_counts.tolist(), COLORS["green"])

    brand = df.groupby("brand")["gromong_score"].mean().sort_values(ascending=False)
    bar_chart(CHART_DIR / "brand_avg_score.svg", "Average Score by Brand", brand.index.tolist(), brand.round(2).tolist(), COLORS["blue"])

    cat = df.groupby("category")["gromong_score"].mean().sort_values(ascending=False)
    bar_chart(CHART_DIR / "category_avg_score.svg", "Average Score by Category", cat.index.tolist(), cat.round(2).tolist(), COLORS["orange"])

    scatter(
        CHART_DIR / "growth_alpha_vs_score.svg",
        "Historical Growth Alpha vs GroMong Score",
        df["historical_internal_growth_alpha"].rename("historical_internal_growth_alpha"),
        df["gromong_score"].rename("gromong_score"),
    )

    seoul = df[df["is_seoul_external"] == 1]
    if not seoul.empty:
        scatter(
            CHART_DIR / "seoul_market_ticket_ratio_vs_score.svg",
            "Seoul Store-vs-Market Ticket Ratio vs Score",
            seoul["store_vs_market_ticket_ratio"].rename("store_vs_market_ticket_ratio"),
            seoul["gromong_score"].rename("gromong_score"),
        )

    top20 = df.sort_values("gromong_score", ascending=False).head(20).copy()
    top20["label"] = top20["platform_shop_id"].astype(str)
    bar_chart(
        CHART_DIR / "top20_store_scores.svg",
        "Top 20 Store Scores",
        top20["label"].tolist(),
        top20["gromong_score"].tolist(),
        COLORS["red"],
        width=1300,
        height=560,
    )

    print(f"WROTE {CHART_DIR}")


if __name__ == "__main__":
    main()
