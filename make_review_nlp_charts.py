from pathlib import Path

import pandas as pd


NLP_DIR = Path("analysis_outputs/nlp")
CHART_DIR = NLP_DIR / "charts"
CHART_DIR.mkdir(parents=True, exist_ok=True)

COLORS = {
    "purple": "#7c3aed",
    "blue": "#2563eb",
    "green": "#16a34a",
    "orange": "#f97316",
    "red": "#dc2626",
    "pink": "#db2777",
    "cyan": "#0891b2",
    "yellow": "#ca8a04",
    "gray": "#64748b",
    "light": "#e2e8f0",
    "text": "#0f172a",
}


def bar_chart(path, title, labels, values, colors=None, width=1100, height=540):
    if colors is None:
        palette = [COLORS["purple"], COLORS["blue"], COLORS["green"], COLORS["orange"], COLORS["red"], COLORS["pink"], COLORS["cyan"], COLORS["yellow"]]
        colors = [palette[i % len(palette)] for i in range(len(values))]
    max_value = max(values) if values else 1
    max_value = max(max_value, 1e-9)
    margin = {"top": 72, "right": 50, "bottom": 150, "left": 90}
    plot_w = width - margin["left"] - margin["right"]
    plot_h = height - margin["top"] - margin["bottom"]
    gap = 12
    bar_w = max(8, (plot_w - gap * (len(values) - 1)) / len(values))
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#f8fafc"/>',
        f'<text x="{width/2}" y="38" text-anchor="middle" font-family="Arial" font-size="24" font-weight="800" fill="{COLORS["text"]}">{title}</text>',
        f'<line x1="{margin["left"]}" y1="{height-margin["bottom"]}" x2="{width-margin["right"]}" y2="{height-margin["bottom"]}" stroke="{COLORS["light"]}" stroke-width="2"/>',
    ]
    for i, (label, value) in enumerate(zip(labels, values)):
        x = margin["left"] + i * (bar_w + gap)
        h = plot_h * value / max_value
        y = height - margin["bottom"] - h
        lines.append(f'<rect x="{x:.2f}" y="{y:.2f}" width="{bar_w:.2f}" height="{h:.2f}" fill="{colors[i]}" rx="5"/>')
        lines.append(f'<text x="{x+bar_w/2:.2f}" y="{y-8:.2f}" text-anchor="middle" font-family="Arial" font-size="12" font-weight="700" fill="{COLORS["text"]}">{value:,.3f}</text>')
        rotate = -35 if len(label) > 4 or len(labels) > 8 else 0
        if rotate:
            lines.append(f'<text x="{x+bar_w/2:.2f}" y="{height-margin["bottom"]+28}" text-anchor="end" transform="rotate({rotate} {x+bar_w/2:.2f},{height-margin["bottom"]+28})" font-family="Arial" font-size="13" fill="{COLORS["text"]}">{label}</text>')
        else:
            lines.append(f'<text x="{x+bar_w/2:.2f}" y="{height-margin["bottom"]+28}" text-anchor="middle" font-family="Arial" font-size="13" fill="{COLORS["text"]}">{label}</text>')
    lines.append("</svg>")
    path.write_text("\n".join(lines), encoding="utf-8")


