# coding: utf-8
"""Unobstructed native front/right CAD views, nearby numbers, no leader lines."""
import base64,html
from PySide import QtCore,QtGui,QtSvg
root=ROOT
W,H=1500,1770
mode=MODE
if mode=='flow':
    name='21-CAD水流与阀门';title='管路与阀门 · 正视 / 右视'
    labels=[('主排微调阀','主排蓝管；手轮朝柜前'),('旋转视窗','蓝管横装，观察面朝柜前'),('上水主管球阀','绿色主管，分流之前'),('上水止回阀','绿色主管，竖直向上'),('前回水球阀','绿色前支路，手柄朝前'),('后回水球阀','绿色后支路，手柄朝前')]
    front_pts=[(1,[300,80,810],0,-38),(2,[500,144,810],0,38),(3,[635,332,600],-36,0),(4,[635,390,715],36,0)]
    right_pts=[(3,[635,390,600],-36,0),(4,[635,390,715],36,0),(5,[635,75,865],36,0),(6,[635,390,865],-36,0)]
    footer='水流：主排→左后沉淀；应急→右后回水格；泵→主管→三通→前后双嘴。'
else:
    name='20-CAD阀门操作位置';title='操作与检修 · 正视 / 右视'
    labels=[('回水嘴候选位置','实际孔位与嘴形另核，禁止按图开孔'),('三只上水阀朝前','后支路阀从柜前右侧伸手'),('主排透明尾管','停泵后松活接与管夹，再取出'),('独立应急末端','落右后泵仓后部，飞溅 / 通量待试水'),('主泵短软接位置','下方泵脚、管夹软衬按实物配套'),('旋转视窗可替换','停泵后换同长直通段，无并联旁通')]
    front_pts=[(3,[85,335,303],-36,0),(5,[550,313,228],-36,0),(6,[500,144,810],0,38)]
    right_pts=[(1,[580,75,1384],36,0),(2,[635,75,865],36,0),(2,[635,390,865],-36,0),(4,[505,375,280],36,0)]
    footer='当前模型为布局评审；接头外形、手握 / 拆洗退让、实际水位与停泵接水仍须实物验证。'
parts=[f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}">',f'<rect width="{W}" height="{H}" fill="white"/>','<style>text{font-family:"PingFang SC";fill:#20313c}.title{font-size:44px;font-weight:600}.head{font-size:30px;font-weight:600}.body{font-size:27px}.note{font-size:24px;fill:#536875}</style>',f'<text x="45" y="65" class="title">{title}</text>']
for x,color,text in [(45,'#2478b5','主排25'),(335,'#ce741b','应急25（无阀）'),(780,'#168966','上水20'),(1080,'#b81f29','红色阀柄')]:
    parts.extend([f'<rect x="{x}" y="98" width="32" height="12" fill="{color}"/>',f'<text x="{x+44}" y="117" class="body">{text}</text>'])
front=App.Rotation(App.Vector(1,0,0),90);right=App.Rotation(App.Vector(0,0,1),90).multiply(front)
for x,title,file in [(40,'从柜子正面看','编号-正视底图.png'),(780,'从鱼缸右侧看','编号-右视底图.png')]:
    parts.extend([f'<rect x="{x}" y="145" width="680" height="1195" rx="18" fill="#fafcfd" stroke="#d5e0e6" stroke-width="2"/>',f'<text x="{x+25}" y="192" class="head">{title}</text>'])
    im=QtGui.QImage(str(root/file)).copy(400,0,1000,1800);assert not im.isNull()
    data=QtCore.QByteArray();buf=QtCore.QBuffer(data);buf.open(QtCore.QIODevice.WriteOnly);im.save(buf,'PNG');buf.close();data=base64.b64encode(bytes(data)).decode()
    parts.append(f'<image x="{x+30}" y="205" width="620" height="1116" xlink:href="data:image/png;base64,{data}"/>')
def context_label(label,pt,x,rot):
    q=rot.inverted().multVec(App.Vector(*pt)-App.Vector(350,225,710));px=x+30+(900+q.x*1800/1550-400)*.62;py=205+(900-q.y*1800/1550)*.62;w=len(label)*26+16
    parts.append(f'<rect x="{px-w/2}" y="{py-23}" width="{w}" height="36" rx="5" fill="white" fill-opacity=".88"/><text x="{px}" y="{py+4}" text-anchor="middle" style="font-size:25px;fill:#4c6471">{label}</text>')
for label,pt in [('主缸',[280,225,1340]),('背包',[660,225,1300]),('底缸',[105,225,423]),('铝架',[330,225,670]),('补水',[95,150,650]),('蛋分',[270,200,200]),('水泵',[493,313,122])]:context_label(label,pt,40,front)
for label,pt in [('主缸侧面',[300,225,1450]),('背包',[660,225,1300]),('底缸',[300,100,423]),('水泵',[493,313,125])]:context_label(label,pt,780,right)

def badge(n,pt,x,rot,dx,dy):
    q=rot.inverted().multVec(App.Vector(*pt)-App.Vector(350,225,710));px=x+30+(900+q.x*1800/1550-400)*.62+dx;py=205+(900-q.y*1800/1550)*.62+dy
    parts.append(f'<circle cx="{px}" cy="{py}" r="24" fill="white" stroke="#253b4a" stroke-width="3"/><text x="{px}" y="{py+11}" text-anchor="middle" style="font-size:32px;font-weight:600">{n}</text>')
for n,pt,dx,dy in front_pts:badge(n,pt,40,front,dx,dy)
for n,pt,dx,dy in right_pts:badge(n,pt,780,right,dx,dy)
for i,(title,desc) in enumerate(labels):
    x=50+(i%2)*740;y=1395+(i//2)*95
    parts.extend([f'<text x="{x}" y="{y}" class="head">{i+1}　{html.escape(title)}</text>',f'<text x="{x}" y="{y+39}" class="note">{html.escape(desc)}</text>'])
parts.extend([f'<text x="45" y="1720" class="note">{footer}</text>','</svg>'])
svg='\n'.join(parts);assert '<polyline' not in svg and '<line ' not in svg
(root/(name+'.svg')).write_text(svg);render=QtSvg.QSvgRenderer(QtCore.QByteArray(svg.encode()));assert render.isValid()
im=QtGui.QImage(W,H,QtGui.QImage.Format_ARGB32);im.fill(QtGui.QColor('white'));p=QtGui.QPainter(im);render.render(p);p.end();assert im.save(str(root/(name+'.png')))
