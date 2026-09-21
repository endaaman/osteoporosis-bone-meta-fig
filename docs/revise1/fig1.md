# Figure 1 (Study design) — revise 1

## 対応した指摘

Reviewer 2, Minor Comment 2（`data/revise1/②Medcomm_査読者コメント.docx`）:

> Figure 1: The flowchart is overly simplified. Briefly incorporating technical details of the AI
> architecture within the "AI model" box (e.g., indicating the DenseNet architecture and target
> skeletal regions) would benefit clinical readers.

著者指示（`MEDCOMM_REVISE_対応＿遠田担当.xlsx`）: 「AIモデル（AI model）」のボックス内に
AIアーキテクチャの技術的詳細を簡潔に記載。Citation: https://pubs.rsna.org/doi/full/10.1148/radiol.231937

## 成果物

| ファイル | 内容 |
|---|---|
| `data/fig1/fig1_rev0.drawio`, `data/fig1/fig1_rev0.png` | rev0（未変更。旧 `fig1.drawio` / `fig1.png`） |
| `data/fig1/fig1_rev1.drawio` | rev1 のソース（rev0 のコピーに AI model ボックスの編集を加えたもの） |
| `out/rev1/fig1.png` | rev1 のレンダリング（3174×4826 px、drawio CLI `-s 4`） |

## AI model ボックスの変更

図中には**モデル名とアーキテクチャの 1 行**だけを足し、引用・学習データ数・RCT などの詳細は
図に入れず legend に回した（ken 指示）。ボックスは rev0 の 480×280 → 480×290、AI アイコンは
180 → 150 px。それ以外の要素の位置は rev0 と同じ（ボックス直下の矢印の折れ位置を y=600→608 に
ずらしただけで、図全体の縦横比は変わらない）。

```
AI model
Input: Perioperative chest radiograph        （rev0: "Perioperative Xray image"）
OPSCAN (DenseNet-based CNN)                  ← 追加（22 px）
[AI icon]
Output: Risk of Osteoporosis (RO)            （rev0 と同じ）
continuous score 0–1 → High RO / Low RO      ← 追加（18 px）
```

ついでに rev0 からあった誤植 "Conduction rate of bone desnsity test" → "bone density test" を rev1 で修正した。

### Figure legend 案（引用はここに載せる）

> **Figure 1. Study design.** Perioperative chest radiographs were analysed with OPSCAN
> (Osteoporotic Precise Screening using Chest radiography and Artificial neural network), a
> DenseNet-based convolutional neural network that outputs a continuous risk of osteoporosis (RO)
> score (0–1); a higher score corresponds to a lower predicted T-score [16, 17]. Patients were
> dichotomized into high RO (HRO) and low RO (LRO) groups at the prespecified cutpoint.
> eBC, early-stage breast cancer; ER, estrogen receptor; HER2, human epidermal growth factor
> receptor 2; BMA, bone-modifying agent.

（[16] Lin C et al. Radiology 2024;311(3):e231937, doi:10.1148/radiol.231937 / [17] Tsai DJ et al.
J Med Syst 2024;48(1):12。カットポイントの値が確定したら "at the prespecified cutpoint" を
"at RO ≥ x.xx" に置き換える。）

## 根拠 1: 初回投稿 manuscript（`data/revise1/①Medcomm_初回投稿_manuscript.docx`）

Procedures:

> The enrolled women were classified by RO estimated using the deep learning application, OPSCAN:
> osteoporotic precise screening using chest radiography and an artificial neural network,[16] which
> yields risk score as a continuous variable [0-1]). As the output of the model was to predict the
> T-score, a higher risk score correlated with a lower T-score.[17] The RO score was used for
> classification; the cutpoint was set according to the incidence of osteopenia in premenopausal
> women.[12-14]

Deep learning model:

> The present study utilized the DL application, OPSCAN.[16] It was based on DenseNet architecture
> and developed using 48353 chest radiography correspondence to T-scores.[17] As the patient age for
> the matched data was 20 years or older, those with osteoporosis, osteopenia, and a normal range of
> T-scores were widely included. Furthermore, the model's efficacy was confirmed by RCTs which aimed
> to identify individuals at high risk of osteoporosis.[16]

引用文献:

> 16. Lin C, Tsai D-J, Wang C-C, Chao YP, Huang J-W, Lin C-S, et al. Osteoporotic Precise Screening
> Using Chest Radiography and Artificial Neural Network: The OPSCAN Randomized Controlled Trial.
> Radiology. 2024;311(3):e231937.
> 17. Tsai DJ, Lin C, Lin CS, Lee CC, Wang CH, Fang WH. Artificial Intelligence-enabled Chest X-ray
> Classifies Osteoporosis and Identifies Mortality Risk. J Med Syst. 2024;48(1):12.

