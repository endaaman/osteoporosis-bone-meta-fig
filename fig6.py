"""Fig6: Time-dependent ROC + calibration plots for the Cox PH BMFS model.

Outputs:
    out/fig6_roc.png         (single ROC panel with 1y/3y/5y curves)
    out/fig6_calibration.png (3 panels, one per time point)
"""

import argparse
import os

import matplotlib.pyplot as plt
import numpy as np
from lifelines import KaplanMeierFitter
from sklearn.metrics import roc_auc_score, roc_curve

from fig4_common import style_roc_ax
from fig5_common import (
    TARGET,
    TIME_COL,
    TIME_LABELS,
    TIME_POINTS,
    cv_oof,
    prepare_data,
)

parser = argparse.ArgumentParser()
parser.add_argument('--noshow', action='store_true')
parser.add_argument('--with-resection', action='store_true')
parser.add_argument('--n-splits', type=int, default=5)
parser.add_argument('--seed', type=int, default=42)
parser.add_argument('--n-groups', type=int, default=5,
                    help='Number of risk groups for calibration (default: 5)')
args = parser.parse_args()

COLORS = {12: '#4A7BA7', 36: '#C44E52', 60: '#5B9856'}


# =========================================================
# Time-dependent ROC
# =========================================================
def plot_roc(ax, times, events, risk):
    for t, label in zip(TIME_POINTS, TIME_LABELS):
        case = (events == 1) & (times <= t)
        ctrl = (times >= t) & ~case
        usable = case | ctrl
        y = case[usable].astype(int)
        s = risk[usable]
        if y.sum() == 0 or len(np.unique(y)) < 2:
            continue
        fpr, tpr, _ = roc_curve(y, s)
        auc_val = roc_auc_score(y, s)
        ax.plot(fpr, tpr, color=COLORS[t], lw=2,
                label=f'{label} (AUC = {auc_val:.3f})')
    ax.plot([0, 1], [0, 1], 'k--', lw=1, alpha=0.5)
    ax.set_title('Time-dependent ROC (5-fold CV)')
    style_roc_ax(ax)
    ax.legend(loc='lower right', frameon=True, edgecolor='black', fancybox=False)


# =========================================================
# Calibration plot
# =========================================================
def calibration_one(ax, times, events, surv_pred_t, t_pt, label, n_groups):
    """Group patients by predicted P(event by t), compute KM-observed in each group."""
    pred_event_prob = 1.0 - surv_pred_t  # predicted probability of event by t

    # Quantile groups
    quantiles = np.linspace(0, 1, n_groups + 1)
    edges = np.quantile(pred_event_prob, quantiles)
    edges[0] = -np.inf
    edges[-1] = np.inf

    pred_means, obs_probs, obs_lower, obs_upper, ns = [], [], [], [], []
    for i in range(n_groups):
        mask = (pred_event_prob > edges[i]) & (pred_event_prob <= edges[i + 1])
        if mask.sum() < 5:
            continue
        kmf = KaplanMeierFitter()
        kmf.fit(times[mask], events[mask])
        # observed S(t)
        s_at_t = float(kmf.survival_function_at_times([t_pt]).iloc[0])
        obs = 1.0 - s_at_t
        # CI from KM (use Greenwood approximation built into lifelines)
        ci = kmf.confidence_interval_survival_function_
        if t_pt in ci.index:
            ci_row = ci.loc[t_pt]
        else:
            idx = ci.index.values
            j = np.searchsorted(idx, t_pt, side='right') - 1
            j = max(0, min(j, len(idx) - 1))
            ci_row = ci.iloc[j]
        s_lo, s_hi = float(ci_row.iloc[0]), float(ci_row.iloc[1])
        pred_means.append(pred_event_prob[mask].mean())
        obs_probs.append(obs)
        obs_lower.append(1.0 - s_hi)
        obs_upper.append(1.0 - s_lo)
        ns.append(int(mask.sum()))

    pred_means = np.array(pred_means)
    obs_probs = np.array(obs_probs)
    obs_lower = np.clip(np.array(obs_lower), 0, 1)
    obs_upper = np.clip(np.array(obs_upper), 0, 1)
    yerr = np.vstack([obs_probs - obs_lower, obs_upper - obs_probs])

    ax.errorbar(pred_means, obs_probs, yerr=yerr,
                fmt='o', color=COLORS[t_pt], ecolor=COLORS[t_pt],
                capsize=3, ms=6, lw=1.2)
    # Diagonal reference
    lim_max = max(pred_means.max(), obs_probs.max(), 0.05) * 1.15
    lim_max = min(lim_max, 1.0)
    ax.plot([0, lim_max], [0, lim_max], 'k--', lw=1, alpha=0.5)

    ax.set_xlim(0, lim_max)
    ax.set_ylim(0, lim_max)
    ax.set_xlabel('Predicted probability')
    ax.set_ylabel('Observed probability')
    ax.set_title(f'{label} calibration')
    ax.set_aspect('equal', adjustable='box')
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.tick_params(axis='both', which='major', direction='out', length=6, width=1.2)


def plot_calibration(times, events, surv, suffix):
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    for ax, t_pt, label in zip(axes, TIME_POINTS, TIME_LABELS):
        col_idx = TIME_POINTS.index(t_pt)
        calibration_one(ax, times, events, surv[:, col_idx], t_pt, label, args.n_groups)
    plt.tight_layout()
    out_path = f'out/fig6_calibration{suffix}.png'
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    print(f'Saved: {out_path}')


def plot_roc_panel(times, events, risk, suffix):
    fig, ax = plt.subplots(figsize=(6, 5.5))
    plot_roc(ax, times, events, risk)
    plt.tight_layout()
    out_path = f'out/fig6_roc{suffix}.png'
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    print(f'Saved: {out_path}')


# =========================================================
# Main
# =========================================================
def main():
    data, feats = prepare_data(with_resection=args.with_resection)
    print(f'Features: {len(feats)} | N = {len(data)} | Events = {int(data[TARGET].sum())}')

    risk, surv = cv_oof(data, feats, n_splits=args.n_splits, seed=args.seed)
    times = data[TIME_COL].values
    events = data[TARGET].values.astype(int)

    os.makedirs('out', exist_ok=True)
    suffix = '_with_resection' if args.with_resection else ''

    plot_roc_panel(times, events, risk, suffix)
    plot_calibration(times, events, surv, suffix)

    if not args.noshow:
        plt.show()


if __name__ == '__main__':
    main()
