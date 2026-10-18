"""Supplementary service and reserve drawings; no fabrication approval."""
from pathlib import Path
from html import escape
import json, math
from generate_v02 import Sheet, C
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'design'
rows=[]
for depth in (400,450):
 for level in (225,235,245):
  for drawdown in (10,20,30):
   area=388*(depth-132)
   reserve=area*(400-level)/1e6
   display=600*depth*drawdown/1e6
   remaining=reserve-display-3-3.3-3-2-2
   rows.append(dict(display_depth_mm=depth,sump_level_mm=level,display_drawdown_mm=drawdown,
     reserve_l=round(reserve,4),display_backflow_l=round(display,4),additional_backflow_l=3,
     max_ato_l=3.3,additional_margin_l=3,module_extra_stored_water_allowance_l=2,
     equipment_and_module_displacement_allowance_l=2,remaining_l=round(remaining,4)))
json_data=dict(status='sensitivity examples; not measured, not safety acceptance',units='mm, L',
 notes=['v0.2 assumed 225mm baseline remains historical; this supplement checks higher level and module storage.',
 '2L module extra liquid and 2L equipment/module solid allowance are separate unverified budgets.',
 'Baffles, trapped voids and actual equipment can reduce reserve further; highest safe 400mm is provisional.'],scenarios=rows)
(OUT/'余量敏感性-v0.3.json').write_text(json.dumps(json_data,ensure_ascii=False,indent=2)+'\n')
# 07: rear/front diagram of lift-out tray independent of drain.
s=Sheet('07 · 可取滤篮与设备维护：条件细化','沿用v0.2外形，B内深318 / A内深268 · 标高从底缸内底面量，单位mm')
s.text(70,180,'B版俯视：后方在上，正面在下',28,weight=700)
x,y,k=75,230,1.8
s.rect(x,y,388*k,318*k,'white',C['frame'],3)
for bx in (100,286):s.rect(x+bx*k,y,6*k,318*k,'#c4ced6')
s.rect(x+4*k,y+9*k,92*k,300*k,'#edf5f7',C['frame'],2)
s.rect(x+7*k,y+12*k,86*k,70*k,'#d7e8f0',C['blue'],2)
s.circle(x+50*k,y+45*k,16*k,C['green'])
s.text(x+50*k,y+73*k,'后接水',19,anchor='middle')
s.rect(x+9*k,y+94*k,82*k,210*k,'#fff0cd',C['gold'],2)
s.text(x+50*k,y+175*k,'前取滤篮',19,anchor='middle')
s.text(x+50*k,y+200*k,'82×210',18,anchor='middle')
s.rect(x+130*k,y+8*k,110*k,90*k,'#d7e9de',C['green'],2)
s.text(x+185*k,y+43*k,'9004本体',20,anchor='middle')
s.text(x+185*k,y+71*k,'110×90',19,anchor='middle')
s.circle(x+260*k,y+40*k,16*k,C['red'])
s.text(x+196*k,y+195*k,'D2直接入中仓',20,C['red'],anchor='middle')
s.text(x+196*k,y+224*k,'不依赖滤篮',20,C['red'],anchor='middle')
s.rect(x+309*k,y+100*k,60*k,103*k,'#d4eafa',C['blue'],2)
s.text(x+340*k,y+237*k,'泵本体',18,anchor='middle')
s.text(x+340*k,y+263*k,'60×103',18,anchor='middle')
s.dimh(x,y+318*k+45,100*k,'100净')
s.dimh(x+106*k,y+318*k+45,180*k,'180净')
s.dimh(x+292*k,y+318*k+45,96*k,'96净')
s.text(875,250,'本体纸样可放入 ≠ 安装完成',28,weight=700)
for yy,t in [(310,'靠后玻璃磁吸，外磁座净空待核'),(365,'A版前取篮暂缩至82×160'),(420,'D1留在后区，换棉不拆管'),(475,'滤篮单独上提，滴水回到底缸'),(530,'先暂停ATO，完成后核对水位'),(585,'整模块拆洗另按停泵流程操作')]:s.text(875,yy,t,23)
s.text(70,960,'接水盒纵剖面：后接水 → 前滤篮 → 底缸内出水 / 堵塞旁通',27,weight=700)
# Exaggerated vertical scale for readable 230/250/255/280 levels.
xx,yy=150,1060; scale=2.2
z=lambda v:1500-(v-200)*scale
s.rect(xx,z(320),900,z(200)-z(320),'#f7fafb',C['frame'],3)
s.rect(xx+5,z(235),890,z(200)-z(235),'#dcefe6')
s.path(f'M{xx} {z(235)} H{xx+900}',C['blue'],2,dash=True)
s.rect(xx+21,z(265),263,z(230)-z(265),'#d4eaf6')
s.path(f'M{xx+22} {z(265)} H{xx+282}',C['blue'],2,dash=True)
s.text(xx+30,z(350),'后盒水面约265：待试水',19,C['blue'])
s.text(1130,1460,'235：本轮工作水深算例',22,C['blue'])
s.path(f'M{xx+170} {z(340)} V{z(250)}',C['green'],8,'green')
s.path(f'M{xx+20} {z(320)} V{z(230)} H{xx+285} V{z(255)}',C['frame'],4)
s.path(f'M{xx+285} {z(255)} H{xx+350}',C['blue'],3,'blue')
s.path(f'M{xx+350} {z(280)} V{z(250)} H{xx+800} V{z(280)}',C['gold'],4)
s.path(f'M{xx+410} {z(260)} V{z(220)}',C['green'],3,'green')
s.path(f'M{xx+720} {z(260)} V{z(220)}',C['green'],3,'green')
s.path(f'M{xx+570} {z(290)} H{xx+850} V{z(240)}',C['red'],3,'red',dash=True)
s.text(1130,1220,'标高候选（mm）',23,weight=700)
s.text(1130,1280,'280：旁通堰口候选',22,C['red'])
s.text(1130,1340,'255：接水盒堰口候选',22)
s.text(1130,1400,'250：滤篮底 / 主管末端例',21)
s.text(70,1580,'后盒正常水面不是堰口高度；滤棉堵塞后最高水位按实际流量验证，目标不超过300。',23,C['red'])
s.text(70,1630,'分隔挡板、模块固定、堰宽和出口未定稿；D2不穿滤棉，水路始终留在底缸内。',23)
s.text(70,1690,'这是维护与水路原型图，不是可直接裁切的亚克力展开图；尺寸与水位均需试装、试水。',22,C['muted'])
s.save('07-滤篮与设备维护-v0.3.svg')
# 08: table and fault response matrix.
s=Sheet('08 · 余量重新筛查与保护动作','加入模块额外储水2L、设备及模块实体占容2L；两者均为待测预算，安全水深400仍未验证')
s.text(70,200,'20mm主缸降水假设：相减后差额（已留额外裕量3L）',29,weight=700)
for col,t in enumerate(['底缸初始水深','A：400深','B：450深']):s.text([100,650,1080][col],275,t,27,weight=700)
for i,level in enumerate((225,235,245)):
 yy=350+i*90
 s.text(100,yy,f'{level} mm',29)
 for depth,px in ((400,650),(450,1080)):
  r=next(a for a in rows if a['display_depth_mm']==depth and a['sump_level_mm']==level and a['display_drawdown_mm']==20)
  s.text(px,yy,f'{r["remaining_l"]:+.2f} L',31,C['red'] if r['remaining_l']<0 else C['gold'],600)
