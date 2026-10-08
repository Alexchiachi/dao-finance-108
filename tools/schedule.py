"""解鎖日程的單一來源。

- 第 1–7 講：首發（isInitialBatch），2026-10-08 起可讀
- 第 8 講：2026-10-08 依日期解鎖
- 第 9 講起：自 2026-10-09 起每天解鎖一篇（第 108 講為 2027-01-16）

調整日程只需改這裡；tools/generate_site.js 內有同一套規則（JS 版），也要一起改。

自動校正：每次部署前（daily-publish.yml）會執行 `python3 tools/schedule.py --write`，
把 manifest.json / manifest_data.js 的 isInitialBatch、releaseDate 還原成這裡的規則；
build_public.py 建置時也會再校正一次。所以即使日後某個批次腳本自行指定日期，
上線的解鎖日程仍以本檔為準。若真的要讓某講提前／延後，請加到 OVERRIDES。
"""
import json
import sys
from datetime import date, timedelta
from pathlib import Path

LAUNCH_DATE = date(2026, 10, 8)
FIRST_DAILY_ID = 9
FIRST_DAILY_DATE = date(2026, 10, 9)
INITIAL_BATCH_MAX_ID = 7

# 例外：{講次: "YYYY-MM-DD"}。有列在這裡的講次以此日期為準（不再套用每天一篇的規則）
OVERRIDES: dict = {}

ROOT = Path(__file__).resolve().parent.parent


def release_date(lecture_id: int) -> str:
    if lecture_id in OVERRIDES:
        return OVERRIDES[lecture_id]
    if lecture_id < FIRST_DAILY_ID:
        return LAUNCH_DATE.isoformat()
    return (FIRST_DAILY_DATE + timedelta(days=lecture_id - FIRST_DAILY_ID)).isoformat()


def apply_schedule(manifest: list) -> int:
    """就地套用解鎖日程到 manifest（list of dict），回傳被校正的講次數。"""
    changed = 0
    for item in manifest:
        want = (item["id"] <= INITIAL_BATCH_MAX_ID, release_date(item["id"]))
        if (item.get("isInitialBatch"), item.get("releaseDate")) != want:
            changed += 1
        item["isInitialBatch"], item["releaseDate"] = want
    return changed


def _write_manifests() -> int:
    """校正 manifest.json 與 manifest_data.js；回傳校正的講次數。"""
    json_path = ROOT / "manifest.json"
    manifest = json.loads(json_path.read_text(encoding="utf-8"))
    changed = apply_schedule(manifest)
    if changed:
        json_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    js_path = ROOT / "manifest_data.js"
    text = js_path.read_text(encoding="utf-8")
    start, end = text.index("["), text.rindex("]")
    data = json.loads(text[start:end + 1])
    if apply_schedule(data):
        js_path.write_text(text[:start] + json.dumps(data, ensure_ascii=False, indent=2) + text[end + 1:], encoding="utf-8")
    return changed


if __name__ == "__main__":
    if "--write" in sys.argv:
        n = _write_manifests()
        print(f"[schedule] 已校正 {n} 講的解鎖日程" if n else "[schedule] 解鎖日程無需校正")
    else:
        m = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        n = apply_schedule(m)
        print(f"[schedule] {n} 講與規則不符（加 --write 可自動校正）")
        sys.exit(1 if n else 0)
