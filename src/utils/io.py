"""Paths and data loading shared by all experiments."""

import os

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_CSV = os.path.join(REPO_ROOT, "data", "indonesia_districts_2019.csv")
RESULTS_DIR = os.path.join(REPO_ROOT, "results")


def load_districts():
    """Load the joined district table, building it first if needed."""
    if not os.path.exists(DATA_CSV):
        import sys
        sys.path.insert(0, os.path.join(REPO_ROOT, "data"))
        from load_indonesia import build
        build().to_csv(DATA_CSV, index=False)
    return pd.read_csv(DATA_CSV)


def save_table(df, filename):
    """Save a results table as CSV in results/ and return its path."""
    os.makedirs(RESULTS_DIR, exist_ok=True)
    path = os.path.join(RESULTS_DIR, filename)
    df.to_csv(path, index=False)
    return path
