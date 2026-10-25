# -*- coding: utf-8 -*-
"""Phase 3-5: firm-level symmetric balance test battery.
Part 1: raw firm-level balance table (joint 1,764 vs other 2,402 firms).
Part 2: persistence-constrained entropy balancing -> weighted Table 6 spec.
Part 3: joint-cell fall among persistent (bal11) vs non-persistent firms.
"""
import numpy as np, pandas as pd
from scipy.optimize import root

est = pd.read_pickle('_est31k.pkl')
CONTROLS = ['Size','ROA','Growth','Cash','lev','Age_c','Female','Edu','Pay_gap']
rng = np.random.default_rng(20261023)

# ---------- firm-level dataset ----------
g = est.groupby('Symbol')
firm = pd.DataFrame({
    'cell': g['cell'].first(),
    'nyears': g.size(),
    'span': g['Year'].max() - g['Year'].min() + 1,
    'bal11': g['bal11'].max(),
    'complete': g['CPATenure'].max().ge(5).astype(int),   # partner clock reaches 5 inside window
    'clock45_share': g.apply(lambda d: ((d.CPATenure.isin([4,5])).sum())/len(d), include_groups=False),
    'joint_share_clock5': g.apply(lambda d: d.loc[d.CPATenure==5,'joint5'].mean() if (d.CPATenure==5).any() else np.nan, include_groups=False),
})
for c in ['soe','Size','ROA','Growth','Cash','lev','Age_c','Female','Edu','Pay_gap','IsBig10','cap_exposed']:
    firm[c] = g[c].mean()
firm['mfg'] = (g['IndustryCode'].first().str.startswith('C')).astype(int)
print('firm-level dataset:', firm.shape)
print(firm.cell.value_counts())

TREATED = firm.index[firm.cell=='joint']
CONTROL = firm.index[firm.cell!='joint']
print('treated:', len(TREATED), 'controls:', len(CONTROL))
print('completion: treated %.3f control %.3f' % (firm.loc[TREATED,'complete'].mean(), firm.loc[CONTROL,'complete'].mean()))
print('nyears: treated %.2f control %.2f' % (firm.loc[TREATED,'nyears'].mean(), firm.loc[CONTROL,'nyears'].mean()))
print('bal11: treated %.3f control %.3f' % (firm.loc[TREATED,'bal11'].mean(), firm.loc[CONTROL,'bal11'].mean()))

# ---------- Part 1: raw balance table ----------
def std_diff(a, b):
    return (a.mean() - b.mean()) / np.sqrt((a.var(ddof=1) + b.var(ddof=1)) / 2)

BAL_VARS = ['soe','Size','ROA','Growth','Cash','lev','Age_c','Female','Edu','Pay_gap','IsBig10','mfg']
rows = []
for v in BAL_VARS + ['nyears','span','bal11','complete','clock45_share']:
    a, b = firm.loc[TREATED, v], firm.loc[CONTROL, v]
    sd = std_diff(a, b)
    # Welch t
    t = (a.mean()-b.mean())/np.sqrt(a.var(ddof=1)/len(a)+b.var(ddof=1)/len(b))
    rows.append({'var':v,'joint':a.mean(),'other':b.mean(),'std_diff':sd,'t':t})
bal = pd.DataFrame(rows)
pd.set_option('display.width', 200)
print('\n=== Part 1: firm-level raw balance (joint vs other) ===')
print(bal.to_string(index=False, float_format=lambda x: f'{x:+.4f}'))
print('max |std diff| ex-completion/clock45:', bal.loc[bal['var'].isin(BAL_VARS+['nyears','span','bal11']),'std_diff'].abs().max())

# ---------- entropy balancing (Hainmueller-Xu, dual solve) ----------
def ebalance(C, q, m_target):
    """C: (Nc, K) covariates (standardized), q: base weights (uniform), m_target: treated means.
    Returns weights summing to len(C)."""
    Nc, K = C.shape
    def moments(lam):
        z = C @ lam
        z = np.exp(z - z.max())
        w = q * z
        w = w / w.sum()
        return w @ C - m_target
    lam0 = np.zeros(K)
    sol = root(moments, lam0, method='hybr', options={'xtol':1e-12})
    z = C @ sol.x
    z = np.exp(z - z.max())
    w = q * z; w = w / w.sum()
    w *= Nc
    return w, sol

