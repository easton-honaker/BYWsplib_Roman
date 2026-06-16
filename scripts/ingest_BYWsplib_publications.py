"""
Ingest all publication shortnames from Disc and Spec columns of BYWsplib_merged.csv
into the Publications table. Uses ignore_ads=True; shortname is used as its own description.
"""

import logging

import pandas as pd

from astrodb_utils import build_db_from_json
from astrodb_utils.publications import find_publication, ingest_publication

logging.getLogger("astrodb_utils").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.basicConfig(format="%(levelname)s - %(message)s")

SAVE_DB = True
SETTINGS_FILE = "database.toml"
DATA_FILE = "inputdata/BYWsplib_merged.csv"

# ── Collect unique shortnames from Disc and Spec only ─────────────────────────

t = pd.read_csv(DATA_FILE, low_memory=False)
refs: set[str] = set()

for col in ["Disc", "Spec"]:
    for val in t[col].dropna():
        for part in str(val).split(","):
            part = part.strip()
            if part and part.lower() not in ("nan", ""):
                refs.add(part)

PUBLICATIONS = sorted(refs)
logger.info(f"Found {len(PUBLICATIONS)} unique reference shortnames to ingest")

# ── Ingest ────────────────────────────────────────────────────────────────────

db = build_db_from_json(settings_file=SETTINGS_FILE)

added = already_present = failed = 0

for ref in PUBLICATIONS:
    found, result = find_publication(db, reference=ref)
    if found:
        already_present += 1
        logger.info(f"  already present: {ref}")
        continue

    try:
        ingest_publication(
            db,
            reference=ref,
            description=ref,
            ignore_ads=True,
        )
        added += 1
        logger.info(f"  ingested: {ref}")
    except Exception as e:
        failed += 1
        logger.warning(f"  FAILED {ref}: {e}")

logger.info(
    f"\nDone: {added} added, {already_present} already present, {failed} failed "
    f"(total {len(PUBLICATIONS)})"
)

if SAVE_DB:
    db.save_database("data/")
    logger.info("Database saved.")
else:
    logger.info("Dry run — NOT saved. Set SAVE_DB = True to persist.")
