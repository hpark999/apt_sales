"""국토교통부 아파트 매매 실거래가 데이터 수집."""

from __future__ import annotations

import os
import ssl
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent

API_URL = (
    "http://apis.data.go.kr/1613000/RTMSDataSvcAptTrade/"
    "getRTMSDataSvcAptTrade"
)
LAWD_CD = "11680"
DISTRICT_NAME = "강남구"
MONTHS_TO_FETCH = 6


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


def get_service_key() -> str:
    load_dotenv()
    return os.environ.get("SERVICE_KEY", "")


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


def fetch_xml(service_key: str, deal_ymd: str, page_no: int, num_of_rows: int = 1000) -> str:
    params = urllib.parse.urlencode(
        {
            "serviceKey": service_key,
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


def fetch_month(service_key: str, deal_ymd: str) -> list[dict[str, str]]:
    first_xml = fetch_xml(service_key, deal_ymd, 1)
    first_items, total = parse_response(first_xml)
    all_items = list(first_items)

    page_size = 1000
    pages = (total + page_size - 1) // page_size
    for page in range(2, pages + 1):
        xml_text = fetch_xml(service_key, deal_ymd, page)
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


def build_dashboard_data(service_key: str | None = None) -> dict:
    key = service_key or get_service_key()
    if not key:
        raise RuntimeError(
            "SERVICE_KEY 환경변수가 없습니다. .env 파일을 만들거나 환경변수를 설정하세요."
        )

    deal_months = recent_deal_months(MONTHS_TO_FETCH)
    trades: list[dict] = []

    for deal_ymd in deal_months:
        raw_items = fetch_month(key, deal_ymd)
        for raw in raw_items:
            trades.append(normalize_item(raw))

    trades.sort(key=lambda t: (t["dealDate"], t["dealAmount"]), reverse=True)

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
