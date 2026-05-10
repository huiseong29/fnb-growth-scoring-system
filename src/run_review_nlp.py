import json
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

import pandas as pd


DATA_DIR = Path("data")
OUT_DIR = Path("analysis_outputs/nlp")
OUT_DIR.mkdir(parents=True, exist_ok=True)
PANEL_PATH = Path("analysis_outputs/store_month_panel.csv")


POSITIVE = {
    "맛": 1,
    "맛있": 2,
    "맛있어": 2,
    "맛있어요": 2,
    "맛있게": 2,
    "맛있네요": 2,
    "맛집": 2,
    "좋": 1,
    "좋아요": 2,
    "좋았": 2,
    "최고": 3,
    "굿": 2,
    "만족": 2,
    "친절": 2,
    "빠르": 1,
    "빨라": 1,
    "신선": 2,
    "깔끔": 2,
    "푸짐": 2,
    "든든": 2,
    "재주문": 3,
    "자주": 1,
    "추천": 2,
    "감사": 1,
    "잘먹": 2,
    "잘 먹": 2,
    "양 많": 2,
    "따뜻": 1,
    "바삭": 1,
    "부드럽": 1,
}

NEGATIVE = {
    "별로": -2,
    "실망": -3,
    "아쉽": -1,
    "아쉬": -1,
    "늦": -1,
    "늦게": -2,
    "차갑": -2,
    "식었": -2,
    "짜": -1,
    "싱겁": -1,
    "비싸": -2,
    "부족": -2,
    "적": -1,
    "누락": -3,
    "빠졌": -2,
    "잘못": -2,
    "불친절": -3,
    "최악": -4,
    "냄새": -2,
    "딱딱": -2,
    "질겨": -2,
    "타": -1,
    "기름": -1,
    "별 하나": -3,
    "환불": -3,
    "다신": -3,
}

CATEGORIES = {
    "taste": ["맛", "맛있", "짜", "싱겁", "바삭", "부드럽", "냄새", "기름"],
    "portion": ["양", "푸짐", "부족", "많", "적", "든든"],
    "delivery": ["배달", "늦", "빠르", "차갑", "식었", "따뜻"],
    "price": ["가격", "비싸", "가성비", "저렴"],
    "service": ["친절", "불친절", "응대", "감사"],
    "reorder": ["재주문", "자주", "또", "추천"],
}


def json_by_size(size):
    matches = [path for path in DATA_DIR.glob("*.json") if path.stat().st_size == size]
    if len(matches) != 1:
        raise RuntimeError(f"Expected one JSON file with size {size}, found {matches}")
    return matches[0]


