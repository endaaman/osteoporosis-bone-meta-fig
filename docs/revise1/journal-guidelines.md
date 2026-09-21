# MedComm（Wiley）の図の投稿規定 — 公式ページの調査

調査日: 2026-09-21。対応表（`README.md` の「投稿規定」節）に書かれた規則が公式規定と一致するかを確認した。

## 結論（先に）

- **MedComm の公式ページには、図のフォント・フォントサイズ・図の高さ上限・線幅・パネルラベル様式・カラーモードの規定は一切無い。**
  ページは Wiley 共通の PDF「Guidelines for the Preparation of Figures」へリンクするだけで、その PDF にも
  フォント名・フォントサイズ・線幅・カラーモード・高さ上限の記載は無い（「Larger fonts make for easier reading」程度）。
- 公式に定量で書かれているのは **ファイル形式・解像度・幅** の 3 点のみ。
  - 形式: 線画（グラフ等）は **EPS / PDF** 推奨、画像は **TIFF / PNG / EPS** 推奨。受理後は GIF/JPG/TIFF/PNG/WMF/DOC/PPT/PSD/AI/PS も可。
  - 解像度: **線画（線画と画像の混在を含む）600 dpi**（受理後は 600–1000 dpi）、**画像 300 dpi**。
  - 幅: **80 mm（1/4 ページ）または 180 mm（半〜全ページ）**、横 1800 px 以上。
- 対応表の「幅 170 mm / 高さ ≤210 mm / 8–10 pt（最低 6 pt）/ 太字大文字パネルラベル / 線 ≥0.25 pt / ≥300 dpi / 白抜き柱」は
  **MedComm・Wiley の公式規定ではなく、著者（または対応表作成者）側の内規**とみるべき。公式と食い違う点は「差分」節を参照。
- `rev1/common.py` の現行設定（Arial・8–10 pt・170 mm・600 dpi・png/pdf/tiff）は公式規定をすべて満たす。

## 1. MedComm Author Guidelines（公式ページ）

URL: <https://onlinelibrary.wiley.com/page/journal/26882663/homepage/author-guidelines>
（「Author Guidelines updated 6 Jun 2022」。Cloudflare で curl/WebFetch が弾かれるためブラウザで読んだ）

図に関する記述の全文（4. Preparing the Submission → Figures）:

> Although authors are encouraged to send the highest-quality figures possible, for peer-review purposes, a wide variety of formats, sizes, and resolutions are accepted.
>
> Click here for the basic figure requirements for figures submitted with manuscripts for initial peer review, as well as the more detailed post-acceptance figure requirements.
>
> Color figures. Figures submitted in color may be reproduced in color online free of charge. If an author would prefer to have figures printed in colour in hard copies of the journal, a fee will be charged by the Publisher.

「Click here」のリンク先（ページの DOM から取得）: <http://media.wiley.com/assets/7323/92/electronic_artwork_guidelines.pdf>
（= Wiley 共通の「Guidelines for the Preparation of Figures」、Updated 1 September 2016 版。§2 参照）

図に関わるその他の記述:

- Free Format submission: 「Figures should be uploaded in the highest resolution possible. If the figures are not of sufficiently high quality your manuscript may be delayed.」
- Parts of the Manuscript: 「The manuscript should be submitted in separate files: main text file; figures.」「Figures and supporting information should be supplied as separate files.」
- Figure Legends: 「Legends should be concise but comprehensive – the figure and its legend must be understandable without reference to the text. Include definitions of any symbols used and define/explain all abbreviations and units of measurement.」
- Tables の脚注記号: 「Footnote symbols: †, ‡, §, ¶, should be used (in that order) and *, **, *** should be reserved for P-values.」（表の規定だが、図中の有意差記号もこれに揃えると無難）
- Graphical Abstract: 「The image should fit within the dimensions of 50mm x 60mm, and be fully legible at this size.」
- 図の数: Original article は「up to 8 figures and tables in total」。

**MedComm ページに無いもの（明示）**: フォントファミリー、フォントサイズ、図の高さ上限、単一/二段組の幅（mm）、線幅、パネルラベルの様式、RGB/CMYK、グラフの柱の塗り（白抜き等）。

## 2. Wiley 共通「Guidelines for the Preparation of Figures」（MedComm ページのリンク先 PDF）

- MedComm がリンクする版: <http://media.wiley.com/assets/7323/92/electronic_artwork_guidelines.pdf>（Updated 1 September 2016）
- 同内容の現行版: <https://authors.wiley.com/asset/photos/electronic_artwork_guidelines.pdf>（Updated 1 September 2016 + Gels and Blots 節）
- 2025 年改訂版（他誌 Clinical Case Reports が掲載）: <https://onlinelibrary.wiley.com/pb-assets/assets/20500904/AG/Electronic-Artwork-Guidelines-CCR3-1741401216880.pdf>（Updated March 2025）。数値規定は 2016 版と同一。

