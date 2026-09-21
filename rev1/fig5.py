"""Revise 1: Figure 5 (旧 Figure 3, fig3.py) の改訂版。

A: 閉経前 / 閉経後の周術期 DXA 実施率 (白抜きバー + 例数 + chi-square)
B: DXA 実施者全員の RO と T-score の相関 (Spearman, rev0 と同じ)
C: 閉経前 DXA 実施者のみの RO と T-score の相関 (新規)

実行: uv run python rev1/fig5.py [--author]
出力: out/rev1/fig5.{png,pdf,tiff}

統計値の扱い (詳細は docs/revise1/fig5.md):
- A, B は計算値がそのまま著者提示値と一致する (B は Spearman で r=-0.64)。
- C は著者提示値 r=-0.58, n=38, p<0.001 がどの計算方法でも再現できないため、
  既定では B/C とも計算値 (Spearman)。--author で C に著者提示値を載せる。
"""
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.ticker import MultipleLocator
from scipy.stats import pearsonr, spearmanr, chi2_contingency

import common

CSV = 'data/osteoporosis_bone_meta.csv'
XLSX = 'data/revise1/REVISE _MEDCIMM _ Tscore_RO_遠田.xlsx'
XLSX_SHEET = 'RO_Tscore_Premeno'

# 図に載せる相関の値。None なら計算値 (Spearman) を使う。
# 著者提示の C (r=-0.58, n=38) は Excel の CORREL 範囲ずれ (A4 始まり, 33 例の Pearson) と判明したので、
# B/C とも計算値 (Spearman) を使う (docs/revise1/fig5.md 参照)。--author で著者値に戻せる。
FIXED_AUTHOR = {
    'B': None,
    'C': dict(r=-0.58, n=38, p_text='p < 0.001'),
}
FIXED = {}

MARKER = dict(color=common.COLOR_LRO, s=14, alpha=0.6, edgecolors='black', linewidth=0.4)


def p_text(p):
    return 'p < 0.01' if p < 0.01 else f'p = {p:.2f}'


def load_csv():
    df = pd.read_csv(CSV)
    df.columns = [c.strip() for c in df.columns]
    df = df.dropna(subset=['研究ID'])
    for c in ['AI_P', 'Tscore']:
        raw = df[c]
        df[c] = pd.to_numeric(raw, errors='coerce')
        bad = raw[df[c].isna() & raw.notna()]
        if len(bad):
            print(f'[warn] CSV {c}: non-numeric values dropped: '
                  f'{[(int(i), v) for i, v in zip(df.loc[bad.index, "研究ID"], bad)]}')
    return df


def load_premeno_sheet():
    """著者の閉経前シート。A-C 列以外の散在セル (R, Count, p 値の式) は捨てる。"""
    raw = pd.read_excel(XLSX, sheet_name=XLSX_SHEET, header=None)
    header = [str(c).strip() for c in raw.iloc[0, :3]]
    assert header == ['RO', 'T-score', 'Dxa presence'], header
    x = raw.iloc[1:, :3].copy()
    x.columns = ['RO', 'Tscore', 'Dxa']
    x = x.apply(pd.to_numeric, errors='coerce').dropna(subset=['RO'])
    return x.reset_index(drop=True)


def cross_check_premeno(csv_pre, sheet):
    """シートと CSV (menopause==0 & Dxa==1) の突合。"""
    a = csv_pre[['AI_P', 'Tscore']].rename(columns={'AI_P': 'RO'})
    a = a.sort_values(['RO', 'Tscore']).reset_index(drop=True)
    b = sheet[['RO', 'Tscore']].sort_values(['RO', 'Tscore']).reset_index(drop=True)
    print(f'\n[cross-check C] CSV premeno&Dxa==1: {len(a)} rows ({a.Tscore.notna().sum()} with T-score); '
          f'sheet: {len(b)} rows ({b.Tscore.notna().sum()} with T-score)')
    if len(a) != len(b) or not np.allclose(a.RO, b.RO):
        print('  [warn] RO column differs between CSV and sheet')
        return
    diff = a[~((a.Tscore == b.Tscore) | (a.Tscore.isna() & b.Tscore.isna()))]
    if len(diff):
        print('  [warn] T-score differs (RO, CSV T, sheet T):')
        for i in diff.index:
            print(f'    RO={a.RO[i]:.3f}  csv={a.Tscore[i]}  sheet={b.Tscore[i]}')
    else:
        print('  RO and T-score identical')


def corr_report(name, x, y):
    x, y = np.asarray(x), np.asarray(y)
    rp, pp = pearsonr(x, y)
    rs, ps = spearmanr(x, y)
    print(f'[{name}] n={len(x)}  Pearson r={rp:.4f} (p={pp:.2e})  Spearman rs={rs:.4f} (p={ps:.2e})')
    return dict(n=len(x), r=rs, p=ps, p_text=p_text(ps), pearson=rp, pearson_p=pp)


