"""
Ingest Spectra from inputdata/BYWsplib_merged.csv into BYW_Roman.

  source           ← shortname
  regime           ← "nir" (all spectra are NIR)
  telescope        ← parsed from Spectrum Instrument (see INSTRUMENT_MAP)
  instrument       ← parsed from Spectrum Instrument
  mode             ← parsed from Spectrum Instrument
  observation_date ← Spectrum Date  (YYMMDD or YYYYMMDD → ISO YYYY-MM-DD)
  reference        ← Spec (first entry if comma-separated)
  comments         ← Spectrum Observers

Skips objects with null Spec (10 objects).
"""

import json
import logging
from datetime import date

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

# Spectrum Instrument string → (telescope, instrument, mode)
INSTRUMENT_MAP = {
    "SpeX Prism":     ("IRTF",     "SpeX",       "Prism"),
    "FIRE Prism":     ("Magellan", "FIRE",        "Prism"),
    "FIRE Echelle":   ("Magellan", "FIRE",        "Echelle"),
    "Keck NIRES":     ("Keck",     "NIRES",       "Prism"),
    "ArcoIRIS":       ("SOAR",     "ARCoIRIS",    "Prism"),
    "APO Triplespec": ("APO",      "TripleSpec",  "Prism"),
    "DCT NIHTS":      ("DCT",      "NIHTS",       "Prism"),
}

# ── Step 1: Populate Telescopes and Instruments lookup JSONs ──────────────────

telescopes = [{"telescope": t} for t in sorted({v[0] for v in INSTRUMENT_MAP.values()})]
with open("data/reference/Telescopes.json", "w") as f:
    json.dump(telescopes, f, indent=2)
logger.info(f"Telescopes.json written ({len(telescopes)} entries)")

instruments = [
    {"instrument": inst, "mode": mode, "telescope": tel}
    for tel, inst, mode in INSTRUMENT_MAP.values()
]
with open("data/reference/Instruments.json", "w") as f:
    json.dump(instruments, f, indent=2)
logger.info(f"Instruments.json written ({len(instruments)} entries)")

# ── Step 2: Build DB and ingest ───────────────────────────────────────────────

db = build_db_from_json(settings_file=SETTINGS_FILE)

Base = automap_base(metadata=db.metadata)
Base.prepare()
Spectra = Base.classes.Spectra

t = pd.read_csv(DATA_FILE, low_memory=False)

sources_in_db = {
    str(r["shortname"]).strip()
    for _, r in t.iterrows()
    if not pd.isna(r.get("catWISE RA")) and not pd.isna(r.get("catWISE Dec"))
}


def parse_obs_date(val):
    """Parse YYMMDD (6-digit) or YYYYMMDD (8-digit) float to a Python date object."""
    if pd.isna(val):
        return None
    s = str(int(val))
    if len(s) == 6:
        return date(2000 + int(s[:2]), int(s[2:4]), int(s[4:6]))
    elif len(s) == 8:
        return date(int(s[:4]), int(s[4:6]), int(s[6:8]))
    return None


added = skipped = failed = 0

with db.session as session:
    for _, row in t.iterrows():
        source = str(row["shortname"]).strip()

        if source not in sources_in_db:
            skipped += 1
            continue

        spec = row.get("Spec")
        if pd.isna(spec) or str(spec).strip() == "":
            skipped += 1
            continue

        reference = str(spec).strip().split(",")[0].strip()

        instr_str = str(row.get("Spectrum Instrument", "")).strip()
        if instr_str not in INSTRUMENT_MAP:
            logger.warning(f"  SKIP {source}: unknown instrument '{instr_str}'")
            skipped += 1
            continue

        telescope, instrument, mode = INSTRUMENT_MAP[instr_str]
        obs_date = parse_obs_date(row.get("Spectrum Date"))
        if obs_date is None:
            logger.warning(f"  SKIP {source}: null Spectrum Date")
            skipped += 1
            continue
        observers = row.get("Spectrum Observers")
        comments = str(observers).strip() if not pd.isna(observers) else None

        try:
            session.add(Spectra(
                source=source,
                regime="nir",
                telescope=telescope,
                instrument=instrument,
                mode=mode,
                observation_date=obs_date,
                reference=reference,
                comments=comments,
            ))
            added += 1
        except Exception as e:
            session.rollback()
            failed += 1
            logger.warning(f"  FAILED {source}: {e}")

    session.commit()

logger.info(f"\nSpectra: {added} added, {skipped} skipped, {failed} failed")

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
