# coding: utf-8
"""Native top-view CAD with warehouse contents, inside dimensions, and shopping labels."""
import base64,html
from PySide import QtCore, QtGui, QtSvg
root=ROOT
W,H=2050,1480
parts=[f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}">','<rect width="2050" height="1480" fill="white"/>','<style>text{font-family:"PingFang SC";fill:#21323e}.title{font-size:46px;font-weight:600}.head{font-size:32px;font-weight:600}.body{font-size:27px}.small{font-size:25px;fill:#546775}</style>', '<text x="60" y="78" class="title">干石开缸 · 五仓放什么</text>', '<text x="60" y="130" class="body">底缸外尺寸600×350×400，玻璃6厚；下图为CAD俯视，单位mm</text>', '<text x="60" y="178" class="small">左前白棉、中间设备、右前生物滤材；本阶段不买活石、不养藻、不配小瓶。</text>']
data=base64.b64encode((root/'22-CAD五仓底图.png').read_bytes()).decode()
parts.append(f'<image x="20" y="230" width="1120" height="1120" xlink:href="data:image/png;base64,{data}"/>')
def p(x,y):return 580+(x-300)*1120/670,790-(y-225)*1120/670
parts.append('<text x="520" y="410" class="body">后侧</text><text x="510" y="1170" class="body">柜前／取洗方向</text>')
labels=[(1,'左后：沉淀仓',(81,354),365,'模型内尺寸150×80','只接主下水；底部留空吸污'),(2,'左前：物理过滤',(81,180),545,'模型内尺寸150×252','单层白棉；买500×500一片裁用'),(3,'中间：设备仓',(272,225),725,'模型内尺寸220×338','预留SK2200；已购加热棒放后侧'),(4,'右前：生物过滤',(480,150),905,'模型内尺寸206×196','Matrix 250ml一瓶＋可平铺网袋一只'),(5,'右后：回水仓',(491,334),1085,'模型内尺寸206×120','170×70×128主泵＋补水探头')]
for n,label,pt,y,dim,content in labels:
    x0,y0=p(*pt)
    parts += [f'<circle cx="{x0:.1f}" cy="{y0:.1f}" r="24" fill="white" stroke="#237d86" stroke-width="3"/><text x="{x0:.1f}" y="{y0+9:.1f}" text-anchor="middle" font-size="28">{n}</text>',f'<text x="1220" y="{y}" class="head">{n}　{label}</text><text x="1220" y="{y+45}" class="body">{dim}</text><text x="1220" y="{y+88}" class="body">{content}</text>']
x,y=p(272,347)
parts += ['<text x="60" y="1300" class="body">水流功能顺序：沉淀 → 白棉 → 设备 → 生物滤材 → 回水泵。</text>','<text x="60" y="1350" class="small">右列商家标约208、原藻仓深约198；模型为尺寸闭合采用206/196。实物内尺寸、板高和水位待核。</text>','<text x="60" y="1394" class="small">网袋模型140×140×25；采购平铺外形≤150×150、装料厚≤30，留过水口，提袋后清底。</text>','<text x="60" y="1438" class="small">已核名义放置与取出路径。加热棒脚架、厂家安装方向/最低水位和实际滤袋外形仍须实物确认。</text>','</svg>']
svg='\n'.join(parts);(root/'22-CAD五仓配置.svg').write_text(svg)
renderer=QtSvg.QSvgRenderer(QtCore.QByteArray(svg.encode('utf-8')));assert renderer.isValid()
img=QtGui.QImage(W,H,QtGui.QImage.Format_ARGB32);img.fill(QtGui.QColor('white'))
painter=QtGui.QPainter(img);renderer.render(painter);painter.end();assert img.save(str(root/'22-CAD五仓配置.png'))
