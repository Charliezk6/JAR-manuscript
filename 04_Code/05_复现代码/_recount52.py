# -*- coding: utf-8 -*-
"""
JAR manuscript - settle the 52.7 percent question in ONE run.

The manuscript's Section 1 originally claimed that the audit-firm clock
"reaches five in the same year the partner clock does in 52.7 percent of
clock-five firm-years".  That number cannot be reproduced from any pair of
counts deposited anywhere in the manuscript, the data package or the data
availability note.  This script computes every plausible reading of
"joint share" from the micro data and reports which (if any) reproduces
52.7 percent, so the question can be closed instead of argued.

USAGE
  1. Edit CONFIG below (path + column names).
  2. python _recount52.py
  3. Read the ADJUDICATION block at the end.

It also re-checks every deposited constant that bears on the question and
prints PASS/FAIL, so a stale sample shows up immediately.
"""

import os
import sys

# ------------------------------- CONFIG -----------------------------------
PATH   = r"18_主面板.dta"      # primary panel (file 18 of the package)
FIRM   = "stkcd"      # firm id
YEAR   = "year"
PCLOCK = "CPATenure"  # partner clock  (longer-serving signing partner)
FCLOCK = "AuditorTenure"  # audit-firm clock
BAL    = "balanced"   # 1 if the firm is observed in all eleven years
INSAMP = "insample"   # 1 if the row is in the 31,274-row estimation sample
FIRMCHG= "firm_change"  # 1 in an audit-firm-change year  (optional)
# Set to None if a column does not exist; the block is then skipped.
# --------------------------------------------------------------------------

TARGET = 52.7
TOL    = 0.15


def load():
    if PATH.lower().endswith((".dta", ".dta.gz")):
        import pandas as pd
        return pd.read_stata(PATH)
    if PATH.lower().endswith((".csv", ".csv.gz", ".txt")):
        import pandas as pd
        return pd.read_csv(PATH)
    raise SystemExit("unsupported file type: %s" % PATH)


