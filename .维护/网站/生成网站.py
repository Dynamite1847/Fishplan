#!/usr/bin/env python3
"""以Claude样稿构建全站；原始物种、报价、组合规则和模型文件不在此维护。
默认输出.work/site_build，由.维护/网站/发布网站.sh发布到既有服务器。
"""
from pathlib import Path
from urllib.parse import unquote,quote
import argparse,html,json,os,re,shutil,subprocess,sys,base64
ASSET_VERSION="20261106-assembly-light-v2"
import markdown
from bs4 import BeautifulSoup
from PIL import Image, ImageOps
import 新版页面 as 新版
import 记录页面
sys.path.insert(0,str(Path(__file__).parent/"记录服务"))
from guide import render as render_care_rules

ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'资料/交付/网站'
KB=ROOT/'海水养殖知识库'
IMG=ROOT/'资料/交付/选鱼图片'
CORAL_IMG=ROOT/'资料/参考图/珊瑚'
ALGAE=ROOT/'资料/交付/藻类图鉴'
ALGAE_ARTICLE='海缸藻类速查：哪些留着，哪些要清'
OUT=ROOT/'.work/site_build'
GUIDES=[('timeline','养护时间表'),('qt','检疫桶养水'),('main','主缸安装与养水'),('quar','检疫观察'),('sand','砂与虾虎窝'),('feed','投喂')]

def fragment(name):
    text=render_care_rules((SRC/'指南'/f'{name}.html').read_text())
    return re.sub(r'<!--(title|lead):.*?-->\n?','',text)

def reading_nav(items,current):
    return '<nav class="reading-nav" aria-label="阅读目录">'+''.join(f'<a href="{新版.esc(u)}"'+(' aria-current="page"' if u==current else '')+f'>{新版.esc(t)}</a>' for u,t in items)+'</nav>'

def build_guides():
    items=[(f'guide-{key}.html',title) for key,title in GUIDES]
    return {f'guide-{key}.html':新版.read_page(title,fragment(key),'guide-timeline.html',nav=reading_nav(items,f'guide-{key}.html')) for key,title in GUIDES}

def kb_articles():
    cats = []
    for ci, d in enumerate(sorted(p for p in KB.iterdir() if p.is_dir())):
        m = re.match(r"(\d+)-(.+)", d.name)
        arts = []
        article_number = 1
        for f in sorted(d.glob("*.md")):
            if f.stem == ALGAE_ARTICLE:
                # 新文章使用独立地址，避免挪动现有藻害文章的公开链接。
                path = 'algae-guide.html'
            else:
                path = f"c{ci+1:02d}-a{article_number:02d}.html"
                article_number += 1
            arts.append({"path": f, "out": path, "title": f.stem})
        cats.append({"no": m.group(1), "name": m.group(2), "dir": d, "arts": arts})
    return cats

def render_md(text, src, pathmap):
    text = re.sub(r"^# .*\n", "", text, count=1)
    text = re.sub(r"^\*\*主题标签：\*\*.*$", "", text, flags=re.M)
    h = markdown.markdown(text, extensions=["tables", "sane_lists"])
    def link(m):
        href, label = m.group(1), m.group(2)
        if re.match(r"https?://", href):
            if re.fullmatch(r"\d+", label):
                return f'<sup class="fn"><a href="{href}" target="_blank" rel="noopener">{label}</a></sup>'
            return f'<a href="{href}" target="_blank" rel="noopener">{label}</a>'
        target = unquote(href.split("#")[0])
        if target.endswith(".md"):
            p = os.path.normpath(os.path.join(src.parent, target))
            if p in pathmap:
                return f'<a href="{pathmap[p]}">{label}</a>'
            return label
        return label
    h = re.sub(r'<a href="([^"]+)">(.*?)</a>', link, h)
    def coral_image(m):
        target = html.unescape(unquote(m.group(1)))
        if re.match(r"https?://", target):
            return m.group(0)
        image_path = (src.parent / target).resolve()
        if image_path.parent == CORAL_IMG.resolve() and image_path.is_file():
            return 'src="../assets/coral-reference/' + quote(image_path.name) + '"'
        return m.group(0)
    h = re.sub(r'src="([^"]+)"', coral_image, h)
    h = h.replace("<table>", '<div class="tw"><table>').replace("</table>", "</table></div>")
    return h

