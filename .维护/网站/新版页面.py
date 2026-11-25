"""Claude样稿的页面移植；项目原始物种、价格和组合规则均由原数据维护。"""
from pathlib import Path
import re, json, html
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'资料/交付/网站'
VERSION='20261106-claude-v1'
CORAL_VERSION='20261113-coral-webp'
PRICE_DATE=''
NAV=[('fish.html','鱼'),('corals.html','珊瑚'),('algae.html','藻类图鉴'),('guide-timeline.html','养护'),('buy.html','采购'),('kb/index.html','知识库'),('assembly.html','装配'),('records.html','记录'),('decisions.html','决定')]

def esc(s):return html.escape(str(s),quote=True)

def links(base='',active=''):
    return ''.join(f'<a href="{base}{u}"'+(' aria-current="page"' if u==active else '')+f'>{t}</a>' for u,t in NAV)

def shell(title,body,active='fish.html',base='',script='',desc='',page='',stylesheet=''):
    version=CORAL_VERSION if page.startswith('coral-') else VERSION
    extra_style=f'<link rel="stylesheet" href="{esc(base+stylesheet)}">' if stylesheet else ''
    return f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#000"><title>{esc(title)} · 60缸</title><meta name="description" content="{esc(desc)}"><link rel="stylesheet" href="{base}assets/style.css?v={version}">{extra_style}</head><body data-page="{page}"><a class="skip" href="#main">跳到正文</a><nav class="nav" aria-label="主导航"><div class="nav-in"><a class="brand" href="{base}index.html">60缸</a><div class="nav-links">{links(base,active)}</div></div></nav><main id="main">{body}</main><footer class="foot"><div class="narrow"><div class="foot-links"><a href="{base}fish.html">鱼类目录</a>{links(base)}</div><p>照片为物种参考，作者与许可见详情；去背景为 AI 辅助处理。报价来自水族名录商城，<span data-price-date>{esc(PRICE_DATE)}</span>数据记录，规格与库存按店家鱼单。</p></div></footer><script>window.SITE_BASE={json.dumps(base)};window.SITE_VERSION={json.dumps(version)};</script>{script}</body></html>'''

def progress():
    text=(ROOT/'01-待办.md').read_text()
    sections=re.findall(r'^## (.+)\n([\s\S]*?)(?=^## |\Z)',text,re.M)[:3]
    rows=[]
    for i,(title,body) in enumerate(sections):
        names=re.findall(r'^- \[ \] \*\*(.+?)\*\*',body,re.M)[:3]
        names=[re.sub(r'（[^）]*）','',x).rstrip('：:') for x in names]
        rows.append({'label':['现在','下一步','之后'][i],'title':re.split('[:：]',title,maxsplit=1)[-1],'text':'、'.join(names)+'。'})
    return {'date':re.search(r'更新：(\d{4}-\d\d-\d\d)',text).group(1),'steps':rows}

def home(data):
    template=(SRC/'模板/首页.html').read_text()
    body=template[template.index('<header class="hero">'):template.index('<footer class="foot">')]
    fish=[f for f in data['fish'] if f['n']]
    body=body.replace('计划 9 种 10 条',f'计划 {len(fish)} 种 {sum(f["n"] for f in fish)} 条')
    body=body.replace('src="img/clown.webp"','src="assets/fish-cutouts/clown.webp"')
    clown=next(f for f in fish if f['id']=='clown')
    credit=clown.get('credit')
    if credit:
        author=credit['a'].removeprefix('(c) ').split(',')[0]
        license=re.search(r'CC BY[^)]*',credit['a'])
        cap=f'公子小丑。照片去背景，原图 <a href="{esc(credit["u"])}" target="_blank" rel="noopener">{esc(author)}</a>（{esc(license.group(0) if license else "版权归原作者")}）。'
        body=re.sub(r'(<p class="hero-cap">)[\s\S]*?(</p>)',lambda m:m[1]+cap+m[2],body)
    body=body.replace('href="#">鱼类目录','href="fish.html">鱼类目录')
    body=body.replace('href="#">完整时间表','href="guide-timeline.html">完整时间表').replace('href="#">采购清单','href="buy.html">采购清单')
    p=progress()
    steps=''.join(f'<div class="step{" now" if i==0 else ""}"><p class="step-label">{s["label"]}</p><h3>{esc(s["title"])}</h3><p>{esc(s["text"])}</p></div>' for i,s in enumerate(p['steps']))
    body=re.sub(r'<div class="steps">[\s\S]*?</div>\s*<div class="step-links">',lambda _:f'<div class="steps">{steps}</div><div class="step-links">',body)
    body=re.sub(r'<p class="lead">2026 年 11 月 5 日。全部活体尚未购买。</p>',f'<p class="lead">待办记录更新 {p["date"]}。完成状态按现场回填。</p>',body)
    return shell('60缸',body,script=f'<script src="assets/tank-data.js?v={VERSION}"></script><script src="assets/presentation.js?v={VERSION}"></script>',page='home')

