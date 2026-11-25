/* Claude样稿的内容渲染，数据由构建流程提取；不改动物种资料和组合检查。 */
(() => {
 const T=window.TANK, page=document.body.dataset.page;
 const e=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 const $=id=>document.getElementById(id),link=f=>`fish-detail.html?id=${encodeURIComponent(f.id)}`;
 document.querySelectorAll('[data-price-date]').forEach(el=>el.textContent=T?.date||el.textContent||'现有');
 const image=(f,cls='',raw=false)=>{const src=raw?f.photo:f.img||f.photo;if(!src)return '';return `<img class="${cls}" src="${e(src)}" alt="${e(f.name)}"${raw||!f.img?` style="width:min(${f.photoWidth||500}px,86vw)"`:''}>`};
 const author=f=>f.credit?`<p class="credit">${e(f.credit.a)} · <a href="${e(f.credit.u)}" target="_blank" rel="noopener">原照片来源</a></p>`:'';
 function initHome(){
  const fish=T.fish.filter(f=>f.n),shown=fish.filter(f=>f.img).sort((a,b)=>b.len-a.len);
  $('lineup-row').innerHTML=shown.flatMap(f=>Array.from({length:f.n},()=>`<a class="fish" href="${link(f)}" style="--len:${f.len}" data-len="${f.len}" data-name="${e(f.name)}"><img src="${e(f.img)}" alt="${e(f.name)}"><b>${e(f.name)}</b><span>${e(f.cm.replace(/（.*）/,''))} cm</span></a>`)).join('');
  for(let n=0;n<=60;n+=10)$('ruler').insertAdjacentHTML('beforeend',`<span class="tick" style="left:${n/60*100}%"><i>${n}</i></span>`);
  const missing=fish.filter(f=>!f.img);$('missing').textContent=missing.length?missing.map(f=>`${f.name}（${f.cm} cm）`).join('、')+' 暂无去背景照片，未列入上方。':'';
  const hl=$('ruler-hl'),cap=$('ruler-cap'),canHover=matchMedia('(hover:hover)').matches;
  const idle=cap.innerHTML=canHover?'指向一条鱼，看它占缸长多少':'点一条鱼查看资料';
  document.querySelectorAll('.fish').forEach(el=>{
   const on=()=>{const n=+el.dataset.len;hl.style.width=`${Math.min(n,60)/60*100}%`;cap.innerHTML=`<b>${e(el.dataset.name)}</b> 成年 ${n} cm，约占缸长 ${Math.round(n/60*100)}%`};
   const off=()=>{hl.style.width=0;cap.innerHTML=idle};
   if(canHover){el.addEventListener('mouseenter',on);el.addEventListener('mouseleave',off)}el.addEventListener('focus',on);el.addEventListener('blur',off);
  });
  const count=fish.reduce((s,f)=>s+f.n,0),sum=fish.reduce((s,f)=>s+(f.price?.lo||0)*f.n,0),noPrice=fish.filter(f=>!f.price).map(f=>f.name),big=fish.reduce((a,b)=>b.len>a.len?b:a);
  $('stats').innerHTML=[
   [`${count}<small>条</small>`,`计划组合，${fish.length} 种。`],
   [`¥${Math.round(sum)}<small>起</small>`,`各品种鱼单最低报价合计${noPrice.length?'；'+noPrice.join('、')+'暂无报价':''}。`],
   [`${big.len}<small>cm</small>`,`组合中最大：${big.name}成年体长，约半个缸长。`],
  ].map(([n,p])=>`<div class="stat center"><div class="stat-num">${n}</div><p>${e(p)}</p></div>`).join('');
  $('zones').innerHTML=['巡游','中层','中下层','洞穴','停栖','底层'].map(z=>{const fs=fish.filter(f=>f.zone===z);return fs.length?`<div class="zone"><dt>${e(z)}</dt><dd>${fs.map(f=>`<a href="${link(f)}">${f.img?`<img src="${e(f.img)}" alt="">`:''}${e(f.name)}${f.n>1?` <em>× ${f.n}</em>`:''}</a>`).join('')}</dd></div>`:''}).join('');
 }
 function priceSection(f){const rows=f.price?.rows||[];return `<section class="sec soft"><div class="narrow"><h2 class="h2">店家报价</h2>${rows.length?`<p class="lead">${f.price.shops} 家店列有这个品种，鱼单最低 ¥${f.price.lo}。</p><table class="prices"><thead><tr><th>价格</th><th>规格</th><th>店铺</th><th class="hide-s">鱼单更新</th></tr></thead><tbody>${rows.map(r=>`<tr><td>¥${e(r.p)}</td><td>${e(r.size||'未标')}<div class="sub">${e(r.name)}${r.note?' · '+e(r.note):''}</div></td><td>${e(r.shop)}<div class="sub">${e(r.loc)}</div></td><td class="hide-s">${e(r.date)}</td></tr>`).join('')}</tbody></table><p class="note">只列库存不为 0 的前 ${rows.length} 条，按价格排序。规格多为体长 cm，店家写法不统一。数据记录 ${e(T.date)}，不含运费。</p>`:'<p class="lead">现有水族名录数据中没有符合展示条件的报价。</p>'}</div></section>`}
 function detail(){
  const id=new URLSearchParams(location.search).get('id')||'clown',f=T.fish.find(x=>x.id===id);
  if(!f){$('species').innerHTML='<section class="sec"><div class="narrow"><h1 class="h2">未找到物种</h1><a class="more back" href="fish.html">鱼类目录 ›</a></div></section>';return}
  document.title=f.name+' · 60缸';
  const specs=[['成年体长',`${f.cm.replace(/（.*）/,'')} cm${/标准体长/.test(f.cm)?'（标准体长，不含尾鳍）':''}`],['活动水层',f.zone],['性格',f.tem],['珊瑚',f.coral],['清洁虾',f.shrimp],['本缸数量',f.n>1?`${f.n} 条（一对）`:f.n?'1 条':'未列入当前组合']];
  $('species').innerHTML=`<header class="sp-hero"><p class="hero-eyebrow">${e(f.zone)} · 成年 ${e(f.cm.replace(/（.*）/,''))} cm</p><h1>${e(f.name)}</h1><p class="sp-sci">${e(f.sci)}${f.alias?`<span style="font-style:normal">　·　${e(f.alias)}</span>`:''}</p>${image(f,f.img?'sp-img':'sp-photo')}</header><section class="sec"><div class="narrow"><h2 class="h2">规格</h2><dl class="specs">${specs.map(([k,v])=>`<div class="spec"><dt>${k}</dt><dd>${e(v)}</dd></div>`).join('')}</dl><div class="step-links"><button class="more" id="detail-pick" data-id="${e(f.id)}"></button><a class="more" href="fish.html#combination">查看组合 ›</a></div><p class="note" id="pick-status" aria-live="polite"></p></div></section>${priceSection(f)}<section class="sec"><div class="narrow"><h2 class="h2">说明</h2><p class="body-text" style="margin-top:32px">${e(f.note)}</p>${f.aq?`<a class="more back" href="${e(f.aq.u)}" target="_blank" rel="noopener">水族名录物种资料 ›</a>`:''}</div></section><section class="sec soft"><div class="narrow center"><h2 class="h2">原始照片</h2>${image(f,'sp-photo',true)}${author(f)}${f.cutoutCredit?`<img class="sp-photo" src="${e(f.cutoutCredit.original)}" alt="${e(f.name)}去背景所用原照片" style="width:min(500px,86vw)"><p class="credit">去背景所用照片：${e(f.cutoutCredit.a)} · <a href="${e(f.cutoutCredit.u)}" target="_blank" rel="noopener">来源</a></p>`:''}<a class="more back" href="index.html#lineup">回到当前组合 ›</a></div></section>`;
  updateDetail();$('detail-pick').onclick=()=>{const n=pick[f.id]||0;pick[f.id]=n?0:(byId[f.id].unit||1);if(!pick[f.id])delete pick[f.id];save();updateDetail();$('pick-status').textContent='当前预览组合 '+check().N+' 条；未改变采购记录。'};
 }
 function updateDetail(){const b=$('detail-pick');if(!b)return;const n=pick[b.dataset.id]||0;b.textContent=n?`已加入 ${n} 条 · 移出组合 ›`:(byId[b.dataset.id].unit?'加入一对 ›':'加入组合 ›');b.setAttribute('aria-pressed',!!n)}
 function catalog(){
  const input=$('catalog-search');input.oninput=()=>{const q=input.value.trim().toLowerCase();let count=0;document.querySelectorAll('.catalog-group').forEach(g=>{let n=0;g.querySelectorAll('.catalog-row').forEach(r=>{const show=r.dataset.search.includes(q);r.hidden=!show;if(show)n++});g.hidden=n===0;count+=n});$('catalog-count').textContent=count};
  renderCombo();$('combo-presets').innerHTML=PRESETS.map((p,i)=>`<button class="more" data-preset-choice="${i}">${e(p.n)} ›</button>`).join('');
  document.addEventListener('click',ev=>{const b=ev.target.closest('[data-combo-id]'),p=ev.target.closest('[data-preset-choice]');if(b){const id=b.dataset.comboId;pick[id]=Math.max(0,(pick[id]||0)+Number(b.dataset.delta)*(byId[id].unit||1));if(!pick[id])delete pick[id];save();renderCombo()}if(p){pick={...PRESETS[+p.dataset.presetChoice].p};save();renderCombo()}});
 }
 function renderCombo(){
  const {N,W}=check();$('combo-count').textContent=N+' 条；只用于组合预览，不改变采购记录。';
  const ids=Object.keys(pick).filter(id=>byId[id]).sort((a,b)=>byId[a].ord-byId[b].ord);
  $('combo-list').innerHTML=ids.map(id=>`<div class="spec"><dt><a href="fish-detail.html?id=${e(id)}">${e(byId[id].cn.split('（')[0])}</a></dt><dd class="combo-quantity"><button class="more" data-combo-id="${e(id)}" data-delta="-1" aria-label="减少${e(byId[id].cn)}">−</button><span>${pick[id]} 条</span><button class="more" data-combo-id="${e(id)}" data-delta="1" aria-label="增加${e(byId[id].cn)}">＋</button></dd></div>`).join('')||'<div class="spec"><dt>组合数量</dt><dd>0 条</dd></div>';
  $('combo-warnings').innerHTML=W.map(([k,t])=>`<li>${e(t)}</li>`).join('');
 }
 function searchCatalog(){
  const input=$('catalog-search'),rows=[...document.querySelectorAll('.catalog-row')],chips=[...document.querySelectorAll('[data-tag-filter]')];let tag='all';
  const apply=()=>{const q=input.value.trim().toLowerCase();let count=0;rows.forEach(r=>{const show=(tag==='all'||r.dataset.tag===tag)&&r.dataset.search.includes(q);r.hidden=!show;if(show)count++});$('catalog-count').textContent=count;chips.forEach(c=>c.setAttribute('aria-pressed',String(c.dataset.tagFilter===tag)))};
  input.oninput=apply;chips.forEach(c=>c.onclick=()=>{tag=c.dataset.tagFilter;apply()});apply();
 }
 const C=window.CORAL_DATA,cd=C?.data,corals=cd?.条目||[],cBy=Object.fromEntries(corals.map(c=>[c.id,c]));
 const load=(key,fallback)=>{try{return JSON.parse(localStorage.getItem(key))??fallback}catch{return fallback}};
 let favorites=new Set(Array.isArray(load('coral_favorites',[]))?load('coral_favorites',[]):[]),comparison=load('coral_compare',[]);
 if(!Array.isArray(comparison))comparison=[];comparison=comparison.filter(id=>cBy[id]).slice(0,4);
 const cImages=c=>C.images[c.id]||[],cPhoto=im=>'assets/coral-reference/'+encodeURIComponent(im.文件.split('/').pop());
 const coralDisplay=id=>'assets/coral-display/'+encodeURIComponent(id)+'.webp?v='+encodeURIComponent(window.SITE_VERSION);
 function coralPrices(c){
  const rows=(Array.isArray(c.价格)?c.价格:[]).filter(r=>String(r.库存)!=='0').sort((a,b)=>Number(a.价格)-Number(b.价格));
  return `<section class="sec soft"><div class="narrow"><h2 class="h2">店家报价</h2>${rows.length?`<p class="lead">公开鱼单最低 ¥${rows[0].价格}。</p><table class="prices"><thead><tr><th>价格</th><th>规格</th><th>店铺</th><th class="hide-s">鱼单更新</th></tr></thead><tbody>${rows.map(r=>`<tr><td>¥${e(r.价格)}</td><td>${e(r.规格||'未标')}<div class="sub">${e(r.店内叫法)}</div></td><td>${e(r.店铺)}<div class="sub">${e(r.发货地)}</div></td><td class="hide-s">${e(r.鱼单更新时间)}</td></tr>`).join('')}</tbody></table><p class="note">${e(rows.map(r=>r.边界).filter((v,i,a)=>a.indexOf(v)===i).join('。'))}</p>`:`<p class="lead">${Array.isArray(c.价格)?'暂无有货报价':'尚未核价'}</p>`}<p class="note">${e(c.价格状态)}</p></div></section>`;
 }
 function coralDetail(){
  const id=new URLSearchParams(location.search).get('id'),c=cBy[id];if(!c){$('species').innerHTML='<section class="sec"><div class="narrow"><h1 class="h2">未找到珊瑚资料</h1><a class="more back" href="corals.html">珊瑚目录 ›</a></div></section>';return}
  document.title=c.中文名+' · 60缸';const im=cImages(c)[0],fields=[['养护分组',c.水族分组],['外观',c.外观筛选.join('、')],['光照',c.光照],['水流',c.水流],['本缸标签',(c.本缸标签||'可以考虑')+' · 未购买']];
  const descriptions=['喂食','长大后的空间','混养与攻击','选购检查','常见问题','本缸安排'];
  const cases=c.论坛案例.map(id=>cd.论坛案例[id]).filter(Boolean).map(x=>`<div class="spec"><dt><a class="more" href="${e(x.网址)}" target="_blank" rel="noopener">${e(x.标题)} ›</a><p class="note">${e(x.作者)} · ${e(x.发表日期)}</p></dt><dd><p>${e(x.实际记录)}</p><p class="note">本缸取舍：${e(x.本缸取舍)}</p><p class="note">适用边界：${e(x.适用边界)}</p><details class="note"><summary>阅读范围</summary><p>${e(x.阅读范围)}</p>${x.后续网址?`<a class="more" href="${e(x.后续网址)}" target="_blank" rel="noopener">作者后续 ›</a>`:''}</details></dd></div>`).join('');
  const sources=c.来源.map(id=>cd.来源[id]).filter(Boolean).map(x=>`<li><a class="more" href="${e(x.网址)}" target="_blank" rel="noopener">${e(x.标题)} ›</a><p class="note">${e(x.类型)} · ${e(x.阅读范围)}</p></li>`).join('');
  $('species').innerHTML=`<header class="sp-hero"><p class="hero-eyebrow">${e(c.水族分组)}</p><h1>${e(c.中文名)}</h1><p class="sp-sci">${e(c.学名或鉴别范围)}</p>${im?`<img class="sp-photo" src="${e(coralDisplay(id))}" alt="${e(c.中文名)}" fetchpriority="high" decoding="async">`:''}</header><section class="sec"><div class="narrow"><h2 class="h2">规格</h2><dl class="specs">${fields.map(([k,v])=>`<div class="spec"><dt>${e(k)}</dt><dd>${e(v)}</dd></div>`).join('')}</dl><div class="step-links"><button class="more" id="coral-save" data-id="${e(id)}"></button><button class="more" id="coral-compare-toggle" data-id="${e(id)}"></button><a class="more" href="coral-compare.html">查看比较 ›</a></div><p id="coral-status" class="note" aria-live="polite"></p></div></section>${coralPrices(c)}<section class="sec"><div class="narrow"><h2 class="h2">说明</h2><p class="body-text" style="margin-top:32px">${e(c.外观与辨别)}</p><dl class="specs">${descriptions.map(k=>`<div class="spec"><dt>${e(k)}</dt><dd>${e(c[k])}</dd></div>`).join('')}</dl>${cases?`<h2 class="h2 detail-subheading">实养记录</h2><dl class="specs coral-cases">${cases}</dl>`:''}<h2 class="h2 detail-subheading">资料来源</h2><ul class="source-list">${sources}</ul></div></section><section class="sec soft"><div class="narrow center"><h2 class="h2">参考照片</h2>${im?`<a href="${e(cPhoto(im))}" target="_blank" rel="noopener" aria-label="查看${e(c.中文名)}的原始照片"><img class="sp-photo" src="${e(coralDisplay(id))}" alt="${e(c.中文名)}的参考照片" loading="lazy" decoding="async"></a><p class="credit">${e(im.原标名称)} · <a href="${e(im.来源页)}" target="_blank" rel="noopener">${e(im.摄影者||new URL(im.来源页).hostname)}</a> · ${im.许可链接?`<a href="${e(im.许可链接)}" target="_blank" rel="noopener">${e(im.许可)}</a>`:'版权归原作者'}${im.图像处理?' · '+e(im.图像处理):''} · 物种参考照片。</p>`:'<p class="note">本条目未收录合格参考照片。外观资料见上方原始来源。</p>'}<a class="more back" href="corals.html">返回珊瑚目录 ›</a></div></section>`;
  updateCoral();$('coral-save').onclick=()=>{favorites.has(id)?favorites.delete(id):favorites.add(id);localStorage.setItem('coral_favorites',JSON.stringify([...favorites]));updateCoral()};$('coral-compare-toggle').onclick=()=>{if(comparison.includes(id))comparison=comparison.filter(x=>x!==id);else if(comparison.length<4)comparison.push(id);else{$('coral-status').textContent='最多比较4类，先从比较页移出一类。';return}localStorage.setItem('coral_compare',JSON.stringify(comparison));$('coral-status').textContent='';updateCoral()};
 }
 function updateCoral(){const a=$('coral-save'),b=$('coral-compare-toggle');a.textContent=favorites.has(a.dataset.id)?'已收藏 · 移出 ›':'收藏候选 ›';a.setAttribute('aria-pressed',favorites.has(a.dataset.id));b.textContent=comparison.includes(b.dataset.id)?'已选比较 · 移出 ›':'加入比较 ›';b.setAttribute('aria-pressed',comparison.includes(b.dataset.id))}
 function coralComparison(){
  const raw=new URLSearchParams(location.search).get('ids'),ids=(raw?raw.split(','):comparison).filter(id=>cBy[id]).slice(0,4),picked=ids.map(id=>cBy[id]);
  const fields=['水族分组','光照','水流','喂食','长大后的空间','混养与攻击','本缸安排'];
  $('coral-comparison').innerHTML=picked.length?picked.map(c=>`<section class="coral-comparison-item"><h2 class="h2"><a href="coral-detail.html?id=${e(c.id)}">${e(c.中文名)}</a></h2><dl class="specs">${fields.map(k=>`<div class="spec"><dt>${e(k)}</dt><dd>${e(c[k])}</dd></div>`).join('')}</dl><button class="more back" data-remove-coral="${e(c.id)}">移出比较 ›</button></section>`).join(''):'<p class="lead">尚未选择比较对象。可在珊瑚详情加入，最多4类。</p>';
  document.querySelectorAll('[data-remove-coral]').forEach(b=>b.onclick=()=>{comparison=comparison.filter(x=>x!==b.dataset.removeCoral);localStorage.setItem('coral_compare',JSON.stringify(comparison));if(raw){const next=ids.filter(x=>x!==b.dataset.removeCoral);history.replaceState(null,'','coral-compare.html'+(next.length?'?ids='+next.join(','):''))}coralComparison()});
 }
 if(T&&page==='home')initHome();if(T&&page==='fish-detail')detail();if(T&&page==='fish-catalog')catalog();if(page==='coral-catalog')searchCatalog();if(page==='coral-detail')coralDetail();if(page==='coral-compare')coralComparison();
})();
