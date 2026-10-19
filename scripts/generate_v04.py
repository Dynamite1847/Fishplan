"""v0.4 aluminum-frame review pack. mm; coordinates are NOT fabrication approval."""
from pathlib import Path
from html import escape
from collections import Counter
import json, math
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'design'/'frame-v0.4'
OUT.mkdir(parents=True,exist_ok=True)
C=dict(ink='#18354a', muted='#576e7d', steel='#d4dfe6', blue='#167faf', green='#21846b', red='#b64141', gold='#b77a17')
class Sheet:
 def __init__(self,title,sub):
  self.p=['<svg xmlns="http://www.w3.org/2000/svg" width="1800" height="1800" viewBox="0 0 1800 1800">', '<rect width="1800" height="1800" fill="#f7f9fb"/>']
  self.text(65,83,title,36,weight=700); self.text(65,135,sub,23,C['muted'])
 def text(self,x,y,t,size=23,col=None,weight=400,anchor='start'):
  self.p.append(f'<text x="{x}" y="{y}" font-family="PingFang SC,Microsoft YaHei,sans-serif" font-size="{size}" fill="{col or C["ink"]}" font-weight="{weight}" text-anchor="{anchor}">{escape(str(t))}</text>')
 def rect(self,x,y,w,h,fill='none',stroke=None,sw=2,dash=False):
  self.p.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke or C["ink"]}" stroke-width="{sw}"'+(' stroke-dasharray="10 7"' if dash else '')+'/>')
 def line(self,x1,y1,x2,y2,col=None,sw=2,dash=False):
  self.p.append(f'<path d="M{x1},{y1} L{x2},{y2}" stroke="{col or C["ink"]}" stroke-width="{sw}" fill="none"'+(' stroke-dasharray="10 7"' if dash else '')+'/>')
 def poly(self,pts,fill,stroke=None):
  self.p.append('<polygon points="'+' '.join(f'{x},{y}' for x,y in pts)+f'" fill="{fill}" stroke="{stroke or C["ink"]}" stroke-width="2"/>')
 def circle(self,x,y,r,col=None,fill='none',dash=False):
  self.p.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{col or C["ink"]}" stroke-width="2"'+(' stroke-dasharray="7 5"' if dash else '')+'/>')
 def dh(self,x,y,w,label):
  self.line(x,y,x+w,y); self.line(x,y-9,x,y+9); self.line(x+w,y-9,x+w,y+9); self.text(x+w/2,y-13,label,22,anchor='middle')
 def dv(self,x,y,h,label):
  self.line(x,y,x,y+h); self.line(x-9,y,x+9,y); self.line(x-9,y+h,x+9,y+h); self.text(x-13,y+h/2,label,22,anchor='end')
 def save(self,name):
  self.text(65,1732,'Fishplan v0.4 · 2026-10-19 · mm · 助手设计提案 / 待供方核验，禁止直接据此加工',22,C['muted'])
  (OUT/(name+'.svg')).write_text('\n'.join(self.p+['</svg>'])+'\n')

# One shared coordinate model: origin at assembly front-left, Z=bare frame bottom.
members=[]
def member(i,name,a,b):
 dims=[b[j]-a[j] for j in range(3)]
 members.append(dict(id=i,name=name,min_mm=a,max_mm=b,cut_length_mm=max(dims)))
for prefix,z in [('T',860),('B',0)]:
 member(prefix+'1','前长梁',[10,10,z],[590,50,z+40])
 member(prefix+'2','后长梁',[10,400,z],[590,440,z+40])
 member(prefix+'3','左深梁',[10,50,z],[50,400,z+40])
 member(prefix+'4','右深梁',[550,50,z],[590,400,z+40])
member('T5','上层偏右深梁',[330,50,860],[370,400,900])
member('B5','下层左内深梁',[140,50,0],[180,400,40])
member('B6','下层右内深梁',[420,50,0],[460,400,40])
for i,(x,y) in enumerate([(10,10),(550,10),(10,400),(550,400)],1):
 member('P'+str(i),'立柱',[x,y,40],[x+40,y+40,860])
plates=[]
for face in ('front','back','left','right'):
 for horizontal in ('low','high'):
  for vertical in ('bottom','top'):
   plates.append(dict(id=f'G{len(plates)+1:02}',face=face,horizontal_corner=horizontal,vertical_corner=vertical,
    local_holes_uv_mm=[[80,20],[130,20],[20,80],[20,130]],thickness_mm=6))
