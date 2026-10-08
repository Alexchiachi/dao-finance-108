#!/usr/bin/env python3
"""
tools/process_issue.py
手機 Issue 雲端自轉處理核心：
支援由手機端 GitHub Issue 發布新文章或調節網頁美感，完全不需開啟本機電腦。
"""
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = ROOT / "manifest.json"
MANIFEST_DATA_JS = ROOT / "manifest_data.js"
ARTICLES_DATA_JS = ROOT / "articles_data.js"
INDEX_HTML = ROOT / "index.html"
ARTICLES_DIR = ROOT / "articles"
RESPONSE_FILE = ROOT / "issue_response.txt"


def set_github_output(name, value):
    output_file = os.environ.get("GITHUB_OUTPUT")
    if output_file:
        with open(output_file, "a", encoding="utf-8") as f:
            f.write(f"{name}={value}\n")


def handle_style(title: str, body: str):
    """處理美感與樣式調整指令"""
    print("[Mobile Automation] 偵測到美感微調指令...")
    html_text = INDEX_HTML.read_text(encoding="utf-8")

    # 支援別名對應
    color_map = {
        "paper": ["paper", "宣紙色", "背景色", "底色"],
        "ink": ["ink", "墨色", "字體色", "文字色"],
        "tea": ["tea", "茶色", "輔助色"],
        "moss": ["moss", "苔色", "松苔綠", "綠色"],
        "seal": ["seal", "印章色", "朱印色", "紅色"],
        "gold": ["gold", "金色", "金句色"]
    }

    updated_colors = []
    for key, aliases in color_map.items():
        pattern = rf"(?:{'|'.join(aliases)})[：:\s]+(#[0-9a-fA-F]{{3,8}})"
        match = re.search(pattern, body)
        if match:
            new_color = match.group(1).upper()
            # 替換 tailwind.config 中的定義
            old_pattern = rf"({key}:\s*['\"])[^'\"]+(['\"])"
            if re.search(old_pattern, html_text):
                html_text = re.sub(old_pattern, rf"\g<1>{new_color}\g<2>", html_text)
                updated_colors.append(f"- **{key}** ({aliases[1]}): `{new_color}`")

    if updated_colors:
        INDEX_HTML.write_text(html_text, encoding="utf-8")
        msg = f"🎨 **美感樣式已全自動更新上線！**\n\n已更新之配色標籤：\n" + "\n".join(updated_colors) + "\n\n🌐 [點此查看最新網頁效果](https://alexchiachi.github.io/dao-finance-108/)\n*(CDN 快取將在 1~2 分鐘內自動刷新)*"
        set_github_output("action_summary", "美感樣式更新: " + ", ".join([c.split('**')[1] for c in updated_colors]))
    else:
        msg = "⚠️ 未在 Issue 內文中找到明確的色碼指令（例如：`背景色: #FAF6EF` 或 `seal: #A8543A`）。"
        set_github_output("action_summary", "美感指令無變更")

    RESPONSE_FILE.write_text(msg, encoding="utf-8")
    print(msg)


