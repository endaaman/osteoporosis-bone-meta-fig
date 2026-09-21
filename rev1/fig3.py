"""Revise 1: Figure 3 (rev0 の Figure 2 = Kaplan-Meier 曲線) を新カットオフで再作成。

データ: data/revise1/REVISE_MEDCOMM_KM_遠田20260921.xlsx (Sheet1, 785 行)
    研究ID / menopause (0=pre, 1=post) / AI_P / RO group ('Low'/'High') / BMFS_Event / BMFS
パネル: A Enrolled women / B Premenopausal / C Postmenopausal
    B, C には Cox 単変量 HR (HRO vs LRO), 95% CI, log-rank p を凡例タイトルに載せる。

実行: uv run python rev1/fig3.py   -> out/rev1/fig3.{png,pdf,tiff}
"""
import os
import sys

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from matplotlib.transforms import blended_transform_factory
from lifelines import KaplanMeierFitter, CoxPHFitter
from lifelines.statistics import logrank_test

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

XLSX = 'data/revise1/REVISE_MEDCOMM_KM_遠田20260921.xlsx'
CSV = 'data/osteoporosis_bone_meta.csv'  # rev0 のデータ。突き合わせ用 (無ければスキップ)

# 著者提供の統計値 (2026-09-15 メール、旧 KM データ時点)。突き合わせ用に残す。図は常に計算値。
PROVIDED = {
    'Premenopausal women': dict(hr=1.91, lo=1.01, hi=3.59, p=0.04, use_provided=False),
    'Postmenopausal women': dict(hr=0.84, lo=0.46, hi=1.51, p=0.56, use_provided=False),
}

COLORS = {'LRO': common.COLOR_LRO, 'HRO': common.COLOR_HRO}
# 表は rev0 (lifelines add_at_risk_counts) と同じ 10 か月刻み 7 列。
TABLE_TIMES = [0, 10, 20, 30, 40, 50, 60]
# 表に出す行 (rev0 と同じ 3 行)。
TABLE_ROWS = ['At risk', 'Censored', 'Events']
TABLE_FONTSIZE = 8
XMAX = 65.5  # rev0 と同じ (右に余白)
TABLE_LABEL_RIGHT = -6.5   # 行ラベル (LRO/HRO, At risk 等) の右端, データ座標 (月)
TABLE_LABEL_LEFT = -19.5   # 表見出し / グループ見出しの左端, データ座標 (月)

# ---- レイアウト (mm) ----
FIG_W = common.FULL_WIDTH_MM
PANEL_LEFT = 15.5   # 各パネルの左余白 (y ラベル + パネルラベル)
PANEL_GAP = 4.0     # パネル間の追加余白
AX_W = 37.0         # 軸の幅 (bbox_inches='tight' + pad で出力幅が ~170 mm になる値)
AX_H = 42.0         # 軸の高さ
TOP = 7.0           # タイトル/パネルラベルの余白
XLABEL_GAP = 13.0   # 軸下端から表の 1 行目まで (x 目盛 + x ラベル + 余白)
LINE_MM = 4.2       # 表の行ピッチ
GROUP_GAP_MM = 3.0  # グループ間の余白 (3 行表示のときのみ)
BOTTOM = 3.0


def table_height_mm():
    if len(TABLE_ROWS) == 1:
        return 3 * LINE_MM  # 見出し + LRO + HRO
    return 2 * (1 + len(TABLE_ROWS)) * LINE_MM + GROUP_GAP_MM


FIG_H = TOP + AX_H + XLABEL_GAP + table_height_mm() + BOTTOM


def load():
    df = pd.read_excel(XLSX, sheet_name='Sheet1')
    df.columns = [str(c).strip() for c in df.columns]
    for c in df.columns:
        if df[c].dtype == object:
            df[c] = df[c].str.strip()
    df = df[['研究ID', 'menopause', 'AI_P', 'RO group', 'BMFS_Event', 'BMFS']].copy()
    assert df['研究ID'].is_unique
    assert df['RO group'].isin(['Low', 'High']).all(), df['RO group'].unique()
    df['risk_group'] = df['RO group'].map({'Low': 'LRO', 'High': 'HRO'})
    assert df[['menopause', 'BMFS_Event', 'BMFS']].notna().all().all()
    return df


