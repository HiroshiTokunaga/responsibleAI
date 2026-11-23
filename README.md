## Research question

When satellite-based HDI estimates are used to target aid to Indonesia’s poorest districts, how often are poor districts inside better-off provinces missed compared with poor districts inside poor provinces? Can group-specific thresholds reduce the gap?

## How this differs from the original paper

Sherman et al. (2026, *Nature Communications*) estimate HDI for districts worldwide from satellite imagery. Their Indonesia validation asks
how closely the estimates match official values, and they have an R² of 0.61 within the
country and 0.53 within provinces.

What we want to ask is if a government acts on these estimates, which
truly poor districts are left out, and are the misses concentrated in a
particular kind of place?

## Approach

1. **Replicate** the paper's Indonesia numbers from public data.
2. **Simulate targeting.** "Needy" = bottom 20% of districts by official HDI.
   "Flagged" = bottom 20% by a our method's score. Compare two scores:
   - the satellite estimate for each district, and
   - the province average
3. **Locate the misses** by splitting provinces into thirds by HDI.
4. *(Next)* **ROC curves per group**: keep "needy" fixed and vary the cutoff
   on the score (equivalently, the size of the aid budget). Then test
   separate cutoffs per group (Hardt, Price & Srebro 2016).

## Data

Both files come from the authors' public repository
([Global-Policy-Lab/hdi_downscaling_mosaiks](https://github.com/Global-Policy-Lab/hdi_downscaling_mosaiks),
MIT license, commit `cea8990`) and are copied into `data/raw/`.

| File | What it is | Source path in their repo |
|---|---|---|
| `hdi_preds_at_adm2.csv` | Satellite HDI estimates for every district worldwide (2019) | `data/preds/hdi_preds_at_adm2.csv` |
| `2019_hdi_by_gender_indonesia.xlsx` | Official 2019 district HDI from BPS (Statistics Indonesia), by sex | `data/raw/indonesia_hdi/2019_hdi_by_gender_indonesia.xlsx` |

`data/load_indonesia.py` joins them into one table of 513 districts. Cleaning
steps, all documented in that file:
- District HDI = average of male and female HDI (as in the authors' notebook).
- Papua districts listed twice in the BPS file; the blank duplicates are dropped.
- 8 district names spelled differently between the files are fixed by hand.
- 4 prediction polygons that are lakes or forests, and 1 district with no
  prediction, are dropped.

The province average comes from the prediction file (`adm1_HDI_Smits`). It is
the survey-based province HDI from the Global Data Lab that the model was
trained on, which groups Indonesia into 29 provinces.

## How to run

```bash
conda env create -f env.yaml
conda activate hdi-audit
python exp_runner.py
```

Tables are saved to `results/`.

## Repository layout

```
data/load_indonesia.py        join and clean the two source files
src/utils/io.py               paths, loading, saving
src/hdi_audit/targeting.py    bottom-k targeting rule, province tiers
src/metrics/confusion.py      2x2 tables, TPR / FPR / PPV
src/metrics/validation.py     within-country and within-province fit
exp_01_replication.py         Experiment 1
exp_02_confusion.py           Experiment 2
exp_03_province_groups.py     Experiment 3
exp_runner.py                 runs all experiments
```

## Preliminary results

**1. Replication.** The public data reproduces the paper's Indonesia numbers.

**2. Targeting 2×2 tables** :

| | Satellite | Province average |
|---|---|---|
| Needy and flagged (TP) | 62 | 57 |
| Not needy but flagged (FP) | 41 | 46 |
| Needy but missed (FN) | 41 | 46 |
| TPR | 0.60 | 0.55 |
| FPR | 0.10 | 0.11 |

**3. misses** :

| Province third | Needy | Satellite | Province average |
|---|---|---|---|
| Poor (10 provinces) | 72 | 54 | 57 |
| Middle (10) | 20 | 5 | 0 |
| Better-off (9) | 11 | 3 | 0 |

The province average catches none of the 31 needy districts in middle or
better-off provinces. The satellite catches 8. Many satellite misses are
island districts (e.g. Pulau Morotai, Pulau Taliabu, Kepulauan Mentawai,
Nias Selatan, Simeulue).


## Reference

Sherman, L., Proctor, J., Druckenmiller, H., Tapia, H., & Hsiang, S. (2026).
Global high-resolution estimates of the UN Human Development Index using
satellite imagery and machine learning. *Nature Communications*, 17, 1315.