manuscript / 査読コメント / スプレッドシートのいずれにも GitHub URL の記載は無い
（Availability of data and materials は患者データの非公開のみ）。

## 根拠 2: OPSCAN の GitHub リポジトリ（著者がモデルを取得して実行した先）

**https://github.com/xup6fup/OPSCAN**（Web 検索で特定。README の "Related publications" が
ref 16 = Radiology 2024;311(3):e231937 なので同一物と判断）。
R 3.4.4 + MXNet 1.3.0。最終 push 2025-01-01（README 更新）、`model/` の更新は 2023-09-14 の
"Update model" が最後。

### リポジトリで確認できたこと（README / コードからの引用）

| 項目 | 内容 | 根拠 |
|---|---|---|
| モデル名 | OPSCAN（Osteoporotic Precise Screening using Chest radiography and Artificial neural network）。学習済みファイル名は `model/OPSCAN-0000.params` / `model/OPSCAN-symbol.json` | README, `model/` |
| 入力前処理 | アスペクト比を保って短辺 256 px にリサイズ（グレースケール化して 3ch に複製）。学習時は 224×224 のランダムクロップ + 50% 左右反転。推論時は 10-crop（4 隅 + 中央 × 反転あり/なし）の平均 | `D01. pre-processing.R`, `M01. cxr_process_core.R`, `P01. predicting.R` |
| ネットワーク入力サイズ | `data = c(224, 224, 3, batch_size)` | `P01. predicting.R` |
| 出力 | `fc1 (num_hidden = 1)` → `sigmoid` の 1 値（`logistic_pred`）。10 crop の平均を `final_pred` とする。ラベル OP = T-score ≤ −2.5 の 2 値 | `M02. architecture.R`, `P01. predicting.R`, README |
| 学習 | Cross-entropy、Adam、batch 32、lr 1e-3→1e-4→1e-5、weight decay、early stopping、クラス重みによる oversampling | README, `M03. run.R` |
| 対象骨領域 | **骨領域の切り出しや ROI 指定は無い**。PA 胸部X線全体（256 短辺 → 224 クロップ）をそのまま入力する | `D01`, `M01` |

README 引用:

> Data preprocessing can be conducted using the D01. pre-processing.R, which resizes the CXRs while
> maintaining their aspect ratio, ensuring that the shorter side is adjusted to 256 pixels.

> During our model training, we opted to incorporate random cropping of a 224 × 224-pixel region as
> input, combined with a 50% likelihood of implementing a random horizontal flip. At the inference
> phase, we utilized a 10-crop evaluation approach, resulting in ten distinct probabilities for each
> CXR. The ultimate prediction was determined by averaging these ten probabilities.

> Osteoporosis (designated as the "OP" column) is defined as a T-score <= -2.5.

> In this instance, we utilized the resnet-18 due to its minimal size and rapid execution speed.
> However, you are free to substitute it with any other model of your preference.

### ⚠ 重要: リポジトリに置かれているモデルは DenseNet ではなく ResNet-18

`model/OPSCAN-symbol.json` を解析した結果:
- 171 ノード中 170 ノードが同梱の `model/resnet-18-symbol.json`（MXNet model zoo の ImageNet 学習済み
  ResNet-18）と一致し、末尾だけ `fc1(1) → sigmoid` に差し替えられている
- 層名は `stage1_unit1_conv1` … の ResNet 命名、Convolution 21 / `elemwise_add`（残差結合）8、
  DenseNet に必須の `Concat` は 0
- `M02. architecture.R` も `mx.model.load(prefix = "model/resnet-18")` の `flatten0_output` に
  `fc1` を載せているだけ

つまり **GitHub から取得して実行したのが `model/OPSCAN-0000.params` なら、走らせたのは
ResNet-18 ベースのモデル**であり、manuscript の "based on DenseNet architecture"（および査読者が
例示した DenseNet）と食い違う。論文（ref 17 の抄録・二次資料）では DenseNet と記載されている
ので、公開リポジトリのモデルが「論文の本番モデル」なのか「README の説明用に resnet-18 で組んだ
デモ」なのかはリポジトリからは判別できない（README は "Due to privacy concerns, we are unable to
provide real patient data … the syntax for model training is available" とし、同梱 label.csv の
T-score も "predicted using the final version of our AI-CXR model" と書いている）。

