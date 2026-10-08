# -*- coding: utf-8 -*-
import os
import shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

base_dir = Path('/Users/chienchiachi/dao-finance-108/images')
obsidian_img_dir = Path('/Users/chienchiachi/Library/Mobile Documents/iCloud~md~obsidian/Documents/簡家旗一人公司幸福行爲藝術家/大道至簡金融/images')
font_path = '/System/Library/Fonts/Supplemental/Songti.ttc'

def create_seal(text, size=(96, 96)):
    seal = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(seal)
    red = (168, 56, 42, 230)
    draw.rounded_rectangle([4, 4, size[0]-5, size[1]-5], radius=16, fill=red, outline=(130, 35, 25, 240), width=4)
    draw.rounded_rectangle([10, 10, size[0]-11, size[1]-11], radius=10, outline=(245, 235, 220, 180), width=2)
    try:
        font = ImageFont.truetype(font_path, 34)
    except:
        font = ImageFont.load_default()
    
    if len(text) == 2:
        draw.text((23, 12), text[0], font=font, fill=(248, 244, 235, 240))
        draw.text((23, 49), text[1], font=font, fill=(248, 244, 235, 240))
    elif len(text) == 4:
        sub_font = ImageFont.truetype(font_path, 30)
        draw.text((54, 15), text[0], font=sub_font, fill=(248, 244, 235, 240))
        draw.text((54, 52), text[1], font=sub_font, fill=(248, 244, 235, 240))
        draw.text((16, 15), text[2], font=sub_font, fill=(248, 244, 235, 240))
        draw.text((16, 52), text[3], font=sub_font, fill=(248, 244, 235, 240))
    return seal

# Source master images from Vol 1 & 2 for rich ink palette
masters = [Image.open(base_dir / f'{i:03d}_cover.jpg') for i in [1, 3, 5, 8, 9, 11, 14, 16, 18, 19, 21, 25, 27, 30, 33, 36]]

seals = [
    '節氣', '驚蟄', '芒種', '秋分', '大寒', '潮汐', 
    '定錨', '順應', '矽潮', '轉型', '年輪', '相變', 
    '重構', '躍遷', '厚土', '無主', '復甦', '知天'
]

obsidian_img_dir.mkdir(parents=True, exist_ok=True)

for idx in range(37, 55):
    # Select distinct blend pair
    m1 = masters[(idx * 5 + 2) % len(masters)].copy()
    m2 = masters[(idx * 9 + 4) % len(masters)].copy()
    
    if idx % 2 == 1:
        m1 = m1.transpose(Image.FLIP_LEFT_RIGHT)
    if idx % 3 == 1:
        m2 = m2.transpose(Image.FLIP_TOP_BOTTOM).transpose(Image.FLIP_LEFT_RIGHT)
        
    blended = Image.blend(m1, m2, 0.42)
    enhancer = ImageEnhance.Color(blended)
    blended = enhancer.enhance(0.88)
    
    # Warm rice paper tint
    overlay = Image.new('RGB', blended.size, (250, 246, 239))
    blended = Image.blend(blended, overlay, 0.09)
    
    seal_text = seals[idx - 37]
    seal = create_seal(seal_text, size=(96, 96))
    blended.paste(seal, (40, 768 - 140), seal)
    
    out_file = base_dir / f'{idx:03d}_cover.jpg'
    blended.save(out_file, 'JPEG', quality=95)
    print(f'Created: {out_file.name} with seal [{seal_text}]')
    
    # Copy to Obsidian
    shutil.copy2(out_file, obsidian_img_dir / out_file.name)

print('All 18 Vol 3 covers created and synced to Obsidian successfully!')