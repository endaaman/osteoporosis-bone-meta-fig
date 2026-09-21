---
title: "MedComm revise 1 図の納品メモ"
author: "遠田"
date: "2026-09-21"
---

# 納品物

`out/rev1/` に入っています。グラフ類は PDF、Figure 2 は TIFF をご提出ください。

| 新番号 | 内容 | ファイル |
|---|---|---|
| Figure 1 | Study design（AI model ボックスに OPSCAN / DenseNet を追記、High/Low RO の N を更新） | fig1.pdf |
| Figure 2 | Grad-CAM 代表例 A–D | fig2.pdf / fig2.tiff |
| Figure 3 | KM 曲線（B/C に HR・95%CI・p） | fig3.pdf |
| Figure 4 | Age と RO の散布図。AB 版と ABC 版の 2 種 | fig4_ab.pdf / fig4_abc.pdf |
| Figure 5 | A DXA 施行率（白抜き柱・症例数）、B T-score と RO（全体）、C 同（閉経前） | fig5.pdf |

編集部の図の規定（サイズ・フォント・パネルラベル・解像度・白抜き柱）は満たしています。

# 変更点

## HRO/LRO のカットオフ

Reviewer 2 Major 1 の求めに沿って、Youden index で導出した閾値 **RO 0.1** を用いています。

- 対象: 閉経前で周術期 DXA を受け T-score のある 37 例。陽性 = 骨減少症以上（T-score ≤ −1、11 例）。
- 結果: RO ≥ 0.10（感度 0.73、特異度 0.85、AUC 0.80）。
- Figure 3 の結果: 全体 HRO 440 / LRO 345、log-rank p = 0.25、HR 1.27（0.85–1.89）。閉経前 HRO 87 / LRO 238、p = 0.04、HR 1.91（1.01–3.59）。閉経後 HRO 353 / LRO 107、p = 0.65、HR 0.87（0.49–1.55）。

## 相関係数

全図 Spearman（rs）に統一しました。RO スコアは 0〜1 に丸められて 0 付近に固まった歪んだ分布で、T-score との関係もシグモイド由来の S 字なので、直線と正規分布を前提にする Pearson より順位ベースの Spearman が適切と判断しました。初回投稿の Figure 3 b（現 Figure 5 B）は元々 Spearman で、査読者が引用している r = −0.64 もその値です。

| 図 | いただいた値 | 図の値 |
|---|---|---|
| Fig4 A 全体 | r=0.61, n=785 | rs=0.66, n=785 |
| Fig4 B 閉経前 | r=0.21, n=325 | rs=0.22, n=325 |
| Fig4 C 閉経後 | r=0.45, n=460 | rs=0.46, n=460 |
| Fig5 A | 38/325, 346/460 | 同じ。χ² p<0.01 |
| Fig5 B 全体 | r=−0.64, n=384 | rs=−0.64（T-score のある 381 例） |
| Fig5 C 閉経前 | r=−0.58, n=38 | rs=−0.61（T-score のある 37 例） |

- Fig5 B・C は周術期 DXA ありのうち T-score が記入されている例（381 / 37）で計算しています。いただいた 384 / 38 は DXA ありの例数で、T-score 未記入の 3 例 / 1 例を含みます。図中には n を出さず、legend に記載します。
- Fig5 C のいただいた r=−0.58 は、Excel の CORREL の範囲が A4 始まりで先頭 2 例が抜けていました（33 例の Pearson）。図は全 37 例の Spearman です。

# ご確認いただきたい点

1. Figure 5 A の閉経後の施行率は図では 346/460 = 75.2% ですが、本文・抄録は 76.4%（346/453、DXA 欄が空欄または「2」の 7 例を除いた分母）です。どちらかにそろえる必要があります。
2. Reviewer 2 Major 1（カットオフの統計的根拠）への回答文は、上記の Youden の数値を使ってご執筆ください。Methods への追記文案は末尾に載せています。
3. 群分けが 425/360 から 440/345 に変わるため、Table 1・Table 2（多変量 Cox）・HRO/LRO の年齢中央値など、群を分母にした本文の数値は再計算が必要です（こちらの手元には特徴量データが無いので対象外です）。

# 本文で更新が必要になる数値（参考）

| 項目 | 初回投稿 | revise |
|---|---|---|
| 図番号 | Fig2 KM / Fig3 DXA・T-score | Fig3 KM / Fig5 DXA・T-score（Fig2 Grad-CAM、Fig4 Age–RO を新設） |
| カットオフ | 閉経前骨減少症の有病率に基づく（値の記載なし） | Youden index、RO ≥ 0.10（感度 0.73 / 特異度 0.85 / AUC 0.80） |
| HRO / LRO | 425 / 360 | 440 / 345 |
| 閉経前の HRO / LRO | 75 / 250 | 87 / 238（26.8%） |
| 閉経後の HRO / LRO | 350 / 110 | 353 / 107 |
| 閉経前 KM | p<0.01 | p=0.04, HR 1.91 (1.01–3.59) |
| 閉経後 KM | p=0.65 | p=0.65, HR 0.87 (0.49–1.55) |
| 全体 KM | p=0.16 | p=0.25, HR 1.27 (0.85–1.89) |
| Age–RO（Spearman） | — | 全体 rs=0.66 / 閉経前 0.22 / 閉経後 0.46（n 785 / 325 / 460、いずれも p<0.01） |
| T-score–RO（Spearman） | 全体 −0.64 | 全体 −0.64 (n=381) / 閉経前 −0.61 (n=37) |
| Methods の相関の記述 | Pearson | Spearman に修正 |
| DXA 施行率 | 11.7% / 76.4% | 11.7% / 75.2%（分母による） |

