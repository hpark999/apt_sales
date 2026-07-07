"""국토교통부 아파트 매매 실거래가 API 프록시 + 정적 파일 서버 (서울 강남구)."""

from __future__ import annotations

import json
import os
import ssl
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import date
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def load_dotenv() -> None:
    env_path = ROOT / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


load_dotenv()
SERVICE_KEY = os.environ.get("SERVICE_KEY", "")
API_URL = (
    "http://apis.data.go.kr/1613000/RTMSDataSvcAptTrade/"
    "getRTMSDataSvcAptTrade"
)
LAWD_CD = "11680"
DISTRICT_NAME = "강남구"
MONTHS_TO_FETCH = 6


def recent_deal_months(count: int) -> list[str]:
    today = date.today()
    year, month = today.year, today.month
    months: list[str] = []
    for _ in range(count):
        months.append(f"{year}{month:02d}")
        month -= 1
        if month == 0:
            month = 12
            year -= 1
    return months


def fetch_xml(deal_ymd: str, page_no: int, num_of_rows: int = 1000) -> str:
    params = urllib.parse.urlencode(
        {
            "serviceKey": SERVICE_KEY,
            "LAWD_CD": LAWD_CD,
            "DEAL_YMD": deal_ymd,
            "pageNo": page_no,
            "numOfRows": num_of_rows,
        }
    )
    url = f"{API_URL}?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(req, timeout=120, context=ctx) as resp:
        return resp.read().decode("utf-8")


def parse_response(xml_text: str) -> tuple[list[dict[str, str]], int]:
    root = ET.fromstring(xml_text)
    result_code = (root.findtext(".//resultCode") or "").strip()
    result_msg = (root.findtext(".//resultMsg") or "알 수 없는 오류").strip()

    if result_code and result_code != "000":
        raise RuntimeError(f"API 오류 ({result_code}): {result_msg}")

    items: list[dict[str, str]] = []
    for item in root.findall(".//item"):
        row = {child.tag: (child.text or "").strip() for child in item}
        items.append(row)

    total = int(root.findtext(".//totalCount") or len(items))
    return items, total


def fetch_month(deal_ymd: str) -> list[dict[str, str]]:
    first_xml = fetch_xml(deal_ymd, 1)
    first_items, total = parse_response(first_xml)
    all_items = list(first_items)

    page_size = 1000
    pages = (total + page_size - 1) // page_size
    for page in range(2, pages + 1):
        xml_text = fetch_xml(deal_ymd, page)
        page_items, _ = parse_response(xml_text)
        all_items.extend(page_items)

    return all_items


def normalize_item(raw: dict[str, str]) -> dict:
    amount_text = raw.get("dealAmount", "0").replace(",", "")
    amount = int(amount_text) if amount_text.isdigit() else 0
    area_text = raw.get("excluUseAr", "0") or "0"
    try:
        area = float(area_text)
    except ValueError:
        area = 0.0

    year = raw.get("dealYear", "")
    month = raw.get("dealMonth", "").zfill(2)
    day = raw.get("dealDay", "").zfill(2)

    return {
        "district": DISTRICT_NAME,
        "aptNm": raw.get("aptNm", ""),
        "umdNm": raw.get("umdNm", ""),
        "dealAmount": amount,
        "excluUseAr": area,
        "floor": raw.get("floor", ""),
        "buildYear": raw.get("buildYear", ""),
        "dealYear": year,
        "dealMonth": month,
        "dealDay": day,
        "dealDate": f"{year}-{month}-{day}" if year else "",
        "dealingGbn": raw.get("dealingGbn", ""),
        "roadNm": raw.get("roadNm", ""),
    }


def build_dashboard_data() -> dict:
    if not SERVICE_KEY:
        raise RuntimeError(
            "SERVICE_KEY 환경변수가 없습니다. .env 파일을 만들거나 환경변수를 설정하세요."
        )

    deal_months = recent_deal_months(MONTHS_TO_FETCH)
    trades: list[dict] = []

    for deal_ymd in deal_months:
        raw_items = fetch_month(deal_ymd)
        for raw in raw_items:
            trades.append(normalize_item(raw))

    trades.sort(
        key=lambda t: (t["dealDate"], t["dealAmount"]),
        reverse=True,
    )

    amounts = [t["dealAmount"] for t in trades if t["dealAmount"] > 0]
    avg_amount = round(sum(amounts) / len(amounts)) if amounts else 0

    by_dong: dict[str, int] = {}
    for trade in trades:
        dong = trade["umdNm"] or "기타"
        by_dong[dong] = by_dong.get(dong, 0) + 1
    top_dongs = sorted(by_dong.items(), key=lambda x: x[1], reverse=True)[:5]

    return {
        "lawdCd": LAWD_CD,
        "district": DISTRICT_NAME,
        "dealMonths": deal_months,
        "summary": {
            "count": len(trades),
            "avgAmount": avg_amount,
            "maxAmount": max(amounts) if amounts else 0,
            "minAmount": min(amounts) if amounts else 0,
            "topDongs": [{"dong": d, "count": c} for d, c in top_dongs],
        },
        "trades": trades,
        "totalCount": len(trades),
    }


class DashboardHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_GET(self) -> None:
        if self.path == "/api/dashboard":
            self.send_dashboard()
            return
        if self.path in ("/", ""):
            self.path = "/index.html"
        super().do_GET()

    def send_dashboard(self) -> None:
        try:
            payload = build_dashboard_data()
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except urllib.error.HTTPError as exc:
            body = json.dumps(
                {"error": f"HTTP {exc.code}: {exc.reason}"},
                ensure_ascii=False,
            ).encode("utf-8")
            self.send_response(500)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except (urllib.error.URLError, TimeoutError, RuntimeError, ET.ParseError) as exc:
            body = json.dumps({"error": str(exc)}, ensure_ascii=False).encode("utf-8")
            self.send_response(500)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    def log_message(self, format: str, *args) -> None:
        print(f"[{self.log_date_time_string()}] {format % args}")


def main() -> None:
    port = int(os.environ.get("PORT", "8080"))
    host = os.environ.get("HOST", "127.0.0.1")
    server = ThreadingHTTPServer((host, port), DashboardHandler)
    print(f"대시보드: http://{host}:{port}")
    print("종료: Ctrl+C")
    server.serve_forever()


if __name__ == "__main__":
    main()
