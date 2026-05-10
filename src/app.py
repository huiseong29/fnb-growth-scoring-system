import csv
import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse


ROOT = Path(__file__).resolve().parents[1]
SCORES_PATH = ROOT / "analysis_outputs" / "scoring" / "store_score_explanations.csv"
DEFAULT_PORT = 8765


def load_rows():
    with SCORES_PATH.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        for key in [
            "final_growth_probability",
            "probability_score",
            "growth_alpha_score",
            "review_growth_score",
            "operation_score",
            "stability_score",
            "market_fit_score",
            "gromong_score",
            "historical_internal_growth_alpha",
            "historical_review_growth_3m",
            "reply_rate",
            "avg_reply_delay_hours",
            "order_count",
            "sales_amount",
            "review_count",
            "market_q4_avg_ticket",
            "store_vs_market_ticket_ratio",
        ]:
            try:
                row[key] = float(row[key]) if row[key] != "" else None
            except (KeyError, ValueError):
                row[key] = None
        row["is_seoul_external"] = str(row.get("is_seoul_external", "0")) == "1"
    return rows


ROWS = load_rows()
ROW_BY_ID = {row["platform_shop_id"]: row for row in ROWS}
SUGGESTIONS = [
    {
        "platform_shop_id": row["platform_shop_id"],
        "shop_name": row["shop_name"],
        "brand": row["brand"],
        "category": row["category"],
        "score": row["gromong_score"],
        "grade": row["grade"],
    }
    for row in sorted(ROWS, key=lambda r: r["gromong_score"] or 0, reverse=True)[:30]
]


def grade_color(grade):
    return {
        "A": "#15803d",
        "B": "#2563eb",
        "C": "#f97316",
        "D": "#dc2626",
    }.get(grade, "#64748b")


def public_row(row):
    if not row:
        return None
    keys = [
        "platform_shop_id",
        "year_month",
        "shop_name",
        "brand",
        "category",
        "sido",
        "sigungu",
        "experiment_group",
        "final_growth_probability",
        "probability_score",
        "growth_alpha_score",
        "review_growth_score",
        "operation_score",
        "stability_score",
        "market_fit_score",
        "gromong_score",
        "grade",
        "historical_internal_growth_alpha",
        "historical_review_growth_3m",
        "reply_rate",
        "avg_reply_delay_hours",
        "order_count",
        "sales_amount",
        "review_count",
        "is_seoul_external",
        "market_q4_avg_ticket",
        "store_vs_market_ticket_ratio",
        "reason_1",
        "reason_2",
        "reason_3",
    ]
    out = {key: row.get(key) for key in keys}
    out["grade_color"] = grade_color(row.get("grade"))
    return out


