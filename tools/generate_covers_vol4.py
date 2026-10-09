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

# Source master images from Vol 1, 2, 3 for rich ink palette
masters = [Image.open(base_dir / f'{i:03d}_cover.jpg') for i in [1, 5, 8, 12, 18, 20, 26, 30, 36, 37, 41, 44, 48, 51, 54]]

seals = [
    '精算', '槓鈴', '對沖', '全候', '尊嚴', '階梯',
    '金約', '減法', '知界', '防偽', '緩衝', '彈性',
    '考驗', '純粹', '隔離', '無債', '守靜', '固柢'
]

obsidian_img_dir.mkdir(parents=True, exist_ok=True)

for idx in range(55, 73):
    m1 = masters[(idx * 7 + 3) % len(masters)].copy()
    m2 = masters[(idx * 11 + 5) % len(masters)].copy()
    
    if idx % 2 == 1:
        m1 = m1.transpose(Image.FLIP_LEFT_RIGHT)
    if idx % 3 == 0:
        m2 = m2.transpose(Image.FLIP_TOP_BOTTOM).transpose(Image.FLIP_LEFT_RIGHT)
        
    blended = Image.blend(m1, m2, 0.40)
    enhancer = ImageEnhance.Color(blended)
    blended = enhancer.enhance(0.85)
    
    # Warm rice paper tint
    overlay = Image.new('RGB', blended.size, (250, 246, 239))
    blended = Image.blend(blended, overlay, 0.09)
    
    seal_text = seals[idx - 55]
    seal = create_seal(seal_text, size=(96, 96))
    blended.paste(seal, (40, 768 - 140), seal)
    
    out_file = base_dir / f'{idx:03d}_cover.jpg'
    blended.save(out_file, 'JPEG', quality=95)
    print(f'Created: {out_file.name} with seal [{seal_text}]')
    
    # Copy to Obsidian
    shutil.copy2(out_file, obsidian_img_dir / out_file.name)

print('All 18 Vol 4 covers created and synced to Obsidian successfully!')
