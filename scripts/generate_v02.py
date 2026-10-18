"""Reproducible concept drawings and geometry. Not fabrication certification."""
from pathlib import Path
from html import escape
import json

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "design"
OUT.mkdir(exist_ok=True)
FONT = "'PingFang SC','Microsoft YaHei',sans-serif"
C = dict(ink="#19354b", muted="#647b8e", blue="#187eb4", green="#23846d", red="#c14e55", gold="#a8771c", frame="#657c8f", bg="#f3f6f8")


class Sheet:
    def __init__(self, title, subtitle, size=1800):
        self.size = size
        self.parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}" role="img">', f'<title>{escape(title)}</title>', f'<rect width="{size}" height="{size}" fill="{C["bg"]}"/>', '<defs>']
        for name in ("blue", "green", "red", "gold", "ink"):
            self.parts.append(f'<marker id="{name}" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 Z" fill="{C[name]}"/></marker>')
        self.parts.append('</defs>')
        self.text(55, 65, title, 36, weight=700)
        self.text(55, 110, subtitle, 22, C["muted"])

    def rect(self, x, y, w, h, fill="none", stroke=None, sw=2, r=0):
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke or "none"}" stroke-width="{sw}"/>')

    def text(self, x, y, value, size=22, color=None, weight=400, anchor="start"):
        self.parts.append(f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" font-weight="{weight}" fill="{color or C["ink"]}" text-anchor="{anchor}">{escape(str(value))}</text>')

    def path(self, d, color=None, width=3, arrow=None, dash=False, fill="none"):
        opt = (' stroke-dasharray="9 7"' if dash else '') + (f' marker-end="url(#{arrow})"' if arrow else '')
        self.parts.append(f'<path d="{d}" fill="{fill}" stroke="{color or C["ink"]}" stroke-width="{width}" stroke-linejoin="round"{opt}/>')

    def poly(self, points, fill, stroke=None, sw=2):
        p = " ".join(f'{x},{y}' for x, y in points)
        self.parts.append(f'<polygon points="{p}" fill="{fill}" stroke="{stroke or "none"}" stroke-width="{sw}"/>')

    def circle(self, x, y, r, fill):
        self.parts.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}"/>')

    def dimh(self, x, y, width, label):
        self.path(f'M{x} {y-8} V{y+8} M{x} {y} H{x+width} M{x+width} {y-8} V{y+8}', C["muted"], 1.5)
        self.text(x+width/2, y-13, label, 20, C["muted"], anchor="middle")

    def dimv(self, x, y, height, label, left=False):
        self.path(f'M{x-8} {y} H{x+8} M{x} {y} V{y+height} M{x-8} {y+height} H{x+8}', C["muted"], 1.5)
        self.text(x-13 if left else x+13, y+height/2, label, 20, C["muted"], anchor="end" if left else "start")

    def save(self, name):
        (OUT/name).write_text("\n".join(self.parts+["</svg>"]), encoding="utf-8")


variants = []
for depth in (400, 450):
    inner = (388, depth-132)
    reserve = inner[0]*inner[1]*(400-225)/1e6
    backflow = 600*depth*20/1e6
    budget = backflow+3+3.3+3
    variants.append(dict(
        display_outer_mm=[600, depth, 400], frame_outer_mm=[600, depth, 800],
        frame_inner_plan_mm=[520, depth-80], sump_outer_mm=[400, depth-120, 450],
        sump_assumed_inner_plan_mm=list(inner), sump_running_upper_depth_mm=225,
        sump_provisional_safe_depth_mm=400, sump_geometric_reserve_l=round(reserve,4),
        assumed_display_backflow_l=backflow, assumed_extra_backflow_l=3,
        assumed_max_ato_l=3.3, example_additional_margin_l=3,
        illustrative_remaining_before_equipment_displacement_l=round(reserve-budget,4),
        cuts_mm={"600":4, str(depth-80):6, "720":4},
        extrusion_total_m=round((600*4+(depth-80)*6+720*4)/1000,3),
    ))

data = dict(status="conditional geometry only; no safety certification", updated="2026-10-19", units=dict(dimensions="mm", water="L"),
    assumptions=["6mm sump walls and glass thicknesses are calculation assumptions, not approved fabrication specs.",
    "All compartments conservatively assumed at 225mm; usable rise to 400mm needs final baffle and pipe verification.",
    "Reserve ignores equipment, pipe and fitting displacement.",
    "20mm display drawdown, 3L extra backflow, 3.3L ATO and 3L margin are examples, not measured values."], variants=variants)
