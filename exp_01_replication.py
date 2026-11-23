"""
Experiment 1: Replicate the paper's Indonesia validation from public data.

The authors' notebook (code/analysis/indonesia_downscaling_analysis_ADM2.ipynb)
cannot run as published: it loads hdi_preds_at_adm2_BRA_IDN_MEX.p and
hdi_preds_from_all_models_at_adm2.p, which are not in their public repo.
So we recompute their headline numbers from the public CSV instead.

Paper (Sherman et al. 2026, Results section 3): in Indonesia the estimates
explain 61% of municipal HDI variation overall and 53% within provinces.
"""

import sys

sys.path.insert(0, "src")

import pandas as pd

from metrics.validation import within_country, within_province
from utils.io import load_districts, save_table

PAPER = {"within-country": 0.61, "within-province": 0.53}


def run():
    df = load_districts()
    rows = []
    for name, fn in [("within-country", within_country), ("within-province", within_province)]:
        s = fn(df)
        rows.append({"comparison": name, "paper_R2": PAPER[name],
                     "ours_R2": round(s["R2"], 3), "ours_rho2": round(s["rho2"], 3)})
    table = pd.DataFrame(rows)

    spread = pd.DataFrame([{
        "sd_official": round(df["hdi_true"].std(), 4),
        "sd_satellite": round(df["hdi_sat"].std(), 4),
        "ratio": round(df["hdi_sat"].std() / df["hdi_true"].std(), 2),
    }])

    print(f"Districts: {len(df)}")
    print(table.to_string(index=False))
    print("\nSpread of values (the estimates are 'squashed' toward the middle):")
    print(spread.to_string(index=False))
    save_table(table, "exp01_replication.csv")
    save_table(spread, "exp01_spread.csv")
    return table


if __name__ == "__main__":
    run()