area=298
reserve=sum(area*width*(410-level)/1e6 for width,level in [(100,250),(200,235),(96,170)])
scenarios=[]
for dd in [10,20,30]:
 back=600*450*dd/1e6
 total=back+5+2.5+.7+2+3
 scenarios.append(dict(display_drawdown_mm=dd,display_backflow_l=back,reserve_l=reserve,
 additional_overflow_and_pipes_l=5,max_ato_l=2.5,module_high_storage_l=.7,
 other_solid_displacement_l=2,extra_margin_l=3,remaining_after_margin_l=round(reserve-total,6)))
tray_empty=596*446*32/1e6
rail_area=2*580*40+4*350*40
tray_bound=tray_empty-rail_area*32/1e6-1
model=dict(version='v0.4',status='assistant proposal; supplier structural review / wet tests outstanding',
 user_confirmed=['approximately 900 mm frame height, maintenance priority'],
 datum='X left to right / Y front to back; origin assembly front-left; Z bare frame bottom, +22 above floor before level shims',
 assembly_footprint_mm=[600,450],bare_frame_mm=[580,430,900],top_board_mm=[600,450,18],
 bottom_board=dict(size_mm=[580,340,18],min_mm=[10,52,40],max_mm=[590,392,58]),
 tabletop_height_above_floor_mm=940,whole_unit_height_with_400_tank_and_3_mat_mm=1343,
 sump=dict(outside_mm=[420,310,460],glass_assumption_mm=6,min_mm=[55,60,63],max_mm=[475,370,523],
  cells_net_mm=[100,200,96],baffles_mm=[6,6],actual_operating_water_max_mm=[250,235,170],provisional_safe_depth_mm=410),
 ato=dict(outside_mm=[65,240,180],wall_assumption_mm=3,min_mm=[480,75,63],max_mm=[545,315,243],geometric_max_l=2.443662,budget_l=2.5,pump_fit_verified=False),
 pipe_bay=dict(min_xy_mm=[90,245],max_xy_mm=[280,390],illustrative_envelopes=[dict(id='D1',center=[130,305],diameter=80),dict(id='D2',center=[235,305],diameter=80),dict(id='R1',center=[180,365],diameter=50)],note='tool envelopes only; NOT glass drill or tabletop cut coordinates'),
 catchtray=dict(outside_mm=[600,450,35],wall_assumption_mm=2,floor_assumption_mm=3,frame_isolation_mm=1,empty_gross_l=tray_empty,conservative_usable_estimate_l=round(tray_bound,6),hardware_reserved_l=1,note='planning only; not measured; no sump footprint deduction because tray lip is below equipment board'),
 filter_module=dict(outside_xy_mm=[92,280],wall_mm=3,rear_inside_depth_mm=70,front_inside_depth_mm=201,basket_xy_mm=[82,190],first_chamber_level_upper_mm=250,module_water_level_upper_to_validate_mm=270,extra_water_budget_l=.7),
 headspace_mm=337,skimmer_body_height_example_mm=305,headspace_difference_mm=32,
 members=members,external_gussets=plates,cut_total_m=sum(m['cut_length_mm'] for m in members)/1000,
 water_scenarios=scenarios)
(OUT/'尺寸与计算-v0.4.json').write_text(json.dumps(model,ensure_ascii=False,indent=2)+'\n')

# F01 front/side elevation, both have external corner gussets.
s=Sheet('F01 · 铝架总装与真实高度','总装占地600×450；裸型材框580×430×900 · 正面与右侧，比例一致')
def elevation(x,y,width,depth=False,k=1.08):
 # frame image y is its top; local X is metal's outer left edge.
 s.rect(x,y,width*k,900*k,'none',C['muted'],1)
 for z in [0,860]:s.rect(x,y+(900-z-40)*k,width*k,40*k,C['steel'])
 for u in [0,width-40]:s.rect(x+u*k,y+40*k,40*k,820*k,C['steel'])
 for h in [0,1]:
  for v in [0,1]:
   cx=x+(width if h else 0)*k; cy=y+(0 if v else 900)*k
   dx=-1 if h else 1; dy=1 if v else -1
   s.poly([(cx,cy),(cx+dx*200*k,cy),(cx,cy+dy*200*k)],'#e7eef3',C['blue'])
   for a,b in [(80,20),(130,20),(20,80),(20,130)]:s.circle(cx+dx*a*k,cy+dy*b*k,4.5*k,C['blue'])
 # top and lower equipment boards
 s.rect(x-10*k,y-18*k,(width+20)*k,18*k,'#e6d3ac')
 by=(900-58)*k+y
 s.rect(x,by,(width if not depth else 340)*k,18*k,'#e6d3ac') if not depth else s.rect(x+42*k,by,340*k,18*k,'#e6d3ac')
 # sump is ghosted behind plates in final position
 su=45 if not depth else 50; sw=420 if not depth else 310
 s.rect(x+su*k,y+(900-523)*k,sw*k,460*k,'none',C['green'],3,True)
 if not depth:
  s.rect(x+40*k,y+(900-700)*k,500*k,500*k,'none',C['gold'],2,True)
  s.text(x+290*k,y+500*k,'正面装入窗口',23,C['gold'],anchor='middle')
  s.text(x+290*k,y+535*k,'500宽 × 500高',23,C['gold'],anchor='middle')
  s.text(x+290*k,y+570*k,'底缸先抬至Z210，再向内下降',20,C['green'],anchor='middle')
 s.dh(x,y+900*k+47,width*k,str(width)+' 裸框')
 s.dv(x-35,y,900*k,'900')
 s.text(x,y-52,'右侧视图' if depth else '正视图（前方）',28,weight=700)
