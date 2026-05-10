import csv
import io
import json
import zipfile
from collections import Counter, defaultdict
from pathlib import Path


BASE = Path("data")
IDENT_PATH = [x for x in BASE.glob("*.json") if x.stat().st_size == 583434][0]
SEOUL_ZIP = Path("external_data/seoul_sales_hdong_2024.zip")

K_SHOP = "shops.platform_shop_id"
K_ADDR = "shop_address"
K_CAT = "shops.category_name"

F_CODE = "행정동_코드"
F_SERVICE = "서비스_업종_코드_명"
F_QUARTER = "기준_년분기_코드"
F_AMOUNT = "당월_매출_금액"
F_COUNT = "당월_매출_건수"

CODE5_TO_GU = {
    "11110": "종로구",
    "11140": "중구",
    "11170": "용산구",
    "11200": "성동구",
    "11215": "광진구",
    "11230": "동대문구",
    "11260": "중랑구",
    "11290": "성북구",
    "11305": "강북구",
    "11320": "도봉구",
    "11350": "노원구",
    "11380": "은평구",
    "11410": "서대문구",
    "11440": "마포구",
    "11470": "양천구",
    "11500": "강서구",
    "11530": "구로구",
    "11545": "금천구",
    "11560": "영등포구",
    "11590": "동작구",
    "11620": "관악구",
    "11650": "서초구",
    "11680": "강남구",
    "11710": "송파구",
    "11740": "강동구",
}

CATEGORY_TO_SERVICES = {
    "치킨": ["치킨전문점"],
    "피자": ["패스트푸드점", "양식음식점"],
    "백반·죽·국수": ["한식음식점", "분식전문점"],
}


def main():
    with open(IDENT_PATH, "r", encoding="utf-8") as f:
        ident = json.load(f)

    seoul = []
    for row in ident:
        parts = (row.get(K_ADDR) or "").split()
        if parts and parts[0] == "서울특별시":
            seoul.append(
                {
                    K_SHOP: row[K_SHOP],
                    "gu": parts[1] if len(parts) > 1 else None,
                    "category": row[K_CAT],
                    "address": row.get(K_ADDR),
                }
            )

    internal_gu = Counter(row["gu"] for row in seoul)
    internal_cat = Counter(row["category"] for row in seoul)

    ext_gu = set()
    ext_services = Counter()
    agg = defaultdict(lambda: {"amount": 0, "count": 0, "rows": 0})

    with zipfile.ZipFile(SEOUL_ZIP) as z:
        name = z.namelist()[0]
        with z.open(name) as f:
            reader = csv.DictReader(io.TextIOWrapper(f, encoding="cp949", newline=""))
            for row in reader:
                gu = CODE5_TO_GU.get(row[F_CODE][:5])
                if not gu:
                    continue
                service = row[F_SERVICE]
                quarter = row[F_QUARTER]
                ext_gu.add(gu)
                ext_services[service] += 1
                key = (gu, service, quarter)
                agg[key]["amount"] += int(row[F_AMOUNT] or 0)
                agg[key]["count"] += int(row[F_COUNT] or 0)
                agg[key]["rows"] += 1

    print("INTERNAL_SEOUL_STORES", len(seoul))
    print("INTERNAL_SEOUL_UNIQUE_STORES", len({row[K_SHOP] for row in seoul}))
    print("INTERNAL_GU_COUNT", len(internal_gu))
    print("INTERNAL_CATEGORY_COUNTS", dict(internal_cat))
    print("INTERNAL_GU_COUNTS", dict(internal_gu))
    print("EXTERNAL_GU_COUNT", len(ext_gu))
    print("GU_MATCH_COUNT", len(set(internal_gu) & ext_gu), "/", len(internal_gu))
    print(
        "STORE_COVERAGE_BY_GU",
        sum(v for k, v in internal_gu.items() if k in ext_gu),
        "/",
        len(seoul),
    )
    print("EXTERNAL_FOOD_SERVICES", [s for s, _ in ext_services.most_common() if any(w in s for w in ["한식", "분식", "치킨", "양식", "패스트", "커피", "일식", "중식"])])

    for category, services in CATEGORY_TO_SERVICES.items():
        stores = [row for row in seoul if row["category"] == category]
        covered = 0
        for store in stores:
            if any((store["gu"], service, "20244") in agg for service in services):
                covered += 1
        print("CATEGORY_MATCH", category, covered, "/", len(stores), services)

    print("SAMPLE_ATTACHMENTS")
    for store in seoul[:15]:
        services = CATEGORY_TO_SERVICES.get(store["category"], [])
        vals = []
        for service in services:
            stat = agg.get((store["gu"], service, "20244"))
            if stat:
                vals.append(
                    {
                        "service": service,
                        "q4_amount": stat["amount"],
                        "q4_count": stat["count"],
                    }
                )
        print(json.dumps({**store, "external_q4": vals}, ensure_ascii=False))

    out_path = Path("external_data/seoul_store_external_features_2024q4.csv")
    with out_path.open("w", encoding="utf-8-sig", newline="") as f:
        fieldnames = [
            "platform_shop_id",
            "gu",
            "category",
            "address",
            "matched_services",
            "market_q4_sales_amount",
            "market_q4_sales_count",
            "market_q4_avg_ticket",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for store in seoul:
            services = CATEGORY_TO_SERVICES.get(store["category"], [])
            amount = 0
            count = 0
            matched_services = []
            for service in services:
                stat = agg.get((store["gu"], service, "20244"))
                if stat:
                    amount += stat["amount"]
                    count += stat["count"]
                    matched_services.append(service)
            writer.writerow(
                {
                    "platform_shop_id": store[K_SHOP],
                    "gu": store["gu"],
                    "category": store["category"],
                    "address": store["address"],
                    "matched_services": "|".join(matched_services),
                    "market_q4_sales_amount": amount,
                    "market_q4_sales_count": count,
                    "market_q4_avg_ticket": round(amount / count, 2) if count else "",
                }
            )
    print("WROTE", out_path)


if __name__ == "__main__":
    main()