数値規定（Preferred / Acceptable の表から引用）:

**ファイル形式**

> Line art: Line art includes graphs, flowcharts, diagrams, scatter plots, and other text-based figures that are not tables. Important! If a figure includes both line art and images, follow the line art guidelines. — Preferred: EPS, PDF — Acceptable: Any standard file type. When in doubt, submit a PDF.
>
> Images: Images include photographs, drawings, imaging system outputs (such as MRIs or ultrasound), and other graphical representations. — Preferred: TIFF, PNG, EPS

受理後（Post-Acceptance）の Acceptable: 「Any standard including: GIF, JPG, TIF/TIFF, PNG, WMF, DOC, PPT, PSD, AI, PS」

> Important tip! Creating your figures in one of the preferred file types is better than converting an existing figure later on. If you cannot create one of your figures as an EPS, TIFF, or PNG, send us what you are able to create and we'll do our best to present it effectively.

**解像度**

> Line art: Resolution for line art needs to be higher than for images because each individual line must be more precisely rendered. Tip! Larger fonts make for easier reading. — Preferred: 600 dpi（査読時）/ 600-1000 dpi（受理後） — Acceptable: As long as it is legible to reviewers.（査読時）/ Must be legible when viewed as an 80 mm or 1800 pixel width, unmagnified.（受理後）
>
> Images: ... — Preferred: 300 dpi

**サイズ**

> Small: Used for small line art and images that will occupy one-quarter of the page. — Preferred: 80 mm canvas size or Pixel dimensions (width): 1800px minimum
>
> Large: Used for larger line art and images that occupy a half-page or an entire page. Carefully consider the minimum space necessary for each figure. — Preferred: 180 mm canvas size or Pixel dimensions (width): 1800px minimum — Acceptable（受理後）: Smaller or larger images will be modified during composition, which may result in decreased quality.

チェックリスト: 「Were figures created between 80 and 180 mm width? 300 to 600 DPI?」

**ファイルサイズ・命名・凡例**

> Individual files: ... Preferred: Less than 10 MB each.
>
> File Naming Convention: to facilitate ease of review, name figure files only with the word "figure" and the appropriate number. — Example: Figure_1.tiff — Preferred: 1 figure per file.
>
> Figure legends or captions should use Arabic numerals, follow the order in which they appear in the manuscript, and explain any abbreviations or symbols that appear in the figure. — Preferred: A separate figure legend section in the manuscript, after references.

**PDF に無いもの（明示）**: フォントファミリー、フォントサイズの数値、図の高さ上限、線幅、パネルラベルの様式、RGB/CMYK。

## 3. Wiley の他の一般資料（参考。MedComm からはリンクされていない）

### 3a. Wiley Author Services「Guidelines for Preparing Figures」（現行 Web 版）

URL: <https://authors.wiley.com/author-resources/Journal-Authors/Prepare/manuscript-preparation-guidelines.html/figure-preparation.html>

§2 の PDF と同じ内容（線画 600 dpi / 画像 300 dpi、80–180 mm、線画は PDF、画像は PNG/TIFF、各ファイル 10 MB 未満）。
フォント・線幅・高さ・カラーモードの記載なし。

### 3b. 旧 Wiley「Artwork Guidelines for Authors」（2000–2006 年の legacy ページ。現在は 404、Wayback Machine で確認）

URL（原本、現在 404）: <https://www.wiley.com/legacy/products/subject/journals/artguide.html>
アーカイブ: <https://web.archive.org/web/2019/https://www.wiley.com/legacy/products/subject/journals/artguide.html>

Web 検索で「Wiley はフォントは Arial/Helvetica、8 pt 以上、線 0.5 pt 以上」と出てくる出典はこのページ。印刷入稿（フロッピー・ハードコピー）時代の規定で、**現行の MedComm / Wiley 規定ではない**が、数値の由来として引用しておく:

> Lettering within figures should be consistent in font, size, and no smaller than 8-pt type. Line thickness must be evenly balanced and no less than 0.5 pt (0.2 mm).
>
> Label individual elements clearly with lower case letters, e.g., (a), (b), (c).
>
> Figures should be saved in graphic format only. Use EPS or TIFF formats only.
>
> EPS files must have fonts embedded or converted into outlines. If this is not possible, please use standard system fonts (e.g. Arial, Helvetica, Times).
>
> With regard to color production, supplying CMYK is preferred over RGB.
>
> The minimum resolution for different artwork categories is as follows: 300-350 dpi for all halftones (both color and black-and-white) / 800-1200 dpi for simple black and white line artwork / 500-600 dpi for line/halftone combinations / 800 dpi for color artwork

