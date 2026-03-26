"""Fig4c: LightGBM 6-fold CV SHAP（閉経前/後の特徴量重要度比較）"""

import matplotlib.pyplot as plt
import numpy as np
from sklearn.model_selection import StratifiedKFold
import lightgbm as lgb
import shap
import argparse
import os
from fig4_common import (
    load_data, get_features, style_ax,
    TARGET, MENOPAUSE, RISK, DISPLAY_NAMES,
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


def compute_cv_shap(X, y, n_splits, seed):
    """6-fold CVの各test setでSHAP値を計算し集約"""
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    shap_vals = np.zeros_like(X, dtype=float)

    for train_idx, test_idx in skf.split(X, y):
        model = create_model(seed)
        model.fit(X[train_idx], y[train_idx])

        explainer = shap.TreeExplainer(model)
        sv = explainer.shap_values(X[test_idx])
        if isinstance(sv, list):
            sv = sv[1]  # positive class
        shap_vals[test_idx] = sv

    return shap_vals


def plot_shap_bar(ax, shap_values, feature_names, title):
    """SHAP重要度の横棒グラフ（ROを赤でハイライト）"""
    mean_abs = np.mean(np.abs(shap_values), axis=0)
    display = [DISPLAY_NAMES.get(f, f) for f in feature_names]

    order = np.argsort(mean_abs)
    sorted_importance = mean_abs[order]
    sorted_names = [display[i] for i in order]
    sorted_raw = [feature_names[i] for i in order]

    colors = ['#C44E52' if f == RISK else '#4A7BA7' for f in sorted_raw]

    ax.barh(range(len(sorted_names)), sorted_importance,
            color=colors, edgecolor='black', linewidth=0.5)
    ax.set_yticks(range(len(sorted_names)))
    ax.set_yticklabels(sorted_names)
    ax.set_xlabel('Mean |SHAP value|')
    ax.set_title(title)
    style_ax(ax)


# === Main ===
df = load_data()
features = get_features(resection=args.resection) + [RISK]
suffix = '_resection' if args.resection else ''

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

for ax, data, title in [
    (axes[0], df[df[MENOPAUSE] == 0], 'Premenopausal women'),
    (axes[1], df[df[MENOPAUSE] == 1], 'Postmenopausal women'),
]:
    all_cols = list(dict.fromkeys(features + [TARGET]))
    valid = data[all_cols].dropna()
    X = valid[features].values
    y = valid[TARGET].values.astype(int)

    n_total, n_events = len(y), int(np.sum(y))
    print(f'\n=== {title} ===')
    print(f'N = {n_total}, Events = {n_events}')

    if n_events < args.n_splits or (n_total - n_events) < args.n_splits:
        ax.text(0.5, 0.5, 'Insufficient data', ha='center', va='center',
                transform=ax.transAxes, fontsize=12)
        ax.set_title(title)
        continue

    shap_vals = compute_cv_shap(X, y, args.n_splits, args.seed)

    # 重要度を表示
    mean_abs = np.mean(np.abs(shap_vals), axis=0)
    order = np.argsort(mean_abs)[::-1]
    print('Feature importance (mean |SHAP|):')
    for i in order:
        display = DISPLAY_NAMES.get(features[i], features[i])
        print(f'  {display}: {mean_abs[i]:.4f}')

    plot_shap_bar(ax, shap_vals, features, title)

plt.tight_layout()
os.makedirs('out', exist_ok=True)
plt.savefig(f'out/fig4c{suffix}.png', dpi=300, bbox_inches='tight')
print(f'\nSaved as out/fig4c{suffix}.png')

if not args.noshow:
    plt.show()
