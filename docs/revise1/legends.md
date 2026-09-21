> **注（2026-09-21）**: カットオフを Youden index（RO ≥ 0.29）に変更したため、Figure 1 の N（276 / 509）、Figure 3 の n・HR・p は変わった。最新の legend は `memo_shimizu.md` を正とする。

# Revise 1 — Figure legends (draft) and numbers for the text

Draft legends for the revised manuscript (MedComm, MCO2-2026-7590, revise 1), written to match what
`out/rev1/fig*.png` actually shows. Style follows the original legends (title sentence, panel
descriptions, statistical test in parentheses, abbreviations at the end), with the additions the
editor and Reviewer 2 asked for (exact n for every statistic; HR / 95% CI / p in the KM plots;
AI details for Figure 1).

Sources of numbers, notation used below:

- **[computed]** … reproduced from the data in this repo (`docs/revise1/figN.md`, `rev1/figN.py`)
- **[author]** … value supplied by the author (`README.md` "著者提供の統計値", KM/相関 xlsx)
- **[ms]** … value in the first-submission manuscript (`data/revise1/①Medcomm_初回投稿_manuscript.docx`)
- **⚠** … still disputed / needs author confirmation before submission

Panel labels in the figures are uppercase (A, B, C) per the editor's instruction, so the legends use
"(A)", "(B)" … instead of the original "a)", "b)".

---

## Figure 1. Study design

> **Figure 1. Study design.** Flow chart of patient selection and analysis. Of 862 women who
> underwent surgery for clinical stage 2–3, estrogen receptor-positive, HER2-negative breast cancer
> between 2007 and 2019, 77 were excluded (male sex, bilateral breast cancer, no perioperative chest
> radiograph, or perioperative use of bone-modifying agents for osteoporosis), leaving 785 women.
> Perioperative chest radiographs were analysed with OPSCAN (Osteoporotic Precise Screening using
> Chest radiography and Artificial neural Network), a DenseNet-based convolutional neural network
> trained on 48,353 chest radiographs paired with DXA T-scores, which outputs a continuous risk of
> osteoporosis (RO) score (0–1); a higher score corresponds to a lower predicted T-score [16, 17].
> The whole posteroanterior chest radiograph is used as input without cropping to a specific skeletal
> region. Women were dichotomized into high RO (HRO, n = 440) and low RO (LRO, n = 345) groups
> [at the prespecified cut-off], and 5-year bone metastasis-free survival was compared with
> stratification by menopausal status (premenopausal, n = 325; postmenopausal, n = 460).
> eBC, early-stage breast cancer; ER, estrogen receptor; HER2, human epidermal growth factor
> receptor 2; BMA, bone-modifying agent; DXA, dual-energy X-ray absorptiometry; RO, risk of
> osteoporosis; HRO, high risk of osteoporosis; LRO, low risk of osteoporosis.

Sources / notes:

- 862 / 77 / 785 — [ms] Methods. 48,353 — [ms] Methods "Deep learning model".
- HRO 440 / LRO 345 — [computed] from the new `RO group` column (`fig3.md`); Fig1 was updated to
  these values (`fig1.md` 追記). The first submission had 425 / 360.
- "DenseNet-based" — kept per ken's decision 2026-09-21 (`fig1.md` 決定): the author used the web
  service (production model), not the GitHub ResNet-18 demo. Citation moved out of the figure into
  the legend: [16] Lin C et al. Radiology 2024;311(3):e231937; [17] Tsai DJ et al. J Med Syst
  2024;48(1):12.
- "without cropping to a specific skeletal region" — the reviewer asked for "target skeletal
  regions" in the AI box; the model has no ROI (`fig1.md` 根拠 2). Keep the sentence only if the
  author agrees; it is the accurate answer to Reviewer 2 Minor 2 / Major 2.
- **[at the prespecified cut-off]** — placeholder. The group assignment in the KM xlsx is
  reproduced by *menopause-specific* thresholds (pre: RO ≥ 0.102, post: RO ≥ 0.110; `fig3.md`
  推定). ⚠ Reviewer 1 #5 and Reviewer 2 Major 1 demand the exact value and a data-driven
  justification; the author has not stated the rule. Replace with e.g. "at RO ≥ 0.102 in
  premenopausal and ≥ 0.110 in postmenopausal women" once confirmed.
