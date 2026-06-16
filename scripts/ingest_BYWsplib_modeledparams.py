"""
Ingest ModeledParameters from inputdata/BYWsplib_merged.csv into BYW_Roman.

Parameters ingested:
  distance_J    ← Dist_J   (string "32.9 pc" → float, strip " pc"; model=photometric)
  distance_W2   ← Dist_W2  (string "37.4 pc" → float; model=photometric)
  bayes_distance← BΣ_distance (float, pc; model=BetaSigma)
  bayes_prob    ← BΣ_PROB    (float, dimensionless; model=BetaSigma)

All rows use reference=EastonH (user-computed).
Skip rows where value is null or '0' (null placeholder in Dist_J/Dist_W2).
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
REFERENCE = "EastonH"

PUB_PATH = "data/reference/Publications.json"

# ── Step 1: Populate ParameterList JSON ───────────────────────────────────────

PARAMETERS = [
    {"parameter": "distance_J",     "description": "Photometric distance from J-band magnitude (pc)"},
    {"parameter": "distance_W2",    "description": "Photometric distance from W2-band magnitude (pc)"},
    {"parameter": "bayes_distance", "description": "Bayesian sigma distance estimate (pc)"},
    {"parameter": "bayes_prob",     "description": "Bayesian sigma membership probability (dimensionless)"},
]
with open("data/reference/ParameterList.json", "w") as f:
    json.dump(PARAMETERS, f, indent=2)
logger.info(f"ParameterList.json written ({len(PARAMETERS)} entries)")

# ── Step 2: Build DB and ingest ───────────────────────────────────────────────

db = build_db_from_json(settings_file=SETTINGS_FILE)

Base = automap_base(metadata=db.metadata)
Base.prepare()
ModeledParameters = Base.classes.ModeledParameters

t = pd.read_csv(DATA_FILE, low_memory=False)

# Sources that exist in the DB (have valid RA/Dec)
sources_in_db = {
    str(r["shortname"]).strip()
    for _, r in t.iterrows()
    if not pd.isna(r.get("catWISE RA")) and not pd.isna(r.get("catWISE Dec"))
}

added = skipped = failed = 0


def parse_pc(val):
    """Parse values like '32.9 pc' or '32.9' to float; return None if invalid."""
    if pd.isna(val):
        return None
    s = str(val).replace(" pc", "").strip()
    try:
        f = float(s)
        return None if f == 0.0 else f
    except ValueError:
        return None


with db.session as session:
    for _, row in t.iterrows():
        source = str(row["shortname"]).strip()
        if source not in sources_in_db:
            skipped += 4
            continue

        # (data_col, parse_fn, parameter_name, model, unit)
        to_ingest = [
            (row.get("Dist_J"),       parse_pc,  "distance_J",     "photometric", "pc"),
            (row.get("Dist_W2"),      parse_pc,  "distance_W2",    "photometric", "pc"),
            (row.get("BΣ_distance"),  float,     "bayes_distance", "BetaSigma",   "pc"),
            (row.get("BΣ_PROB"),      float,     "bayes_prob",     "BetaSigma",   ""),
        ]

        for raw, parse_fn, param, model, unit in to_ingest:
            if pd.isna(raw):
                skipped += 1
                continue
            try:
                value = parse_fn(raw) if parse_fn is not float else float(raw)
            except (ValueError, TypeError):
                skipped += 1
                continue
            if value is None:
                skipped += 1
                continue
            try:
                session.add(ModeledParameters(
                    source=source,
                    parameter=param,
                    model=model,
                    value=value,
                    unit=unit,
                    reference=REFERENCE,
                ))
                added += 1
            except Exception as e:
                session.rollback()
                failed += 1
                logger.warning(f"  FAILED {source} {param}: {e}")

    session.commit()

logger.info(f"\nModeledParameters: {added} added, {skipped} skipped, {failed} failed")

if SAVE_DB:
    db.save_database("data/")
    pubs = json.load(open(PUB_PATH))
    pubs_clean = [{k: v for k, v in p.items() if v is not None} for p in pubs]
    with open(PUB_PATH, "w") as f:
        json.dump(pubs_clean, f, indent=2)
    pfilt = json.load(open("data/reference/PhotometryFilters.json"))
    pfilt_clean = [{k: v for k, v in r.items() if v is not None} for r in pfilt]
    with open("data/reference/PhotometryFilters.json", "w") as f:
        json.dump(pfilt_clean, f, indent=2)
    logger.info("Database saved.")
else:
    logger.info("Dry run — NOT saved. Set SAVE_DB = True to persist.")
