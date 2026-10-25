# -*- coding: utf-8 -*-
"""Phase 2: reproduce Table 6 benchmark (firm+year FE, controls, cell x T4/T5 interactions)."""
import numpy as np, pandas as pd

est = pd.read_pickle('_est31k.pkl')
CONTROLS = ['Size','ROA','Growth','Cash','lev','Age_c','Female','Edu','Pay_gap']  # soe time-invariant -> absorbed by firm FE

# design matrix pieces
est['T4'] = (est.CPATenure==4).astype(float)
est['T5'] = (est.CPATenure==5).astype(float)
cells_order = ['joint','below','above','none']
X_parts, names = [], []
for c in cells_order:
    X_parts.append((est.cell==c).astype(float).values * est['T4'].values)
    names.append(f'{c}*T4')
for c in ['joint','below','above']:   # none has no T5 rows
    X_parts.append((est.cell==c).astype(float).values * est['T5'].values)
    names.append(f'{c}*T5')
X = np.column_stack(X_parts + [est[c].values.astype(float) for c in CONTROLS])
y = est['E_H'].values.astype(float)
names = names + CONTROLS
firm = est.Symbol.values; year = est.Year.values
n = len(y)

# two-way within transformation via alternating projections
def twoway_demean(M, firm, year, iters=200, tol=1e-12):
    M = M.astype(float).copy()
    fcodes = pd.factorize(firm)[0]; ycodes = pd.factorize(year)[0]
    nf = fcodes.max()+1; ny = ycodes.max()+1
    fcount = np.bincount(fcodes, minlength=nf); ycount = np.bincount(ycodes, minlength=ny)
    for it in range(iters):
        old = M.copy()
        # demean by firm
        fs = np.zeros((nf, M.shape[1])); np.add.at(fs, fcodes, M); fs /= fcount[:,None]
        M -= fs[fcodes]
        # demean by year
        ys = np.zeros((ny, M.shape[1])); np.add.at(ys, ycodes, M); ys /= ycount[:,None]
        M -= ys[ycodes]
        if np.max(np.abs(M-old)) < tol: break
    return M, it

Xd, it = twoway_demean(X, firm, year)
yd, _ = twoway_demean(y.reshape(-1,1), firm, year, iters=200, tol=1e-12)
yd = yd.ravel()
print('demean iterations:', it)

# OLS on demeaned data, cluster by firm
XtX = Xd.T @ Xd
beta = np.linalg.solve(XtX, Xd.T @ yd)
resid = yd - Xd @ beta
# meat: sum over clusters of (X_g' e)(X_g' e)'
meat = np.zeros((XtX.shape[0], XtX.shape[0]))
fcodes = pd.factorize(firm)[0]
for g in np.unique(fcodes):
    m = fcodes==g
    Xg = Xd[m]; ug = resid[m]
    s = Xg.T @ ug
    meat += np.outer(s, s)
G = len(np.unique(fcodes))
bread = np.linalg.inv(XtX)
V = bread @ meat @ bread
# small-sample correction
dfc = (G/(G-1)) * ((n-1)/(n-X.shape[1]))
V *= dfc
se = np.sqrt(np.diag(V))
res = pd.DataFrame({'term':names,'coef':beta,'se':se,'t':beta/se}, index=names)
print(res.loc[[f'{c}*T4' for c in cells_order]+[f'{c}*T5' for c in ['joint','below','above']]])

# fall = beta(T4*cell) - beta(T5*cell); level = beta(T5*cell) vs base T1-T3
print('\nTable 6 targets: level joint -0.547 (t -4.08), fall +1.192 (t 8.85); below -0.120/+0.104; above +0.221/+0.191')
idx = {nm:i for i,nm in enumerate(names)}
for c in ['joint','below','above']:
    b4, b5 = beta[idx[f'{c}*T4']], beta[idx[f'{c}*T5']]
    v = V[idx[f'{c}*T4'],idx[f'{c}*T4']] + V[idx[f'{c}*T5'],idx[f'{c}*T5']] - 2*V[idx[f'{c}*T4'],idx[f'{c}*T5']]
    fall_se = np.sqrt(max(v,0))
    print(f'{c:6s} level {b5:+.3f} (t {b5/se[idx[f"{c}*T5"]]:+.2f}) | fall {b4-b5:+.3f} (se {fall_se:.3f}, t {(b4-b5)/fall_se:+.2f})')
# gap: joint fall - below fall
g = (beta[idx['joint*T4']]-beta[idx['joint*T5']]) - (beta[idx['below*T4']]-beta[idx['below*T5']])
vg = V[idx['joint*T4'],idx['joint*T4']] + V[idx['joint*T5'],idx['joint*T5']] - 2*V[idx['joint*T4'],idx['joint*T5']] \
   + V[idx['below*T4'],idx['below*T4']] + V[idx['below*T5'],idx['below*T5']] - 2*V[idx['below*T4'],idx['below*T5']] \
   + 2*(V[idx['joint*T4'],idx['below*T4']] - V[idx['joint*T4'],idx['below*T5']] - V[idx['joint*T5'],idx['below*T4']] + V[idx['joint*T5'],idx['below*T5']])
print(f'joint-minus-below gap: {g:+.3f} (t {g/np.sqrt(vg):+.2f})  [target +1.088]')
