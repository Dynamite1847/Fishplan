"""Run inside official FreeCAD. Native expressions remain editable after reopening.

The slotted profile is an illustrative envelope, not a supplier section or FEA model.
"""
from pathlib import Path
from collections import Counter
import json
import math
import os
import traceback

import FreeCAD as App
import Part
import Sketcher

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'design' / 'freecad-v0.5'
OUT.mkdir(parents=True, exist_ok=True)
V = App.Vector
DOC = App.newDocument('Fishplan_v05')
P = DOC.addObject('App::FeaturePython', 'Parameters')
P.Label = '00 参数总表 - 在数据面板改尺寸'

PARAMS = [
    ('FrameLength', 600, '01 主体', '用户确认：承重框与主缸外长对应'),
    ('FrameDepth', 450, '01 主体', '候选深度，可改；与主缸外深对应'),
    ('FrameHeight', 900, '01 主体', '用户接受约900架高，维护优先'),
    ('Profile', 40, '01 主体', '4040候选截面外包；真实槽型待供方'),
    ('TopThickness', 18, '02 板材与底座', '台面厚度候选'),
    ('BottomThickness', 18, '02 板材与底座', '底缸承板厚度候选'),
    ('BottomFront', 50, '02 板材与底座', '底缸板前沿Y'),
    ('BottomRearInset', 50, '02 板材与底座', '底缸板距框后沿'),
    ('PanOverhang', 15, '02 板材与底座', '接水盘外侧超出主体每边15候选'),
    ('PanHeight', 35, '02 板材与底座', '盘总高候选'),
    ('PanWall', 2, '02 板材与底座', '盘侧壁厚度算例'),
    ('PanFloor', 3, '02 板材与底座', '盘底厚度算例，持续压载待核'),
    ('Isolation', 1, '02 板材与底座', '下框与盘之间硬隔离层'),
    ('GroundBoard', 18, '02 板材与底座', '地面承压板厚度候选'),
    ('SumpMat', 5, '02 板材与底座', '底缸垫，服从缸厂要求'),
    ('DisplayMat', 3, '02 板材与底座', '主缸垫，服从缸厂要求'),
    ('PlateSize', 200, '03 节点', '三角板直角边候选'),
    ('PlateThickness', 6, '03 节点', '外置板厚度候选'),
    ('NodeHoleDiameter', 9, '03 节点', 'M8安装通孔候选；沉头待供方'),
    ('TopInnerX', 350, '03 节点', '上内深梁中心X，避开穿缸区'),
    ('BottomInner1X', 160, '03 节点', '下内深梁中心X'),
    ('BottomInner2X', 440, '03 节点', '下内深梁中心X'),
    ('DisplayHeight', 400, '04 玻璃与设备', '主缸高候选'),
    ('DisplayGlass', 8, '04 玻璃与设备', '仅用于三维占位，未确认厚度'),
    ('SumpLength', 420, '04 玻璃与设备', '底缸外长候选'),
    ('SumpDepth', 310, '04 玻璃与设备', '底缸外深候选'),
    ('SumpHeight', 460, '04 玻璃与设备', '底缸外高候选'),
    ('SumpGlass', 6, '04 玻璃与设备', '容量算例厚度，待缸厂核验'),
    ('SumpX', 55, '04 玻璃与设备', '底缸外左面X'),
    ('SumpY', 60, '04 玻璃与设备', '底缸外前面Y'),
    ('AtoLength', 65, '04 玻璃与设备', '限量补水盒外长'),
    ('AtoDepth', 240, '04 玻璃与设备', '限量补水盒外深'),
    ('AtoHeight', 180, '04 玻璃与设备', '限量补水盒外高'),
    ('AtoWall', 3, '04 玻璃与设备', '补水盒壁厚算例'),
    ('AtoX', 480, '04 玻璃与设备', '补水盒X'),
    ('AtoY', 75, '04 玻璃与设备', '补水盒Y'),
]
for name, val, group, tip in PARAMS:
    P.addProperty('App::PropertyLength', name, group, tip)
    setattr(P, name, val)