def run_ebalance(covars, label):
    sub = firm.loc[list(TREATED)+list(CONTROL)].copy()
    Xc = sub.loc[CONTROL, covars].values.astype(float)
    Xt = sub.loc[TREATED, covars].values.astype(float)
    # standardize by pooled SD for conditioning
    sd = np.sqrt((Xt.var(0, ddof=1) + Xc.var(0, ddof=1)) / 2)
    sd[sd==0] = 1
    Cs, Xts = Xc/sd, Xt/sd
    q = np.ones(len(CONTROL))/len(CONTROL)
    m_target = Xts.mean(0)
    w, sol = ebalance(Cs, q, m_target)
    wser = pd.Series(w, index=CONTROL)
    tmeans = sub.loc[TREATED, covars].mean()
    cmeans_w = (wser @ sub.loc[CONTROL, covars]) / wser.sum()
    # standardized differences after balancing, using the pre-balance pooled SD
    sdif_after = ((cmeans_w - tmeans) / sd).abs()
    maxsd = sdif_after.max()
    ess = wser.sum()**2 / (wser**2).sum()
    nz = int((wser < 1e-8).sum())
    print(f'\n--- ebalance set {label}: converged={sol.success}, max|std diff| after={maxsd:.2e}, '
          f'w range [{wser.min():.3f},{wser.max():.3f}], ESS={ess:.0f} of {len(CONTROL)}, zero-weight controls={nz}')
    return wser

# Set B1: replicate A.8 (nine covariates)
SET_B1 = ['soe','Size','ROA','Growth','Cash','lev','Age_c','IsBig10','mfg']
w_B1 = run_ebalance(SET_B1, 'B1 nine covariates (A.8 replication)')
# Set B2: + persistence (years observed, span)
SET_B2 = SET_B1 + ['nyears','span']
w_B2 = run_ebalance(SET_B2, 'B2 nine + years observed + span')
# Set B3: + completion flag (firm-level analogue of the clock-4/5-share constraint in 8.26)
SET_B3 = SET_B2 + ['complete']
w_B3 = run_ebalance(SET_B3, 'B3 nine + persistence + completion')

# ---------- weighted Table 6 spec ----------
est['T4'] = (est.CPATenure==4).astype(float)
est['T5'] = (est.CPATenure==5).astype(float)
cells_order = ['joint','below','above','none']

def build_X(d):
    parts, names = [], []
    for c in cells_order:
        parts.append((d.cell==c).astype(float).values * d['T4'].values); names.append(f'{c}*T4')
    for c in ['joint','below','above']:
        parts.append((d.cell==c).astype(float).values * d['T5'].values); names.append(f'{c}*T5')
    X = np.column_stack(parts + [d[c].values.astype(float) for c in CONTROLS])
    return X, names

def wls_twoway(d, weights=None):
    if weights is not None:
        wmap = d.Symbol.map(weights).values.astype(float)
        d = d[wmap > 1e-10].copy()
        w = wmap[wmap > 1e-10]
    else:
        w = np.ones(len(d))
    X, names = build_X(d)
    # drop design columns with no variation in the retained sample (e.g. none*T4 when all
    # non-completing firms are zero-weighted away)
    keepcol = X.sum(axis=0) != 0
    X, names = X[:, keepcol], [n for n, k in zip(names, keepcol) if k]
    firm_id, year_id = d.Symbol.values, d.Year.values
    fcodes = pd.factorize(firm_id)[0]; ycodes = pd.factorize(year_id)[0]
    nf, ny = fcodes.max()+1, ycodes.max()+1
    fw = np.bincount(fcodes, weights=w, minlength=nf); yw = np.bincount(ycodes, weights=w, minlength=ny)
    M = np.column_stack([d['E_H'].values.astype(float), X]).astype(float)
    ww = w[:,None]
    for it in range(300):
        old = M.copy()
        fs = np.zeros((nf, M.shape[1])); np.add.at(fs, fcodes, M*ww); fs /= fw[:,None]
        M = M - fs[fcodes]
        ys = np.zeros((ny, M.shape[1])); np.add.at(ys, ycodes, M*ww); ys /= yw[:,None]
        M = M - ys[ycodes]
        if np.max(np.abs(M-old)) < 1e-11: break
    yd = np.asarray(M[:,0]).ravel(); Xd = M[:,1:]
    sw = np.sqrt(w)
    Xw = Xd*sw[:,None]
    XtWX = Xw.T @ Xw
    beta = np.linalg.solve(XtWX, Xw.T @ (yd*sw))
    r = (yd*sw) - Xw @ beta
    meat = np.zeros((XtWX.shape[0],)*2)
    for g_ in np.unique(fcodes):
        msk = fcodes==g_
        Xg = Xw[msk]; ug = r[msk]
        s = Xg.T @ ug; meat += np.outer(s, s)
    G = len(np.unique(fcodes))
    bread = np.linalg.inv(XtWX)
    V = bread @ meat @ bread * (G/(G-1)) * ((len(d)-1)/(len(d)-X.shape[1]))
    return beta, V, names

