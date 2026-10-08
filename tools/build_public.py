#!/usr/bin/env python3
"""產生對外發布用的 _site/：只包含「已解鎖」的內容。

客戶端的日期檢查只能控制畫面；只要文稿還在公開檔案裡，任何人都能直接讀 articles_data.js
或 /articles/*.md。因此部署前由本腳本過濾：
  - manifest.json / manifest_data.js：只留已解鎖講次
  - articles_data.js：只留已解鎖講次的文稿
  - images/：只留已解鎖講次的封面（加 og.jpg）
  - 不發布 articles/（Markdown 原稿）、tools/、.github/、node_modules 等

「已解鎖」與前端判斷一致：isInitialBatch 或 releaseDate <= 今天（UTC+8）。
測試時可用環境變數 BUILD_DATE=YYYY-MM-DD 模擬日期。
"""
import json
import os
import re
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "_site"

TOP_LEVEL_FILES = ["index.html", "feed.xml", "sitemap.xml", ".nojekyll"]
TOP_LEVEL_DIRS = ["assets"]


def today_utc8() -> str:
    override = os.environ.get("BUILD_DATE")
    if override:
        return override
    return (datetime.now(timezone.utc) + timedelta(hours=8)).strftime("%Y-%m-%d")


def read_js_object(path: Path, var: str):
    text = path.read_text(encoding="utf-8")
    m = re.search(rf"const {var} = ", text)
    start = m.end()
    end = text.index("\n};" if text[start] == "{" else "\n];", start) + 2
    return json.loads(text[start:end])


def write_js(path: Path, var: str, data):
    path.write_text(
        f"const {var} = {json.dumps(data, ensure_ascii=False, indent=2)};\n\n"
        f"if (typeof module !== 'undefined' && module.exports) {{\n  module.exports = {var};\n}}\n",
        encoding="utf-8",
    )


def main():
    today = today_utc8()
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    unlocked = [a for a in manifest if a.get("isInitialBatch") or a["releaseDate"] <= today]
    ids = {a["id"] for a in unlocked}

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()

    for name in TOP_LEVEL_FILES:
        src = ROOT / name
        if src.exists():
            shutil.copy2(src, OUT / name)
    for name in TOP_LEVEL_DIRS:
        shutil.copytree(ROOT / name, OUT / name)

    (OUT / "manifest.json").write_text(json.dumps(unlocked, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_js(OUT / "manifest_data.js", "MANIFEST_DATA", unlocked)

    articles = read_js_object(ROOT / "articles_data.js", "ARTICLES_DATA")
    write_js(OUT / "articles_data.js", "ARTICLES_DATA", {k: v for k, v in articles.items() if int(k) in ids})

    (OUT / "images").mkdir()
    for img in (ROOT / "images").iterdir():
        m = re.match(r"(\d{3})_cover\.", img.name)
        if (m and int(m.group(1)) in ids) or img.name == "og.jpg":
            shutil.copy2(img, OUT / "images" / img.name)

    print(f"[build_public] {today}: 發布 {len(ids)} / {len(manifest)} 講 -> {OUT}")


if __name__ == "__main__":
    main()
