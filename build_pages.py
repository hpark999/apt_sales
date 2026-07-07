"""GitHub Pages용 docs/ 폴더 생성."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from fetch_data import build_dashboard_data

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"


def main() -> None:
    DOCS.mkdir(exist_ok=True)
    data = build_dashboard_data()
    (DOCS / "data.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    shutil.copy(ROOT / "index.html", DOCS / "index.html")
    print(f"Generated docs/ ({data['totalCount']} trades)")


if __name__ == "__main__":
    main()