def handle_article(title: str, body: str):
    """處理文章發布或靈感編譯指令"""
    print("[Mobile Automation] 偵測到文章發布/靈感指令...")
    
    # 提取第幾講
    lecture_match = re.search(r"(?:第\s*(\d{1,3})\s*講|\b(?:day|lecture|art|no)[-_ ]?(\d{1,3})\b)", title + " " + body, re.I)
    lecture_id = int(lecture_match.group(1) or lecture_match.group(2)) if lecture_match else None

    # 讀取現有 manifest
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    if not lecture_id:
        # 若未指定講次，自動找第一個未填寫正文的講次（從 8 開始）
        articles_raw = ARTICLES_DATA_JS.read_text(encoding="utf-8")
        for a in manifest:
            if a["id"] >= 8 and f'"{a["id"]}":' not in articles_raw:
                lecture_id = a["id"]
                break
        if not lecture_id:
            lecture_id = 8

    # 找尋 manifest 裡的元數據
    art_meta = next((a for a in manifest if a["id"] == lecture_id), None)
    clean_title = re.sub(r"^\[(?:發文|第\d+講|文章|靈感|publish)\]\s*", "", title, flags=re.I).strip()
    if not clean_title and art_meta:
        clean_title = art_meta["title"]
    elif art_meta and not clean_title:
        clean_title = art_meta["title"]

    # 提取金句（若有）
    quote_match = re.search(r"(?:金句|核心句|quote)[：:\s]+([^\n]+)", body)
    if quote_match:
        quote = quote_match.group(1).strip()
    else:
        # 取破妄鏡第一句或預設
        quote = "在資本的驚濤駭浪裡，守住身心的清寧，是任何人都奪不走的無價資產。"

    release_date = art_meta["releaseDate"] if art_meta else "2026-10-08"
    signature_footer = f"\n---\n\n**發布日期**：{release_date}  \n**署名**：大道至簡 簡家旗\n\n*（本文純屬虛構、若有雷同純屬巧合。）*"

    # 構建 Markdown 內文（確保大道五鏡、署名與虛構聲明）
    has_five_mirrors = "【破妄鏡】" in body and "【生活行】" in body
    if has_five_mirrors:
        content_md = body.strip()
        if "署名：大道至簡 簡家旗" not in content_md:
            if "*（本文純屬虛構" in content_md:
                content_md = re.sub(r"\n+---\n+\*\（本文純屬虛構[^\*]*\）\*", signature_footer, content_md)
            else:
                content_md += signature_footer
    else:
        # 自動包裝成五鏡框架
        content_md = f"""# 《大道至簡・金融一百零八講｜第{lecture_id}講》
## {clean_title}

![{clean_title}](images/{lecture_id:03d}_cover.jpg)

---

### 【破妄鏡】
{body.strip()}

---

### 【真實的人性故事】
（此篇由手機靈感觸發自動入庫，真實故事與細節持續自轉更新。）

---

### 【見真鏡】
老子曰：「為學日益，為道日損。」去我執，見真實，萬物並作，吾以觀復。

---

### 【AI 視角】
以第二種心智純粹理性視角俯瞰，資本的短期波動僅是熵增擾動，唯有守住系統邊界，方能抵禦尾部風險。

---

### 【生活行】
知行合一。今天回到身體感知，深呼吸，喝一杯溫潤茶湯，感受脈搏與身心的踏實安頓。
{signature_footer}
"""

    # 更新 articles_data.js
    articles_js_str = ARTICLES_DATA_JS.read_text(encoding="utf-8")
    # 解析出 ARTICLES_DATA 物件
    match_dict = re.search(r"const\s+ARTICLES_DATA\s*=\s*(\{[\s\S]*\});?\s*$", articles_js_str)
    
    # 簡單插入或替換文章
    new_entry = {
        "id": lecture_id,
        "vol": art_meta["vol"] if art_meta else 1,
        "volName": art_meta["volName"] if art_meta else "第一卷：破妄卷",
        "title": clean_title,
        "quote": quote,
        "image": f"images/{lecture_id:03d}_cover.jpg",
        "content": content_md
    }

    # 用 Node.js 輔助寫入以保證純淨的 JS 格式
    helper_script = f"""
    const fs = require('fs');
    const path = require('path');
    let raw = fs.readFileSync('{ARTICLES_DATA_JS}', 'utf8');
    let startIdx = raw.indexOf('{{');
    let endIdx = raw.lastIndexOf('}}');
    let jsonPart = raw.substring(startIdx, endIdx + 1);
    
    // 安全解析或構造
    let data;
    try {{
        data = eval('(' + jsonPart + ')');
    }} catch(e) {{
        data = {{}};
    }}
    
    data['{lecture_id}'] = {json.dumps(new_entry, ensure_ascii=False)};
    
    fs.writeFileSync('{ARTICLES_DATA_JS}', 'const ARTICLES_DATA = ' + JSON.stringify(data, null, 2) + ';\\n', 'utf8');
    """
    node_tmp = ROOT / "tools" / "temp_update.js"
    node_tmp.write_text(helper_script, encoding="utf-8")
    os.system(f"node {node_tmp}")
    if node_tmp.exists():
        node_tmp.unlink()

    # 同步儲存獨立 Markdown 檔案
    ARTICLES_DIR.mkdir(exist_ok=True)
    md_file = ARTICLES_DIR / f"{lecture_id:03d}_{clean_title.replace('/', '_')}.md"
    md_file.write_text(content_md, encoding="utf-8")

    # 更新 manifest 如果篇名有調整
    if art_meta and clean_title != art_meta["title"]:
        art_meta["title"] = clean_title
        MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        MANIFEST_DATA_JS.write_text("const MANIFEST_DATA = " + json.dumps(manifest, ensure_ascii=False, indent=2) + ";\n", encoding="utf-8")

    msg = f"""🎉 **第 {lecture_id:03d} 講已全自動編譯並上線！**

- **講次**：第 {lecture_id:03d} 講
- **篇名**：{clean_title}
- **金句**：「{quote}」

🌐 **線上閱讀網址**：https://alexchiachi.github.io/dao-finance-108/
*(GitHub Actions 將在 60 秒內全自動部署完畢)*"""

    RESPONSE_FILE.write_text(msg, encoding="utf-8")
    set_github_output("action_summary", f"發布第 {lecture_id:03d} 講: {clean_title}")
    print(msg)


def main():
    title = os.environ.get("ISSUE_TITLE", "").strip()
    body = os.environ.get("ISSUE_BODY", "").strip()

    if not title:
        print("未接收到 ISSUE_TITLE，退出。")
        return

    # 判斷指令類型
    is_style = any(k in title.lower() for k in ["[調美感]", "[美感]", "[style]", "[css]"])
    if is_style:
        handle_style(title, body)
    else:
        handle_article(title, body)


if __name__ == "__main__":
    main()
