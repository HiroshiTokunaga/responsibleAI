"""
Experiment 2: 2x2 tables for aid targeting, satellite vs province average.

Setup:
  needy   = bottom 20% of districts by official BPS HDI      (the truth)
  flagged = bottom 20% of districts by each method's score   (the decision)

With equal numbers flagged and needy, every miss frees a slot that goes to a
non-needy district, so FN = FP and FPR = (1 - TPR) * P / N. One fixed cutoff
therefore gives no information beyond TPR. We print this check below; varying
the cutoff (an ROC curve) is the next step.
"""

import sys

sys.path.insert(0, "src")

import pandas as pd

from hdi_audit.targeting import bottom_k, bottom_k_random_ties
from metrics.confusion import as_2x2, confusion, rates, summary_row
from utils.io import load_districts, save_table

SHARE = 0.20


def label_needy_and_flags(df, share=SHARE):
    """Add needy / flagged columns. Used again by experiment 3."""
    k = int(round(share * len(df)))
    df = df.copy()
    df["needy"] = bottom_k(df["hdi_true"], k)
    df["flag_sat"] = bottom_k(df["hdi_sat"], k)
    # Province scores tie within a province. Choice: order tied districts by
    # their satellite estimate. Checked against random tie-breaking below.
    df["flag_prov"] = bottom_k(df["hdi_province"], k, tiebreak=df["hdi_sat"])
    df["flag_prov_random_share"] = bottom_k_random_ties(df["hdi_province"], k)
    return df, k


def run():
    df, k = label_needy_and_flags(load_districts())
    P, N = int(df["needy"].sum()), int((~df["needy"]).sum())
    print(f"{len(df)} districts; bottom 20% = {k} needy, {N} not needy\n")

    rows = []
    for name, col in [("satellite", "flag_sat"), ("province average", "flag_prov")]:
        c = confusion(df["needy"], df[col])
        r = rates(c)
        print(f"{name}:\n{as_2x2(c)}")
        print(f"  TPR {r['TPR']:.2f}  FPR {r['FPR']:.2f}  "
              f"check (1-TPR)*P/N = {(1 - r['TPR']) * P / N:.2f}\n")
        rows.append(summary_row(df["needy"], df[col], method=name))

    # Robustness: expected TPR for the province method if ties are random.
    exp_tp = (df["flag_prov_random_share"] * df["needy"]).sum()
    print(f"province average, random tie-breaking: expected TPR {exp_tp / P:.2f}")

    table = pd.DataFrame(rows).round(3)
    save_table(table, "exp02_confusion.csv")
    return table


if __name__ == "__main__":
    run()
