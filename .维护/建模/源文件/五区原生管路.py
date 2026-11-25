"""FreeCAD native five-zone assembly, with swept hollow pipes and separate fittings.

Run with the installed FreeCAD Python runtime. Standard Part::Feature/Part::Box
objects need no Python proxy when reopening the FCStd file.
"""
from pathlib import Path
import sys, json, math
sys.path.insert(0, '/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A
import Part

OUT=Path(__file__).resolve().parents[1]
assert '.work' in OUT.parts,'请用 源文件/刷新图纸.py --rebuild-model 在临时目录构建，禁止直接覆盖交付文件'
V=A.Vector
doc=A.newDocument('FishplanFiveZone')
groups={}
for key,label in [('Frame','01 铝架与承托（固定支座见各路步骤0）'),('Glass','02 主缸与右侧长背包'),('Sump','03 已购600五区底缸'),('Equipment','04 蛋分与回水泵'),('DrainMain','05 主下水25'),('DrainEmergency','06 独立应急25'),('Return','07 单泵双20回水'),('ATO','08 自动补水暂缓（空）'),('Optional','09 试配水面（隐藏）')]:
    g=doc.addObject('App::DocumentObjectGroup',key);g.Label=label;groups[key]=g
STYLE={}; SHAPES={}; PIPES={}; EXPECTED=[]
WHITE=(.91,.92,.91); GREY=(.28,.31,.34); RED=(.72,.12,.16); GLASS=(.62,.83,.88)

def obj(name,label,shape,group,color=WHITE,alpha=0,role='助手建模占位，实际接口与结构未验收'):
    o=doc.addObject('Part::Feature',name);o.Label=label;o.Shape=shape
    o.addProperty('App::PropertyString','Evidence','Fishplan');o.Evidence=role
    groups[group].addObject(o);STYLE[name]={'color':color,'alpha':alpha,'visible':True,'group':group};SHAPES[name]=o
    return o

def box(name,label,size,pos,group,color=WHITE,alpha=0,role='尺寸包络，非厂商实物模型'):
    o=doc.addObject('Part::Box',name);o.Label=label
    o.Length,o.Width,o.Height=size;o.Placement.Base=V(*pos)
    o.addProperty('App::PropertyString','Evidence','Fishplan');o.Evidence=role
    groups[group].addObject(o);STYLE[name]={'color':color,'alpha':alpha,'visible':True,'group':group};SHAPES[name]=o
    return o

def cyl(r,h,p,d=(0,0,1)):return Part.makeCylinder(r,h,V(*p),V(*d))
def tube(r,ri,h,p,d=(0,0,1)):return cyl(r,h,p,d).cut(cyl(ri,h,p,d))

def profile(name,size,pos,axis):
    # Approximate 4040 slot appearance; not a manufacturer section or strength model.
    L=size[axis];shape=Part.makeBox(*size,V(*pos))
    if axis==2:
        cuts=[(V(pos[0]+16,pos[1]-1,pos[2]),[8,7,L]),(V(pos[0]+16,pos[1]+34,pos[2]),[8,7,L]),(V(pos[0]-1,pos[1]+16,pos[2]),[7,8,L]),(V(pos[0]+34,pos[1]+16,pos[2]),[7,8,L])]
    elif axis==0:
        cuts=[(V(pos[0],pos[1]+16,pos[2]-1),[L,8,7]),(V(pos[0],pos[1]+16,pos[2]+34),[L,8,7]),(V(pos[0],pos[1]-1,pos[2]+16),[L,7,8]),(V(pos[0],pos[1]+34,pos[2]+16),[L,7,8])]
    else:
        cuts=[(V(pos[0]+16,pos[1],pos[2]-1),[8,L,7]),(V(pos[0]+16,pos[1],pos[2]+34),[8,L,7]),(V(pos[0]-1,pos[1],pos[2]+16),[7,L,8]),(V(pos[0]+34,pos[1],pos[2]+16),[7,L,8])]
    for p,d in cuts:shape=shape.cut(Part.makeBox(*d,p))
    return obj(name,'4040 '+name,shape,'Frame',GREY,role='4040外包络与槽外观简化；不代表原厂截面或承重验算')

for z,prefix in [(0,'Bottom'),(860,'Top')]:
    for y in [0,410]:profile(f'{prefix}_X_{y}',[600,40,40],[0,y,z],0)
    for x in [0,200,400,560]:profile(f'{prefix}_Y_{x}',[40,370,40],[x,40,z],1)
for x in [0,560]:
    for y in [0,410]:profile(f'Post_{x}_{y}',[40,40,820],[x,y,40],2)
box('LowerPP','下层10厚PP板（600×350覆盖待核）',[600,350,10],[0,50,40],'Frame',(.64,.66,.67),role='只确认原板10厚；此为完整覆盖底缸的承托要求，实际长深/挠度待核')
box('UpperBoard','顶部承板（18厚为占位，实物核）',[600,450,18],[0,0,900],'Frame',(.19,.21,.23))
box('UpperMat','已购主缸垫层8厚',[600,450,8],[0,0,918],'Frame',(.07,.08,.09))

# Main tank, bottom intact; visual return cut-outs are explicitly provisional.
display=Part.makeBox(600,450,500,V(0,0,926)).cut(Part.makeBox(584,434,500,V(8,8,934)))
for yy in [75,390]:display=display.cut(cyl(16,24,[588,yy,1389],[1,0,0]))
obj('Display','主缸600×450×500，8厚，底部无孔',display,'Glass',GLASS,88,'外尺寸/厚度用户确认；两回水孔位置及32孔径为建模占位，禁止作为玻璃开孔依据')
overflow=Part.makeBox(120,240,450,V(600,105,976)).cut(Part.makeBox(104,224,450,V(608,113,984)))
for yy in [160,280]:overflow=overflow.cut(cyl(21,20,[660,yy,970]))
obj('Overflow','右侧长背包120×240×450',overflow,'Glass',GLASS,85,'沿缸侧240、外突120、高450；底部标高、42示意孔径与孔距待核')
board=Part.makeBox(4,240,440,V(598,105,984))
for i in range(16):board=board.cut(Part.makeBox(8,5,23,V(596,119+i*13,1392)))
for i in range(16):board=board.cut(Part.makeBox(8,5,15,V(596,119+i*13,1023)))
obj('BlackComb','黑色上下鱼梳面板（内部水道未建实）',board,'Glass',(.07,.08,.09),role='只表达外观与上下取水口；密封导流夹层、堰高及真实过水水道未知')

# Purchased sump: exact outside, approximate partition closure, no fabrication approval.
box('SumpBase','底缸底板600×350×6',[600,350,6],[0,50,50],'Sump',GLASS,75)
for name,size,pos in [('Front',[600,6,394],[0,50,56]),('Back',[600,6,394],[0,394,56]),('Left',[6,338,394],[0,56,56]),('Right',[6,338,394],[594,56,56])]:
    box('Sump'+name,'底缸'+name+'玻璃6厚',size,pos,'Sump',GLASS,82)
for name,size,pos in [('PartitionA',[6,338,200],[156,56,56]),('PartitionB',[6,338,200],[382,56,56]),('Sediment',[150,6,220],[6,308,56]),('AlgaeFirst',[206,6,200],[388,252,56]),('PumpSecond',[206,6,180],[388,268,76])]:
    box(name,'示意隔板 '+name,size,pos,'Sump',GLASS,50,role='板高/过水口未确认；闭合内尺寸左150、中220、右206，商家右列标约208，未改实物')
# Explicitly model a bottom passage rather than accidentally sealing all flow.
SHAPES['PartitionA'].Height=180;SHAPES['PartitionA'].Placement.Base.z=76
box('DryWetTray','左列可取洗干湿板占位',[136,180,5],[13,100,280],'Sump',(.93,.94,.93),role='商品是否含干湿板及实际板高/防堵溢流待核；非另购过滤塔')

# SK2200 silhouette within verified 175x171x474 equipment envelope.
skpos=V(185,95,56);cx,cy=272.5,180.5
sk=Part.makeBox(165,165,12,V(190,98,56)).fuse(Part.makeCone(72,32,285,V(cx,cy,68))).fuse(cyl(32,72,[cx,cy,353]))
obj('SkimmerBody','SK2200蛋分本体（外观简化）',sk,'Equipment',(.93,.94,.94),role='厂家整机瓶身175×171、总高474；用户底座165×165；非原厂内部结构')
obj('SkimmerCup','SK2200可取收集杯',tube(75,70,94,[cx,cy,430]),'Equipment',GLASS,55)
obj('SkimmerCupBase','收集杯底',cyl(75,5,[cx,cy,425]),'Equipment',(.78,.8,.81))
obj('SkimmerLid','收集杯盖',cyl(76,6,[cx,cy,524]),'Equipment',(.25,.28,.3))
obj('SkimmerKnob','蛋分旋钮占位',cyl(12,16,[355,170,150],[0,-1,0]),'Equipment',RED)
sk_env=Part.makeBox(175,171,474,skpos)
pump=Part.makeBox(170,70,95,V(408,278,60)).fuse(cyl(30,70,[548,313,120],[1,0,0]).common(Part.makeBox(170,70,128,V(408,278,60)))).fuse(cyl(11,33,[550,313,155]))
pump.rotate(V(493,313,0),V(0,0,1),180)
obj('MainPump','CN-S600 18W，水平转180°布置',pump,'Equipment',(.22,.28,.32),role='尺寸/价格用户提供；水平转180°后名义出水口从右端移至左端X436，给接头及卡箍留空间；端口外形仍为占位，实物试摆核吸入口净距')
pump_env=Part.makeBox(170,70,128,V(408,278,60))
pump_feet=Part.makeCompound([Part.makeBox(14,14,4,V(x,y,56)) for x in [416,556] for y in [286,326]])
obj('PumpFeet','主泵4高隔振脚占位',pump_feet,'Equipment',(.13,.15,.16),role='机身前移22、抬高4；4mm隔振脚为布局占位，实物脚垫/最低水位及吸入口间距待核')

# Purchased heater and planned dry-start biological media. No extra reactor or algae light.
# Image says height 74 x width 190 x thickness 25. This placement is a planning orientation.
heater_env=Part.makeBox(190,25,84,V(177,335,56))
obj('HeaterBody','已购300W低水位加热棒：190×25×74外形',Part.makeBox(190,25,74,V(177,335,66)),'Equipment',(.17,.20,.23),role='用户商品图高×宽×厚74×190×25；按图卧放候选，支脚10为占位；海水适用、最低水位及厂家安装方向待实物说明，不代表热安全验收')
cover=Part.makeBox(180,3,60,V(182,335,73))
for n in range(12):cover=cover.cut(Part.makeBox(7,5,42,V(188+n*14,334,82)))
obj('HeaterCover','加热棒红色护网外观',cover,'Equipment',(.80,.14,.18))
feet=Part.makeBox(12,25,10,V(185,335,56)).fuse(Part.makeBox(12,25,10,V(347,335,56)))
obj('HeaterFeet','加热棒安装脚占位',feet,'Equipment',(.17,.20,.23),role='仅用于留出10高支撑包络；真实吸盘/脚架与离玻璃距离未核')
for j,(x,y,z) in enumerate([(25,75,76),(25,185,76),(25,75,111),(25,185,111)]):
    box('BioBlock'+str(j),'已购培菌砖：共4块，尺寸占位',[100,100,25],[x,y,z],'Equipment',(.65,.59,.48))
box('CoarsePad','粗棉单层',[136,180,20],[13,100,305],'Equipment',(.72,.81,.82))
box('FinePad','细棉单层',[136,180,20],[13,100,285],'Equipment',(.87,.91,.9))
box('CarbonBag','棉后炭袋（首鱼前启用）',[90,65,12],[30,90,150],'Equipment',(.25,.32,.32))
for z in [71,106]:box('BrickGrid'+str(z),'开孔托砖架包络',[110,220,5],[20,70,z],'Equipment',(.44,.51,.48),55)

# Design paths: vertical legs and plan-diagonal drain runs. Corner radii make actual hollow elbow-like geometry.
paths={
 'Main':[[660,160,976],[660,160,840],[85,335,840],[85,335,256]],
 'Emergency':[[660,280,976],[660,280,840],[115,375,840],[115,375,296]],
 'ReturnCommon':[[538,225,350],[538,225,740]],
 'ReturnFront':[[538,225,740],[538,75,740],[538,75,838],[635,75,838],[635,75,1389],[580,75,1389]],
 'ReturnRear':[[538,225,740],[538,390,740],[538,390,838],[635,390,838],[635,390,1389],[580,390,1389]],
}

assert paths['ReturnCommon'][-1] == paths['ReturnFront'][0] == paths['ReturnRear'][0], 'disconnected tee'

def on_centerline(p,key):
    point=V(*p)
    return any((point-V(*a)).cross(V(*b)-V(*a)).Length<1e-6 and (point-V(*a)).dot(point-V(*b))<=1e-6 for a,b in zip(paths[key],paths[key][1:]))

def swept(points,r,ri,bend):
    vv=[V(*p) for p in points];edges=[];last=vv[0]
    for i in range(1,len(vv)-1):
        vin=vv[i]-vv[i-1];vout=vv[i+1]-vv[i]
        n1,n2=vin.Length,vout.Length;vin.normalize();vout.normalize()
        if abs(vin.dot(vout))>1e-7:raise ValueError('only orthogonal corners supported')
        # Two adjacent fillets share a segment; allow a fuller radius at an endpoint.
        lim1=n1*.9 if i==1 else n1*.45;lim2=n2*.9 if i==len(vv)-2 else n2*.45
        rr=min(bend,lim1,lim2)
        assert rr>r+0.5,(rr,r,points)
        entry=vv[i]-vin*rr;exitp=vv[i]+vout*rr;center=vv[i]-vin*rr+vout*rr
        if (entry-last).Length>1e-7:edges.append(Part.makeLine(last,entry))
        midvec=(entry-center)+(exitp-center);midvec.normalize();mid=center+midvec*rr
        edges.append(Part.Arc(entry,mid,exitp).toShape());last=exitp
    if (vv[-1]-last).Length>1e-7:edges.append(Part.makeLine(last,vv[-1]))
    wire=Part.Wire(edges);normal=vv[1]-vv[0];normal.normalize()
    outer=Part.Wire([Part.makeCircle(r,vv[0],normal)])
    solid=wire.makePipeShell([outer],True,False)
    if ri:
        inner=Part.Wire([Part.makeCircle(ri,vv[0],normal)]);solid=solid.cut(wire.makePipeShell([inner],True,False))
    return solid

for key,pts in paths.items():
    group='DrainMain' if key=='Main' else 'DrainEmergency' if key=='Emergency' else 'ATO' if key=='ATO' else 'Return'
    r,ri,bend=(12.5,10.5,30) if key in ['Main','Emergency'] else (3,2,10) if key=='ATO' else (10,8,28)
    sh=swept(pts,r,ri,bend)
    if key=='Main':
        # Separate removable tail below the above-rim union.
        sh=sh.cut(Part.makeBox(50,50,520,V(60,310,0)))
    if key=='Emergency':sh=sh.cut(Part.makeBox(50,50,580,V(90,350,0)))
    if key=='ReturnCommon':
        sh=sh.cut(Part.makeBox(90,90,70,V(493,180,630)))
    o=obj('Pipe'+key,{'Main':'主下水25：前孔→上部微调阀→左后接水格','Emergency':'独立应急25：后孔→上部横管→左后接水格（无阀）','ReturnCommon':'主泵上水20：柜内主管→顶部三通→前后回水','ReturnFront':'前侧20回水','ReturnRear':'后侧20回水','ATO':'补水软管：沿边固定，禁止跨杯'}[key],sh,group,WHITE if key!='ATO' else (.48,.57,.63),role='公制外径示意，壁厚/弯头半径/承口长度待所购产品核；竖直腿经90°接水平斜管，横段微坡/复电排气待试验')
    o.addProperty('App::PropertyString','CenterlineMM','Fishplan');o.CenterlineMM=json.dumps(pts)
    PIPES[key]=o
    if key in ['ReturnFront','ReturnRear']:
        yy=75 if key=='ReturnFront' else 390
        region=Part.makeBox(120,60,100,V(550,yy-30,1361))
        included_elbow=o.Shape.common(region)
        o.Shape=o.Shape.cut(region)
        obj('ReturnElbow'+str(yy),'20回水穿缸套装自带弯头 '+str(yy),included_elbow,'Return',GREY,role='按用户已购回水接头自带弯头规划；此转向计入R01套装，不另耗R06独立90°。具体承口长度按实物')

# Separate removable tail; the reference water surface is a trial setting, not measured.
tail=tube(12.5,10.5,264,[85,335,256])
PIPES['MainTail']=obj('PipeMainTail','主排透明可拆尾管：参考水面下20',tail,'DrainMain',WHITE,role='Z520活接以下264长为模型试配；参考水面Z276未实测，真实水位确认后按10至25浅淹试调定长，拆前停泵/松管夹')
PIPES['EmergencyTail']=obj('PipeEmergencyTail','应急透明可拆尾管：参考水面上20',tube(12.5,10.5,284,[115,375,296]),'DrainEmergency',WHITE,role='Z580活接以下284为模型试配；正常水面未实测，按实际水面上10至20定尾管，拆前停泵')
water_ref=Part.makeBox(130,60,0.5,V(16,323,275.75))
obj('SedimentTrialWater','试配水面Z276（非实际运行水位）',water_ref,'Optional',(.23,.64,.85),80,role='仅供表达主排末端浅淹20；不推定隔板水位，不计入容量验收；默认隐藏')
STYLE['SedimentTrialWater']['visible']=False

def union(name,p,axis,r,group):
    d=V(*axis);base=V(*p)-d*18
    sh=Part.makeCylinder(r+7,36,base,d).cut(Part.makeCylinder(r-2,36,base,d))
    sh=sh.fuse(Part.makeCylinder(r+10,13,V(*p)-d*6.5,d).cut(Part.makeCylinder(r-2,13,V(*p)-d*6.5,d)))
    finish='白色' if name in ['UnionClearCommon','ReturnUnionPump'] else '透明' if name in ['MainTailUnion','EmergencyUnionLower','UnionClearFront','ReturnUnionFront','UnionClearRear','ReturnUnionRear'] else '深灰色'
    return obj(name,('25' if r==12.5 else '20')+finish+'独立活接',sh,group,(.58,.62,.65),role='用户2026-11-04实物颜色清单；独立活接安装包络，承口和扳手空间按实物')
for x in [260,380]:union('MainGateUnion'+str(x),[x,160,840],[1,0,0],12.5,'DrainMain')
union('MainTailUnion',[85,335,520],[0,0,1],12.5,'DrainMain')
union('MainUpperUnion',[660,160,950],[0,0,1],12.5,'DrainMain')
for p,ax,n in [([660,280,950],[0,0,1],'Upper'),([115,375,580],[0,0,1],'Lower')]:union('EmergencyUnion'+n,p,ax,12.5,'DrainEmergency')
for p,ax,n in [([538,225,480],[0,0,1],'Pump'),([635,75,1190],[0,0,1],'Front'),([635,390,1190],[0,0,1],'Rear')]:union('ReturnUnion'+n,p,ax,10,'Return')

# D1: front drain, accessible wheel facing the room.
valve=Part.makeBox(82,52,52,V(259,134,784)).cut(cyl(10.5,100,[250,160,810],[1,0,0]))
valve=valve.fuse(cyl(12,56,[300,140,810],[0,-1,0]))
obj('GateValveBody','D1 前排主下水25微调阀',valve,'DrainMain',WHITE,role='82/112简化包络，真实商品全开行程待核')
wheel=tube(25,20,8,[300,76,810],[0,1,0]).fuse(Part.makeBox(46,8,8,V(277,76,806))).fuse(Part.makeBox(8,8,46,V(296,76,787)))
obj('GateHandwheel','D1 朝前微调手轮',wheel,'DrainMain',RED)

# R1/R2/R3: three independently removable return shutoff valves.
# Bodies include simplified union collars; subtract included unions from the purchase list.
valve_access=[]
operating_envelopes={}
check_removal_envelope=None

def return_ball(name,label,center,axis,kind):
    c=V(*center);d=V(*axis)
    body=tube(24,8,80,list(c-d*40),axis)
    for k in [-40,28]:body=body.fuse(tube(27,8,12,list(c+d*k),axis))
    if kind=='down':
        body=body.fuse(cyl(9,22,[c.x,c.y,c.z-24],[0,0,-1]))
        handle=cyl(10,8,[c.x,c.y,c.z-46],[0,0,-1]).fuse(Part.makeBox(12,55,8,V(c.x-6,c.y,c.z-54)))
        copies=[]
        for angle in range(0,91,10):
            h=handle.copy();h.rotate(V(c.x,c.y,c.z-50),V(0,0,1),angle);copies.append(h)
        operating_envelopes[name]=Part.makeBox(100,100,48,V(c.x-80,c.y-20,c.z-83))
        handle_center=[c.x,c.y,c.z-50]
    elif kind.startswith('top'):
        body=body.fuse(cyl(9,22,[c.x,c.y,c.z+24]))
        handle=cyl(10,8,[c.x,c.y,c.z+46]).fuse(Part.makeBox(12,55,8,V(c.x-6,c.y,c.z+46)))
        # 90 degree sweep from +Y to +X; add hand clearance when testing.
        copies=[]
        for angle in range(0,91,10):
            h=handle.copy();h.rotate(V(c.x,c.y,c.z+50),V(0,0,1),angle if kind=='top_left' else -angle);copies.append(h)
        operating_envelopes[name]=Part.makeBox(100,100,48,V(c.x-80 if kind=='top_left' else c.x-20,c.y-20,c.z+35))
        handle_center=[c.x,c.y,c.z+50]
    elif kind.startswith('right'):
        body=body.fuse(cyl(9,30,[c.x+24,c.y,c.z],[1,0,0]))
        handle=cyl(10,8,[c.x+50,c.y,c.z],[1,0,0]).fuse(Part.makeBox(8,12,55,V(c.x+50,c.y-6,c.z)))
        copies=[]
        for angle in range(0,91,10):
            h=handle.copy();h.rotate(V(c.x+54,c.y,c.z),V(1,0,0),-angle if kind=='right_rear' else angle);copies.append(h)
        operating_envelopes[name]=Part.makeBox(45,100,100,V(c.x+35,c.y-80,c.z-20))
        handle_center=[c.x+54,c.y,c.z]
    else:
        body=body.fuse(cyl(9,30,[c.x,c.y-24,c.z],[0,-1,0]))
        handle=cyl(10,8,[c.x,c.y-58,c.z],[0,1,0]).fuse(Part.makeBox(12,8,55,V(c.x-6,c.y-58,c.z)))
        copies=[]
        for angle in range(0,91,10):
            h=handle.copy();h.rotate(V(c.x,c.y-54,c.z),V(0,1,0),angle);copies.append(h)
        operating_envelopes[name]=Part.makeBox(100,45,100,V(c.x-20,c.y-80,c.z-20))
        handle_center=[c.x,c.y-54,c.z]
    obj(name+'Body',label+' 双活接阀体占位',body,'Return',WHITE,role='公制20、完整阀体80长为布局候选；全塑海水适用、真实长度/通径/手柄行程待具体SKU核验')
    obj(name+'Handle',label+' 红色操作柄',handle,'Return',RED)
    valve_access.append({'id':name,'role':label,'center_mm':center,'handle_mm':handle_center,'handle_direction':'朝下、柜内可达' if kind=='down' else '朝上、右侧可达' if kind.startswith('top') else '朝右侧' if kind.startswith('right') else '朝柜前','access_checked_nominal':False})
    return Part.makeCompound(copies)

return_sweeps={}
return_sweeps['ReturnIsolation']=return_ball('ReturnIsolation','R1 主管20检修球阀',[538,225,550],[0,0,1],'front')
return_sweeps['ReturnFrontValve']=return_ball('ReturnFrontValve','R2 前口20独立球阀',[635,75,965],[0,0,1],'right')
return_sweeps['ReturnRearValve']=return_ball('ReturnRearValve','R3 后口20独立球阀',[635,390,965],[0,0,1],'right_rear')

# C1: common inboard vertical riser immediately before the split; upward flow.
check_body=tube(26,18,70,[538,225,630])
obj('ReturnCheckBody','C1 主管20可拆止回阀：竖直向上',check_body,'Return',(.48,.77,.79),65,role='70长候选包络，海水材料、竖直安装及起开流量待具体商品核，不作为接水唯一措施')
check_ends=tube(29,8,12,[538,225,630]).fuse(tube(29,8,12,[538,225,688]))
obj('ReturnCheckUnions','C1 两端自带活接包络',check_ends,'Return',WHITE)
obj('ReturnCheckFlap','C1 内件类别示意',cyl(17,3,[538,225,663]),'Return',(.36,.42,.44))
check_removal_stages=[Part.makeBox(60,110,80,V(605,310,675)),
                      Part.makeBox(180,60,80,V(485,310,675)),
                      Part.makeBox(60,450,80,V(485,-80,675))]
operating_envelopes['GateValve']=Part.makeBox(100,85,100,V(250,25,760))
valve_access.append({'id':'GateValve','role':'D1 主下水25精调','center_mm':[300,160,810],'handle_mm':[300,80,810],'handle_direction':'朝柜前','access_checked_nominal':False})
# A smooth ~0.20 m hose raises above the sump's baffles before entering the rigid riser.
softcurve=Part.BezierCurve();softcurve.setPoles([V(436,313,188),V(436,313,285),V(538,225,285),V(538,225,350)])
softwire=Part.Wire([softcurve.toShape()])
softshape=softwire.makePipeShell([Part.Wire([Part.makeCircle(12,V(436,313,188),V(0,0,1))])],True,False).cut(softwire.makePipeShell([Part.Wire([Part.makeCircle(10,V(436,313,188),V(0,0,1))])],True,False))
obj('PumpSoftLink','泵上内径20柔性短接：弧长约'+str(round(softcurve.toShape().Length))+'mm',softshape,'Return',(.23,.27,.30),role='内径20，外径24为占位；泵水平转180°，从左侧出水口上升越隔板后弯向柜内主管；弧长约222、最小中心曲率半径约42为布局估算，保留已列0.3m备料。实物试弯不折扁；泵不悬吊管重')

for key,y in [('Main',160),('Emergency',280)]:
    obj('Bulkhead'+key,'25主排穿缸套装' if key=='Main' else '25应急穿缸套装',tube(23,10.5,6,[660,y,970]).fuse(tube(19,10.5,8,[660,y,976])).fuse(tube(23,10.5,5,[660,y,984])),'DrainMain' if key=='Main' else 'DrainEmergency',(.73,.75,.76),role='接头法兰和穿缸螺母包络；实际型号、孔径与密封件未冻结')
    height=262 if key=='Main' else 422
    obj('Standpipe'+key,'背包抬高主排立管' if key=='Main' else '背包高位应急立管',tube(12.5,10.5,height,[660,y,984]),'DrainMain' if key=='Main' else 'DrainEmergency',WHITE,role='主排/应急分别独立；入口标高为外观占位，须结合背包运行水位及停泵排水核实')
for y in [75,390]:
    bulk=tube(14,8,8,[592,y,1389],[1,0,0]).fuse(tube(20,8,4,[588,y,1389],[1,0,0])).fuse(tube(20,8,4,[600,y,1389],[1,0,0]))
    obj('ReturnBulkhead'+str(y),'20回水穿缸接头 '+str(y),bulk,'Return',(.72,.74,.75),role='颈部/两侧法兰分开示意；孔中心仅评审候选上移4，实物孔已定时须用适配可调嘴，禁止据此开孔')
    nozzle=Part.makeCone(12,8,30,V(580,y,1389),V(-1,0,0)).cut(cyl(6,32,[581,y,1389],[-1,0,0]))
    obj('ReturnNozzle'+str(y),'高位可调回水嘴 '+str(y),nozzle,'Return',(.15,.18,.20),role='模型开口中心463、半径6、最低边缘457（相对主缸外底），比455条件高2；实际嘴型/孔位/破虹吸及回流仍须实物验收')
# Inverted equal tee: upward common inlet, front/rear outputs along Y.
tee=cyl(17,60,[538,195,740],[0,1,0]).fuse(cyl(17,30,[538,225,710]))
tee=tee.cut(cyl(8,70,[538,190,740],[0,1,0])).cut(cyl(8,40,[538,225,705]))
obj('ReturnTee','20三通：下进、前后横向分流',tee,'Return',WHITE,role='标准等径三通转向安装；止回放在分流前，接口尺寸按实物')
for name in ['GateValveBody','GateHandwheel']:
    shape=SHAPES[name].Shape.copy();shape.translate(V(20,0,30));SHAPES[name].Shape=shape
# Rotate the whole serviceable gate assembly onto the diagonal run.
angle=-math.degrees(math.atan2(175,575));gate_y=160+(660-320)*175/575
for name in ['GateValveBody','GateHandwheel','MainGateUnion260','MainGateUnion380']:
    shape=SHAPES[name].Shape.copy();shape.rotate(V(320,160,840),V(0,0,1),angle);shape.translate(V(0,gate_y-160,0));SHAPES[name].Shape=shape

# Both plain bulkheads use one independent union, then a short clear spool.
# The lower transparent tail is independently removable on each drain.
clear_specs=[('ClearMainUpper','Main',[660,160,870],60,'DrainMain',[0,0,1]),('ClearEmergencyUpper','Emergency',[660,280,870],60,'DrainEmergency',[0,0,1]),('ClearCommon','ReturnCommon',[538,225,380],100,'Return',[0,0,1]),('ClearFront','ReturnFront',[635,75,1050],140,'Return',[0,0,1]),('ClearRear','ReturnRear',[635,390,1050],140,'Return',[0,0,1])]
for name,key,base,length,group,axis in clear_specs:
    rr=12.5 if key in ['Main','Emergency'] else 10
    original=PIPES[key].Shape.copy();blank=tube(rr,rr-2,length,base,axis)
    clear=original.common(blank);PIPES[key].Shape=original.cut(blank)
    assert clear.Volume>0,name
    obj(name,{'ClearMainUpper':'主排孔下透明直管','ClearEmergencyUpper':'应急孔下透明直管','ClearCommon':'泵上可拆透明管','ClearFront':'前回水可拆透明管','ClearRear':'后回水可拆透明管'}[name],clear,group,GLASS,22,'布局用本体长度，真实裁长需计实物承插；孔下60为给独立活接留位的估算')
    if key not in ['Main','Emergency']:union('Union'+name,base,axis,rr,group)

# Give each real installation stage its own CAD shape. Splits preserve BRep
# volumes exactly, including the swept 90 degree elbows; the web uses these.
def split_pipe(key,specs):
    o=PIPES[key];original=o.Shape.copy();remaining=original.copy();group=STYLE[o.Name]['group'];made=[]
    for suffix,size,pos in specs:
        sh=original.common(Part.makeBox(*size,V(*pos)))
        if sh.Volume>1e-6:
            no=obj('Pipe'+key+suffix,o.Label+' '+suffix,sh,group,WHITE)
            made.append(no)
    assert abs(original.Volume-sum(x.Shape.Volume for x in made))<1e-3,key
    del STYLE[o.Name];del SHAPES[o.Name];doc.removeObject(o.Name)
    return made
split_pipe('Main',[('02',[110,450,1200],[620,0,0]),('03',[490,450,100],[130,0,760]),('04',[130,450,1200],[0,0,0])])
split_pipe('Emergency',[('02',[110,450,1200],[620,0,0]),('03',[460,450,100],[160,0,760]),('04',[160,450,1200],[0,0,0])])
split_pipe('ReturnCommon',[('02',[800,500,500],[0,0,0]),('03',[800,500,110],[0,0,500]),('04',[800,500,1000],[0,0,610])])

# Direct-mounted pipe clips: integrated bases touch the aluminum face.
# Base-to-axis 20 mm is a layout assumption pending the user's actual clip.
supports=[]
def support(name,p,axis,od,group,anchor,kind):
    rr=od/2;d=V(*axis);ring=tube(rr+3,rr+.2,12,list(V(*p)-d*6),axis)
    # User's photo: open C snap clip with an integral flat slot-mounted base.
    if kind=='top':mouth=Part.makeBox(14,rr*1.3,rr+4,V(p[0]-7,p[1]-rr*.65,p[2]-rr-4))
    elif axis==[0,1,0]:mouth=Part.makeBox(rr+4,14,rr*1.3,V(p[0],p[1]-7,p[2]-rr*.65))
    else:mouth=Part.makeBox(rr+4,rr*1.3,14,V(p[0],p[1]-rr*.65,p[2]-7))
    angle=math.degrees(math.atan2(axis[1],axis[0])) if kind=='top' else 0
    if kind=='top':mouth.rotate(V(*p),V(0,0,1),angle)
    ring=ring.cut(mouth)
    label={'Main220':'主排支点1','Main420':'主排支点2','Emergency220':'应急支点1','Emergency420':'应急支点2','ReturnFront':'前回水顶部支点','ReturnRear':'后回水顶部支点'}[name]
    if kind=='top':
        thickness=860-(p[2]+rr+3)
        base=Part.makeBox(24,20,thickness+.5,V(p[0]-12,p[1]-10,p[2]+rr+2.5))
    else:
        thickness=p[0]-(rr+3)-600
        base=Part.makeBox(thickness+.5,24,12,V(600,p[1]-12,p[2]-6))
    if kind=='top':base.rotate(V(*p),V(0,0,1),angle)
    sh=ring.fuse(base)
    assert len(sh.Solids)==1,(name,"clip body disconnected")
    o=obj('Clip'+name,str(od)+'直装C形管夹 '+label,sh,group,(.43,.56,.48),role='按用户商品图改为开口C形、底座直接贴型材；图无尺寸，中心距按约20放样（25夹20、20夹22），不另加吊杆/长支座')
    gap=sh.distToShape(SHAPES[anchor].Shape)[0];assert gap<.01,(name,'not direct mounted',gap)
    supports.append({'id':name,'group':group,'pipeAxisMM':p,'anchorFrame':anchor,'frameContactGapMM':round(gap,4),'directMounted':True,'baseToAxisMM':20 if od==25 else 22,'status':'直装款式用户确认；中心高20为暂定放样值'})
for rid,y,group in [('Main',160,'DrainMain'),('Emergency',280,'DrainEmergency')]:
    a,b=paths[rid][1:3];direction=V(*a)-V(*b);direction.normalize()
    for x,beam in [(220,200),(420,400)]:
        yy=a[1]+(a[0]-x)*(b[1]-a[1])/(a[0]-b[0]);support(rid+str(x),[x,yy,840],list(direction),25,group,'Top_Y_'+str(beam),'top')
support('ReturnFront',[580,75,838],[1,0,0],20,'Return','Top_Y_560','top')
support('ReturnRear',[580,390,838],[1,0,0],20,'Return','Top_Y_560','top')
for name,p in [('PumpBarb',[436,313,178]),('HardBarb',[538,225,340])]:obj(name,'20软管宝塔接头',tube(11,8,20,p),'Return',WHITE)
for j,p in enumerate([[436,313,195],[538,225,340]]):obj('HoseClamp'+str(j),'短软接防脱卡箍',tube(14,12,6,p),'Return',(.5,.57,.55))

# Assembly descriptions use the existing procurement IDs. Handles/integrated
# union ends share the purchased valve, so they never create extra quantities.
def part(pid,name,qty=1,unit='只'):return {'id':pid,'name':name,'qty':qty,'unit':unit}
routes=[];steps={};assigned={}
def route(rid,title,color,items):
    r={'id':rid,'title':title,'shortTitle':{'main':'主下水','emergency':'应急下水','return':'上水'}[rid],'color':color,'steps':[]};routes.append(r)
    for num,title,desc,checks,parts,names in items:
        sid=rid+str(num).zfill(2);ids=[n for n in names if n in SHAPES]
        assert len(ids)==len(names),(sid,[n for n in names if n not in SHAPES])
        st={'id':sid,'title':title,'description':desc,'checks':checks,'parts':parts,'objectIds':ids};steps[sid]=st;r['steps'].append(st)
        for n in ids:assert n not in assigned,n;assigned[n]=(rid,sid)
route('main','主下水：孔下透明、斜向左后','#8759a7',[
 (0,'先装两处斜管支撑','25直装C卡仍贴顶部两根前后向梁底槽，夹体顺着斜管转向；沿槽调Y位置，不加吊杆。',['先松定位，再无胶试拼','管中心距梁底暂20，夹直管、避开阀体和活接'],[part('M01a','25管夹',2)],['ClipMain220','ClipMain420']),
 (1,'前孔普通穿缸件与立管','用户确认穿缸件只有玻璃固定螺母；其用于压紧胶垫，不能替代独立管路活接。装好两穿缸件后可先局部RO检漏。',['固定螺母与胶垫按套装说明装','背包内立管按水位试配，不按占位高度裁切'],[part('D01','25穿缸套装',1,'套'),part('D04','25紫管立管',1,'段')],['BulkheadMain','StandpipeMain']),
 (2,'孔下活接→透明短管→90°','两路孔下统一：独立深灰活接→透明短直管→25承插90°。将弯头绕竖管轴转向左后，让斜管直接指向左后接水格。透明本体暂约60，实际计承插定裁长。',['穿缸件固定螺母不作日常拆管用','这只孔下活接使硬管可拆，透明段不再按原100硬裁'],[part('D03','25独立深灰活接'),part('CL25','25透明短管',1,'段'),part('D06','25承插90°弯头'),part('D04','25紫管短接',1,'段')],['MainUpperUnion','ClearMainUpper','PipeMain02']),
 (3,'斜管→活接→近黑灰微调阀（红柄）→活接','柜顶下方沿斜线直达左后；阀及两端活接随管轴转向，手轮仍朝柜前可操作。',['两处C卡承托斜管','两端活接使近黑灰微调阀（红柄）可单独拆洗'],[part('D02','25近黑灰微调闸阀（红柄）'),part('D03','25独立深灰活接',2),part('D04','25紫管',1,'组')],['PipeMain03','MainGateUnion260','GateValveBody','GateHandwheel','MainGateUnion380']),
 (4,'到左后→第二个90°转下','斜管到左后接水格上方，第二个90°直接转下；取消原先先向左、再向后的中间弯头。',['本路90°共2只','上部按管夹实物轻微调坡，RO试水检查排气'],[part('D06','25承插90°弯头'),part('D04','25紫管',1,'段')],['PipeMain04']),
 (5,'末端活接→透明尾管','保留缸沿上方活接及透明尾管；实际运行后按水面下约20定末端长度，图示264只作放样。',['拆尾管前停泵','末端不深埋、不压棉'],[part('D03','25独立透明活接'),part('CL25','25透明尾管',1,'段')],['MainTailUnion','PipeMainTail'])])
route('emergency','应急下水：同样孔下透明、独立斜走','#b18dc8',[
 (0,'先装应急两处斜管支撑','应急也沿两根顶部前后梁底槽，夹体顺应急斜管转向；两路各2夹，前后错开。',['25直装夹共4只','沿槽调夹点，保持两路独立'],[part('M01a','25管夹',2)],['ClipEmergency220','ClipEmergency420']),
 (1,'后孔普通穿缸件与高位立管','后孔穿缸件同样只有固定玻璃的螺母，孔下另留独立可拆点；应急入口高于主排，实际按背包水位放样。',['入口留上涨余量','正常尽量无水，启泵短时过水不靠尾阀关断'],[part('D01','25穿缸套装',1,'套'),part('D04','25紫管立管',1,'段')],['BulkheadEmergency','StandpipeEmergency']),
 (2,'孔下活接→透明短管→90°','和主排同位置、同接法：独立透明活接→约60透明短管→第一个90°转向左后。',['实物承插深度计入裁长','两孔下各1只活接，穿缸件胶垫密封保持不动'],[part('D03','25独立深灰活接'),part('CL25','25透明短管',1,'段'),part('D06','25承插90°弯头'),part('D04','25紫管短接',1,'段')],['EmergencyUnionUpper','ClearEmergencyUpper','PipeEmergency02']),
 (3,'独立斜管直达左后','应急从后孔直接斜向左后接水格，不再先向左再接一段短横管。',['全程不合流、不加阀','两支点固定，保持平顺'],[part('D04','25紫管',1,'段')],['PipeEmergency03']),
 (4,'第二个90°转下','到接水格正上方用第二个90°转下，取消原左侧中间弯。原左侧透明观察段改到孔下，不再用双活接夹住中间观察段。',['本路90°共2只','下降段不挡取棉及设备拆取'],[part('D06','25承插90°弯头'),part('D04','25紫管',1,'段')],['PipeEmergency04']),
 (5,'尾端活接→透明尾管→故障测试','应急尾端和主排一样保留1只可拆活接及透明尾管，活接比主排高60便于拧，图示尾管284，出口按实际水面上10～20定长；不装尾阀。',['正常无水通过主排阀与泵流量试调实现','要停水拆管：先停泵，等回流停止；拆穿缸件前还须排空背包','主排全堵，从低到最高泵档测独立应急，接近外溢即停'],[part('D03','25独立透明活接'),part('CL25','25透明尾管',1,'段')],['EmergencyUnionLower','PipeEmergencyTail'])])
route('return','上水：从缸侧向下，最后接泵','#a2adb2',[
 (0,'先松装柜顶两处管夹','两只20直装C卡贴右侧450方向顶部梁底槽，前后各一只。先松装，待缸侧接口向下试拼后锁紧。',['管夹夹直管，底座直接贴型材','低位管路留在铝架内，靠电视柜侧尽早收进柜顶'],[part('M01b','20管夹',2)],['ClipReturnFront','ClipReturnRear']),
 (1,'从前回水口向下接前支路','先安装前回水嘴和自带弯头的穿缸套装；从缸侧向下接透明活接→140透明管→透明活接→侧面竖管球阀，再接向柜顶管夹的弯头和横管，向下、向内接到三通位置。',['缸口已自带弯头，不再叠加独立90°','本支路另用灰色90°三只；球阀深灰、柄朝右侧，操作转向前方','顶部横向弯头中心距97，露出直段约41；竖向中心距98，露出约42；实物承插另计'],[part('R01','20自带弯头回水穿缸套装',1,'套'),part('R02','回水嘴',1,'套'),part('R04','20透明独立活接',2),part('CL20','20透明管',1,'段'),part('V01','20深灰双活接球阀'),part('R06','20灰色承插90°',3),part('R03','20浅灰管',1,'组')],['ReturnBulkhead75','ReturnElbow75','ReturnNozzle75','ReturnUnionFront','ClearFront','UnionClearFront','ReturnFrontValveBody','ReturnFrontValveHandle','PipeReturnFront']),
 (2,'从后回水口向下，和前支路对齐','后口同样从缸侧向下接。透明段与前路同高同长，阀门在侧面竖管同高，后阀红柄朝右、操作转向后方避开背包。两支路下端先留在三通位置。',['后口也复用套装弯头，独立灰色90°三只','两路竖管对准后再锁紧顶部管夹，不强掰玻璃接口'],[part('R01','20自带弯头回水穿缸套装',1,'套'),part('R02','回水嘴',1,'套'),part('R04','20透明独立活接',2),part('CL20','20透明管',1,'段'),part('V01','20深灰双活接球阀'),part('R06','20灰色承插90°',3),part('R03','20浅灰管',1,'组')],['ReturnBulkhead390','ReturnElbow390','ReturnNozzle390','ReturnUnionRear','ClearRear','UnionClearRear','ReturnRearValveBody','ReturnRearValveHandle','PipeReturnRear']),
 (3,'合到三通，再向下接止回阀','灰色20三通横向两口接前后支路，向下的一口接白色＋透明止回阀。安装向下推进，水流箭头仍向上。止回保持紧靠分流处。',['止回阀套装自带拆卸端，不额外叠加独立活接','止回按未封住测停泵最高水位'],[part('R05','20灰色等径三通'),part('V02','20白色＋透明止回阀'),part('R03','20浅灰管',1,'段')],['ReturnTee','PipeReturnCommon04','ReturnCheckBody','ReturnCheckUnions','ReturnCheckFlap']),
 (4,'继续向下接主管球阀','止回阀下接主管深灰双活接球阀，阀柄朝柜前。日常全开，检修先停泵再隔离。',['球阀自带活接端，独立活接不重复加在阀两端','实物阀长决定上下短管裁长'],[part('V01','20深灰双活接球阀'),part('R03','20浅灰管',1,'段')],['PipeReturnCommon03','ReturnIsolationBody','ReturnIsolationHandle']),
 (5,'白活接→主管透明段→白活接','向下接白色独立活接、100透明观察管、白色独立活接，再接硬管宝塔接口位置。两只白活接集中在主管，便于辨认拆泵位置。',['主管用白2只，前后支路用透明4只；灰20活接3只留备用','透明管长度为模型本体，承插深度现场另计'],[part('R04','20白色独立活接',2),part('CL20','20透明管',1,'段'),part('R03','20浅灰管',1,'段')],['ReturnUnionPump','ClearCommon','UnionClearCommon','PipeReturnCommon02']),
 (6,'最后摆泵，量裁柔性短接','泵在右后仓水平转180°，名义出水口移到左端，先试摆再量软管。软管从泵口向上越过隔板，接到已定位的硬管宝塔；两端装防脱卡箍。',['模型软管弧长约222，备0.3m；最小中心曲率半径约42，实物试弯不折扁后定裁长','旋转后泵包络不变，实际吸入口与出水接头按实物核；硬管重量由管夹承担','全部无胶试拼对准，按活接分组件取出胶接；固化后装回试水'],[part('PUMP','CN-S600（水平转180°）',1,'台'),part('R07b','泵端原配接头',1,'套'),part('R07a','内径20短软管',1,'段'),part('R07b2','宝塔转接'),part('R07c','防脱卡箍',2)],['MainPump','PumpBarb','PumpSoftLink','HardBarb','HoseClamp0','HoseClamp1'])])

# No old options remain: ATO and Optional are valid empty/hidden groups.
STYLE['SedimentTrialWater']['visible']=False
# Colour and assign one installation step to every routed physical component.
for n,o in SHAPES.items():
    if n in assigned:
        rid,sid=assigned[n]
        o.addProperty('App::PropertyString','AssemblyStep','Fishplan');o.AssemblyStep=sid
        STYLE[n]['color']=(.53,.35,.66) if rid in ['main','emergency'] else (.65,.7,.72)
        if n.startswith('Clear') or n in ['PipeMainTail','PipeEmergencyTail']:STYLE[n]['color']=(.15,.66,.78);STYLE[n]['alpha']=22
        if 'Union' in n:STYLE[n]['color']=(.25,.28,.30)
        if n in ['MainTailUnion','EmergencyUnionLower','UnionClearFront','ReturnUnionFront','UnionClearRear','ReturnUnionRear']:STYLE[n]['color']=(.66,.77,.80);STYLE[n]['alpha']=8
        if n in ['UnionClearCommon','ReturnUnionPump','ReturnCheckUnions']:STYLE[n]['color']=(.91,.93,.92)
        if 'Handle' in n:STYLE[n]['color']=(.7,.18,.2)
        if n=='GateValveBody' or n.endswith(('ValveBody','IsolationBody')):STYLE[n]['color']=(.16,.18,.20)
        if n=='GateHandwheel':STYLE[n]['color']=(.72,.12,.16)
        if n=='ReturnCheckBody':STYLE[n]['color']=(.62,.76,.79);STYLE[n]['alpha']=12
        if n=='ReturnCheckFlap':STYLE[n]['color']=(.35,.40,.42)
        if n.startswith(('Bulkhead','ReturnBulkhead','ReturnElbow')) or n=='ReturnTee':STYLE[n]['color']=(.23,.26,.28)
        if n.startswith(('Mount','Clip')):STYLE[n]['color']=(.45,.59,.5)
        if n in ['MainPump','PumpSoftLink']:STYLE[n]['color']=(.23,.3,.32)
    elif STYLE[n]['group'] in ['DrainMain','DrainEmergency','Return']:
        raise AssertionError(('routed object has no assembly step',n))
# Mark the swept elbow faces gray in the native CAD as well as the web view.
for n,o in SHAPES.items():
    key=next((k for k in paths if n.startswith('Pipe'+k)),None)
    if not key or n in ['PipeMainTail','PipeEmergencyTail']:continue
    pts=paths[key];zones=[]
    for i in range(1,len(pts)-1):
        incoming=V(*pts[i])-V(*pts[i-1]);outgoing=V(*pts[i+1])-V(*pts[i])
        before,after=incoming.Length,outgoing.Length;incoming.normalize();outgoing.normalize()
        radius=min(30 if key in ['Main','Emergency'] else 28,before*(.9 if i==1 else .45),after*(.9 if i==len(pts)-2 else .45))
        entry=V(*pts[i])-incoming*radius;exitp=V(*pts[i])+outgoing*radius
        zones.append((entry,exitp,entry+outgoing*radius,incoming,outgoing,radius+(12.5 if key in ['Main','Emergency'] else 10)+.1))
    def is_elbow(p):return any((p-a).dot(u)>=-.01 and (p-b).dot(v)<=.01 and (p-c).Length<=limit for a,b,c,u,v,limit in zones)
    STYLE[n]['faceColors']=[(.22,.24,.26) if is_elbow(f.CenterOfMass) else STYLE[n]['color'] for f in o.Shape.Faces]
# Layer visibility uses standard shapes, with no Python proxy.
doc.recompute()
invalid=[n for n,o in SHAPES.items() if o.Shape.isNull() or not o.Shape.isValid()];assert not invalid,invalid
fixed=[o for n,o in SHAPES.items() if n.startswith(('Top_','Bottom_','Post_','Sump')) or n in ['UpperBoard','UpperMat','LowerPP','PartitionA','PartitionB','Sediment','AlgaeFirst','PumpSecond','Display','Overflow','BlackComb']]
primary=[o for n,o in SHAPES.items() if n.startswith(('Pipe','Clear')) or n=='PumpSoftLink']
conflicts=[];pairs=[]
for o in primary:
    for b in fixed:
        if not o.Shape.BoundBox.intersect(b.Shape.BoundBox):continue
        vv=o.Shape.common(b.Shape).Volume
        if vv>.02:conflicts.append([o.Name,b.Name,round(vv,3)])
for i,o in enumerate(primary):
    for b in primary[i+1:]:
        if assigned[o.Name][0]==assigned[b.Name][0] or not o.Shape.BoundBox.intersect(b.Shape.BoundBox):continue
        vv=o.Shape.common(b.Shape).Volume
        if vv>.02:pairs.append([o.Name,b.Name,round(vv,3)])
assert not conflicts,conflicts
assert not pairs,pairs
fitting_fixed=[]
for name,o in SHAPES.items():
    if not name.startswith(('Union','MainUpperUnion','MainGateUnion','MainTailUnion','EmergencyUnion','ReturnUnion','GateValveBody','GateHandwheel','ReturnIsolation','ReturnFrontValve','ReturnRearValve','ReturnCheck','ReturnTee')):continue
    for b in fixed:
        if not o.Shape.BoundBox.intersect(b.Shape.BoundBox):continue
        vv=o.Shape.common(b.Shape).Volume
        if vv>.02:fitting_fixed.append([name,b.Name,round(vv,3)])
assert not fitting_fixed,fitting_fixed
handle_conflicts=[]
for name in ['ReturnFrontValve','ReturnRearValve']:
    for b in fixed:
        vv=return_sweeps[name].common(b.Shape).Volume
        if vv>.02:handle_conflicts.append([name,b.Name,round(vv,3)])
assert not handle_conflicts,handle_conflicts
mount_conflicts=[]
for n in SHAPES:
    if not n.startswith('Clip'):continue
    for other in primary+[o for name,o in SHAPES.items() if name.startswith(('GateValve','ReturnCheck','ReturnIsolation','ReturnFrontValve','ReturnRearValve'))]:
        vv=SHAPES[n].Shape.common(other.Shape).Volume
        if vv>.02:mount_conflicts.append([n,other.Name,round(vv,3)])
assert not mount_conflicts,mount_conflicts
cup=cyl(78,210,[272.5,180.5,530]);cup_conflicts=[]
for n in assigned:
    vv=SHAPES[n].Shape.common(cup).Volume
    if vv>.02:cup_conflicts.append([n,round(vv,3)])
assert not cup_conflicts,cup_conflicts
assert len(supports)==6
counts={}
for r in routes:
    for st in r['steps']:
        for p in st['parts']:counts[p['id']]=counts.get(p['id'],0)+p['qty']
for pid,q in [('D01',2),('D02',1),('D03',6),('D06',4),('V01',3),('V02',1),('R04',6),('R06',6),('R05',1),('R01',2),('R02',2),('M01a',4),('M01b',2),('CL25',4),('CL20',3)]:assert counts[pid]==q,(pid,counts[pid],q)
validation={'valid_shapes':len(SHAPES),'invalid':invalid,'pipe_frame_sump_conflicts':conflicts,'pipe_pipe_conflicts':pairs,'fitting_frame_glass_conflicts':fitting_fixed,'branch_handle_sweep_conflicts':handle_conflicts,'cup_vertical_sweep_conflicts':cup_conflicts,'supports':supports,'support_pipe_valve_conflicts':mount_conflicts,'quantity_check':counts,'manual_valves':5,'emergency_manual_valves':0,'pipe_centerlines':paths,'gui_open_save_reopen':False,'scope':'名义布局/独立加载核验；真实承口/工具/整机拆卸及水力以现场试装和RO联调验收'}
scene={'schema':1,'revision':'2026-11-04-actual-colors-topdown-v12','units':'mm','pipeCenterlinesMM':paths,'routes':routes,'supports':supports,'objects':[],'quantityCheck':counts,'notes':['穿缸件装好后可先封正常出水口、少量RO局部检漏；下鱼梳可能连通主缸，详细步骤见安装与试水说明。','按用户实物颜色：25灰活接4只装孔下及微调阀两端，透明2只装尾管，透明1只备用；20透明4只装前后支路，白2只装主管，灰3只备用。微调阀近黑灰＋红柄，止回白＋透明。','先松装型材管夹，三路均从鱼缸端向下无胶试拼；上水先前后支路，再三通、止回、主管阀及透明段，最后连接转180°的泵和软管。','试拼完成并检查阀门、活接和设备拆取后，再分组件在缸外胶接；按实际胶水固化后才能通水。','管夹为贴型材直装款；底面到管轴按约20mm放样（25夹20、20夹22），用户接受估算，安装沿槽微调。孔位、承口及阀件按实物，不直接照模型裁管或开孔。','两根下水各2只25的90°，孔下均为独立活接＋约60透明短管，普通穿缸固定螺母不作活接。应急全程无阀；停水检修先停泵，拆穿缸件前排空背包。','25直装管夹4只、20直装管夹2只；不加支臂或吊杆。20独立弯头安装6只、原备料8只余2；两缸口复用穿缸套装自带弯头；20管夹备料3只余1备用。先核订单，只补缺件。','两下水各自独立落左后格；末段高度按运行水位定长。止回失效、停泵复电与最高档应急通量均须实测。']}
for n,o in SHAPES.items():
    if not STYLE[n]['visible']:continue
    rid,sid=assigned.get(n,(None,None));st=steps.get(sid,{})
    pid=''
    if rid:
        if n.startswith('Mount'):pid='M01c'
        elif n.startswith('Clip'):pid='M01a' if rid in ['main','emergency'] else 'M01b'
        elif 'Bulkhead' in n or n.startswith('ReturnElbow'):pid='D01' if rid in ['main','emergency'] else 'R01'
        elif n.startswith('Standpipe'):pid='D04'
        elif 'Nozzle' in n:pid='R02'
        elif 'Check' in n:pid='V02'
        elif 'Union' in n:pid='D03' if rid in ['main','emergency'] else 'R04'
        elif n.startswith('Clear') or n in ['PipeMainTail','PipeEmergencyTail']:pid='CL25' if rid in ['main','emergency'] else 'CL20'
        elif 'Gate' in n:pid='D02'
        elif 'Valve' in n or 'Isolation' in n:pid='V01'
        elif n=='ReturnTee':pid='R05'
        elif n=='PumpSoftLink':pid='R07a'
        elif n=='PumpBarb':pid='R07b'
        elif n=='HardBarb':pid='R07b2'
        elif n.startswith('HoseClamp'):pid='R07c'
        elif n=='MainPump':pid='PUMP'
        else:pid='D04 / D06' if rid in ['main','emergency'] else 'R03 / R06'
    import MeshPart
    mesh=MeshPart.meshFromShape(Shape=o.Shape,LinearDeflection=1.0,AngularDeflection=.25,Relative=False)
    verts,faces=mesh.Topology
    c=STYLE[n]['color'];color='#'+''.join(format(round(x*255),'02x') for x in c)
    scene['objects'].append({'id':n,'label':o.Label,'group':STYLE[n]['group'],'route':rid,'stepId':sid,'kind':'clear' if n.startswith('Clear') or n in ['PipeMainTail','PipeEmergencyTail'] else 'mount' if n.startswith('Mount') else 'support' if n.startswith('Clip') else 'context' if not rid else 'part','procurementId':pid,'description':st.get('description',o.Label),'evidence':o.Evidence,'color':color,'finish':('white' if n in ['UnionClearCommon','ReturnUnionPump','ReturnCheckUnions'] else 'clear' if n in ['MainTailUnion','EmergencyUnionLower','UnionClearFront','ReturnUnionFront','UnionClearRear','ReturnUnionRear','ReturnCheckBody'] else 'gray'),'opacity':1-STYLE[n]['alpha']/100,'geometry':{'positions':[round(x,3) for v in verts for x in (v.x,v.y,v.z)],'indices':[i for f in faces for i in f]}})
(OUT/'assembly-scene.json').write_text(json.dumps(scene,ensure_ascii=False,separators=(',',':'))+'\n')
(OUT/'五区CAD验证.json').write_text(json.dumps(validation,ensure_ascii=False,indent=2)+'\n')
(OUT/'五区CAD显示.json').write_text(json.dumps(STYLE,ensure_ascii=False,indent=2)+'\n')
doc.Label='60缸｜实物配色与缸侧向下装配｜2026-11-04'
doc.saveAs(str(OUT/'五区管路总装.FCStd'))
Part.export([o for n,o in SHAPES.items() if STYLE[n]['visible']],str(OUT/'五区管路总装.step'))
A.closeDocument(doc.Name)
print(json.dumps({'shapes':len(SHAPES),'steps':len(steps),'supports':len(supports)},ensure_ascii=False))