(OUT/"几何与物料算例-v0.2.json").write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")


def tank_front(s, x, y, depth=450, scale=.75, side=False):
    w = (depth if side else 600)*scale
    h = 400*scale
    s.rect(x,y,w,h,"#e5f3f9",C["blue"],3)
    s.rect(x+3,y+h-22,w-6,17,"#e0ceb1")
    s.path(f'M{x+w*.24} {y+h-22} L{x+w*.30} {y+h-85} L{x+w*.42} {y+h-105} L{x+w*.50} {y+h-55} L{x+w*.63} {y+h-125} L{x+w*.76} {y+h-45} L{x+w*.78} {y+h-22} Z',"#788b85",2,fill="#93a49b")
    s.path(f'M{x+5} {y+34} H{x+w-5}',C["blue"],2,dash=True)
    return w,h


# Drawing 01: same scale front/side, plus plan and cabinet plan.
s=Sheet("01 · B版尺寸关系与三视图", "主缸600×450×400 / 架体600×450×800 / 单位mm · 方案图，不能直接加工")
scale=.75
for side,x in [(False,100),(True,800)]:
    y=245
    w,h=tank_front(s,x,y,scale=scale,side=side)
    s.text(x,185,"正面关系" if not side else "侧面关系",28,weight=700)
    s.dimh(x,220,w,"600" if not side else "450")
    fy=y+h
    s.rect(x,fy,w,600,"white",C["frame"],3)
    s.rect(x,fy,w,30,C["frame"])
    s.rect(x,fy+570,w,30,C["frame"])
    s.rect(x,fy,30,600,C["frame"])
    s.rect(x+w-30,fy,30,600,C["frame"])
    board_y=fy+570-13.5
    sump_base=board_y-6
    sh=450*scale
    sump_x=x+37.5
    sw=(330 if side else 400)*scale
    s.rect(x+31,board_y,w-62,13.5,"#d4c6ad")
    s.rect(x+33,board_y-8,w-66,8,"#f4dda8",C["gold"],1)
    s.rect(sump_x,sump_base-sh,sw,sh,"#eff8f3",C["green"],2)
    inside_base=sump_base-6*scale
    s.rect(sump_x+2,inside_base-225*scale,sw-4,225*scale,"#cee8dc")
    s.path(f'M{sump_x+3} {inside_base-400*scale} H{sump_x+sw-3}',C["red"],2,dash=True)
    s.path(f'M{sump_x+3} {inside_base-225*scale} H{sump_x+sw-3}',C["blue"],2,dash=True)
    s.text(sump_x+sw/2,sump_base-sh+55,"底缸450高",24,C["green"],600,"middle")
    s.text(sump_x+sw/2,sump_base-45,"滤盒 / 蛋分 / 回水",19,C["green"],anchor="middle")
    if not side:
        s.rect(x+345,sump_base-135,67.5,135,"#fff0c9",C["gold"],2)
        s.text(x+379,sump_base-68,"补水",19,C["gold"],anchor="middle")
        s.dimv(x-40,y,h,"400",left=True)
        s.dimv(x-40,fy,600,"800",left=True)
    else:
        s.dimv(x+w+40,fy+30,(sump_base-sh)-(fy+30),"约244净高")
        s.text(x+w+25,fy+400,"取杯/接头",18,C["muted"])
        s.text(x+w+25,fy+428,"仍需扣空间",18,C["muted"])
    s.text(x,fy+620,"台面/垫层未展开；总高随最终支撑方案统一",18,C["muted"])

# Plan of upper glass with the approximate overflow footprint.
x,y=100,1250
s.text(x,1200,"主缸俯视：上方为后墙",28,weight=700)
s.rect(x,y,450,337.5,"#e5f3f9",C["blue"],3)
s.rect(x+5,y+5,165,105,"#c9d6df",C["frame"],2)
s.text(x+87,y+45,"溢流区占位",20,anchor="middle")
s.text(x+87,y+78,"三接头须避梁",18,anchor="middle")
s.text(x+260,y+220,"活石 + 砂面",25,anchor="middle")
s.circle(x+395,y+110,16,C["blue"])
s.text(x+350,y+148,"造浪占位",18,C["blue"])
s.dimh(x,1630,450,"600")
s.dimv(x+485,y,337.5,"450")