elevation(155,300,580)
elevation(1100,300,430,True)
s.text(70,1390,'自下而上：18承压底板 + 3盘底 + 1隔离条 + 900裸架 + 18台面 = 940',27,weight=700)
s.text(70,1442,'主缸400高、垫3厚时，缸顶约1343；调平垫片另计。900不是整柜最终高度。',24)
s.text(70,1496,'绿色虚线：底缸420×310×460；正面装入后降到Z63，顶部Z523。',24,C['green'])
s.text(70,1548,'16块外置200三角板：每个空间角两块，前后、左右两个方向同时加固。',24)
s.text(70,1600,'角板挡住正面四角：不能仍把500×820柱间矩形当作完全无遮挡窗口。',24,C['red'])
s.text(70,1650,'架体稳定、节点抗滑移、玻璃支撑及板材承载尚待供方核验；本图不是承重证明。',23,C['red'])
s.save('F01-总装与标高')

# F02 frame plans / member IDs and cuts.
s=Sheet('F02 · 上下框梁位与型材下料','X/Y从600×450总装前左角量；俯视图后方在上 · 全部4040同一配套系列')
def plan(x,y,which,k=1.08):
 s.rect(x,y,600*k,450*k,'white',C['muted'],2,True)
 s.text(x,y-27,'上框：Z860～900' if which=='T' else '下框：Z0～40',27,weight=700)
 for m in members:
  if not m['id'].startswith(which):continue
  a,b=m['min_mm'],m['max_mm'];xx=x+a[0]*k; yy=y+(450-b[1])*k
  s.rect(xx,yy,(b[0]-a[0])*k,(b[1]-a[1])*k,C['steel'])
  s.text((xx+x+b[0]*k)/2,yy+(b[1]-a[1])*k/2+7,m['id'],20,anchor='middle')
 s.dh(x,y+450*k+45,600*k,'600 总装 / 580裸框')
 s.text(x+300*k,y+450*k+88,'前方 Y=0',21,anchor='middle')
 if which=='T':
  bay=model['pipe_bay'];a,b=bay['min_xy_mm'],bay['max_xy_mm']
  s.rect(x+a[0]*k,y+(450-b[1])*k,(b[0]-a[0])*k,(b[1]-a[1])*k,'#eef7ed',C['green'],2,True)
  for e in bay['illustrative_envelopes']:
   px,py=e['center'];s.circle(x+px*k,y+(450-py)*k,e['diameter']/2*k,C['green'])
   s.text(x+px*k,y+(450-py)*k+6,e['id'],16,anchor='middle')
 else:
  s.rect(x+10*k,y+(450-392)*k,580*k,340*k,'none',C['gold'],3,True)
plan(80,270,'T');plan(990,270,'B')
s.text(80,990,'下料清单（净切长，锯缝及余料由供方排料）',29,weight=700)
for yy,ids,label,q,l in [(1065,'T1/T2/B1/B2','前后长梁',4,580),(1145,'T3/T4/T5/B3/B4/B5/B6','深梁',7,350),(1225,'P1/P2/P3/P4','立柱',4,820)]:
 s.text(90,yy,ids,22);s.text(720,yy,label,25);s.text(1050,yy,f'{l} × {q}根',27);s.text(1450,yy,f'{q*l/1000:.2f}m',26)