def build_kb(cats):
    out={}
    pathmap={os.path.normpath(str(a['path'])):a['out'] for c in cats for a in c['arts']}
    grid=''.join(f'<section class="kb-category"><h2 class="h2">{新版.esc(c["name"])}</h2><ul>'+''.join(f'<li><a class="more" href="{a["out"]}">{新版.esc(a["title"])} ›</a></li>' for a in c['arts'])+'</ul></section>' for c in cats)
    count=sum(len(c['arts']) for c in cats)
    out['kb/index.html']=新版.read_page('知识库',f'<p class="lead">{len(cats)} 个主题，{count} 篇文章。</p>'+grid,'kb/index.html',base='../')
    for c in cats:
        for a in c['arts']:
            text=a['path'].read_text();m=re.match(r'# (.+)',text);title=m.group(1).strip() if m else a['title']
            nav=reading_nav([('index.html','知识库'),*[(x['out'],x['title']) for x in c['arts']]],a['out'])
            body=render_md(text,a['path'],pathmap)
            if a['title']==ALGAE_ARTICLE:
                body='<p><a class="more" href="../algae.html">查看藻类图鉴 ›</a></p>'+body
            out['kb/'+a['out']]=新版.read_page(title,body,'kb/index.html',base='../',nav=nav)
    return out


def build_algae_atlas(guide_url):
    source = BeautifulSoup((ALGAE/'藻类图鉴.html').read_text(encoding='utf-8'), 'html.parser')
    hero = source.body.header
    hero['class'] = ['hero', 'algae-hero']
    hero.div['class'] = ['narrow']
    hero.p['class'] = ['hero-sub']
    toc = source.body.nav
    toc['class'] = ['algae-jumps']
    toc['aria-label'] = '图鉴目录'
    toc.b.decompose()
    toc.div.unwrap()
    hero.div.append(toc)

    image_dir = OUT/'assets/algae'
    image_dir.mkdir()
    for figure in source.find_all('figure'):
        if '仅本地参考' in figure.figcaption.get_text():
            figure.decompose()
            continue
        image = figure.img
        name = Path(image['src']).name
        shutil.copy2(ALGAE/'img'/name, image_dir/name)
        image['src'] = 'assets/algae/'+quote(name)

    sections = source.body.find_all('section', recursive=False)
    for section in sections:
        section['class'] = ['sec', 'soft'] if 'g' in section['class'] else ['sec']
        section.div['class'] = ['narrow']
    for article in source.find_all('article', class_='sp'):
        photo = article.find('div', class_='ph')
        if photo.find('figure'):
            article['class'].append('has-photo')
        else:
            photo.decompose()

    table = source.select_one('#check table')
    table['class'] = ['algae-identification']
    for row in table.find_all('tr'):
        row.td.name = 'th'
        row.th['scope'] = 'row'
    guide = source.select_one('#tank .srcs')
    guide.string = guide.get_text().split('文字版', 1)[0]
    guide_link = source.new_tag('a', href=guide_url)
    guide_link.string = ALGAE_ARTICLE+' ›'
    guide.append(guide_link)

    credits = source.body.footer
    for item in credits.find_all('li'):
        if '仅本地参考' in item.get_text():
            item.decompose()
    credits.p.string = credits.p.get_text().split('；金箔藻图', 1)[0]+'。'
    for heading in credits.find_all('h4'):
        heading.name = 'h3'
    credits.name = 'section'
    credits['class'] = ['sec', 'algae-sources']
    credits.div['class'] = ['narrow']
    heading = source.new_tag('h2', attrs={'class': 'h2'})
    heading.string = '照片与资料'
    credits.div.insert(0, heading)

    body = '<div class="algae-atlas">'+str(hero)+''.join(map(str, sections))+str(credits)+'</div>'
    return 新版.shell(source.title.string, body, 'algae.html', page='algae',
                     desc=hero.p.get_text(), stylesheet='assets/algae.css')


