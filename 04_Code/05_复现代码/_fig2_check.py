# -*- coding: utf-8 -*-
"""Recompute every number annotated on Figure 2 (pre-trend check by balanced
status) from the estimation sample, so the redrawn figure carries verified
values: implied E levels by clock year for non-balanced and balanced firms,
one firm-and-year FE regression with full controls, firm-clustered.
"""
import numpy as np, pandas as pd, json

est = pd.read_pickle('_est31k.pkl')
CONTROLS = [c for c in ['Size', 'ROA', 'Growth', 'Cash', 'lev', 'Age_c',
                        'Female', 'Edu', 'Pay_gap'] if est[c].std() > 0]
est['bal'] = est.bal11.astype(float)
est['nb'] = 1 - est['bal']

# year dummies relative to year one, interacted with group
parts, names = [], []
for yr in [2, 3, 4, 5]:
    d = (est.CPATenure == yr).astype(float).values
    parts.append(d * est['nb'].values); names.append(f'Y{yr}*nb')
    parts.append(d * est['bal'].values); names.append(f'Y{yr}*b')
X = np.column_stack(parts + [est[c].values.astype(float) for c in CONTROLS])
names = names + CONTROLS

fcodes = pd.factorize(est.Symbol.values)[0]
ycodes = pd.factorize(est.Year.values)[0]
nf, ny = fcodes.max() + 1, ycodes.max() + 1
w = np.ones(len(est))
M = np.column_stack([est['E_H'].values.astype(float), X]).astype(float)
ww = w[:, None]
for it in range(400):
    old = M.copy()
    fs = np.zeros((nf, M.shape[1])); np.add.at(fs, fcodes, M * ww); fs /= np.bincount(fcodes, minlength=nf)[:, None]
    M = M - fs[fcodes]
    ys = np.zeros((ny, M.shape[1])); np.add.at(ys, ycodes, M * ww); ys /= np.bincount(ycodes, minlength=ny)[:, None]
    M = M - ys[ycodes]
    if np.max(np.abs(M - old)) < 1e-11:
        break
yd = np.asarray(M[:, 0]).ravel(); Xd = M[:, 1:]
XtWX = Xd.T @ Xd
beta = np.linalg.solve(XtWX, Xd.T @ yd)
r = yd - Xd @ beta
meat = np.zeros((XtWX.shape[0],) * 2)
for g in np.unique(fcodes):
    msk = fcodes == g
    s = Xd[msk].T @ r[msk]
    meat += np.outer(s, s)
G = len(np.unique(fcodes))
V = np.linalg.inv(XtWX) @ meat @ np.linalg.inv(XtWX) * (G / (G - 1)) * ((len(est) - 1) / (len(est) - X.shape[1]))

i = {nm: k for k, nm in enumerate(names)}


def level(yr, grp):
    if yr == 1:
        return 0.0, 0.0
    k = i[f'Y{yr}*{grp}']
    return float(beta[k]), float(np.sqrt(V[k, k]))


def fall(yr_hi, yr_lo, grp):
    a, b = i[f'Y{yr_hi}*{grp}'], i[f'Y{yr_lo}*{grp}']
    v = V[a, a] + V[b, b] - 2 * V[a, b]
    e = float(beta[a] - beta[b]); se = float(np.sqrt(max(v, 0)))
    return e, se, e / se


series = {grp: [level(yr, grp) for yr in range(1, 6)] for grp in ('nb', 'b')}
print('implied levels (rel. year 1), [coef, se]:')
for grp in ('nb', 'b'):
    print(' ', grp, [(round(c, 3), round(s, 3)) for c, s in series[grp]])

e, se, t = fall(5, 4, 'nb')
print('Y4-Y5 non-balanced fall : %+.3f (SE %.3f, t %.2f)  [figure +1.198/1.197, t 10.19]' % (e, se, t))
e, se, t = fall(5, 4, 'b')
print('Y4-Y5 balanced fall     : %+.3f (SE %.3f, t %.2f)  [figure/table -0.112, t -0.88]' % (e, se, t))

# Y2-Y3 contrast per group and the between-group difference
c2n, c2n_se, c2n_t = fall(2, 3, 'nb')
c2b, c2b_se, c2b_t = fall(2, 3, 'b')
a1, b1 = i['Y2*nb'], i['Y3*nb']
a2, b2 = i['Y2*b'], i['Y3*b']
cv = np.zeros(len(names)); cv[a1] = 1; cv[b1] = -1; cv[a2] = -1; cv[b2] = 1
de = float(cv @ beta); dse = float(np.sqrt(max(cv @ V @ cv, 0)))
print('Y2-Y3 non-balanced      : %+.3f (t %.2f)   [DAN -0.040, t -0.41]' % (c2n, c2n_t))
print('Y2-Y3 balanced          : %+.3f (t %.2f)' % (c2b, c2b_t))
print('Y2-Y3 difference nb-b   : %+.3f (t %.2f)  [figure -0.056, t -0.37; MDE 0.42 -> 2.8*SE=%.2f]'
      % (de, dse / abs(dse) * (de / dse) if dse else 0, 2.8 * dse))

# Y3-Y4 divergence: between-group difference of (Y4 - Y3)
cv = np.zeros(len(names))
cv[i['Y4*nb']] = 1; cv[i['Y3*nb']] = -1; cv[i['Y4*b']] = -1; cv[i['Y3*b']] = 1
de = float(cv @ beta); dse = float(np.sqrt(max(cv @ V @ cv, 0)))
print('Y3-Y4 difference nb-b   : %+.3f (t %.2f)  [figure -0.567, t -3.51]' % (de, de / dse))

out = {'levels': {g: [[round(c, 4), round(s, 4)] for c, s in series[g]] for g in ('nb', 'b')},
       'fall_nb_45': [round(x, 4) for x in fall(5, 4, 'nb')],
       'fall_b_45': [round(x, 4) for x in fall(5, 4, 'b')]}
json.dump(out, open('_fig2_numbers.json', 'w'), indent=1)
print('saved _fig2_numbers.json')
