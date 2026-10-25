# -*- coding: utf-8 -*-
"""Final consolidated firm-level balance battery -> JSON + markdown artifact."""
import numpy as np, pandas as pd, json
from scipy.optimize import root

est = pd.read_pickle('_est31k.pkl')
CONTROLS = ['Size','ROA','Growth','Cash','lev','Age_c','Female','Edu','Pay_gap']
R = {}

# ---------- firm-level dataset ----------
g = est.groupby('Symbol')
firm = pd.DataFrame({
    'cell': g['cell'].first(),
    'nyears': g.size(),
    'span': g['Year'].max() - g['Year'].min() + 1,
    'bal11': g['bal11'].max(),
    'complete': g['CPATenure'].max().ge(5).astype(int),
    'clock45_share': g.apply(lambda d: ((d.CPATenure.isin([4,5])).sum())/len(d), include_groups=False),
})
for c in ['soe','Size','ROA','Growth','Cash','lev','Age_c','Female','Edu','Pay_gap','IsBig10','cap_exposed']:
    firm[c] = g[c].mean()
firm['mfg'] = (g['IndustryCode'].first().str.startswith('C')).astype(int)
TREATED = firm.index[firm.cell=='joint']; CONTROL = firm.index[firm.cell!='joint']

def std_diff(a, b):
    return (a.mean() - b.mean()) / np.sqrt((a.var(ddof=1) + b.var(ddof=1)) / 2)

# ---------- Part 1 ----------
bal_rows = []
for v in ['soe','Size','ROA','Growth','Cash','lev','Age_c','Female','Edu','Pay_gap','IsBig10','mfg',
          'nyears','span','bal11','complete','clock45_share']:
    a, b = firm.loc[TREATED, v], firm.loc[CONTROL, v]
    t = (a.mean()-b.mean())/np.sqrt(a.var(ddof=1)/len(a)+b.var(ddof=1)/len(b))
    bal_rows.append({'var': v, 'joint': round(a.mean(),4), 'other': round(b.mean(),4),
                     'std_diff': round(std_diff(a,b),3), 't': round(t,2)})
R['balance_table'] = bal_rows
R['balance_max_std_ex_persistence'] = round(max(abs(r['std_diff']) for r in bal_rows
                                        if r['var'] in ['soe','Size','ROA','Growth','Cash','lev','Age_c','Female','Edu','Pay_gap','IsBig10','mfg']),3)

# ---------- entropy balancing ----------
def ebalance(C, q, m_target):
    Nc, K = C.shape
    def moments(lam):
        z = C @ lam; z = np.exp(z - z.max()); w = q*z; w = w/w.sum()
        return w @ C - m_target
    sol = root(moments, np.zeros(K), method='hybr', options={'xtol':1e-12})
    z = C @ sol.x; z = np.exp(z - z.max()); w = q*z; w = w/w.sum(); w *= Nc
    return w, sol

def run_ebalance(covars):
    sub = firm.loc[list(TREATED)+list(CONTROL)]
    Xc = sub.loc[CONTROL, covars].values.astype(float); Xt = sub.loc[TREATED, covars].values.astype(float)
    sd = np.sqrt((Xt.var(0, ddof=1) + Xc.var(0, ddof=1)) / 2); sd[sd==0] = 1
    q = np.ones(len(CONTROL))/len(CONTROL)
    w, sol = ebalance(Xc/sd, q, (Xt/sd).mean(0))
    wser = pd.Series(w, index=CONTROL)
    tmeans = sub.loc[TREATED, covars].mean(); cmeans_w = (wser @ sub.loc[CONTROL, covars]) / wser.sum()
    maxsd = float((((cmeans_w - tmeans)/sd).abs()).max())
    ess = float(wser.sum()**2 / (wser**2).sum())
    return wser, {'converged': bool(sol.success), 'max_std_after': maxsd,
                  'w_min': round(float(wser.min()),3), 'w_max': round(float(wser.max()),3),
                  'ess': round(ess), 'n_control': len(CONTROL),
                  'zero_weight': int((wser < 1e-8).sum())}

SET_B1 = ['soe','Size','ROA','Growth','Cash','lev','Age_c','IsBig10','mfg']
SET_B2 = SET_B1 + ['nyears','span']
SET_B3 = SET_B2 + ['complete']
w_B1, d_B1 = run_ebalance(SET_B1)
w_B2, d_B2 = run_ebalance(SET_B2)
w_B3, d_B3 = run_ebalance(SET_B3)
R['ebalance'] = {'B1': d_B1, 'B2': d_B2, 'B3': d_B3}

# ---------- Table 6 spec machinery ----------
est['T4'] = (est.CPATenure==4).astype(float); est['T5'] = (est.CPATenure==5).astype(float)
cells_order = ['joint','below','above','none']

def build_X(d):
    parts, names = [], []
    for c in cells_order:
        parts.append((d.cell==c).astype(float).values * d['T4'].values); names.append(f'{c}*T4')
    for c in ['joint','below','above']:
        parts.append((d.cell==c).astype(float).values * d['T5'].values); names.append(f'{c}*T5')
    return np.column_stack(parts + [d[c].values.astype(float) for c in CONTROLS]), names