def parse_dt(value):
    if not value:
        return None
    try:
        return datetime.strptime(str(value), "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None


def month_key(dt):
    return f"{dt.year:04d}-{dt.month:02d}" if dt else None


def normalize(text):
    text = str(text or "").lower()
    text = re.sub(r"[^0-9a-zA-Z가-힣\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def sentiment_score(text):
    t = normalize(text)
    pos_hits = []
    neg_hits = []
    score = 0
    for key, weight in POSITIVE.items():
        if key in t:
            c = t.count(key)
            score += weight * c
            pos_hits.extend([key] * c)
    for key, weight in NEGATIVE.items():
        if key in t:
            c = t.count(key)
            score += weight * c
            neg_hits.extend([key] * c)
    # compress to a bounded score for aggregation
    bounded = max(-5, min(5, score)) / 5
    return bounded, pos_hits, neg_hits


def category_hits(text):
    t = normalize(text)
    out = {}
    for category, keywords in CATEGORIES.items():
        out[category] = int(any(k in t for k in keywords))
    return out


def main():
    reviews_path = json_by_size(133241526)
    with reviews_path.open("r", encoding="utf-8") as f:
        reviews = json.load(f)

    panel = pd.read_csv(PANEL_PATH, encoding="utf-8-sig")
    label_map = panel[panel["is_label_valid"] == 1][["platform_shop_id", "year_month", "growth_label_top30", "category", "brand"]].copy()
    label_map["growth_label_top30"] = pd.to_numeric(label_map["growth_label_top30"], errors="coerce")
    label_lookup = {
        (r.platform_shop_id, r.year_month): {
            "growth_label_top30": int(r.growth_label_top30),
            "category": r.category,
            "brand": r.brand,
        }
        for r in label_map.itertuples(index=False)
        if pd.notna(r.growth_label_top30)
    }

    rows = []
    pos_counter = Counter()
    neg_counter = Counter()
    mismatch_rows = []
    by_store_month = defaultdict(lambda: {"sentiment_sum": 0, "review_count": 0, "pos_count": 0, "neg_count": 0, **{f"{c}_count": 0 for c in CATEGORIES}})

    for row in reviews:
        shop_id = row.get("platform_shop_id")
        dt = parse_dt(row.get("review.created_at"))
        month = month_key(dt)
        content = row.get("review.content") or ""
        if not shop_id or not month or not content:
            continue
        label_info = label_lookup.get((shop_id, month))
        if not label_info:
            continue
        score, pos_hits, neg_hits = sentiment_score(content)
        cats = category_hits(content)
        rating = row.get("review.rating")
        pos_counter.update(pos_hits)
        neg_counter.update(neg_hits)

        agg = by_store_month[(shop_id, month)]
        agg["sentiment_sum"] += score
        agg["review_count"] += 1
        agg["pos_count"] += int(score > 0)
        agg["neg_count"] += int(score < 0)
        for c, v in cats.items():
            agg[f"{c}_count"] += v

        if isinstance(rating, (int, float)):
            if rating >= 4 and score < 0:
                mismatch_type = "high_rating_negative_text"
            elif rating <= 2 and score > 0:
                mismatch_type = "low_rating_positive_text"
            else:
                mismatch_type = ""
            if mismatch_type:
                mismatch_rows.append(
                    {
                        "platform_shop_id": shop_id,
                        "year_month": month,
                        "review_id": row.get("review_id", ""),
                        "rating": rating,
                        "sentiment_score": score,
                        "mismatch_type": mismatch_type,
                        "content": content[:240],
                    }
                )

        rows.append(
            {
                "platform_shop_id": shop_id,
                "year_month": month,
                "review_id": row.get("review_id", ""),
                "rating": rating,
                "sentiment_score": score,
                "positive_hits": "|".join(pos_hits),
                "negative_hits": "|".join(neg_hits),
                **cats,
                **label_info,
            }
        )

    review_features = pd.DataFrame(rows)
    review_features.to_csv(OUT_DIR / "review_text_features.csv", index=False, encoding="utf-8-sig")

    store_month_rows = []
    for (shop_id, month), values in by_store_month.items():
        label_info = label_lookup[(shop_id, month)]
        n = values["review_count"]
        store_month_rows.append(
            {
                "platform_shop_id": shop_id,
                "year_month": month,
                "avg_text_sentiment": values["sentiment_sum"] / n if n else 0,
                "text_review_count": n,
                "positive_text_rate": values["pos_count"] / n if n else 0,
                "negative_text_rate": values["neg_count"] / n if n else 0,
                **{f"{c}_rate": values[f"{c}_count"] / n if n else 0 for c in CATEGORIES},
                **label_info,
            }
        )
    store_month = pd.DataFrame(store_month_rows)
    store_month.to_csv(OUT_DIR / "review_store_month_sentiment.csv", index=False, encoding="utf-8-sig")

    label_summary = (
        store_month.groupby("growth_label_top30")
        .agg(
            rows=("platform_shop_id", "count"),
            stores=("platform_shop_id", "nunique"),
            avg_text_sentiment=("avg_text_sentiment", "mean"),
            positive_text_rate=("positive_text_rate", "mean"),
            negative_text_rate=("negative_text_rate", "mean"),
            taste_rate=("taste_rate", "mean"),
            portion_rate=("portion_rate", "mean"),
            delivery_rate=("delivery_rate", "mean"),
            price_rate=("price_rate", "mean"),
            service_rate=("service_rate", "mean"),
            reorder_rate=("reorder_rate", "mean"),
        )
        .reset_index()
    )
    label_summary.to_csv(OUT_DIR / "review_sentiment_summary.csv", index=False, encoding="utf-8-sig")

    category_summary = (
        store_month.groupby(["category", "growth_label_top30"])
        .agg(
            rows=("platform_shop_id", "count"),
            avg_text_sentiment=("avg_text_sentiment", "mean"),
            positive_text_rate=("positive_text_rate", "mean"),
            negative_text_rate=("negative_text_rate", "mean"),
        )
        .reset_index()
    )
    category_summary.to_csv(OUT_DIR / "review_category_sentiment_summary.csv", index=False, encoding="utf-8-sig")

    pd.DataFrame(pos_counter.most_common(50), columns=["keyword", "count"]).to_csv(
        OUT_DIR / "positive_keyword_top50.csv", index=False, encoding="utf-8-sig"
    )
    pd.DataFrame(neg_counter.most_common(50), columns=["keyword", "count"]).to_csv(
        OUT_DIR / "negative_keyword_top50.csv", index=False, encoding="utf-8-sig"
    )
    pd.DataFrame(mismatch_rows).to_csv(OUT_DIR / "rating_sentiment_mismatch_examples.csv", index=False, encoding="utf-8-sig")

    report = [
        "# Review NLP Summary",
        "",
        "## 목적",
        "",
        "리뷰 원문에서 감성/키워드 신호를 추출해 성장 매장과 비성장 매장의 고객 반응 차이를 확인했다.",
        "",
        "## 분석 방식",
        "",
        "- 한국어 키워드 사전 기반 파일럿 감성 분석",
        "- 긍정/부정 키워드 카운트",
        "- 맛, 양, 배달, 가격, 서비스, 재주문 주제 분류",
        "- 별점과 텍스트 감성 불일치 사례 탐색",
        "",
        "## 주요 결과",
        "",
    ]
    for r in label_summary.itertuples(index=False):
        report.append(
            f"- 성장 라벨 {int(r.growth_label_top30)}: 평균 텍스트 감성 {r.avg_text_sentiment:.4f}, 긍정 리뷰율 {r.positive_text_rate:.4f}, 부정 리뷰율 {r.negative_text_rate:.4f}"
        )
    report.extend(
        [
            "",
            "## 해석",
            "",
            "이 분석은 리뷰 별점과 리뷰 수만 보던 기존 구조에서 한 단계 나아가, 고객이 실제로 남긴 언어에서 성장 신호를 찾기 위한 파일럿 NLP 분석이다.",
            "",
            "키워드 사전 기반이므로 정교한 딥러닝 감성분석은 아니지만, 중간발표에서는 리뷰 원문까지 활용했다는 점과 성장/비성장 그룹의 언어 차이를 보여주는 근거로 활용할 수 있다.",
        ]
    )
    (OUT_DIR / "review_sentiment_report.md").write_text("\n".join(report), encoding="utf-8")

    print("WROTE", OUT_DIR)
    print(label_summary.to_string(index=False))
    print("positive_top", pos_counter.most_common(10))
    print("negative_top", neg_counter.most_common(10))


if __name__ == "__main__":
    main()