# Plan of frame and sump. Dimensioned chamber footprints are conditional.
x,y=800,1250
s.text(x,1200,"架内俯视：上方为后部",28,weight=700)
s.rect(x,y,450,337.5,C["frame"])
s.rect(x+30,y+30,390,277.5,"white")
s.rect(x+33.75,y+33.75,382.5,270,"#fff6df",C["gold"],1)
sx,sy=x+37.5,y+41.25
s.rect(sx,sy,300,247.5,"#e1f0e9",C["green"],2)
ix,iy=sx+4.5,sy+4.5
for length,label in [(100,"滤盒"),(180,"蛋分"),(96,"回水")]:
    s.rect(ix,iy,length*.75,238.5,"none",C["green"],1)
    s.text(ix+length*.375,iy+130,label,19,C["green"],anchor="middle")
    ix+=(length+6)*.75
s.rect(x+345,y+60,67.5,180,"#fff0c9",C["gold"],2)
s.text(x+379,y+140,"补水",18,C["gold"],anchor="middle")
s.text(x,1630,"内净520×370；角件、管件和面板接口仍需核对",19,C["muted"])
s.text(55,1710,"外尺寸、几何净空及比例明确；孔位、玻璃厚度、分仓、设备及载荷均未通过制造方核验。",23,C["red"])
s.text(55,1750,"更新2026-10-19 · 正面/侧面同尺度，顶部支架与脚轮不包含在800架体高度中。",20,C["muted"])
s.save("01-三视图与布局-v0.2.svg")


# Drawing 02: structural member and bulkhead coordination.
s=Sheet("02 · 铝架构型、下料逻辑与孔位避让", "B版600×450×800 / A版600×400×800 · 构型示例，供应商确认后才能下料")
x,y,sc=140,230,1.15
s.text(x,180,"上框俯视（B）",28,weight=700)
s.rect(x,y,600*sc,450*sc,"#b9c7d1",C["frame"],2)
s.rect(x+40*sc,y+40*sc,520*sc,370*sc,"white")
s.rect(x+280*sc,y+40*sc,40*sc,370*sc,"#b9c7d1",C["frame"],2)
s.rect(x+50*sc,y+45*sc,175*sc,110*sc,"#fff0c9",C["gold"],2)
s.text(x+137*sc,y+93*sc,"后左穿缸候选区",21,C["gold"],anchor="middle")
s.text(x+137*sc,y+127*sc,"孔位及接头包络待定",18,C["gold"],anchor="middle")
s.dimh(x,y-25,600*sc,"600")
s.dimv(x+600*sc+35,y,450*sc,"450")
s.text(x,800,"黄色区域仅表示需避梁的位置关系，不是开孔模板。",23,C["gold"])
s.text(x,840,"接头螺母、工具、活接和台面孔都需避让，不只看玻璃孔中心。",22,C["muted"])
s.text(1010,240,"构型示例下料",29,weight=700)
rows=[("600 × 4","上下框前后梁"),("370 × 6","侧梁＋上下承托梁"),("720 × 4","四角立柱，夹上下框"),("合计 7.50m","不含斜撑与损耗")]
for i,(a,b) in enumerate(rows):
    yy=310+i*100
    s.text(1010,yy,a,30,C["green"],600)
    s.text(1010,yy+35,b,22,C["muted"])
s.text(1010,750,"A版：370改320",27)
s.text(1010,793,"合计7.20m",25,C["green"])
s.rect(85,925,1630,690,"white","#dbe4eb",r=16)
s.text(120,980,"必须一起确认",30,weight=700)
notes=[
    "实际截面 / 惯性矩 / 连接 / 防侧摆：4040只是候选规格，不能单凭名称认定承重。",
    "上层200kg、下层100kg及架体自重为拟核验工况，供应商说明长期挠度、节点及安全系数。",
    "台面按缸厂支撑要求，开孔用接头模板；不能随意切掉整块角部。",
    "木地板需要分散荷载与可靠调平；小脚、底板、接水盘和板件防潮一并设计。",
    "正面保留取杯、取泵和底缸装入路径；背部或侧面的加固不得擅自省掉。",
    "800为架体构型高度；若添加轮/脚底座h，需重新统一总高及立柱长度，不能直接叠上去。",
    "未来面板内嵌或预留板厚，保持总长限制；饰板不作为初期结构稳定的必要条件。",
]
for i,n in enumerate(notes):s.text(120,1040+i*73,n,23)
s.text(55,1730,"本图不能证明载荷合格；穿缸区、角码及中梁以缸厂/型材商同版图为准。",24,C["red"])
s.save("02-铝架与避梁-v0.2.svg")


