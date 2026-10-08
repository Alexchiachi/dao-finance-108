import re

def audit_article(text):
    # Count Chinese characters
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    
    # Check "我" outside of dialogs
    # remove text inside 「...」, 『...』, "...", “...”
    no_dialog = re.sub(r'「[^」]*」', '', text)
    no_dialog = re.sub(r'『[^』]*』', '', no_dialog)
    no_dialog = re.sub(r'“[^”]*”', '', no_dialog)
    no_dialog = re.sub(r'"[^"]*"', '', no_dialog)
    
    # Also ignore in title/colophon if specific
    self_words = re.findall(r'我|我們', no_dialog)
    
    # Check mirrors
    mirrors = [
        '【破妄鏡】' in text,
        '【真實的人性故事】' in text,
        '【見真鏡】' in text,
        '【AI 視角】' in text,
        '【生活行】' in text
    ]
    
    # Check colophon
    colophon = ('大道至簡 簡家旗' in text) and ('本文純屬虛構' in text)
    
    return {
        'char_count': chinese_chars,
        'self_words': self_words,
        'all_mirrors': all(mirrors),
        'colophon': colophon
    }

print("Audit function ready")
