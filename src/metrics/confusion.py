"""Confusion matrices and rates, as in Lab 2."""

import numpy as np
import pandas as pd


def confusion(y_true, y_flag):
    """Counts for the 2x2 table. y_true = truly needy, y_flag = flagged for aid."""
    y_true = np.asarray(y_true, dtype=bool)
    y_flag = np.asarray(y_flag, dtype=bool)
    return {
        "TP": int((y_flag & y_true).sum()),    # needy and flagged
        "FP": int((y_flag & ~y_true).sum()),   # not needy but flagged (wasted aid)
        "FN": int((~y_flag & y_true).sum()),   # needy but missed
        "TN": int((~y_flag & ~y_true).sum()),  # not needy, not flagged
    }


def rates(c):
    """TPR, FPR and PPV from a confusion dict. NaN if a denominator is zero."""
    def safe(a, b):
        return a / b if b > 0 else np.nan
    return {
        "TPR": safe(c["TP"], c["TP"] + c["FN"]),  # share of needy that are caught
        "FPR": safe(c["FP"], c["FP"] + c["TN"]),  # share of not-needy that are flagged
        "PPV": safe(c["TP"], c["TP"] + c["FP"]),  # share of flagged that are needy
    }


def summary_row(y_true, y_flag, **labels):
    """One row with labels, counts and rates, for building results tables."""
    c = confusion(y_true, y_flag)
    return {**labels, "n": len(np.asarray(y_true)), **c, **rates(c)}


def as_2x2(c):
    """Format a confusion dict as a 2x2 DataFrame for printing."""
    return pd.DataFrame(
        [[c["TP"], c["FP"]], [c["FN"], c["TN"]]],
        index=["flagged", "not flagged"],
        columns=["needy", "not needy"],
    )
