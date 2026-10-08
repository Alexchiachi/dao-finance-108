"""解鎖日程的單一來源。

- 第 1–7 講：首發（isInitialBatch），2026-10-08 起可讀
- 第 8 講：2026-10-08 依日期解鎖
- 第 9 講起：自 2026-10-09 起每天解鎖一篇（第 108 講為 2027-01-16）

調整日程只需改這裡；tools/generate_site.js 內有同一套規則（JS 版）。
"""
from datetime import date, timedelta

LAUNCH_DATE = date(2026, 10, 8)
FIRST_DAILY_ID = 9
FIRST_DAILY_DATE = date(2026, 10, 9)
INITIAL_BATCH_MAX_ID = 7


def release_date(lecture_id: int) -> str:
    if lecture_id < FIRST_DAILY_ID:
        return LAUNCH_DATE.isoformat()
    return (FIRST_DAILY_DATE + timedelta(days=lecture_id - FIRST_DAILY_ID)).isoformat()


def apply_schedule(manifest: list) -> None:
    """就地套用解鎖日程到 manifest（list of dict）。"""
    for item in manifest:
        item["isInitialBatch"] = item["id"] <= INITIAL_BATCH_MAX_ID
        item["releaseDate"] = release_date(item["id"])
