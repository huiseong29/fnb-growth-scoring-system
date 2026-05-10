import csv
import json
import math
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path


DATA_DIR = Path("data")
EXTERNAL_DIR = Path("external_data")
OUTPUT_DIR = Path("analysis_outputs")
OUTPUT_DIR.mkdir(exist_ok=True)


def json_by_size(size):
    matches = [path for path in DATA_DIR.glob("*.json") if path.stat().st_size == size]
    if len(matches) != 1:
        raise RuntimeError(f"Expected one JSON file with size {size}, found {matches}")
    return matches[0]


FILES = {
    "identity": json_by_size(583434),
    "treatment": json_by_size(196566),
    "orders": json_by_size(470180924),
    "reviews": json_by_size(133241526),
    "controls": json_by_size(46512758),
}


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def parse_dt(value):
    if not value:
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y.%m.%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(str(value), fmt)
        except ValueError:
            pass
    return None


def month_key(dt):
    return f"{dt.year:04d}-{dt.month:02d}" if dt else None


def month_index(month):
    year, m = map(int, month.split("-"))
    return year * 12 + m


def month_from_index(idx):
    year = (idx - 1) // 12
    month = (idx - 1) % 12 + 1
    return f"{year:04d}-{month:02d}"


def safe_div(num, den):
    return num / den if den else ""


def pct_change(new, old):
    if old in ("", None) or old == 0:
        return ""
    return (new - old) / old


def norm_platform_shop_id_from_store_id(value):
    return f"ba_{value}" if value is not None else None


def parse_region(address):
    parts = (address or "").split()
    return {
        "sido": parts[0] if len(parts) > 0 else "",
        "sigungu": parts[1] if len(parts) > 1 else "",
        "road_or_eupmyeondong": parts[2] if len(parts) > 2 else "",
    }


def avg(values):
    return sum(values) / len(values) if values else ""


def stdev(values):
    if len(values) < 2:
        return ""
    m = sum(values) / len(values)
    return math.sqrt(sum((v - m) ** 2 for v in values) / (len(values) - 1))


print("Loading identity/treatment/control data...")
identity_rows = load_json(FILES["identity"])
treatment_rows = load_json(FILES["treatment"])
control_rows = load_json(FILES["controls"])

store_meta = {}
for row in identity_rows:
    shop_id = row["shops.platform_shop_id"]
    region = parse_region(row.get("shop_address"))
    store_meta[shop_id] = {
        "platform_shop_id": shop_id,
        "platform": row.get("shops.platform", ""),
        "shop_name": row.get("shop.name", ""),
        "category": row.get("shops.category_name", ""),
        "brand": row.get("brand_shop_id.brands.display_name", ""),
        "address": row.get("shop_address", ""),
        "sido": region["sido"],
        "sigungu": region["sigungu"],
        "road_or_eupmyeondong": region["road_or_eupmyeondong"],
        "promo_phrase_enabled": row.get("홍보문구 추가 여부", ""),
        "persona_tone_enabled": row.get(
            "페르소나 말투 지정 여부 (user_persona / shops.user_id = user_persona.user_id)",
            "",
        ),
        "experiment_group": row.get("구분", ""),
    }

treatment_by_shop = {}
for row in treatment_rows:
    shop_id = row["platform_shop_id"]
    dt = parse_dt(row.get("service_term_agree_date_utc"))
    if dt and (shop_id not in treatment_by_shop or dt < treatment_by_shop[shop_id]):
        treatment_by_shop[shop_id] = dt

menu_stats = defaultdict(lambda: {"menu_count": 0, "active": 0, "hidden": 0, "sold_out": 0, "delivery_prices": [], "pickup_prices": []})
for row in control_rows:
    shop_id = norm_platform_shop_id_from_store_id(row.get("가게 ID"))
    if not shop_id:
        continue
    stat = menu_stats[shop_id]
    stat["menu_count"] += 1
    status = row.get("메뉴 상태")
    if status == "ACTIVE":
        stat["active"] += 1
    elif status == "HIDDEN":
        stat["hidden"] += 1
    elif status == "SOLD_OUT":
        stat["sold_out"] += 1
    if isinstance(row.get("배달 금액"), (int, float)):
        stat["delivery_prices"].append(row["배달 금액"])
    if isinstance(row.get("픽업 금액"), (int, float)):
        stat["pickup_prices"].append(row["픽업 금액"])

