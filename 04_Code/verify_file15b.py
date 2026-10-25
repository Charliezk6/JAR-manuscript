# End-to-end verification of the broad-flag penalty result (file 15) from _est31k.pkl.
import pickle
import numpy as np
import pandas as pd

WB = r"C:\Users\Administrator\WorkBuddy\2026-10-23-06-03-49"
with open(f"{WB}\\_est31k.pkl", "rb") as f:
    df = pickle.load(f)

CONTROLS = ["Size", "ROA", "Growth", "Cash", "lev", "soe", "Age_c", "Female", "Edu", "Pay_gap"]

def twoway_demean(frame, cols, g="Symbol", t="Year", iters=60):
    X = frame[cols].astype(float).copy()
    for _ in range(iters):
        X = X - X.groupby(frame[g]).transform("mean")
        X = X - X.groupby(frame[t]).transform("mean")
    return X

def run_fall(frame, outcome, label, expect=""):
    d = frame[["Symbol", "Year", outcome, "CPATenure"] + CONTROLS].dropna().copy()
    d = d[d["CPATenure"].between(1, 5)]
    for k in (2, 3, 4, 5):
        d[f"Y{k}"] = (d["CPATenure"] == k).astype(float)
    cols = [outcome] + [f"Y{k}" for k in (2, 3, 4, 5)] + CONTROLS
    dm = twoway_demean(d, cols)
    y = dm[outcome].to_numpy()
    keep, names = [], []
    for c in [f"Y{k}" for k in (2, 3, 4, 5)] + CONTROLS:
        v = dm[c].to_numpy()
        if np.std(v) > 1e-8:
            keep.append(v)
            names.append(c)
    X = np.column_stack(keep)
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    n, k = X.shape
    XtX_inv = np.linalg.pinv(X.T @ X)
    groups = pd.Series(d["Symbol"].to_numpy())
    idx = groups.groupby(groups).indices
    meat = np.zeros((k, k))
    for g_i in idx.values():
        s = X[g_i].T @ resid[g_i]
        meat += np.outer(s, s)
    G = len(idx)
    c = (G / (G - 1)) * ((n - 1) / (n - k))
    V = XtX_inv @ (c * meat) @ XtX_inv
    b = dict(zip(names, beta))
    fall = b["Y4"] - b["Y5"]
    v44, v55, v45 = V[names.index("Y4"), names.index("Y4")], V[names.index("Y5"), names.index("Y5")], V[names.index("Y4"), names.index("Y5")]
    t = fall / np.sqrt(v44 + v55 - 2 * v45)
    print(f"{label}: N={n}, firms={G}, dropped-cols={set([f'Y{k}' for k in (2,3,4,5)]+CONTROLS)-set(names)}, fall={fall:.3f}, t={t:.2f}   [{expect}]")

print("== calibration: Table 4 E_H fall")
run_fall(df, "E_H", "E_H", "expect 0.646, t 7.44")

w = df[(df["Year"] >= 2013) & (df["Year"] <= 2020)]
print(f"\n== broad flag, 2013-2020 window: rows={len(w)}, events={int((w['env_penalty']>0).sum())}, "
      f"rate={100*(w['env_penalty']>0).mean():.2f}%  [expect 1,414 / 7.04]")
print(f"== register same window: events={int((w['pen_register']>0).sum())}, rate={100*(w['pen_register']>0).mean():.2f}%  [expect 204 / 1.02]")

print("\n== broad-flag fall")
run_fall(w, "env_penalty", "broad*100", "expect +1.458 pp, t +2.68")

print("\n== year-by-year broad base rates")
print((w.assign(flag=(w["env_penalty"] > 0).astype(int)).groupby("Year")["flag"].agg(["sum", "size", "mean"]).round(3)))