for name, expr in {
    'SumpZ': 'Profile + BottomThickness + SumpMat',
    'FloorOffset': 'GroundBoard + PanFloor + Isolation',
    'PanLength': 'FrameLength + 2 * PanOverhang',
    'PanDepth': 'FrameDepth + 2 * PanOverhang',
    'TopZ': 'FrameHeight + TopThickness',
    'DisplayZ': 'TopZ + DisplayMat',
    'Headspace': 'FrameHeight - Profile - SumpZ - SumpHeight',
}.items():
    P.addProperty('App::PropertyLength', name, '05 自动计算')
    P.setExpression(name, expr)
P.addProperty('App::PropertyString', 'Status', '00 版本')
P.Status = 'v0.5 设计评审；未获供方结构/玻璃/孔位批准，禁止直接加工'
P.addProperty('App::PropertyString', 'ProfileSource', '00 版本')
P.ProfileSource = '4040通用可视化截面：槽与中心孔仅示意，无供方Ix/Iy或米重'

GROUPS = {}
for name, label in [('Frame', '01 裸架 - 15根型材'), ('Nodes', '02 外置节点 - 16板'),
                    ('Brackets', '03 内梁角码 - 12个包络'), ('Boards', '04 板材与盘'),
                    ('Tanks', '05 主底缸与补水盒'), ('Equipment', '06 设备与水路占位'),
                    ('Construction', '99 隐藏构造 - 不导出')]:
    g = DOC.addObject('App::DocumentObjectGroup', name)
    g.Label = label
    GROUPS[name] = g

FINALS = []
BEAMS = []
PLATES = []

def expr(obj, prop, value):
    if isinstance(value, (int, float)) and '.' not in prop:
        setattr(obj, prop, value)
    else:
        obj.setExpression(prop, str(value))

def color(obj, rgb, alpha=0):
    if App.GuiUp:
        obj.ViewObject.ShapeColor = rgb
        obj.ViewObject.LineColor = (0.19, 0.25, 0.31)
        obj.ViewObject.LineWidth = 1.1
        obj.ViewObject.Transparency = alpha

def visible(obj, yes):
    if App.GuiUp:
        obj.ViewObject.Visibility = yes

def box(name, dims, pos=(0, 0, 0), group='Construction', rgb=(.75, .78, .81), alpha=0):
    o = DOC.addObject('Part::Box', name)
    for prop, val in zip(('Length', 'Width', 'Height'), dims): expr(o, prop, val)
    for axis, val in zip(('x', 'y', 'z'), pos): expr(o, 'Placement.Base.' + axis, val)
    GROUPS[group].addObject(o)
    color(o, rgb, alpha)
    return o

def rotation(axes):
    m = App.Matrix()
    for j, axis in enumerate(axes, 1):
        for i, val in enumerate(axis, 1): setattr(m, f'A{i}{j}', val)
    return App.Rotation(m)