def main():
    try:
        import pandas as pd
    except ImportError:
        raise SystemExit("pandas is required")

    df = load()
    cols = set(df.columns)
    for c in (FIRM, YEAR, PCLOCK, FCLOCK):
        if c not in cols:
            raise SystemExit("column not found: %s (have: %s)"
                             % (c, sorted(cols)[:20]))

    if INSAMP in cols:
        d = df[df[INSAMP] == 1].copy()
        samp_note = "restricted to %s == 1" % INSAMP
    else:
        d = df.copy()
        samp_note = "NO insample column found - using all rows, " \
                    "CHECK THAT THIS IS THE 31,274-ROW SAMPLE"

    d["joint"] = ((d[PCLOCK] == 5) & (d[FCLOCK] == 5)).astype(int)

    out = []
    out.append("=" * 74)
    out.append("52.7 PERCENT ADJUDICATION")
    out.append("=" * 74)
    out.append("sample: %d rows, %d firms   (%s)"
               % (len(d), d[FIRM].nunique(), samp_note))
    out.append("")

    # ------------------------------------------------------------------
    # 0. Do the deposited constants still hold?  If any of these FAIL the
    #    sample has moved and every share below is on a new footing.
    # ------------------------------------------------------------------
    out.append("--- (0) deposited constants ---------------------------------")
    checks = []

    def chk(label, got, want, tol=0):
        ok = (got == want) if tol == 0 else abs(got - want) <= tol
        checks.append(ok)
        out.append("  [%s] %-42s got %-10s want %s"
                   % ("PASS" if ok else "FAIL", label, got, want))

    chk("rows in estimation sample", len(d), 31274)
    chk("firms in estimation sample", d[FIRM].nunique(), 4166)
    chk("joint firm-years (DAN 6 / 8.16)", int(d["joint"].sum()), 2018)

    n5 = int((d[PCLOCK] == 5).sum())
    out.append("  [info] partner-clock-five firm-years   = %d" % n5)
    out.append("         (derivation in the memo predicts 4,880-4,900)")

    if BAL in cols:
        b = d[d[BAL] == 1]
        nb = d[d[BAL] == 0]
        chk("balanced clock-five rows", int((b[PCLOCK] == 5).sum()), 1887)
        chk("balanced joint clock-five rows",
            int(((b[PCLOCK] == 5) & (b[FCLOCK] == 5)).sum()), 413)
        chk("balanced rows (total)", len(b), 13122)
        chk("non-balanced rows (total)", len(nb), 18152)
    else:
        out.append("  [skip] no '%s' column - persistence split unavailable" % BAL)
    out.append("")

    # ------------------------------------------------------------------
    # 1. Candidate readings of "joint share".
    # ------------------------------------------------------------------
    cands = []

    def add(label, num, den, expect=None):
        if den:
            cands.append((label, num, den, 100.0 * num / den, expect))

    j = int(d["joint"].sum())
    add("all firm-years", j, len(d), None)
    add("clock-five firm-years  <-- manuscript's wording", j, n5, "~41 (derived)")

    # first clock-five year, firm level (the Table 6 / 6A construction)
    f5 = d[d[PCLOCK] == 5].sort_values([FIRM, YEAR]).groupby(FIRM, as_index=False).first()
    add("firms, joint at FIRST clock-five year", int((f5[FCLOCK] == 5).sum()), len(f5), 42.3)
    add("firms ever reaching clock five", int((f5[FCLOCK] == 5).sum()), len(f5), None)

    if BAL in cols:
        for g, lab in ((0, "non-balanced firms"), (1, "balanced firms")):
            s = d[d[BAL] == g]
            add("clock-five firm-years, %s" % lab,
                int(s["joint"].sum()), int((s[PCLOCK] == 5).sum()),
                53.4 if g == 0 else 21.9)

    # window / repeal splits - the most likely source of a stale denominator
    if YEAR in cols:
        for lo, hi, lab in ((2013, 2021, "pre-repeal 2013-2021"),
                            (2022, 2023, "post-repeal 2022-2023"),
                            (2013, 2019, "2013-2019"),
                            (2020, 2021, "2020-2021")):
            s = d[(d[YEAR] >= lo) & (d[YEAR] <= hi)]
            add("clock-five firm-years, %s" % lab,
                int(s["joint"].sum()), int((s[PCLOCK] == 5).sum()), None)

    if FIRMCHG in cols:
        s = d[d[FIRMCHG] == 0]
        add("clock-five firm-years, excluding firm-change years",
            int(s["joint"].sum()), int((s[PCLOCK] == 5).sum()), None)

    # clock sample (all tenure rows, not only 1-5) if the column exists
    if INSAMP in cols:
        a = df.copy()
        a["joint"] = ((a[PCLOCK] == 5) & (a[FCLOCK] == 5)).astype(int)
        add("clock-five rows, FULL panel (no insample filter)",
            int(a["joint"].sum()), int((a[PCLOCK] == 5).sum()), None)

    out.append("--- (1) candidate readings -----------------------------------")
    out.append("  %-52s %8s %8s %9s" % ("definition", "num", "den", "share%"))
    out.append("  " + "-" * 70)
    hits = []
    for label, num, den, share, expect in cands:
        flag = ""
        if abs(share - TARGET) <= TOL:
            flag = "   <<< MATCHES 52.7"
            hits.append((label, num, den, share))
        exp = "" if expect is None else "  (expect %s)" % expect
        out.append("  %-52s %8d %8d %8.2f%%%s%s"
                   % (label[:52], num, den, share, exp, flag))
    out.append("")

    # ------------------------------------------------------------------
    # 2. Adjudication
    # ------------------------------------------------------------------
    out.append("--- (2) ADJUDICATION -----------------------------------------")
    if hits:
        out.append("  52.7 percent REPRODUCED by:")
        for label, num, den, share in hits:
            out.append("    %s  =  %d / %d  =  %.2f%%" % (label, num, den, share))
        out.append("  -> the manuscript's sentence was using that denominator.")
        out.append("     Keep it only if that denominator is the one you want")
        out.append("     a reader to verify; otherwise restate with the counts.")
    else:
        out.append("  No reading reproduces 52.7 percent (within +/-%.2f pp)." % TOL)
        out.append("  -> 52.7 is stale: it belongs to a sample vintage that is")
        out.append("     not the deposited one.  Do not reinstate it.")
        out.append("  -> The current Section 1 text uses 1,764/4,166 (firm level)")
        out.append("     and 53.4 / 21.9 (by persistence), none of which depend on")
        out.append("     the unknown total count of clock-five firm-years, so it")
        out.append("     stands whatever this script returns.")
    out.append("")
    if not all(checks):
        out.append("  WARNING: at least one deposited constant FAILED above.")
        out.append("  The sample has moved; re-derive before trusting any share.")
    out.append("=" * 74)

    txt = "\n".join(out)
    print(txt)
    with open("_recount52_out.txt", "w", encoding="utf-8") as fh:
        fh.write(txt)


if __name__ == "__main__":
    main()