def report_cutoff(df):
    print('\n=== RO group vs AI_P cutoff ===')
    for m, name in [(0, 'Premenopausal'), (1, 'Postmenopausal')]:
        d = df[df['menopause'] == m]
        lo = d[d['risk_group'] == 'LRO']['AI_P']
        hi = d[d['risk_group'] == 'HRO']['AI_P']
        thr = hi.min()
        pred = np.where(d['AI_P'] >= thr, 'HRO', 'LRO')
        ok = (pred == d['risk_group']).all()
        print(f'{name}: Low max={lo.max():.3f}, High min={thr:.3f} '
              f'-> rule "High iff AI_P >= {thr:.3f}" consistent={ok}')
    lo_all = df[df['risk_group'] == 'LRO']['AI_P'].max()
    hi_all = df[df['risk_group'] == 'HRO']['AI_P'].min()
    print(f'Pooled: Low max={lo_all:.3f}, High min={hi_all:.3f} '
          f'(overlap -> no single pooled threshold)')


def crosscheck_csv(df):
    if not os.path.exists(CSV):
        print(f'\n(skip csv cross-check: {CSV} not found)')
        return
    csv = pd.read_csv(CSV)
    csv.columns = [str(c).strip() for c in csv.columns]
    m = df.merge(csv[['研究ID', 'menopause', 'AI_P', 'Cehst xray score', 'BMFS_Event', 'BMFS']],
                 on='研究ID', how='left', suffixes=('', '_csv'), indicator=True)
    print('\n=== cross-check with rev0 csv (join on 研究ID) ===')
    print('unmatched IDs:', int((m['_merge'] != 'both').sum()))
    for c in ['menopause', 'BMFS_Event', 'BMFS']:
        print(f'{c} mismatches:', int((m[c] != m[c + "_csv"]).sum()))
    print('AI_P mismatches:', int(((m['AI_P'] - m['AI_P_csv']).abs() > 1e-9).sum()))
    m['old_group'] = m['Cehst xray score'].str.strip().map({'Low': 'LRO', 'High': 'HRO'})
    print('rev0 group (rows) vs new group (cols), by menopause:')
    print(pd.crosstab([m['menopause'], m['old_group']], m['risk_group']))


def compute_stats(data):
    d = data.copy()
    d['hro'] = (d['risk_group'] == 'HRO').astype(int)
    lro, hro = d[d.hro == 0], d[d.hro == 1]
    lr = logrank_test(lro['BMFS'], hro['BMFS'], lro['BMFS_Event'], hro['BMFS_Event'])
    cph = CoxPHFitter().fit(d[['BMFS', 'BMFS_Event', 'hro']], 'BMFS', 'BMFS_Event')
    s = cph.summary.loc['hro']
    return dict(
        n_lro=len(lro), ev_lro=int(lro['BMFS_Event'].sum()),
        n_hro=len(hro), ev_hro=int(hro['BMFS_Event'].sum()),
        logrank_p=lr.p_value,
        hr=s['exp(coef)'], lo=s['exp(coef) lower 95%'], hi=s['exp(coef) upper 95%'],
        wald_p=s['p'],
    )


def at_risk_table(data, group):
    """rev0 (lifelines add_at_risk_counts) と同じ意味の数: 時点 t で
    At risk = T >= t の人数, Censored/Events = T < t の累積。"""
    d = data[data['risk_group'] == group]
    T, E = d['BMFS'].values, d['BMFS_Event'].values
    rows = {'At risk': [], 'Censored': [], 'Events': []}
    for t in TABLE_TIMES:
        rows['At risk'].append(int((T >= t).sum()))
        rows['Censored'].append(int(((T < t) & (E == 0)).sum()))
        rows['Events'].append(int(((T < t) & (E == 1)).sum()))
    return {k: rows[k] for k in TABLE_ROWS}


