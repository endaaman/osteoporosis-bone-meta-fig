# 論文用fig作成

- データの場所: data/osteoporosis_bone_meta.csv
- ライブラリは `uv add` で入れる
- 実行は `uv run` で実行すること


---


## Figure１　
Study Design 
Xp を使用した画期的なAIにより「閉経前乳癌患者」のRisk of osteoporosis が評価可能になったことを伝えたい

---

## Figure2 　
Censorのひげを必ず入れる
Enrolled women 785名
Premenopause women: Menopause「0」
Postmenopausal women: Menopause 「１」

Osteoporosis high or low risk : H列参照


Figure のオリジナル

> Figure 2. Univariate analyses for bone metastasis-free survival stratified by the menopausal status　(差し替え予定、遠田作成)
> Survival analysis representing the proportion of bone metastasis-free patient-based risk of osteoporosis scores in a) all enrolled women, b) premenopausal women, and c) postmenopausal women. LRO; low risk of osteoporosis, HRO: high risk of osteoporosis

---


# Figure 3

BMFS 
Bonemeta or death : 1 （N列）
BMFS 0-60 month (O列)

Figure3 
a)Perioperative Dxa presence(J列):  1の患者の閉経前と閉経後の施行率の差を見る
Perioperative DXAは手術前後2年以内であり、「０」の人の一部にdxa dateの記載あり。今回はJ列で1の患者の閉経前と閉経後の施行率を比較

b)RO とTscore の関連：Dxa presence(J列):  1の患者
     AI_Pの連続変数(G列)とTscore (L列)の相関係数とう


> Figure 3. Perioperative bone density test in enrolled women(差し替え予定、遠田作成)
> a) Conduction rate of bone density tests in premenopausal and postmenopausal women. b) Correlation between T-scores and risk of osteoporosis in the enrolled women.  