def build_assembly():
    body = """
<link rel="stylesheet" href="assets/assembly.css">
<div class="assembly-page">
<div class="assembly-work">
<div class="assembly-stage">
<div id="assembly-viewport" aria-label="可旋转管路模型"><div id="assembly-status" role="status"><p>正在加载管路模型</p></div><div id="assembly-labels" aria-hidden="true"></div><span class="assembly-axis" aria-hidden="true">拖动旋转 · 滚轮或双指缩放</span><div class="assembly-presets" role="group" aria-label="模型视角"><button data-view="front" aria-pressed="true">正视</button><button data-view="right" aria-pressed="false">侧视</button><button data-view="top" aria-pressed="false">俯视</button></div><div id="assembly-part" class="assembly-part" aria-live="polite" hidden></div></div>
</div>
<aside class="assembly-panel" aria-label="管路装配步骤">
<header class="assembly-heading"><h1>管路装配</h1><p id="assembly-total">3 条管路 · 19 步</p></header>
<div id="assembly-routes" class="assembly-routes" role="group" aria-label="选择管路"></div>
<section class="assembly-guide">
<div class="assembly-progress" id="assembly-top"><span id="assembly-progress-text">正在读取步骤</span><div><i id="assembly-progress-bar"></i></div></div>
<div id="assembly-instruction" aria-live="polite"></div>
<div class="assembly-stepnav"><button id="assembly-prev" disabled>‹ 上一步</button><button id="assembly-next" class="assembly-next" disabled>下一步 ›</button></div>
<div class="assembly-stepdetails"><p class="assembly-steps-label">全部步骤 <span id="assembly-step-count"></span></p><ol id="assembly-steps"></ol></div>
</section>
</aside>
</div>
<section class="sec assembly-ref assembly-colors"><div class="narrow"><h2 class="assembly-h2">实物配色</h2><div class="assembly-legend" aria-label="管路与管件实物配色"></div><h3 class="assembly-sublabel">透明观察管</h3><div id="assembly-clear-parts"></div><p class="note">微调阀近黑灰＋红柄，止回阀白＋透明。透明件加深轮廓便于辨认。孔下两段约60mm，主排／应急尾管264／284mm，上水主管100mm、前后各140mm；为模型本体长度，现场计承插后定裁长。</p></div></section>
STOCK_SECTION
<section class="sec assembly-ref assembly-notes"><div class="narrow"><h2 class="assembly-h2">安装前须知</h2><table class="prices"><thead><tr><th>项目</th><th>说明</th></tr></thead><tbody id="assembly-notes"></tbody></table><table class="prices"><tbody><tr><td>查看方法</td><td>选一路后，按“下一步”顺着接管。镜头跟随当前步骤，图上的数字与本步零件对应；拖动可旋转，模型右下角切换正视、侧视和俯视。</td></tr><tr><td>相关说明</td><td><a class="more" href="guide-main.html">安装与试水 ›</a>　<a class="more" href="assembly-offline.html" download="管路3D装配.html">下载离线版 ↓</a></td></tr></tbody></table><p class="note" id="assembly-revision">CAD装配模型</p></div></section>
<noscript><p class="assembly-error">开启JavaScript可查看3D模型，也可阅读<a href="guide-main.html">文字安装说明</a>。</p></noscript>
</div>"""
    stock = json.loads((ROOT / ".维护/建模/数据/管件与设备.json").read_text())["stock_color_allocation"]
    rows = "".join(f'<tr><td>{html.escape(r["name"])}</td><td>{r["stock"]}</td><td>{r["install"]}</td><td>{r["spare"]}</td><td>{html.escape(r["position"])}</td></tr>' for r in stock)
    allocation = '<section class="sec assembly-ref assembly-stock"><div class="narrow"><h2 class="assembly-h2">已购管件怎么用</h2><table class="prices"><thead><tr><th>配件</th><th>现有</th><th>装用</th><th>备用</th><th>安装位置</th></tr></thead><tbody>'+rows+'</tbody></table><p class="note">阀套装自带的拆卸端不重复占用独立活接；备用件留存，不为用完库存增加接头。</p></div></section>'
    body = body.replace('STOCK_SECTION', allocation)
    body = body.replace('href="assets/assembly.css"', f'href="assets/assembly.css?v={ASSET_VERSION}"')
    return 新版.shell("管路装配", body, "assembly.html", page="assembly", desc="60缸管路总装与19步安装顺序", script=f'<script type="module" src="assets/assembly.js?v={ASSET_VERSION}"></script>')

