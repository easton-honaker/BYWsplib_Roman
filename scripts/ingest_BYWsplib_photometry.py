"""
Ingest photometry into BYW_Roman.

Bands ingested:
  W1, W2  ← CatWISE2020 (all objects with non-null W1/W2)
  Y, J, H, K ← per-band reference parsed from NIR ref column

NIR ref parsing rules:
  - Single survey → all bands from that survey
  - Multiple surveys → explicit "(BAND)" entries assign that survey to that band;
    the non-parenthetical (non-PS1) survey covers all remaining bands;
    PS1 without parens → Y (PS1's only NIR-adjacent band)
"""

import json
import logging
import re

import pandas as pd

from astrodb_utils import build_db_from_json
from astrodb_utils.photometry import ingest_photometry

logging.getLogger("astrodb_utils").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.basicConfig(format="%(levelname)s - %(message)s")

SAVE_DB = True
SETTINGS_FILE = "database.toml"
DATA_FILE = "inputdata/BYWsplib_merged.csv"
WISE_REF = "CatWISE2020"

# ── Step 1: Add new Publications (survey names) directly to JSON ───────────────

NEW_PUBS = [
    "CatWISE2020", "2MASS", "PS1", "Sandy/Gemini",
    "UHS", "UHS DR3", "UKIDSS GCS", "UKIDSS GPS", "UKIDSS LAS",
    "VHS", "VIKING", "VIRAC2", "VVV",
]

PUB_PATH = "data/reference/Publications.json"
pubs = json.load(open(PUB_PATH))
existing_refs = {p["reference"] for p in pubs}
added_pubs = 0
for ref in NEW_PUBS:
    if ref not in existing_refs:
        pubs.append({"reference": ref, "description": ref})
        existing_refs.add(ref)
        added_pubs += 1
        logger.info(f"  pub added: {ref}")
pubs.sort(key=lambda p: p["reference"])
with open(PUB_PATH, "w") as f:
    json.dump(pubs, f, indent=2)
logger.info(f"Publications: {added_pubs} new survey entries added to JSON")

# ── Step 2: Build DB and add PhotometryFilters ─────────────────────────────────

db = build_db_from_json(settings_file=SETTINGS_FILE)

# Filters are pre-loaded via data/reference/PhotometryFilters.json — no action needed here

# ── NIR ref parser ─────────────────────────────────────────────────────────────

def parse_nir_ref(nir_ref_str):
    """Return dict mapping band letter (Y/J/H/K) to survey name string."""
    if pd.isna(nir_ref_str) or str(nir_ref_str).strip() == "":
        return {}

    parts = [p.strip() for p in str(nir_ref_str).split(",")]

    explicit = {}   # band -> survey (from "(BAND)" notation)
    primary_surveys = []  # surveys without explicit band

    for part in parts:
        m = re.match(r"^(.+?)\s*\(([A-Za-z]+)\)\s*(?:reject)?$", part.strip())
        if m:
            survey = re.sub(r"\breject\b", "", m.group(1)).strip()
            band = m.group(2).upper()
            explicit[band] = survey
        else:
            survey = re.sub(r"\breject\b", "", part).strip()
            if survey:
                primary_surveys.append(survey)

    band_ref = dict(explicit)

    if len(primary_surveys) == 1:
        # Single primary: covers all bands not explicitly assigned
        primary = primary_surveys[0]
        for b in ["Y", "J", "H", "K"]:
            if b not in band_ref:
                band_ref[b] = primary
    elif len(primary_surveys) > 1:
        # PS1 without parens → always Y
        if "PS1" in primary_surveys:
            if "Y" not in band_ref:
                band_ref["Y"] = "PS1"
            primary_surveys = [s for s in primary_surveys if s != "PS1"]
        # Remaining primary → all other unassigned bands
        if primary_surveys:
            primary = primary_surveys[0]
            for b in ["Y", "J", "H", "K"]:
                if b not in band_ref:
                    band_ref[b] = primary

    return band_ref

# ── Step 3: Ingest photometry ──────────────────────────────────────────────────

t = pd.read_csv(DATA_FILE, low_memory=False)

added = failed = 0

for _, row in t.iterrows():
    source = str(row["shortname"]).strip()

    # WISE W1/W2
    for band, mag_col, err_col in [("W1", "W1", "eW1"), ("W2", "W2", "eW2")]:
        mag = row.get(mag_col)
        err = row.get(err_col)
        if pd.isna(mag):
            continue
        try:
            ingest_photometry(
                db,
                source=source,
                band=band,
                magnitude=float(mag),
                magnitude_error=float(err) if not pd.isna(err) else None,
                reference=WISE_REF,
                regime="mir",
                raise_error=True,
            )
            added += 1
        except Exception as e:
            failed += 1
            logger.warning(f"  FAILED {source} {band}: {e}")

    # NIR Y/J/H/K
    nir_ref = row.get("NIR ref")
    if pd.isna(nir_ref):
        continue

    band_refs = parse_nir_ref(nir_ref)

    for band, mag_col, err_col in [("Y","Y","eY"), ("J","J","eJ"), ("H","H","eH"), ("K","K","eK")]:
        mag = row.get(mag_col)
        err = row.get(err_col)
        if pd.isna(mag):
            continue
        ref = band_refs.get(band)
        if not ref:
            logger.warning(f"  SKIP {source} {band}: no ref parsed from '{nir_ref}'")
            continue
        try:
            ingest_photometry(
                db,
                source=source,
                band=band,
                magnitude=float(mag),
                magnitude_error=float(err) if not pd.isna(err) else None,
                reference=ref,
                regime="nir",
                raise_error=True,
            )
            added += 1
        except Exception as e:
            failed += 1
            logger.warning(f"  FAILED {source} {band}: {e}")

logger.info(f"\nPhotometry: {added} rows added, {failed} failed")

if SAVE_DB:
    db.save_database("data/")
    logger.info("Database saved.")
else:
    logger.info("Dry run — NOT saved. Set SAVE_DB = True to persist.")