### 3c. Wiley 他誌の例（Small の Graphics FAQ。MedComm には適用されない参考値）

URL: <https://onlinelibrary.wiley.com/page/journal/16136829/homepage/graphics-faq/index.html>

> Images are usually printed as either one column wide (8.5 cm, or about 3.35 in) or two columns wide (17.8 cm, or about 7.01 in)
>
> Axis labels and symbols should be 10 to 12 point at the intended reproduction size
>
> Labels should be consistent throughout the manuscript, using lower-case letters (a,b,c...) in a 12 point sans-serif typeface (such as Arial or Helvetica). The labels should be consistently positioned, preferably in the top left corner of the panels.

## 4. 対応表の規則と公式規定の差分

| 項目 | 対応表（著者指示） | MedComm / Wiley 公式 | 判定 |
|---|---|---|---|
| 幅 | 170 mm（または 80 mm） | 80 mm または 180 mm（「between 80 and 180 mm」） | 170 mm は範囲内で問題なし。公式の「Large」は 180 mm |
| 高さ | ≤210 mm | 規定なし | 著者内規。公式に矛盾しない |
| フォントファミリー | （指定なし。common.py は Arial） | **規定なし**。旧 legacy 資料で「standard system fonts (e.g. Arial, Helvetica, Times)」 | Arial で問題なし |
| フォントサイズ | 8–10 pt（最低 6 pt） | 規定なし（「Larger fonts make for easier reading」）。旧 legacy 資料は「no smaller than 8-pt」 | 8–10 pt で問題なし。**6 pt は旧 Wiley 資料の 8 pt 下限を割る**ので、実際に 6 pt を使う箇所は作らないのが安全 |
| パネルラベル | 大文字・太字 | **規定なし**。旧 legacy 資料と Small は小文字 (a),(b) | 公式に大文字/小文字の指定は無い。著者指示（大文字太字）に従ってよい。MedComm 掲載論文は大文字 A/B/C が多数派なので実態にも合う |
| 線幅 | ≥0.25 pt | **規定なし**。旧 legacy 資料は「no less than 0.5 pt (0.2 mm)」 | **差分あり**: 旧 Wiley 資料の下限 0.5 pt に対し対応表は 0.25 pt。現行規定に線幅の記載は無いので違反ではないが、細線（軸・エラーバー・KM の打ち切りマーク等）は 0.5 pt 以上にしておくと安全 |
| 解像度 | ≥300 dpi | **線画（グラフ・散布図・KM 曲線、および線画+画像の混在図）は 600 dpi** 推奨（受理後 600–1000 dpi）。写真のみの図は 300 dpi | **差分あり**: 本プロジェクトの図は全てグラフ／フローチャート／Grad-CAM+ラベルの混在なので、公式には **600 dpi** が Preferred。300 dpi は「Acceptable（判読できれば可）」止まり。`common.py` の 600 dpi を維持すること |
| ファイル形式 | （png/pdf/tiff を出力） | 線画は EPS/PDF 推奨、画像は TIFF/PNG/EPS 推奨。「When in doubt, submit a PDF」 | 問題なし。**TIFF/EPS 限定ではない**（TIFF/EPS 限定は 2006 年以前の旧規定）。線画主体の図は PDF、Grad-CAM（Fig2）は TIFF/PNG が第一候補 |
| カラーモード | （指定なし） | **規定なし**。オンライン OA 誌でカラー無料。旧 legacy 資料は印刷向けに CMYK 推奨 | RGB のままで問題なし（Grad-CAM ヒートマップの色再現上も RGB が望ましい） |
| 白抜きの柱 | 個々の値を示すときは白抜き | 規定なし | 著者内規（査読対応の内容） |
| ファイル名 | — | 「Figure_1.tiff」形式、1 図 1 ファイル、各 10 MB 未満 | 出力時に `Figure_N.<ext>` に揃える。600 dpi の TIFF は 10 MB を超えやすいので LZW 圧縮するか PDF を提出 |

## 5. 実務上の推奨（上記を踏まえて）

1. 提出形式: グラフ系（Fig1, 3, 4, 5）は **PDF**（ベクタ、フォント埋め込み）を主、TIFF（600 dpi, LZW）を副。Grad-CAM（Fig2）は **TIFF/PNG 600 dpi**（線画+画像の混在扱い）。
2. 解像度は 600 dpi を維持（300 dpi に落とさない）。
3. フォントは Arial、本文 8–10 pt、6 pt は使わない。
4. 線幅は最低 0.5 pt を目安にする（対応表の 0.25 pt は旧 Wiley 下限を割る）。
5. パネルラベルは著者指示どおり大文字太字（公式指定なし）。
6. 各ファイル 10 MB 未満、`Figure_1.pdf` のような命名。
