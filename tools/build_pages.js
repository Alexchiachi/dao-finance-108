#!/usr/bin/env node
/**
 * 為每一個已解鎖的講次產生獨立的靜態頁 _site/a/NNN/index.html，並預先渲染首頁的最新一講。
 *
 * 為什麼：頁面網址原本是 #/007（井號後面搜尋引擎會忽略），社群分享預覽也只會抓到首頁資訊。
 * 靜態頁有各自的網址、標題、描述、分享圖與結構化資料，正文直接寫在 HTML 裡（不靠 JS 也能讀，首屏最快）。
 * 頁面本身仍是同一個應用：載入後按鈕、搜尋、深色模式、金句圖卡、上一講／下一講等照常運作。
 *
 * 流程：tools/build_public.py 先產生 _site/（只含已解鎖內容）→ 本腳本再把 _site/index.html 當樣板展開。
 * 與 tools/build_public.py 同一個前提：只處理 _site/manifest.json 裡的講次（即已解鎖者）。
 */
const fs = require('fs');
const path = require('path');
const R = require('../assets/render.js');

const ROOT = path.resolve(__dirname, '..');
const OUT = path.join(ROOT, '_site');
const SITE_URL = 'https://alexchiachi.github.io/dao-finance-108/';
const SITE_PATH = new URL(SITE_URL).pathname;           // /dao-finance-108/
const SITE_TITLE = '大道至簡・金融一百零八講';
const pad3 = n => String(n).padStart(3, '0');

const template = fs.readFileSync(path.join(OUT, 'index.html'), 'utf8');
const manifest = JSON.parse(fs.readFileSync(path.join(OUT, 'manifest.json'), 'utf8'));

// 取代時要求一定要命中，樣板被改壞時建置會直接失敗，而不是悄悄產生壞頁面
function sub(html, regex, replacement, label) {
  if (!regex.test(html)) throw new Error(`build_pages: 樣板中找不到「${label}」`);
  return html.replace(regex, replacement);
}
const attr = s => R.escapeHtml(s);

function excerpt(text, max) {
  const t = text.replace(/\s+/g, ' ').trim();
  return t.length > max ? t.slice(0, max - 1) + '…' : t;
}