print("Aggregating orders by store-month...")
orders = load_json(FILES["orders"])
order_month = defaultdict(lambda: {"order_count": 0, "sales_amount": 0.0, "quantity_sum": 0})
all_months = set()
for row in orders:
    shop_id = row.get("platform_shop_id")
    dt = parse_dt(row.get("order_date"))
    month = month_key(dt)
    if not shop_id or not month:
        continue
    key = (shop_id, month)
    order_month[key]["order_count"] += 1
    order_month[key]["sales_amount"] += float(row.get("price") or 0)
    order_month[key]["quantity_sum"] += int(row.get("quantity") or 0)
    all_months.add(month)
del orders

print("Aggregating reviews by store-month...")
reviews = load_json(FILES["reviews"])
review_month = defaultdict(lambda: {"review_count": 0, "rating_sum": 0.0, "rating_count": 0, "reply_count": 0, "reply_delay_hours": []})
for row in reviews:
    shop_id = row.get("platform_shop_id")
    review_dt = parse_dt(row.get("review.created_at"))
    month = month_key(review_dt)
    if not shop_id or not month:
        continue
    key = (shop_id, month)
    stat = review_month[key]
    stat["review_count"] += 1
    if isinstance(row.get("review.rating"), (int, float)):
        stat["rating_sum"] += float(row["review.rating"])
        stat["rating_count"] += 1
    reply_dt = parse_dt(row.get("replies.created_at"))
    if reply_dt:
        stat["reply_count"] += 1
        if review_dt:
            stat["reply_delay_hours"].append((reply_dt - review_dt).total_seconds() / 3600)
    all_months.add(month)
del reviews

