#!/usr/bin/env python3
"""Stage exports in .work, isolate FreeCAD recovery cache, verify before publishing.

Default: update PNG/SVG only. --rebuild-model is the explicit geometry-build path.
"""
from pathlib import Path
import argparse,subprocess,shutil,os,json,hashlib,zipfile,uuid,re
import xml.etree.ElementTree as ET

here=Path(__file__).resolve().parent;internal=here.parent;repo=internal.parents[1];delivery=repo/'图纸与模型'
parser=argparse.ArgumentParser();parser.add_argument('--rebuild-model',action='store_true');parser.add_argument('--audit-only',action='store_true');parser.add_argument('--guard',action='store_true',help='主缸围挡独立总装');args=parser.parse_args()
if args.guard:
    if not args.rebuild_model or args.audit_only:
        parser.error('围挡总装发布使用 --guard --rebuild-model')
    from 围挡发布 import publish_guard
    publish_guard(repo, here, delivery)
    raise SystemExit(0)
run=repo/'.work'/('freecad-run-'+uuid.uuid4().hex[:10]);run.mkdir(parents=True)
stage=run/'delivery';stage.mkdir();(run/'cache').mkdir();(run/'audit-cache').mkdir()
freecad=Path('/Users/dongyu/Applications/FreeCAD.app/Contents/Resources/bin/freecad')
python=freecad.parent/'python'
source_native=delivery/'底滤管路.FCStd';initial_hash=hashlib.sha256(source_native.read_bytes()).hexdigest()
if args.rebuild_model:
    snapshot=run/'发布前完整快照';snapshot.mkdir()
    for existing in [source_native,delivery/'底滤管路.step',internal/'数据/五区CAD显示.json']:
        shutil.copy2(existing,snapshot/existing.name)
shutil.copytree(here,stage/'源文件');shutil.copy2(here/'五区CAD显示.FCMacro',stage/'五区CAD显示.FCMacro')
shutil.copy2(source_native,stage/'五区管路总装.FCStd')
shutil.copy2(delivery/'底滤管路.step',stage/'五区管路总装.step')
shutil.copy2(internal/'数据/五区CAD显示.json',stage/'五区CAD显示.json')
cfg=run/'user.cfg';base=repo/'.work/五区CAD用户配置.cfg'
if base.exists():shutil.copy2(base,cfg)
env=os.environ.copy();env['FREECAD_USER_TEMP']=str(run/'cache');env['FISHPLAN_RUN_DIR']=str(run);env['FISHPLAN_WRITE_NATIVE']='1' if args.rebuild_model else '0'

def execute(command,environment,log):
    with log.open('w') as stream:
        result=subprocess.run([str(x) for x in command],env=environment,cwd=str(repo),stdout=stream,stderr=subprocess.STDOUT)
    assert result.returncode==0,(result.returncode,str(log))

def integrity(path):
    with zipfile.ZipFile(path) as archive:
        assert archive.testzip() is None,path
        ET.fromstring(archive.read('Document.xml'));ET.fromstring(archive.read('GuiDocument.xml'))

if not args.audit_only:
    if args.rebuild_model:
        execute([python,stage/'源文件/五区原生管路.py'],env,run/'生成日志.txt')
    execute([freecad,'-u',cfg,'-l','--log-file',run/'图纸应用日志.txt',stage/'五区CAD显示.FCMacro'],env,run/'图纸进程日志.txt')
    assert (run/'五区CAD完成.flag').exists(),str(run)
    report=json.loads((stage/'五区CAD验证.json').read_text());assert report['gui_open_save_reopen']
    assert not (run/'五区CAD显示错误.log').exists(),str(run)
integrity(stage/'五区管路总装.FCStd')
# The file is passed before the audit macro: exercise ordinary cold-start opening.
audit_env=env.copy();audit_env.update(FREECAD_USER_TEMP=str(run/'audit-cache'),FISHPLAN_AUDIT_DIR=str(run),FISHPLAN_AUDIT_FILE=str(stage/'五区管路总装.FCStd'),FISHPLAN_AUDIT_STYLES=str(stage/'五区CAD显示.json'))
execute([freecad,'-u',cfg,'-l','--log-file',run/'独立启动应用日志.txt',stage/'五区管路总装.FCStd',stage/'源文件/独立打开核验.FCMacro'],audit_env,run/'独立启动进程日志.txt')
audit=json.loads((run/'独立打开结果.json').read_text());assert audit['ok'],str(run/'独立打开结果.json')
assert Path(audit['cache_path']).resolve()==(run/'audit-cache').resolve(),audit['cache_path']
# Promote only complete files. Presentation refresh must not replace FCStd or STEP.
published=[]
if not args.audit_only:
    # Only publish final, useful views; throw-away capture bases stay inside this run.
    prefixes=('15-','16-','17-','19-','20-CAD阀门操作位置','21-CAD水流与阀门','22-CAD五仓配置','23-CAD实物配色.','24-CAD透明管放大')
    names=[p for p in stage.iterdir() if p.suffix.lower() in ['.png','.svg'] and p.name.startswith(prefixes) and '底图' not in p.name]
    names += [stage/'五区CAD显示.json']
    if args.rebuild_model:names += [stage/'五区管路总装.FCStd',stage/'五区管路总装.step',stage/'assembly-scene.json']
    image_names={'15-CAD正视管路.png':'管路正视.png','16-CAD底缸俯视.png':'底缸俯视.png','19-CAD右侧管路.png':'管路右视.png','17-CAD主泵越缸沿.png':'主泵越缸沿.png','20-CAD阀门操作位置.png':'阀门操作位置.png','21-CAD水流与阀门.png':'水流与阀门.png','22-CAD五仓配置.png':'五仓分区-含旧标注.png','23-CAD实物配色.png':'实物配色.png','24-CAD透明管放大.png':'透明管放大.png'}
    for src in names:
        target_name=src.name
        if src.suffix.lower()=='.svg':folder=internal/'矢量'
        elif src.suffix.lower()=='.png':
            folder=delivery if src.name.startswith(('15-','16-','19-')) else delivery/'细节'
            target_name=image_names[src.name]
        elif src.name=='assembly-scene.json':folder=repo/'资料/交付/网站/assets'
        elif src.suffix.lower()=='.json':folder=internal/'数据'
        else:
            folder=delivery
            target_name={'五区管路总装.FCStd':'底滤管路.FCStd','五区管路总装.step':'底滤管路.step'}[src.name]
        folder.mkdir(parents=True,exist_ok=True)
        target=folder/target_name;pending=folder/('.'+target_name+'.pending')
        shutil.copy2(src,pending);os.replace(pending,target);published.append(src.name)
if not args.rebuild_model:assert hashlib.sha256(source_native.read_bytes()).hexdigest()==initial_hash,'presentation overwrote native'
summary={'ok':True,'audit_only':args.audit_only,'rebuild_model':args.rebuild_model,'native_hash_before':initial_hash,'native_hash_after':hashlib.sha256(source_native.read_bytes()).hexdigest(),'cold_start':audit,'published':published,'run_dir':str(run),'cache_isolated':True}
(run/'结果.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
# Full validation reports belong to the isolated run, not the delivery folder.
print(json.dumps({'ok':True,'shapes':audit['valid_shapes'],'partial':audit['partial'],'cache_isolated':True,'native_unchanged':summary['native_hash_before']==summary['native_hash_after'],'run':str(run)},ensure_ascii=False))