- Single panel, no A/B label.

---

## Figure 2. Grad-CAM visualisation

> **Figure 2. Gradient-weighted class activation mapping (Grad-CAM) of the deep learning model on
> perioperative chest radiographs.** Representative Grad-CAM saliency maps of the OPSCAN model
> overlaid on posteroanterior chest radiographs of four women in the cohort. Warmer colours (yellow
> to red) indicate regions that contributed more to the predicted risk of osteoporosis (RO) score;
> cooler colours (purple to black) indicate low contribution. (A) [HRO case, RO = 0.xx, T-score
> −x.x; premenopausal/postmenopausal]. (B) [LRO case, RO = 0.xx, T-score +x.x; …]. (C) [case with
> … ; RO = 0.xx]. (D) [case with an implanted cardiac device; RO = 0.xx, …]. [Activation is
> concentrated on skeletal structures (thoracic spine, ribs, clavicles) rather than on surgical
> clips, ports or devices.] Grad-CAM, gradient-weighted class activation mapping; RO, risk of
> osteoporosis; HRO, high risk of osteoporosis; LRO, low risk of osteoporosis.

Sources / notes:

- The four input images carry no colour bar, patient information or RO value (`fig2.md`); every
  bracketed item is a **placeholder** the author must fill in (which case is HRO/LRO, RO score,
  T-score if DXA was done, menopausal status).
- Colour description (magma-type map, purple → red → yellow) — [computed] from the images
  (`fig2.md` 入力画像の内容).
- Panel D visibly contains a cardiac device (`fig2.md`); the last bracketed sentence is what
  Reviewer 2 Major 2 wants confirmed, but by `fig2.md` the activations in A–D sit largely over the
  mediastinum / lung fields, ⚠ so do **not** keep that sentence unless the author verifies it on
  the full-resolution maps. Also confirm the string of characters visible in C is not patient
  information (`fig2.md` 問題点 4).
- No statistics in this figure; no n needed beyond "four women".

---

## Figure 3. Kaplan–Meier curves (old Figure 2)

> **Figure 3. Univariate analyses for 5-year bone metastasis-free survival stratified by
> menopausal status.** Kaplan–Meier curves of bone metastasis-free survival (BMFS) after surgery
> according to the deep learning-derived risk of osteoporosis in (A) all enrolled women (n = 785;
> LRO n = 345, HRO n = 440), (B) premenopausal women (n = 325; LRO n = 238, HRO n = 87) and
> (C) postmenopausal women (n = 460; LRO n = 107, HRO n = 353). Tick marks indicate censored
> observations, and the numbers of women at risk at 0, 20, 40 and 60 months are shown below each
> panel. P values are from the log-rank test. In (B) and (C), hazard ratios (HR) with 95%
> confidence intervals (CI) of HRO versus LRO were estimated by univariate Cox proportional hazards
> regression: premenopausal women, HR 1.91 (95% CI 1.01–3.59), p = 0.04; postmenopausal women,
> HR 0.84 (95% CI 0.46–1.51), p = 0.56. BMFS, bone metastasis-free survival; LRO, low risk of
> osteoporosis; HRO, high risk of osteoporosis; HR, hazard ratio; CI, confidence interval.

Sources / notes:

