"""Compose review sheets from actual CAD projections; no illustrated substitute geometry."""
import sys
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageChops

run=Path(sys.argv[1]); FONT='/System/Library/Fonts/Hiragino Sans GB.ttc'
def text(draw,xy,words,size=27,color='#172329',bold=False):
    draw.text(xy,words,font=ImageFont.truetype(FONT,size,index=int(bold)),fill=color)

def paste(canvas,name,rect):
    im=Image.open(run/name).convert('RGB')
    mask=ImageChops.difference(im,Image.new('RGB',im.size,'white')).convert('L').point(lambda x:255 if x>20 else 0)
    bound=mask.getbbox()
    if bound:im=im.crop((max(0,bound[0]-25),max(0,bound[1]-25),min(im.width,bound[2]+25),min(im.height,bound[3]+25)))
    x,y,w,h=rect;im.thumbnail((w,h),Image.Resampling.LANCZOS)
    canvas.paste(im,(x+(w-im.width)//2,y+(h-im.height)//2))

sheet=Image.new('RGB',(2000,1900),'white');d=ImageDraw.Draw(sheet)
text(d,(70,45),'围挡，把连接和日常使用一起设计',47,bold=True)
text(d,(72,115),'设计评审  /  哑黑外壳 · 灰银图案 · 隐藏挂接 · 后置低位风扇',27,'#607078')
paste(sheet,'围挡正视底图.png',(55,225,1110,835))
paste(sheet,'围挡总装正视底图.png',(1230,215,690,865))
text(d,(72,178),'1  正视 · 图案随前板一起拆走',30,bold=True)
text(d,(1260,178),'2  全缸位置参照',30,bold=True)
text(d,(72,1080),'3  俯视 · 灯在中央，风扇靠后',30,bold=True)
paste(sheet,'围挡俯视底图.png',(55,1130,970,560))
text(d,(1100,1115),'前板 612 × 216 × 4 mm',34,bold=True)
text(d,(1100,1175),'缸沿上 202 mm；下裙遮住安装座',27,'#56666f')
text(d,(1100,1250),'上提 12 mm → 向前取下',34,bold=True)
text(d,(1100,1310),'四个挂点承接；两只内侧旋扣防抬',27,'#56666f')
text(d,(1100,1385),'后部连接梁跨过灯夹缺口',34,bold=True)
text(d,(1100,1445),'左右板与后板构成固定 U 框',27,'#56666f')
text(d,(1100,1520),'风扇藏在围挡里',34,bold=True)
text(d,(1100,1580),'独立托臂传到后缸沿，前板不承重',27,'#56666f')
text(d,(72,1750),'图案为不透明黑板表面印刷；顶面保持敞开。围挡不能保证挡住向上跃出的鱼。',26,'#56666f')
text(d,(72,1800),'灯罩、风扇夹脚为外形包络；实物灯高与夹脚位置决定最终加工尺寸。',26,'#56666f')
sheet.save(run/'围挡设计总览.png')

sheet=Image.new('RGB',(2000,1580),'white');d=ImageDraw.Draw(sheet)
text(d,(70,45),'前板快拆，固定框保持连接',47,bold=True)
text(d,(72,115),'先旋开两只防抬扣，再上提 12 mm、向前取下；装回时反向操作。',27,'#607078')
paste(sheet,'围挡快拆底图.png',(50,220,1190,1010))
paste(sheet,'围挡挂接细节底图.png',(1270,250,660,650))
text(d,(75,180),'1  前板取下后的结构',30,bold=True)
text(d,(1290,180),'2  左上挂点 · 横向分解',30,bold=True)
text(d,(1280,935),'左：前板背面的钥匙孔挂片',27,bold=True)
text(d,(1280,985),'右：固定立条和灰色挂点',27,bold=True)
text(d,(1280,1035),'上面的横片：90°防抬旋扣',27,bold=True)
text(d,(75,1280),'后角连接',32,bold=True)
text(d,(75,1335),'两根 20 × 20 × 4 PMMA 内角条双面粘接；后顶梁连接两片后板。',28,'#56666f')
text(d,(75,1395),'正面没有外露螺丝。印刷不穿透板材，四角内侧遮缝。',28,'#56666f')
text(d,(75,1480),'模型已表达装拆路径；粘接强度、加工公差及风扇托臂先做局部试样。',25,'#607078')
sheet.save(run/'围挡连接与快拆.png')
