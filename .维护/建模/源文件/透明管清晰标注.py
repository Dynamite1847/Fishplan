# coding: utf-8
"""Legible orthographic locator plus five isolated native CAD details."""
from pathlib import Path
import base64,html
from PySide import QtCore,QtGui,QtSvg
root=ROOT

def pic(name,crop):
    im=QtGui.QImage(str(root/name));assert not im.isNull(),name
    im=im.copy(*crop)
    data=QtCore.QByteArray();buffer=QtCore.QBuffer(data);buffer.open(QtCore.QIODevice.WriteOnly);im.save(buffer,'PNG');buffer.close()
    return base64.b64encode(bytes(data)).decode()

def start(w,h,title,sub):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',f'<rect width="{w}" height="{h}" fill="#fff"/>','<style>text{font-family:"PingFang SC";fill:#20313c}.title{font-size:44px;font-weight:600}.head{font-size:32px;font-weight:600}.body{font-size:28px}.note{font-size:24px;fill:#526672}</style>',f'<text x="45" y="65" class="title">{title}</text>',f'<text x="45" y="111" class="body">{sub}</text>']

def finish(parts,name,w,h):
    parts.append('</svg>');svg='\n'.join(parts);(root/(name+'.svg')).write_text(svg)
    renderer=QtSvg.QSvgRenderer(QtCore.QByteArray(svg.encode()));assert renderer.isValid()
    im=QtGui.QImage(w,h,QtGui.QImage.Format_ARGB32);im.fill(QtGui.QColor('white'));p=QtGui.QPainter(im);renderer.render(p);p.end();assert im.save(str(root/(name+'.png')))

def image(parts,data,x,y,w,h):parts.append(f'<image x="{x}" y="{y}" width="{w}" height="{h}" xlink:href="data:image/png;base64,{data}"/>')

W,H=1500,1510
parts=start(W,H,'上水浅灰 · 两路下水紫色','按整路统一直管颜色　管件原配色示意　五段透明观察管保留')
rot_front=App.Rotation(App.Vector(1,0,0),90)
rot_right=App.Rotation(App.Vector(0,0,1),90).multiply(rot_front)
for x,title,file in [(40,'从柜子正面看','透明段-正视底图.png'),(780,'从鱼缸右侧看','透明段-右视底图.png')]:
    parts.append(f'<rect x="{x}" y="145" width="680" height="1195" rx="18" fill="#fafcfd" stroke="#d5e0e6" stroke-width="2"/>')
    parts.append(f'<text x="{x+25}" y="192" class="head">{title}</text>')
    image(parts,pic(file,(400,0,1000,1800)),x+30,205,620,1116)

def project(pt,x,rot):
    q=rot.inverted().multVec(App.Vector(*pt)-App.Vector(350,225,710))
    rawx=900+q.x*1800/1550;rawy=900-q.y*1800/1550
    return x+30+(rawx-400)*.62,205+rawy*.62

def context_label(label,pt,x,rot):
    px,py=project(pt,x,rot);w=len(label)*26+16
    parts.append(f'<rect x="{px-w/2}" y="{py-23}" width="{w}" height="36" rx="5" fill="white" fill-opacity=".88"/><text x="{px}" y="{py+4}" text-anchor="middle" style="font-size:25px;fill:#4c6471">{label}</text>')
for label,pt in [('主缸',[280,225,1340]),('背包',[660,225,1300]),('底缸',[105,225,423]),('铝架',[330,225,670]),('补水',[95,150,650]),('蛋分',[270,200,200]),('水泵',[493,313,122])]:context_label(label,pt,40,rot_front)
for label,pt in [('主缸侧面',[300,225,1450]),('背包',[660,225,1300]),('底缸',[300,100,423]),('水泵',[493,313,125])]:context_label(label,pt,780,rot_right)

def badge(pt,key,x,rot,dx,dy):
    px,py=project(pt,x,rot);bx,by=px+dx,py+dy
    # A nearby number only; never draw a leader to a remote text block.
    number=key[1:]
    parts.append(f'<circle cx="{bx}" cy="{by}" r="24" fill="white" stroke="#007f9c" stroke-width="4"/><text x="{bx}" y="{by+11}" text-anchor="middle" style="font-size:32px;font-weight:600">{number}</text>')

for pt,key,dx,dy in [([85,335,303],'T1',-36,0),([550,313,375],'T3',-36,0),([660,280,820],'T2',36,-10),([635,75,1190],'T4',-36,0)]:badge(pt,key,40,rot_front,dx,dy)
for pt,key,dx,dy in [([660,280,820],'T2',-36,0),([635,75,1190],'T4',36,0),([635,390,1190],'T5',-36,0)]:badge(pt,key,780,rot_right,dx,dy)
parts.extend(['<text x="75" y="1307" class="note">正面看：4与5前后重合，右图可分开看。</text>','<text x="45" y="1397" class="body">1 主排尾管　2 应急下水　3 上水主管　4 前回水　5 后回水</text>','<text x="45" y="1445" class="note">配色为建议，实际颜色随合格商品核对；浅蓝代表透明PVC-U。管路位置、数量未改动。</text>'])
finish(parts,'23-CAD实物配色',W,H)

W,H=1400,1620
parts=start(W,H,'五段分别放大 · 看清透明管与活接','管件按原厂供货色示意　淡蓝代表透明管，紫色只用于下水直管')
cards=[
 ('T1','主下水25','现有活接在上端',['透明尾管外露约76mm','末端开放，直接向下出水','只拆上端活接；原管夹也松开'],0,0),
 ('T2','应急下水25','两端活接，中间透明',['透明段外露约144mm','整路无阀、无转子、保持畅通','两端松开后取下'],1,0),
 ('T3','上水主管20','主泵上方的透明段',['透明段外露约104mm','两端活接，泵上软接仍保留','拆泵时先取下本段'],0,1),
 ('T4','前回水20','前侧回水竖管',['透明段外露约104mm','上、下各一个活接','与后侧透明段同高同长'],1,1),
 ('T5','后回水20','后侧回水竖管',['透明段外露约104mm','上、下各一个活接','图中用右视，避免与前管重叠'],0,2)]
for key,title,sub,lines,col,row in cards:
    x=35+col*685;y=150+row*455
    parts.append(f'<rect x="{x}" y="{y}" width="645" height="430" rx="18" fill="#fafcfd" stroke="#c9d9e1" stroke-width="2"/>')
    parts.append(f'<text x="{x+22}" y="{y+49}" class="head">{key[1:]}　{title}</text>')
    image(parts,pic('透明段-'+key+'底图.png',(650,80,500,1640)),x+20,y+72,105,344)
    parts.append(f'<text x="{x+145}" y="{y+115}" class="body">{sub}</text>')
    for i,line in enumerate(lines):parts.append(f'<text x="{x+145}" y="{y+178+i*56}" class="note">{html.escape(line)}</text>')
# Sixth card: concise service sequence, rather than another diagram crowded with labels.
x=720;y=1060
parts.extend([f'<rect x="{x}" y="{y}" width="645" height="430" rx="18" fill="#eef8fa" stroke="#9fc9d2" stroke-width="2"/>',f'<text x="{x+25}" y="{y+49}" class="head">清洗时怎么拆</text>'])
for i,line in enumerate(['① 停主泵、暂停补水、等待回流','② 接水，松开活接与该段管夹','③ 整段取下，用软管刷清洗','④ 装回，恢复运行后检查渗漏']):parts.append(f'<text x="{x+25}" y="{y+120+i*70}" class="body">{line}</text>')
parts.extend(['<text x="45" y="1545" class="note">每段独立放大，比例不同；长度均为模型外露长度，不能照图裁管。补水沿用原配透明软管。</text>','<text x="45" y="1587" class="note">活接密封圈 / 密封面不粘死。具体承插、轴向退让和手握空间到货试拼；拆管期间保持停机。</text>'])
finish(parts,'24-CAD透明管放大',W,H)
