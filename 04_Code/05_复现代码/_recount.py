# -*- coding: utf-8 -*-
"""pandas counterpart of _recount.do.

Settles the 52.7 percent question and builds the firm-year counterpart of
Table 6A. Edit the three column names and the input path, then run.
"""
import pandas as pd

PCLOCK, FCLOCK, BAL = "pclock", "fclock", "bal"   # <-- edit

df = pd.read_csv("18_main_panel.csv")             # <-- edit path
d = df[df["tenure"].between(1, 5)].copy()

# ---- (a) full-sample joint share -------------------------------------------
# Decision rule: if n5 lands in 4,880-4,900 the full-sample share is ~41
# percent and the manuscript's 52.7 percent is a scope error.
n5 = int((d[PCLOCK] == 5).sum())
j5 = int(((d[PCLOCK] == 5) & (d[FCLOCK] == 5)).sum())
print("(a) clock-five firm-years       = %-6d (expect 4,880-4,900)" % n5)
print("    joint clock-five firm-years = %-6d (expect 2,018)" % j5)
print("    full-sample joint share     = %.1f%%  (expect ~41)" % (100 * j5 / n5))

# ---- (b) by panel persistence: expect 53.4 and 21.9 ------------------------
print("\n(b) by panel persistence")
for g in (0, 1):
    s = d[d[BAL] == g]
    dn = int((s[PCLOCK] == 5).sum())
    dj = int(((s[PCLOCK] == 5) & (s[FCLOCK] == 5)).sum())
    print("    bal=%d  clock-five rows = %-5d  joint share = %.1f%%" % (g, dn, 100 * dj / dn))

# ---- (c) firm-year cross-tabulation ----------------------------------------
print("\n(c) firm-year crosstab, tenures 1-5")
print(pd.crosstab(d[PCLOCK], d[FCLOCK].clip(upper=6), margins=True))

# ---- (d) firm-level, first clock-five year ---------------------------------
# Resolves the combined "2 and 3" row of Table 6A Panel A (234 firms).
f = (d[d[PCLOCK] == 5].sort_values(["firm", "year"]).groupby("firm").first())
print("\n(d) firm-level audit-firm clock at the first partner-clock-five year")
print(f[FCLOCK].value_counts().sort_index().to_string())
print("    total firms with a clock-five year =", len(f))
# expect: 1 -> 101 ; 2+3 -> 234 ; 4 -> 128 ; 5 -> 1,764
#         6 -> 173 ; 7 -> 157 ; 8-19 -> 666 ; grand total 4,166


# ---- pairsym zero-padding (data-package item) ------------------------------
def pad_pairsym(s):
    """'name1,name2||6' -> 'name1,name2||000006'"""
    if not isinstance(s, str) or "||" not in s:
        return s
    left, right = s.split("||", 1)
    right = right.zfill(6) if right.strip().isdigit() else right
    return left + "||" + right


if "pairsym" in df.columns:
    df["pairsym"] = df["pairsym"].map(pad_pairsym)
    # df.to_csv("18_main_panel_padded.csv", index=False)
    print("\npairsym zero-padded (write out with the commented line above)")