/** 預先渲染一講的內容到樣板；page=true 時同時改寫 <head>（標題、描述、canonical、分享圖、結構化資料）。 */
function render(art, content, { page, base, prev, next }) {
  let html = template;
  const id3 = pad3(art.id);
  const webp = art.image.replace(/\.jpe?g$/i, '.webp');
  const cover = base + webp;
  const url = `${SITE_URL}a/${id3}/`;
  const fullTitle = `第 ${id3} 講｜${art.title}｜${SITE_TITLE}`;
  const desc = excerpt(content.quote, 110);

  // 靜態模式旗標與預先渲染的講次
  html = sub(html, /<meta name="site-base" content="\.\/">/, `<meta name="site-base" content="${base}">\n  <script>window.SITE_STATIC=true;window.PRERENDERED_ID=${art.id};</script>`, 'site-base meta');

  if (page) {
    // 相對資源改成從 a/NNN/ 往上兩層
    html = html.replace(/(href|src)="(assets\/|feed\.xml|manifest_data\.js)/g, `$1="${base}$2`);

    html = sub(html, /<title>[\s\S]*?<\/title>/, `<title>${attr(fullTitle)}</title>`, 'title');
    html = sub(html, /<meta name="description" content="[^"]*">/, `<meta name="description" content="${attr(desc)}">`, 'description');
    html = sub(html, /<meta property="og:title" content="[^"]*">/, `<meta property="og:title" content="${attr(fullTitle)}">`, 'og:title');
    html = sub(html, /<meta property="og:description" content="[^"]*">/, `<meta property="og:description" content="${attr(desc)}">`, 'og:description');
    html = sub(html, /<link rel="canonical" href="[^"]*">/, `<link rel="canonical" href="${url}">`, 'canonical');
    html = sub(html, /<meta property="og:type" content="website">/, '<meta property="og:type" content="article">', 'og:type');
    html = sub(html, /<meta property="og:url" content="[^"]*">/, `<meta property="og:url" content="${url}">`, 'og:url');
    html = sub(html, /<meta property="og:image" content="[^"]*">/,
      `<meta property="og:image" content="${SITE_URL}${webp}">\n  <meta property="og:image:width" content="1376">\n  <meta property="og:image:height" content="768">`, 'og:image');
    html = sub(html, /<meta name="twitter:card" content="summary_large_image">/,
      `<meta name="twitter:card" content="summary_large_image">\n  <meta name="twitter:title" content="${attr(fullTitle)}">\n  <meta name="twitter:description" content="${attr(desc)}">\n  <meta name="twitter:image" content="${SITE_URL}${webp}">`, 'twitter:card');

    const ld = {
      '@context': 'https://schema.org',
      '@type': 'Article',
      headline: art.title,
      description: desc,
      datePublished: art.releaseDate,
      inLanguage: 'zh-TW',
      image: [`${SITE_URL}${webp}`],
      author: { '@type': 'Person', name: '簡家旗' },
      isPartOf: { '@type': 'WebSite', name: SITE_TITLE, url: SITE_URL },
      mainEntityOfPage: url,
    };
    const rel = (prev ? `\n  <link rel="prev" href="${SITE_URL}a/${pad3(prev.id)}/">` : '') + (next ? `\n  <link rel="next" href="${SITE_URL}a/${pad3(next.id)}/">` : '');
    html = sub(html, /<\/head>/,
      `  <link rel="preload" as="image" href="${cover}" fetchpriority="high">${rel}\n  <script type="application/ld+json">${JSON.stringify(ld).replace(/</g, '\\u003c')}</script>\n</head>`, 'head end');
  }

  // 文章區塊
  html = sub(html, /(<span id="art-vol-badge"[^>]*>)[^<]*(<\/span>)/, `$1${attr(art.volName)}$2`, 'art-vol-badge');
  html = sub(html, /(<span id="art-id-badge"[^>]*>)[^<]*(<\/span>)/, `$1第 ${id3} 講$2`, 'art-id-badge');
  html = sub(html, /(<time id="art-release-date"[^>]*>)[^<]*(<\/time>)/, `$1${art.releaseDate}$2`, 'art-release-date');
  html = sub(html, /(<span id="art-colophon-date"[^>]*>)[^<]*(<\/span>)/, `$1${art.releaseDate}$2`, 'art-colophon-date');
  html = sub(html, /<!--T-->[\s\S]*?<!--\/T-->/, () => R.titleHtml(art.title), 'title marker');
  html = sub(html, /<img id="art-cover-img"[^>]*>/,
    () => `<img id="art-cover-img" src="${cover}" alt="${attr(`第 ${art.id} 講封面：${art.title}`)}" width="1280" height="720" decoding="async" fetchpriority="high" class="cover">`, 'cover img');
  html = sub(html, /<!--B-->[\s\S]*?<!--\/B-->/, () => R.parseMarkdown(content.content), 'body marker');

  // 不執行 JS 時仍可前後翻閱
  if (page) {
    const links = [prev && `<a href="${base}a/${pad3(prev.id)}/">‹ 上一講：${attr(prev.title.split('：')[0])}</a>`, next && `<a href="${base}a/${pad3(next.id)}/">下一講：${attr(next.title.split('：')[0])} ›</a>`].filter(Boolean).join(' ｜ ');
    html = sub(html, /(<div class="mt-8 flex flex-col-reverse)/, `<noscript><p class="mt-6 text-center text-sm">${links} ｜ <a href="${base}">回到目錄</a></p></noscript>\n          $1`, 'nav noscript');
  }
  return html;
}

function main() {
  const unlocked = manifest; // build_public.py 已濾成已解鎖
  let count = 0;
  const aDir = path.join(OUT, 'a');
  fs.rmSync(aDir, { recursive: true, force: true });

  unlocked.forEach((art, i) => {
    const file = path.join(OUT, 'content', `${pad3(art.id)}.json`);
    if (!fs.existsSync(file)) return; // 文稿尚未入庫的講次不產生頁面（首頁仍可點，顯示「整理中」）
    const content = JSON.parse(fs.readFileSync(file, 'utf8'));
    const html = render(art, content, { page: true, base: '../../', prev: unlocked[i - 1], next: unlocked[i + 1] });
    const dir = path.join(aDir, pad3(art.id));
    fs.mkdirSync(dir, { recursive: true });
    fs.writeFileSync(path.join(dir, 'index.html'), html);
    count++;
  });

  // 首頁：預先渲染「最新一講」（有文稿者），讓首頁不必等 JS 下載文稿
  const withBody = unlocked.filter(a => fs.existsSync(path.join(OUT, 'content', `${pad3(a.id)}.json`)));
  const latest = withBody[withBody.length - 1];
  let home = template.replace(/<meta name="site-base" content="\.\/">/, '<meta name="site-base" content="./">\n  <script>window.SITE_STATIC=true;</script>');
  if (latest) {
    const content = JSON.parse(fs.readFileSync(path.join(OUT, 'content', `${pad3(latest.id)}.json`), 'utf8'));
    home = render(latest, content, { page: false, base: './' });
  }
  fs.writeFileSync(path.join(OUT, 'index.html'), home);

  // 404：已解鎖之外的講次網址（例如尚未到期的 a/050/）
  const notFound = `<!doctype html>
<html lang="zh-TW"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex"><title>找不到這一頁｜${SITE_TITLE}</title>
<link rel="stylesheet" href="${SITE_PATH}assets/tailwind.css">
<style>:root{--c-paper:250 246 239;--c-ink:42 37 32;--c-seal:168 84 58}@media(prefers-color-scheme:dark){:root{--c-paper:22 19 16;--c-ink:237 230 220;--c-seal:222 134 108}}body{background:rgb(var(--c-paper));color:rgb(var(--c-ink))}</style></head>
<body class="min-h-screen flex items-center justify-center p-6 text-center font-serif">
<main><p class="text-sm tracking-widest mb-3" style="color:rgb(var(--c-seal))">大道至簡</p>
<h1 class="text-3xl font-black mb-3">這一講還沒有點亮</h1>
<p class="mb-8 opacity-80">每天清晨解鎖新的一講，敬請期待。</p>
<a href="${SITE_PATH}" class="inline-flex items-center justify-center min-h-[44px] px-6 rounded-full text-white" style="background:rgb(var(--c-seal))">回到首頁</a></main></body></html>
`;
  fs.writeFileSync(path.join(OUT, '404.html'), notFound);

  console.log(`[build_pages] 產生 ${count} 個講次頁 + 預先渲染首頁（第 ${latest ? latest.id : '-'} 講）+ 404.html`);
}

main();