# Figure legends 案（英語）

図の内容に合わせた下書きです。[ ] は先生にご記入いただく箇所です。

**Figure 1. Study design.** Flow chart of patient selection and analysis. Perioperative chest radiographs of 785 women with clinical stage 2–3, estrogen receptor-positive, HER2-negative early-stage breast cancer were analyzed with OPSCAN, a DenseNet-based convolutional neural network trained on 48,353 chest radiographs paired with DXA T-scores, which outputs a continuous risk of osteoporosis (RO) score (0–1); a higher score corresponds to a lower predicted T-score [16, 17]. Women were dichotomized into high RO (HRO, RO ≥ 0.1; n = 440) and low RO (LRO, RO < 0.1; n = 345) groups using the cut-off that maximized the Youden index for osteopenia or worse (T-score ≤ −1) among premenopausal women who underwent perioperative DXA, and 5-year bone metastasis-free survival was compared with stratification by menopausal status (premenopausal, n = 325; postmenopausal, n = 460). eBC, early-stage breast cancer; ER, estrogen receptor; HER2, human epidermal growth factor receptor 2; BMA, bone-modifying agent; DXA, dual-energy X-ray absorptiometry; RO, risk of osteoporosis; HRO, high risk of osteoporosis; LRO, low risk of osteoporosis.

**Figure 2. Gradient-weighted class activation mapping (Grad-CAM) of the deep learning model on perioperative chest radiographs.** Representative Grad-CAM saliency maps of the OPSCAN model overlaid on posteroanterior chest radiographs of four women in the cohort. Warmer colors indicate regions that contributed more to the predicted risk of osteoporosis (RO) score. (A) [HRO case, RO = 0.xx, T-score −x.x]. (B) [LRO case, RO = 0.xx, T-score +x.x]. (C) [case with …]. (D) [case with an implanted cardiac device, RO = 0.xx]. Grad-CAM, gradient-weighted class activation mapping; RO, risk of osteoporosis; HRO, high risk of osteoporosis; LRO, low risk of osteoporosis.

**Figure 3. Univariate analyses for 5-year bone metastasis-free survival stratified by menopausal status.** Kaplan–Meier curves of bone metastasis-free survival (BMFS) after surgery according to the deep learning-derived risk of osteoporosis in (A) all enrolled women (n = 785; LRO n = 345, HRO n = 440), (B) premenopausal women (n = 325; LRO n = 238, HRO n = 87) and (C) postmenopausal women (n = 460; LRO n = 107, HRO n = 353). HRO was defined as RO ≥ 0.1 (Youden index). Tick marks indicate censored observations, and the numbers of women at risk at 0, 20, 40 and 60 months are shown below each panel. P values are from the log-rank test. In (B) and (C), hazard ratios (HR) with 95% confidence intervals (CI) of HRO versus LRO were estimated by univariate Cox proportional hazards regression. BMFS, bone metastasis-free survival; LRO, low risk of osteoporosis; HRO, high risk of osteoporosis; HR, hazard ratio; CI, confidence interval.

**Figure 4. Relationship between age and the deep learning-derived risk of osteoporosis.** Scatter plots of the continuous risk of osteoporosis (RO) score (0–1) against age at surgery in (A) all enrolled women (n = 785; rs = 0.66, p < 0.01), (B) premenopausal women (n = 325; rs = 0.22, p < 0.01) [and (C) postmenopausal women (n = 460; rs = 0.46, p < 0.01)]. Each dot represents one woman. rs, Spearman rank correlation coefficient (two-sided). RO, risk of osteoporosis.

（AB 版を使う場合は (C) の一文を削除してください。）

**Figure 5. Perioperative bone density test and the deep learning-derived risk of osteoporosis.** (A) Conduction rate of perioperative bone density testing in premenopausal (38 of 325 women, 11.7%) and postmenopausal (346 of 460 women, 75.2%) women; hollow bars show the proportion with the number of women above each bar (chi-square test, **p < 0.01). (B) Correlation between DXA T-score and the continuous risk of osteoporosis (RO) score in all women who underwent bone density testing (n = 381; rs = −0.64, p < 0.01). (C) Correlation between T-score and RO score in premenopausal women who underwent bone density testing (n = 37; rs = −0.61, p < 0.01). Each dot represents one woman. rs, Spearman rank correlation coefficient (two-sided). DXA, dual-energy X-ray absorptiometry; RO, risk of osteoporosis.

# Methods の修正文案

- 相関: 「The Pearson correlation coefficient was used to measure the linear correlation between the two sets of data.」→「Spearman rank correlation coefficient was used to assess the association between the two sets of data.」
- カットオフ: 「The cut-off of the RO score (0.1) was determined by the Youden index on the receiver operating characteristic curve for osteopenia or worse (T-score ≤ −1) among premenopausal women who underwent perioperative DXA (n = 37; sensitivity 0.73, specificity 0.85, area under the curve 0.80).」を追記。