# Drawing 03: water circuit and conservative reserve comparison.
s=Sheet("03 · 正常循环、备用排水与容水初筛", "砂和活石在主缸；过滤设备在下方底缸 · 主下水和应急下水保持独立")
s.rect(110,200,1000,280,"#e5f3f9",C["blue"],3)
s.rect(130,215,200,250,"#d4dfe6",C["frame"],2)
s.text(665,340,"主缸：回水持续送入，表层水日常就溢入",27,weight=600,anchor="middle")
s.text(665,385,"不是等快漫缸时才启用的洗脸池应急孔",23,C["blue"],anchor="middle")
s.path("M420 260 H155",C["blue"],4,"blue")
s.path("M170 300 V630 H210 V900",C["green"],6,"green")
s.path("M220 255 V610 H310 V815",C["red"],5,"red",True)
for xx,cc in [(170,C["green"]),(220,C["red"]),(260,C["blue"])]:s.rect(xx-8,470,16,20,"white",cc,2)
s.rect(130,730,820,310,"#eef7f1",C["green"],3)
s.rect(134,865,812,170,"#cee8dc")
s.path("M140 785 H940",C["red"],2,dash=True)
s.path("M140 865 H940",C["blue"],2,dash=True)
s.text(610,772,"最高安全水位待核验",23,C["red"],anchor="middle")
s.text(600,850,"初筛保守按全缸水深225",23,C["blue"],anchor="middle")
s.text(420,955,"可取物理过滤 → 蛋分 → 回水区",26,C["green"],600,anchor="middle")
s.path("M800 970 H1010 V570 H260 V275 H420",C["blue"],5,"blue")
s.rect(1060,825,100,215,"#fff0c9",C["gold"],2,r=8)
s.text(1110,900,"有限",21,C["gold"],anchor="middle")
s.text(1110,935,"补水",21,C["gold"],anchor="middle")
s.path("M1110 985 V690 H860 V825",C["gold"],3,"gold")
s.text(1200,260,"日常流量：主下水",26,C["green"],600)
s.text(1200,310,"异常接流：独立备用管",25,C["red"],600)
s.text(1200,380,"管路拟经溢流区缸底",23)
s.text(1200,420,"进入柜内，孔位待定",23)
s.text(1200,520,"物理过滤堵塞时",24)
s.text(1200,560,"旁通仍在底缸内部",24)
s.text(1200,660,"鱼便：悬浮颗粒进过滤",23)
s.text(1200,700,"沉积物留通道虹吸",23)
s.text(1200,800,"最高水位 / 漏水保护",23)
s.text(1200,840,"实际动作和复位须测试",23)
s.rect(85,1130,1630,480,"white","#dbe4eb",r=16)
s.text(125,1190,"几何初筛，不是安全验收",30,weight=700)
for i,c in enumerate(variants):
    xx=125+i*800
    s.text(xx,1250,f'{c["display_outer_mm"][1]}深方案 · 底缸高450',27,weight=600)
    s.text(xx,1310,f'225→400水深几何余量：{c["sump_geometric_reserve_l"]:.1f} L',26,C["green"])
    s.text(xx,1360,f'回流算例 {c["assumed_display_backflow_l"]:.1f} + 3.0 L',23)
    s.text(xx,1405,'最大误补3.3 L + 额外裕量3.0 L',23)
    s.text(xx,1460,f'未扣设备占容的账面差额：{c["illustrative_remaining_before_equipment_displacement_l"]:.1f} L',25,C["gold"])
s.text(125,1545,"回流、水位和设备占容均待真实图纸计算、实物验证；改变补水容器/管路后重算。",23,C["red"])
s.text(55,1725,"主虹吸与备用管需匹配真实回水量；止回阀和报警都不能代替底缸容水空间。",24,C["red"])
s.save("03-水路与余量-v0.2.svg")


