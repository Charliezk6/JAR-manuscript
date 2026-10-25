# -*- coding: utf-8 -*-
"""Phase 1b: cell assignment on reconstructed estimation sample + benchmark reproduction."""
import numpy as np, pandas as pd

df = pd.read_pickle('_panel18.pkl')
m = (df.CPATenure<=5)
est = df[m].copy()
cnt = est.groupby('Symbol').size()
keep = cnt[cnt>=2].index
est = est[est.Symbol.isin(keep)].copy()
print('estimation sample:', est.shape, '| firms:', est.Symbol.nunique(), '| joint5:', int(est.joint5.sum()))

# cell assignment: audit-firm clock in first partner-clock-five year
c5 = est[est.CPATenure==5]
first5 = c5.groupby('Symbol').agg(first5_year=('Year','min')).reset_index()
first5 = first5.merge(est[['Symbol','Year','AuditorTenure']], left_on=['Symbol','first5_year'],
                      right_on=['Symbol','Year'], how='left').drop(columns='Year')
first5['cell'] = np.where(first5.AuditorTenure==5, 'joint',
                  np.where(first5.AuditorTenure<5, 'below', 'above'))
cells = first5.set_index('Symbol')['cell']
est['cell'] = est.Symbol.map(cells).fillna('none')
vc = est.groupby('cell').Symbol.nunique()
print('firm counts by cell (target joint 1,764 / below 463 / above 996 / none 943):')
print(vc, '| total:', est.Symbol.nunique())
print('joint firm-years (target 2,018):', int(est.joint5.sum()))
# cross-check joint_deadline_cell vs joint5
print('joint_deadline_cell sum:', int(est.joint_deadline_cell.sum()))
# balanced panel rows in est (target 13,122)
print('bal11 rows in est (target 13,122):', int(est.bal11.sum()), '| firms:', est.loc[est.bal11==1,'Symbol'].nunique())
# in_pair rows in est (target 19,376)
print('in_pair rows in est (target 19,376):', int(est.in_pair.sum()))
# audit-firm clock distribution at first clock-five year (Table A.6 check)
d = first5.AuditorTenure.value_counts().sort_index()
print('audit-firm clock at first partner-clock-five year:'); print(d)
est.to_pickle('_est31k.pkl'); first5.to_pickle('_first5.pkl')
print('saved')
