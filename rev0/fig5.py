"""Fig5: Cox PH nomogram for bone metastasis-free survival (BMFS).

Endpoint: BMFS_Event (bone metastasis or death, composite — same as Fig4).
Time points: 1 / 3 / 5 year BMFS probability.
"""

import argparse
import os

import matplotlib.pyplot as plt
import numpy as np

from fig4_common import DISPLAY_NAMES
from fig5_common import (
    TARGET,
    TIME_COL,
    TIME_LABELS,
    TIME_POINTS,
    cv_oof,
    fit_cox,
    prepare_data,
    time_metrics,
)

parser = argparse.ArgumentParser()
parser.add_argument('--noshow', action='store_true')
parser.add_argument('--with-resection', action='store_true',
                    help='Include resection-derived features (reduces N)')
parser.add_argument('--n-splits', type=int, default=5)
parser.add_argument('--seed', type=int, default=42)
args = parser.parse_args()


# =========================================================
# Nomogram math
# =========================================================
def feature_axis_values(data, feat):
    """Return tick values used to label a feature axis on the nomogram."""
    s = data[feat].dropna()
    uniq = np.sort(s.unique())
    # treat as categorical/ordinal if <= 6 distinct values
    if len(uniq) <= 6:
        return uniq
    lo, hi = float(s.min()), float(s.max())
    # 5 round-number ticks
    span = hi - lo
    step = 10 ** np.floor(np.log10(span / 4))
    candidates = [step, step * 2, step * 2.5, step * 5, step * 10]
    step = min(candidates, key=lambda c: abs((span / c) - 4))
    start = np.ceil(lo / step) * step
    ticks = np.arange(start, hi + step / 2, step)
    return ticks


def compute_nomogram_table(cph, data, features):
    """For each feature compute (β, x_min, x_max, contribution, ticks)."""
    coefs = cph.params_  # Series indexed by feature
    table = []
    for f in features:
        beta = float(coefs[f])
        s = data[f].dropna()
        x_min, x_max = float(s.min()), float(s.max())
        contrib = beta * (x_max - x_min)  # signed
        ticks = feature_axis_values(data, f)
        table.append({
            'feat': f,
            'beta': beta,
            'x_min': x_min,
            'x_max': x_max,
            'contrib': contrib,
            'ticks': ticks,
        })
    # The variable with the largest |contrib| spans 100 points
    max_abs = max(abs(t['contrib']) for t in table)
    for t in table:
        # points(x) = 100 * β*(x - x_ref) / max_abs   (x_ref minimizes points)
        if t['beta'] >= 0:
            t['x_ref'] = t['x_min']
        else:
            t['x_ref'] = t['x_max']
        t['points_per_unit'] = 100 * t['beta'] / max_abs
    return table, max_abs


def baseline_survival(cph, t):
    """S0(t) for the baseline (mean covariate = 0 in centered form)."""
    bs = cph.baseline_survival_
    # bs index is time; find S at t (use the value at the largest time <= t)
    idx = bs.index.values
    s = bs.iloc[:, 0].values
    # Reference baseline survival from lifelines is at "baseline" which uses mean covariates
    # We need the LP-anchored survival. Below we compute via LP shift.
    if t <= idx.min():
        return float(s[0])
    if t >= idx.max():
        return float(s[-1])
    i = np.searchsorted(idx, t, side='right') - 1
    return float(s[i])


def survival_from_lp(cph, lp_centered_diff, t):
    """S(t | LP centered to mean) = S0(t)^exp(LP_diff)."""
    s0 = baseline_survival(cph, t)
    return s0 ** np.exp(lp_centered_diff)