def beam(code, label, axis, length, pos):
    stock = box(code + '_Stock', ['Parameters.Profile', 'Parameters.Profile', length])
    # Longitudinal open grooves are illustrative and explicitly excluded from structural use.
    cuts = []
    for n, dims, base in [
        (1, [8, 4.01, length], ['Parameters.Profile / 2 - 4 mm', -.01, 0]),
        (2, [8, 4.01, length], ['Parameters.Profile / 2 - 4 mm', 'Parameters.Profile - 4 mm', 0]),
        (3, [4.01, 8, length], [-.01, 'Parameters.Profile / 2 - 4 mm', 0]),
        (4, [4.01, 8, length], ['Parameters.Profile - 4 mm', 'Parameters.Profile / 2 - 4 mm', 0]),
    ]:
        cuts.append(box(code + '_Slot' + str(n), dims, base))
    core = DOC.addObject('Part::Cylinder', code + '_Core')
    core.Radius = 4
    expr(core, 'Height', length)
    expr(core, 'Placement.Base.x', 'Parameters.Profile / 2')
    expr(core, 'Placement.Base.y', 'Parameters.Profile / 2')
    GROUPS['Construction'].addObject(core)
    tool = DOC.addObject('Part::MultiFuse', code + '_Grooves')
    tool.Shapes = cuts + [core]
    GROUPS['Construction'].addObject(tool)
    o = DOC.addObject('Part::Cut', code)
    o.Base, o.Tool = stock, tool
    o.Label = code + ' ' + label + ' [4040示意]'
    axes = {'X': [(0, 1, 0), (0, 0, 1), (1, 0, 0)],
            'Y': [(1, 0, 0), (0, 0, -1), (0, 1, 0)],
            'Z': [(1, 0, 0), (0, 1, 0), (0, 0, 1)]}[axis]
    o.Placement.Rotation = rotation(axes)
    for a, val in zip(('x', 'y', 'z'), pos): expr(o, 'Placement.Base.' + a, val)
    o.addProperty('App::PropertyLength', 'CutLength', '下料')
    expr(o, 'CutLength', length)
    o.addProperty('App::PropertyString', 'Axis', '下料'); o.Axis = axis
    GROUPS['Frame'].addObject(o)
    color(o, (.72, .76, .80))
    FINALS.append(o); BEAMS.append(o)
    for v in [stock, tool, core] + cuts: visible(v, False)
    return o

for prefix, z in [('T', 'Parameters.FrameHeight - Parameters.Profile'), ('B', 0)]:
    z_y = 'Parameters.FrameHeight' if prefix == 'T' else 'Parameters.Profile'
    beam(prefix+'1', '前长梁', 'X', 'Parameters.FrameLength', [0, 0, z])
    beam(prefix+'2', '后长梁', 'X', 'Parameters.FrameLength', [0, 'Parameters.FrameDepth - Parameters.Profile', z])
    beam(prefix+'3', '左深梁', 'Y', 'Parameters.FrameDepth - 2 * Parameters.Profile', [0, 'Parameters.Profile', z_y])
    beam(prefix+'4', '右深梁', 'Y', 'Parameters.FrameDepth - 2 * Parameters.Profile', ['Parameters.FrameLength - Parameters.Profile', 'Parameters.Profile', z_y])
beam('T5', '上内深梁', 'Y', 'Parameters.FrameDepth - 2 * Parameters.Profile', ['Parameters.TopInnerX - Parameters.Profile / 2', 'Parameters.Profile', 'Parameters.FrameHeight'])
for code, center in [('B5', 'BottomInner1X'), ('B6', 'BottomInner2X')]:
    beam(code, '下内深梁', 'Y', 'Parameters.FrameDepth - 2 * Parameters.Profile', ['Parameters.'+center+' - Parameters.Profile / 2', 'Parameters.Profile', 'Parameters.Profile'])
for n, x, y in [(1, 0, 0), (2, 'Parameters.FrameLength - Parameters.Profile', 0),
                (3, 0, 'Parameters.FrameDepth - Parameters.Profile'),
                (4, 'Parameters.FrameLength - Parameters.Profile', 'Parameters.FrameDepth - Parameters.Profile')]:
    beam('P'+str(n), '立柱', 'Z', 'Parameters.FrameHeight - 2 * Parameters.Profile', [x, y, 'Parameters.Profile'])

# Shared native constrained sketch; hole positions remain editable Sketcher dimensions.
sk = DOC.addObject('Sketcher::SketchObject', 'NodeSketch')
sk.Label = '节点原型草图 - 四孔尺寸可编辑，沉头待回图'
for a,b in [((0,0),(200,0)), ((200,0),(0,200)), ((0,200),(0,0))]:
    sk.addGeometry(Part.LineSegment(V(*a,0), V(*b,0)), False)
