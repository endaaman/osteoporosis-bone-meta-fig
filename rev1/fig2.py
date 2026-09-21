"""Revise 1 Figure 2: Grad-CAM 代表例 (A-D) を横 1 列 (1x4) に並べる。

入力: data/revise1/MEDCOMM DATA for Revised Figure2/Label {A,B,C,D}.png
      (著者提供の RGBA スクリーンショット。A/B/D は約 490 px 角、C は約 1130 px 角)
      画像はトリミングせずそのまま使う (透明画素を白に合成するだけ)。
出力: out/rev1/fig2.{png,pdf,tiff}

実行: uv run python rev1/fig2.py
"""
import os

import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

import common

SRC_DIR = 'data/revise1/MEDCOMM DATA for Revised Figure2'
LABELS = ['A', 'B', 'C', 'D']

# レイアウト [mm]
FIG_W = 170.0
COL_GAP = 3.0                              # パネル間の隙間
PANEL_W = (FIG_W - 3 * COL_GAP) / 4        # = 40.25 mm: パネル 1 枚の幅 = 高さ (正方形の枠)
LABEL_H = 5.0       # パネル上に置くラベル用の余白


def load_panel(label):
    path = os.path.join(SRC_DIR, f'Label {label}.png')
    rgba = np.asarray(Image.open(path).convert('RGBA'))
    # 透明/半透明画素は白に合成 (トリミングはしない)
    a = rgba[..., 3:4].astype(np.float32) / 255.0
    rgb = rgba[..., :3].astype(np.float32) * a + 255.0 * (1.0 - a)
    return np.clip(rgb, 0, 255).astype(np.uint8)


def main():
    common.setup()

    fig_w = FIG_W
    fig_h = LABEL_H + PANEL_W
    print(f'figure size: {fig_w:.2f} x {fig_h:.2f} mm '
          f'(panel {PANEL_W:.2f} mm square, gap {COL_GAP:.1f} mm, '
          f'max height {common.MAX_HEIGHT_MM} mm)')
    fig = plt.figure(figsize=(common.mm(fig_w), common.mm(fig_h)))

    for i, label in enumerate(LABELS):
        img = load_panel(label)
        h, w = img.shape[:2]
        # 正方形枠なので長辺が PANEL_W に収まる (実効 dpi は長辺で決まる)
        dpi_eff = max(w, h) / common.mm(PANEL_W)
        print(f'{label}: {w}x{h} px -> {dpi_eff:.0f} dpi in {PANEL_W:.2f} mm square')

        x0 = i * (PANEL_W + COL_GAP)   # 左から A B C D
        y0 = 0.0                       # 下端に揃え、上に LABEL_H の余白
        ax = fig.add_axes([x0 / fig_w, y0 / fig_h, PANEL_W / fig_w, PANEL_W / fig_h])
        # 正方形の枠に等倍で中央配置 (縦横比は保持、余りは白)
        ax.imshow(img, interpolation='lanczos', aspect='equal')
        ax.set_xlim(-0.5, w - 0.5)
        ax.set_ylim(h - 0.5, -0.5)
        # 縦横比が 1 でないぶんは枠内で中央に寄せる
        ax.set_anchor('C')
        ax.axis('off')
        # ラベルはパネル左上の外側 (画像の暗い角の上に載せない)
        common.panel_label(ax, label, dx=0.0, dy=1.01)

    common.save(fig, 'fig2')


if __name__ == '__main__':
    main()