external_by_shop = {}
external_path = EXTERNAL_DIR / "seoul_store_external_features_2024q4.csv"
if external_path.exists():
    with external_path.open("r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            external_by_shop[row["platform_shop_id"]] = row

first_month = "2024-11"
last_month = "2025-12"
month_range = [month_from_index(idx) for idx in range(month_index(first_month), month_index(last_month) + 1)]

print("Building base panel rows...")
rows = []
metric_by_store_month = {}
for shop_id in sorted(store_meta):
    meta = store_meta[shop_id]
    treatment_dt = treatment_by_shop.get(shop_id)
    menu = menu_stats.get(shop_id, {})
    ext = external_by_shop.get(shop_id, {})
    for month in month_range:
        orders_stat = order_month.get((shop_id, month), {})
        reviews_stat = review_month.get((shop_id, month), {})
        order_count = orders_stat.get("order_count", 0)
        sales_amount = orders_stat.get("sales_amount", 0.0)
        quantity_sum = orders_stat.get("quantity_sum", 0)
        review_count = reviews_stat.get("review_count", 0)
        rating_count = reviews_stat.get("rating_count", 0)
        reply_count = reviews_stat.get("reply_count", 0)
        avg_rating = safe_div(reviews_stat.get("rating_sum", 0.0), rating_count)
        reply_delay_avg = avg(reviews_stat.get("reply_delay_hours", []))
        row = {
            **meta,
            "year_month": month,
            "service_term_agree_date_utc": treatment_dt.strftime("%Y-%m-%d %H:%M:%S") if treatment_dt else "",
            "is_post_treatment": int(bool(treatment_dt and month_index(month) >= treatment_dt.year * 12 + treatment_dt.month)),
            "menu_count": menu.get("menu_count", ""),
            "active_menu_count": menu.get("active", ""),
            "hidden_menu_count": menu.get("hidden", ""),
            "sold_out_menu_count": menu.get("sold_out", ""),
            "avg_delivery_menu_price": avg(menu.get("delivery_prices", [])),
            "avg_pickup_menu_price": avg(menu.get("pickup_prices", [])),
            "order_count": order_count,
            "sales_amount": round(sales_amount, 2),
            "quantity_sum": quantity_sum,
            "store_avg_ticket": round(sales_amount / order_count, 2) if order_count else "",
            "review_count": review_count,
            "avg_rating": round(avg_rating, 4) if avg_rating != "" else "",
            "reply_count": reply_count,
            "reply_rate": round(reply_count / review_count, 4) if review_count else "",
            "avg_reply_delay_hours": round(reply_delay_avg, 2) if reply_delay_avg != "" else "",
            "rating_count": rating_count,
            "market_matched_services": ext.get("matched_services", ""),
            "market_q4_sales_amount": ext.get("market_q4_sales_amount", ""),
            "market_q4_sales_count": ext.get("market_q4_sales_count", ""),
            "market_q4_avg_ticket": ext.get("market_q4_avg_ticket", ""),
            "store_vs_market_ticket_ratio": (
                round((sales_amount / order_count) / float(ext["market_q4_avg_ticket"]), 4)
                if order_count and ext.get("market_q4_avg_ticket")
                else ""
            ),
        }
        rows.append(row)
        metric_by_store_month[(shop_id, month)] = {
            "order_count": order_count,
            "sales_amount": sales_amount,
            "review_count": review_count,
        }

print("Adding rolling growth labels...")
growth_scores = []
for row in rows:
    shop_id = row["platform_shop_id"]
    idx = month_index(row["year_month"])
    prev_period = [month_from_index(i) for i in range(idx - 5, idx - 2)]
    trailing = [month_from_index(i) for i in range(idx - 2, idx + 1)]
    future = [month_from_index(i) for i in range(idx + 1, idx + 4)]
    if prev_period[0] < first_month:
        row.update(
            {
                "historical_order_growth_3m": "",
                "historical_sales_growth_3m": "",
                "historical_review_growth_3m": "",
                "historical_composite_growth": "",
            }
        )
    else:
        def collect_hist(metric, months):
            return [metric_by_store_month[(shop_id, m)][metric] for m in months]

        prev_order = avg(collect_hist("order_count", prev_period))
        trailing_order_hist = avg(collect_hist("order_count", trailing))
        prev_sales = avg(collect_hist("sales_amount", prev_period))
        trailing_sales_hist = avg(collect_hist("sales_amount", trailing))
        prev_reviews = avg(collect_hist("review_count", prev_period))
        trailing_reviews_hist = avg(collect_hist("review_count", trailing))
        hist_order_growth = pct_change(trailing_order_hist, prev_order)
        hist_sales_growth = pct_change(trailing_sales_hist, prev_sales)
        hist_review_growth = pct_change(trailing_reviews_hist, prev_reviews)
        hist_components = [
            0.5 * hist_order_growth if hist_order_growth != "" else 0,
            0.3 * hist_sales_growth if hist_sales_growth != "" else 0,
            0.2 * hist_review_growth if hist_review_growth != "" else 0,
        ]
        row.update(
            {
                "historical_order_growth_3m": round(hist_order_growth, 6) if hist_order_growth != "" else "",
                "historical_sales_growth_3m": round(hist_sales_growth, 6) if hist_sales_growth != "" else "",
                "historical_review_growth_3m": round(hist_review_growth, 6) if hist_review_growth != "" else "",
                "historical_composite_growth": round(sum(hist_components), 6),
            }
        )

    if trailing[0] < first_month or future[-1] > last_month:
        row.update(
            {
                "trailing_3m_order_avg": "",
                "future_3m_order_avg": "",
                "order_growth_3m_forward": "",
                "sales_growth_3m_forward": "",
                "review_growth_3m_forward": "",
                "composite_growth_score": "",
            }
        )
        continue

    def collect(metric, months):
        return [metric_by_store_month[(shop_id, m)][metric] for m in months]

    trailing_order = avg(collect("order_count", trailing))
    future_order = avg(collect("order_count", future))
    trailing_sales = avg(collect("sales_amount", trailing))
    future_sales = avg(collect("sales_amount", future))
    trailing_reviews = avg(collect("review_count", trailing))
    future_reviews = avg(collect("review_count", future))
    order_growth = pct_change(future_order, trailing_order)
    sales_growth = pct_change(future_sales, trailing_sales)
    review_growth = pct_change(future_reviews, trailing_reviews)
    components = [
        0.5 * order_growth if order_growth != "" else 0,
        0.3 * sales_growth if sales_growth != "" else 0,
        0.2 * review_growth if review_growth != "" else 0,
    ]
    composite = sum(components)
    row.update(
        {
            "trailing_3m_order_avg": round(trailing_order, 4),
            "future_3m_order_avg": round(future_order, 4),
            "order_growth_3m_forward": round(order_growth, 6) if order_growth != "" else "",
            "sales_growth_3m_forward": round(sales_growth, 6) if sales_growth != "" else "",
            "review_growth_3m_forward": round(review_growth, 6) if review_growth != "" else "",
            "composite_growth_score": round(composite, 6),
        }
    )
    growth_scores.append(composite)

threshold = sorted(growth_scores)[int(len(growth_scores) * 0.7)] if growth_scores else None
for row in rows:
    score = row.get("composite_growth_score")
    row["is_label_valid"] = int(score != "" and threshold is not None)
    row["growth_label_top30"] = int(score >= threshold) if score != "" and threshold is not None else ""

print("Adding brand/category adjusted growth...")
valid_rows = [row for row in rows if row.get("composite_growth_score") != ""]
brand_month_avg = defaultdict(list)
category_month_avg = defaultdict(list)
hist_valid_rows = [row for row in rows if row.get("historical_composite_growth") != ""]
hist_brand_month_avg = defaultdict(list)
hist_category_month_avg = defaultdict(list)
for row in valid_rows:
    score = row["composite_growth_score"]
    brand_month_avg[(row["brand"], row["year_month"])].append(score)
    category_month_avg[(row["category"], row["year_month"])].append(score)
for row in hist_valid_rows:
    score = row["historical_composite_growth"]
    hist_brand_month_avg[(row["brand"], row["year_month"])].append(score)
    hist_category_month_avg[(row["category"], row["year_month"])].append(score)
brand_month_avg = {k: avg(v) for k, v in brand_month_avg.items()}
category_month_avg = {k: avg(v) for k, v in category_month_avg.items()}
hist_brand_month_avg = {k: avg(v) for k, v in hist_brand_month_avg.items()}
hist_category_month_avg = {k: avg(v) for k, v in hist_category_month_avg.items()}

for row in rows:
    score = row.get("composite_growth_score")
    if score == "":
        row["brand_adjusted_growth"] = ""
        row["category_adjusted_growth"] = ""
        row["internal_growth_alpha"] = ""
    else:
        brand_adj = score - brand_month_avg[(row["brand"], row["year_month"])]
        category_adj = score - category_month_avg[(row["category"], row["year_month"])]
        row["brand_adjusted_growth"] = round(brand_adj, 6)
        row["category_adjusted_growth"] = round(category_adj, 6)
        row["internal_growth_alpha"] = round((brand_adj + category_adj) / 2, 6)

    hist_score = row.get("historical_composite_growth")
    if hist_score == "":
        row["historical_brand_adjusted_growth"] = ""
        row["historical_category_adjusted_growth"] = ""
        row["historical_internal_growth_alpha"] = ""
    else:
        hist_brand_adj = hist_score - hist_brand_month_avg[(row["brand"], row["year_month"])]
        hist_category_adj = hist_score - hist_category_month_avg[(row["category"], row["year_month"])]
        row["historical_brand_adjusted_growth"] = round(hist_brand_adj, 6)
        row["historical_category_adjusted_growth"] = round(hist_category_adj, 6)
        row["historical_internal_growth_alpha"] = round((hist_brand_adj + hist_category_adj) / 2, 6)

output_path = OUTPUT_DIR / "store_month_panel.csv"
fieldnames = list(rows[0].keys())
with output_path.open("w", encoding="utf-8-sig", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"WROTE {output_path}")
print(f"ROWS {len(rows)}")
print(f"STORES {len(store_meta)}")
print(f"MONTHS {first_month}..{last_month} ({len(month_range)})")
print(f"VALID_LABEL_ROWS {len(growth_scores)}")
print(f"GROWTH_TOP30_THRESHOLD {threshold}")
