"""
Ingest Sources and Names from inputdata/BYWsplib_merged.csv into BYW_Roman.

Sources:
  source     ← shortname
  ra_deg     ← catWISE RA
  dec_deg    ← catWISE Dec
  reference  ← Disc  (EastonH for the 9 objects where Disc is null)
  comments   ← concatenation of Comment, extra2, Flags, Notes (non-null)

Names (one row per non-null alias per source):
  Jname, Jdesignation, Submitted Name
"""

import logging

import pandas as pd

from astrodb_utils import build_db_from_json
from astrodb_utils.sources import ingest_name, ingest_source

logging.getLogger("astrodb_utils").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.basicConfig(format="%(levelname)s - %(message)s")

SAVE_DB = True
SETTINGS_FILE = "database.toml"
DATA_FILE = "inputdata/BYWsplib_merged.csv"
FALLBACK_REF = "EastonH"

t = pd.read_csv(DATA_FILE, low_memory=False)
db = build_db_from_json(settings_file=SETTINGS_FILE)

sources_added = sources_skipped = sources_failed = 0
names_added = names_failed = 0

COMMENT_COLS = ["Comment", "extra2", "Flags", "Notes"]

for _, row in t.iterrows():
    source = str(row["shortname"]).strip()
    ra = row.get("catWISE RA")
    dec = row.get("catWISE Dec")

    # Skip rows where we can't place the object in the sky
    if pd.isna(ra) or pd.isna(dec):
        logger.warning(f"  SKIP {source}: null RA/Dec")
        sources_skipped += 1
        continue

    # Discovery reference — split comma-separated entries; first is the FK reference
    disc = row.get("Disc")
    if pd.isna(disc) or str(disc).strip() == "":
        disc_parts = [FALLBACK_REF]
    else:
        disc_parts = [p.strip() for p in str(disc).split(",") if p.strip()]
    reference = disc_parts[0]
    other_references = ", ".join(disc_parts[1:]) if len(disc_parts) > 1 else None

    # Build comments string from all comment-like columns
    comment_parts = []
    for col in COMMENT_COLS:
        val = row.get(col)
        if not pd.isna(val) and str(val).strip():
            comment_parts.append(f"{col}: {str(val).strip()}")
    comment = "; ".join(comment_parts) if comment_parts else None

    try:
        ingest_source(
            db,
            source,
            reference,
            ra=float(ra),
            dec=float(dec),
            other_reference=other_references,
            comment=comment,
            use_simbad=False,
            search_db=False,
            raise_error=True,
        )
        sources_added += 1
        logger.info(f"  source: {source}")
    except Exception as e:
        sources_failed += 1
        logger.warning(f"  FAILED source {source}: {e}")
        continue

    # Names
    for col in ["Jname", "Jdesignation", "Submitted Name"]:
        val = row.get(col)
        if pd.isna(val) or str(val).strip() == "":
            continue
        name_str = str(val).strip()
        try:
            ingest_name(db, source=source, other_name=name_str, raise_error=True)
            names_added += 1
        except Exception as e:
            names_failed += 1
            logger.warning(f"  FAILED name {name_str} for {source}: {e}")

logger.info(
    f"\nSources: {sources_added} added, {sources_skipped} skipped, {sources_failed} failed"
)
logger.info(f"Names:   {names_added} added, {names_failed} failed")

if SAVE_DB:
    db.save_database("data/")
    logger.info("Database saved.")
else:
    logger.info("Dry run — NOT saved. Set SAVE_DB = True to persist.")
