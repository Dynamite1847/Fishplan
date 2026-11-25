"""记录页和养护页共用的规则；无第三方依赖。"""
import json, math
from pathlib import Path
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo

RULES = json.loads(Path(__file__).with_name('rules.json').read_text())
TZ = ZoneInfo('Asia/Shanghai')
UNITS = {'nh3':'mg/L','no2':'mg/L','no3':'mg/L','kh':'dKH','ph':'','salinity':'比重','temperature':'℃','po4':'mg/L'}
NAMES = {'nh3':'NH3','no2':'NO2','no3':'NO3','kh':'KH','ph':'pH','salinity':'盐度','temperature':'水温','po4':'PO4'}

def number(v):
    return 0.0 if v == '<0.15' else 2.00001 if v == '>2' else (RULES['cycling']['no2_pass']+RULES['cycling']['no2_top'])/2 if v == 'between' else float(v)

def dt(s): return datetime.fromisoformat(s.replace('Z','+00:00')).astimezone(timezone.utc)
def fmt(v): return f'{v:g}'
def classify(key, value, phase):
    r=RULES; l=r['limits']; c=r['cycling']; animal=phase=='animals'; v=number(value)
    level='neutral'; text='仅记录'
    if key=='nh3':
        level=('green' if v==0 else 'red') if animal else ('yellow' if v>c['nh3_high'] else 'green')
        text=('0色' if v==0 else '换一半水，再按规则加Prime' if v>=r['doses']['animal_nh3_half_change_at'] else '换三分之一水') if animal else ('测稀释样，今天不加氯化铵水' if level=='yellow' else '养水期读数')
    elif key=='no2':
        level=('green' if v==0 else 'red') if animal else ('yellow' if v>=c['no2_top'] else 'green')
        text=('未显色' if v==0 else '已显色，复测并检查水质') if animal else ('到顶格，测稀释样' if level=='yellow' else '按NH3一起判断')
    elif key=='no3' and animal:
        level='green' if v<=l['no3_green_max'] else 'red' if v>=l['no3_red_min'] else 'yellow';text='正常' if level=='green' else '偏高，安排换水'
    elif key=='kh':level='green' if v>=l['kh'][1] else 'yellow' if v>=l['kh'][0] else 'red';text='正常' if level=='green' else '偏低' if level=='yellow' else '换水并复测'
    elif key=='ph':level='green' if v>=l['ph_min'] else 'red';text='正常' if level=='green' else '换水并复测'
    elif key=='salinity':
        a,b=l['salinity_green'];lo,hi=l['salinity_yellow'];level='green' if a<=v<=b else 'yellow' if lo<=v<=hi else 'red';text='正常' if level=='green' else '偏离目标，复核盐度'
    elif key=='temperature':
        tag='animals' if animal else 'cycling';a,b=l[f'temperature_{tag}_green'];lo,hi=l[f'temperature_{tag}_yellow'];level='green' if a<=v<=b else 'yellow' if lo<=v<=hi else 'red';text='正常' if level=='green' else '检查温控'
    elif key=='no3':text='养水期不分档'
    return {'level':level,'text':text}

def latest_metrics(records, phase):
    latest={}
    for row in reversed(records):
        for key,value in row['measurements'].items():
            if key in NAMES and value is not None and key not in latest:
                latest[key]={'value':value,'observed_at':row['observed_at'],'reagent':row.get('nh3_reagent') if key=='nh3' else None,**classify(key,value,phase)}
    return latest

def challenge_progress(records, volume):
    c=RULES['cycling']; passed=0;pending=None;events=[]
    for row in records:
        at=dt(row['observed_at']);m=row['measurements'];a=row['actions']
        if pending:
            hours=(at-dt(pending['observed_at'])).total_seconds()/3600
            if hours>c['check_latest_hours']:
                events.append({'at':row['observed_at'],'result':'超出24小时检查窗口，重新检查'});passed=0;pending=None
            elif hours>=c['check_hours'] and 'nh3' in m and 'no2' in m and row.get('nh3_reagent')=='yier':
                okay=number(m['nh3'])==0 and number(m['no2'])<=c['no2_pass']
                passed=passed+1 if okay else 0;events.append({'at':row['observed_at'],'result':f'通过第{passed}轮' if okay else '本轮未通过，连续轮次归零'});pending=None
        if a.get('ammonium_ml',0)>0:
            if pending:passed=0;pending=None;events.append({'at':row['observed_at'],'result':'检查期间又加氯化铵水，本轮不计'})
            if a.get('ammonium_kind')=='check':
                expected=volume*RULES['doses']['check_ml_per_l'] if volume else None
                if expected and .9*expected<=a['ammonium_ml']<=1.1*expected:pending={'observed_at':row['observed_at'],'due_at':(at+timedelta(hours=c['check_hours'])).isoformat()}
                else:passed=0;events.append({'at':row['observed_at'],'result':'检查剂量与当前水量不匹配，本轮不计'})
            elif passed:passed=0
        if pending and (a.get('water_change_l',0)>0 or a.get('prime_ml',0)>0):
            passed=0;pending=None;events.append({'at':row['observed_at'],'result':'检查期间换水或加Prime，本轮不计'})
    return {'passed':min(passed,c['check_rounds']),'required':c['check_rounds'],'pending':pending,'events':events[-10:]}