s.text(80,1330,'合计15根 / 8.05m（不含损耗）；柱夹在上下框之间：40 + 820 + 40 = 900。',26,weight=700)
s.text(80,1400,'上内梁T5中心X350；下内梁B5/B6中心X160 / X440。',25)
s.text(80,1452,'底缸板580×340：X10～590 / Y52～392，压在四根下层深梁上。',24,C['gold'])
s.text(80,1504,'管件工具包络区X90～280 / Y245～390；绿圆不是玻璃开孔。',24,C['green'])
s.text(80,1556,'12套90°角码仅连接三根内深梁的T形节点，每端左右各一套。',24)
s.text(80,1608,'牌号、壁厚、槽型、角码和螺母必须按同一供方系列核对；“4040”本身不足以采购。',23,C['red'])
s.save('F02-梁位与下料')

# F03 external gusset, mounting and counted hardware.
s=Sheet('F03 · 外置三角节点板与紧固件','节点提案：200×200×6直角三角板 ×16；每块4孔 · 最终材料/沉头/紧固力矩由供方确认')
px,py,k=145,1130,3.6
s.rect(px,py-40*k,200*k,40*k,'#d4dfe6',C['muted'])
s.rect(px,py-200*k,40*k,200*k,'#d4dfe6',C['muted'])
s.poly([(px,py),(px+200*k,py),(px,py-200*k)],'#e6eff6',C['blue'])
for n,(u,v) in enumerate([(80,20),(130,20),(20,80),(20,130)],1):
 xx=px+u*k; yy=py-v*k;s.circle(xx,yy,4.5*k,C['ink'],'white');s.circle(xx,yy,8.25*k,C['muted'])
 s.text(xx+25,yy-25,'H'+str(n),22,C['blue'])
s.dh(px,py+65,200*k,'200');s.dv(px-45,py-200*k,200*k,'200')
s.text(145,1238,'局部原点：直角顶点；u沿横梁向内，v沿立柱向内。',23)
s.text(145,1280,'H1 (80,20)  H2 (130,20)  H3 (20,80)  H4 (20,130)',22)
s.text(1030,310,'孔与表面',29,weight=700)
for yy,t in [(375,'4 × Ø9通孔，配M8'),(425,'90°沉头，按实际螺钉头加工'),(475,'沉头大径暂按Ø16.5复核'),(525,'外侧齐平；不得用凸头顶到盘壁'),(575,'建议6061-T6板，材质须确认'),(625,'孔/外形去毛刺，隔离海水飞溅')]:s.text(1030,yy,t,23)
s.text(1030,750,'每块板：4螺钉 + 4配套T螺母',24,weight=700)
s.text(1030,805,'16块：64组安装，另备8组',24)
s.text(1030,860,'M8×16沉头仅为长度候选',24,C['red'])
s.text(1030,910,'6板厚后的有效啮合/不顶底待核',23,C['red'])
s.text(1030,1010,'板装在四面外表面：',25,weight=700)
for yy,t in [(1065,'前 Y4～10 / 后 Y440～446'),(1115,'左 X4～10 / 右 X590～596'),(1165,'相邻两板在空间角边缘相接')]:s.text(1030,yy,t,22)
s.text(80,1400,'外轮廓：X4～596 / Y4～446 → 含板592×442；落在600×450台面/盘范围内。',24,weight=700)
s.text(80,1455,'四个底角板不跨过Z0；上角不高过Z900。板不伸进柱间，底板不用切角。',24)
s.text(80,1510,'内梁连接：12套同系列4040角码，安装共24螺钉+24螺母；采购14套含2备用。',24)
s.text(80,1565,'节点可制造、能拧紧不等于整架安全；必须复核槽口抗拉、抗滑移与双向侧摆。',24,C['red'])
s.text(80,1620,'DXF为单块板2D几何；不是已批准的激光/铣削加工单，孔口做法需供方回图。',23,C['muted'])
s.save('F03-节点与连接件')

