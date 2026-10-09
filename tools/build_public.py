#!/usr/bin/env python3
"""產生對外發布用的 _site/：只包含「已解鎖」的內容。

客戶端的日期檢查只能控制畫面；只要文稿還在公開檔案裡，任何人都能直接讀 articles_data.js
或 /articles/*.md。因此部署前由本腳本過濾：
  - manifest.json / manifest_data.js：只留已解鎖講次
  - content/NNN.json：已解鎖講次的文稿，每講一個小檔，頁面依需要才載入（不再出貨整包 articles_data.js）
  - images/：只留已解鎖講次的封面 WebP（缺 WebP 時才帶 jpg；另有 og.jpg）
  - 不發布 articles/（Markdown 原稿）、tools/、.github/、node_modules 等

「已解鎖」與前端判斷一致：isInitialBatch 或 releaseDate <= 今天（UTC+8）。
測試時可用環境變數 BUILD_DATE=YYYY-MM-DD 模擬日期。
"""
import hashlib
import json
import os
import re
import shutil
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from schedule import apply_schedule  # noqa: E402
OUT = ROOT / "_site"

TOP_LEVEL_FILES = ["index.html", "feed.xml", "sitemap.xml", "robots.txt", ".nojekyll"]
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
    fixed = apply_schedule(manifest)  # 以 tools/schedule.py 為準，防止批次腳本寫入錯誤日期
    if fixed:
        print(f"[build_public] 警告：manifest 有 {fixed} 講與解鎖日程不符，已依 schedule.py 校正")
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

    # 每講一個小檔 content/NNN.json（只含 id/quote/content），頁面讀到哪一講才下載；
    # 內容雜湊 ch 寫進 manifest，檔案沒變時瀏覽器可沿用快取
    articles = read_js_object(ROOT / "articles_data.js", "ARTICLES_DATA")
    (OUT / "content").mkdir()
    for item in unlocked:
        art = articles.get(str(item["id"]))
        if not art:
            continue
        payload = json.dumps({"id": art["id"], "quote": art["quote"], "content": art["content"]}, ensure_ascii=False, separators=(",", ":"))
        (OUT / "content" / f"{item['id']:03d}.json").write_text(payload, encoding="utf-8")
        item["ch"] = hashlib.sha1(payload.encode("utf-8")).hexdigest()[:10]

    (OUT / "manifest.json").write_text(json.dumps(unlocked, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_js(OUT / "manifest_data.js", "MANIFEST_DATA", unlocked)

    # 快取破壞：GitHub Pages 對靜態檔有約 10 分鐘快取，資料檔改名成帶內容雜湊的查詢字串，
    # 讓每次部署後瀏覽器一定抓到新的 manifest / 文稿 / CSS
    html = (OUT / "index.html").read_text(encoding="utf-8")
    html = html.replace('  <script src="articles_data.js"></script>\n', "", 1)  # 正式站改為依需要載入 content/*.json
    for rel in ("manifest_data.js", "assets/tailwind.css", "assets/render.js"):
        digest = hashlib.sha1((OUT / rel).read_bytes()).hexdigest()[:10]
        html = html.replace(f'"{rel}"', f'"{rel}?v={digest}"')
    (OUT / "index.html").write_text(html, encoding="utf-8")

    (OUT / "images").mkdir()
    for img in (ROOT / "images").iterdir():
        m = re.match(r"(\d{3})_cover\.", img.name)
        if img.name == "og.jpg":
            shutil.copy2(img, OUT / "images" / img.name)
        elif m and int(m.group(1)) in ids:
            # 有 WebP 時不再打包原始 jpg（頁面只載入 .webp；jpg 僅在缺 WebP 時當備援）
            if img.suffix == ".jpg" and img.with_suffix(".webp").exists():
                continue
            shutil.copy2(img, OUT / "images" / img.name)

    print(f"[build_public] {today}: 發布 {len(ids)} / {len(manifest)} 講 -> {OUT}")


if __name__ == "__main__":
    main()
