import pandas as pd
import matplotlib.pyplot as plt
from lifelines import KaplanMeierFitter
from lifelines.statistics import logrank_test
import numpy as np
import matplotlib.font_manager as fm

# Arialフォントの設定
arial_path = 'data/fonts/arial.ttf'
arial_prop = fm.FontProperties(fname=arial_path)
plt.rcParams['font.family'] = arial_prop.get_name()
fm.fontManager.addfont(arial_path)

# CSVファイルを読み込み
df = pd.read_csv('data/osteoporosis_bone_meta.csv')

# 必要な列を選択
df = df[['menopause', 'Cehst xray score ', 'BMFS_Event', 'BMFS']].copy()

# 欠損値を除外
df = df.dropna()

# リスクグループの作成
df['risk_group'] = df['Cehst xray score '].apply(lambda x: 'HRO' if x == 'High' else 'LRO')

# Figure 2の作成
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

# KMFitterのインスタンス
kmf = KaplanMeierFitter()

# a) All enrolled women
ax = axes[0]
df_all = df.copy()

# Log-rank test
lro_mask = df_all['risk_group'] == 'LRO'
hro_mask = df_all['risk_group'] == 'HRO'
result = logrank_test(df_all[lro_mask]['BMFS'], df_all[hro_mask]['BMFS'],
                      df_all[lro_mask]['BMFS_Event'], df_all[hro_mask]['BMFS_Event'])
p_value = result.p_value

n_lro = lro_mask.sum()
n_hro = hro_mask.sum()

for group in ['LRO', 'HRO']:
    mask = df_all['risk_group'] == group
    n = mask.sum()
    kmf.fit(df_all[mask]['BMFS'], df_all[mask]['BMFS_Event'], label=f'{group} (n={n})')
    kmf.plot(ax=ax, ci_show=False, show_censors=True, censor_styles={'ms': 6, 'marker': '|'})

ax.set_title('Enrolled women')
ax.set_xlabel('Months')
ax.set_ylabel('Bone metastasis-free survival')
ax.set_ylim([0, 1])
ax.legend(loc='lower left', title=f'p = {p_value:.2f}')

# b) Premenopausal women
ax = axes[1]
df_pre = df[df['menopause'] == 0].copy()

# Log-rank test
lro_mask = df_pre['risk_group'] == 'LRO'
hro_mask = df_pre['risk_group'] == 'HRO'
if lro_mask.sum() > 0 and hro_mask.sum() > 0:
    result = logrank_test(df_pre[lro_mask]['BMFS'], df_pre[hro_mask]['BMFS'],
                          df_pre[lro_mask]['BMFS_Event'], df_pre[hro_mask]['BMFS_Event'])
    p_value = result.p_value
else:
    p_value = np.nan

n_lro = lro_mask.sum()
n_hro = hro_mask.sum()

for group in ['LRO', 'HRO']:
    mask = df_pre['risk_group'] == group
    if mask.sum() > 0:
        n = mask.sum()
        kmf.fit(df_pre[mask]['BMFS'], df_pre[mask]['BMFS_Event'], label=f'{group} (n={n})')
        kmf.plot(ax=ax, ci_show=False, show_censors=True, censor_styles={'ms': 6, 'marker': '|'})

p_str = f'p < 0.01' if p_value < 0.01 else f'p = {p_value:.2f}'
ax.set_title('Premenopausal women')
ax.set_xlabel('Months')
ax.set_ylabel('Bone metastasis-free survival')
ax.set_ylim([0, 1])
ax.legend(loc='lower left', title=p_str)

# c) Postmenopausal women
ax = axes[2]
df_post = df[df['menopause'] == 1].copy()

# Log-rank test
lro_mask = df_post['risk_group'] == 'LRO'
hro_mask = df_post['risk_group'] == 'HRO'
if lro_mask.sum() > 0 and hro_mask.sum() > 0:
    result = logrank_test(df_post[lro_mask]['BMFS'], df_post[hro_mask]['BMFS'],
                          df_post[lro_mask]['BMFS_Event'], df_post[hro_mask]['BMFS_Event'])
    p_value = result.p_value
else:
    p_value = np.nan

n_lro = lro_mask.sum()
n_hro = hro_mask.sum()

for group in ['LRO', 'HRO']:
    mask = df_post['risk_group'] == group
    if mask.sum() > 0:
        n = mask.sum()
        kmf.fit(df_post[mask]['BMFS'], df_post[mask]['BMFS_Event'], label=f'{group} (n={n})')
        kmf.plot(ax=ax, ci_show=False, show_censors=True, censor_styles={'ms': 6, 'marker': '|'})

ax.set_title('Postmenopausal women')
ax.set_xlabel('Months')
ax.set_ylabel('Bone metastasis-free survival')
ax.set_ylim([0, 1])
ax.legend(loc='lower left', title=f'p = {p_value:.2f}')

plt.tight_layout()

# out/ ディレクトリに出力
import os
os.makedirs('out', exist_ok=True)
plt.savefig('out/fig2.png', dpi=300, bbox_inches='tight')
print('Figure 2 saved as out/fig2.png')
plt.show()
