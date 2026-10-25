# Compute the joint x balanced 2x2 on the primary sample, replicating Table 2's funnel
# from the deposited main panel (18_主面板), for DAN Section 8.17 reconciliation.
import openpyxl

wb = openpyxl.load_workbook(r"C:\Users\Administrator\.zcode\workspace\d5a1bb80-98c9-4938-b326-e00ffcce69ae\jar\data_package.xlsx", read_only=True, data_only=True)
ws = wb["18_主面板"]

rows = ws.iter_rows(values_only=True)
header = list(next(rows))
idx = {name: i for i, name in enumerate(header)}
need = ["Symbol", "CPATenure", "AuditorTenure", "bal11", "joint5"]
for n in need:
    if n not in idx:
        raise SystemExit(f"missing column {n}; header={header}")

clock_rows = []  # (symbol, cpa, aud, bal11, joint5)
n_all = 0
for r in rows:
    n_all += 1
    clock_rows.append((r[idx["Symbol"]], r[idx["CPATenure"]], r[idx["AuditorTenure"]], r[idx["bal11"]], r[idx["joint5"]]))

print("total rows in 18_主面板:", n_all)

# Step 1: restrict to partner-clock tenures 1-5
t15 = [r for r in clock_rows if r[1] is not None and 1 <= r[1] <= 5]
print("after tenure 1-5:", len(t15))

# Step 2: singleton absorption (firms with a single retained firm-year)
from collections import Counter, defaultdict
cnt = Counter(r[0] for r in t15)
primary = [r for r in t15 if cnt[r[0]] > 1]
firms = len(set(r[0] for r in primary))
print("after singleton absorption:", len(primary), "firms:", firms)

joint_total = sum(1 for r in primary if r[4] == 1)
print("joint firm-years (joint5==1):", joint_total)

# Step 3: 2x2 on clock-five rows (CPATenure==5): bal11 x joint5
five = [r for r in primary if r[1] == 5]
cell = Counter((r[3], r[4]) for r in five)
bal_total = sum(1 for r in five if r[3] == 1)
nbal_total = sum(1 for r in five if r[3] != 1)
bal_joint = cell.get((1, 1), 0)
nbal_joint = cell.get((0, 1), 0)
print("\n2x2 on partner-clock-five rows of the primary sample:")
print(f"  balanced  : clock-five rows {bal_total}, joint {bal_joint}, share {bal_joint/bal_total:.3f}")
print(f"  non-bal   : clock-five rows {nbal_total}, joint {nbal_joint}, share {nbal_joint/nbal_total:.3f}")
print(f"  total     : clock-five rows {bal_total+nbal_total}, joint {bal_joint+nbal_joint}")

# Cross-check: joint firm-years split by balanced status over ALL primary rows (not just year five)
jall = Counter(r[3] for r in primary if r[4] == 1)
print("\nall joint firm-years by balanced status:", dict(jall))

# Also verify joint5 definition consistency: CPATenure==5 & AuditorTenure==5
mismatch = sum(1 for r in primary if r[4] != (1 if (r[1] == 5 and r[2] == 5) else 0))
print("joint5 vs (CPATenure==5 & AuditorTenure==5) mismatches:", mismatch)
wb.close()
