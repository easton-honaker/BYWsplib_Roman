"""
Ingest Associations from inputdata/BYWsplib_merged.csv into BYW_Roman.

BΣ_YMGs format: semicolon-separated entries, each optionally followed by (PROB)
  e.g. "ARG(68);CARN(32)"  → ARG with prob=68, CARN with prob=32
       "BPMG"               → BPMG with prob=null

One Associations row per (source, association) pair.
AssociationList is pre-populated with all unique YMG names.
Reference = EastonH for all rows (BetaSigma-derived membership).
"""

import json
import logging
import re

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
PUB_PATH = "data/reference/Publications.json"
REFERENCE = "EastonH"


def parse_ymg_entry(entry):
    """Parse 'NAME(PROB)' or 'NAME' → (name, prob_or_None)."""
    m = re.match(r"^([A-Za-z0-9+_]+)\s*\((\d+)\)$", entry.strip())
    if m:
        return m.group(1), float(m.group(2))
    name = entry.strip()
    if name:
        return name, None
    return None, None


# ── Step 1: Collect all unique YMG names and write AssociationList ────────────

t = pd.read_csv(DATA_FILE, low_memory=False)

sources_in_db = {
    str(r["shortname"]).strip()
    for _, r in t.iterrows()
    if not pd.isna(r.get("catWISE RA")) and not pd.isna(r.get("catWISE Dec"))
}

all_assoc_names = set()
for _, row in t.iterrows():
    ymg_val = row.get("BΣ_YMGs")
    if pd.isna(ymg_val) or str(ymg_val).strip() == "":
        continue
    for entry in str(ymg_val).split(";"):
        name, _ = parse_ymg_entry(entry)
        if name:
            all_assoc_names.add(name)

assoc_list = [{"association": a, "reference": REFERENCE} for a in sorted(all_assoc_names)]
with open("data/reference/AssociationList.json", "w") as f:
    json.dump(assoc_list, f, indent=2)
logger.info(f"AssociationList.json written ({len(assoc_list)} entries)")

# ── Step 2: Build DB and ingest ───────────────────────────────────────────────

db = build_db_from_json(settings_file=SETTINGS_FILE)

Base = automap_base(metadata=db.metadata)
Base.prepare()
Associations = Base.classes.Associations

added = skipped = failed = 0

with db.session as session:
    for _, row in t.iterrows():
        source = str(row["shortname"]).strip()

        if source not in sources_in_db:
            skipped += 1
            continue

        ymg_val = row.get("BΣ_YMGs")
        if pd.isna(ymg_val) or str(ymg_val).strip() == "":
            skipped += 1
            continue

        for entry in str(ymg_val).split(";"):
            assoc_name, prob = parse_ymg_entry(entry)
            if not assoc_name:
                continue
            try:
                session.add(Associations(
                    source=source,
                    association=assoc_name,
                    membership_probability=prob,
                    reference=REFERENCE,
                ))
                added += 1
            except Exception as e:
                session.rollback()
                failed += 1
                logger.warning(f"  FAILED {source} / {assoc_name}: {e}")

    session.commit()

logger.info(f"\nAssociations: {added} added, {skipped} skipped, {failed} failed")

if SAVE_DB:
    db.save_database("data/")
    for path in [PUB_PATH, "data/reference/PhotometryFilters.json"]:
        rows = json.load(open(path))
        rows_clean = [{k: v for k, v in r.items() if v is not None} for r in rows]
        with open(path, "w") as f:
            json.dump(rows_clean, f, indent=2)
    logger.info("Database saved.")
else:
    logger.info("Dry run — NOT saved. Set SAVE_DB = True to persist.")