# =========================================================
# Drawing
# =========================================================
def draw_nomogram(cph, data, features, out_path):
    table, max_abs = compute_nomogram_table(cph, data, features)
    # LP at all-x_ref (each var contributes its minimum points)
    lp_at_ref = sum(t['beta'] * t['x_ref'] for t in table)
    # mean LP (used by baseline_survival)
    mean_x = {f: float(data[f].mean()) for f in features}
    lp_mean = sum(t['beta'] * mean_x[t['feat']] for t in table)

    # total_points <-> LP linear map:
    # total_points = sum_j 100*β_j*(x_j - x_ref_j)/max_abs
    #              = (100/max_abs) * (LP - lp_at_ref)
    # so LP = lp_at_ref + total_points * max_abs / 100
    max_total = sum(abs(t['contrib']) for t in table) * 100 / max_abs  # = sum(|β*range|*100/max_abs)

    # Layout
    n_feat = len(features)
    # rows: Points, n_feat features, Total Points, 1y, 3y, 5y
    n_rows = 1 + n_feat + 1 + len(TIME_POINTS)
    row_h = 0.55
    fig_h = max(6, row_h * n_rows + 1.5)
    fig, ax = plt.subplots(figsize=(11, fig_h))
    ax.set_xlim(-0.18, 1.05)
    ax.set_ylim(0, n_rows + 0.5)
    ax.axis('off')

    # y positions: top to bottom
    def yrow(i):
        return n_rows - i  # row 0 at top

    # ---- Points axis (0–100) ----
    pts = np.arange(0, 101, 10)
    draw_axis(ax, yrow(0), 0, 1, ticks=pts / 100,
              labels=[str(int(v)) for v in pts],
              left_label='Points')

    # ---- Feature axes ----
    for i, t in enumerate(table, start=1):
        # map feature value -> [0, 1] x position (relative to 100-point range)
        # x_in_points = points_per_unit * (x - x_ref)
        # frac = x_in_points / 100
        ticks = t['ticks']
        positions = (t['points_per_unit'] * (ticks - t['x_ref'])) / 100
        # may be negative for negative β; clip into [0,1] for drawing? Negative β means the right end is x_min
        # but our parameterization sets x_ref so that positions are >= 0
        labels = [_fmt_tick(v) for v in ticks]
        draw_axis(ax, yrow(i), 0, 1, ticks=positions, labels=labels,
                  left_label=DISPLAY_NAMES.get(t['feat'], t['feat']))

    # ---- Total Points axis ----
    tp_row = 1 + n_feat
    tp_step = _nice_step(max_total, 8)
    tp_ticks = np.arange(0, max_total + tp_step / 2, tp_step)
    draw_axis(ax, yrow(tp_row), 0, 1,
              ticks=tp_ticks / max_total,
              labels=[str(int(round(v))) for v in tp_ticks],
              left_label='Total Points')

    # ---- Survival probability axes ----
    for k, (t_pt, label) in enumerate(zip(TIME_POINTS, TIME_LABELS)):
        tp_grid = np.linspace(0, max_total, 400)
        lp_grid = lp_at_ref + tp_grid * max_abs / 100
        s_grid = baseline_survival(cph, t_pt) ** np.exp(lp_grid - lp_mean)
        s_min, s_max = float(s_grid.min()), float(s_grid.max())

        # Choose tick step adaptively so we get ~6–10 ticks across the range
        span = s_max - s_min
        for step in (0.01, 0.02, 0.05, 0.1, 0.2):
            if span / step <= 10:
                break
        p_ticks = []
        p = np.ceil(s_min / step - 1e-9) * step
        while p <= s_max + 1e-9:
            if 0.0 < p < 1.0:
                p_ticks.append(round(p, 6))
            p += step

        positions, labels = [], []
        fmt = '{:.2f}' if step < 0.1 else '{:.1f}'
        for p in p_ticks:
            tp_at_p = np.interp(p, s_grid[::-1], tp_grid[::-1])
            positions.append(tp_at_p / max_total)
            labels.append(fmt.format(p + 0.0))
        row = tp_row + 1 + k
        draw_axis(ax, yrow(row), 0, 1, ticks=positions, labels=labels,
                  left_label=f'{label} BMFS', min_gap=0.018)

    title = 'Nomogram for bone metastasis-free survival'
    if args.with_resection:
        title += ' (with resection features)'
    ax.set_title(title, fontsize=14, pad=14)

    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    print(f'Saved: {out_path}')


def draw_axis(ax, y, x0, x1, ticks, labels, left_label, min_gap=0.025):
    ax.plot([x0, x1], [y, y], color='black', lw=1.0)
    pairs = [(float(t), l) for t, l in zip(ticks, labels)
             if x0 - 0.005 <= float(t) <= x1 + 0.005]
    pairs.sort(key=lambda p: p[0])
    last_label_x = -np.inf
    for tk, lab in pairs:
        ax.plot([tk, tk], [y - 0.12, y + 0.12], color='black', lw=0.8)
        if tk - last_label_x >= min_gap:
            ax.text(tk, y + 0.18, lab, ha='center', va='bottom', fontsize=8)
            last_label_x = tk
    ax.text(-0.02, y, left_label, ha='right', va='center', fontsize=10)


def _fmt_tick(v):
    if float(v).is_integer():
        return str(int(v))
    return f'{v:.2g}'


def _nice_step(span, n_target):
    raw = span / n_target
    if raw <= 0:
        return 1
    mag = 10 ** np.floor(np.log10(raw))
    for m in (1, 2, 2.5, 5, 10):
        if raw <= m * mag:
            return m * mag
    return 10 * mag


# =========================================================
# Main
# =========================================================
def main():
    data, feats = prepare_data(with_resection=args.with_resection)
    print(f'Features: {len(feats)} | N = {len(data)} | Events = {int(data[TARGET].sum())}')

    cph = fit_cox(data, feats)
    print('\n=== Cox PH summary ===')
    print(cph.summary[['coef', 'exp(coef)', 'p']].round(4).to_string())

    print('\n=== CV metrics (KFold n_splits={}) ==='.format(args.n_splits))
    risk, _ = cv_oof(data, feats, n_splits=args.n_splits, seed=args.seed)
    times = data[TIME_COL].values
    events = data[TARGET].values.astype(int)
    c_idx, aucs = time_metrics(times, events, risk, None)
    print(f'C-index: {c_idx:.3f}')
    for t, label in zip(TIME_POINTS, TIME_LABELS):
        print(f'{label} AUC: {aucs[t]:.3f}')

    os.makedirs('out/rev0', exist_ok=True)
    suffix = '_with_resection' if args.with_resection else ''
    out_path = f'out/rev0/fig5_nomogram{suffix}.png'
    draw_nomogram(cph, data, feats, out_path)

    if not args.noshow:
        plt.show()


if __name__ == '__main__':
    main()
