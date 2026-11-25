// 只读项目物种、组合、报价和署名；构建时输出，筛选规则沿用Claude样稿。
const fs=require('fs'),vm=require('vm'),path=require('path');
const root=path.resolve(__dirname,'../..'),out=path.resolve(process.argv[2]);
const app=fs.readFileSync(path.join(root,'资料/交付/网站/assets/app.js'),'utf8');
function grab(name){
 const start=app.indexOf(`const ${name}=`),j=app.indexOf('[',start);let depth=0,quote='',escape=false;
 for(let k=j;k<app.length;k++){
  const c=app[k];if(quote){if(escape)escape=false;else if(c==='\\')escape=true;else if(c===quote)quote='';continue}
  if(c==='"'||c==="'"){quote=c;continue}if(c==='[')depth++;if(c===']'&&!--depth)return vm.runInNewContext(app.slice(j,k+1));
 }throw Error('不能提取 '+name);
}
const F=grab('F'),presets=grab('PRESETS'),ctx={window:{}};vm.createContext(ctx);
for(const name of ['credits.js','mall.js','aquaml.js'])vm.runInContext(fs.readFileSync(path.join(out,'img',name),'utf8'),ctx);
const mall=ctx.window.FISH_MALL,credits=ctx.window.FISH_IMG,aq=ctx.window.FISH_AQ;
const sourceFile=path.join(out,'assets/fish-cutouts/sources.json'),cutoutSources=fs.existsSync(sourceFile)?JSON.parse(fs.readFileSync(sourceFile,'utf8')):{};
const fish=F.map(f=>{
 const m=mall.by[f.id],rows=m?m.rows.filter(r=>r[5]!=='0').sort((a,b)=>a[0]-b[0]).slice(0,8).map(r=>({p:r[0],size:r[1],shop:r[2],loc:r[3],date:r[4],stock:r[5],name:r[6],note:r[7]})):[];
 const [name,alias]=f.cn.replace('）','').split('（'),c=credits[f.id],cut=`assets/fish-cutouts/${f.id}.webp`;
 return {...f,n:presets[0].p[f.id]||0,name,alias:alias||'',img:fs.existsSync(path.join(out,cut))?cut:null,photo:c&&fs.existsSync(path.join(out,'img',c.f))?'img/'+c.f:null,credit:c?{a:c.a.replace(/\s+/g,' ').trim(),u:c.u}:null,cutoutCredit:cutoutSources[f.id]?{a:cutoutSources[f.id].a,u:cutoutSources[f.id].u,original:cutoutSources[f.id].original}:null,aq:aq[f.id]||null,price:rows.length?{lo:rows[0].p,shops:m.s,rows}:null};
});
fs.writeFileSync(path.join(out,'assets/tank-data.json'),JSON.stringify({date:mall.d,fish,presets}));
console.log('构建物种 '+fish.length+'，当前组合 '+fish.filter(f=>f.n).length+' 种');