for a,b in [(0,1),(1,2),(2,0)]: sk.addConstraint(Sketcher.Constraint('Coincident',a,2,b,1))
sk.addConstraint(Sketcher.Constraint('Coincident',0,1,-1,1))
sk.addConstraint(Sketcher.Constraint('Horizontal',0))
sk.addConstraint(Sketcher.Constraint('Vertical',2))
for idx in (0,2):
    c = sk.addConstraint(Sketcher.Constraint('Distance',idx,200.0))
    sk.setExpression(f'Constraints[{c}]', 'Parameters.PlateSize')
for u,v in [(80,20),(130,20),(20,80),(20,130)]:
    i = sk.addGeometry(Part.Circle(V(u,v,0),V(0,0,1),4.5),False)
    sk.addConstraint(Sketcher.Constraint('DistanceX',i,3,float(u)))
    sk.addConstraint(Sketcher.Constraint('DistanceY',i,3,float(v)))
    c = sk.addConstraint(Sketcher.Constraint('Diameter',i,9.0))
    sk.setExpression(f'Constraints[{c}]','Parameters.NodeHoleDiameter')
GROUPS['Construction'].addObject(sk)
DOC.recompute()

for face in ('front','back','left','right'):
    for high in (False,True):
        for top in (False,True):
            sign = -1 if high else 1
            vz = -1 if top else 1
            if face in ('front','back'):
                u, v = V(sign,0,0), V(0,0,vz)
                outer = V(0,-1 if face=='front' else 1,0)
                base = ['Parameters.FrameLength' if high else 0,
                        0 if face=='front' else 'Parameters.FrameDepth',
                        'Parameters.FrameHeight' if top else 0]
            else:
                u, v = V(0,sign,0), V(0,0,vz)
                outer = V(-1 if face=='left' else 1,0,0)
                base = [0 if face=='left' else 'Parameters.FrameLength',
                        'Parameters.FrameDepth' if high else 0,
                        'Parameters.FrameHeight' if top else 0]
            normal = u.cross(v)
            if normal.dot(outer) < 0:
                for i, val in enumerate(outer):
                    if val: base[i] = f'({str(base[i]) + (" mm" if isinstance(base[i],(int,float)) else "")}) + ({val}) * Parameters.PlateThickness'
            o = DOC.addObject('Part::Extrusion', f'G{len(PLATES)+1:02}')
            o.Base = sk; o.DirMode = 'Normal'; o.Solid = True
            expr(o,'LengthFwd','Parameters.PlateThickness')
            o.Placement.Rotation = rotation([tuple(u),tuple(v),tuple(normal)])
            for a,val in zip(('x','y','z'),base): expr(o,'Placement.Base.'+a,val)
            o.Label = o.Name + ' ' + face + ('上' if top else '下') + '节点 [四通孔/沉头待核]'
            GROUPS['Nodes'].addObject(o); color(o,(.19,.43,.63))
            FINALS.append(o); PLATES.append(o)

# Brackets are labelled maximum envelopes, deliberately excluded from machining solids.
for code, center, z in [('T5','TopInnerX','Parameters.FrameHeight - Parameters.Profile'),
                         ('B5','BottomInner1X',0),('B6','BottomInner2X',0)]:
    for rear in (False,True):
        for side in (-1,1):
            x = f'Parameters.{center} - Parameters.Profile / 2 - 40 mm' if side<0 else f'Parameters.{center} + Parameters.Profile / 2'
            y = 'Parameters.FrameDepth - Parameters.Profile - 40 mm' if rear else 'Parameters.Profile'
            o=box('K'+str(len(GROUPS['Brackets'].Group)+1).zfill(2),[40,40,40],[x,y,z], 'Brackets',(.24,.51,.68),65)
            o.Label += ' 内梁角码40包络 [非零件实体]'

