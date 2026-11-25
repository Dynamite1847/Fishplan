#!/bin/bash
set -euo pipefail
PACKAGE="${1:?需要代码包目录}"
SNAPSHOT="/var/backups/fish-records-deploy/$(date -u +%Y%m%d-%H%M%S)"
install -d -m 700 "$SNAPSHOT"
cp -a /etc/nginx/sites-available/resume "$SNAPSHOT/nginx-resume"
if [ -d /opt/fish-records ]; then cp -a /opt/fish-records "$SNAPSHOT/app"; fi
if [ -f /var/lib/fish-records/records.sqlite3 ]; then
 /usr/bin/python3 - "$SNAPSHOT/records.sqlite3" <<'PY'
import sqlite3,sys
with sqlite3.connect('/var/lib/fish-records/records.sqlite3') as src,sqlite3.connect(sys.argv[1]) as dst:src.backup(dst)
PY
fi
if ! id fish-records >/dev/null 2>&1; then useradd --system --no-create-home --home-dir /var/lib/fish-records --shell /usr/sbin/nologin fish-records; fi
install -d -o root -g root -m 755 /opt/fish-records
install -d -o fish-records -g fish-records -m 700 /var/lib/fish-records /var/backups/fish-records
for filename in server.py care.py guide.py rules.json backup.py; do install -o root -g root -m 644 "$PACKAGE/$filename" "/opt/fish-records/$filename"; done
for filename in fish-records.service fish-records-backup.service fish-records-backup.timer; do install -o root -g root -m 644 "$PACKAGE/$filename" "/etc/systemd/system/$filename"; done
rollback() {
 cp -a "$SNAPSHOT/nginx-resume" /etc/nginx/sites-available/resume
 if [ -d "$SNAPSHOT/app" ]; then cp -a "$SNAPSHOT/app/." /opt/fish-records/; systemctl restart fish-records || true; else systemctl stop fish-records || true; fi
 nginx -t && systemctl reload nginx
 echo '部署未完成，已恢复原nginx配置；快照保留。' >&2
}
trap rollback ERR
/usr/bin/python3 - <<'PY'
from pathlib import Path
p=Path('/etc/nginx/sites-available/resume');s=p.read_text()
marker='    # Fish records API: public read, HTTPS authenticated write\n'
if marker not in s:
 needle='    location / {'
 assert s.count(needle)==2,'原站结构变化，停止自动修改'
 block=marker+'''    location ^~ /fish/api/ {
        proxy_pass http://127.0.0.1:8766/fish/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        client_max_body_size 16k;
        proxy_read_timeout 30s;
    }
'''
 s=s.replace(needle,block+needle);p.write_text(s)
PY
nginx -t
systemctl daemon-reload
systemctl enable --now fish-records.service
systemctl restart fish-records.service
for attempt in $(seq 1 20); do if curl -fsS http://127.0.0.1:8766/fish/api/state >/dev/null; then break; fi; sleep 1; done
curl -fsS http://127.0.0.1:8766/fish/api/state >/dev/null
systemctl reload nginx
systemctl enable --now fish-records-backup.timer
systemctl start fish-records-backup.service
trap - ERR
printf '记录服务已安装；nginx已检查并生效；数据库首份备份已生成。\n'
