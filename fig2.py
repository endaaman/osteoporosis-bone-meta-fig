import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from lifelines import KaplanMeierFitter
from lifelines.statistics import logrank_test
from lifelines.plotting import add_at_risk_counts
import numpy as np
import matplotlib.font_manager as fm
from matplotlib.ticker import MultipleLocator
import argparse

# Arialフォントの設定
arial_path = 'data/fonts/arial.ttf'
arial_prop = fm.FontProperties(fname=arial_path)
plt.rcParams['font.family'] = arial_prop.get_name()
fm.fontManager.addfont(arial_path)

# Matplotlibスタイルの設定
plt.rcParams['font.size'] = 12
plt.rcParams['axes.labelsize'] = 14
plt.rcParams['xtick.labelsize'] = 12
plt.rcParams['ytick.labelsize'] = 12
plt.rcParams['legend.fontsize'] = 11

# コマンドライン引数の処理
parser = argparse.ArgumentParser()
parser.add_argument('--noshow', action='store_true', help='Do not display the plot')
args = parser.parse_args()

# CSVファイルを読み込み
df = pd.read_csv('data/osteoporosis_bone_meta.csv')

# 必要な列を選択
df = df[['menopause', 'Cehst xray score ', 'BMFS_Event', 'BMFS']].copy()

# 欠損値を除外
df = df.dropna()

# リスクグループの作成
df['risk_group'] = df['Cehst xray score '].apply(lambda x: 'HRO' if x == 'High' else 'LRO')

def plot_km_panel(ax, data, title):
    """Kaplan-Meierプロットを描画する関数"""
    print(f"\n=== {title} ===")

    # Log-rank test
    lro_mask = data['risk_group'] == 'LRO'
    hro_mask = data['risk_group'] == 'HRO'

    print(f"LRO: n={lro_mask.sum()}, events={data[lro_mask]['BMFS_Event'].sum():.0f}")
    print(f"HRO: n={hro_mask.sum()}, events={data[hro_mask]['BMFS_Event'].sum():.0f}")

    if lro_mask.sum() > 0 and hro_mask.sum() > 0:
        result = logrank_test(data[lro_mask]['BMFS'], data[hro_mask]['BMFS'],
                              data[lro_mask]['BMFS_Event'], data[hro_mask]['BMFS_Event'])
        p_value = result.p_value
        print(f"Log-rank test p-value: {p_value:.4f}")
    else:
        p_value = np.nan
        print("Log-rank test: N/A (insufficient data)")

    # KMプロット
    # 論文用の落ち着いた色
    colors = {'LRO': '#4A7BA7', 'HRO': '#C44E52'}  # 青と赤

    kmf_list = []
    for group in ['LRO', 'HRO']:
        mask = data['risk_group'] == group
        if mask.sum() > 0:
            n = mask.sum()
            kmf_temp = KaplanMeierFitter()
            kmf_temp.fit(data[mask]['BMFS'], data[mask]['BMFS_Event'], label=f'{group} (n={n})')
            kmf_temp.plot(ax=ax, ci_show=False, show_censors=True,
                         censor_styles={'ms': 8, 'marker': '|'},
                         color=colors[group])
            kmf_list.append(kmf_temp)

    # number at riskを表示
    if len(kmf_list) > 0:
        add_at_risk_counts(*kmf_list, ax=ax, xticks=[0, 9, 19, 29, 39, 49, 59], fontsize=11)

        # Number at riskの値を表示
        print("\nNumber at risk at key time points:")
        for i, kmf_temp in enumerate(kmf_list):
            group_name = ['LRO', 'HRO'][i]
            at_risk_at_key_times = []
            for t in [0, 10, 20, 30, 40, 50, 60]:
                future_times = kmf_temp.event_table.index[kmf_temp.event_table.index >= t]
                if len(future_times) > 0:
                    at_risk_at_key_times.append(int(kmf_temp.event_table.loc[future_times[0], 'at_risk']))
                else:
                    at_risk_at_key_times.append(0)
            print(f"{group_name}: {at_risk_at_key_times}")

    # 軸設定
    p_str = f'p < 0.01' if p_value < 0.01 else f'p = {p_value:.2f}'
    ax.set_title(title)
    ax.set_xlabel('Months after surgery')
    ax.set_ylabel('Bone metastasis-free ratio')
    ax.set_xlim([0, 65.5])  # padding rightで数字間隔を広げる
    ax.set_ylim([0, 1])

    # 右と上の枠線を非表示
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    # Y軸の設定：0.2刻みでラベル付き長いひげ、0.1刻みでラベルなし短いひげ
    ax.yaxis.set_major_locator(MultipleLocator(0.2))
    ax.yaxis.set_minor_locator(MultipleLocator(0.1))

    # X軸の設定：20刻みでラベル付き長いひげ、10刻みでラベルなし短いひげ
    ax.xaxis.set_major_locator(MultipleLocator(20))
    ax.xaxis.set_minor_locator(MultipleLocator(10))

    # 軸のティックを表示
    # X軸：major=6, minor=3
    ax.tick_params(axis='x', which='major', direction='out', length=6, width=1.2)
    ax.tick_params(axis='x', which='minor', direction='out', length=3, width=1)
    # Y軸：major=6, minor=3
    ax.tick_params(axis='y', which='major', direction='out', length=6, width=1.2)
    ax.tick_params(axis='y', which='minor', direction='out', length=3, width=1)

    # 凡例（軸線と同じ黒線）
    legend = ax.legend(loc='lower left', title=p_str, frameon=True, edgecolor='black', fancybox=False)

# Figure 2の作成 (number at riskのためにheightを増やす)
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

# 各パネルをプロット
plot_km_panel(axes[0], df.copy(), 'Enrolled women')
plot_km_panel(axes[1], df[df['menopause'] == 0].copy(), 'Premenopausal women')
plot_km_panel(axes[2], df[df['menopause'] == 1].copy(), 'Postmenopausal women')

plt.tight_layout()
plt.subplots_adjust(bottom=0.4)  # number at riskとプロットの間隔を広げる

# out/ ディレクトリに出力
import os
os.makedirs('out', exist_ok=True)
plt.savefig('out/fig2.png', dpi=300, bbox_inches='tight')
print('Figure 2 saved as out/fig2.png')

if not args.noshow:
    plt.show()