top=box('D01',['Parameters.FrameLength','Parameters.FrameDepth','Parameters.TopThickness'],[0,0,'Parameters.FrameHeight'],'Boards',(.77,.67,.48))
top.Label='D01 台面 - 孔位待真接头，当前无加工孔'; FINALS.append(top)
bottom=box('D02',['Parameters.FrameLength','Parameters.FrameDepth - Parameters.BottomFront - Parameters.BottomRearInset','Parameters.BottomThickness'],[0,'Parameters.BottomFront','Parameters.Profile'],'Boards',(.77,.67,.48))
bottom.Label='D02 底缸承板 - 四深梁承托'; FINALS.append(bottom)
ground=box('D03',['Parameters.PanLength','Parameters.PanDepth','Parameters.GroundBoard'],['-Parameters.PanOverhang','-Parameters.PanOverhang','-Parameters.FloorOffset'],'Boards',(.71,.61,.43))
ground.Label='D03 地面承压板';FINALS.append(ground)

def hollow(name, dims, wall, bottom_t, pos, group, rgb, alpha):
    outside=box(name+'_Outer',dims)
    inside=box(name+'_Void',[f'({dims[0]}) - 2 * ({wall})',f'({dims[1]}) - 2 * ({wall})',dims[2]],[wall,wall,bottom_t])
    o=DOC.addObject('Part::Cut',name);o.Base=outside;o.Tool=inside
    for a,val in zip(('x','y','z'),pos):expr(o,'Placement.Base.'+a,val)
    GROUPS[group].addObject(o);color(o,rgb,alpha);FINALS.append(o)
    visible(outside,False);visible(inside,False)
    return o

pan=hollow('D04',['Parameters.PanLength','Parameters.PanDepth','Parameters.PanHeight'],'Parameters.PanWall','Parameters.PanFloor',
           ['-Parameters.PanOverhang','-Parameters.PanOverhang','-Parameters.Isolation - Parameters.PanFloor'],'Boards',(.19,.43,.56),35)
pan.Label='D04 全架下接水盘 - 承压/材质待核'
display=hollow('A01',['Parameters.FrameLength','Parameters.FrameDepth','Parameters.DisplayHeight'],'Parameters.DisplayGlass','Parameters.DisplayGlass',
               [0,0,'Parameters.DisplayZ'],'Tanks',(.49,.76,.83),83)
display.Label='A01 主缸占位 - 8玻璃算例/无钻孔'
sump=hollow('A02',['Parameters.SumpLength','Parameters.SumpDepth','Parameters.SumpHeight'],'Parameters.SumpGlass','Parameters.SumpGlass',
            ['Parameters.SumpX','Parameters.SumpY','Parameters.SumpZ'],'Tanks',(.42,.73,.68),78)
sump.Label='A02 底缸占位 - 分仓水位须另核'
ato=hollow('A03',['Parameters.AtoLength','Parameters.AtoDepth','Parameters.AtoHeight'],'Parameters.AtoWall','Parameters.AtoWall',
           ['Parameters.AtoX','Parameters.AtoY','Parameters.SumpZ'],'Tanks',(.36,.61,.82),62)
ato.Label='A03 限量补水盒 - 泵适配待核'
for n,x,w,level in [(1,61,100,250),(2,167,200,235),(3,373,96,170)]:
    o=box('W'+str(n),[w,'Parameters.SumpDepth - 2 * Parameters.SumpGlass',1],
          [x,'Parameters.SumpY + Parameters.SumpGlass',f'Parameters.SumpZ + Parameters.SumpGlass + {level} mm'], 'Equipment',(.15,.56,.69),55)
    o.Label=f'W{n} 三仓水面上界 {level} [无挡板切高含义]'
o=box('E01',[110,90,305],[220,265,'Parameters.SumpZ + Parameters.SumpGlass'],'Equipment',(.81,.73,.52),28)
o.Label='E01 9004本体包络 - 未含磁座/取杯'
o=box('E02',[60,103,77],[390,100,'Parameters.SumpZ + Parameters.SumpGlass'],'Equipment',(.27,.42,.51),20)
o.Label='E02 回水泵本体示例 - 接管附件待核'
o=box('E03',[220,200,'Parameters.DisplayHeight - Parameters.DisplayGlass'],[70,230,'Parameters.DisplayZ + Parameters.DisplayGlass'],'Equipment',(.23,.31,.37),75)
o.Label='E03 溢流功能区占位 - 无已批准玻璃结构'
for code,cx,cy,d in [('D1',130,305,80),('D2',235,305,80),('R1',180,365,50)]:
    o=DOC.addObject('Part::Cylinder','Tool_'+code);o.Radius=d/2;o.Height=100
    o.Placement.Base=V(cx,cy,800)
    o.Label=code+' 工具包络 - 严禁用作钻孔坐标'
    GROUPS['Equipment'].addObject(o);color(o,(.79,.43,.24),80)