→ **著者に確認必須**: 実際に使ったのが (a) リポジトリ同梱の `OPSCAN-0000.params`（= ResNet-18）か、
(b) 原著者から別途提供された DenseNet モデルか。(a) なら図の "DenseNet-based" は
"ResNet-18-based" に直し、本文 Methods も合わせる必要がある。図の文言は差し替えるだけなので、
`make` 相当の再生成は不要（drawio の該当セルを書き換える）。

### リポジトリから分からないこと

- DenseNet の深さ（DenseNet-121 等）— リポジトリには DenseNet 自体が無い
- 論文の本番モデルの重みそのもの（同梱重みがそれかどうか）
- 「高リスク」のカットオフ値 — RCT 解析コードには `Group %in% 'Low risk'` のようにラベル済み
  データしか無く、しきい値の数値は無い
- Grad-CAM / saliency のコード（無い）。したがって「対象骨格領域」はリポジトリからも言えない
  （モデルは胸部X線全体を見る）

### ref 17（J Med Syst 2024）で確認できたこと

Europe PMC 抄録: 48,353 CXR（学習 35,633 / 検証 12,720）、内部 AUC 0.930 / 外部 0.892。
本文（Springer）は購読制で取得できず。Web 検索の要約では「DenseNet、短辺 256 リサイズ、224 ランダム
クロップ、batch 32、Adam lr 0.001」とあり、前処理はリポジトリと一致する。

## 著者への確認事項（open questions）

1. **DenseNet か ResNet-18 か**（上記）。図と本文の整合に直結する最優先事項。
2. **対象骨格領域**: 査読者は "target skeletal regions" を例示しているが、manuscript にもリポジトリにも
   記載が無く、モデルは胸部X線全体を入力にしている。図には入れていない。Reviewer 2 Major #2
   （Grad-CAM）の回答で "the model uses the whole PA chest radiograph without region cropping" と
   説明するのが正確。Grad-CAM で胸椎・鎖骨などへの注視が確認できれば legend に 1 文追加できる。
3. **カットオフ値**（Reviewer 1 #5 / Reviewer 2 Major #1）: 確定後、legend の "prespecified cutpoint"
   と図の "→ High RO / Low RO" の間に値を入れるか判断。
4. **図のサイズ規定**: 図は縦長（縦/横 = 1.52、rev0 も 1.55）。170 mm 幅だと高さ 258 mm で 210 mm
   上限超過、210 mm 高さに収めると幅 138 mm。フローを 2 列に組み替えれば 170×≤210 mm に入るが、
   デザイン変更が大きいので著者判断。フォントは 138 mm 幅で置いた場合、追加行 22 px ≈ 10.6 pt /
   18 px ≈ 8.7 pt、本文 28 px ≈ 13.8 pt、タイトル 41 px ≈ 20 pt（8–10 pt 規定内）。
5. 単一パネルなのでパネルラベル（A, B…）は付けていない。

## 再レンダリング

```sh
# drawio CLI（/usr/bin/drawio）。headless では --no-sandbox --disable-gpu が必要
drawio --no-sandbox --disable-gpu -x -f png -s 4 -b 20 \
  -o out/rev1/fig1.png data/fig1/fig1_rev1.drawio
# PDF / SVG が要る場合は -f pdf / -f svg
```

`-s 4` で 800 px 幅のページを 4 倍にレンダリング（3174×4826 px）。170 mm 幅で貼ると約 474 dpi、
138 mm 幅なら約 584 dpi で、300 dpi 要件は満たす。

## 追記（メインセッション）

- High RO / Low RO の N を旧カットオフの 425 / 360 から、新カットオフ（`REVISE_MEDCOMM_KM_遠田.xlsx` の RO group）の **440 / 345** に更新。Fig3 A の LRO/HRO の n と一致させた

## 追記（メインセッションで OPSCAN リポジトリを直接検証、2026-09-21）

`git clone https://github.com/xup6fup/OPSCAN` して `model/` を解析した。

| 項目 | 内容 |
|---|---|
| `model/` の中身 | `OPSCAN-symbol.json` / `OPSCAN-0000.params` と `resnet-18-symbol.json` / `resnet-18-0000.params` の 4 ファイルのみ。DenseNet の定義・重みは無い |
| `OPSCAN-symbol.json` の構成 | Convolution 21 / BatchNorm 19 / elemwise_add 8 / Concat 0。層名は `stage1_unit1_conv1`, `stage1_unit1_sc` … の MXNet ResNet 命名。resnet-18-symbol.json と出力層以外同一（fc1 が 1000→1、Softmax→sigmoid） |
| `OPSCAN-0000.params` の重み名 | `conv0, bn0, stage1_unit1_conv1 …, fc1` の 99 配列。ResNet-18 の構成と一致 |
| ファイルサイズ | resnet-18 46.8 MB − fc(512×1000×4 B ≈ 2.0 MB) ≈ 44.8 MB = OPSCAN の 44.76 MB。DenseNet-121（約 8M パラメータ ≈ 32 MB）とは合わない |
| 重みは学習済みか | ImageNet resnet-18 の 64 KB 断片 12 個を OPSCAN 側で検索して一致 0/12 → 全層の重みが更新されている（fine-tune 済み） |
| README の位置づけ | 「we utilized the resnet-18 due to its minimal size」「this is merely a demonstration」。同梱データは ChestX-ray14 の 100 枚で、その T-score ラベルは「final version of our AI-CXR model で予測した値」 |

