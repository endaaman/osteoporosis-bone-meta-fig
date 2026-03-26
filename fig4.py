import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.font_manager as fm
from matplotlib.ticker import MultipleLocator
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_curve, auc
from sklearn.preprocessing import StandardScaler
from scipy.stats import norm
import argparse
import os
import warnings
warnings.filterwarnings('ignore', category=UserWarning)

# --- Arialフォントの設定 ---
arial_path = 'data/fonts/arial.ttf'
arial_prop = fm.FontProperties(fname=arial_path)
plt.rcParams['font.family'] = arial_prop.get_name()
fm.fontManager.addfont(arial_path)

# --- Matplotlibスタイルの設定 ---
plt.rcParams['font.size'] = 12
plt.rcParams['axes.labelsize'] = 14
plt.rcParams['xtick.labelsize'] = 12
plt.rcParams['ytick.labelsize'] = 12
plt.rcParams['legend.fontsize'] = 11

# --- コマンドライン引数 ---
parser = argparse.ArgumentParser()
parser.add_argument('--noshow', action='store_true', help='Do not display the plot')
parser.add_argument('--model', choices=['lr', 'ridge', 'lasso', 'lgbm'], default='lr',
                    help='Model type (default: lr)')
parser.add_argument('--shap', action='store_true', help='Generate SHAP plots')
parser.add_argument('--n-splits', type=int, default=6, help='Number of CV folds')
parser.add_argument('--seed', type=int, default=42, help='Random seed')
args = parser.parse_args()

# --- データ読み込み ---
df = pd.read_excel('data/fig4/enrolled_patients_20260322.xlsx')

# --- カラム名定義 ---
TARGET = 'BMFS_Event（ROCの答え＝骨メタあり）'
MENOPAUSE = '閉経あり=1'
RISK = 'Risk of osteosporosis'

BASE_FEATURES = [
    'BMI', 'Age', 'ER', 'PR', 'HER2 ', 'Ki67(%)',
    'Stage', 'perioperative chemo', 'endcrine', 'post-radiation',
]

RESECTION_FEATURES = [
    'Tumor size', 'Nodal involvement',
    'number of affected nodes', 'resected nodes', 'grade',
]

DISPLAY_NAMES = {
    'BMI': 'BMI', 'Age': 'Age', 'ER': 'ER', 'PR': 'PR',
    'HER2 ': 'HER2', 'Ki67(%)': 'Ki67', 'Stage': 'Stage',
    'perioperative chemo': 'Chemotherapy',
    'endcrine': 'Endocrine therapy',
    'post-radiation': 'Radiation',
    'Risk of osteosporosis': 'Risk of osteoporosis',
    'Tumor size': 'Tumor size',
    'Nodal involvement': 'Nodal involvement',
    'number of affected nodes': 'Affected nodes',
    'resected nodes': 'Resected nodes',
    'grade': 'Grade',
}

# --- 前処理 ---
df = df[df['Exclude'] == 0].copy()

for col in BASE_FEATURES + [RISK] + RESECTION_FEATURES + [TARGET, MENOPAUSE]:
    df[col] = pd.to_numeric(df[col], errors='coerce')


# =========================================================
# モデル作成
# =========================================================
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


def _needs_scaling():
    return args.model != 'lgbm'


