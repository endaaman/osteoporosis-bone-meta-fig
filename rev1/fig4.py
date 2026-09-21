"""
Revise 1 新 Figure 4: Age vs Risk of osteoporosis (RO = AI_P) の散布図。

A: 全患者 / B: 閉経前 / C: 閉経後。各パネルに n, r, p を表示。
著者提供値 (Pearson): A r=0.61 n=785 / B r=0.21 n=325 / C r=0.45 n=460 (いずれも p<0.01)。

出力 (out/rev1/):
    fig4_ab   … A, B の 2 パネル (C を使わない場合)
    fig4_abc  … A, B, C の 3 パネル

実行: uv run python rev1/fig4.py
図に載せる係数は既定で Spearman (rs)。docs/revise1/fig4.md 参照。
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from scipy.stats import pearsonr, spearmanr

import common

XLSX = 'data/revise1/REVISE _MEDCIMM _AGE _RO_遠田.xlsx'
CSV = 'data/osteoporosis_bone_meta.csv'

PANELS = [
    # (label, sheet, title, CSV subset)
    ('A', 'Age_RO_全患者', 'All enrolled women', lambda d: d),
    ('B', 'Age_RO_閉経前', 'Premenopausal women', lambda d: d[d['menopause'] == 0]),
    ('C', 'Age_RO_閉経後', 'Postmenopausal women', lambda d: d[d['menopause'] == 1]),
]

# 著者提供値 (Excel CORREL = Pearson)
PROVIDED = {'A': (0.61, 785), 'B': (0.21, 325), 'C': (0.45, 460)}

XLIM = (20, 92)
YLIM = (-0.03, 1.03)


def load_sheet(sheet):
    """先頭 2 列 (Age, AI_P/RO) だけ読む。E-H 列の Excel 数式は無視して自前で計算する。"""
    df = pd.read_excel(XLSX, sheet_name=sheet, usecols=[0, 1])
    df.columns = ['Age', 'RO']
    for c in df.columns:
        if df[c].dtype == object:
            df[c] = df[c].astype(str).str.strip()
        df[c] = pd.to_numeric(df[c], errors='coerce')
    n_raw = len(df)
    df = df.dropna().reset_index(drop=True)
    if len(df) != n_raw:
        print(f'  [{sheet}] dropped {n_raw - len(df)} non-numeric/empty rows')
    return df


def load_csv():
    df = pd.read_csv(CSV)
    df = df[df['Exclude'] == 0].copy()
    df['Age'] = pd.to_numeric(df['Age'], errors='coerce')
    df['RO'] = pd.to_numeric(df['AI_P'], errors='coerce')
    return df[['Age', 'RO', 'menopause']].dropna(subset=['Age', 'RO'])


def same_multiset(a, b):
    """(Age, RO) ペアの多重集合として一致するか。"""
    ka = sorted(zip(a['Age'].round(6), a['RO'].round(6)))
    kb = sorted(zip(b['Age'].round(6), b['RO'].round(6)))
    return ka == kb


def stats(df):
    r, p = pearsonr(df['Age'], df['RO'])
    rho, p_s = spearmanr(df['Age'], df['RO'])
    return dict(n=len(df), r=r, p=p, rho=rho, p_s=p_s)


def fmt_p(p):
    return 'p < 0.01' if p < 0.01 else f'p = {p:.2f}'


def draw_panel(ax, df, st, label, title, label_dx, method='spearman', label_dy=1.04,
               title_size=9, ylabel=True):
    ax.scatter(df['Age'], df['RO'], s=7, color=common.COLOR_LRO, alpha=0.5,
               edgecolors='black', linewidths=0.3, zorder=3)
    # 正の相関なので左上 (若年・高 RO) が空く。3 行に畳んで幅を抑え、点を隠さない。
    if method == 'spearman':
        text = f"rs = {st['rho']:.2f}\nn = {st['n']}\n{fmt_p(st['p_s'])}"
    else:
        text = f"r = {st['r']:.2f}\nn = {st['n']}\n{fmt_p(st['p'])}"
    ax.text(0.04, 0.96, text, transform=ax.transAxes, ha='left', va='top', fontsize=8,
            linespacing=1.3, zorder=4,
            bbox=dict(boxstyle='square,pad=0.4', facecolor='white', edgecolor='black', linewidth=0.8))
    ax.set_title(title, fontsize=title_size)
    ax.set_xlabel('Age (years)')
    if ylabel:
        ax.set_ylabel('Risk of osteoporosis')
    ax.set_xlim(*XLIM)
    ax.set_ylim(*YLIM)
    ax.xaxis.set_major_locator(MultipleLocator(20))
    ax.xaxis.set_minor_locator(MultipleLocator(10))
    ax.yaxis.set_major_locator(MultipleLocator(0.2))
    ax.yaxis.set_minor_locator(MultipleLocator(0.1))
    ax.tick_params(axis='both', which='major', length=3)
    ax.tick_params(axis='both', which='minor', length=1.5)
    common.panel_label(ax, label, dx=label_dx, dy=label_dy)


def make_figure(panels, data, results, name, width_mm, height_mm, nrows, ncols, label_dx,
                method='spearman', label_dy=1.04, title_size=9, share_ylabel=False, w_pad=2.0):
    fig, axes = plt.subplots(nrows, ncols, figsize=(common.mm(width_mm), common.mm(height_mm)))
    for i, (ax, (label, sheet, title, _)) in enumerate(zip(np.atleast_1d(axes).ravel(), panels)):
        draw_panel(ax, data[label], results[label], label, title, label_dx, method,
                   label_dy=label_dy, title_size=title_size, ylabel=(i == 0 or not share_ylabel))
    fig.tight_layout(w_pad=w_pad, h_pad=2.0)
    w, h = fig.get_size_inches()
    print(f'{name}: figure {w * 25.4:.1f} x {h * 25.4:.1f} mm ({nrows}x{ncols})')
    for ax in np.atleast_1d(axes).ravel():
        bb = ax.get_position()
        print(f'  panel plot area {bb.width * w * 25.4:.1f} x {bb.height * h * 25.4:.1f} mm')
    common.save(fig, name)
    plt.close(fig)


def main():
    common.setup()
    csv = load_csv()
    print(f'CSV (Exclude==0): n={len(csv)}, pre={int((csv.menopause == 0).sum())}, '
          f'post={int((csv.menopause == 1).sum())}')

    data, results = {}, {}
    print('\n== stats (Age vs RO) ==')
    print(f"{'panel':6s} {'n':>4s} {'Pearson r':>10s} {'p':>10s} {'Spearman rho':>13s} {'p':>10s} "
          f"{'provided r':>11s} {'provided n':>11s} {'CSV match':>10s}")
    for label, sheet, title, subset in PANELS:
        df = load_sheet(sheet)
        st = stats(df)
        sub = subset(csv)
        st_csv = stats(sub)
        match = same_multiset(df, sub)
        data[label], results[label] = df, st
        pr, pn = PROVIDED[label]
        print(f"{label:6s} {st['n']:4d} {st['r']:10.3f} {st['p']:10.2e} {st['rho']:13.3f} {st['p_s']:10.2e} "
              f"{pr:11.2f} {pn:11d} {str(match):>10s}")
        if not match:
            print(f"   CSV subset: n={st_csv['n']} r={st_csv['r']:.3f} rho={st_csv['rho']:.3f}")
        if round(st['r'], 2) != pr or st['n'] != pn:
            print(f'   !! provided value differs: r={pr}, n={pn}')

    print()
    # fig4_ab: 1 段組 (80 mm 幅) に A|B を横並び。y ラベルは A のみ、タイトルは 8 pt、
    #          パネルラベルはタイトル行より上に置いて衝突を避ける。
    # fig4_abc: 2 段組 (170 mm 幅) に 1x3。各パネルがほぼ正方形になる高さ 60 mm。
    make_figure(PANELS[:2], data, results, 'fig4_ab', width_mm=common.HALF_WIDTH_MM, height_mm=48,
                nrows=1, ncols=2, label_dx=-0.36, label_dy=1.13, title_size=8, share_ylabel=True,
                w_pad=1.0)
    make_figure(PANELS, data, results, 'fig4_abc', width_mm=common.FULL_WIDTH_MM, height_mm=60,
                nrows=1, ncols=3, label_dx=-0.30)


if __name__ == '__main__':
    main()
