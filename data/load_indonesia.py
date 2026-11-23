"""
Build one clean table of Indonesian districts (2019) by joining two files.

Inputs (both from the authors' public repository, MIT license):
  data/raw/hdi_preds_at_adm2.csv
      Satellite-based HDI estimates for ~61,500 districts worldwide
      (Sherman et al. 2026). Source:
      https://github.com/Global-Policy-Lab/hdi_downscaling_mosaiks/raw/master/data/preds/hdi_preds_at_adm2.csv
  data/raw/2019_hdi_by_gender_indonesia.xlsx
      Official 2019 district HDI from BPS (Statistics Indonesia), split by
      sex. The authors use this same file for their Indonesia validation.
      Source:
      https://github.com/Global-Policy-Lab/hdi_downscaling_mosaiks/raw/master/data/raw/indonesia_hdi/2019_hdi_by_gender_indonesia.xlsx

Output: data/indonesia_districts_2019.csv, one row per district (513 rows).

Run from the repo root:  python data/load_indonesia.py
"""

import os

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
PRED_PATH = os.path.join(HERE, "raw", "hdi_preds_at_adm2.csv")
TRUTH_PATH = os.path.join(HERE, "raw", "2019_hdi_by_gender_indonesia.xlsx")
OUT_PATH = os.path.join(HERE, "indonesia_districts_2019.csv")

# District names spelled differently in the two files.
# Keys: spelling in the BPS spreadsheet. Values: spelling in the prediction file.
# Found by listing names that failed to match and checking each one by hand.
NAME_FIXES = {
    "Toba Samosir / Toba": "Toba Samosir",
    "Karangasem": "Karang Asem",
    "Kotabaru": "Kota Baru",  # a regency, despite the "Kota" in its name
    "Mahakam Ulu": "Mahakam Hulu",
    "Pangkajene dan Kepulauan": "Pangkajene Dan Kepulauan",
    "Kota Makasar": "Kota Makassar",
    "Mamuju Utara / Pasangkayu": "Mamuju Utara",
    "Maluku Tenggara Barat / Kepulauan Tanimbar": "Maluku Tenggara Barat",
}


def load_truth(path=TRUTH_PATH):
    """Official 2019 district HDI from BPS, on a 0-1 scale.

    The file gives HDI separately for men and women. Following the authors'
    validation notebook, we use the average of the two as district HDI.
    This is close to, but not identical to, BPS's official total HDI.
    """
    # Row 0 of the sheet is a year label; rows after 579 are notes.
    df = pd.read_excel(path, header=1).iloc[1:579]
    df = df.rename(columns={"Unnamed: 0": "name"})
    for col in ["Male", "Female"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")  # "-" becomes NaN

    # Province rows are in capital letters; each district sits under its province.
    is_province = df["name"].str.isupper()
    df["bps_province"] = df["name"].where(is_province).ffill()
    df = df[~is_province]

    # Papua districts appear twice: once under the old provinces (with values)
    # and once under the provinces created in 2022 (blank). Keep the filled copy.
    df = df.dropna(subset=["Male", "Female"])

    df["hdi_true"] = (df["Male"] + df["Female"]) / 200  # BPS uses a 0-100 scale
    df["name"] = df["name"].replace(NAME_FIXES)
    return df[["name", "bps_province", "hdi_true"]]


def load_preds(path=PRED_PATH):
    """Satellite-based HDI estimates for Indonesian districts."""
    df = pd.read_csv(path)
    df = df[df["shapeGroup"] == "IDN"]
    return df.rename(columns={
        "shapeName": "name",
        "GDL_ADM1": "gdl_province",          # province ID the model was trained on
        "adm1_HDI_Smits": "hdi_province",    # that province's survey-based HDI
        "predicted_adm2_HDI": "hdi_sat",     # the satellite estimate
        "est_total_pop": "population",
    })[["name", "shapeID", "gdl_province", "hdi_province", "hdi_sat", "population"]]


def build():
    truth = load_truth()
    preds = load_preds()
    # Inner join on name. Dropped on purpose: 4 prediction polygons that are
    # lakes or forests rather than districts (Danau Toba, Hutan, Waduk Cirata,
    # Wadung Kedungombo), and Kepulauan Seribu (no prediction).
    data = preds.merge(truth, on="name", how="inner")
    assert data["name"].is_unique
    return data


if __name__ == "__main__":
    data = build()
    data.to_csv(OUT_PATH, index=False)
    print(f"Saved {len(data)} districts to {OUT_PATH}")
