# -*- coding: utf-8 -*-
import json
import os
import re
from pathlib import Path

from generate_batch1_part1 import ARTICLES_PART1
from generate_batch1_part2 import ARTICLES_PART2
from generate_batch1_part3 import ARTICLES_PART3

ROOT = Path("/Users/chienchiachi/dao-finance-108")
ARTICLES_DIR = ROOT / "articles"
OBSIDIAN_DIR = Path("/Users/chienchiachi/Library/Mobile Documents/iCloud~md~obsidian/Documents/簡家旗一人公司幸福行爲藝術家/大道至簡金融")

# Merge all 11 articles
ALL_NEW = {}
ALL_NEW.update(ARTICLES_PART1)
ALL_NEW.update(ARTICLES_PART2)
ALL_NEW.update(ARTICLES_PART3)

print(f"Total articles in Batch 1 (8-18): {len(ALL_NEW)}")

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
prefix = "const ARTICLES_DATA = "
match = re.search(r"const ARTICLES_DATA\s*=\s*(\{[\s\S]*\});?\s*$", js_text)
if match:
    existing_data = json.loads(match.group(1))
else:
    raise ValueError("Could not parse ARTICLES_DATA from articles_data.js")

for idx, data in sorted(ALL_NEW.items()):
    existing_data[str(idx)] = {
        "id": idx,
        "vol": 1,
        "volName": "第一卷：破妄卷",
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

for item in manifest:
    # 1 to 18 are now unlocked as Initial Batch
    if item["id"] <= 18:
        item["isInitialBatch"] = True
        item["releaseDate"] = "2026-10-08"

with open(manifest_path, "w", encoding="utf-8") as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)

manifest_data_js = ROOT / "manifest_data.js"
with open(manifest_data_js, "w", encoding="utf-8") as f:
    f.write(f"const MANIFEST_DATA = {json.dumps(manifest, ensure_ascii=False, indent=2)};\n\nif (typeof module !== 'undefined' && module.exports) {{\n  module.exports = MANIFEST_DATA;\n}}\n")
print("Updated manifest.json and manifest_data.js!")

