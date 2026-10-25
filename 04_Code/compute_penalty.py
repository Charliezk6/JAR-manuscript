# Resolve the broad-flag base-rate denominator (DAN 8.23 / A.4: "1,413 events, 7.17 percent")
# from the deposited main panel, on the primary-sample 2013-2020 window.
import openpyxl
from collections import Counter

wb = openpyxl.load_workbook(r"C:\Users\Administrator\.zcode\workspace\d5a1bb80-98c9-4938-b326-e00ffcce69ae\jar\data_package.xlsx", read_only=True, data_only=True)
ws = wb["18_主面板"]
rows = ws.iter_rows(values_only=True)
header = list(next(rows))
idx = {name: i for i, name in enumerate(header)}

def col(*names):
    for n in names:
        if n in idx:
            return n
    return None

pen_col = col("env_penalty")          # merged-panel broad flag (file 03 convention)
reg_col = col("pen_register")          # licensed register count (file 05)
print("env_penalty col:", pen_col, "| pen_register col:", reg_col)
print("all columns:", header)

data = []
for r in rows:
    data.append(r)

# primary sample: tenure 1-5 + singleton absorption (validated earlier)
cnt = Counter(r[idx["Symbol"]] for r in data if r[idx["CPATenure"]] is not None and 1 <= r[idx["CPATenure"]] <= 5)
primary = [r for r in data if r[idx["CPATenure"]] is not None and 1 <= r[idx["CPATenure"]] <= 5 and cnt[r[idx["Symbol"]]] > 1]

w = [r for r in primary if 2013 <= r[idx["Year"]] <= 2020]
print("\nprimary-sample firm-years 2013-2020:", len(w))

for c in (pen_col, reg_col):
    if c is None:
        continue
    events = sum(1 for r in w if (r[idx[c]] or 0) > 0)
    print(f"{c}: events {events}, base rate {events/len(w):.4f} on N={len(w)}")

# how many non-missing env_penalty rows in window (to see if base uses only populated rows)
if pen_col:
    nonmiss = sum(1 for r in w if r[idx[pen_col]] is not None)
    print("env_penalty non-missing rows in window:", nonmiss)
wb.close()
