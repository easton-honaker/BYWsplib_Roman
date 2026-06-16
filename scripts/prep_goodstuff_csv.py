"""
Download goodstuffcopy219 and Reconcile_0426 from Google Sheets via the gviz
endpoint (which returns the correct column layout for each tab), filter
Reconcile to Code != 'skip', and left-join onto goodstuffcopy219 on 'shortname'.
Saves the merged result to data/BYWsplib_merged.csv.
"""

import ssl
import urllib.request
import io
import pandas as pd
from pathlib import Path

SHEET_ID = "1q5a8h63n-EJa83nGhFYfl6-jDRNCSfTZWxSTW7lwrkM"
GVIZ_BASE = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet="

OUT_DIR = Path(__file__).parent.parent / "inputdata"
OUT_DIR.mkdir(parents=True, exist_ok=True)

ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE


def read_sheet(tab_name):
    url = GVIZ_BASE + tab_name
    with urllib.request.urlopen(url, context=ssl_ctx) as resp:
        return pd.read_csv(io.BytesIO(resp.read()))


print("Downloading Reconcile_0426...")
reconcile = read_sheet("Reconcile_0426")
print(f"  {len(reconcile)} rows, columns: {reconcile.columns.tolist()[:13]}")

print("\nCode breakdown:")
print(reconcile["Code"].value_counts(dropna=False).to_string())

reconcile_filtered = reconcile[
    reconcile["Code"].str.strip().str.lower() != "skip"
].copy()
print(f"\n→ {len(reconcile_filtered)} rows after removing Code='skip'")

print("\nDownloading goodstuffcopy219...")
goodstuff = read_sheet("goodstuffcopy219")
# The join key in goodstuffcopy219 is ';shortname' — rename for the merge
goodstuff = goodstuff.rename(columns={";shortname": "shortname"})
print(f"  {len(goodstuff)} rows, {len(goodstuff.columns)} columns")

# Drop junk unnamed columns from the Reconcile tab before merging
reconcile_filtered = reconcile_filtered.loc[
    :, ~reconcile_filtered.columns.str.startswith("Unnamed:")
]

# Rename the blank-header catWISE J-designation column before merging
goodstuff = goodstuff.rename(columns={" ": "Jdesignation"})

# Left-join: every non-skip object gets its goodstuffcopy219 data if present
merged = reconcile_filtered.merge(goodstuff, on="shortname", how="left")

print(f"\nMerged table: {len(merged)} rows, {len(merged.columns)} columns")

out_path = OUT_DIR / "BYWsplib_merged.csv"
merged.to_csv(out_path, index=False)
print(f"Saved to {out_path}")

# Report any shortnames not found in goodstuffcopy219
missing = merged[merged["RA SXG"].isna()]["shortname"].tolist()
if missing:
    print(f"\n⚠ {len(missing)} objects not found in goodstuffcopy219:")
    for s in missing:
        print(f"  {s}")
else:
    print("\n✓ All non-skip objects matched in goodstuffcopy219")

print("\nColumn list in merged CSV:")
for col in merged.columns:
    print(f"  {col}")
