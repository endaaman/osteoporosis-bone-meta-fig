"""Fig4 SHAP: 6-fold CV SHAP（閉経前/後の特徴量重要度比較）"""

import matplotlib.pyplot as plt
import numpy as np
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler
import shap
import argparse
import os
import warnings
warnings.filterwarnings('ignore', category=UserWarning)
from fig4_common import (
    load_data, get_features, style_ax,
    TARGET, MENOPAUSE, RISK, DISPLAY_NAMES,
)

parser = argparse.ArgumentParser()
parser.add_argument('--noshow', action='store_true', help='Do not display the plot')
parser.add_argument('--model', choices=['lr', 'ridge', 'lasso', 'lgbm'], default='lgbm',
                    help='Model type (default: lgbm)')
parser.add_argument('--n-splits', type=int, default=6)
parser.add_argument('--seed', type=int, default=42)
args = parser.parse_args()


def create_model(model_type, seed):
    if model_type == 'lgbm':
        import lightgbm as lgb
        return lgb.LGBMClassifier(
            n_estimators=100, max_depth=4, learning_rate=0.1,
            num_leaves=15, random_state=seed, verbose=-1,
        )
    elif model_type == 'ridge':
        from sklearn.linear_model import LogisticRegression
        return LogisticRegression(penalty='l2', C=0.1, max_iter=1000, random_state=seed)
    elif model_type == 'lasso':
        from sklearn.linear_model import LogisticRegression
        return LogisticRegression(penalty='l1', C=0.1, solver='saga', max_iter=5000, random_state=seed)
    else:  # lr
        from sklearn.linear_model import LogisticRegression
        return LogisticRegression(max_iter=1000, random_state=seed)


def compute_cv_shap(X, y, n_splits, seed):
    """6-fold CVの各test setでSHAP値を計算し集約"""
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    shap_vals = np.zeros_like(X, dtype=float)
    needs_scaling = args.model != 'lgbm'

    for train_idx, test_idx in skf.split(X, y):
        model = create_model(args.model, seed)

        if needs_scaling:
            scaler = StandardScaler()
            X_train = scaler.fit_transform(X[train_idx])
            X_test = scaler.transform(X[test_idx])
        else:
            X_train, X_test = X[train_idx], X[test_idx]

        model.fit(X_train, y[train_idx])

        if args.model == 'lgbm':
            explainer = shap.TreeExplainer(model)
        else:
            explainer = shap.LinearExplainer(model, X_train)
        sv = explainer.shap_values(X_test)
        if isinstance(sv, list):
            sv = sv[1]
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
import pandas as pd

df = load_data()
features = get_features(resection=True) + [RISK, MENOPAUSE]
display_features = [DISPLAY_NAMES.get(f, f) for f in features]
model_name = args.model

print(f'SHAP: model={model_name}, CV={args.n_splits}-fold, seed={args.seed}')

os.makedirs('out', exist_ok=True)

# barとsummaryの両方を生成
panels = [
    (df[df[MENOPAUSE] == 0], 'pre', 'Premenopausal women'),
    (df[df[MENOPAUSE] == 1], 'post', 'Postmenopausal women'),
    (df, 'all', 'Enrolled women'),
]

fig_bar, axes_bar = plt.subplots(1, len(panels), figsize=(6 * len(panels), 5))

for idx, (data, key, title) in enumerate(panels):
    all_cols = list(dict.fromkeys(features + [TARGET]))
    valid = data[all_cols].dropna()
    X = valid[features].values
    y = valid[TARGET].values.astype(int)

    n_total, n_events = len(y), int(np.sum(y))
    print(f'\n=== {title} ===')
    print(f'N = {n_total}, Events = {n_events}')

    if n_events < args.n_splits or (n_total - n_events) < args.n_splits:
        axes_bar[idx].text(0.5, 0.5, 'Insufficient data', ha='center', va='center',
                           transform=axes_bar[idx].transAxes, fontsize=12)
        axes_bar[idx].set_title(title)
        continue

    shap_vals = compute_cv_shap(X, y, args.n_splits, args.seed)

    mean_abs = np.mean(np.abs(shap_vals), axis=0)
    order = np.argsort(mean_abs)[::-1]
    print('Feature importance (mean |SHAP|):')
    for i in order:
        print(f'  {display_features[i]}: {mean_abs[i]:.4f}')

    # bar plot
    plot_shap_bar(axes_bar[idx], shap_vals, features, title)

    # summary plot (beeswarm)
    X_display = pd.DataFrame(X, columns=display_features)
    fig_sum, ax_sum = plt.subplots(1, 1, figsize=(8, 6))
    shap.summary_plot(shap_vals, X_display, show=False, plot_size=None)
    plt.title(title)
    plt.tight_layout()
    sum_suffix = f'_{key}' if key != 'all' else ''
    sum_path = f'out/fig4_{model_name}_shap{sum_suffix}.png'
    plt.savefig(sum_path, dpi=300, bbox_inches='tight')
    print(f'Summary saved as {sum_path}')
    plt.close(fig_sum)

fig_bar.tight_layout()
bar_path = f'out/fig4_{model_name}_shap_bar.png'
fig_bar.savefig(bar_path, dpi=300, bbox_inches='tight')
print(f'\nBar saved as {bar_path}')

if not args.noshow:
    plt.show()