結論: リポジトリにあるのは ResNet-18 だけで、DenseNet は存在しない。同梱の `OPSCAN-0000.params` が
本番モデルか README のデモ（100 枚で学習）かはファイルからは判別できないが、README の記述は
デモを示唆している。原稿の「DenseNet」は ref 17（Tsai DJ et al., J Med Syst 2024;48(1):12）由来。

## 決定（ken、2026-09-21）

著者は GitHub の重みではなく **web で提供されているサービス**（本番モデル）で RO を算出したとのこと。
よって本文は変更せず、図も「OPSCAN (DenseNet-based CNN)」のままとする。上の ResNet-18 の件は
GitHub 同梱デモの話であり、本論文には影響しない扱いで閉じる。

## 追記（2026-09-21）: Youden 閾値に追従

High RO / Low RO の N を Youden 閾値（RO ≥ 0.291）の **276 / 509** に更新。Fig3 A と一致。

## 80 mm 幅（1 段組）向けの再レイアウト（2026-09-21）

前提: 図の内容幅 753.5 px（PNG 3174 px ÷ `-s 4` − 余白 20×2）を 80 mm に割り当てる。
1 px = 0.1062 mm = **0.3010 pt**（1 pt = 0.3528 mm）。内容幅は再レイアウト前後で不変（最も幅の広い
Outcomes 行を触っていない）ので、換算係数も前後で同じ。

### フォントサイズ（80 mm 幅時、drawio px → pt）

| 要素 | before (px → pt) | after (px → pt) |
|---|---|---|
| AI model（タイトル） | 41 → 12.3 | 41 → 12.3 |
| Multicenter retrospective cohort / Outcomes | 36 → 10.8 | 36 → 10.8 |
| High RO / Low RO / Primary / Secondary / 各アウトカム | 32 → 9.6 | 32 → 9.6 |
| Enrolled women… / Exclusion… / Input… / Output… / N= | 28 → 8.4 | 28 → 8.4 |
| OPSCAN (DenseNet-based CNN) | 22 → **6.6** | **28 → 8.4** |
| continuous score 0–1 → High RO / Low RO | 18 → **5.4** | **28 → 8.4**（文言短縮: "Score 0–1 → High RO / Low RO"） |

8 pt 未満だったのは AI model ボックス内の追加 2 行だけで、両方とも本文と同じ 28 px（8.4 pt）に
上げた。6 pt に落とした要素は無い。

### 変更内容（`data/fig1/fig1_rev1.drawio`）

- N ラベル: High RO **N=440** / Low RO **N=345**（合計 785）
- AI model ボックス 480×290 → 480×**320**（y=290–610）。中の配置: Input y=350 / OPSCAN y=390 (h34) /
  AI アイコン 150→**120 px**（x=340, y=422）/ Output y=538 / Score 行 y=572 (h34)
- ボックスより下の要素（分岐矢印・High/Low RO ボックス・Outcomes 一式）を一律 **+30 px** 下げた。
  横位置・色・矢印の形は変えていない
- 文言変更は "continuous score 0–1 → High RO / Low RO" → "Score 0–1 → High RO / Low RO" のみ

### 出力サイズ

- `out/rev1/fig1.png`: **3174 × 4946 px**（`-s 4`, `-b 20`）
- 80 mm 幅で貼ると **80 × 127.0 mm**（縦横比 1.59。210 mm 高さ上限内）、**約 1008 dpi**（300 dpi 要件 OK。
  必要なら `-s 6` で 4761 px 幅だが不要）
- 目視確認: 重なり無し。AI アイコンを 120 px にしたぶん Output 行との間隔は確保されている

## 書き出し（2026-09-21）

`uv run python rev1/fig1.py` が drawio CLI で PNG と PDF を書き出し、後処理する:
- PNG: 幅 80 mm で 600 dpi 相当になる倍率で出力し、dpi メタデータを付ける
- PDF: drawio の出力（554 × 873 pt）を pypdf でページごと 80 mm 幅に縮小（文字はベクタのまま、Arial 埋め込み）