# =========================================================
# DeLong test
# =========================================================
def delong_test(y_true, y_score1, y_score2):
    y_true = np.asarray(y_true, dtype=int)
    y_score1 = np.asarray(y_score1, dtype=float)
    y_score2 = np.asarray(y_score2, dtype=float)

    pos_mask = y_true == 1
    neg_mask = y_true == 0
    pos1, neg1 = y_score1[pos_mask], y_score1[neg_mask]
    pos2, neg2 = y_score2[pos_mask], y_score2[neg_mask]
    m, n = len(pos1), len(neg1)

    if m == 0 or n == 0:
        return np.nan, np.nan, np.nan, 1.0

    v10_1 = np.array([(np.sum(p > neg1) + 0.5 * np.sum(p == neg1)) / n for p in pos1])
    v01_1 = np.array([(np.sum(q < pos1) + 0.5 * np.sum(q == pos1)) / m for q in neg1])
    v10_2 = np.array([(np.sum(p > neg2) + 0.5 * np.sum(p == neg2)) / n for p in pos2])
    v01_2 = np.array([(np.sum(q < pos2) + 0.5 * np.sum(q == pos2)) / m for q in neg2])

    auc1, auc2 = np.mean(v10_1), np.mean(v10_2)

    s10 = np.cov(v10_1, v10_2, ddof=1) if m > 1 else np.zeros((2, 2))
    s01 = np.cov(v01_1, v01_2, ddof=1) if n > 1 else np.zeros((2, 2))

    var_diff = (s10[0, 0] + s10[1, 1] - 2 * s10[0, 1]) / m + \
               (s01[0, 0] + s01[1, 1] - 2 * s01[0, 1]) / n

    if var_diff <= 0:
        return auc1, auc2, 0.0, 1.0

    z = (auc1 - auc2) / np.sqrt(var_diff)
    p = 2 * (1 - norm.cdf(abs(z)))
    return auc1, auc2, z, p


# =========================================================
# Stratified CV（予測値 + SHAP値）
# =========================================================
def compute_cv(X, y, n_splits, seed, compute_shap=False):
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    y_prob = np.zeros(len(y))
    shap_vals = np.zeros_like(X, dtype=float) if compute_shap else None

    for train_idx, test_idx in skf.split(X, y):
        model = create_model(args.model, seed)

        if _needs_scaling():
            scaler = StandardScaler()
            X_train = scaler.fit_transform(X[train_idx])
            X_test = scaler.transform(X[test_idx])
        else:
            X_train, X_test = X[train_idx], X[test_idx]

        model.fit(X_train, y[train_idx])
        y_prob[test_idx] = model.predict_proba(X_test)[:, 1]

        if compute_shap:
            import shap
            if args.model == 'lgbm':
                explainer = shap.TreeExplainer(model)
            else:
                explainer = shap.LinearExplainer(model, X_train)
            sv = explainer.shap_values(X_test)
            if isinstance(sv, list):
                sv = sv[1]
            shap_vals[test_idx] = sv

    return y_prob, shap_vals


# =========================================================
# ROCパネル描画（SHAP値も返す）
# =========================================================
def plot_roc_panel(ax, data, title, base_feats, risk_feat, extra_feats=None):
    feats_with = base_feats + [risk_feat]
    feats_without = base_feats[:]
    if extra_feats:
        feats_with = feats_with + extra_feats
        feats_without = feats_without + extra_feats

    # 両モデルで同一患者セットを使用
    all_cols = list(dict.fromkeys(feats_with + [TARGET]))
    valid = data[all_cols].dropna()
    X_with = valid[feats_with].values
    X_without = valid[feats_without].values
    y = valid[TARGET].values.astype(int)

    n_total = len(y)
    n_events = int(np.sum(y))
    print(f'\n=== {title} ===')
    print(f'N = {n_total}, Events = {n_events}')

    if n_events < args.n_splits or (n_total - n_events) < args.n_splits:
        ax.text(0.5, 0.5, 'Insufficient data', ha='center', va='center',
                transform=ax.transAxes, fontsize=12)
        ax.set_title(title)
        return None, None

    # CV予測値（with ROのみSHAP計算）
    prob_with, shap_with = compute_cv(X_with, y, args.n_splits, args.seed,
                                      compute_shap=args.shap)
    prob_without, _ = compute_cv(X_without, y, args.n_splits, args.seed)

    # ROC曲線
    fpr1, tpr1, _ = roc_curve(y, prob_with)
    fpr2, tpr2, _ = roc_curve(y, prob_without)
    auc1 = auc(fpr1, tpr1)
    auc2 = auc(fpr2, tpr2)

    # DeLong test
    _, _, z_val, p_val = delong_test(y, prob_with, prob_without)

    print(f'With RO:    AUC = {auc1:.3f}')
    print(f'Without RO: AUC = {auc2:.3f}')
    print(f'DeLong: z = {z_val:.3f}, p = {p_val:.4f}')

    # 描画
    ax.plot(fpr1, tpr1, color='#4A7BA7', lw=2,
            label=f'With RO (AUC = {auc1:.3f})')
    ax.plot(fpr2, tpr2, color='#C44E52', lw=2,
            label=f'Without RO (AUC = {auc2:.3f})')
    ax.plot([0, 1], [0, 1], 'k--', lw=1, alpha=0.5)

    # 軸設定
    p_str = 'p < 0.01' if p_val < 0.01 else f'p = {p_val:.2f}'
    ax.set_title(title)
    ax.set_xlabel('1 - Specificity')
    ax.set_ylabel('Sensitivity')
    ax.set_xlim([0, 1])
    ax.set_ylim([0, 1])

    ax.xaxis.set_major_locator(MultipleLocator(0.2))
    ax.xaxis.set_minor_locator(MultipleLocator(0.1))
    ax.yaxis.set_major_locator(MultipleLocator(0.2))
    ax.yaxis.set_minor_locator(MultipleLocator(0.1))

    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    ax.tick_params(axis='both', which='major', direction='out', length=6, width=1.2)
    ax.tick_params(axis='both', which='minor', direction='out', length=3, width=1)

    ax.legend(loc='lower right', title=p_str, frameon=True, edgecolor='black', fancybox=False)

    return feats_with, shap_with


