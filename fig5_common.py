"""Shared logic for Cox PH BMFS modeling (used by fig5.py and fig6.py)."""

import warnings

import numpy as np
import pandas as pd
from lifelines import CoxPHFitter
from lifelines.utils import concordance_index
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import KFold

from fig4_common import (
    BASE_FEATURES,
    RESECTION_FEATURES,
    RISK,
    TARGET,
    load_data,
)

warnings.filterwarnings('ignore')

TIME_COL = 'BMFS'
TIME_POINTS = [12, 36, 60]
TIME_LABELS = ['1-year', '3-year', '5-year']


def load_with_time():
    """xlsx 特徴量 + csv の BMFS 時間 を merge."""
    df = load_data()
    csv = pd.read_csv('data/osteoporosis_bone_meta.csv')
    csv = csv.dropna(subset=['研究ID']).drop_duplicates(subset=['研究ID'])
    df = df.merge(csv[['研究ID', TIME_COL]], on='研究ID', how='left')
    return df


def get_features(with_resection=False):
    feats = BASE_FEATURES + [RISK]
    if with_resection:
        feats = feats + RESECTION_FEATURES
    return feats


def prepare_data(with_resection=False):
    df = load_with_time()
    feats = get_features(with_resection)
    cols = feats + [TIME_COL, TARGET]
    data = df[cols].dropna().reset_index(drop=True)
    return data, feats


def fit_cox(data, features, penalizer=0.01):
    cols = features + [TIME_COL, TARGET]
    cph = CoxPHFitter(penalizer=penalizer)
    cph.fit(data[cols], duration_col=TIME_COL, event_col=TARGET)
    return cph


def cv_oof(data, features, time_points=TIME_POINTS, n_splits=5, seed=42, penalizer=0.01):
    """Return out-of-fold partial hazard scores and survival probabilities at time_points."""
    cols = features + [TIME_COL, TARGET]
    n = len(data)
    risk = np.zeros(n)
    surv = np.full((n, len(time_points)), np.nan)

    kf = KFold(n_splits=n_splits, shuffle=True, random_state=seed)
    for tr, te in kf.split(data):
        cph = CoxPHFitter(penalizer=penalizer)
        cph.fit(data.iloc[tr][cols], duration_col=TIME_COL, event_col=TARGET)
        risk[te] = cph.predict_partial_hazard(data.iloc[te][features]).values
        sf = cph.predict_survival_function(data.iloc[te][features], times=time_points)
        # sf: index=time_points, columns=row index of test set
        surv[te, :] = sf.T.values
    return risk, surv


def time_metrics(times, events, risk, surv, time_points=TIME_POINTS):
    """Return C-index plus per-time-point AUC."""
    c_idx = concordance_index(times, -risk, events)
    aucs = {}
    for i, t in enumerate(time_points):
        case = (events == 1) & (times <= t)
        ctrl = (times >= t) & ~case
        usable = case | ctrl
        y = case[usable].astype(int)
        s = risk[usable]
        if y.sum() > 0 and len(np.unique(y)) > 1:
            aucs[t] = roc_auc_score(y, s)
        else:
            aucs[t] = np.nan
    return c_idx, aucs
