"""Build the review atlas from geometry exported by the native FreeCAD run."""
from pathlib import Path
from collections import Counter
from html import escape
import json, math

from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor, Color
from reportlab.lib.utils import ImageReader
from PIL import Image, ImageChops

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'design/freecad-v0.5'
DATA=json.loads((OUT/'参数与验证-v0.5.json').read_text())
MESH=json.loads((OUT/'绘图几何-v0.5.json').read_text())
P=DATA['parameters_mm']; C=DATA['calculated_mm']
PDF=ROOT/'output/pdf/Fishplan-v0.5-设计审阅图册.pdf'
PDF.parent.mkdir(parents=True,exist_ok=True)
pdfmetrics.registerFont(TTFont('CN','/System/Library/Fonts/Supplemental/Arial Unicode.ttf'))
W,H=1190.55,841.89
c=canvas.Canvas(str(PDF),pagesize=(W,H))
c.setTitle('Fishplan v0.5 - 参数化总装与框架审阅图册')
c.setAuthor('Fishplan')
INK='#203448'; MUTED='#5e7281'; BLUE='#23799a'; GOLD='#aa8149'; BG='#f5f7f9'
PAGE=0

def text(x,y,s,size=12,col=INK):
    c.setFillColor(HexColor(col));c.setFont('CN',size);c.drawString(x,y,str(s))

def line(x,y,x2,y2,col=MUTED,width=.7,dash=None):
    c.saveState();c.setStrokeColor(HexColor(col));c.setLineWidth(width)
    if dash:c.setDash(dash)
    c.line(x,y,x2,y2);c.restoreState()

def rect(x,y,w,h,fill=None,stroke=INK,width=.7):
    c.saveState();c.setLineWidth(width)
    if fill:c.setFillColor(HexColor(fill))
    c.setStrokeColor(HexColor(stroke));c.rect(x,y,w,h,stroke=1,fill=bool(fill));c.restoreState()

def poly(points,fill=None,stroke=INK,width=.7):
    c.saveState();c.setLineWidth(width)
    if fill:c.setFillColor(HexColor(fill))
    c.setStrokeColor(HexColor(stroke));q=c.beginPath();q.moveTo(*points[0])
    for v in points[1:]:q.lineTo(*v)
    q.close();c.drawPath(q,stroke=1,fill=bool(fill));c.restoreState()

def wrap(x,y,s,width=360,size=12,leading=21,col=INK):
    row=''
    for ch in s:
        if ch=='\n' or (pdfmetrics.stringWidth(row+ch,'CN',size)>width and ch not in '。，、；：）'):
            text(x,y,row,size,col);y-=leading;row='' if ch=='\n' else ch
        else:row+=ch
    if row:text(x,y,row,size,col);y-=leading
    return y

def page(title,sub):
    global PAGE
    PAGE+=1;c.setFillColor(HexColor(BG));c.rect(0,0,W,H,fill=1,stroke=0)
    text(38,H-40,'FISHPLAN   /   v0.5',13,BLUE)
    text(38,H-83,title,28)
    text(38,H-111,sub,12,MUTED)
    line(38,49,W-38,49,'#d5dfe5')
    text(38,29,'2026-10-19  |  单位 mm  |  设计评审版，未批准加工  |  原生模型与零件编号配套',10,MUTED)
    text(W-105,29,f'{PAGE:02d} / 09',10,MUTED)

def end():c.showPage()

def native_figure(name,box):
    img=Image.open(OUT/name).convert('RGB')
    bounds=ImageChops.difference(img,Image.new('RGB',img.size,'white')).getbbox()
    assert bounds, 'blank native preview'
    img=img.crop(bounds)
    x,y,w,h=box;k=min(w/img.width,h/img.height)
    c.drawImage(ImageReader(img),x+(w-img.width*k)/2,y+(h-img.height*k)/2,img.width*k,img.height*k)

def dh(x,y,w,label):
    line(x,y,x+w,y);line(x,y-5,x,y+5);line(x+w,y-5,x+w,y+5)
    tw=pdfmetrics.stringWidth(label,'CN',11);text(x+w/2-tw/2,y+8,label,11)

def dv(x,y,h,label):
    line(x,y,x,y+h);line(x-5,y,x+5,y);line(x-5,y+h,x+5,y+h)
    c.saveState();c.translate(x-9,y+h/2);c.rotate(90)
    text(-pdfmetrics.stringWidth(label,'CN',11)/2,0,label,11);c.restoreState()