def report(beta, V, names, tag):
    idx = {nm:i for i,nm in enumerate(names)}
    out = {}
    for c in ['joint','below','above']:
        b4, b5 = beta[idx[f'{c}*T4']], beta[idx[f'{c}*T5']]
        v = V[idx[f'{c}*T4'],idx[f'{c}*T4']] + V[idx[f'{c}*T5'],idx[f'{c}*T5']] - 2*V[idx[f'{c}*T4'],idx[f'{c}*T5']]
        fse = np.sqrt(max(v,0))
        out[f'{c}_fall'] = (b4-b5, fse)
    g = (beta[idx['joint*T4']]-beta[idx['joint*T5']]) - (beta[idx['below*T4']]-beta[idx['below*T5']])
    vg = (V[idx['joint*T4'],idx['joint*T4']] + V[idx['joint*T5'],idx['joint*T5']] - 2*V[idx['joint*T4'],idx['joint*T5']]
        + V[idx['below*T4'],idx['below*T4']] + V[idx['below*T5'],idx['below*T5']] - 2*V[idx['below*T4'],idx['below*T5']]
        + 2*(V[idx['joint*T4'],idx['below*T4']] - V[idx['joint*T4'],idx['below*T5']] - V[idx['joint*T5'],idx['below*T4']] + V[idx['joint*T5'],idx['below*T5']]))
    out['gap'] = (g, np.sqrt(max(vg,0)))
    print(f'[{tag}] joint fall {out["joint_fall"][0]:+.3f} (t {out["joint_fall"][0]/out["joint_fall"][1]:+.2f}) | '
          f'below {out["below_fall"][0]:+.3f} (t {out["below_fall"][0]/out["below_fall"][1]:+.2f}) | '
          f'gap {out["gap"][0]:+.3f} (t {out["gap"][0]/out["gap"][1]:+.2f})')
    return out

print('\n=== Part 2: weighted Table 6 spec ===')
b0, V0, n0 = wls_twoway(est)
r_unw = report(b0, V0, n0, 'unweighted (benchmark)')
for wset, tag in [(w_B1,'B1 nine-covariate balanced'), (w_B2,'B2 + persistence'), (w_B3,'B3 + completion')]:
    wall = pd.concat([pd.Series(1.0, index=TREATED), wset])
    b, V, n = wls_twoway(est, weights=wall)
    report(b, V, n, tag)

print('\n=== Part 3: joint-cell fall by persistence ===')
for flag, lab in [(1,'persistent (bal11)'), (0,'non-persistent')]:
    d = est[est.bal11==flag]
    b, V, n = wls_twoway(d)
    r = report(b, V, n, lab)
    jf = r['joint_fall']
    print(f'   N rows {len(d)}, firms {d.Symbol.nunique()}, joint-cell firms {d.loc[d.cell=="joint","Symbol"].nunique()}, MDE80={2.80*jf[1]:.2f}')

# cell composition among balanced firms
bb = est[est.bal11==1]
print('\nbalanced firms by cell:'); print(bb.groupby('cell').Symbol.nunique())
