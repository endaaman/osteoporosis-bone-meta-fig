# Figure 5 (Revise 1) — 旧 Figure 3 の改訂 + 閉経前パネル追加

スクリプト: `rev1/fig5.py`（rev0 は `fig3.py`、出力 `out/fig3.png`）
出力: `out/rev1/fig5.{png,pdf,tiff}`（170 × 68 mm、600 dpi。tight bbox で実測 173 × 68 mm）

再生成:

```
uv run python rev1/fig5.py            # 既定（C は著者提示値を表示）
uv run python rev1/fig5.py --computed # B/C とも計算値 (Spearman) を表示
```

## パネル構成

1 × 3 横並び（幅比 1.2 : 1 : 1）。A（棒 2 本）は x 目盛ラベルが長いので少し広め、
B / C は同じ軸範囲（RO −0.05〜1.05、T-score −4.5〜4.5）で並べて比較できるようにした。
「A 左 + B/C 縦積み」は散布図が横長・低身長になって点が潰れるので不採用。

- **A** DXA 実施率。著者指示により白抜き（白塗り・黒枠）。各バー上に `件数/母数` と `(%)`。
  chi-square（rev0 と同じ `scipy.stats.chi2_contingency`、Yates 補正あり）で `**` と `p < 0.01`。
  y 軸は 1.0 で止め（`spines.set_bounds`）、有意差ブラケットはその上に置く。
- **B** DXA 実施者全員の RO vs T-score 散布図。rev0 と同じマーカー（`#4A7BA7`、黒縁、α=0.6）、
  回帰線なし（rev0 も無し）。右上に `rs, n, p` をボックスで表示。
- **C** 閉経前 DXA 実施者のみ。B と同じ体裁。

フォント: `common.setup()`（Arial 8 pt、軸ラベル 9 pt、パネルラベル 10 pt 太字）。線幅 0.8 / 0.6 / 0.4 pt。

## データソース

| パネル | データ | 抽出条件 |
|---|---|---|
| A | `data/osteoporosis_bone_meta.csv` | `menopause` 0/1 ごとに `Perioperative Dxa presence == 1` の割合。母数はグループ全行（Dxa NA・2 を含む） |
| B | 同上 | `Perioperative Dxa presence == 1` かつ `AI_P`, `Tscore` が数値 |
| C | 同上（描画）+ `data/revise1/REVISE _MEDCIMM _ Tscore_RO_遠田.xlsx` sheet `RO_Tscore_Premeno`（突合） | `menopause == 0 & Dxa == 1` かつ `Tscore` が数値 |

## 著者提示値との照合

| パネル | 著者提示 | 計算値 | 判定 |
|---|---|---|---|
| A 閉経前 | 38/325 | 38/325 (11.7%) | 一致 |
| A 閉経後 | 346/460 | 346/460 (75.2%)　※ 母数 460 は Dxa NA 3 例・Dxa=2 4 例を含む | 一致 |
| A p | p < 0.01 | chi-square (Yates) χ²=305.0, p=2.7e-68（補正なし 7.4e-69、Fisher 4.9e-75） | 一致 |
| B r | r = −0.64 | **Spearman rs = −0.6405** (p=2.2e-45) / Pearson r = −0.5982 | **Spearman が一致**（rev0 も Spearman） |
| B n | n = 384 | Dxa==1 は 384 人だが T-score が数値なのは **381** 人 | 図には描画点数と同じ **381** を表示 |
| C r | r = −0.58 | CSV n=37: Spearman −0.6059 / Pearson −0.5520 ／ 著者シート n=35: Spearman −0.6637 / Pearson −0.5702 | **どれも四捨五入で一致しない** |
| C n | n = 38 | 閉経前 & Dxa==1 は 38 行、うち T-score あり CSV 37 行・シート 35 行 | 38 は空欄込みの行数 |
| C p | p < 0.001 | CSV Spearman 7.1e-05 / Pearson 4.0e-04、シート Pearson 3.5e-04 | いずれも < 0.001 |

### C の著者値について（要確認）

- シート D〜H 列に散在する式セルの値: `R = −0.582238`, `Count = 38`, `t = −4.296859`, `P value = 0.000126`。
- `t = r·√(n−2)/√(1−r²)` に r=−0.582238, **n=38** を入れると −4.2969 で t が完全に再現する
  → 著者は p の計算に空欄 3 行込みの n=38 を使っている（実効ペア数は 35）。
