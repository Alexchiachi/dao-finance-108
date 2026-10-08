#!/usr/bin/env python3
"""把 images/*_cover.jpg 轉成寬 1600px 的 WebP（頁面優先載入 .webp，缺檔時回退原 jpg），
並產生 1200x630 的社群分享圖 images/og.jpg。已是最新者會略過。需要 Pillow。"""
from pathlib import Path
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
IMAGES = ROOT / "images"
MAX_W = 1600


def newer(dst: Path, src: Path) -> bool:
    return dst.exists() and dst.stat().st_mtime >= src.stat().st_mtime


def main():
    for src in sorted(IMAGES.glob("*_cover.jpg")):
        dst = src.with_suffix(".webp")
        if newer(dst, src):
            continue
        im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
        if im.width > MAX_W:
            im = im.resize((MAX_W, round(im.height * MAX_W / im.width)), Image.LANCZOS)
        im.save(dst, "WEBP", quality=80, method=6)
        print(f"{src.name} -> {dst.name} ({dst.stat().st_size // 1024} KB)")

    og, first = IMAGES / "og.jpg", IMAGES / "001_cover.jpg"
    if first.exists() and not newer(og, first):
        im = ImageOps.fit(Image.open(first).convert("RGB"), (1200, 630), Image.LANCZOS)
        im.save(og, "JPEG", quality=82, optimize=True, progressive=True)
        print(f"og.jpg ({og.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
