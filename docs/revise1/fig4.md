# Revise 1 — 新 Figure 4: Age vs Risk of osteoporosis

MedComm 査読対応で新設する Figure 4。年齢と RO (Risk of osteoporosis, AI スコア `AI_P`, 0–1) の散布図を
A: 全患者 / B: 閉経前 / C: 閉経後 の 3 群で示し、各パネルに n, r, p を表示する。

## データソース

| 項目 | 内容 |
|---|---|
| 一次データ | `data/revise1/REVISE _MEDCIMM _AGE _RO_遠田.xlsx`（ファイル名に半角スペースあり） |
| シート | `Age_RO_全患者` (785 行) / `Age_RO_閉経前` (325 行) / `Age_RO_閉経後` (460 行) |
| 使用列 | A = Age, B = AI_P（閉経前シートだけ見出しが `age` / `RO`。列位置で読む） |
| 無視した列 | E–H の Excel 数式 (`CORREL`, t 値, `T.DIST.2T`)。**H2 の自由度が全シートで `326-2` に固定**されており（閉経前 n=325 のコピペ）、全患者・閉経後では誤り。r は正しいので p だけ自前で再計算 |
| 照合先 | `data/osteoporosis_bone_meta.csv`（`Exclude==0` → 785 = 閉経前 325 + 閉経後 460） |

読み込み時に `strip` + `to_numeric(errors='coerce')` + `dropna` をかけているが、実際には
欠損・非数値・空白行は 0 件だった（3 シートとも全行が数値）。

## CSV との照合結果

3 シートとも、CSV の `Exclude==0` サブセット（全体 / `menopause==0` / `menopause==1`）と
**(Age, AI_P) ペアの多重集合として完全一致**した（順序は無視、6 桁丸め）。
したがって著者シートは CSV から抽出したもので、値の改変・脱落はない。

## 統計

Age と RO の相関。p は両側。

| Panel | n | Pearson r (計算) | p | Spearman ρ (計算) | p | 著者提供 r | 著者提供 n |
|---|---|---|---|---|---|---|---|
| A 全患者 | 785 | **0.615** | 9.3e-83 | 0.658 | 1.9e-98 | 0.61 | 785 |
| B 閉経前 | 325 | **0.205** | 2.0e-04 | 0.223 | 5.1e-05 | 0.21 | 325 |
| C 閉経後 | 460 | **0.446** | 8.2e-24 | 0.457 | 3.9e-25 | 0.45 | 460 |

- 著者の r は **Pearson**（Excel `CORREL`）と小数 2 桁で完全一致。Spearman は一致しない
  （0.66 / 0.22 / 0.46）。図には Pearson を採用し、`r = 0.61` の形で 2 桁表示。
- p はいずれの方法でも p < 0.01（rev0 と同じ表記規則: p<0.01 なら `p < 0.01`、それ以外は `p = 0.xx`）。
- **注意**: rev0 の Fig 3b（T-score vs RO）は Spearman（`rs`）を使っている。本図を Pearson にすると
  論文内で相関手法が混在するので、figure legend / Methods に「Pearson correlation」と明記するか、
  Fig 3b も含めて統一するかは著者判断。統一するなら Spearman 値は上表のとおり（結論は変わらない）。

## 図の仕様・レイアウト

| 項目 | 内容 |
|---|---|
| 出力 | `out/rev1/fig4_ab.{png,pdf,tiff}`（A, B のみ）/ `out/rev1/fig4_abc.{png,pdf,tiff}`（A, B, C） |
| サイズ | **fig4_ab**: 幅 80 mm（1 段組 `common.HALF_WIDTH_MM`）× 高さ 158 mm（出力 PNG 実測 78.7 × 157.2 mm）。**fig4_abc**: 幅 170 mm（2 段組 `common.FULL_WIDTH_MM`）× 高さ 60 mm（実測 169.1 × 58.8 mm）。いずれも高さ上限 210 mm 内 |
| 解像度 | 600 dpi（`common.DPI`）。PDF はフォント埋め込み (Type 42) |
| フォント | Arial。本文 8 pt、軸ラベル・タイトル 9 pt、パネルラベル 12 pt 太字（編集部指定）|
| マーカー | rev0 Fig 3b と同じ `#4A7BA7`、黒縁 0.25 pt。s=7, alpha=0.5 と小さく半透明にして、AI_P が 3 桁丸めで重なる点（0 や 0.001 が 20 件超）の密度が見えるようにした |
| 回帰線 | なし（rev0 Fig 3b も引いていない） |
| 軸 | x: Age (years) 20–92、major 20 / minor 10。y: Risk of osteoporosis −0.03–1.03、major 0.2 / minor 0.1。上・右スパインなし |
| 軸範囲の共有 | 3 パネルとも同一の x, y 範囲。B は 25–57 歳に集中して右半分が空くが、A/C と直接比較できることを優先した（閉経前が年齢幅の狭い集団であることも図から読める） |
| 統計表示 | 各パネル左上に枠付きテキスト 3 行 `r = 0.61 / n = 785 / p < 0.01`。正の相関なので左上（若年・高 RO）が空いており点を隠さない。rev0 の legend 形式（1 行・マーカー付き）だと幅が広く A/C の RO≈1 の点を隠したため畳んだ |
| 配置 | **fig4_ab**: 2×1（A の下に B を縦積み）、各パネルのプロット領域約 63 × 58 mm。80 mm 幅で 1×2 にすると各パネル 35 mm 程度になり 8 pt の文字が入らないので縦積みにした。y 軸ラベル・目盛（約 10 mm）とパネルラベルの分だけプロット幅は 70 mm に届かず、高さも 160 mm 以内に収めるため 58 mm（ほぼ正方形）。パネルラベルの `dx` は幅に合わせて −0.16（abc は −0.30）。**fig4_abc**: 1×3、各パネルのプロット領域約 39 mm 角。2+1 段組は A が他より大きく見えて重み付けが生じること、Fig 2（KM: 全体/閉経前/閉経後）と同じ横一列にすると図間で対応が取りやすいことから 1×3 を選択。50 mm 幅でも 8 pt の目盛と点密度は判読できることを PNG で確認 |

## 再生成

```sh
uv run python rev1/fig4.py
```

標準出力に CSV 照合結果と統計表（Pearson / Spearman / 著者提供値）が出る。
共通スタイルは `rev1/common.py`（`setup` / `panel_label` / `save`）。

## 決定（ken、2026-09-21）: 図は Spearman に統一

RO は 0–1 に丸められた歪んだ分布で直線関係でもないため、全相関を Spearman (rs) に統一する
（Fig5 B/C と同じ）。図の値は A rs=0.66 / B 0.22 / C 0.46。原稿 Methods の「Pearson」は
著者側で修正してもらう（memo_shimizu.md に記載）。`draw_panel(..., method='pearson')` で戻せる。

## 追記（2026-09-21）: AB 版は 80 mm 幅の横並び

`fig4_ab` は 1×2（A | B）で 80 mm 幅、出力 76 × 40 mm。y ラベルは A のみ、タイトル 8 pt。`fig4_abc` は 170 mm 幅 1×3。
マーカー縁は 0.3 pt（規定の下限 0.25 pt に余裕）。`common.save` は pad_inches=0 にしたので出力幅が
指定幅を超えない。
