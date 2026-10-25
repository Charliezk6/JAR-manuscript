# -*- coding: utf-8 -*-
"""Repair the previous append: drop everything from the round-13 section onward,
then re-append sheets 22 / 23 (Figure 1 block included this time)."""
import os, io, sys
from collections import OrderedDict
BASE = r'C:\Users\Administrator\WorkBuddy\2026-10-23-06-03-49'
os.chdir(BASE)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import openpyxl
from docx import Document
from docx.shared import Pt
from docx.oxml.ns import qn

PATH = os.path.join(BASE, 'JAR档案_数据包_文档部分_20261023.docx')
XLSX = os.path.join(BASE, 'JAR档案_数据包_定稿_20261023.xlsx')
log = []

doc = Document(PATH)
body = doc.element.body
anchor = None
for p in doc.paragraphs:
    if '本轮新增两个工作表' in p.text:
        anchor = p._p
        break
if anchor is None:
    raise SystemExit('anchor paragraph not found')
parent = anchor.getparent()
removed = 0
el = anchor
while el.getnext() is not None:
    nxt = el.getnext()
    if nxt.tag.endswith('}sectPr'):
        el = nxt
        continue
    parent.remove(nxt)
    removed += 1
parent.remove(anchor)
removed += 1
doc.save(PATH)
log.append('dropped %d tail elements (anchor included)' % removed)

# ------------------------------------------------------------ rebuild -------
wb = openpyxl.load_workbook(XLSX, read_only=True)
ws22, ws23 = wb['22_正文表格数值'], wb['23_图件作图数据']

tables = OrderedDict()
for row in ws22.iter_rows(min_row=5, values_only=True):
    if row[0] is None:
        continue
    tno, ctx, ri, rlab, ci, chd, vtxt, vnum = row[:8]
    d = tables.setdefault(tno, [ctx or '', OrderedDict()])
    if ctx and not d[0]:
        d[0] = ctx
    d[1].setdefault(ri, {})[ci] = vtxt


def wide(tno):
    ctx, rows = tables[tno]
    ncols = max((max(cs.keys()) + 1) for cs in rows.values())
    return ctx, [[cs.get(c, '') or '' for c in range(ncols)] for cs in
                 (rows[ri] for ri in sorted(rows))]


def add_table(doc, rows_data, size=8):
    ncols = max(len(r) for r in rows_data)
    tbl = doc.add_table(rows=len(rows_data), cols=ncols)
    try:
        tbl.style = 'Table Grid'
    except KeyError:
        pass
    for ri, row in enumerate(rows_data):
        for ci in range(ncols):
            val = row[ci] if ci < len(row) else ''
            cell = tbl.cell(ri, ci)
            cell.text = ''
            run = cell.paragraphs[0].add_run(str(val))
            if ri == 0:
                run.bold = True
            run.font.size = Pt(size)
    return tbl


def para(doc, text, size=9, bold=False):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.font.size = Pt(size)
    r.bold = bold
    return p


doc = Document(PATH)
para(doc, '本轮新增两个工作表：22_正文表格数值 与 23_图件作图数据。前者把手稿 24 张表的每一格'
          '以长表形式落到数据包，让数据编辑不必打开 Word 稿件即可检索任何一个正文数字；'
          '后者收录 Figure 1 / Figure 2 的作图坐标，并为 Figure 2 补上本来缺位的 cell-level '
          '标准误与 95% 区间（填补 DAN §8.17 自己声明的存档缺口）。')
para(doc, '22_正文表格数值（长表 %d 行；下列按键值重建为可读宽表）'
          % (ws22.max_row - 4), bold=True, size=11)
for tno in tables:
    ctx, rowsTx = wide(tno)
    para(doc, '%s — %s' % (tno, ctx[:150]), size=9, bold=True)
    add_table(doc, rowsTx)

para(doc, '23_图件作图数据（%d 行）' % ws23.max_row, bold=True, size=11)
para(doc, '说明：Figure 1 的残差化 cell means 与 cell counts 来自 DAN §8.17；'
          'cell-level 标准误仍未存档，故 Figure 1 的 whisker 无法由本包重算。'
          'Figure 2 的点位来自同一节的交互设定，SE 由脚本 _fig2_check.py 从 18_主面板 复算，'
          '95% 区间 = 点 ± 1.96 × SE。', size=9)

blocks, cur = OrderedDict(), None
for r in ws23.iter_rows(values_only=True):
    v = ['' if c is None else str(c) for c in r]
    head = v[0]
    if head.startswith('Figure 1 —'):
        cur = 'Figure 1'; blocks[cur] = []; continue
    if head.startswith('Figure 2 —'):
        cur = 'Figure 2 levels'; blocks[cur] = []; continue
    if head.startswith('Figure 2 的落差'):
        cur = 'Figure 2 falls'; blocks[cur] = []; continue
    if head.startswith('Pre-trend'):
        cur = 'Pre-trend'; blocks[cur] = []; continue
    if cur and head:
        blocks[cur].append(v)

log.append('figure blocks found: %s' % {k: len(v) for k, v in blocks.items()})
for key, head in [('Figure 1', 'Figure 1 — 残差化 cell means 与 cell counts'),
                  ('Figure 2 levels', 'Figure 2 — 隐含水平与复算 SE'),
                  ('Figure 2 falls', 'Figure 2 — 落差'),
                  ('Pre-trend', 'Pre-trend 检验')]:
    if blocks.get(key):
        para(doc, head, bold=True, size=9)
        add_table(doc, blocks[key])

doc.save(PATH)

# ------------------------------------------------------------ verify -------
d2 = Document(PATH)
txt = '\n'.join(p.text for p in d2.paragraphs)
alltbl = '\n'.join('\n'.join(' | '.join(c.text.strip() for c in r.cells) for r in t.rows)
                   for t in d2.tables)
log.append('VERIFY paragraphs            : %d' % len(d2.paragraphs))
log.append('VERIFY tables                : %d (target 34 = 8 + 22 + 4)' % len(d2.tables))
for name, needle in [
        ('22 heading', '22_正文表格数值'), ('23 heading', '23_图件作图数据'),
        ('scope 22/23', '19 / 20 / 21 / 22 / 23'),
        ('Table 6 fall', '+1.192'), ('Table 6A panel', '1,764'),
        ('Table 8 implied', '+0.653'), ('Table 9 E/S/G', '+1.201'),
        ('Table 10 row9', '0.514'), ('Table 12 primary', '+0.646'),
        ('Table A.8 ESS', '428'), ('Table 13 event', '-0.681'),
        ('Fig 1 joint cell', '-0.202'), ('Fig 1 balanced row', '0.147'),
        ('Fig 2 nb level', '0.8389'), ('Fig 2 CI high', '1.11918'),
        ('Fig 2 fall', '+1.198'), ('Pre-trend gap', '1.310')]:
    ok = needle in txt or needle in alltbl
    log.append('VERIFY %-18s %-14s : %s' % (name, needle, ok))
with open(os.path.join(BASE, '_pkgdoc22.txt'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(log))
print('\n'.join(log))