def table(x,y,rows,widths,row_h=30,head=True,size=11):
    for ri,row in enumerate(rows):
        split=[]
        for val,ww in zip(row,widths):
            lines=[];cur=''
            for ch in str(val):
                if pdfmetrics.stringWidth(cur+ch,'CN',size)>ww-16:
                    lines.append(cur);cur=ch
                else:cur+=ch
            lines.append(cur);split.append(lines)
        rh=max(row_h,14+max(len(v) for v in split)*(size+3))
        xx=x
        for ci,(lines,ww) in enumerate(zip(split,widths)):
            rect(xx,y-rh,ww,rh,'#e3edf3' if ri==0 and head else '#ffffff','#d1dce4',.4)
            yy=y-rh/2+(len(lines)-1)*(size+3)/2-4
            for val in lines:
                text(xx+8,yy,val,size,INK);yy-=size+3
            xx+=ww
        y-=rh
    return y

def iso(ids,box,explode=False,wire_ids=()):
    selected=[m for m in MESH if m['id'] in ids or m['id'] in wire_ids]
    def delta(m):
        if not explode:return (0,0,0)
        code=m['id']
        if code.startswith('T'):return (0,0,95)
        if code.startswith('B'):return (0,0,-65)
        if code.startswith('P'):
            return ((-90 if code in ('P1','P3') else 90),(-90 if code in ('P1','P2') else 90),0)
        return (0,0,0)
    def proj(v):return (.8660254*(v[0]+v[1]),v[2]+.5*v[1]-.5*v[0])
    verts=[]
    for m in selected:
        d=delta(m);verts += [proj([v[j]+d[j] for j in range(3)]) for v in m['vertices']]
    mnx=min(v[0] for v in verts);mxx=max(v[0] for v in verts)
    mny=min(v[1] for v in verts);mxy=max(v[1] for v in verts)
    x,y,bw,bh=box;k=min(bw/(mxx-mnx),bh/(mxy-mny))
    ox=x+(bw-(mxx-mnx)*k)/2-mnx*k;oy=y+(bh-(mxy-mny)*k)/2-mny*k
    def to2(v):u,z=proj(v);return (ox+u*k,oy+z*k)
    faces=[]
    for m in selected:
        if m['id'] in wire_ids:continue
        d=delta(m);vv=[[v[j]+d[j] for j in range(3)] for v in m['vertices']]
        code=m['id'];rgb=(.68,.73,.78)
        if code.startswith('G'):rgb=(.17,.40,.57)
        if code in ('D01','D02','D03'):rgb=(.72,.61,.43)
        if code=='D04':rgb=(.18,.40,.48)
        if code.startswith('E'):rgb=(.56,.63,.64)
        for tri in m['triangles']:
            a,b,dv3=[vv[i] for i in tri]
            ab=[b[j]-a[j] for j in range(3)];ad=[dv3[j]-a[j] for j in range(3)]
            n=[ab[1]*ad[2]-ab[2]*ad[1],ab[2]*ad[0]-ab[0]*ad[2],ab[0]*ad[1]-ab[1]*ad[0]]
            norm=math.sqrt(sum(t*t for t in n))
            if norm==0 or n[0]-n[1]+n[2] <= 0:continue
            shade=.74+.22*abs(n[2])/norm
            depth=sum(v[0]-v[1]+v[2] for v in (a,b,dv3))/3
            faces.append((depth,[to2(v) for v in (a,b,dv3)],tuple(t*shade for t in rgb)))
    for _,pts,rgb in sorted(faces,key=lambda x:x[0]):
        q=c.beginPath();q.moveTo(*pts[0]);q.lineTo(*pts[1]);q.lineTo(*pts[2]);q.close()
        c.setFillColor(Color(*rgb));c.drawPath(q,stroke=0,fill=1)
    for m in selected:
        if m['id'] not in wire_ids:continue
        d=delta(m)
        for edge in m['edges']:
            vv=[to2([v[j]+d[j] for j in range(3)]) for v in edge]
            for a,b in zip(vv,vv[1:]):line(*a,*b,'#4f8d9e',.6)
    if explode:
        for m in selected:
            vv=m['vertices'];dd=delta(m)
            v=[sum(t[j] for t in vv)/len(vv)+dd[j] for j in range(3)]
            xx,yy=to2(v);rect(xx-12,yy-8,25,17,'#ffffff',BLUE,.4);text(xx-9,yy-4,m['id'],9,BLUE)
    return to2

