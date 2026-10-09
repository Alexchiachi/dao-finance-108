/* 共用渲染：瀏覽器（頁面內）與 Node（tools/build_pages.js 預先渲染靜態頁）使用同一份，確保輸出一致。 */
(function (root, factory) {
  if (typeof module !== 'undefined' && module.exports) module.exports = factory();
  else root.DaoRender = factory();
})(typeof self !== 'undefined' ? self : this, function () {
  const escapeHtml = s => String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

  // 標題排版：「主標：副標」→ 主標一行大字；副標依「，、」逐句換行並去掉標點
  function titleHtml(title) {
    const i = title.indexOf('：');
    const main = i > 0 ? title.slice(0, i) : title;
    const sub = i > 0 ? title.slice(i + 1) : '';
    const lines = sub.split(/[，、]/).map(t => t.trim()).filter(Boolean);
    return `<span class="title-main">${escapeHtml(main)}</span>` + (lines.length
      ? `<span class="title-sub">${lines.map(l => `<span class="title-line">${escapeHtml(l)}</span>`).join('')}</span>`
      : '');
  }

  // 極簡 Markdown 轉 HTML 渲染器
  function parseMarkdown(md) {
    // 剝除前兩行標題與封面圖（避免與舞台重複）
    let clean = md.replace(/^#\s+[^\n]+\n+##\s+[^\n]+\n+!\[[^\]]*\]\([^\)]*\)\n+/g, '');
    // 剝除內文結尾落款（統一由下方專屬落款區塊高雅渲染）
    clean = clean.replace(/\n+---\n+\*\*發布日期\*\*：[^\n]+\s*\n+\*\*署名\*\*：[^\n]+/g, '');
    
    clean = clean.replace(/^[ \t]*-{3,}[ \t]*$/gm, '').replace(/\n{3,}/g, '\n\n');

    return clean
      .replace(/### 【破妄鏡】/g, '<div class="my-8 p-6 sm:p-7 bg-wash1 rounded-2xl"><h3 class="text-seal text-sm eyebrow mb-3 font-sans">破妄鏡</h3><div class="text-ink/90 leading-[2] font-serif">')
      .replace(/### 【真實的人性故事】/g, '</div></div><div class="my-8 p-6 sm:p-7 bg-wash2 ring-1 ring-tea/15 rounded-2xl"><h3 class="text-soft text-sm eyebrow mb-3 font-sans">真實的人性故事</h3><div class="text-ink space-y-4 leading-[2] font-serif">')
      .replace(/### 【見真鏡】/g, '</div></div><div class="my-8 p-6 sm:p-7 bg-wash3 rounded-2xl"><h3 class="text-soft text-sm eyebrow mb-3 font-sans">見真鏡</h3><div class="text-ink/90 leading-[2] font-serif">')
      .replace(/### 【AI 視角】/g, '</div></div><div class="my-8 p-6 sm:p-7 bg-wash4 rounded-2xl"><h3 class="text-soft text-sm eyebrow mb-3 font-sans">AI 視角</h3><div class="text-ink leading-[2] font-serif">')
      .replace(/### 【生活行】/g, '</div></div><div class="my-8 p-6 sm:p-7 bg-wash5 rounded-2xl"><h3 class="text-moss text-sm eyebrow mb-3 font-sans">生活行</h3><div class="text-ink/90 leading-[2] font-serif">')
      .replace(/\*\（本文純屬虛構[^\*]*\）\*/g, '</div></div><div class="mt-8 text-center text-xs text-soft italic font-serif">（本文純屬虛構、若有雷同純屬巧合。）</div>')
      .replace(/\*\*([^\*]+)\*\*/g, '<strong class="font-bold text-ink">$1</strong>')
      .replace(/\*([^\*]+)\*/g, '<em class="italic text-soft">$1</em>')
      .replace(/\n\n/g, '<p class="my-4"></p>')
      .replace(/\n/g, '<br>');
  }

  return { escapeHtml, titleHtml, parseMarkdown };
});
