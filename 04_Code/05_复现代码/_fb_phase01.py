# -*- coding: utf-8 -*-
"""Phase 0-1: reconstruct estimation sample, assign Table 6 cells, reproduce benchmark."""
import numpy as np, pandas as pd

df = pd.read_pickle('_panel18.pkl')
print('panel18:', df.shape)

CONTROLS = ['Size','ROA','Growth','Cash','lev','soe','Age_c','Female','Edu','Pay_gap']

# --- Phase 0: reconstruct the 31,274 estimation sample ---
need = ['E_H'] + CONTROLS
miss = df[need].isna().any(axis=1)
print('rows missing E_H or any control:', miss.sum())
est = df[~miss].copy()
print('estimation sample:', est.shape, '| firms:', est.Symbol.nunique())
print('joint5 firm-years in est:', int(est.joint5.sum()))
print('bal11 firms:', df.loc[df.bal11==1,'Symbol'].nunique(), '| bal11 rows in panel18:', int(df.bal11.sum()),
      '| bal11 rows in est:', int(est.bal11.sum()))
print('in_pair rows in est:', int(est.in_pair.sum()))
print('years:', sorted(est.Year.unique()))

# --- Phase 1: cell assignment by audit-firm clock in first partner-clock-five year ---
c5 = est[est.CPATenure==5]
first5 = c5.groupby('Symbol').agg(first5_year=('Year','min')).reset_index()
first5 = first5.merge(est[['Symbol','Year','AuditorTenure']], left_on=['Symbol','first5_year'],
                      right_on=['Symbol','Year'], how='left').drop(columns='Year')
first5['cell'] = np.where(first5.AuditorTenure==5, 'joint',
                  np.where(first5.AuditorTenure<5, 'below', 'above'))
cells = first5.set_index('Symbol')['cell']
est['cell'] = est.Symbol.map(cells).fillna('none')
vc = est.groupby('cell').Symbol.nunique()
print('\nfirm counts by cell (target 1,764/463/996/943):')
print(vc)
print('total firms:', est.Symbol.nunique())
# joint firm-years check (target 2,018)
jy = est[(est.CPATenure==5)]
print('firm-years with CPATenure==5:', len(jy), '| joint5 among them:', int(jy.joint5.sum()))

# sanity: joint cell firms all have AuditorTenure==5 at first5?
chk = first5.groupby('cell').AuditorTenure.describe()[['count','min','max']]
print(chk)

est.to_pickle('_est31k.pkl')
first5.to_pickle('_first5.pkl')
print('saved _est31k.pkl / _first5.pkl')
