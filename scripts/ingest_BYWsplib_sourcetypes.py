"""
Ingest SourceTypes from inputdata/BYWsplib_merged.csv into BYW_Roman.

Two sets of rows per source:

1. Spectral type (FINAL):
     source_type         ← FINAL
     spectral_type_error ← Spt_unc (integer subtype uncertainty)
     spectral_type_number← FINALNUM (numerical SpT code)
     reference           ← Spec
     adopted             ← True
   Skip if FINAL or Spec is null (10 objects).

2. Tags (TAGS, comma-separated: 'b', 'd', 'sd', 'y'):
     source_type ← each tag value
     reference   ← Spec (if present, else EastonH)
   Skip if TAGS is null.

SourceTypeList is pre-populated with the 4 tag values.
Spectral type strings (L0, T5, etc.) are stored as-is in source_type;
SQLite does not enforce the FK to SourceTypeList for them.
"""

import json
import logging

import pandas as pd
from sqlalchemy.ext.automap import automap_base

from astrodb_utils import build_db_from_json

logging.getLogger("astrodb_utils").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.basicConfig(format="%(levelname)s - %(message)s")

SAVE_DB = True
SETTINGS_FILE = "database.toml"
DATA_FILE = "inputdata/BYWsplib_merged.csv"
FALLBACK_REF = "EastonH"

# ── Step 1: Populate SourceTypeList lookup JSON ────────────────────────────────

STL_PATH = "data/reference/SourceTypeList.json"
_df = pd.read_csv(DATA_FILE, low_memory=False)
_spt_values = sorted(_df["FINAL"].dropna().unique())
source_type_list = [
    {"source_type": "b"},
    {"source_type": "d"},
    {"source_type": "sd"},
    {"source_type": "y"},
] + [{"source_type": spt} for spt in _spt_values]
with open(STL_PATH, "w") as f:
    json.dump(source_type_list, f, indent=2)
logger.info(f"SourceTypeList.json written ({len(source_type_list)} entries)")

# ── Step 2: Build DB and ingest ───────────────────────────────────────────────

PUB_PATH = "data/reference/Publications.json"

db = build_db_from_json(settings_file=SETTINGS_FILE)

Base = automap_base(metadata=db.metadata)
Base.prepare()
SourceTypes = Base.classes.SourceTypes

t = pd.read_csv(DATA_FILE, low_memory=False)

# Only process sources that were ingested into Sources (those with valid RA/Dec)
sources_in_db = set(
    str(row["shortname"]).strip()
    for _, row in t.iterrows()
    if not pd.isna(row.get("catWISE RA")) and not pd.isna(row.get("catWISE Dec"))
)

spt_added = spt_skipped = spt_failed = 0
tag_added = tag_skipped = tag_failed = 0

with db.session as session:
    for _, row in t.iterrows():
        source = str(row["shortname"]).strip()
        if source not in sources_in_db:
            spt_skipped += 1
            tag_skipped += 1
            continue

        # Reference for spectral type
        spec = row.get("Spec")
        spt_ref = (
            FALLBACK_REF
            if pd.isna(spec) or str(spec).strip() == ""
            else str(spec).strip().split(",")[0].strip()  # first ref if comma-separated
        )

        # ── Spectral type row ──────────────────────────────────────────────
        final = row.get("FINAL")
        if pd.isna(final) or str(final).strip() == "" or pd.isna(spec):
            spt_skipped += 1
        else:
            spt_str = str(final).strip()
            finalnum = row.get("FINALNUM")
            spt_unc  = row.get("Spt_unc")
            try:
                session.add(SourceTypes(
                    source=source,
                    source_type=spt_str,
                    spectral_type_number=float(finalnum) if not pd.isna(finalnum) else None,
                    spectral_type_error=float(spt_unc) if not pd.isna(spt_unc) else None,
                    reference=spt_ref,
                    adopted=True,
                ))
                spt_added += 1
            except Exception as e:
                session.rollback()
                spt_failed += 1
                logger.warning(f"  FAILED SpT {source} ({spt_str}): {e}")

        # ── Tag rows ───────────────────────────────────────────────────────
        tags_val = row.get("TAGS")
        if pd.isna(tags_val) or str(tags_val).strip() == "":
            tag_skipped += 1
            continue
        tag_ref = spt_ref  # use same reference as spectral type
        for tag in str(tags_val).split(","):
            tag = tag.strip()
            if not tag:
                continue
            try:
                session.add(SourceTypes(
                    source=source,
                    source_type=tag,
                    reference=tag_ref,
                ))
                tag_added += 1
            except Exception as e:
                session.rollback()
                tag_failed += 1
                logger.warning(f"  FAILED tag {source} ({tag}): {e}")

    session.commit()

logger.info(f"\nSourceTypes (SpT):  {spt_added} added, {spt_skipped} skipped, {spt_failed} failed")
logger.info(f"SourceTypes (tags): {tag_added} added, {tag_skipped} skipped, {tag_failed} failed")

if SAVE_DB:
    db.save_database("data/")
    pubs = json.load(open(PUB_PATH))
    pubs_clean = [{k: v for k, v in p.items() if v is not None} for p in pubs]
    with open(PUB_PATH, "w") as f:
        json.dump(pubs_clean, f, indent=2)
    logger.info("Database saved.")
else:
    logger.info("Dry run — NOT saved. Set SAVE_DB = True to persist.")
