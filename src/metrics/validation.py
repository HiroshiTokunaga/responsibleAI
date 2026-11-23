"""Fit between satellite estimates and official values, as in Sherman et al."""

import numpy as np
from sklearn.metrics import r2_score


def fit_stats(true, pred):
    """Squared Pearson correlation and R^2 of pred against true."""
    rho2 = np.corrcoef(true, pred)[0, 1] ** 2
    return {"rho2": rho2, "R2": r2_score(true, pred)}


def within_country(df, true="hdi_true", pred="hdi_sat"):
    """Fit after subtracting the national mean from both columns."""
    return fit_stats(df[true] - df[true].mean(), df[pred] - df[pred].mean())


def within_province(df, true="hdi_true", pred="hdi_sat", group="gdl_province"):
    """Fit after subtracting each province's mean from both columns.

    This asks only: within each province, does the model tell the better-off
    districts from the worse-off ones? It is the paper's main test.
    """
    g = df.groupby(group)
    t = df[true] - g[true].transform("mean")
    p = df[pred] - g[pred].transform("mean")
    return fit_stats(t, p)