- しかし r=−0.5822 自体は、シートの 35 ペア（Pearson −0.5702）、CSV の 37 ペア（Pearson −0.5520 /
  Spearman −0.6059）、空欄を 0 扱い（Pearson −0.5618）のどれでも再現できない。
  leave-one-out でも一致する単一行は特定できず（複数候補があり決め手なし）。
- **現状の図は著者提示値 `rs = −0.58, n = 38, p < 0.001` を C に載せている**（`FIXED['C']`）。
  描画されている点は CSV の 37 点なので、n=38 と表示点数が食い違う。
  著者に「−0.58 の算出方法（Pearson/Spearman、何ペア）」を確認し、
  再現できなければ `--computed`（rs = −0.61, n = 37, p < 0.01）に切り替えるのが安全。
- B と C で p の閾値表記が `< 0.01` / `< 0.001` と揃っていないのも著者指示のまま。
  揃えるなら B/C とも `< 0.001` に変えられる（実 p はどちらも遥かに小さい）。

## データの異常・注意点

CSV `data/osteoporosis_bone_meta.csv`:
- `Tscore` に非数値 `"3.4 dish?"`（研究ID 29、閉経後、Dxa=1）→ 欠損扱いで除外。
- 研究ID 5（閉経後、Dxa=1）は T-score / BMD が空欄。研究ID 2130（閉経前、Dxa=1、RO 0.062）も T-score 空欄。
  → B の n が 384 でなく 381、C が 38 でなく 37 になる理由。
- `Perioperative Dxa presence == 2` が 4 行（閉経後、T-score あり）。rev0 と同様に「実施」に数えず、A の分母には含める。
- 閉経後 3 行は Dxa 空欄（A の分母 460 に含む。rev0・著者値と同じ扱い）。
- 列名 `Cehst xray score ` に末尾スペース（今回は未使用。読み込み時に全列名を strip している）。
- 末尾に空行 216 行（研究ID NaN）→ 除外。

Excel `REVISE _MEDCIMM _ Tscore_RO_遠田.xlsx`（ファイル名にスペース）sheet `RO_Tscore_Premeno`:
- ヘッダ `T-score ` に末尾スペース。
- D〜H 列に式セル（R / Count / t / P value）と、332 行目 E 列に孤立値 `38.025` が散在 → A〜C 列のみ読む。
- 38 行のうち T-score 空欄 3 行。**うち 2 行は CSV に値がある**（RO 0.136 → T 2.0、RO 0.245 → T −1.9）。
  シート作成時の転記漏れの可能性が高い。RO 列は CSV と完全一致。

## 追記（メインセッションでの修正）

- B の y 軸を −5〜5 に広げた（T-score 4.6 と −4.4 の点が軸端で切れていた）
- B/C の統計ボックスを 3 行（rs / n / p）にして幅を詰めた（研究ID 683、RO 0.318 / T-score 4.6 の点がボックスの裏に隠れていた）

## 追記: 提供値 r=−0.58 の再現（メインセッション、2026-09-21）

提供シートの式は `D6 =CORREL(A4:A326,B4:B326)` で、**データ 2〜3 行目（2 例）を範囲から外している**。
シートの 4 行目以降 33 例で Pearson を取ると −0.582 となり、提供値 −0.58 と一致。
つまり提供値は「Pearson、シート 35 例のうち 33 例」。p の式 `T.DIST.2T(..., 38-2)` は n=38（空欄込み）で計算されている。

| データ | n | Pearson | Spearman |
|---|---|---|---|
| 提供シート全ペア | 35 | −0.570 | −0.664 |
| 提供シート 4 行目以降（Excel 式の範囲） | 33 | **−0.582** | — |
| csv 閉経前・DXA あり・T-score あり | 37 | −0.552 | −0.606 |
| csv 全 DXA あり（Fig5 B） | 381 | −0.598 | −0.640 |

## 決定（ken、2026-09-21）: C は再計算値

著者値 −0.58 は Excel の範囲ずれと判明したので、既定で B/C とも計算値（Spearman、C は n=37, rs=−0.61）。
`--author` で C に著者値を戻せる。
