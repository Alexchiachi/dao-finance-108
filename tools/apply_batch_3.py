# -*- coding: utf-8 -*-
import json
import os
import re
from pathlib import Path

from generate_batch3_part1 import ARTICLES_PART1
from generate_batch3_part2 import ARTICLES_PART2
from generate_batch3_part3 import ARTICLES_PART3
from schedule import apply_schedule

ROOT = Path("/Users/chienchiachi/dao-finance-108")
ARTICLES_DIR = ROOT / "articles"
OBSIDIAN_DIR = Path("/Users/chienchiachi/Library/Mobile Documents/iCloud~md~obsidian/Documents/簡家旗一人公司幸福行爲藝術家/大道至簡金融")

# Merge all 18 articles for Batch 3 (37-54)
ALL_NEW = {}
ALL_NEW.update(ARTICLES_PART1)
ALL_NEW.update(ARTICLES_PART2)
ALL_NEW.update(ARTICLES_PART3)

print(f"Total articles in Batch 3 (37-54): {len(ALL_NEW)}")
assert len(ALL_NEW) == 18, f"Expected 18 articles, got {len(ALL_NEW)}"

# 1. Write individual Markdown files
for idx, data in sorted(ALL_NEW.items()):
    title = data["title"]
    filename = f"{idx:03d}_{title}.md"
    file_path = ARTICLES_DIR / filename
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(data["content"].strip() + "\n")
    print(f"Saved: {file_path.name}")
    
    # Sync to Obsidian if exists
    if OBSIDIAN_DIR.exists():
        obsidian_path = OBSIDIAN_DIR / filename
        with open(obsidian_path, "w", encoding="utf-8") as f:
            f.write(data["content"].strip() + "\n")
        print(f"Synced to Obsidian: {obsidian_path.name}")

# 2. Update articles_data.js
articles_js_path = ROOT / "articles_data.js"
with open(articles_js_path, "r", encoding="utf-8") as f:
    js_text = f.read()

# Extract existing ARTICLES_DATA object
start_marker = "const ARTICLES_DATA = "
start_idx = js_text.find(start_marker)
if start_idx == -1:
    raise ValueError("Could not find const ARTICLES_DATA in articles_data.js")
start_idx += len(start_marker)
end_idx = js_text.rfind("};\n\nif") + 1
if end_idx <= 0:
    end_idx = js_text.rfind("};") + 1

json_str = js_text[start_idx:end_idx]
existing_data = json.loads(json_str)

for idx, data in sorted(ALL_NEW.items()):
    existing_data[str(idx)] = {
        "id": idx,
        "vol": 3,
        "volName": "第三卷：節氣卷",
        "title": data["title"],
        "quote": data["quote"],
        "image": data["image"],
        "content": data["content"].strip()
    }

new_js_text = f"const ARTICLES_DATA = {json.dumps(existing_data, ensure_ascii=False, indent=2)};\n\nif (typeof module !== 'undefined' && module.exports) {{\n  module.exports = ARTICLES_DATA;\n}}\n"
with open(articles_js_path, "w", encoding="utf-8") as f:
    f.write(new_js_text)
print(f"Updated articles_data.js with {len(existing_data)} articles!")

# 3. Update manifest.json & manifest_data.js
manifest_path = ROOT / "manifest.json"
with open(manifest_path, "r", encoding="utf-8") as f:
    manifest = json.load(f)

# 解鎖日程統一由 tools/schedule.py 決定（1–8 講已解鎖，第 9 講起每天一篇），此處不再自行指定
apply_schedule(manifest)

with open(manifest_path, "w", encoding="utf-8") as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)

manifest_data_js = ROOT / "manifest_data.js"
with open(manifest_data_js, "w", encoding="utf-8") as f:
    f.write(f"const MANIFEST_DATA = {json.dumps(manifest, ensure_ascii=False, indent=2)};\n\nif (typeof module !== 'undefined' && module.exports) {{\n  module.exports = MANIFEST_DATA;\n}}\n")
print("Updated manifest.json and manifest_data.js!")