# =========================================================
# SHAPバーチャート
# =========================================================
def plot_shap_bar(ax, shap_values, feature_names, title):
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
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.tick_params(axis='both', which='major', direction='out', length=6, width=1.2)

    # 重要度を表示
    print(f'\n=== SHAP: {title} ===')
    for i in np.argsort(mean_abs)[::-1]:
        print(f'  {display[i]}: {mean_abs[i]:.4f}')


# =========================================================
# メイン
# =========================================================
os.makedirs('out', exist_ok=True)
model_name = args.model
pre = df[df[MENOPAUSE] == 0]
post = df[df[MENOPAUSE] == 1]

print(f'Model: {model_name}, CV: {args.n_splits}-fold, Seed: {args.seed}')


def run_figure(base_feats, extra_feats, suffix):
    """ROC figure + optional SHAP figure を生成"""
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    shap_data = {}
    for ax, data, key, title in [
        (axes[0], pre, 'pre', 'Premenopausal women'),
        (axes[1], post, 'post', 'Postmenopausal women'),
        (axes[2], df, 'all', 'Enrolled women'),
    ]:
        feats, shap_vals = plot_roc_panel(ax, data, title, base_feats, RISK, extra_feats)
        shap_data[key] = (feats, shap_vals)

    plt.tight_layout()
    roc_path = f'out/fig4_{model_name}{suffix}.png'
    plt.savefig(roc_path, dpi=300, bbox_inches='tight')
    print(f'\nROC saved as {roc_path}')

    # SHAP figure（閉経前/後の2パネル）
    if args.shap:
        n_panels = sum(1 for k in ['pre', 'post'] if shap_data[k][1] is not None)
        if n_panels > 0:
            fig_s, axes_s = plt.subplots(1, n_panels, figsize=(6 * n_panels, 5))
            if n_panels == 1:
                axes_s = [axes_s]
            idx = 0
            for key, title in [('pre', 'Premenopausal women'), ('post', 'Postmenopausal women')]:
                feats, shap_vals = shap_data[key]
                if shap_vals is not None:
                    plot_shap_bar(axes_s[idx], shap_vals, feats, title)
                    idx += 1
            plt.tight_layout()
            shap_path = f'out/fig4_{model_name}{suffix}_shap.png'
            plt.savefig(shap_path, dpi=300, bbox_inches='tight')
            print(f'SHAP saved as {shap_path}')


# 切除検体因子なし
run_figure(BASE_FEATURES, None, '')

# 切除検体因子あり
run_figure(BASE_FEATURES, RESECTION_FEATURES, '_resection')

if not args.noshow:
    plt.show()
