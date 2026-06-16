"""
Ingest Parallaxes from inputdata/BYWsplib_merged.csv into BYW_Roman.

  parallax_mas  ← plx
  parallax_error ← eplx
  reference      ← plx_ref  (normalized: 'Gaia DR3' → 'GaiaDR3')
  adopted        ← True for all (only one measurement per source)

Skips rows where plx is null (172/258 objects have no parallax).
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

# Normalize variant spellings before looking up in Publications
REF_MAP = {"Gaia DR3": "GaiaDR3"}

# ── Step 1: Add new Publications directly to JSON ─────────────────────────────

NEW_PUBS = ["Best20", "GaiaDR3", "Kirk21"]

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

# ── Step 2: Build DB and ingest via ORM ───────────────────────────────────────

db = build_db_from_json(settings_file=SETTINGS_FILE)

Base = automap_base(metadata=db.metadata)
Base.prepare()
Parallaxes = Base.classes.Parallaxes

t = pd.read_csv(DATA_FILE, low_memory=False)

added = skipped = failed = 0

with db.session as session:
    for _, row in t.iterrows():
        source = str(row["shortname"]).strip()
        plx = row.get("plx")
        if pd.isna(plx):
            skipped += 1
            continue

        eplx = row.get("eplx")
        raw_ref = str(row.get("plx_ref", "")).strip()
        reference = REF_MAP.get(raw_ref, raw_ref)

        if not reference or reference == "nan":
            logger.warning(f"  SKIP {source}: null plx_ref")
            skipped += 1
            continue

        try:
            session.add(Parallaxes(
                source=source,
                parallax_mas=float(plx),
                parallax_error=float(eplx) if not pd.isna(eplx) else None,
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

logger.info(f"\nParallaxes: {added} added, {skipped} skipped (no plx), {failed} failed")

if SAVE_DB:
    db.save_database("data/")
    logger.info("Database saved.")
else:
    logger.info("Dry run — NOT saved. Set SAVE_DB = True to persist.")