def offline_assembly(document):
    """Single file: no server/CDN needed, same CAD mesh and same viewer code."""
    assets = SRC / 'assets'
    scene = (assets / 'assembly-scene.json').read_text(encoding='utf-8')
    def module_url(text):
        return 'data:text/javascript;base64,' + base64.b64encode(text.encode()).decode()
    three = module_url((assets / 'vendor/three/three.module.js').read_text())
    orbit = (assets / 'vendor/three/OrbitControls.js').read_text().replace("'./three.module.js'", repr(three))
    viewer = (assets / 'assembly.js').read_text()
    fetch_start = viewer.index("    const response = await fetch(")
    fetch_end = viewer.index("    data = validateScene(await response.json());", fetch_start) + len("    data = validateScene(await response.json());")
    viewer = viewer[:fetch_start] + "    data = validateScene(JSON.parse(document.getElementById('embedded-cad-scene').textContent));" + viewer[fetch_end:]
    viewer = viewer.replace("'./vendor/three/three.module.js'", repr(three)).replace("'./vendor/three/OrbitControls.js'", repr(module_url(orbit)))
    for name in ['style.css', 'assembly.css']:
        document = re.sub(r'<link rel="stylesheet" href="assets/' + re.escape(name) + r'(?:\?[^"]*)?">', lambda _: '<style>' + (assets / name).read_text() + '</style>', document)
    embedded = '<script type="application/json" id="embedded-cad-scene">' + scene.replace('</', '<\\/') + '</script>'
    document = re.sub(r'<script type="module" src="assets/assembly\.js(?:\?[^"]*)?"></script>', lambda _: embedded + '<script type="module">' + viewer.replace('</script', '<\\/script') + '</script>', document)
    document = re.sub(r'<script src="assets/site\.js(?:\?[^"]*)?"></script>', lambda _: '<script>' + (assets / 'site.js').read_text() + '</script>', document)
    document = document.replace('<head>', '<head><base href="https://dystudio.fun/fish/">', 1)
    license_text = (assets / 'vendor/three/LICENSE.txt').read_text()
    document = document.replace('</head>', '<!-- ' + license_text.replace('--', '—') + ' -->\n</head>')
    (OUT / 'assembly-offline.html').write_text(document, encoding='utf-8')


def build_coral_photos(images):
    """为目录和详情输出对应显示尺寸的 WebP，参考原图另存。"""
    thumbs = OUT / 'assets/coral-thumbs'
    detail = OUT / 'assets/coral-display'
    thumbs.mkdir()
    detail.mkdir()
    for coral_id, photos in images.items():
        if not photos:
            continue
        with Image.open(ROOT / photos[0]['文件']) as original:
            photo = ImageOps.exif_transpose(original).convert('RGB')
            color_profile = photo.info.get('icc_profile', b'')
            thumb = ImageOps.fit(photo, (288, 224), Image.Resampling.LANCZOS)
            thumb.save(thumbs / f'{coral_id}.webp', quality=82, icc_profile=color_profile)
            photo.thumbnail((1000, 1000), Image.Resampling.LANCZOS)
            photo.save(detail / f'{coral_id}.webp', quality=85, icc_profile=color_profile)


