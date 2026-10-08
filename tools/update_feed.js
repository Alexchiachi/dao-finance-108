const fs = require('fs');
const path = require('path');

// 取得當前 UTC+8 日期字串
function getTodayString() {
  const now = new Date();
  const utc8 = new Date(now.getTime() + (now.getTimezoneOffset() + 480) * 60000);
  return utc8.toISOString().split('T')[0];
}

const today = getTodayString();
const rootDir = path.resolve(__dirname, '..');
const manifestPath = path.join(rootDir, 'manifest.json');
const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));

// 篩選出今天（含）以前已解鎖的文章
const unlockedArticles = manifest.filter(a => a.isInitialBatch || a.releaseDate <= today);

console.log(`[RSS/Sitemap Update] 截至今日 (${today})，已解鎖篇數: ${unlockedArticles.length} / 108`);

// 生成 RSS 2.0 (feed.xml)
let rssItems = '';
unlockedArticles.forEach(art => {
  const pubDate = new Date(art.releaseDate + 'T00:00:00+08:00').toUTCString();
  rssItems += `
    <item>
      <title><![CDATA[第 ${String(art.id).padStart(3, '0')} 講｜${art.title}]]></title>
      <link>https://alexchiachi.github.io/dao-finance-108/#/${String(art.id).padStart(3, '0')}</link>
      <guid>https://alexchiachi.github.io/dao-finance-108/#article-${art.id}</guid>
      <pubDate>${pubDate}</pubDate>
      <description><![CDATA[${art.volName} · 台灣南投與中國雲南雙基地風土 · 大道至簡金融一百零八講]]></description>
    </item>`;
});

const rssContent = `<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
  <channel>
    <title>大道至簡・金融一百零八講</title>
    <link>https://alexchiachi.github.io/dao-finance-108/</link>
    <description>當金融遇見老莊、AI與雙基地風土。前基金經理人的破妄與善活錄。</description>
    <language>zh-TW</language>
    <lastBuildDate>${new Date().toUTCString()}</lastBuildDate>
    ${rssItems}
  </channel>
</rss>
`;

fs.writeFileSync(path.join(rootDir, 'feed.xml'), rssContent.trim());
console.log('✅ 已更新 feed.xml');

// 生成 sitemap.xml
let urlEntries = `
  <url>
    <loc>https://alexchiachi.github.io/dao-finance-108/</loc>
    <lastmod>${today}</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>`;

unlockedArticles.forEach(art => {
  urlEntries += `
  <url>
    <loc>https://alexchiachi.github.io/dao-finance-108/#/${String(art.id).padStart(3, '0')}</loc>
    <lastmod>${art.releaseDate}</lastmod>
    <changefreq>never</changefreq>
    <priority>0.8</priority>
  </url>`;
});

const sitemapContent = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urlEntries}
</urlset>
`;

fs.writeFileSync(path.join(rootDir, 'sitemap.xml'), sitemapContent.trim());
console.log('✅ 已更新 sitemap.xml');
