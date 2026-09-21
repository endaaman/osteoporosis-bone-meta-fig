# Fig5 / Fig6 解析レポート

Cox PH ノモグラム（Fig5）と内部検証（Fig6: time-dependent ROC + calibration）。
PMC10876661（Fine-Gray nomogram 論文）と同じ枠組みでの内部検証。

## エンドポイント・データ

| 項目 | 内容 |
|---|---|
| イベント | `BMFS_Event`（骨転移 or 死亡の合算。Fig4 と同一定義） |
| 時間 | `BMFS`（月、観察期間 60 ヶ月で administrative censoring） |
| データ | `data/fig4/enrolled_patients_20260322.xlsx` (特徴量) + `data/osteoporosis_bone_meta.csv` (BMFS 時間)、`研究ID` で merge |
| 全体 N | 785（Exclude=0）／ events 100 |
| Cox PH 学習用 N | 556（特徴量欠損 dropna 後）／ events 62（BASE） |
| 切除検体込みの N | 301／ events 27（with-resection） |

死亡を骨メタと分離した event 列が現データには無いため、合算エンドポイントで Cox PH を採用。
Fine-Gray ではない（競合リスクの定義不能）。

## 特徴量

BASE（11個）: `BMI, Age, ER, PR, HER2, Ki67, Stage, perioperative chemo, endocrine, post-radiation, Risk of osteoporosis`

Resection（5個、`--with-resection` で追加）: `Tumor size, Nodal involvement, number of affected nodes, resected nodes, grade`

## 手法

| 項目 | 設定 |
|---|---|
| モデル | Cox PH（lifelines `CoxPHFitter`、penalizer=0.01） |
| ノモグラム fit | 全データで 1 回 fit |
| 内部検証 | 5-fold CV（KFold, shuffle, seed=42） |
| 評価指標 | C-index（lifelines）、time-dependent AUC（1/3/5 年）、calibration（KM 観測 vs 予測） |
| 予測時点 | 12 / 36 / 60 ヶ月 |

time-dependent AUC のケース定義:
- case = `events==1 & times <= t`
- ctrl = `times >= t & ~case`
- score = OOF partial hazard

## 結果

### Cox PH 係数（全データ fit、BASE）

| 変数 | coef (β) | exp(coef) (HR) | p |
|---|---|---|---|
| BMI | -0.0533 | 0.948 | 0.075 |
| Age | 0.0018 | 1.002 | 0.887 |
| ER | 0.0030 | 1.003 | 0.477 |
| PR | -0.0081 | 0.992 | 0.175 |
| HER2 | -0.0319 | 0.969 | 0.796 |
| Ki67 | 0.0075 | 1.008 | 0.190 |
| **Stage** | **1.2792** | **3.594** | **<0.001** |
| Chemotherapy | 0.2871 | 1.333 | 0.346 |
| Endocrine | -0.1377 | 0.871 | 0.785 |
| Radiation | 0.0017 | 1.002 | 0.995 |
| Risk of osteoporosis | 0.3355 | 1.399 | 0.540 |

Stage が支配的（HR 3.59、p<0.001）。他は個別の有意性なし。
RO スコアは Cox 多変量では非有意（β=0.34、p=0.54）— Fig4 の binary 分類で postmenopausal AUC 寄与は見えていたが、Stage と相関する情報を持つため Cox では飲まれる。

### 内部検証指標（5-fold CV）

| 指標 | BASE (n=556) | with-resection (n=301) |
|---|---|---|
| C-index | 0.661 | 0.593 |
| 1-year AUC | 0.689 | 0.633 |
| 3-year AUC | 0.685 | 0.598 |
| 5-year AUC | 0.671 | 0.601 |

切除検体込みは BASE より **C-index で -0.068、AUC で -0.05〜-0.09** 悪化。

#### resection 版が悪化する理由

1. **N が半減しイベント数が極端に減る（EPV 不足）**
   - 556 → 301、events 62 → 27
   - grade（n=461）と Ki67（n=586）の欠損が dropna で効く
   - 16 変数 / 27 events ＝ **EPV 1.7**（推奨は ≥10）→ 完全に過適合領域
   - 5-fold CV では fold あたり ~240 例 / ~22 events で fit するためさらに不安定

2. **Stage の支配が崩れる**
   - BASE: Stage HR=3.59, p<0.001（圧倒的）
   - resection: Stage HR=1.86, p=0.20（非有意化）
   - 代わりに `number of affected nodes` HR=1.12, p=0.005 が出る
   - リンパ節転移個数が Stage の情報を分割して食う構造で、係数が散る

→ **BASE 版を主、resection 版は補助/感度解析扱い**が妥当。論文本文では BASE のみ提示、resection は supplementary に回すのが安全。

### Calibration

5 群（予測確率の quintile）で Kaplan–Meier 観測 vs 予測を比較。
Greenwood 95% CI 付き。

- **1y**: events ~6 例しかなく CI 広いが、点推定は 45° 線上
- **3y / 5y**: 5 群すべてが 45° 線にほぼ乗る。最高リスク群の予測 0.28 / 観測 0.24（5y）も整合

→ discrimination は中等度だが **calibration は 1/3/5y すべてで良好**

## 出力ファイル

| ファイル | 内容 |
|---|---|
| `out/fig5_nomogram.png` | ノモグラム（BASE） |
| `out/fig5_nomogram_with_resection.png` | ノモグラム（resection 込み） |
| `out/fig6_roc.png` | time-dependent ROC（BASE、3 曲線） |
| `out/fig6_roc_with_resection.png` | 同上、resection 込み |
| `out/fig6_calibration.png` | calibration 3 パネル（BASE） |
| `out/fig6_calibration_with_resection.png` | 同上、resection 込み |

## ファイル構成

| スクリプト | 役割 |
|---|---|
| `fig5_common.py` | データ load + merge、OOF Cox 予測、time_metrics |
| `fig5.py` | ノモグラム描画（matplotlib 自前） |
| `fig6.py` | time-dependent ROC + calibration |
| `scripts/fig5.sh`, `scripts/fig6.sh` | uv run ラッパー、`all.sh` から呼ばれる |

## 論文化時の注意

1. **Methods**:
   - 「Cox proportional hazards model with 5-fold cross-validation for internal validation」
   - 「Composite endpoint of bone metastasis or death」（合算エンドポイントの注釈）
   - PMC10876661 と同様、外部検証はなし（内部検証のみで通った前例あり）

2. **Limitations**:
   - 外部コホートなし
   - 観察期間 60 ヶ月での administrative censoring が多く、5-year 推定は他時点より不安定（CV AUC は 0.67、1y/3y より僅かに低い）
   - 競合リスク（骨メタ前死亡）を分離していない → 死亡だけのリスクは別途出せない

3. **Discussion で書ける要点**:
   - C-index 0.66 で「中等度の discrimination」、calibration は良好
   - Stage が支配的予測因子。RO スコアは Fig4 の binary 設定では postmenopausal で寄与が見えるが、Cox 多変量では Stage と情報が重なるため非有意

## 改善余地（将来作業）

- 競合リスク分離した event 列を臨床医に依頼 → Fine-Gray モデルに置き換え
- bootstrap optimism 補正（B=1000）を追加（PMC10876661 はやっていないので必須ではない）
- decision curve analysis（DCA）を追加するなら `dcurves` 等で可能