def advice(tank, records, now=None):
    now=now or datetime.now(timezone.utc);r=RULES;c=r['cycling'];d=r['doses'];v=tank['volume_l'];phase=tank['phase']
    rows=sorted([x for x in records if dt(x['observed_at'])<=now],key=lambda x:(x['observed_at'],x['id']))
    latest=latest_metrics(rows,phase);cycle=[x for x in rows if x.get('cycle_id')==tank['cycle_id'] and x.get('phase')=='cycling']
    progress=challenge_progress(cycle,v) if phase=='cycling' else {'passed':0,'required':c['check_rounds'],'pending':None,'events':[]}
    tips=[]
    def add(level,title,text):tips.append({'level':level,'title':title,'text':text})
    def amount(factor,unit='mL'):return f'{v*factor:.2f}{unit}' if v else '先填写实际水量，再计算用量'
    def fresh(key):return key in latest and (now-dt(latest[key]['observed_at'])).total_seconds()<=c['fresh_hours']*3600
    prime=next((x for x in reversed(rows) if x['actions'].get('prime_ml',0)>0),None)
    interference=prime is not None and (now-dt(prime['observed_at'])).total_seconds()<d['prime_interference_hours']*3600
    if not v:add('neutral','填写实际水量','主缸水量按加满后的实测升数填写；在此之前不计算加药和换水升数。')
    low_buffer=any(fresh(k) and number(latest[k]['value'])<threshold for k,threshold in [('kh',r['limits']['kh'][0]),('ph',r['limits']['ph_min'])])
    if low_buffer:
        lo,hi=c['low_buffer_change'];add('red','KH或pH偏低',f'换{lo*100:g}–{hi*100:g}%同温同盐海水（'+(f'{v*lo:.1f}–{v*hi:.1f}L' if v else '水量待填')+'），然后复测。')
    if phase=='animals':
        add('neutral','有动物：停加氯化铵水','少量分餐喂，吸走残饵和粪便；观察呼吸、游姿和进食。')
        if interference:add('yellow','Prime已记录，今天不重复加',f'加Prime后约{d["prime_interference_hours"]}小时内，沙里发NH3不能用于判断；按换水和动物状态处理，满{d["prime_interference_hours"]}小时再测。')
        if fresh('no2') and number(latest['no2']['value'])>0:add('red','NO2已显色','复测NO2，检查供氧和过滤，按检疫观察页处理。')
        if not fresh('nh3'):add('neutral','补测今天的NH3','最近24小时没有NH3记录，暂不据此计算应急换水。')
        else:
            item=latest['nh3'];n=number(item['value'])
            if item['reagent']=='salifert':add('yellow','沙里发仅供参考',r['notes']['nh3_salifert']+'；用益尔复核，同时观察动物状态。')
            if not (interference and (item['reagent']=='salifert' or dt(item['observed_at'])<=dt(prime['observed_at']))):
                if n>=d['animal_nh3_half_change_at']:add('red','NH3升高：换一半水',f'减喂、吸污，换{amount(d["animal_change_high"],"L")}同温同盐海水。'+('Prime已记录，今天不重复加。' if interference else f'换后Prime按整缸水量为{amount(d["prime_ml_per_l"])}。')+'如在用药，先核对兼容性。')
                elif n>0:add('red','NH3显色：换三分之一水',f'减喂、吸污，换{amount(d["animal_change_low"],"L")}同温同盐海水，第二天复测。')
                else:add('green','NH3为0色',f'维持观察；NH3一直为0时，每周换约{amount(d["weekly_change"],"L")}水。')
        return {'tips':tips,'progress':progress,'latest':latest}
    if low_buffer:
        add('neutral','换水后复测，再决定加药','今天先不加氯化铵水，KH和pH恢复后按新的NH3、NO2读数判断。')
        return {'tips':tips,'progress':progress,'latest':latest}
    if interference:add('yellow','养水期间已记录Prime','先停加氯化铵水；Prime干扰期内不自动判定检查通过，满24小时用可靠试剂复测。');return {'tips':tips,'progress':progress,'latest':latest}
    if progress['passed']>=c['check_rounds']:
        add('green',f'养好了：连续{c["check_rounds"]}轮通过',f'停止加氯化铵水，测NO3并按检疫桶养水页换水，水温调回{r["limits"]["temperature_animals_green"][0]:g}–{r["limits"]["temperature_animals_green"][1]:g}℃。');return {'tips':tips,'progress':progress,'latest':latest}
    pending=progress['pending']
    if pending:
        due=dt(pending['due_at']);end=due+timedelta(hours=c['check_latest_hours']-c['check_hours'])
        if now<due:add('neutral','正在做24小时检查',f'本轮到{due.astimezone(TZ):%m月%d日 %H:%M}满24小时；今天不追加氯化铵水。到时同次测NH3、NO2。')
        elif now<=end:add('neutral','检查量已满24小时',f'现在同次测益尔NH3和NO2并保存；NH3为0、NO2≤{c["no2_pass"]:g}才计通过。今天先不追加。')
        else:add('yellow','本轮缺少24小时复测','已超检查窗口，不能自动记为通过；先补测NH3和NO2，再按当前读数重新开始。')
        return {'tips':tips,'progress':progress,'latest':latest}
    if not fresh('nh3'):add('neutral','先测今天的NH3','最近24小时没有NH3读数；先测后决定，今天先不加。')
    elif latest['nh3']['reagent']!='yier':add('yellow','先用可靠NH3读数复核','沙里发在这桶海水里读数偏低；参考读数不自动触发补氨或通过检查，今天先不加。')
    elif number(latest['nh3']['value'])!=0:add('yellow' if number(latest['nh3']['value'])>c['nh3_high'] else 'neutral','今天不加氯化铵水','NH3还没有回到0。'+(f'读数高于{c["nh3_high"]:g}，按养水页测稀释样。' if number(latest['nh3']['value'])>c['nh3_high'] else '继续供氧控温，明天再测。'))
    elif not fresh('no2'):add('neutral','NH3为0，补测NO2','最近24小时没有NO2读数，先不加氯化铵水。')
    else:
        last_dose=next((x for x in reversed(cycle) if x['actions'].get('ammonium_ml',0)>0),None)
        measured=min(dt(latest['nh3']['observed_at']),dt(latest['no2']['observed_at']))
        if last_dose and (measured<=dt(last_dose['observed_at']) or (now-dt(last_dose['observed_at'])).total_seconds()<c['check_hours']*3600):
            add('neutral','今天已有加药记录','不重复加；本次加药满约24小时后再测NH3、NO2。')
        else:
            n=number(latest['no2']['value']);prefix=f'已通过第{progress["passed"]}轮，' if progress['passed'] else ''
            if n<=c['no2_pass']:add('green',prefix+'开始24小时检查',f'NH3为0、NO2≤{c["no2_pass"]:g}；检查量为{amount(d["check_ml_per_l"])}，加入后另存一条加药记录并选“检查量”。')
            elif n<c['no2_top']:
                today=now.astimezone(TZ).date();daily={}
                for x in cycle:
                    m=x['measurements']
                    if x.get('nh3_reagent')=='yier' and 'nh3' in m and 'no2' in m:
                        if not last_dose or dt(x['observed_at'])>dt(last_dose['observed_at']):daily[dt(x['observed_at']).astimezone(TZ).date()]=number(m['nh3'])==0 and c['no2_pass']<number(m['no2'])<c['no2_top']
                consecutive=all(daily.get(today-timedelta(days=i),False) for i in range(c['feed_wait_days']))
                add('yellow' if consecutive else 'neutral','补喂一次' if consecutive else '等NO2下降',f'连续{c["feed_wait_days"]}天在此范围，补喂{amount(d["feed_ml_per_l"])}。' if consecutive else f'NO2介于{c["no2_pass"]:g}与{c["no2_top"]:g}之间，今天先不加，明天再测。')
            else:
                row=next(x for x in reversed(rows) if 'no2' in x['measurements']);dil=row['measurements'].get('no2_diluted')
                if dil is None:add('yellow','NO2到顶格：测稀释样',f'2mL桶水＋{2*(c["dilution_factor"]-1):g}mL RO水，读数×{c["dilution_factor"]}。把稀释样读数补进同一条记录，再判断。')
                elif number(dil)*c['dilution_factor']<c['no2_feed_below']:add('yellow',f'稀释后低于{c["no2_feed_below"]:g}：补喂一次',f'稀释后约{number(dil)*c["dilution_factor"]:g}mg/L，补喂{amount(d["feed_ml_per_l"])}。')
                else:add('yellow',f'稀释后{c["no2_feed_below"]:g}或更高：继续等',f'今天不加氯化铵水，等NO2下降。稀释样也到顶时只能记作≥{c["no2_top"]*c["dilution_factor"]:g}。')
    return {'tips':tips,'progress':progress,'latest':latest}
