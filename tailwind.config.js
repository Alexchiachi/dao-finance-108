// 顏色以 CSS 變數（RGB 通道）提供，定義在 index.html 的 :root，
// 這樣「調美感」自動化只需改寫變數，不必重新編譯 CSS。
const c = (name) => `rgb(var(--c-${name}) / <alpha-value>)`;

module.exports = {
  content: ['./index.html', './assets/render.js', './tools/build_pages.js'],
  theme: {
    extend: {
      colors: {
        paper: c('paper'),
        ink: c('ink'),
        tea: c('tea'),
        moss: c('moss'),
        seal: c('seal'),
        gold: c('gold'),
        surface: c('surface'),
        sunken: c('sunken'),
        wash1: c('wash1'),
        wash2: c('wash2'),
        wash3: c('wash3'),
        wash4: c('wash4'),
        wash5: c('wash5'),
      },
      fontFamily: {
        serif: ['"Noto Serif TC"', '"Songti TC"', '"Songti SC"', 'serif'],
        sans: ['-apple-system', 'BlinkMacSystemFont', '"SF Pro Text"', '"PingFang TC"', '"Noto Sans TC"', 'system-ui', 'sans-serif'],
      },
    },
  },
};