def main():
    global OUT
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,default=OUT);parser.add_argument('--skip-offline',action='store_true',help='跳过导出网页离线装配版；不重建CAD模型')
    args=parser.parse_args();OUT=args.out.resolve()
    if not OUT.is_relative_to(ROOT/'.work') or OUT==ROOT/'.work':parser.error('输出目录须为项目.work下的独立构建目录')
    if OUT.exists():shutil.rmtree(OUT)
    (OUT/'kb').mkdir(parents=True)
    shutil.copytree(SRC/'assets',OUT/'assets',ignore=shutil.ignore_patterns('atlas.js','species-placeholder.svg','site.js'))
    shutil.copytree(IMG,OUT/'img');(OUT/'img/taobao.js').unlink(missing_ok=True)
    if CORAL_IMG.exists():shutil.copytree(CORAL_IMG,OUT/'assets/coral-reference',dirs_exist_ok=True)
    import 商城价格
    print('水族名录价格对上',商城价格.write_js(OUT/'img/mall.js'),'种')
    subprocess.run(['node',str(ROOT/'.维护/网站/生成数据.js'),str(OUT)],check=True)
    data_path=OUT/'assets/tank-data.json';tank_data=json.loads(data_path.read_text())
    for fish in tank_data['fish']:
        if fish['photo']:
            with Image.open(OUT/fish['photo']) as photo:fish['photoWidth']=min(500,photo.width)
    data_path.write_text(json.dumps(tank_data,ensure_ascii=False));(OUT/'assets/tank-data.js').write_text('window.TANK='+json.dumps(tank_data,ensure_ascii=False)+';')
    新版.PRICE_DATE=tank_data['date']
    coral_path=ROOT/'.维护/网站/珊瑚资料.json';corals=json.loads(coral_path.read_text());shutil.copy2(coral_path,OUT/'assets/corals.json')
    images = 新版.coral_images(corals)
    build_coral_photos(images)
    (OUT/'assets/coral-data.js').write_text('window.CORAL_DATA='+json.dumps({'data':corals,'images':images},ensure_ascii=False)+';')
    pages={'index.html':新版.home(tank_data),'fish.html':新版.fish_catalog(tank_data),'fish-detail.html':新版.fish_detail(),'corals.html':新版.coral_catalog(corals,images),'coral-detail.html':新版.coral_detail(),'coral-compare.html':新版.coral_compare(),'assembly.html':build_assembly()}
    pages['records.html']=记录页面.page()
    pages['detail.html']=pages['fish-detail.html']
    pages['buy.html']=新版.read_page('采购清单',fragment('buy'),'buy.html')
    pages['decisions.html']=新版.read_page('决定记录',fragment('decided'),'decisions.html')
    categories = kb_articles()
    algae_guide = next(f'kb/{a["out"]}' for c in categories for a in c['arts'] if a['title']==ALGAE_ARTICLE)
    pages['algae.html'] = build_algae_atlas(algae_guide)
    pages.update(build_guides());pages.update(build_kb(categories))
    pages['designs/notebook.html']='<!doctype html><meta charset="utf-8"><meta http-equiv="refresh" content="0;url=../index.html"><title>60缸</title><a href="../index.html">60缸</a>'
    for name,document in pages.items():
        target=OUT/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(document)
    if not args.skip_offline:offline_assembly(pages['assembly.html'])
    print(f'{len(pages)} pages -> {OUT}')

if __name__=='__main__':main()