DOC.recompute()
visible(sk,False)
for o in GROUPS['Construction'].Group: visible(o,False)

def checks():
    DOC.recompute()
    for o in FINALS:
        assert not o.Shape.isNull(),o.Name
        assert o.Shape.isValid(),o.Name
        assert o.Shape.Volume>0,o.Name
    frame=Part.makeCompound([o.Shape for o in BEAMS]);bb=frame.BoundBox
    assert math.isclose(bb.XLength,P.FrameLength.Value,abs_tol=1e-5),(bb.XLength,P.FrameLength)
    assert math.isclose(bb.YLength,P.FrameDepth.Value,abs_tol=1e-5)
    assert math.isclose(bb.ZLength,P.FrameHeight.Value,abs_tol=1e-5)
    for i,a in enumerate(BEAMS):
        for b in BEAMS[i+1:]: assert a.Shape.common(b.Shape).Volume<1e-6,(a.Name,b.Name)
    for a in PLATES:
        for b in BEAMS: assert a.Shape.common(b.Shape).Volume<1e-6,(a.Name,b.Name)
    for i,a in enumerate(PLATES):
        for b in PLATES[i+1:]: assert a.Shape.common(b.Shape).Volume<1e-6,(a.Name,b.Name)
    return frame

frame=checks()
# Exercise native dependency graph rather than merely checking stored dimensions.
orig_d,orig_h=P.FrameDepth.Value,P.FrameHeight.Value
P.FrameDepth=470;P.FrameHeight=920;DOC.recompute()
changed_frame=Part.makeCompound([o.Shape for o in BEAMS]).BoundBox
assert math.isclose(changed_frame.YLength,470,abs_tol=1e-5)
assert math.isclose(changed_frame.ZLength,920,abs_tol=1e-5)
assert math.isclose(DOC.T3.CutLength.Value,390,abs_tol=1e-5)
assert math.isclose(DOC.P1.CutLength.Value,840,abs_tol=1e-5)
assert math.isclose(DOC.D02.Width.Value,370,abs_tol=1e-5)
assert math.isclose(DOC.A01.Shape.BoundBox.YLength,470,abs_tol=1e-5)
P.FrameDepth=orig_d;P.FrameHeight=orig_h;DOC.recompute();frame=checks()

cut_counts=Counter(round(o.CutLength.Value,6) for o in BEAMS)
assert cut_counts=={600:4,370:7,820:4},cut_counts
assert math.isclose(sum(o.CutLength.Value for o in BEAMS),8270,abs_tol=1e-6)
pan_usable=((P.PanLength.Value-4)*(P.PanDepth.Value-4)*32 - (2*600*40+4*370*40)*32)/1e6-1
assert math.isclose(pan_usable,5.104832,abs_tol=1e-8)