def scatter_panel(ax, sub, label, stats, xlabel='Risk of osteoporosis'):
    ax.scatter(sub['AI_P'], sub['Tscore'], **MARKER)
    r_txt = f"{stats['r']:.2f}".replace('-', '\u2212')
    ax.text(0.97, 0.97, f"rs = {r_txt}\n{stats['p_text']}",
            transform=ax.transAxes, ha='right', va='top', fontsize=8,
            bbox=dict(boxstyle='square,pad=0.3', facecolor='white', edgecolor='black', linewidth=0.6))
    ax.set_xlabel(xlabel)
    ax.set_ylabel('T-score')
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(-5, 5)
    ax.xaxis.set_major_locator(MultipleLocator(0.2))
    ax.xaxis.set_minor_locator(MultipleLocator(0.1))
    ax.yaxis.set_major_locator(MultipleLocator(2))
    ax.yaxis.set_minor_locator(MultipleLocator(1))
    ax.tick_params(which='major', length=3)
    ax.tick_params(which='minor', length=1.5)
    common.panel_label(ax, label, dx=-0.24, dy=1.0)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--author', action='store_true',
                        help='C に著者提示値 (r=-0.58, n=38) を載せる')
    args = parser.parse_args()
    fixed = FIXED_AUTHOR if args.author else FIXED

    common.setup()
    df = load_csv()
    dxa = df['Perioperative Dxa presence']

    # ---------------- A: DXA 実施率 ----------------
    groups = {}
    for name, m in [('pre', 0), ('post', 1)]:
        g = df[df['menopause'] == m]
        d = g['Perioperative Dxa presence']
        n_dxa, n_all = int((d == 1).sum()), len(g)
        groups[name] = (n_dxa, n_all)
        print(f'[A] {name}menopausal: DXA {n_dxa}/{n_all} = {n_dxa / n_all:.4f} '
              f'(Dxa==0: {(d == 0).sum()}, Dxa==2: {(d == 2).sum()}, NA: {d.isna().sum()})')
    (a, na), (b, nb) = groups['pre'], groups['post']
    chi2, p_chi, _, _ = chi2_contingency([[a, na - a], [b, nb - b]])  # rev0 と同じ (Yates 補正あり)
    print(f'[A] chi-square (Yates): chi2={chi2:.2f}, p={p_chi:.3e}')

    # ---------------- B: 全 DXA 実施者 ----------------
    dxa_all = df[dxa == 1]
    print(f'[B] Dxa==1: {len(dxa_all)} patients, with T-score: {dxa_all.Tscore.notna().sum()}')
    sub_b = dxa_all.dropna(subset=['AI_P', 'Tscore'])
    stats_b = corr_report('B', sub_b['AI_P'], sub_b['Tscore'])

    # ---------------- C: 閉経前 DXA 実施者 ----------------
    sub_c_all = df[(df['menopause'] == 0) & (dxa == 1)]
    sheet = load_premeno_sheet()
    cross_check_premeno(sub_c_all, sheet)
    sub_c = sub_c_all.dropna(subset=['AI_P', 'Tscore'])
    stats_c = corr_report('C (CSV)', sub_c['AI_P'], sub_c['Tscore'])
    sh = sheet.dropna(subset=['RO', 'Tscore'])
    corr_report('C (author sheet, blanks dropped)', sh['RO'], sh['Tscore'])

    for k, s in [('B', stats_b), ('C', stats_c)]:
        if fixed.get(k):
            s.update(fixed[k])
            print(f'[{k}] !!! figure shows AUTHOR-PROVIDED values {fixed[k]} (not reproduced from data)')
        else:
            print(f'[{k}] figure shows computed Spearman: rs={s["r"]:.2f}, n={s["n"]}, {s["p_text"]}')

    # ---------------- 描画 ----------------
    fig = plt.figure(figsize=(common.mm(common.FULL_WIDTH_MM), common.mm(68)))
    gs = GridSpec(1, 3, figure=fig, width_ratios=[1.2, 1, 1], wspace=0.5,
                  left=0.085, right=0.99, bottom=0.19, top=0.93)
    ax1, ax2, ax3 = [fig.add_subplot(gs[0, i]) for i in range(3)]

    # A
    x_pos = [0, 1.3]
    xm = sum(x_pos) / 2
    rates = [a / na, b / nb]
    ax1.bar(x_pos, rates, width=0.7, color='white', edgecolor='black', linewidth=0.8)
    for x, r, (k, n) in zip(x_pos, rates, [(a, na), (b, nb)]):
        ax1.text(x, r + 0.015, f'{k}/{n}\n({r * 100:.1f}%)', ha='center', va='bottom', fontsize=8)
    # 有意差ブラケット: 軸は 1.0 で止め、その上に置く
    y_br = max(rates) + 0.22
    ax1.plot([x_pos[0], x_pos[0], x_pos[1], x_pos[1]],
             [y_br - 0.02, y_br, y_br, y_br - 0.02], 'k-', linewidth=0.8, clip_on=False)
    if p_chi < 0.01:
        ax1.text(xm, y_br - 0.005, '**', ha='center', va='bottom', fontsize=10, fontweight='bold')
        ax1.text(xm, y_br + 0.075, 'p < 0.01', ha='center', va='bottom', fontsize=8)
    else:
        ax1.text(xm, y_br + 0.02, f'p = {p_chi:.2f}', ha='center', va='bottom', fontsize=8)
    ax1.set_ylabel('Conduction rate of\nperioperative bone density test')
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(['Premenopausal\nwomen', 'Postmenopausal\nwomen'])
    ax1.set_xlim(-0.65, 1.95)
    ax1.set_ylim(0, 1.2)
    ax1.set_yticks(np.arange(0, 1.01, 0.1))
    ax1.spines['left'].set_bounds(0, 1.0)
    ax1.tick_params(which='major', length=3)
    common.panel_label(ax1, 'A', dx=-0.32, dy=1.0)

    # B, C
    scatter_panel(ax2, sub_b, 'B', stats_b)
    scatter_panel(ax3, sub_c, 'C', stats_c)

    w, h = fig.get_size_inches() * 25.4
    print(f'\nfigure size: {w:.0f} x {h:.0f} mm')
    common.save(fig, 'fig5')


if __name__ == '__main__':
    main()
