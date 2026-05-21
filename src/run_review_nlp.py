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
    "맛": 1, "맛있": 2, "맛있어": 2, "맛있어요": 2, "맛있게": 2, "맛있네요": 2,
    "맛집": 2, "좋": 1, "좋아요": 2, "좋았": 2, "최고": 3, "굿": 2,
    "만족": 2, "친절": 2, "빠르": 1, "빨라": 1, "신선": 2, "깔끔": 2,
    "푸짐": 2, "든든": 2, "재주문": 3, "자주": 1, "추천": 2, "감사": 1,
    "잘먹": 2, "잘 먹": 2, "양 많": 2, "따뜻": 1, "바삭": 1, "부드럽": 1,
}

NEGATIVE = {
    "별로": -2, "실망": -3, "아쉽": -1, "아쉬": -1, "늦": -1, "늦게": -2,
    "차갑": -2, "식었": -2, "짜": -1, "싱겁": -1, "비싸": -2, "부족": -2,
    "적": -1, "누락": -3, "빠졌": -2, "잘못": -2, "불친절": -3, "최악": -4,
    "냄새": -2, "딱딱": -2, "질겨": -2, "타": -1, "기름": -1, "별 하나": -3,
    "환불": -3, "다신": -3,
}

CATEGORIES = {
    "taste": ["맛", "맛있", "짜", "싱겁", "바삭", "부드럽", "냄새", "기름"],
    "portion": ["양", "푸짐", "부족", "많", "적", "든든"],
    "delivery": ["배달", "늦", "빠르", "차갑", "식었", "따뜻"],
    "price": ["가격", "비싸", "가성비", "저렴"],
    "service": ["친절", "불친절", "응대", "감사"],
    "reorder": ["재주문", "자주", "또", "추천"],
}

