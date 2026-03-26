"""Fig4a: ROスコア単体のAUROC（閉経前/後/全体を1パネルに）"""

import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import roc_curve, auc
import argparse
import os
from fig4_common import load_data, style_roc_ax, TARGET, MENOPAUSE, RISK

parser = argparse.ArgumentParser()
parser.add_argument('--noshow', action='store_true', help='Do not display the plot')
args = parser.parse_args()

df = load_data()

fig, ax = plt.subplots(1, 1, figsize=(6, 5.5))

pre = df[df[MENOPAUSE] == 0]
post = df[df[MENOPAUSE] == 1]

colors = {'pre': '#4A7BA7', 'post': '#C44E52', 'all': '#666666'}

for data, label, color in [
    (pre, 'Premenopausal', colors['pre']),
    (post, 'Postmenopausal', colors['post']),
    (df, 'All enrolled', colors['all']),
]:
    valid = data[[RISK, TARGET]].dropna()
    y = valid[TARGET].values.astype(int)
    score = valid[RISK].values
    fpr, tpr, _ = roc_curve(y, score)
    auc_val = auc(fpr, tpr)
    n = len(y)
    events = int(np.sum(y))
    print(f'{label}: N={n}, Events={events}, AUC={auc_val:.3f}')
    ax.plot(fpr, tpr, color=color, lw=2,
            label=f'{label} (AUC = {auc_val:.3f}, n={n})')

ax.plot([0, 1], [0, 1], 'k--', lw=1, alpha=0.5)
ax.set_title('Risk of osteoporosis score')
style_roc_ax(ax)
ax.legend(loc='lower right', frameon=True, edgecolor='black', fancybox=False)

plt.tight_layout()
os.makedirs('out', exist_ok=True)
plt.savefig('out/fig4a.png', dpi=300, bbox_inches='tight')
print('\nSaved as out/fig4a.png')

if not args.noshow:
    plt.show()