INDEX_HTML = r"""
<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>GroMong Score Demo</title>
  <style>
    :root {
      --bg: #f8fafc;
      --panel: #ffffff;
      --text: #0f172a;
      --muted: #64748b;
      --line: #e2e8f0;
      --blue: #2563eb;
      --green: #15803d;
      --orange: #f97316;
      --red: #dc2626;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: Arial, "Noto Sans KR", sans-serif;
      background: var(--bg);
      color: var(--text);
    }
    header {
      border-bottom: 1px solid var(--line);
      background: #fff;
      padding: 18px 28px;
      position: sticky;
      top: 0;
      z-index: 2;
    }
    .title {
      display: flex;
      align-items: baseline;
      justify-content: space-between;
      gap: 16px;
      max-width: 1280px;
      margin: 0 auto;
    }
    h1 { margin: 0; font-size: 22px; letter-spacing: 0; }
    .subtitle { color: var(--muted); font-size: 13px; }
    main {
      max-width: 1280px;
      margin: 0 auto;
      padding: 24px;
    }
    .search {
      display: grid;
      grid-template-columns: minmax(260px, 1fr) auto;
      gap: 10px;
      margin-bottom: 18px;
    }
    input {
      height: 44px;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 0 14px;
      font-size: 15px;
      background: #fff;
    }
    button {
      height: 44px;
      border: 0;
      border-radius: 8px;
      background: var(--blue);
      color: #fff;
      padding: 0 18px;
      font-weight: 700;
      cursor: pointer;
    }
    .layout {
      display: grid;
      grid-template-columns: 380px 1fr;
      gap: 18px;
      align-items: start;
    }
    .panel {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 18px;
    }
    .suggestions {
      display: grid;
      gap: 8px;
      max-height: 560px;
      overflow: auto;
    }
    .suggestion {
      width: 100%;
      text-align: left;
      background: #fff;
      color: var(--text);
      border: 1px solid var(--line);
      height: auto;
      padding: 10px;
      display: grid;
      gap: 3px;
    }
    .suggestion:hover { border-color: var(--blue); }
    .small { color: var(--muted); font-size: 12px; }
    .result {
      display: grid;
      grid-template-columns: 290px 1fr;
      gap: 18px;
    }
    .gauge-wrap {
      display: grid;
      justify-items: center;
      gap: 12px;
    }
    .gauge {
      width: 220px;
      height: 220px;
      border-radius: 50%;
      display: grid;
      place-items: center;
      background: conic-gradient(var(--blue) calc(var(--score) * 1%), #e5e7eb 0);
      position: relative;
    }
    .gauge::after {
      content: "";
      width: 160px;
      height: 160px;
      border-radius: 50%;
      background: #fff;
      position: absolute;
    }
    .score {
      position: relative;
      z-index: 1;
      text-align: center;
    }
    .score strong { font-size: 42px; display: block; }
    .badge {
      display: inline-grid;
      place-items: center;
      width: 68px;
      height: 68px;
      border-radius: 12px;
      color: #fff;
      font-size: 34px;
      font-weight: 800;
      background: var(--grade-color);
    }
    .meta {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 10px;
      margin-bottom: 16px;
    }
    .metric {
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 12px;
      background: #fff;
    }
    .metric b { display: block; font-size: 18px; margin-top: 4px; }
    .bars { display: grid; gap: 12px; }
    .bar-row { display: grid; gap: 5px; }
    .bar-label { display: flex; justify-content: space-between; font-size: 13px; }
    .bar {
      height: 12px;
      border-radius: 999px;
      background: #e5e7eb;
      overflow: hidden;
    }
    .bar span {
      display: block;
      height: 100%;
      width: calc(var(--value) * 1%);
      background: var(--blue);
    }
    .reasons {
      margin-top: 16px;
      display: grid;
      gap: 8px;
    }
    .reason {
      border-left: 4px solid var(--blue);
      background: #eff6ff;
      padding: 10px 12px;
      border-radius: 6px;
    }
    .market {
      margin-top: 16px;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 14px;
      background: #fff;
    }
    .empty {
      min-height: 420px;
      display: grid;
      place-items: center;
      color: var(--muted);
      text-align: center;
    }
    @media (max-width: 900px) {
      .layout, .result { grid-template-columns: 1fr; }
      .search { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <header>
    <div class="title">
      <h1>GroMong Score Demo</h1>
      <div class="subtitle">AI 기반 F&B 성장 유망 매장 스코어링</div>
    </div>
  </header>
  <main>
    <section class="search">
      <input id="shopInput" placeholder="platform_shop_id 입력: ba_13248384">
      <button id="searchBtn">조회</button>
    </section>
    <section class="layout">
      <aside class="panel">
        <h2 style="font-size:16px;margin:0 0 10px;">추천 샘플</h2>
        <div id="suggestions" class="suggestions"></div>
      </aside>
      <section id="content" class="panel empty">
        <div>
          <b>매장 ID를 입력하세요.</b>
          <div class="small" style="margin-top:8px;">왼쪽 추천 샘플을 클릭해도 됩니다.</div>
        </div>
      </section>
    </section>
  </main>
  <script>
    const fmt = (v, digits = 2) => v === null || v === undefined || Number.isNaN(Number(v)) ? "-" : Number(v).toLocaleString("ko-KR", { maximumFractionDigits: digits });
    const pct = (v) => v === null || v === undefined ? "-" : `${(Number(v) * 100).toFixed(1)}%`;
    const clamp = (v) => Math.max(0, Math.min(100, Number(v || 0)));

    async function api(path) {
      const res = await fetch(path);
      if (!res.ok) throw new Error("request failed");
      return await res.json();
    }

    function bar(label, value) {
      const v = clamp(value);
      return `<div class="bar-row">
        <div class="bar-label"><span>${label}</span><b>${fmt(v, 1)}</b></div>
        <div class="bar" style="--value:${v}"><span></span></div>
      </div>`;
    }

    function renderStore(row) {
      const reasons = [row.reason_1, row.reason_2, row.reason_3].filter(Boolean);
      const market = row.is_seoul_external ? `
        <div class="market">
          <b>서울 외부 상권 보정</b>
          <div class="meta" style="margin-top:10px;margin-bottom:0;">
            <div class="metric"><span class="small">상권 평균 객단가</span><b>${fmt(row.market_q4_avg_ticket)}원</b></div>
            <div class="metric"><span class="small">매장/상권 객단가 비율</span><b>${fmt(row.store_vs_market_ticket_ratio, 3)}</b></div>
          </div>
        </div>` : `
        <div class="market">
          <b>외부 상권 보정</b>
          <div class="small" style="margin-top:6px;">현재 외부 상권 변수는 서울 매장 211개에만 적용됩니다.</div>
        </div>`;

      document.documentElement.style.setProperty("--grade-color", row.grade_color);
      document.getElementById("content").className = "panel";
      document.getElementById("content").innerHTML = `
        <div class="result">
          <div class="gauge-wrap">
            <div class="gauge" style="--score:${clamp(row.gromong_score)}">
              <div class="score"><strong>${fmt(row.gromong_score, 1)}</strong><span>GroMong Score</span></div>
            </div>
            <div class="badge" style="background:${row.grade_color}">${row.grade}</div>
            <div class="small">기준 월 ${row.year_month}</div>
          </div>
          <div>
            <h2 style="margin:0 0 4px;">${row.shop_name || row.platform_shop_id}</h2>
            <div class="small">${row.platform_shop_id} · ${row.brand} · ${row.category} · ${row.sido} ${row.sigungu}</div>
            <div class="meta" style="margin-top:16px;">
              <div class="metric"><span class="small">성장 확률</span><b>${pct(row.final_growth_probability)}</b></div>
              <div class="metric"><span class="small">실험 구분</span><b>${row.experiment_group || "-"}</b></div>
              <div class="metric"><span class="small">월 주문수</span><b>${fmt(row.order_count, 0)}</b></div>
              <div class="metric"><span class="small">월 리뷰수</span><b>${fmt(row.review_count, 0)}</b></div>
            </div>
            <div class="bars">
              ${bar("성장 확률 점수", row.probability_score)}
              ${bar("Growth Alpha 점수", row.growth_alpha_score)}
              ${bar("리뷰 성장 지수", row.review_growth_score)}
              ${bar("운영역량 지수", row.operation_score)}
              ${bar("안정성 지수", row.stability_score)}
              ${row.is_seoul_external ? bar("상권 적합도", row.market_fit_score) : ""}
            </div>
            <div class="reasons">
              ${reasons.map((r, i) => `<div class="reason"><b>근거 ${i + 1}</b><br>${r}</div>`).join("")}
            </div>
            ${market}
          </div>
        </div>`;
    }

    async function searchStore(id) {
      const data = await api(`/api/store?id=${encodeURIComponent(id)}`);
      if (!data.store) {
        document.getElementById("content").className = "panel empty";
        document.getElementById("content").innerHTML = `<div><b>매장을 찾을 수 없습니다.</b><div class="small" style="margin-top:8px;">platform_shop_id를 다시 확인하세요.</div></div>`;
        return;
      }
      renderStore(data.store);
    }

    async function init() {
      const data = await api("/api/suggestions");
      const box = document.getElementById("suggestions");
      box.innerHTML = data.suggestions.map(s => `
        <button class="suggestion" data-id="${s.platform_shop_id}">
          <b>${s.platform_shop_id} · ${s.grade} · ${fmt(s.score, 1)}</b>
          <span>${s.shop_name}</span>
          <span class="small">${s.brand} · ${s.category}</span>
        </button>`).join("");
      box.querySelectorAll("button").forEach(btn => btn.addEventListener("click", () => {
        document.getElementById("shopInput").value = btn.dataset.id;
        searchStore(btn.dataset.id);
      }));
      const first = data.suggestions[0]?.platform_shop_id;
      if (first) {
        document.getElementById("shopInput").value = first;
        searchStore(first);
      }
    }

    document.getElementById("searchBtn").addEventListener("click", () => {
      searchStore(document.getElementById("shopInput").value.trim());
    });
    document.getElementById("shopInput").addEventListener("keydown", e => {
      if (e.key === "Enter") searchStore(e.currentTarget.value.trim());
    });
    init();
  </script>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    def send_json(self, payload, status=200):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_html(self):
        body = INDEX_HTML.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/":
            self.send_html()
            return
        if parsed.path == "/api/suggestions":
            self.send_json({"suggestions": SUGGESTIONS})
            return
        if parsed.path == "/api/store":
            shop_id = parse_qs(parsed.query).get("id", [""])[0].strip()
            self.send_json({"store": public_row(ROW_BY_ID.get(shop_id))})
            return
        self.send_json({"error": "not found"}, status=404)

    def log_message(self, fmt, *args):
        sys.stdout.write("%s - %s\n" % (self.address_string(), fmt % args))


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PORT
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"GroMong demo running at http://127.0.0.1:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
