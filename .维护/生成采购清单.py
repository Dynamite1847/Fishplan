#!/usr/bin/env python3
"""从本地的02-采购账本.md生成不带价格的02-采购清单.md（公开到GitHub）。

账本只留本地（已写进.gitignore），清单由本脚本生成，不手改。
git提交前钩子（.git/hooks/pre-commit）会自动运行；发现价格漏进清单就报错、拦下提交。
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / '02-采购账本.md'
DST = ROOT / '02-采购清单.md'

# 账本里要公开的二级标题 → 清单里的标题
KEEP = {
    '已下单': '已买',
    '接下来配什么': '接下来配什么',
    '已购设备与接口': '已购设备与接口',
    '管件备料与订单核对': '管件备料',
    '滤材、砂石与菌剂': '滤材、砂石与菌剂',
}
SKIP_SUB = {'已到账退款'}
MONEY = re.compile(r'\d[\d,]*(?:\.\d+)?\s*元|实付|退款|退回|已合计|金额|单价|价格|查价|降价|报价|付款|入账|记账|预算')
RETURNED = re.compile(r'全额退款|全额退回')
# 指向不公开文件的链接只留文字（链接地址里可能带价格）
PRIVATE_LINK = re.compile(
    r'\[([^\]]*)\]\((?:资料/商家/|资料/参考图/|\.维护/水族名录价格/|\.维护/蓝海有赞/|02-采购账本\.md)[^)]*\)')
DROP = re.compile(r'当前有效订单|见退款表')
MONEY_PAREN = re.compile(r'（[^（）]*(?:降价|\d\s*元|实付)[^（）]*）')


def clean_text(text):
    text = PRIVATE_LINK.sub(r'\1', text)
    text = MONEY_PAREN.sub('', text)
    parts = re.split(r'([，；。])', text)
    out = []
    for i in range(0, len(parts), 2):
        clause, sep = parts[i], parts[i + 1] if i + 1 < len(parts) else ''
        if MONEY.search(clause) or DROP.search(clause):
            continue
        if clause.strip() or (sep == '。' and out):
            out.append(clause + sep)
    s = ''.join(out).strip()
    s = re.sub(r'[，；]+$', '', s)
    s = re.sub(r'^[，；。]+', '', s)
    return s.replace('：。', '。').replace('：，', '：')


def cells(line):
    return [c.strip() for c in line.strip().strip('|').split('|')]


def build(src):
    lines = src.splitlines()
    date = next((m.group(1) for m in (re.search(r'更新：([\d-]+)', l) for l in lines[:5]) if m), '')
    out = ['# 采购清单', '',
           f'更新：{date}。这缸买了什么、接下来配什么，按用途分组，不含价格。'
           '规格和装法见[05方案](05-缸体与设备方案.md)，操作步骤见[03安装与开缸](03-安装与开缸.md)。', '',
           '<!-- 由 .维护/生成采购清单.py 从本地账本生成，不要手改 -->']
    keep = skip = False
    drop_cols = []
    for line in lines:
        if line.startswith('## '):
            title = line[3:].strip()
            keep, skip = title in KEEP, False
            if keep:
                out += ['', '## ' + KEEP[title]]
            continue
        if not keep:
            continue
        if line.startswith('### '):
            skip = line[4:].strip() in SKIP_SUB
            if not skip:
                out += ['', line]
            continue
        if skip:
            continue
        if line.startswith('|'):
            c = cells(line)
            if all(re.fullmatch(r':?-+:?', x) for x in c):
                out.append('|' + '|'.join(x for i, x in enumerate(c) if i not in drop_cols) + '|')
                continue
            if any(h in ('实付', '金额', '已记账金额') for h in c):
                drop_cols = [i for i, h in enumerate(c) if h in ('实付', '金额', '已记账金额')]
                out.append('| ' + ' | '.join(x for i, x in enumerate(c) if i not in drop_cols) + ' |')
                continue
            if not out[-1].startswith('|'):
                drop_cols = []          # 新表格且表头里没有金额列
            if any(RETURNED.search(x) for x in c):
                continue
            c = [clean_text(x) or '已买' for i, x in enumerate(c) if i not in drop_cols]
            out.append('| ' + ' | '.join(c) + ' |')
            continue
        if not line.strip():
            if out[-1] != '':
                out.append('')
            continue
        t = clean_text(line)
        if t:
            out.append(t)
    text = '\n'.join(out).rstrip() + '\n'
    return re.sub(r'\n{3,}', '\n\n', text)


def check(text, src):
    bad = re.findall(r'.{0,20}\d[\d,]*(?:\.\d+)?\s*元.{0,10}', text)
    amounts = {m.replace(',', '') for m in re.findall(r'\|\s*-?([\d,]+\.\d\d)\s*\|', src)}
    bad += [a for a in amounts if a in text.replace(',', '')]
    bad += re.findall(r'.{0,20}实付.{0,10}', text)
    return bad


def main():
    if not SRC.exists():
        print('没有本地账本，跳过生成采购清单')
        return 0
    src = SRC.read_text(encoding='utf-8')
    text = build(src)
    bad = check(text, src)
    if bad:
        print('采购清单里还有价格，没写入：', *bad[:10], sep='\n  ', file=sys.stderr)
        return 1
    if not DST.exists() or DST.read_text(encoding='utf-8') != text:
        DST.write_text(text, encoding='utf-8')
        print('已更新', DST.name)
    return 0


if __name__ == '__main__':
    sys.exit(main())
