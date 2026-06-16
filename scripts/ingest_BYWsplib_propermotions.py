"""
Ingest ProperMotions from inputdata/BYWsplib_merged.csv into BYW_Roman.

  pm_ra       ← PMRA   (nullable=false, skip row if null)
  pm_ra_error ← ePMRA
  pm_dec      ← PMDE   (nullable=false)
  pm_dec_error← ePMDE
  pm_total    ← PMTot
  v_tan       ← Vtan
  reference   ← PM_ref (FK to Publications)
  adopted     ← True

Skips the 9 binary components with null PMRA/PMDE.
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

# ── Step 1: Add new Publications ──────────────────────────────────────────────

NEW_PUBS = [
    "NSC (Adam)", "NSC DR2", "PS1 (Adam)", "UHS (Adam)",
    "VHS (Adam)", "VIKING (Adam)", "VIKING+UKIDSS LAS (Adam)",
    "VIKING+VHS (Adam)", "unTimely (Adam)",
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
logger.info(f"Publications: {added_pubs} new entries added to JSON")

# ── Step 2: Build DB and ingest ───────────────────────────────────────────────

db = build_db_from_json(settings_file=SETTINGS_FILE)

Base = automap_base(metadata=db.metadata)
Base.prepare()
ProperMotions = Base.classes.ProperMotions

t = pd.read_csv(DATA_FILE, low_memory=False)

added = skipped = failed = 0

with db.session as session:
    for _, row in t.iterrows():
        source = str(row["shortname"]).strip()
        pmra = row.get("PMRA")
        pmde = row.get("PMDE")

        if pd.isna(pmra) or pd.isna(pmde):
            skipped += 1
            continue

        reference = str(row.get("PM_ref", "")).strip()
        if not reference or reference == "nan":
            logger.warning(f"  SKIP {source}: null PM_ref")
            skipped += 1
            continue

        epmra = row.get("ePMRA")
        epmde = row.get("ePMDE")
        pmtot = row.get("PMTot")
        vtan  = row.get("Vtan")

        try:
            session.add(ProperMotions(
                source=source,
                pm_ra=float(pmra),
                pm_ra_error=float(epmra) if not pd.isna(epmra) else None,
                pm_dec=float(pmde),
                pm_dec_error=float(epmde) if not pd.isna(epmde) else None,
                pm_total=float(pmtot) if not pd.isna(pmtot) else None,
                v_tan=float(vtan) if not pd.isna(vtan) else None,
                reference=reference,
                adopted=True,
            ))
            added += 1
        except Exception as e:
            session.rollback()
            failed += 1
            logger.warning(f"  FAILED {source}: {e}")
            continue

    session.commit()

logger.info(f"\nProperMotions: {added} added, {skipped} skipped, {failed} failed")

if SAVE_DB:
    db.save_database("data/")
    # Strip null fields from Publications JSON (save_database re-introduces them)
    pubs = json.load(open(PUB_PATH))
    pubs_clean = [{k: v for k, v in p.items() if v is not None} for p in pubs]
    with open(PUB_PATH, "w") as f:
        json.dump(pubs_clean, f, indent=2)
    logger.info("Database saved.")
else:
    logger.info("Dry run — NOT saved. Set SAVE_DB = True to persist.")
