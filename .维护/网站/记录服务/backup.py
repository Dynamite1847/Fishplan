from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
import sqlite3,os
source=Path('/var/lib/fish-records/records.sqlite3')
if not source.is_file():raise SystemExit('数据库不存在，未生成空备份')
folder=Path('/var/backups/fish-records');folder.mkdir(parents=True,exist_ok=True)
target=folder/('records-'+datetime.now(ZoneInfo('Asia/Shanghai')).strftime('%Y%m%d-%H%M%S')+'.sqlite3')
with sqlite3.connect(source) as live,sqlite3.connect(target) as copy:
 live.backup(copy)
 assert copy.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
os.chmod(target,0o600)
print('记录数据库已备份并检查')