snapshot={
 'version':'v0.5','status':'设计评审，非加工批准','freecad_version':list(App.Version()),
 'parameters_mm':{name:getattr(P,name).Value for name,_,_,_ in PARAMS},
 'calculated_mm':{name:getattr(P,name).Value for name in ['SumpZ','FloorOffset','PanLength','PanDepth','TopZ','DisplayZ','Headspace']},
 'frame_bbox_mm':[frame.BoundBox.XLength,frame.BoundBox.YLength,frame.BoundBox.ZLength],
 'frame_with_nodes_bbox_mm':[612,462,900], 'pan_planning_usable_l':pan_usable,
 'reserve_l':22.06392,'reserve_remaining_30mm_l':.76392,
 'checks':{'native_depth_height_recompute':True,'beams_pairwise_no_solid_overlap':True,'plates_beams_and_each_other_no_solid_overlap':True},
 'beams':[{'id':o.Name,'label':o.Label,'cut_mm':o.CutLength.Value,'axis':o.Axis,
           'bbox_mm':[o.Shape.BoundBox.XMin,o.Shape.BoundBox.YMin,o.Shape.BoundBox.ZMin,o.Shape.BoundBox.XMax,o.Shape.BoundBox.YMax,o.Shape.BoundBox.ZMax]} for o in BEAMS],
 'objects':[{'id':o.Name,'label':o.Label,'volume_mm3':o.Shape.Volume} for o in FINALS],
 'limitations':['型材槽仅为通用示意，无真实供方截面','节点当前为四通孔，M8沉头待供方回图','玻璃厚度和支撑未批准','穿缸工具圆不是孔位','角码及设备包络不是完整采购实物','盘底长期压载和实测容水待核']
}
(OUT/'参数与验证-v0.5.json').write_text(json.dumps(snapshot,ensure_ascii=False,indent=2)+'\n')

# Visuals are projected from these native B-rep tessellations, not independently redrawn solids.
meshes=[]
for o in FINALS + list(GROUPS['Equipment'].Group):
    pts,tris=o.Shape.tessellate(1.0)
    meshes.append({'id':o.Name,'label':o.Label,
                   'vertices':[[v.x,v.y,v.z] for v in pts],
                   'triangles':[list(t) for t in tris],
                   'edges':[[[v.x,v.y,v.z] for v in e.discretize(Deflection=1.0)] for e in o.Shape.Edges]})
(OUT/'绘图几何-v0.5.json').write_text(json.dumps(meshes,separators=(',',':'),ensure_ascii=False))

Part.export(BEAMS+PLATES+[top,bottom,ground,pan],str(OUT/'框架与板件-v0.5.step'))
Part.export(FINALS,str(OUT/'总装布局-v0.5.step'))

# Reopen neutral file in an independent document; check assembly envelope survives.
roundtrip=App.newDocument('STEP_Check')
Part.insert(str(OUT/'框架与板件-v0.5.step'),roundtrip.Name)
roundtrip.recompute()
shapes=[o.Shape for o in roundtrip.Objects if hasattr(o,'Shape') and not o.Shape.isNull()]
assert shapes and all(s.isValid() for s in shapes)
rbb=Part.makeCompound(shapes).BoundBox
assert math.isclose(rbb.XLength,630,abs_tol=1e-4)
assert math.isclose(rbb.YLength,480,abs_tol=1e-4)
App.closeDocument(roundtrip.Name);App.setActiveDocument(DOC.Name)

if App.GuiUp:
    import FreeCADGui as Gui
    Gui.activeDocument().activeView().viewAxonometric()
    Gui.activeDocument().activeView().fitAll()
DOC.recompute()
DOC.saveAs(str(OUT/'Fishplan-v0.5.FCStd'))
print('FISHPLAN_NATIVE_MODEL_OK',str(OUT/'Fishplan-v0.5.FCStd'),flush=True)

if App.GuiUp:
    try:
        view=Gui.activeDocument().activeView()
        # The final file opens with the complete review layout. Frame-only views are export states.
        view.saveImage(str(OUT/'总装预览.png'),1800,1800,'White')
        for key in ['Tanks','Equipment']:
            for o in GROUPS[key].Group: visible(o,False)
        visible(top,False)
        view.fitAll();view.saveImage(str(OUT/'框架预览.png'),1800,1800,'White')
        for key in ['Tanks','Equipment']:
            for o in GROUPS[key].Group: visible(o,True)
        visible(top,True);view.fitAll();DOC.save()
    except Exception:
        (OUT/'预览异常.txt').write_text(traceback.format_exc())

(OUT/'建模完成.flag').write_text('native model and STEP verified\n')