beams=[m['id'] for m in MESH if m['id'].startswith(('T','B','P')) and m['id'][1:].isdigit()]
nodes=[m['id'] for m in MESH if m['id'].startswith('G')]

page('参数化总装 · 第一版', '主缸与金属承重框外长、外深对应；外挂和盘的包络单独计入场地。')
native_figure('总装预览.png',(55,91,660,605))
table(770,674,[['项目','本版候选'],['承重框','600 × 450 × 900'],['主缸外形','600 × 450 × 400'],['含外置节点','612 × 462'],['盘 / 承压底板','630 × 480'],['台面离地','940（调平另计）'],['主缸顶离地','1343'],['底缸','420 × 310 × 460'],['头部净高','337']], [150,190],32)
wrap(770,342,'600外长已确认；450深、400主缸高、4040及节点细部仍为候选。\n主缸8厚玻璃仅供三维占位，未作强度确认。\n设备显示本体包络，尚未含全部附件。\n现场该方向约700；盘长630的两侧实际操作余量待核。',340,12,23)
end()

page('裸架立体图 · 构型与装配', '15根型材、16块外置三角板；型材槽口为通用可视化示意，采购须配真实截面。')
native_figure('框架预览.png',(65,95,660,605))
table(776,671,[['构件','净切长','数量'],['前 / 后长梁','600','4'],['左右 / 内深梁','370','7'],['四立柱','820','4'],['总计','8.27m','15']], [154,108,73],37)
wrap(776,437,'拼接关系：\n前后梁通长；深梁夹在前后梁之间；立柱夹在上下框之间。\n外置节点在框外安装，保持主体600×450。\n框体自身双向稳定需供方核验，未来面板不承担必要结构作用。\n上层200kg、下层100kg及水平工况仅为拟核验载荷，尚无承载批准。',335,13,25)
end()

page('正侧视 · 标高与维护窗口', 'Z0为裸架底；离地22，调平另计。各层厚度改变后必须重新核对标高。')
def elevation(x,y,width,k,side=False):
    for zz in [0,860]:rect(x,y+zz*k,width*k,40*k,'#cad5dc')
    for xx in [0,width-40]:rect(x+xx*k,y+40*k,40*k,820*k,'#cad5dc')
    for xx,sgn in [(0,1),(width,-1)]:
        for zz,sz in [(0,1),(900,-1)]:poly([(x+xx*k,y+zz*k),(x+(xx+sgn*200)*k,y+zz*k),(x+xx*k,y+(zz+sz*200)*k)],'#d9e6ee',BLUE)
    rect(x,y+900*k,width*k,18*k,'#dac6a6',GOLD)
    sleft=60 if side else 55;sw=310 if side else 420
    rect(x+sleft*k,y+63*k,sw*k,460*k,None,'#388d7b',1.1)
    dh(x,y-28,width*k,str(width)+' 主体外尺寸');dv(x-25,y,900*k,'900 裸架')
    text(x,y+942*k,'侧视' if side else '正视',14,BLUE)
    if not side:
        c.saveState();c.setDash([4,3]);rect(x+40*k,y+200*k,520*k,500*k,None,GOLD);c.restoreState()
        text(x+150*k,y+440*k,'保守窗口 520×500',13,GOLD)
elevation(98,150,600,.56);elevation(615,150,450,.56,True)
table(920,672,[['相对标高Z','数值'],['上梁底','860'],['底缸沿','523'],['头部净高','337'],['底缸外底','63'],['底缸承板顶','58'],['盘沿','31'],['裸架底','0']], [115,90],32)
text(67,87,'底缸装入：空缸底抬到Z210、顶670，前方平移入架再下降至Z63；完整等大装取尚待验证。',13)
end()

