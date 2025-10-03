import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import matplotlib.font_manager as fm
from matplotlib.ticker import MultipleLocator
from scipy.stats import pearsonr, spearmanr
import argparse
from scipy.stats import chi2_contingency

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

# Figure 3の作成
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# =========================================
# a) Conduction rate of perioperative bone density test
# =========================================
ax1 = axes[0]

# 閉経前と閉経後の実施率を計算
premenopausal = df[df['menopause'] == 0]
postmenopausal = df[df['menopause'] == 1]

pre_rate = (premenopausal['Perioperative Dxa presence'] == 1).sum() / len(premenopausal)
post_rate = (postmenopausal['Perioperative Dxa presence'] == 1).sum() / len(postmenopausal)

print(f"Premenopausal DXA rate: {pre_rate:.3f} ({(premenopausal['Perioperative Dxa presence'] == 1).sum()}/{len(premenopausal)})")
print(f"Postmenopausal DXA rate: {post_rate:.3f} ({(postmenopausal['Perioperative Dxa presence'] == 1).sum()}/{len(postmenopausal)})")

# 棒グラフを描画
x_pos = [0, 0.5]
rates = [pre_rate, post_rate]
labels = ['Premenopausal\nwomen', 'Postmenopausal\nwomen']

# 濃い青と薄い青
bars = ax1.bar(x_pos, rates, width=0.3, color=['#4A7BA7', '#8EBBE8'], edgecolor='black', linewidth=1.2)

# 有意差の表示
pre_dxa = (premenopausal['Perioperative Dxa presence'] == 1).sum()
pre_total = len(premenopausal)
post_dxa = (postmenopausal['Perioperative Dxa presence'] == 1).sum()
post_total = len(postmenopausal)

# カイ二乗検定
contingency_table = [[pre_dxa, pre_total - pre_dxa], [post_dxa, post_total - post_dxa]]
chi2, p_value, dof, expected = chi2_contingency(contingency_table)
print(f"Chi-square test: p={p_value:.4e}")

# 有意差の棒線とアスタリスク
y_max = max(rates)
h = 0.05  # 棒線の高さ
ax1.plot([0, 0.5], [y_max + h, y_max + h], 'k-', linewidth=1.2)
ax1.plot([0, 0], [y_max + h - 0.01, y_max + h], 'k-', linewidth=1.2)
ax1.plot([0.5, 0.5], [y_max + h - 0.01, y_max + h], 'k-', linewidth=1.2)

# 有意差テキストの表示
if p_value < 0.01:
    ax1.text(0.25, y_max + h - 0.01, '**', ha='center', va='bottom', fontsize=16, fontweight='bold')
    ax1.text(0.25, y_max + h + 0.05, 'p < 0.01', ha='center', va='bottom', fontsize=11)
else:
    ax1.text(0.25, y_max + h + 0.02, f'p = {p_value:.2f}', ha='center', va='bottom', fontsize=11)

# 軸設定
ax1.set_ylabel('Conduction rate of\nperioperative bone density test')
ax1.set_xticks(x_pos)
ax1.set_xlim([-0.3, 0.8])
ax1.set_xticklabels(labels)
ax1.set_ylim([0, 0.9])

# Y軸の設定：0.1刻みでmajorティック
ax1.yaxis.set_major_locator(MultipleLocator(0.1))

# 右と上の枠線を非表示
ax1.spines['right'].set_visible(False)
ax1.spines['top'].set_visible(False)

# 軸のティックを表示
ax1.tick_params(axis='both', which='major', direction='out', length=6, width=1.2)

# =========================================
# b) Correlation between T-scores and risk of osteoporosis
# =========================================
ax2 = axes[1]

# J列=1の患者のみ
dxa_patients = df[df['Perioperative Dxa presence'] == 1].copy()

# numeric型に変換
dxa_patients['AI_P'] = pd.to_numeric(dxa_patients['AI_P'], errors='coerce')
dxa_patients['Tscore'] = pd.to_numeric(dxa_patients['Tscore'], errors='coerce')

# 欠損値を除外
dxa_patients = dxa_patients.dropna(subset=['AI_P', 'Tscore'])

# 相関係数を計算（Spearman）
if len(dxa_patients) > 0:
    r, p_value = spearmanr(dxa_patients['AI_P'], dxa_patients['Tscore'])
    print(f"\nSpearman correlation: rs={r:.3f}, p={p_value:.4f}")

    # 散布図
    ax2.scatter(dxa_patients['AI_P'], dxa_patients['Tscore'],
                color='#4A7BA7', s=50, alpha=0.6, edgecolors='black', linewidth=0.5)

    # 相関係数を凡例として表示
    legend_text = f'rs = {r:.3f}, p < 0.01' if p_value < 0.01 else f'rs = {r:.3f}, p = {p_value:.2f}'
    ax2.legend([legend_text], loc='upper right', frameon=True, edgecolor='black', fancybox=False)

# 軸設定
ax2.set_xlabel('Risk of osteoporosis')
ax2.set_ylabel('T-score')
ax2.set_xlim([-0.1, 1.1])
ax2.set_ylim([-4.5, 4.5])

# X軸の設定：0.2刻みでmajor、0.1刻みでminor
ax2.xaxis.set_major_locator(MultipleLocator(0.2))
ax2.xaxis.set_minor_locator(MultipleLocator(0.1))

# Y軸の設定：2刻みでmajor、1刻みでminor
ax2.yaxis.set_major_locator(MultipleLocator(2))
ax2.yaxis.set_minor_locator(MultipleLocator(1))

# 右と上の枠線を非表示
ax2.spines['right'].set_visible(False)
ax2.spines['top'].set_visible(False)

# 軸のティックを表示
ax2.tick_params(axis='both', which='major', direction='out', length=6, width=1.2)
ax2.tick_params(axis='both', which='minor', direction='out', length=3, width=1)

plt.tight_layout()

# out/ ディレクトリに出力
import os
os.makedirs('out', exist_ok=True)
plt.savefig('out/fig3.png', dpi=300, bbox_inches='tight')
print('\nFigure 3 saved as out/fig3.png')

if not args.noshow:
    plt.show()