# Drawing 04: original visual illustration, not a photograph or brand rendering.
s=Sheet("04 · 开放架与后装面板：外观方向", "本项目原创示意，非品牌实物照片 · 顶部灯/风扇/喂食/检修接口需真实尺寸核对",1600)
def iso(x,y,closed=False):
    W,DX,DY,H,SH=420,150,90,240,480
    # Cabinet side and either a removable front or an open frame.
    s.poly([(x+W,y+H),(x+W+DX,y-DY+H),(x+W+DX,y-DY+H+SH),(x+W,y+H+SH)],"#294154" if closed else "#e1e7ec",C["frame"],3)
    if closed:
        s.rect(x,y+H,W,SH,"#243e52",C["frame"],3)
        s.rect(x+W-33,y+H+105,8,90,"#a9bac7",r=3)
        for r in range(12):
            for c in range(4):
                xx=x+W+25+c*25
                yy=y+H+50+r*26-(xx-x-W)*DY/DX
                s.circle(xx,yy,3,"#8da4b3")
    else:
        s.rect(x,y+H,W,SH,"white",C["frame"],3)
        for xx in (x,x+W-18):s.rect(xx,y+H,18,SH,C["frame"])
        for yy in (y+H,y+H+SH-18):s.rect(x,yy,W,18,C["frame"])
        s.rect(x+35,y+H+245,270,205,"#d5eade",C["green"],2)
        s.path(f'M{x+45} {y+H+325} H{x+295}',C["blue"],2,dash=True)
        s.rect(x+330,y+H+355,55,95,"#ffe5ac",C["gold"],2)
        s.rect(x+285,y+H+70,105,80,"#e6edf2",C["frame"],2,r=4)
        s.path(f'M{x+80} {y+H-10} V{y+H+285}',C["green"],5)
        s.path(f'M{x+110} {y+H-10} V{y+H+285}',C["red"],4,dash=True)
    s.poly([(x,y),(x+DX,y-DY),(x+W+DX,y-DY),(x+W,y)],"#dbedf5",C["blue"],3)
    s.poly([(x+W,y),(x+W+DX,y-DY),(x+W+DX,y-DY+H),(x+W,y+H)],"#c8e5f0",C["blue"],3)
    s.rect(x,y,W,H,"#e4f4fa",C["blue"],3)
    s.rect(x+3,y+H-23,W-6,19,"#d9c7a9")
    s.path(f'M{x+90} {y+H-23} L{x+120} {y+H-95} L{x+180} {y+H-110} L{x+225} {y+H-60} L{x+290} {y+H-125} L{x+340} {y+H-23} Z',"#788b85",2,fill="#91a69a")
    for dx,dy,rr,col in [(165,110,17,"#db8ba0"),(282,124,18,"#dcb479"),(255,70,13,"#8aafd0")]:
        s.circle(x+dx,y+H-dy,rr,col)
    s.rect(x+20,y+9,90,H-15,"#455e6f")
    # Separate light support; all positions illustrative.
    s.path(f'M{x+190} {y-30} V{y-125} H{x+365}',C["frame"],9)
    s.rect(x+205,y-132,190,19,"#253b50",r=5)
    return y+H+SH
iso(65,405)
iso(835,405,True)
s.text(65,1190,"初期：开放铝架",30,weight=700)
s.text(65,1235,"先控制水声、振动，电源和线缆集中固定",22)
s.text(835,1190,"未来：可拆实体面板 + 局部洞洞板",28,weight=700)
s.text(835,1235,"面板厚度纳入外尺寸，右侧不依赖日常检修",22)
s.text(65,1335,"顶部：灯、风扇、喂食口、溢流检修盖分开安排；防猫结构另核跨度与固定。",25)
s.text(65,1400,"造景：铺砂 + 活石，留玻璃清洁、石后水流和虹吸通道。珊瑚及海葵按生长空间安排。",24)
s.text(65,1480,"示意中的设备、颜色、盖板及面板均非已购产品，不代表品牌外观已核验或结构已定稿。",22,C["red"])
s.save("04-外观与面板示意-v0.2.svg")