# F04 internal layout, head clearance and real pan capacity.
s=Sheet('F04 · 底缸装取、支撑与接水盘','候选底缸420×310×460；主缸及管件同版核对后再冻结 · 不是独立于铝架的采购规格')
x,y,k=90,270,1.5
s.rect(x,y,600*k,450*k,'white',C['muted'],2,True)
s.rect(x+50*k,y+(450-400)*k,500*k,350*k,'#eef1f4',C['muted'],1)
s.rect(x+10*k,y+(450-392)*k,580*k,340*k,'#f5ead0',C['gold'],2)
s.rect(x+55*k,y+(450-370)*k,420*k,310*k,'#e2f1ec',C['green'],3)
for xx in [161,367]:s.rect(x+xx*k,y+(450-364)*k,6*k,298*k,'#b2bfc5',C['muted'],1)
s.text(x+111*k,y+245*k,'物理',23,anchor='middle');s.text(x+267*k,y+245*k,'蛋分',23,anchor='middle');s.text(x+421*k,y+245*k,'回水',23,anchor='middle')
s.rect(x+480*k,y+(450-315)*k,65*k,240*k,'#ddeaf7',C['blue'],2)
s.text(x+512*k,y+236*k,'ATO',17,anchor='middle')
s.text(x+275*k,y+75*k,'后玻璃外侧至框内侧30',21,C['green'],anchor='middle')
s.text(x+300*k,y+450*k+50,'前方：装入后再向下降到板上',23,anchor='middle')
s.text(1100,285,'蛋分整机几何取出',28,weight=700)
for yy,t in [(350,'上梁底 Z860'),(405,'底缸沿 Z523'),(460,'净高 337 = 860 − 523'),(515,'9004本体高305 → 余32'),(585,'杯、磁吸、软线及实际姿态'),(635,'必须用完整设备/等大模型演练'),(715,'ATO外65×240×180'),(765,'3厚算例实际总容水约2.44L'),(815,'容水预算2.5L；泵能否放入待核')]:s.text(1100,yy,t,23,C['red'] if yy in (635,815) else None)
s.text(80,1060,'底部剖面：取Y140，竖向放大；盘在整个架体下面',27,weight=700)
sx,base,kx,kz=90,1470,1.3,3.2
sy=lambda zz:base-(zz+22)*kz
def section(xx,zz,ww,hh,fill,stroke=None):s.rect(sx+xx*kx,sy(zz+hh),ww*kx,hh*kz,fill,stroke,1.5)
section(0,-22,600,18,'#e6d3ac')
section(0,-4,600,3,'#cce7f5',C['blue'])
section(0,-1,2,32,'#cce7f5',C['blue']);section(598,-1,2,32,'#cce7f5',C['blue'])
for xx in [10,140,420,550]:
 section(xx,-1,40,1,'#546573');section(xx,0,40,40,C['steel'])
section(4,0,6,70,'#e7eef3',C['blue']);section(590,0,6,70,'#e7eef3',C['blue'])
section(10,40,580,18,'#e6d3ac')
section(55,58,420,5,'#b8c9b9',C['green']);section(55,63,420,6,'#e2f1ec',C['green'])
section(55,69,6,21,'#e2f1ec',C['green']);section(469,69,6,21,'#e2f1ec',C['green'])
s.text(90,1520,'承压板18 → 盘底3 → 硬隔离1 → 下框40 → 底板18 → 垫5',22)
for yy,t in [(1130,'底缸底Z63；沿Z523（上部省略）'),(1180,'底板Z40～58，四根下深梁实承托'),(1230,'盘沿Z31，低于底板，不扣底缸占地'),(1280,'Z0裸架底；离地22 + 调平垫片'),(1340,'空盘8.51L − 下框3.28L − 五金1L'),(1390,'规划可用约4.23L，尚未实测'),(1450,'盘底长期压载/蠕变及找平待核')]:s.text(1040,yy,t,22,C['red'] if yy==1450 else None)
s.text(80,1580,'盘只能接局部滴漏，不接得住整缸破损；不能用薄软托盘或软泡棉替代已核验承压结构。',23,C['red'])
s.text(80,1630,'泵阀由管夹承力；底缸外深改310，旧300深滤盒停用。标高Z0不是房间地面。',23)
s.save('F04-柜内与接水盘')

# DXF in millimeters. ASCII labels avoid missing-font dependence; readable Chinese SVG above.
class DXF:
 def __init__(self): self.e=[]
 def line(self,a,b,layer='FRAME'):
  self.e += ['0','LINE','8',layer,'10',str(a[0]),'20',str(a[1]),'30','0','11',str(b[0]),'21',str(b[1]),'31','0']
 def rect(self,x,y,w,h,layer='FRAME'):
  for a,b in [((x,y),(x+w,y)),((x+w,y),(x+w,y+h)),((x+w,y+h),(x,y+h)),((x,y+h),(x,y))]:self.line(a,b,layer)
 def circle(self,x,y,r,layer='HOLES'):
  self.e += ['0','CIRCLE','8',layer,'10',str(x),'20',str(y),'30','0','40',str(r)]
 def text(self,x,y,t,h=12):
  self.e += ['0','TEXT','8','LABELS','10',str(x),'20',str(y),'30','0','40',str(h),'1',t]
 def save(self,name):
  head=['0','SECTION','2','HEADER','9','$ACADVER','1','AC1009','9','$INSUNITS','70','4','0','ENDSEC','0','SECTION','2','ENTITIES']
  (OUT/name).write_text('\n'.join(head+self.e+['0','ENDSEC','0','EOF'])+'\n')