page('上下框俯视 · 孔下避梁与柜内布局', '后方在图上方；穿缸绿圆表示工具包络，未指定玻璃孔径或可钻孔心。')
def plan(x,y,upper):
    k=.76
    for b in DATA['beams']:
        if not b['id'].startswith('T' if upper else 'B'):continue
        a=b['bbox_mm'];rect(x+a[0]*k,y+a[1]*k,(a[3]-a[0])*k,(a[4]-a[1])*k,'#cad5dc')
        text(x+(a[0]+a[3])*k/2-8,y+(a[1]+a[4])*k/2-4,b['id'],10)
    dh(x,y-30,600*k,'600');dv(x-24,y,450*k,'450')
    text(x,y+370,'上框' if upper else '下框与设备平面',17,BLUE)
    if upper:
        c.saveState();c.setDash([4,3]);rect(x+90*k,y+245*k,190*k,145*k,None,'#398c6b');c.restoreState()
        for name,cx,cy,d in [('D1',130,305,80),('D2',235,305,80),('R1',180,365,50)]:
            c.setStrokeColor(HexColor('#398c6b'));c.circle(x+cx*k,y+cy*k,d*k/2,stroke=1,fill=0)
            text(x+cx*k-8,y+cy*k-4,name,9,'#398c6b')
    else:
        rect(x,y+50*k,600*k,350*k,None,GOLD,1)
        rect(x+55*k,y+60*k,420*k,310*k,None,'#388d7b',1.5)
        for xx in [161,367]:line(x+xx*k,y+66*k,x+xx*k,y+364*k,'#388d7b')
        rect(x+480*k,y+75*k,65*k,240*k,None,BLUE,1)
        for xx,label in [(100,'物理'),(240,'蛋分'),(395,'回水')]:text(x+xx*k,y+200*k,label,11,'#388d7b')
        text(x+490*k,y+150*k,'ATO',9,BLUE)
plan(86,265,True);plan(683,265,False)
wrap(73,184,'上内梁中心X350；40包络角码最近边X290，工具区最右X280，名义10间隙。实际接头/阀/工具必须重新干装。\n三路示例平面位置沿用空间初筛，严禁直接转为玻璃加工图。',495,12,22)
wrap(677,184,'底缸板改为600×350，Y50～400，压四根下深梁。\n底缸后玻璃至框内后沿名义40，磁座真实厚度仍待核。\n分仓线仅表示平面分区，未指定挡板加工高度。',440,12,22)
end()

page('构件爆炸示意 · 编号与下料对应', '仅把构件沿装配方向移开以便辨认；爆炸位移不属于零件尺寸。')
iso(beams,(70,90,720,605),explode=True)
rows=[['编号','净长','用途']]
for b in DATA['beams']:
    rows.append([b['id'],str(round(b['cut_mm'])), '立柱' if b['id'].startswith('P') else ('长梁' if b['id'][-1] in '12' else '深梁')])
table(846,675,rows,[70,74,111],30)
end()

page('外节点原型 · 四孔与安装方向', '16块200×200×6三角板；原生模型保留可编辑草图，当前实体仅含四通孔。')
x,y,k=110,185,2.15
poly([(x,y),(x+200*k,y),(x,y+200*k)],'#d8e7ee',BLUE,1)
for name,u,v in [('H1',80,20),('H2',130,20),('H3',20,80),('H4',20,130)]:
    c.setStrokeColor(HexColor(INK));c.circle(x+u*k,y+v*k,4.5*k,stroke=1,fill=0)
    text(x+u*k+12,y+v*k+9,name,12,BLUE)
dh(x,y-33,200*k,'200');dv(x-33,y,200*k,'200')
text(x,y+200*k+24,'局部原点为三角板直角顶点',13)
table(672,672,[['孔','u','v'],['H1','80','20'],['H2','130','20'],['H3','20','80'],['H4','20','130']], [100,110,110],35)
wrap(672,450,'4 × Ø9通孔，配M8候选。\n沉头角、头径、有效啮合及防顶底必须按供方实际螺钉回图，当前STEP未包含沉头加工。\n每个空间角两板，外包612×462；板不得高于架顶或低于架底。\n16板安装64组M8；内梁12套角码另含24组。\n材料、节点抗滑、槽口拉脱及整架稳定均待供方核验。',410,13,26)
text(75,99,'通孔草图可编辑 ≠ 已确认加工。沉头和螺钉回图完成后，更新原生模型、STEP、DXF及材料清单。',12,MUTED)
end()

page('板材、接水盘与承压叠层', '框体改回600×450后，盘与底座同步放大；本版固定底座，不含轮。')
items=[('D01 台面',600,450,(75,380),.60),('D02 底缸承板',600,350,(75,110),.60),('D03 承压板 / D04盘外包',630,480,(600,370),.62)]
for label,w,h,(x,y),k in items:
    rect(x,y,w*k,h*k,'#eee4d4',GOLD,1)
    text(x,y+h*k+21,label,15,GOLD);dh(x,y-25,w*k,str(w));dv(x-22,y,h*k,str(h))
