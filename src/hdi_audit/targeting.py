"""
Simulated aid targeting.

A "targeting rule" takes a score for each district and flags the k districts
with the lowest scores (lowest = poorest). We compare two scores:
  - hdi_sat:      the satellite estimate for the district itself
  - hdi_province: the HDI of the district's whole province (the "old method")
"""

import numpy as np
import pandas as pd


def bottom_k(score, k, tiebreak=None):
    """Return a boolean array: True for the k districts with the lowest score.

    tiebreak: optional second score used to order districts with equal scores.
    This matters for hdi_province, where every district in a province shares
    one value, so the cutoff can land in the middle of a province.
    """
    score = np.asarray(score)
    if tiebreak is None:
        order = np.argsort(score, kind="stable")
    else:
        # np.lexsort sorts by the LAST key first, so score is primary.
        order = np.lexsort((np.asarray(tiebreak), score))
    flags = np.zeros(len(score), dtype=bool)
    flags[order[:k]] = True
    return flags


def bottom_k_random_ties(score, k, n_draws=1000, seed=0):
    """Like bottom_k, but ties are broken at random.

    Returns the share of draws in which each district is flagged (0 to 1).
    Used as a check that our tie-breaking choice does not drive results.
    """
    rng = np.random.default_rng(seed)
    score = np.asarray(score)
    total = np.zeros(len(score))
    for _ in range(n_draws):
        total += bottom_k(score, k, tiebreak=rng.random(len(score)))
    return total / n_draws


def province_tiers(df, n_tiers=3):
    """Split provinces into thirds by province HDI and label each district.

    We rank the 29 provinces (not the districts) so that each tier holds
    roughly the same number of provinces: 10 poor, 10 middle, 9 better-off.
    """
    prov = df.groupby("gdl_province")["hdi_province"].first().sort_values()
    labels = ["poor", "middle", "better-off"][:n_tiers]
    tier = pd.Series(
        pd.qcut(np.arange(len(prov)), n_tiers, labels=labels),
        index=prov.index,
    )
    return df["gdl_province"].map(tier)
