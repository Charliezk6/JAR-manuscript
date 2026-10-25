import openpyxl
from collections import Counter, defaultdict

wb = openpyxl.load_workbook(r"data_package.xlsx", read_only=True, data_only=True)
ws = wb["18_主面板"]
rows = ws.iter_rows(values_only=True)
header = list(next(rows))
idx = {n: i for i, n in enumerate(header)}
data = [r for r in rows]
cnt = Counter(r[idx["Symbol"]] for r in data if r[idx["CPATenure"]] is not None and 1 <= r[idx["CPATenure"]] <= 5)
primary = [r for r in data if r[idx["CPATenure"]] is not None and 1 <= r[idx["CPATenure"]] <= 5 and cnt[r[idx["Symbol"]]] > 1]
w = [r for r in primary if 2013 <= r[idx["Year"]] <= 2020]

by = defaultdict(lambda: [0, 0])
for r in w:
    y = r[idx["Year"]]
    by[y][1] += 1
    if (r[idx["env_penalty"]] or 0) > 0:
        by[y][0] += 1
for y in sorted(by):
    e, n = by[y]
    print(y, "events", e, "N", n, "rate", round(100 * e / n, 2))

e1718 = by[2017][0] + by[2018][0]
print("2017+2018 events:", e1718, "share of broad events:", round(100 * e1718 / 1414, 1))
wb.close()
