"""HRO/LRO のカットオフの導出（Youden index）。

Reviewer 2 Major 1 への対応: DXA ground truth を持つ症例で、骨減少症以上（T-score <= -1）を
陽性とした ROC を描き、Youden index (感度 + 特異度 - 1) が最大になる RO (AI_P) を閾値とする。
論文で採用したのは閉経前・周術期 DXA 施行例（cohort='pre_peri'）での値 = RO 0.10。
fig3 は xlsx の RO group 列をそのまま使うので、このスクリプトは閾値の根拠を示す用途。

    uv run python rev1/cutoff.py      # 閾値・感度・特異度・AUC・bootstrap 区間を表示
"""
import numpy as np
import pandas as pd
from sklearn.metrics import roc_curve, roc_auc_score

CSV = 'data/osteoporosis_bone_meta.csv'
T_POSITIVE = -1.0   # 骨減少症以上 (WHO: T <= -1)
SEED = 0


COHORTS = {
    'pre_peri': '閉経前・周術期 DXA 施行例 (Perioperative Dxa presence == 1)',
    'all': 'T-score のある全症例（閉経前後、周術期以外の DXA も含む）',
}


def load_dxa_cohort(cohort='pre_peri'):
    """Exclude==0 かつ T-score が数値で入っている症例。"""
    df = pd.read_csv(CSV)
    df.columns = df.columns.str.strip()
    df = df[df['Exclude'] == 0].copy()
    df['Tscore'] = pd.to_numeric(df['Tscore'], errors='coerce')   # "3.4 dish?" 等は NaN
    df['AI_P'] = pd.to_numeric(df['AI_P'], errors='coerce')
    d = df.dropna(subset=['Tscore', 'AI_P'])
    if cohort == 'pre_peri':
        d = d[(d['menopause'] == 0) & (d['Perioperative Dxa presence'] == 1)]
    elif cohort != 'all':
        raise ValueError(cohort)
    return d[['研究ID', 'menopause', 'AI_P', 'Tscore']].reset_index(drop=True)


def youden(score, positive):
    fpr, tpr, thr = roc_curve(positive, score)
    j = tpr - fpr
    i = int(j.argmax())
    return dict(cutoff=float(thr[i]), sens=float(tpr[i]), spec=float(1 - fpr[i]), J=float(j[i]),
                auc=float(roc_auc_score(positive, score)), fpr=fpr, tpr=tpr, thr=thr)


def youden_cutoff(t_positive=T_POSITIVE, n_boot=0, verbose=False, cohort='pre_peri'):
    d = load_dxa_cohort(cohort)
    y = (d['Tscore'] <= t_positive).astype(int)
    res = youden(d['AI_P'], y)
    res.update(n=len(d), n_pos=int(y.sum()), n_pre=int((d['menopause'] == 0).sum()),
               n_post=int((d['menopause'] == 1).sum()), t_positive=t_positive)
    if n_boot:
        rng = np.random.default_rng(SEED)
        cs = []
        for _ in range(n_boot):
            idx = rng.integers(0, len(d), len(d))
            yy = y.values[idx]
            if yy.min() == yy.max():
                continue
            cs.append(youden(d['AI_P'].values[idx], yy)['cutoff'])
        res['boot_ci'] = tuple(np.percentile(cs, [2.5, 97.5]))
    res['cohort'] = cohort
    if verbose:
        print(f"[{cohort}: {COHORTS[cohort]}]")
        print(f"DXA cohort n={res['n']} (pre {res['n_pre']}, post {res['n_post']}), "
              f"positive (T <= {t_positive}) = {res['n_pos']}")
        print(f"AUC = {res['auc']:.3f}")
        print(f"Youden cutoff: RO >= {res['cutoff']:.3f}  sens {res['sens']:.2f}  spec {res['spec']:.2f}  J {res['J']:.2f}")
        if n_boot:
            lo, hi = res['boot_ci']
            print(f"bootstrap ({n_boot}) 95% CI of cutoff: {lo:.3f}-{hi:.3f}")
    return res


if __name__ == '__main__':
    youden_cutoff(n_boot=1000, verbose=True)
    print('--- reference: all DXA cohort')
    youden_cutoff(n_boot=1000, verbose=True, cohort='all')
