"""
Experiment 3: Where are the misses?

Hypothesis (from the results-meeting feedback): poor districts inside
better-off provinces are the ones that get missed.

We split the 29 provinces into thirds by province HDI, then ask, for the truly
needy districts in each third, how many each method flags. We also list the
needy districts the satellite method misses.
"""

import sys

sys.path.insert(0, "src")

import pandas as pd

from exp_02_confusion import label_needy_and_flags
from hdi_audit.targeting import province_tiers
from metrics.confusion import summary_row
from utils.io import load_districts, save_table


def run():
    df, k = label_needy_and_flags(load_districts())
    df["prov_tier"] = province_tiers(df)

    rows = []
    for tier, g in df.groupby("prov_tier", observed=True, sort=False):
        for name, col in [("satellite", "flag_sat"), ("province average", "flag_prov")]:
            rows.append(summary_row(g["needy"], g[col], province_tier=str(tier), method=name))
    table = pd.DataFrame(rows).round(3)
    table = table.sort_values(["province_tier", "method"],
                              key=lambda s: s.map({"poor": 0, "middle": 1, "better-off": 2}).fillna(s))

    # Compact view: needy districts caught, per tier and method
    caught = table.pivot(index="province_tier", columns="method", values="TP")
    caught["needy"] = table.groupby("province_tier")["TP"].first() + table.groupby("province_tier")["FN"].first()
    caught = caught.loc[["poor", "middle", "better-off"], ["needy", "satellite", "province average"]]
    print("Truly needy districts, and how many each method catches:")
    print(caught.to_string(), "\n")

    # Average error among needy districts: positive = estimate too high
    df["error"] = df["hdi_sat"] - df["hdi_true"]
    err = df[df["needy"]].groupby("prov_tier", observed=True)["error"].mean().round(3)
    print("Mean satellite error among needy districts (positive = looks richer than it is):")
    print(err.to_string(), "\n")

    misses = (df[df["needy"] & ~df["flag_sat"]]
              .sort_values("hdi_true")
              [["name", "bps_province", "prov_tier", "hdi_true", "hdi_sat", "hdi_province"]]
              .round(3))
    print(f"Needy districts the satellite method misses: {len(misses)} (poorest 15 shown)")
    print(misses.head(15).to_string(index=False))

    save_table(table, "exp03_by_province_tier.csv")
    save_table(caught.reset_index(), "exp03_caught_summary.csv")
    save_table(misses, "exp03_satellite_misses.csv")
    return table


if __name__ == "__main__":
    run()