s.text(70,655,'B版235水深：若主缸降水改为30mm，差额变成 -1.04L。',27,C['red'])
s.text(70,710,'正数也不是通过：真实接头、挡板、设备和回水口可能继续改变结果。',26)
s.text(70,770,'A版需要重新优化模块/水位/容水布置；不能只删掉保护或省略占容。',25)
s.text(70,890,'保护动作草案：定义检测对象，再选能完成动作的产品',29,weight=700)
cards=[('主缸异常高水位','停回水 + 停ATO；锁定原因，人工复核后恢复'),('底缸 / 接水盘漏水','停回水 + 停ATO；警报持续，评估停加热/蛋分'),('ATO红探头或超时','已核One 2 SE说明：停补水泵；不代表会停主回水'),('停电后恢复','先恢复水路并稳定；高水位/漏水故障不能被盲目清除')]
for i,(a,b) in enumerate(cards):
 yy=955+i*135
 s.rect(65,yy,1665,110,'white','#d6e0e7',1.5,r=12)
 s.text(95,yy+40,a,25,weight=700)
 s.text(95,yy+82,b,24)
s.text(70,1595,'故障停泵后仍有回流，重力漏水不会自动消失；浅接水盘不等于整缸容水。',24,C['red'])
s.text(70,1660,'未选定主缸高水位和地面漏水联动硬件；本图不是市电接线图或已完成的控制系统。',23,C['muted'])
s.save('08-容水与保护动作-v0.3.svg')
# 09: actual-size body templates, not component installation envelopes.
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="297mm" height="210mm" viewBox="0 0 297 210">',
 '<title>设备本体纸样 A4横向 1:1，打印后量校准线</title>',
 '<rect width="297" height="210" fill="white"/>']
def txt(x,y,t,size=4):svg.append(f'<text x="{x}" y="{y}" font-family="PingFang SC,Microsoft YaHei,sans-serif" font-size="{size}" fill="#19354b">{escape(t)}</text>')
def rect(x,y,w,h,col):svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="{col}" stroke-width=".4"/>')
txt(12,13,'09 · A4横向设备本体纸样：选择100% / 实际大小打印',5)
txt(12,22,'先量下方100mm校准线；本图不含挂件、磁吸、管件、出水或取出空间。')
rect(15,33,110,90,'#23846d');txt(22,48,'TUNZE 9004.000');txt(22,58,'本体110×90，竖高305');txt(22,68,'225～245浸没，磁吸另核')
rect(155,33,103,60,'#187eb4');txt(160,49,'SICCE Syncra Silent 1.5');txt(160,59,'本体约103×60，竖高77');txt(160,69,'接头/吸盘/软管另核')
txt(155,105,'纸样通过只代表本体平面初筛。')
txt(155,114,'旧资料与所售版本不符时重做。')
svg.append('<path d="M15 153 H115 M15 149 V157 M115 149 V157" stroke="#19354b" stroke-width=".4"/>')
txt(15,165,'此线应为100mm，量错则不能据纸样判断尺寸。')
txt(15,185,'来源与限制见 research/设备空间与回水核验-v0.3.md')
svg.append('</svg>')
(OUT/'09-设备本体纸样-A4-v0.3.svg').write_text('\n'.join(svg)+'\n')
preview=svg.copy()
preview[0]='<svg xmlns="http://www.w3.org/2000/svg" width="1800" height="1800" viewBox="0 0 297 297">'
preview[2]='<rect width="297" height="297" fill="white"/>'
(OUT/'09-纸样屏幕预览-v0.3.svg').write_text('\n'.join(preview)+'\n')
print('Generated three supplementary SVG sheets and 18 sensitivity scenarios.')