def fish_detail():
    return shell('鱼类详情','<div id="species"></div>',script=f'<script src="assets/tank-data.js?v={VERSION}"></script><script src="img/credits.js"></script><script src="img/mall.js"></script><script src="img/aquaml.js"></script><script src="assets/app.js?v={VERSION}"></script><script src="assets/presentation.js?v={VERSION}"></script>',page='fish-detail')

def fish_catalog(data):
    groups=[]
    order=['巡游','中层','中下层','洞穴','停栖','底层']
    order+=sorted({f['zone'] for f in data['fish']}-set(order))
    for zone in order:
        rows=[]
        for f in data['fish']:
            if f['zone']!=zone:continue
            terms=' '.join(str(f.get(k,'')) for k in ['cn','sci'])+' '+str(f.get('aq') or '')
            art=f'<span class="row-art"><img src="{esc(f["img"])}" style="--len:{f["len"]}" alt=""></span>' if f['img'] else ''
            price=f'¥{f["price"]["lo"]} 起' if f['price'] else '暂无报价'
            cm=re.sub(r'（.*?）','',f['cm'])
            rows.append(f'<a class="catalog-row{" has-art" if art else ""}" data-search="{esc(terms.lower())}" href="fish-detail.html?id={esc(f["id"])}">{art}<span class="row-name"><b>{esc(f["name"])}</b><span class="sub">{esc(f["sci"])}</span></span><span class="row-length" title="{esc(f["cm"])}">{esc(cm)} cm</span><span class="row-price">{esc(price)}</span></a>')
        if rows:groups.append(f'<div class="zone catalog-group"><dt>{esc(zone)}</dt><dd>{"".join(rows)}</dd></div>')
    body=f'''<section class="sec catalog"><div class="narrow"><h1 class="h2">鱼类目录</h1><label class="search"><span>搜索鱼名、学名或店名</span><input type="search" id="catalog-search" placeholder="搜索" autocomplete="off"></label><p class="note"><span id="catalog-count">{len(data['fish'])}</span> 种。按活动水层分组；成年体长和最低报价见各条详情。</p><dl class="zones">{''.join(groups)}</dl><p class="note">报价记录 {esc(data['date'])}，筛选库存不为0的鱼单；规格、鱼单更新时间和来源见详情。不含运费。</p></div></section><section class="sec soft" id="combination"><div class="narrow"><h2 class="h2">当前预览组合</h2><p class="lead" id="combo-count"></p><dl class="specs" id="combo-list"></dl><h3 class="combo-subtitle">组合检查</h3><ul id="combo-warnings" class="combo-warnings"></ul><details class="preset-list"><summary>现成组合</summary><div id="combo-presets"></div></details></div></section>'''
    scripts=f'<script src="assets/tank-data.js?v={VERSION}"></script><script src="img/credits.js"></script><script src="img/mall.js"></script><script src="img/aquaml.js"></script><script src="assets/app.js?v={VERSION}"></script><script src="assets/presentation.js?v={VERSION}"></script>'
    return shell('鱼类目录',body,script=scripts,page='fish-catalog')

def coral_images(data):
    review=json.loads((ROOT/'.维护/网站/照片检查.json').read_text())
    clean={r['path'] for r in review['记录'] if r['结论']=='可用'}
    return {c['id']:[im for im in c['图片'] if im['文件'] in clean and (ROOT/im['文件']).is_file()] for c in data['条目']}

CORAL_TAGS=[('打算养','plan'),('可以考虑','maybe'),('难养','hard'),('不养','no')]

