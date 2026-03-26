"""Fig4b: LightGBM 6-fold CV AUROC（with/without RO ablation）"""

import matplotlib.pyplot as plt
import numpy as np
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_curve, auc
import lightgbm as lgb
import argparse
import os
from fig4_common import (
    load_data, get_features, style_roc_ax, delong_test,
    TARGET, MENOPAUSE, RISK,
)

parser = argparse.ArgumentParser()
parser.add_argument('--noshow', action='store_true', help='Do not display the plot')
parser.add_argument('--resection', action='store_true', help='Include resection features')
parser.add_argument('--n-splits', type=int, default=6)
parser.add_argument('--seed', type=int, default=42)
args = parser.parse_args()


def create_model(seed):
    return lgb.LGBMClassifier(
        n_estimators=100, max_depth=4, learning_rate=0.1,
        num_leaves=15, random_state=seed, verbose=-1,
    )


def compute_cv_predictions(X, y, n_splits, seed):
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    y_prob = np.zeros(len(y))

    for train_idx, test_idx in skf.split(X, y):
        model = create_model(seed)
        model.fit(X[train_idx], y[train_idx])
        y_prob[test_idx] = model.predict_proba(X[test_idx])[:, 1]

    return y_prob


def plot_roc_panel(ax, data, title, features, risk_feat, n_splits, seed):
    feats_with = features + [risk_feat]
    feats_without = features[:]

    all_cols = list(dict.fromkeys(feats_with + [TARGET]))
    valid = data[all_cols].dropna()
    X_with = valid[feats_with].values
    X_without = valid[feats_without].values
    y = valid[TARGET].values.astype(int)

    n_total, n_events = len(y), int(np.sum(y))
    print(f'\n=== {title} ===')
    print(f'N = {n_total}, Events = {n_events}')

    if n_events < n_splits or (n_total - n_events) < n_splits:
        ax.text(0.5, 0.5, 'Insufficient data', ha='center', va='center',
                transform=ax.transAxes, fontsize=12)
        ax.set_title(title)
        return

    prob_with = compute_cv_predictions(X_with, y, n_splits, seed)
    prob_without = compute_cv_predictions(X_without, y, n_splits, seed)

    fpr1, tpr1, _ = roc_curve(y, prob_with)
    fpr2, tpr2, _ = roc_curve(y, prob_without)
    auc1, auc2 = auc(fpr1, tpr1), auc(fpr2, tpr2)

    _, _, z_val, p_val = delong_test(y, prob_with, prob_without)

    print(f'With RO:    AUC = {auc1:.3f}')
    print(f'Without RO: AUC = {auc2:.3f}')
    print(f'DeLong: z = {z_val:.3f}, p = {p_val:.4f}')

    ax.plot(fpr1, tpr1, color='#4A7BA7', lw=2,
            label=f'With RO (AUC = {auc1:.3f})')
    ax.plot(fpr2, tpr2, color='#C44E52', lw=2,
            label=f'Without RO (AUC = {auc2:.3f})')
    ax.plot([0, 1], [0, 1], 'k--', lw=1, alpha=0.5)

    p_str = 'p < 0.01' if p_val < 0.01 else f'p = {p_val:.2f}'
    ax.set_title(title)
    style_roc_ax(ax)
    ax.legend(loc='lower right', title=p_str, frameon=True, edgecolor='black', fancybox=False)


# === Main ===
df = load_data()
features = get_features(resection=args.resection)
suffix = '_resection' if args.resection else ''

fig, axes = plt.subplots(1, 3, figsize=(15, 5))

pre = df[df[MENOPAUSE] == 0]
post = df[df[MENOPAUSE] == 1]

plot_roc_panel(axes[0], pre, 'Premenopausal women', features, RISK, args.n_splits, args.seed)
plot_roc_panel(axes[1], post, 'Postmenopausal women', features, RISK, args.n_splits, args.seed)
plot_roc_panel(axes[2], df, 'Enrolled women', features, RISK, args.n_splits, args.seed)

plt.tight_layout()
os.makedirs('out', exist_ok=True)
plt.savefig(f'out/fig4b{suffix}.png', dpi=300, bbox_inches='tight')
print(f'\nSaved as out/fig4b{suffix}.png')

if not args.noshow:
    plt.show()