COUPON_WORDS = ["쿠폰", "서비스", "이벤트", "혜택", "리뷰이벤트"]
TEMPLATE_WORDS = ["감사합니다", "소중한", "리뷰", "고객님", "앞으로도", "최선을", "찾아주셔서"]
AI_LIKE_WORDS = ["고객님", "소중한 리뷰", "만족하셨다니", "더 나은", "최선을 다하겠습니다", "이용해 주셔서"]


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
    text = re.sub(r"[^0-9a-zA-Z가-힣\s!?]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def tokenize(text):
    return [t for t in normalize(text).split(" ") if t]


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
    bounded = max(-5, min(5, score)) / 5
    return bounded, pos_hits, neg_hits


def category_hits(text):
    t = normalize(text)
    return {category: int(any(k in t for k in keywords)) for category, keywords in CATEGORIES.items()}


def text_basic_features(text, pos_hits, neg_hits, score):
    raw = str(text or "")
    tokens = tokenize(raw)
    pos_n = len(pos_hits)
    neg_n = len(neg_hits)
    return {
        "review_length": len(raw),
        "token_count": len(tokens),
        "exclamation_count": raw.count("!"),
        "question_count": raw.count("?"),
        "positive_hit_count": pos_n,
        "negative_hit_count": neg_n,
        "sentiment_abs": abs(score),
        "mixed_sentiment_flag": int(pos_n > 0 and neg_n > 0),
    }


def reply_features(reply):
    raw = str(reply or "").strip()
    t = normalize(raw)
    tokens = tokenize(raw)
    has_reply = int(bool(raw))
    template_hits = sum(int(w in t) for w in TEMPLATE_WORDS)
    ai_hits = sum(int(w in t) for w in AI_LIKE_WORDS)
    coupon_hits = sum(int(w in t) for w in COUPON_WORDS)
    return {
        "has_reply": has_reply,
        "reply_length": len(raw) if has_reply else 0,
        "reply_token_count": len(tokens) if has_reply else 0,
        "reply_contains_coupon": int(coupon_hits > 0),
        "reply_coupon_flag": int(coupon_hits > 0),
        "reply_template_score": template_hits / max(1, len(TEMPLATE_WORDS)),
        "reply_ai_like_score": ai_hits / max(1, len(AI_LIKE_WORDS)),
    }


def mean_or_zero(values, key):
    vals = [v[key] for v in values]
    return sum(vals) / len(vals) if vals else 0


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
    by_store_month = defaultdict(lambda: {
        "sentiment_sum": 0, "review_count": 0, "pos_count": 0, "neg_count": 0,
        "review_features": [], "reply_features": [], **{f"{c}_count": 0 for c in CATEGORIES}
    })

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
        basic = text_basic_features(content, pos_hits, neg_hits, score)
        reply = reply_features(row.get("replies.comment"))
        rating = row.get("review.rating")
        pos_counter.update(pos_hits)
        neg_counter.update(neg_hits)

        agg = by_store_month[(shop_id, month)]
        agg["sentiment_sum"] += score
        agg["review_count"] += 1
        agg["pos_count"] += int(score > 0)
        agg["neg_count"] += int(score < 0)
        agg["review_features"].append(basic)
        agg["reply_features"].append(reply)
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
                mismatch_rows.append({
                    "platform_shop_id": shop_id, "year_month": month, "review_id": row.get("review_id", ""),
                    "rating": rating, "sentiment_score": score, "mismatch_type": mismatch_type, "content": content[:240],
                })

        rows.append({
            "platform_shop_id": shop_id,
            "year_month": month,
            "review_id": row.get("review_id", ""),
            "rating": rating,
            "sentiment_score": score,
            "positive_hits": "|".join(pos_hits),
            "negative_hits": "|".join(neg_hits),
            **basic,
            **reply,
            **cats,
            **label_info,
        })

    review_features = pd.DataFrame(rows)
    review_features.to_csv(OUT_DIR / "review_text_features.csv", index=False, encoding="utf-8-sig")

    store_month_rows = []
    reply_rows = []
    for (shop_id, month), values in by_store_month.items():
        label_info = label_lookup[(shop_id, month)]
        n = values["review_count"]
        review_aggs = {k: mean_or_zero(values["review_features"], k) for k in [
            "review_length", "token_count", "exclamation_count", "question_count", "positive_hit_count",
            "negative_hit_count", "sentiment_abs", "mixed_sentiment_flag"
        ]}
        reply_aggs = {k: mean_or_zero(values["reply_features"], k) for k in [
            "has_reply", "reply_length", "reply_token_count", "reply_contains_coupon", "reply_coupon_flag", "reply_template_score", "reply_ai_like_score"
        ]}
        row_base = {
            "platform_shop_id": shop_id,
            "year_month": month,
            "avg_text_sentiment": values["sentiment_sum"] / n if n else 0,
            "text_review_count": n,
            "positive_text_rate": values["pos_count"] / n if n else 0,
            "negative_text_rate": values["neg_count"] / n if n else 0,
            **{f"{c}_rate": values[f"{c}_count"] / n if n else 0 for c in CATEGORIES},
            **review_aggs,
            **reply_aggs,
            **label_info,
        }
        store_month_rows.append(row_base)
        reply_rows.append({"platform_shop_id": shop_id, "year_month": month, **reply_aggs, **label_info})

    store_month = pd.DataFrame(store_month_rows)
    store_month.to_csv(OUT_DIR / "review_store_month_sentiment.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(reply_rows).to_csv(OUT_DIR / "reply_text_features.csv", index=False, encoding="utf-8-sig")

    label_summary = store_month.groupby("growth_label_top30").agg(
        rows=("platform_shop_id", "count"), stores=("platform_shop_id", "nunique"),
        avg_text_sentiment=("avg_text_sentiment", "mean"), positive_text_rate=("positive_text_rate", "mean"),
        negative_text_rate=("negative_text_rate", "mean"), taste_rate=("taste_rate", "mean"),
        portion_rate=("portion_rate", "mean"), delivery_rate=("delivery_rate", "mean"), price_rate=("price_rate", "mean"),
        service_rate=("service_rate", "mean"), reorder_rate=("reorder_rate", "mean"),
        review_length=("review_length", "mean"), token_count=("token_count", "mean"),
        positive_hit_count=("positive_hit_count", "mean"), negative_hit_count=("negative_hit_count", "mean"),
        mixed_sentiment_flag=("mixed_sentiment_flag", "mean"), has_reply=("has_reply", "mean"),
        reply_template_score=("reply_template_score", "mean"), reply_ai_like_score=("reply_ai_like_score", "mean"),
    ).reset_index()
    label_summary.to_csv(OUT_DIR / "review_sentiment_summary.csv", index=False, encoding="utf-8-sig")

    category_summary = store_month.groupby(["category", "growth_label_top30"]).agg(
        rows=("platform_shop_id", "count"), avg_text_sentiment=("avg_text_sentiment", "mean"),
        positive_text_rate=("positive_text_rate", "mean"), negative_text_rate=("negative_text_rate", "mean"),
    ).reset_index()
    category_summary.to_csv(OUT_DIR / "review_category_sentiment_summary.csv", index=False, encoding="utf-8-sig")

    pd.DataFrame(pos_counter.most_common(50), columns=["keyword", "count"]).to_csv(OUT_DIR / "positive_keyword_top50.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(neg_counter.most_common(50), columns=["keyword", "count"]).to_csv(OUT_DIR / "negative_keyword_top50.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(mismatch_rows).to_csv(OUT_DIR / "rating_sentiment_mismatch_examples.csv", index=False, encoding="utf-8-sig")

    ablation_rows = []
    for col in ["avg_text_sentiment", "positive_text_rate", "negative_text_rate", "reorder_rate", "review_length", "negative_hit_count", "has_reply", "reply_template_score", "reply_ai_like_score"]:
        g = store_month.groupby("growth_label_top30")[col].mean()
        if 0 in g.index and 1 in g.index:
            ablation_rows.append({"feature": col, "non_growth_mean": g.loc[0], "growth_mean": g.loc[1], "gap": g.loc[1] - g.loc[0]})
    pd.DataFrame(ablation_rows).to_csv(OUT_DIR / "nlp_ablation_report.csv", index=False, encoding="utf-8-sig")

    report = [
        "# Review NLP Summary", "", "## 목적", "",
        "리뷰 원문과 답글 본문에서 사전 기반 텍스트 피처를 추출해 성장 매장과 비성장 매장의 고객 반응 차이를 확인했다.", "",
        "## 분석 방식", "",
        "- 한국어 키워드 사전 기반 경량 텍스트 피처", "- 리뷰 길이, 토큰 수, 긍정/부정 hit 수, 혼합 감성 flag 추가",
        "- 답글 길이, 쿠폰 언급, 템플릿성, AI 유사 표현 score 추가", "- KoBERT fine-tuning은 수행하지 않았고 향후 과제로 둔다", "",
        "## 주요 결과", "",
    ]
    for r in label_summary.itertuples(index=False):
        report.append(f"- 성장 라벨 {int(r.growth_label_top30)}: 평균 텍스트 감성 {r.avg_text_sentiment:.4f}, 긍정 리뷰율 {r.positive_text_rate:.4f}, 부정 리뷰율 {r.negative_text_rate:.4f}")
    report.extend(["", "## 해석", "", "현재 NLP는 고급 언어모델이 아니라 사전 기반 텍스트 feature engineering이다. 효과 크기는 제한적이므로 모델 성능 개선보다 피드백 반영 및 보조 신호 확보로 해석한다."])
    (OUT_DIR / "review_sentiment_report.md").write_text("\n".join(report), encoding="utf-8")

    print("WROTE", OUT_DIR)
    print(label_summary.to_string(index=False))


if __name__ == "__main__":
    main()