table(610,314,[['叠层 / 规划值','尺寸或容量'],['地面承压板 / 盘底 / 隔离','18 / 3 / 1'],['台面 / 底缸承板','18 / 18'],['盘外 / 内平面','630×480 / 626×476'],['盘内高 / 含节点框外包','32 / 612×462'],['盘内至节点名义每侧间隙','7'],['扣下框及1L五金后的盘容量','约5.10L，待实测']], [265,245],28)
text(75,65,'台面当前没有穿缸开孔；待真接头/台面剖面与玻璃支撑回图。盘底长期压载、板材挠度和地板找平未验收。',11,MUTED)
end()

page('设备与水位 · 维护和故障空间', '底缸420×310×460及原水位预算保留候选状态；不以三维放得下代替装取和试水。')
table(63,675,[['项目','本版值','仍须核对'],['三仓净长 / 净深','100 / 200 / 96；298','玻璃6与两挡板6为算例'],['运行水深上界','250 / 235 / 170','从内底量，不能直接当挡板切高'],['底缸沿 / 上梁底Z','523 / 860','头部净高337'],['9004本体','110 × 90 × 305','完整磁座、取杯及整机取出'],['补水盒','65 × 240 × 180','约2.44L；窄盒泵适配'],['三仓几何预留','22.06392L','设备/模块占容与实际回流待测'],['主缸降30组合后差额','+0.76392L，已含3L裕量','额外回流5、ATO2.5、模块0.7、占容2'],['静扬程算例','1.042～1.062m，未计管损','主缸余高20～40、回水仓170假设']], [270,365,430],43)
wrap(72,240,'维护优先：前取滤篮不拆主下水；蛋分杯与整机分别干装验证；泵/活接/补水盒从正面可拆。\n应急下水独立绕过物理滤材；停泵容量按止回失效处理。\n主缸高水位或盘内漏水拟停回水与补水并告警，保护硬件尚未配齐。冷水机外置位置、防猫盖及夜间声音继续作为专项。',1020,14,28)
end()

page('材料清单 · 修改与加工接口', '所有尺寸按本版原生模型导出；未报价格留空，结构/玻璃/孔位批准后才签发加工版。')
yy=table(63,675,[['编号 / 类别','规格 / 用途','安装 / 询价数量'],['T1/T2/B1/B2','4040示意；净切600','4根'],['T3/T4/T5/B3/B4/B5/B6','4040示意；净切370','7根'],['P1～P4','4040示意；净切820','4根'],['G01～G16','三角节点200×200×6；4×Ø9，沉头待回图','16板'],['节点M8螺钉 / 配套槽螺母','长度、槽型和啮合按实物','64组安装；报72组含备用'],['K01～K12角码套装','40×40×40包络；每套2螺钉/2螺母','12套安装；报14套含备用'],['D01 / D02 / D03','台面600×450×18 / 底板600×350×18 / 底座630×480×18','各1'],['D04 / 硬隔离 / 找平','盘630×480×35，底3侧2算例；隔离1','1套；材料和压载待核'],['板夹 / M6 / 木螺钉','顶、底各4个防窜夹，不承担悬吊荷载','8夹；M6 10组；木螺钉20颗'],['主缸 / 底缸 / 补水盒','参考第1、8页；玻璃、垫层、孔位和真设备另核','各1，按商家同版回图'],['另计','阀、活接、管夹、泵灯蛋分造浪、保护、配电、猫盖、冷却','未选全、未报价']], [270,650,145],36,size=10)
wrap(72,yy-30,'修改模型：打开Fishplan-v0.5.FCStd，选“00 参数总表”，在数据面板修改FrameDepth或FrameHeight，重算后检查空间。\n本轮已验证450→470深、900→920高时，关联深梁/立柱/板件/主缸更新，并恢复目标尺寸。\n孔位、设备工作点、结构和玻璃支撑仍须供方及实物验证。改版后重新导出所有文件，旧STEP/PDF/DXF不会自行同步。',1030,11,22)
end();c.save()

class DXF:
    def __init__(self):self.e=[]
    def line(self,a,b,layer):
        self.e+=['0','LINE','8',layer,'10',str(a[0]),'20',str(a[1]),'30','0','11',str(b[0]),'21',str(b[1]),'31','0']
    def closed(self,pts,layer):
        for a,b in zip(pts,pts[1:]+pts[:1]):self.line(a,b,layer)
    def circle(self,x,y,r,layer):self.e+=['0','CIRCLE','8',layer,'10',str(x),'20',str(y),'30','0','40',str(r)]
    def text(self,x,y,s):self.e+=['0','TEXT','8','NOTES','10',str(x),'20',str(y),'30','0','40','10','1',s]
    def save(self,name):
        head=['0','SECTION','2','HEADER','9','$ACADVER','1','AC1009','9','$INSUNITS','70','4','0','ENDSEC','0','SECTION','2','ENTITIES']
        (OUT/name).write_text('\n'.join(head+self.e+['0','ENDSEC','0','EOF'])+'\n')
