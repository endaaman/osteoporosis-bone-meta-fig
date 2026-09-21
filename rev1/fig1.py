"""Revise 1 Figure 1 (study design, drawio) の書き出し。

    uv run python rev1/fig1.py

- data/fig1/fig1_rev1.drawio → out/rev1/fig1.png (600 dpi 相当, dpi メタデータ付き)
                             → out/rev1/fig1.pdf (ページ幅 80 mm に縮小。文字はベクタのまま)
"""
import os
import subprocess

from PIL import Image
from pypdf import PdfReader, PdfWriter, Transformation

import common

SRC = 'data/fig1/fig1_rev1.drawio'
OUT_DIR = common.OUT_DIR
WIDTH_MM = common.HALF_WIDTH_MM     # 80 mm (1 段幅)
BORDER_PX = 20
DRAWIO = ['drawio', '--no-sandbox', '--disable-gpu', '-x', '-b', str(BORDER_PX)]


def run(args):
    r = subprocess.run(args, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(r.stdout + r.stderr)


def export_png(path):
    # drawio の -s は倍率。まず 1 倍で幅 px を測り、目標 dpi になる倍率で再出力する
    run(DRAWIO + ['-f', 'png', '-s', '1', '-o', path, SRC])
    w1 = Image.open(path).size[0]
    scale = common.DPI * WIDTH_MM / 25.4 / w1
    run(DRAWIO + ['-f', 'png', '-s', f'{scale:.4f}', '-o', path, SRC])
    im = Image.open(path)
    dpi = im.size[0] / (WIDTH_MM / 25.4)
    im.save(path, dpi=(dpi, dpi))
    print(f'saved {path}  {im.size[0]}x{im.size[1]} px  = {WIDTH_MM} x {im.size[1] / dpi * 25.4:.1f} mm @ {dpi:.0f} dpi')


def export_pdf(path):
    run(DRAWIO + ['-f', 'pdf', '--crop', '-o', path, SRC])
    reader = PdfReader(path)
    page = reader.pages[0]
    w_pt = float(page.mediabox.width)
    h_pt = float(page.mediabox.height)
    target_w_pt = WIDTH_MM / 25.4 * 72
    k = target_w_pt / w_pt
    page.add_transformation(Transformation().scale(k, k))
    page.mediabox.lower_left = (0, 0)
    page.mediabox.upper_right = (target_w_pt, h_pt * k)
    for box in ('cropbox', 'trimbox', 'bleedbox', 'artbox'):
        if box in page:
            del page[box]
    writer = PdfWriter()
    writer.add_page(page)
    with open(path, 'wb') as f:
        writer.write(f)
    print(f'saved {path}  page {WIDTH_MM} x {h_pt * k / 72 * 25.4:.1f} mm (scale {k:.4f})')


if __name__ == '__main__':
    os.makedirs(OUT_DIR, exist_ok=True)
    export_png(os.path.join(OUT_DIR, 'fig1.png'))
    export_pdf(os.path.join(OUT_DIR, 'fig1.pdf'))
