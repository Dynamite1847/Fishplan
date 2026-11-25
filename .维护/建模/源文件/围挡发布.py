"""Stage and cold-open the standalone rim guard before publishing it."""

import json
import os
import shutil
import subprocess
import uuid
from pathlib import Path


def publish_guard(repo, source, delivery):
    run = repo / '.work' / f'围挡FreeCAD-{uuid.uuid4().hex[:10]}'
    run.mkdir(parents=True)
    for folder in ('build-cache', 'audit-cache', '发布前完整快照'):
        (run / folder).mkdir()
    native = '主缸防跳围挡.FCStd'
    deliverables = {
        native: delivery,
        '主缸防跳围挡.step': delivery,
        '围挡背装总装.png': delivery / '细节',
        '围挡背视.png': delivery / '细节',
        '围挡右视.png': delivery / '细节',
        '围挡设计总览.png': delivery / '细节',
        '围挡连接与快拆.png': delivery / '细节',
    }
    for name, folder in deliverables.items():
        if (folder / name).is_file():
            shutil.copy2(folder / name, run / '发布前完整快照' / name)

    freecad = '/Users/dongyu/Applications/FreeCAD.app/Contents/Resources/bin/freecad'
    macro = source / '主缸围挡.FCMacro'
    config = run / 'user.cfg'
    environment = os.environ.copy()
    environment.update(
        FISHPLAN_GUARD_RUN=str(run),
        FISHPLAN_GUARD_REFERENCE=str(delivery / '底滤管路.FCStd'),
    )

    def execute(phase, *files):
        with (run / f'{phase}.log').open('w') as log:
            result = subprocess.run(
                [freecad, '-u', str(config), '-l', '--log-file', str(run / f'{phase}-App.log'), *map(str, files)],
                env=environment, cwd=repo, stdout=log, stderr=subprocess.STDOUT,
            )
        error = run / '围挡错误.log'
        if error.exists():
            raise RuntimeError(f'{run}\n{error.read_text()}')
        if result.returncode:
            raise RuntimeError(f'FreeCAD {phase} 退出 {result.returncode}，检查 {run}')

    environment.update(FREECAD_USER_TEMP=str(run / 'build-cache'), FISHPLAN_GUARD_AUDIT='0')
    execute('生成', macro)
    drawing_python = Path.home() / '.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3'
    subprocess.run([drawing_python, source / '围挡侧剖标注.py', run], check=True)
    subprocess.run([drawing_python, source / '围挡设计排版.py', run], check=True)
    environment.update(FREECAD_USER_TEMP=str(run / 'audit-cache'), FISHPLAN_GUARD_AUDIT='1')
    execute('冷启动', run / native, macro)
    audit = json.loads((run / '围挡冷启动结果.json').read_text())
    assert audit['ok'] and not audit['partial'], audit
    for name in deliverables:
        assert (run / name).stat().st_size > 0, name
    for name, folder in deliverables.items():
        pending = folder / f'.{name}.pending'
        shutil.copy2(run / name, pending)
        pending.replace(folder / name)
    print(json.dumps({'run': str(run), 'audit': audit, 'published': list(deliverables)}, ensure_ascii=False))