d=DXF();d.closed([(0,0),(200,0),(0,200)],'NODE_OUTLINE')
for u,v in [(80,20),(130,20),(20,80),(20,130)]:d.circle(u,v,4.5,'THRU_DIA9')
d.text(0,235,'v0.5 REVIEW ONLY - DO NOT FABRICATE');d.text(0,220,'16x t6 / 4x DIA9 / CSK TO SUPPLIER DRAWING')
d.save('节点板-v0.5-mm.dxf')
d=DXF()
for name,x,y,w,h in [('D01_TOP',0,0,600,450),('D02_BOTTOM',750,0,600,350),('D03_GROUND',0,650,630,480)]:
    d.closed([(x,y),(x+w,y),(x+w,y+h),(x,y+h)],name);d.text(x,y+h+25,name+' / t18 / NO DRILL TEMPLATE')
d.text(750,750,'v0.5 REVIEW ONLY');d.text(750,725,'PAN NOT A FLAT CUTTING PATTERN')
d.save('板件轮廓-v0.5-mm.dxf')

lines=['# v0.5 材料清单与模型编号','',
       '2026-10-19。设计评审版，未批准加工。参数来自同版FreeCAD主模型；当前4040槽口仅示意。','',
       '| 编号 | 净切长mm | 数量 | 备注 |','|---|---:|---:|---|']
for length in [600,370,820]:
    selected=[b for b in DATA['beams'] if round(b['cut_mm'])==length]
    lines.append('| '+','.join(b['id'] for b in selected)+f' | {length} | {len(selected)} | 同系列型材，实际截面/连接待核 |')
lines+=['','合计15根，净长8.27m；损耗和锯缝另列。','',
 '| 编号/类别 | 规格 | 安装/询价数量 |','|---|---|---|',
 '| G01～G16 | 200×200×6，四Ø9通孔；沉头和材料待回图 | 16板 |',
 '| 节点螺钉/槽螺母 | M8长度、槽型及啮合待供方 | 64组安装，报72组含备用 |',
 '| K01～K12 | 内梁角码40包络；每套两螺钉两螺母 | 12套安装，报14套含备用；模型仅包络 |',
 '| D01 | 台面600×450×18，无已批准管孔 | 1 |',
 '| D02 | 底缸板600×350×18，Y50～400 | 1 |',
 '| D03 | 地面承压板630×480×18 | 1 |',
 '| D04 | 接水盘外630×480×35，侧2底3算例 | 1；盘底压载/焊缝待核 |',
 '| 硬隔离条 | 厚1，按下框接触线排布，不叠层 | 1套；图册叠层示意，模型未逐条建实体 |',
 '| 找平硬垫 | 按供方及实际地面工法 | 1套，未建实物实体 |',
 '| 板材防窜夹 | 台面/底板各4，不悬吊 | 8，模型未建细部 |',
 '| M6及木螺钉 | 匹配板夹，长度不穿板 | M6报10组，木螺钉报20颗 |',
 '| 底缸垫 / 主缸垫 | 420×310×5 / 600×450×3候选 | 各1，服从缸厂 |',
 '| A01 | 主缸600×450×400，8玻璃占位 | 1；玻璃/孔位/支撑待批准 |',
 '| A02 | 底缸420×310×460，6玻璃算例 | 1；挡板及运行水位另核 |',
 '| A03 | 补水盒65×240×180，壁3算例 | 1；最大总容水约2.44L，泵适配待核 |',
 '', '结构M8安装64+12×2=88组；询价72+14×2=100组，角码自带件避免重复计算。',
 '', '另计：管件/阀/活接/管夹、所有设备及保护、配电、灯盖、猫盖、冷却和面板、包装运费、板材封边及加工。当前无有效商家报价。',
 '', 'DXF仅含节点板通孔和三块板轮廓，没有玻璃/台面钻孔模板、盘焊接展开或已批准加工公差。']
(OUT/'材料清单-v0.5.md').write_text('\n'.join(lines)+'\n')
print('Review PDF, 2 DXF and material list created:',PDF)