# Drawing 05: top interfaces and service clearances.
s=Sheet("05 · 顶部功能与维护路径", "借鉴用户观察到的模块化顶盖思路；开口、支架、风扇和承重盖均未定稿",1600)
x,y=140,260
s.rect(x,y,900,675,"#e5f3f9",C["blue"],3)
s.rect(x+12,y+12,300,190,"#c9d6df",C["frame"],2)
s.text(x+162,y+88,"溢流检修盖",27,anchor="middle")
s.text(x+162,y+135,"能独立打开、取鱼梳",22,anchor="middle")
s.rect(x+170,y-60,540,25,"#2c465a",r=5)
s.text(x+440,y-85,"灯架独立，拆盖不拆灯",25,anchor="middle")
s.rect(x+700,y+15,160,100,"#dce5ed",C["frame"],2,r=5)
s.text(x+780,y+75,"风扇接口",23,anchor="middle")
s.rect(x+330,y+520,180,110,"#fff0c9",C["gold"],2,r=5)
s.text(x+420,y+565,"可关闭喂食口",23,C["gold"],anchor="middle")
s.text(x+420,y+603,"后配喂食器",21,C["gold"],anchor="middle")
s.circle(x+795,y+270,33,C["blue"])
s.text(x+740,y+335,"造浪 + 海葵防护",21,C["blue"])
s.text(x+420,y+385,"防跳 / 防猫盖分片与支撑待设计",27,anchor="middle")
s.text(1130,310,"维护从正面为主",26,weight=700)
s.text(1130,360,"左侧过道辅助",24)
s.text(1130,430,"右侧电视柜",24)
s.text(1130,470,"不作为取杯/取泵口",23)
s.text(1130,560,"接口不等于开玻璃孔",24,C["gold"])
s.text(1130,610,"装好后仍须符合",24)
s.text(1130,650,"600长及深度边界",24)
s.text(140,1060,"柜内动作：滤篮前取 → 蛋分杯向上提 → 泵可拆出 → 补水盒前方拿取",27,weight=600)
s.text(140,1130,"避免：为了换棉拆承压接头、把控制器放接水盘底、用饰板挡住阀门。",25)
s.text(140,1230,"防猫盖：普通防跳网不能自动承受约5kg猫踩踏，盖子与固定需单独核验。",25,C["red"])
s.text(140,1320,"散热：风扇口与盖板不应妨碍必要通风；夏季冷水机仍需独立安装位置和噪声核验。",24)
s.text(140,1450,"这是一张接口和维护要求图，不是指定盖板材料、承重或照度的加工图。",23,C["muted"])
s.save("05-顶部与维护-v0.2.svg")


# Drawing 06: optional mobility is not an emergency response method.
s=Sheet("06 · 固定底座与可收回轮：选装比较", "默认固定运行；轮子用于按缸厂搬运要求排水后的检修，不用于推走满水缸抢险",1600)
for i,title in enumerate(["A · 固定承压底座（主方案）","B · 可收回轮 + 独立支撑（选装）"]):
    xx=90+i*790
    s.text(xx,210,title,27,weight=700)
    s.rect(xx+40,290,500,400,"#e9eff3",C["frame"],10)
    s.rect(xx+75,360,430,225,"#d5eade",C["green"],2)
    s.rect(xx+30,700,520,35,"#d6c6ac",C["frame"],2)
    s.path(f'M{xx+290} 305 V{xx*0+660}',C["ink"],5,"ink")
    if i==0:
        s.rect(xx+20,750,540,35,"#bac7d1",C["frame"],2)
        s.rect(xx+10,790,560,15,"#d9e1e7")
        s.text(xx+35,865,"接触面积、调平、防潮及巡检一起设计",21)
    else:
        for dx in (80,470):
            s.path(f'M{xx+dx} 735 V800',C["frame"],12)
            s.rect(xx+dx-35,800,70,20,"#bac7d1",C["frame"],2)
            s.circle(xx+dx+60,775,23,"#b0bec9")
        s.text(xx+35,865,"正常由支撑落地，轮不作为唯一稳定手段",21)
    s.path(f'M{xx} 825 H{xx+610}',C["muted"],2)
s.text(90,1010,"若底座组件增加高度h：保持总目标约800时，架体和立柱长度必须重新计算。",26)
s.text(90,1080,"轮子额定载荷不代表玻璃缸可满水移动；偏载、侧向稳定及搬运方法另核验。",25,C["red"])
s.text(90,1160,"漏水时先停相关泵、控制水源并受控排水；不把推满缸列为应急动作。",25)
s.text(90,1250,"轮子/调平脚的型号、安装板、载荷与支撑面积尚未选定，未包含在现有下料表中。",24)
s.text(90,1380,"功能示意，非承载认证；木地板还需检查支撑点压与轮子滚动损伤。",23,C["muted"])
s.save("06-底座与轮子-v0.2.svg")

for v in variants:
    print(f'{v["display_outer_mm"][1]}mm: reserve={v["sump_geometric_reserve_l"]:.2f}L, remaining={v["illustrative_remaining_before_equipment_displacement_l"]:.2f}L, extrusion={v["extrusion_total_m"]:.2f}m')
print('Generated 6 SVG concept sheets and calculation JSON. No physical or structural certification.')
