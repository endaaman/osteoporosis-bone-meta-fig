# Revise 1 (MedComm) 対応

- 元資料: `data/revise1/MEDCOMM_REVISE_対応＿遠田担当.xlsx`（対応表）、査読コメント・初回原稿も同ディレクトリ
- revise 前の状態は git tag `rev0`（commit 5a1b043）
- rev1 の成果物は `rev1/*.py` → `out/rev1/`。旧スクリプトは `rev0/`（`rev0/scripts/all.sh` で再生成、出力は `out/rev0/`）、旧メモは `docs/rev0/`
- drawio 等の手編集ファイルは `_rev0` / `_rev1` サフィックスで分ける（`data/fig1/fig1_rev0.drawio`, `fig1_rev1.drawio`）
- 共通スタイルは `rev1/common.py`（Arial、8–10 pt、170 mm または 80 mm 幅、600 dpi、png/pdf/tiff）。Fig1 は `rev1/fig1.py`（drawio → PNG/PDF、80 mm 幅）
- 各図の詳細・提供値との突き合わせは `docs/revise1/figN.md`

## 投稿規定（対応表より）

- 幅 170 mm（または 80 mm）、高さ 210 mm 以内
- フォント 8〜10 pt（最低 6 pt）
- パネルラベル A/B/C は 12 pt・大文字・太字・左上（編集部コメントで 12 pt と明記）
- 線幅 0.25 pt 以上
- 300 dpi 以上
- 個々の値を示すときは白抜きの柱

## 番号の対応

| rev0 | rev1 | 内容 | 入力 |
|---|---|---|---|
| Fig1 | Fig1 | Study design。AI model ボックスに DenseNet 等の技術詳細を追記（引用 radiol.231937） | `data/fig1/fig1_rev1.drawio` |
| なし | Fig2 | Grad-CAM 代表例 A–D | `data/revise1/MEDCOMM DATA for Revised Figure2/` |
| Fig2 | Fig3 | KM 曲線。Youden カットオフで再作成。B/C に HR・95%CI・p | `REVISE_MEDCOMM_KM_遠田20260921.xlsx` |
| なし | Fig4 | Age vs RO 散布図 A 全体 / B 閉経前 / C 閉経後。AB 版と ABC 版の 2 種 | `REVISE _MEDCIMM _AGE _RO_遠田.xlsx` |
| Fig3 | Fig5 | A DXA 施行率（白抜き柱、症例数）/ B T-score vs RO 全体 / C 閉経前（新規） | `REVISE _MEDCIMM _ Tscore_RO_遠田.xlsx` + csv |

Fig4 系（LASSO/LightGBM/SHAP）と旧 Fig5/6（Cox ノモグラム・内部検証）は今回の対応表に無い。

## 著者提供の統計値

| 図 | 群 | 値 |
|---|---|---|
| Fig3 B | 閉経前 | p=0.04, HR 1.91, 95%CI 1.01–3.59 |
| Fig3 C | 閉経後 | p=0.56, HR 0.84, 95%CI 0.46–1.51（旧 KM データ時点。新データでは p=0.65, HR 0.87 (0.49–1.55)） |
| Fig4 A | 全患者 | r=0.61, n=785, p<0.01 |
| Fig4 B | 閉経前 | r=0.21, n=325, p<0.01 |
| Fig4 C | 閉経後 | r=0.45, n=460, p<0.01 |
| Fig5 A | DXA 施行 | 閉経前 38/325、閉経後 346/460 |
| Fig5 B | 全患者 | r=-0.64, n=384, p<0.01 |
| Fig5 C | 閉経前 | r=-0.58, n=38, p<0.001 |

## データの注意

- 提供 xlsx は表記揺れが多い（`'High '` の末尾スペース、ヘッダ `'T-score '`、ファイル名の空白、
  p 値式の自由度が全シート 326-2 固定 など）。読み込み時は必ず strip し、n を照合する
- 著者提供の RO group 列は閉経状態でカットオフが異なる（閉経前 ≥0.102、閉経後 ≥0.110）が、
  標準的手法で再現できなかった。詳細は `fig3.md`

## 相関係数（ken、2026-09-21）

全図 Spearman (rs) に統一（RO が 0–1 に丸められた歪んだ分布のため）。Fig4 rs 0.66 / 0.22 / 0.46、
Fig5 B rs −0.64 (n=381)、C rs −0.61 (n=37)。原稿 Methods の「Pearson」は著者に修正依頼。

## カットオフ（2026-09-21）

HRO/LRO は xlsx の RO group 列をそのまま使う（閉経前 RO ≥ 0.102 / 閉経後 ≥ 0.110）。
著者の説明は「閉経前・周術期 DXA 施行 37 例で骨減少症以上（T ≤ −1）を陽性とした Youden index = RO 0.1」で、
`rev1/cutoff.py`（cohort='pre_peri'）で再現できる（感度 0.73、特異度 0.85、AUC 0.80、bootstrap 95% CI 0.05–0.25）。
Fig1 の N は HRO 440 / LRO 345。Fig3 は閉経前 p=0.04・HR 1.91 (1.01–3.59)。

## 置き場所

- `data/` と `out/` は `~/Sync/Projects/Shimizu/op/` への symlink（git 管理外・Syncthing 同期）。
  git には `rev1/*.py` と `docs/` だけ入る。データを投入し直したら `uv run python rev1/figN.py` で再生成する
- 各図は png / pdf / tiff（600 dpi、tight bbox・余白 0 なので幅は指定値以下）。tiff は 20〜70 MB あるので提出形式に合わせて選ぶ

## 清水先生向けメモ

`docs/revise1/memo_shimizu.md` → `out/rev1/memo_遠田_<日付>.docx`。フォントは Meiryo UI
（`docs/revise1/reference.docx` の styles を差し替えた pandoc 参照 docx）。

```
pandoc docs/revise1/memo_shimizu.md --reference-doc=docs/revise1/reference.docx -o out/rev1/memo_遠田_20260921.docx
```