| Item | Value in figure | Source | Status |
|---|---|---|---|
| A: n, LRO/HRO | 785; 345 / 440 | fig3.md [computed] | OK |
| A: log-rank p | p = 0.32 (0.324) | fig3.md [computed] | not provided by author; only p shown, no HR (author asked HR for B/C only). Computed Cox HR 1.22 (0.82–1.82) if wanted for text |
| B: n, LRO/HRO | 325; 238 / 87 | fig3.md [computed] | OK (rev0 was 250 / 75) |
| B: log-rank p | p = 0.04 (0.041) | [computed] = [author] | OK. Note Cox Wald p = 0.045; the "0.04" in the figure is the log-rank p |
| B: HR (95% CI) | 1.91 (1.01–3.59) | [computed] = [author] | OK |
| C: n, LRO/HRO | 460; 107 / 353 | fig3.md [computed] | OK (rev0 was 110 / 350) |
| C: log-rank p | p = 0.56 (0.564) | [computed] = [author] | OK |
| C: HR | 0.84 (0.845) | [computed] = [author] | OK |
| C: 95% CI | **0.46–1.51** | **[author]**, used in figure (`PROVIDED[...]['use_provided']=True`) | ⚠ computed (Efron and Breslow) is **0.48–1.50**. The author's CI is not symmetric on the log scale around 0.84 — likely a transcription slip or different software. Table 2 in the text must match whichever is chosen |
| Events (for text) | A 40/60, B 24/16, C 16/44 (LRO/HRO) | fig3.md [computed] | not drawn (table reduced to "At risk" only) |

Number at risk (t = 0/20/40/60 months) [computed]: A LRO 345 336 321 305, HRO 440 413 391 369;
B LRO 238 235 225 215, HRO 87 84 80 71; C LRO 107 101 96 90, HRO 353 329 311 298.

---

## Figure 4. Age vs RO (new)

Two layouts exist: `fig4_ab` (A, B only; 170 × 76.5 mm) and `fig4_abc` (A, B, C; 169 × 58 mm).
Both show, in each panel, a boxed "r = / n = / p" text; no regression line.

### Version 1 — `fig4_ab` (A–B only)

> **Figure 4. Relationship between age and the deep learning-derived risk of osteoporosis.**
> Scatter plots of the continuous risk of osteoporosis (RO) score (0–1) against age at surgery in
> (A) all enrolled women (n = 785; r = 0.61, p < 0.01) and (B) premenopausal women (n = 325;
> r = 0.21, p < 0.01). Each dot represents one woman. r, Pearson correlation coefficient; p values
> are two-sided (Pearson correlation). RO, risk of osteoporosis.

### Version 2 — `fig4_abc` (A–C)

> **Figure 4. Relationship between age and the deep learning-derived risk of osteoporosis.**
> Scatter plots of the continuous risk of osteoporosis (RO) score (0–1) against age at surgery in
> (A) all enrolled women (n = 785; r = 0.61, p < 0.01), (B) premenopausal women (n = 325;
> r = 0.21, p < 0.01) and (C) postmenopausal women (n = 460; r = 0.45, p < 0.01). Each dot
> represents one woman; axes are identical across panels. r, Pearson correlation coefficient;
> p values are two-sided (Pearson correlation). RO, risk of osteoporosis.

Sources / notes:

| Panel | n | r | p | Source | Status |
|---|---|---|---|---|---|
| A all | 785 | 0.61 (0.615) | < 0.01 (9.3e-83) | fig4.md [computed] = [author] | OK |
| B pre | 325 | 0.21 (0.205) | < 0.01 (2.0e-04) | fig4.md [computed] = [author] | OK |
| C post | 460 | 0.45 (0.446) | < 0.01 (8.2e-24) | fig4.md [computed] = [author] | OK |

- The author's r values are **Pearson** (Excel `CORREL`), matched to 2 decimals; Spearman would be
  0.66 / 0.22 / 0.46 (`fig4.md`). Figure 5 B/C use **Spearman** (see below), so the two figures
  use different correlation methods — each legend names its own method. ⚠ The Methods sentence
  "The Pearson correlation coefficient was used…" [ms] needs to say both, e.g. "Pearson correlation
  for age vs RO (Figure 4) and Spearman rank correlation for T-score vs RO (Figure 5)", unless the
  author decides to unify (conclusions do not change either way).
- The author's Excel p values are wrong for A and C (degrees of freedom fixed at 326−2 in every
  sheet; `fig4.md`); the figure uses recomputed p, which is < 0.01 in all panels anyway.
- This figure answers Reviewer 2 Major 3 (age confounding in the premenopausal subgroup). For the
  response letter: the weak correlation in premenopausal women (r = 0.21, r² ≈ 0.04) means age
  explains ~4% of the RO variance in that subgroup.