d=DXF()
for prefix,ox in [('T',0),('B',800)]:
 d.rect(ox,0,600,450,'ASSEMBLY')
 for m in members:
  if m['id'].startswith(prefix):
   a,b=m['min_mm'],m['max_mm'];d.rect(ox+a[0],a[1],b[0]-a[0],b[1]-a[1]);d.text(ox+(a[0]+b[0])/2,(a[1]+b[1])/2,m['id'],10)
 d.text(ox,490,'TOP Z860-900' if prefix=='T' else 'BOTTOM Z0-40')
# front elevation translated 800 down; use exact plate outlines.
d.text(0,-110,'FRONT / BARE 580 x 430 x 900 / ALL mm')
for m in members:
 if m['id'] in ('T1','B1','P1','P2'):
  a,b=m['min_mm'],m['max_mm'];d.rect(a[0],a[2]-1100,b[0]-a[0],b[2]-a[2])
for xx,sgn in [(10,1),(590,-1)]:
 for zz,zsgn in [(0,1),(900,-1)]:
  pts=[(xx,zz-1100),(xx+200*sgn,zz-1100),(xx,zz+200*zsgn-1100)]
  for a,b in zip(pts,pts[1:]+pts[:1]):d.line(a,b,'GUSSETS')
d.text(800,-150,'REVIEW ONLY - DO NOT FABRICATE')
d.save('架体梁位与正视-mm.dxf')
d=DXF();tri=[(0,0),(200,0),(0,200)]
for a,b in zip(tri,tri[1:]+tri[:1]):d.line(a,b,'OUTLINE')
for u,v in [(80,20),(130,20),(20,80),(20,130)]:d.circle(u,v,4.5);d.circle(u,v,8.25,'CSK_REFERENCE')
d.text(0,230,'16x / t6 / 4x DIA9 THRU',8);d.text(0,215,'90 DEG CSK TO SUIT ACTUAL M8 SCREW',6)
d.text(0,-20,'REVIEW ONLY / CSK DIA16.5 PROVISIONAL',6)
d.save('三角节点板-200-mm.dxf')

# Checks genuinely independent of drawing positions.
assert len(members)==15 and Counter(m['cut_length_mm'] for m in members)=={580:4,350:7,820:4}
assert math.isclose(model['cut_total_m'],8.05)
def overlap(a,b):return all(min(a['max_mm'][i],b['max_mm'][i])>max(a['min_mm'][i],b['min_mm'][i]) for i in range(3))
for i,a in enumerate(members):
 for b in members[i+1:]:assert not overlap(a,b),(a['id'],b['id'])
assert 860-(40+18+5+460)==337
assert 6+100+6+200+6+96+6==420
assert 410<460-6 and min(r['remaining_after_margin_l'] for r in scenarios)>0
assert 210+460<700 and 420<500 # bounded front insertion rectangle
bay=model['pipe_bay']
for e in bay['illustrative_envelopes']:
 cx,cy=e['center'];r=e['diameter']/2
 assert 90<=cx-r and cx+r<=280 and 245<=cy-r and cy+r<=390
 for m in members:
  if m['id'].startswith('T'):
   a,b=m['min_mm'],m['max_mm'];dx=max(a[0]-cx,0,cx-b[0]);dy=max(a[1]-cy,0,cy-b[1])
   assert dx*dx+dy*dy>=r*r,e['id']
for i,a in enumerate(bay['illustrative_envelopes']):
 for b in bay['illustrative_envelopes'][i+1:]:assert math.dist(a['center'],b['center'])>(a['diameter']+b['diameter'])/2
for u,v in [(80,20),(130,20),(20,80),(20,130)]:
 assert min(u,v,(200-u-v)/math.sqrt(2))>8.25 # countersink fully inside plate
assert 280-3-3-3-70==201 and 201>190
assert 92*280*(270-250)/1e6<.7
assert math.isclose(reserve,22.06392)
print('Generated 4 SVG / 2 DXF / coordinate JSON. Geometry and reserve checks passed.')
