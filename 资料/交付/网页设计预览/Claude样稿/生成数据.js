// 样稿用的 data.js：当前组合（PRESETS[0]）的物种资料 + 当日最低报价 + 照片署名。
// 这是 2026-11-05 的快照写法，正式站应在 生成网站.py 构建时生成，不要手抄数字。
// 在 Fishplan 根目录运行：node 资料/交付/网页设计预览/Claude样稿/生成数据.js
const fs = require('fs'), vm = require('vm'), path = require('path');
const OUT = path.join(__dirname, 'data.js');

const app = fs.readFileSync('资料/交付/网站/assets/app.js', 'utf8');
const grab = name => {            // 取出 app.js 里的 const F=[...] / const PRESETS=[...]
  const i = app.indexOf(`const ${name}=`), j = app.indexOf('[', i);
  for (let k = j, d = 0; k < app.length; k++) {
    if (app[k] === '[') d++;
    if (app[k] === ']' && !--d) return vm.runInNewContext(app.slice(j, k + 1));
  }
};
const F = grab('F'), PRESETS = grab('PRESETS');
const ctx = { window: {} }; vm.createContext(ctx);
for (const f of ['mall.js', 'credits.js']) vm.runInContext(fs.readFileSync(`.work/site_build/img/${f}`, 'utf8'), ctx);
const MALL = ctx.window.FISH_MALL, CREDITS = Object.values(ctx.window).find(v => v && v.clown && v.clown.a);
const cut = new Set(fs.readdirSync(path.join(__dirname, 'img')).map(f => f.replace('.webp', '')));

const fish = Object.entries(PRESETS[0].p).map(([id, n]) => {
  const f = F.find(x => x.id === id), m = MALL.by[id];
  const rows = m ? m.rows.filter(r => r[5] !== '0').sort((a, b) => a[0] - b[0]).slice(0, 8)
    .map(r => ({ p: r[0], size: r[1], shop: r[2], loc: r[3], date: r[4], stock: r[5], name: r[6], note: r[7] })) : [];
  const [name, alias] = f.cn.replace('）', '').split('（');
  const c = CREDITS[id];
  return { id, n, name, alias: alias || '', sci: f.sci, len: f.len, cm: f.cm, zone: f.zone, tem: f.tem,
    coral: f.coral, shrimp: f.shrimp, note: f.note, img: cut.has(id) ? `img/${id}.webp` : null, photo: `photo/${id}.jpg`,
    credit: c ? { a: c.a.replace(/\s+/g, ' ').trim(), u: c.u } : null,
    price: rows.length ? { lo: rows[0].p, shops: m.s, rows } : null };
});
fs.writeFileSync(OUT, `window.TANK=${JSON.stringify({ date: MALL.d, fish })};\n`);
console.log(fish.map(f => `${f.id} ${f.name} 抠图:${!!f.img} 最低价:${f.price && f.price.lo}`).join('\n'));
