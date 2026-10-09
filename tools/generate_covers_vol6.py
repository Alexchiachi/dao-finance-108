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

# Source master images from rich ink wash masters across earlier volumes
master_ids = [3, 7, 10, 15, 19, 23, 27, 31, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90]
masters = [Image.open(base_dir / f'{i:03d}_cover.jpg') for i in master_ids]

seals = [
    '先軀', '平息', '主權', '日損', '五感', '安寧',
    '茶根', '渡船', '傳承', '善活', '回流', '泥土',
    '傾聽', '家書', '退場', '星空', '清涼', '圓滿'
]

obsidian_img_dir.mkdir(parents=True, exist_ok=True)

for idx in range(91, 109):
    m1 = masters[(idx * 7 + 4) % len(masters)].copy()
    m2 = masters[(idx * 11 + 3) % len(masters)].copy()
    
    if idx % 2 == 1:
        m1 = m1.transpose(Image.FLIP_LEFT_RIGHT)
    if idx % 3 == 0:
        m2 = m2.transpose(Image.FLIP_TOP_BOTTOM).transpose(Image.FLIP_LEFT_RIGHT)
        
    blended = Image.blend(m1, m2, 0.44)
    enhancer = ImageEnhance.Color(blended)
    blended = enhancer.enhance(0.85)
    
    # Warm rice paper tint
    overlay = Image.new('RGB', blended.size, (250, 246, 239))
    blended = Image.blend(blended, overlay, 0.09)
    
    seal_text = seals[idx - 91]
    seal = create_seal(seal_text, size=(96, 96))
    blended.paste(seal, (40, 768 - 140), seal)
    
    out_file = base_dir / f'{idx:03d}_cover.jpg'
    blended.save(out_file, 'JPEG', quality=95)
    
    # Save webp
    webp_file = base_dir / f'{idx:03d}_cover.webp'
    blended.save(webp_file, 'WEBP', quality=82, method=6)
    
    print(f'Created: {out_file.name} & {webp_file.name} with seal [{seal_text}]')
    
    # Copy to Obsidian
    shutil.copy2(out_file, obsidian_img_dir / out_file.name)
    shutil.copy2(webp_file, obsidian_img_dir / webp_file.name)

print('All 18 Vol 6 covers created and synced to Obsidian successfully!')
