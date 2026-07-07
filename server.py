"""로컬 개발용 API 프록시 + 정적 파일 서버."""

from __future__ import annotations

import json
import os
import urllib.error
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from xml.etree.ElementTree import ParseError

from fetch_data import build_dashboard_data

ROOT = Path(__file__).resolve().parent


class DashboardHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_GET(self) -> None:
        if self.path == "/api/dashboard":
            self.send_dashboard()
            return
        if self.path == "/api/health":
            self.send_json(200, {"status": "ok"})
            return
        if self.path in ("/", ""):
            self.path = "/index.html"
        super().do_GET()

    def send_json(self, code: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_dashboard(self) -> None:
        try:
            self.send_json(200, build_dashboard_data())
        except urllib.error.HTTPError as exc:
            self.send_json(500, {"error": f"HTTP {exc.code}: {exc.reason}"})
        except (urllib.error.URLError, TimeoutError, RuntimeError, ParseError) as exc:
            self.send_json(500, {"error": str(exc)})

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