def grouped_bar(path, title, groups, series, width=1000, height=540):
    palette = [COLORS["purple"], COLORS["green"], COLORS["red"], COLORS["blue"]]
    max_value = max(v for values in series.values() for v in values)
    margin = {"top": 76, "right": 160, "bottom": 110, "left": 90}
    plot_w = width - margin["left"] - margin["right"]
    plot_h = height - margin["top"] - margin["bottom"]
    group_w = plot_w / len(groups)
    bar_w = group_w / (len(series) + 1)
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#f8fafc"/>',
        f'<text x="{width/2}" y="38" text-anchor="middle" font-family="Arial" font-size="24" font-weight="800" fill="{COLORS["text"]}">{title}</text>',
        f'<line x1="{margin["left"]}" y1="{height-margin["bottom"]}" x2="{width-margin["right"]}" y2="{height-margin["bottom"]}" stroke="{COLORS["light"]}" stroke-width="2"/>',
    ]
    for gi, group in enumerate(groups):
        gx = margin["left"] + gi * group_w
        lines.append(f'<text x="{gx+group_w/2:.2f}" y="{height-margin["bottom"]+30}" text-anchor="middle" font-family="Arial" font-size="14" fill="{COLORS["text"]}">{group}</text>')
        for si, (name, values) in enumerate(series.items()):
            value = values[gi]
            h = plot_h * value / max_value if max_value else 0
            x = gx + (si + 0.5) * bar_w
            y = height - margin["bottom"] - h
            lines.append(f'<rect x="{x:.2f}" y="{y:.2f}" width="{bar_w*0.82:.2f}" height="{h:.2f}" fill="{palette[si]}" rx="5"/>')
            lines.append(f'<text x="{x+bar_w*0.41:.2f}" y="{y-7:.2f}" text-anchor="middle" font-family="Arial" font-size="12" fill="{COLORS["text"]}">{value:.3f}</text>')
    for si, name in enumerate(series):
        ly = margin["top"] + si * 26
        lx = width - margin["right"] + 20
        lines.append(f'<rect x="{lx}" y="{ly-12}" width="16" height="16" fill="{palette[si]}" rx="3"/>')
        lines.append(f'<text x="{lx+24}" y="{ly+1}" font-family="Arial" font-size="14" fill="{COLORS["text"]}">{name}</text>')
    lines.append("</svg>")
    path.write_text("\n".join(lines), encoding="utf-8")


def main():
    label = pd.read_csv(NLP_DIR / "review_sentiment_summary.csv")
    label["label"] = label["growth_label_top30"].map({0: "Non-growth", 1: "Growth"})
    grouped_bar(
        CHART_DIR / "sentiment_by_growth_label.svg",
        "Review Text Sentiment by Growth Label",
        label["label"].tolist(),
        {
            "Avg sentiment": label["avg_text_sentiment"].tolist(),
            "Positive rate": label["positive_text_rate"].tolist(),
            "Negative rate": label["negative_text_rate"].tolist(),
        },
    )

    topic_cols = ["taste_rate", "portion_rate", "delivery_rate", "price_rate", "service_rate", "reorder_rate"]
    grouped_bar(
        CHART_DIR / "review_topic_rates_by_growth_label.svg",
        "Review Topic Mention Rates by Growth Label",
        [c.replace("_rate", "") for c in topic_cols],
        {
            "Non-growth": label[label["growth_label_top30"] == 0][topic_cols].iloc[0].tolist(),
            "Growth": label[label["growth_label_top30"] == 1][topic_cols].iloc[0].tolist(),
        },
        width=1200,
    )

    pos = pd.read_csv(NLP_DIR / "positive_keyword_top50.csv").head(20)
    bar_chart(
        CHART_DIR / "positive_keywords_top20.svg",
        "Positive Review Keywords Top 20",
        pos["keyword"].tolist(),
        pos["count"].tolist(),
        width=1300,
        height=620,
    )

    neg = pd.read_csv(NLP_DIR / "negative_keyword_top50.csv").head(20)
    bar_chart(
        CHART_DIR / "negative_keywords_top20.svg",
        "Negative Review Keywords Top 20",
        neg["keyword"].tolist(),
        neg["count"].tolist(),
        width=1300,
        height=620,
    )

    cat = pd.read_csv(NLP_DIR / "review_category_sentiment_summary.csv")
    pivot = cat.pivot(index="category", columns="growth_label_top30", values="avg_text_sentiment").fillna(0)
    grouped_bar(
        CHART_DIR / "category_sentiment_by_growth_label.svg",
        "Category Sentiment by Growth Label",
        pivot.index.tolist(),
        {
            "Non-growth": pivot[0].tolist(),
            "Growth": pivot[1].tolist(),
        },
        width=1100,
    )

    mismatch = pd.read_csv(NLP_DIR / "rating_sentiment_mismatch_examples.csv")
    if not mismatch.empty:
        counts = mismatch["mismatch_type"].value_counts()
        bar_chart(
            CHART_DIR / "rating_sentiment_mismatch_counts.svg",
            "Rating-Sentiment Mismatch Counts",
            counts.index.tolist(),
            counts.tolist(),
            [COLORS["red"], COLORS["blue"]],
            width=1000,
        )

    print(f"WROTE {CHART_DIR}")


if __name__ == "__main__":
    main()