def wls_twoway(d, weights=None):
    if weights is not None:
        wmap = d.Symbol.map(weights).values.astype(float)
        keep = wmap > 1e-10; d = d[keep].copy(); w = wmap[keep]
    else:
        w = np.ones(len(d))
    X, names = build_X(d)
    keepcol = X.sum(axis=0) != 0
    X, names = X[:, keepcol], [n for n, k in zip(names, keepcol) if k]
    fcodes = pd.factorize(d.Symbol.values)[0]; ycodes = pd.factorize(d.Year.values)[0]
    nf, ny = fcodes.max()+1, ycodes.max()+1
    fw = np.bincount(fcodes, weights=w, minlength=nf); yw = np.bincount(ycodes, weights=w, minlength=ny)
    M = np.column_stack([d['E_H'].values.astype(float), X]).astype(float); ww = w[:,None]
    for it in range(300):
        old = M.copy()
        fs = np.zeros((nf, M.shape[1])); np.add.at(fs, fcodes, M*ww); fs /= fw[:,None]; M = M - fs[fcodes]
        ys = np.zeros((ny, M.shape[1])); np.add.at(ys, ycodes, M*ww); ys /= yw[:,None]; M = M - ys[ycodes]
        if np.max(np.abs(M-old)) < 1e-11: break
    yd = np.asarray(M[:,0]).ravel(); Xd = M[:,1:]; sw = np.sqrt(w); Xw = Xd*sw[:,None]
    XtWX = Xw.T @ Xw
    beta = np.linalg.solve(XtWX, Xw.T @ (yd*sw))
    r = (yd*sw) - Xw @ beta
    meat = np.zeros((XtWX.shape[0],)*2)
    for g_ in np.unique(fcodes):
        msk = fcodes==g_; s = Xw[msk].T @ r[msk]; meat += np.outer(s, s)
    G = len(np.unique(fcodes)); bread = np.linalg.inv(XtWX)
    V = bread @ meat @ bread * (G/(G-1)) * ((len(d)-1)/(len(d)-X.shape[1]))
    return beta, V, names, len(d), d.Symbol.nunique()

def contrast(beta, V, names):
    idx = {nm:i for i,nm in enumerate(names)}
    out = {}
    for c in ['joint','below','above']:
        b4, b5 = beta[idx[f'{c}*T4']], beta[idx[f'{c}*T5']]
        v = V[idx[f'{c}*T4'],idx[f'{c}*T4']] + V[idx[f'{c}*T5'],idx[f'{c}*T5']] - 2*V[idx[f'{c}*T4'],idx[f'{c}*T5']]
        fse = float(np.sqrt(max(v,0))); out[f'{c}_fall'] = (round(float(b4-b5),3), round(fse,3), round(float((b4-b5)/fse),2))
    g = (beta[idx['joint*T4']]-beta[idx['joint*T5']]) - (beta[idx['below*T4']]-beta[idx['below*T5']])
    vg = (V[idx['joint*T4'],idx['joint*T4']] + V[idx['joint*T5'],idx['joint*T5']] - 2*V[idx['joint*T4'],idx['joint*T5']]
        + V[idx['below*T4'],idx['below*T4']] + V[idx['below*T5'],idx['below*T5']] - 2*V[idx['below*T4'],idx['below*T5']]
        + 2*(V[idx['joint*T4'],idx['below*T4']] - V[idx['joint*T4'],idx['below*T5']] - V[idx['joint*T5'],idx['below*T4']] + V[idx['joint*T5'],idx['below*T5']]))
    gse = float(np.sqrt(max(vg,0))); out['gap'] = (round(float(g),3), round(gse,3), round(float(g/gse),2))
    return out

# ---------- Part 2 ----------
b0, V0, n0, N0, F0 = wls_twoway(est)
R['part2'] = {'unweighted': contrast(b0, V0, n0)}
for wset, key in [(w_B1,'B1'), (w_B2,'B2'), (w_B3,'B3')]:
    wall = pd.concat([pd.Series(1.0, index=TREATED), wset])
    b, V, n, N, F = wls_twoway(est, weights=wall)
    R['part2'][key] = contrast(b, V, n)

# ---------- Part 3 ----------
R['part3'] = {}
for flag, lab in [(1,'persistent'), (0,'non_persistent')]:
    d = est[est.bal11==flag]
    b, V, n, N, F = wls_twoway(d)
    c = contrast(b, V, n)
    jf = c['joint_fall']
    c['n_rows'] = int(N); c['n_firms'] = int(F)
    c['joint_cell_firms'] = int(d.loc[d.cell=='joint','Symbol'].nunique())
    c['mde80'] = round(2.80*jf[1],2)
    R['part3'][lab] = c

R['counts'] = {'joint_firms': 1764, 'other_firms': 2402, 'bal11_joint_share': round(float(firm.loc[TREATED,'bal11'].mean()),3),
               'bal11_other_share': round(float(firm.loc[CONTROL,'bal11'].mean()),3),
               'nyears_joint': round(float(firm.loc[TREATED,'nyears'].mean()),2),
               'nyears_other': round(float(firm.loc[CONTROL,'nyears'].mean()),2),
               'complete_control_share': round(float(firm.loc[CONTROL,'complete'].mean()),3)}

with open('_firm_balance_results.json','w',encoding='utf-8') as f:
    json.dump(R, f, ensure_ascii=False, indent=1)
print(json.dumps(R, ensure_ascii=False, indent=1))