def coral_catalog(data,images):
    order={t:i for i,(t,_) in enumerate(CORAL_TAGS)};key=dict(CORAL_TAGS);rows=[]
    for c in sorted(data['条目'],key=lambda c:order.get(c.get('本缸标签'),1)):
        tag=c.get('本缸标签','可以考虑')
        art=''
        if images[c['id']]:
            priority='fetchpriority="high"' if not rows else ('loading="lazy"' if len(rows)>=2 else '')
            art=f'<span class="row-art"><img src="assets/coral-thumbs/{esc(c["id"])}.webp?v={CORAL_VERSION}" alt="" class="coral-thumb" {priority} decoding="async"></span>'
        terms=' '.join([c['中文名'],c['学名或鉴别范围'],*c['别名'],*c['外观筛选'],tag]).lower()
        quotes=c['价格'] if isinstance(c['价格'],list) else []
        available=[r for r in quotes if str(r.get('库存','0'))!='0']
        price=f'¥{min(float(r["价格"]) for r in available):g} 起' if available else ('暂无有货价' if quotes else '尚未核价')
        rows.append(f'<a class="catalog-row{" has-art" if art else ""}" data-search="{esc(terms)}" data-tag="{key.get(tag,"maybe")}" href="coral-detail.html?id={esc(c["id"])}">{art}<span class="row-name"><b>{esc(c["中文名"])}</b><span class="ctag ctag-{key.get(tag,"maybe")}">{esc(tag)}</span><span class="sub">{esc(c["学名或鉴别范围"])}</span></span><span class="row-length coral-shape">{esc("、".join(c["外观筛选"][:2]))}</span><span class="row-price">{esc(price)}</span></a>')
    chips=''.join(f'<button type="button" class="ctag-filter" data-tag-filter="{k}" aria-pressed="false">{esc(t)}</button>' for t,k in [('全部','all'),*CORAL_TAGS])
    body=f'<section class="sec catalog"><div class="narrow"><h1 class="h2">珊瑚目录</h1><label class="search"><span>搜索名称、学名或外观</span><input id="catalog-search" type="search" placeholder="搜索" autocomplete="off"></label><div class="ctag-filters" role="group" aria-label="按本缸标签筛选">{chips}</div><p class="note"><span id="catalog-count">{len(data["条目"])}</span> 类。标签是本缸的打算：打算养、可以考虑、难养（失败记录多，不放第一批）、不养。都还没买。</p><div class="catalog-list">{"".join(rows)}</div><a class="more back" href="coral-compare.html">查看珊瑚比较 ›</a></div></section>'
    scripts=f'<script defer src="assets/presentation.js?v={CORAL_VERSION}"></script>'
    return shell('珊瑚目录',body,'corals.html',script=scripts,page='coral-catalog')

def coral_detail():
    scripts=f'<script defer src="assets/coral-data.js?v={CORAL_VERSION}"></script><script defer src="assets/presentation.js?v={CORAL_VERSION}"></script>'
    return shell('珊瑚详情','<div id="species"></div>','corals.html',script=scripts,page='coral-detail')

def coral_compare():
    scripts=f'<script defer src="assets/coral-data.js?v={CORAL_VERSION}"></script><script defer src="assets/presentation.js?v={CORAL_VERSION}"></script>'
    return shell('珊瑚比较','<section class="sec"><div class="narrow"><h1 class="h2">珊瑚比较</h1><div id="coral-comparison"></div><a class="more back" href="corals.html">返回珊瑚目录 ›</a></div></section>','corals.html',script=scripts,page='coral-compare')

def read_page(title,body,active,base='',desc='',nav=''):
    soup=BeautifulSoup(body,'html.parser')
    for el in soup.find_all(style=True):del el['style']
    for el in soup.find_all(['h2']):el['class']=['h2']
    for table in soup.find_all('table'):
        table['class']=['prices']
        rows=table.find_all('tr');headers=[]
        if rows and rows[0].find_all('th'):
            headers=[c.get_text(' ',strip=True) for c in rows[0].find_all(['th','td'],recursive=False)]
            rows[0]['class']=['table-head']
            table['data-columns']=len(headers)
            if '金额' in headers:table['data-money']='true'
            if all(x in headers for x in ['现有','装用','备用']):table['data-quantity']='true'
        for row in rows[1:] if headers else rows:
            for i,cell in enumerate(row.find_all(['td','th'],recursive=False)):
                if i<len(headers) and not cell.get('colspan'):cell['data-label']=headers[i]
    return shell(title,f'<section class="sec reading"><div class="narrow"><h1 class="h2">{esc(title)}</h1>{nav}<article class="prose">{soup}</article></div></section>',active,base,desc=desc,page='reading')
