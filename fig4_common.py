import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.ticker import MultipleLocator
from scipy.stats import norm

# --- Arialフォント ---
arial_path = 'data/fonts/arial.ttf'
arial_prop = fm.FontProperties(fname=arial_path)
plt.rcParams['font.family'] = arial_prop.get_name()
fm.fontManager.addfont(arial_path)

# --- Matplotlibスタイル ---
plt.rcParams['font.size'] = 12
plt.rcParams['axes.labelsize'] = 14
plt.rcParams['xtick.labelsize'] = 12
plt.rcParams['ytick.labelsize'] = 12
plt.rcParams['legend.fontsize'] = 11

# --- カラム名 ---
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
    '閉経あり=1': 'Menopause',
}


def load_data():
    df = pd.read_excel('data/fig4/enrolled_patients_20260322.xlsx')
    df = df[df['Exclude'] == 0].copy()
    for col in BASE_FEATURES + [RISK] + RESECTION_FEATURES + [TARGET, MENOPAUSE]:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    return df


def get_features(resection=False):
    feats = BASE_FEATURES[:]
    if resection:
        feats += RESECTION_FEATURES
    return feats


def style_ax(ax):
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.tick_params(axis='both', which='major', direction='out', length=6, width=1.2)
    ax.tick_params(axis='both', which='minor', direction='out', length=3, width=1)


def style_roc_ax(ax):
    style_ax(ax)
    ax.set_xlabel('1 - Specificity')
    ax.set_ylabel('Sensitivity')
    ax.set_xlim([0, 1])
    ax.set_ylim([0, 1])
    ax.xaxis.set_major_locator(MultipleLocator(0.2))
    ax.xaxis.set_minor_locator(MultipleLocator(0.1))
    ax.yaxis.set_major_locator(MultipleLocator(0.2))
    ax.yaxis.set_minor_locator(MultipleLocator(0.1))


def delong_test(y_true, y_score1, y_score2):
    """DeLong test for comparing two correlated AUROCs."""
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