---

## Figure 5. Bone density test and RO (old Figure 3 + new premenopausal panel)

> **Figure 5. Perioperative bone density test and the deep learning-derived risk of osteoporosis.**
> (A) Conduction rate of perioperative bone density testing (lumbar DXA within two years of
> surgery) in premenopausal (38 of 325 women, 11.7%) and postmenopausal (346 of 460 women, 75.2%)
> women; hollow bars show the proportion with the number of women above each bar (chi-square test,
> **p < 0.01). (B) Correlation between DXA T-score and the continuous risk of osteoporosis (RO)
> score in all women who underwent bone density testing (n = 381). (C) Correlation between T-score
> and RO score in premenopausal women who underwent bone density testing (n = 38). Each dot
> represents one woman. rs, Spearman rank correlation coefficient (Spearman rank correlation, two-
> sided): (B) rs = −0.64, p < 0.01; (C) rs = −0.58, p < 0.001. DXA, dual-energy X-ray
> absorptiometry; RO, risk of osteoporosis.

Sources / notes:

| Item | Value in figure | Source | Status |
|---|---|---|---|
| A pre | 38/325 (11.7%) | fig5.md [computed] = [author] = [ms] | OK |
| A post | 346/460 (**75.2%**) | fig5.md [computed]; 346/460 [author] | ⚠ The manuscript text and abstract say **76.4%** = 346/453 (denominator excludes 3 DXA-unknown and 4 "presence = 2" women; `docs/rev0/memo.md`). The figure divides by all 460. Either change the text to 75.2% (346/460) or change the figure denominator to 453 — must match |
| A p | p < 0.01 (χ² = 305.0, p = 2.7e-68, Yates-corrected) | fig5.md [computed] | OK; text says p < 0.001 in Results, p < 0.01 in Abstract — harmonise |
| B rs | −0.64 (−0.6405) | fig5.md [computed] = [author] = [ms] | OK — this is **Spearman**; Pearson would be −0.60 |
| B n | **381** (drawn) | fig5.md [computed] | ⚠ author says **n = 384** (= all DXA-done women). 3 of them have no numeric T-score (ID 5 blank, ID 29 "3.4 dish?", ID 2130 blank), so only 381 points exist and are plotted; the figure shows 381 |
| B p | p < 0.01 (2.2e-45) | [computed] = [author] | OK |
| C rs | **−0.58** | **[author]** (`FIXED['C']`) | ⚠ not reproducible: Spearman on the 37 CSV pairs = −0.61, Pearson = −0.55; on the author's 35-pair sheet Spearman = −0.66, Pearson = −0.57. Author's t-statistic reproduces only with r = −0.5822 and n = 38 (blank rows counted). Ask the author how −0.58 was obtained; fallback `--computed` gives rs = −0.61, n = 37, p < 0.01 |
| C n | **38** | [author] | ⚠ 38 = premenopausal women with DXA done, but only **37** have a T-score in the CSV (35 in the author's sheet) — 37 dots are drawn |
| C p | p < 0.001 | [author] | all reproductions give p < 0.001 (7.1e-05 … 4.0e-04); note B says "< 0.01" and C "< 0.001" — could be unified to "< 0.001" for both |

If the author cannot reproduce −0.58, the legend line for (C) becomes "rs = −0.61, p < 0.01"
with "n = 37" and (B)/(C) phrased "…who underwent bone density testing and had a recorded T-score".

---

## Numbers to update in the main text / response letter

| Where | First submission | Revised | Source / status |
|---|---|---|---|
| Figure numbering | Fig 1 study design / Fig 2 KM / Fig 3 DXA | Fig 1 study design / **Fig 2 Grad-CAM (new)** / **Fig 3 KM** / **Fig 4 Age–RO (new)** / **Fig 5 DXA + premenopausal T-score** | README.md 番号の対応 |
| HRO / LRO n (whole cohort) | 425 / 360 (54.1% HRO) | **440 / 345** (56.1% HRO) | fig3.md [computed]; Table 1 "High risk of osteoporosis 425 (54.1)" → 440 (56.1) |
| Premenopausal HRO | 75/325 (23.1%) | **87/325 (26.8%)** | fig3.md [computed]; Abstract + Results |
| Postmenopausal HRO/LRO | 350 / 110 | **353 / 107** | fig3.md [computed] |
| Cut-off rule | "set according to the incidence of osteopenia in premenopausal women" (no value) | ⚠ group column is reproduced by **pre RO ≥ 0.102 / post RO ≥ 0.110** (rev0 was a single cut-off between 0.111 and 0.112) | fig3.md 推定 — author must confirm and justify (Rev1 #5, Rev2 Major 1) |
| KM premenopausal (Fig 3B) | log-rank p < 0.01; HR 2.37 (1.23–4.57) in Results; univariate Table 2 HR 2.32 (1.22–4.39) | **log-rank p = 0.04; HR 1.91 (95% CI 1.01–3.59)** | [computed] = [author]. Abstract "p<0.01" → "p = 0.04". Table 2 univariate row must be updated; multivariate HR 2.71 (1.23–5.63) must be **re-run** with the new groups (no value available yet) |
| KM postmenopausal (Fig 3C) | p = 0.65; HR 1.13 (0.64–2.02) | **p = 0.56; HR 0.84 (95% CI 0.46–1.51 [author] / 0.48–1.50 [computed])** | ⚠ CI disputed; Table 2 univariate row must match the figure; multivariate 1.03 (0.53–2.01) must be re-run |
| KM all women (Fig 3A) | p = 0.16 | **p = 0.32** (HR 1.22, 0.82–1.82 if needed) | fig3.md [computed]; Abstract "p=0.16" → "p = 0.32" |
| Age–RO (Fig 4) | — | all r = 0.61 (n = 785); pre r = 0.21 (n = 325); post r = 0.45 (n = 460); all p < 0.01, **Pearson** | fig4.md [computed] = [author] |
| DXA rate | pre 11.7% (38/325); post 76.4% (346/460 as written) | pre 11.7% (38/325); post **75.2% (346/460)** as drawn, or 76.4% (346/453) if denominator excludes unknowns | ⚠ fig5.md — choose one and align text, abstract and figure |
| T-score vs RO, all (Fig 5B) | r = −0.64, p < 0.01 (no n) | rs = −0.64, **n = 381** (author: 384), p < 0.01, **Spearman** | ⚠ n |
| T-score vs RO, premenopausal (Fig 5C) | — | rs = −0.58, n = 38, p < 0.001 [author] / rs = −0.61, n = 37, p < 0.01 [computed] | ⚠ r and n |
| Methods, correlation | "The Pearson correlation coefficient was used" | Pearson for age vs RO (Fig 4); **Spearman rank correlation** for T-score vs RO (Fig 5) | fig4.md / fig5.md |
| Methods, OPSCAN | DenseNet, 48,353 CXR [16, 17] | unchanged; citation now in the Figure 1 legend, not in the figure | fig1.md 決定 |
| Age HRO vs LRO (Results) | median 64 (56–70) vs 47 (43–53) | must be **recomputed** with the new groups (15 women moved LRO → HRO) | not available in repo |
| Other HRO/LRO comparisons in Results (stage 3, chemotherapy, endocrine therapy, tamoxifen, first recurrence site counts) | 425 / 360 denominators | must be **recomputed** with 440 / 345 | not available in repo |

Open questions to send to the author (one line each):

1. Cut-off rule for HRO (pre ≥ 0.102 / post ≥ 0.110?) and its justification.
2. Fig 3C 95% CI: 0.46–1.51 (yours) or 0.48–1.50 (recomputed)?
3. Fig 5B n: 384 or 381 (three women lack a T-score)?
4. Fig 5C: how was r = −0.58 with n = 38 obtained? Otherwise use rs = −0.61, n = 37.
5. Fig 5A postmenopausal rate: 75.2% (346/460) or 76.4% (346/453)?
6. Fig 2: what each of A–D is (HRO/LRO, RO score, T-score, menopausal status), and whether the
   activations are on bone.
7. Re-run multivariate Cox (Table 2) and the Results comparisons with the new 440/345 groups.
