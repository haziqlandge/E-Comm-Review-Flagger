"""Clean the Kaggle Flipkart reviews file and draw the stratified 300-record annotation sample.

Usage:  python scripts/sample_dataset.py path/to/Dataset-SA.csv
Source: https://www.kaggle.com/datasets/niraliivaghani/flipkart-product-customer-reviews-dataset
"""
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
QUOTA = {5: 85, 4: 60, 3: 60, 2: 45, 1: 50}  # records per star rating
MAX_PER_PRODUCT = 3


def main(src):
    df = pd.read_csv(src)
    df = df.dropna(subset=["Summary"]).copy()
    df["Rate"] = pd.to_numeric(df.Rate, errors="coerce")
    df = df.dropna(subset=["Rate"])
    df["Rate"] = df.Rate.astype(int)
    df["wc"] = df.Summary.str.split().str.len()
    df = df[(df.wc >= 6) & (df.wc <= 60)]
    df = df[df.Summary.str.match(r"^[\x00-\x7f]+$")]
    df = df.drop_duplicates("Summary")
    df["product_name"] = df.product_name.str.replace(r"\?+", "", regex=True).str.strip()
    print(f"eligible records: {len(df)}")

    parts = []
    for rate, q in QUOTA.items():
        sub = df[df.Rate == rate].sample(frac=1, random_state=42)
        parts.append(sub.groupby("product_name").head(MAX_PER_PRODUCT).head(q))
    sample = pd.concat(parts).sample(frac=1, random_state=7).reset_index(drop=True)
    sample.insert(0, "ID", [f"FK{i + 1:03d}" for i in range(len(sample))])
    out = ROOT / "data" / "flipkart_sample_300_raw.csv"
    sample.to_csv(out, index=False)
    print(f"wrote {len(sample)} records from {sample.product_name.nunique()} products to {out}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "Dataset-SA.csv")