def fmt_p(p):
    return 'p < 0.01' if p < 0.01 else f'p = {p:.2f}'


def plot_km_panel(ax, data, title):
    print(f'\n=== {title} ===')
    st = compute_stats(data)
    print(f"LRO: n={st['n_lro']}, events={st['ev_lro']}")
    print(f"HRO: n={st['n_hro']}, events={st['ev_hro']}")
    print(f"Log-rank p = {st['logrank_p']:.4f}")
    print(f"Cox HR (HRO vs LRO) = {st['hr']:.3f} (95% CI {st['lo']:.3f}-{st['hi']:.3f}), "
          f"Wald p = {st['wald_p']:.4f}")

    # KM 曲線 (rev0 と同じ見た目)
    for group in ['LRO', 'HRO']:
        mask = data['risk_group'] == group
        kmf = KaplanMeierFitter()
        kmf.fit(data[mask]['BMFS'], data[mask]['BMFS_Event'], label=f'{group} (n={mask.sum()})')
        kmf.plot(ax=ax, ci_show=False, show_censors=True,
                 censor_styles={'ms': 5, 'marker': '|', 'mew': 0.8},
                 color=COLORS[group], linewidth=1.0)

    # 凡例タイトル: p 値 (+ B, C は HR)
    lines = [fmt_p(st['logrank_p'])]
    if title in PROVIDED:
        pv = PROVIDED[title]
        if pv['use_provided']:
            hr, lo, hi, p = pv['hr'], pv['lo'], pv['hi'], pv['p']
            print(f"  -> figure uses AUTHOR-PROVIDED values: HR {hr:.2f} ({lo:.2f}-{hi:.2f}), p = {p:.2f}")
            lines = [fmt_p(p)]
        else:
            hr, lo, hi = st['hr'], st['lo'], st['hi']
            print(f"  -> figure uses computed values (provided: HR {pv['hr']:.2f} "
                  f"({pv['lo']:.2f}-{pv['hi']:.2f}), p = {pv['p']:.2f})")
        lines += [f'HR {hr:.2f}', f'95% CI {lo:.2f}–{hi:.2f}']
    legend_title = '\n'.join(lines)

    ax.set_title(title)
    ax.set_xlabel('Months after surgery')
    ax.set_ylabel('Bone metastasis-free ratio')
    ax.set_xlim([0, XMAX])
    ax.set_ylim([0, 1])
    ax.yaxis.set_major_locator(MultipleLocator(0.2))
    ax.yaxis.set_minor_locator(MultipleLocator(0.1))
    ax.xaxis.set_major_locator(MultipleLocator(20))
    ax.xaxis.set_minor_locator(MultipleLocator(10))
    ax.tick_params(axis='both', which='major', direction='out', length=3.5)
    ax.tick_params(axis='both', which='minor', direction='out', length=2)
    leg = ax.legend(loc='lower left', title=legend_title, frameon=True, edgecolor='black',
                    fancybox=False, framealpha=1.0, borderpad=0.6, handlelength=1.8,
                    alignment='left')
    leg.get_title().set_multialignment('left')

    # Number at risk 表 (自前描画: x はデータ座標, y は軸下の mm)
    trans = blended_transform_factory(ax.transData, ax.transAxes)
    kw = dict(transform=trans, fontsize=TABLE_FONTSIZE, va='top')
    y_mm = -XLABEL_GAP
    print('\nNumber at risk table (t = %s):' % TABLE_TIMES)
    if len(TABLE_ROWS) == 1:
        # 簡易版: 見出し 1 行 + 群ごとに 1 行
        ax.text(TABLE_LABEL_LEFT, y_mm / AX_H, 'Number at risk', ha='left', **kw)
        y_mm -= LINE_MM
        for group in ['LRO', 'HRO']:
            vals = at_risk_table(data, group)[TABLE_ROWS[0]]
            ax.text(TABLE_LABEL_RIGHT, y_mm / AX_H, group, ha='right', **kw)
            for t, v in zip(TABLE_TIMES, vals):
                ax.text(t, y_mm / AX_H, str(v), ha='center', **kw)
            print(f'  {group} {TABLE_ROWS[0]:9s}: {vals}')
            y_mm -= LINE_MM
    else:
        # rev0 (lifelines add_at_risk_counts) 風: 群見出し + 行
        for group in ['LRO', 'HRO']:
            n = (data['risk_group'] == group).sum()
            ax.text(TABLE_LABEL_LEFT, y_mm / AX_H, f'{group} (n={n})', ha='left', **kw)
            y_mm -= LINE_MM
            for label, vals in at_risk_table(data, group).items():
                ax.text(TABLE_LABEL_RIGHT, y_mm / AX_H, label, ha='right', **kw)
                for t, v in zip(TABLE_TIMES, vals):
                    ax.text(t, y_mm / AX_H, str(v), ha='center', **kw)
                print(f'  {group} {label:9s}: {vals}')
                y_mm -= LINE_MM
            y_mm -= GROUP_GAP_MM
    return st


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--cutoff', type=float, default=None,
                    help='RO group 列を使わず AI_P >= cutoff を HRO とする (試算用。既定は xlsx の RO group 列)')
    ap.add_argument('--name', default=None, help='出力ファイル名 (既定 fig3)')
    args = ap.parse_args()

    common.setup()
    df = load()
    out_name = args.name or 'fig3'
    if args.cutoff is not None:
        df['risk_group'] = np.where(df['AI_P'] >= args.cutoff, 'HRO', 'LRO')
        df['RO group'] = df['risk_group'].map({'LRO': 'Low', 'HRO': 'High'})
        out_name = args.name or f"fig3_cut{args.cutoff:g}".replace('.', 'p')
        print(f'*** grouping: AI_P >= {args.cutoff:.3f} -> HRO  (output {out_name})')
    else:
        # 既定: xlsx の RO group 列 (著者のカットオフ: 閉経前 DXA コホートの Youden index, RO 0.1)。rev1/cutoff.py 参照
        print('*** grouping: RO group column of the xlsx')
    print(f'rows={len(df)}  ' + ', '.join(f'{k}={v}' for k, v in df['risk_group'].value_counts().items()))
    report_cutoff(df)
    crosscheck_csv(df)

    fig = plt.figure(figsize=(common.mm(FIG_W), common.mm(FIG_H)))
    panels = [
        ('A', 'Enrolled women', df),
        ('B', 'Premenopausal women', df[df['menopause'] == 0]),
        ('C', 'Postmenopausal women', df[df['menopause'] == 1]),
    ]
    results = {}
    for i, (label, title, data) in enumerate(panels):
        left = i * (PANEL_LEFT + AX_W + PANEL_GAP) + PANEL_LEFT
        bottom = FIG_H - TOP - AX_H
        ax = fig.add_axes([left / FIG_W, bottom / FIG_H, AX_W / FIG_W, AX_H / FIG_H])
        results[title] = plot_km_panel(ax, data.copy(), title)
        common.panel_label(ax, label, dx=-14.5 / AX_W, dy=1.0)

    print('\n=== summary (computed) ===')
    for title, st in results.items():
        print(f"{title}: LRO n={st['n_lro']}/ev={st['ev_lro']}, HRO n={st['n_hro']}/ev={st['ev_hro']}, "
              f"log-rank p={st['logrank_p']:.3f}, HR={st['hr']:.2f} ({st['lo']:.2f}-{st['hi']:.2f}), "
              f"Wald p={st['wald_p']:.3f}")
    print(f'figure size: {FIG_W} x {FIG_H:.1f} mm')
    common.save(fig, out_name)


if __name__ == '__main__':
    main()
