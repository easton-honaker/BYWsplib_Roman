"""
Validate the schema mapping: check nullable violations and type mismatches
for every column mapped in schema-match-result.md.
"""
import json, os, numpy as np
from astropy.table import Table

DATA_FILE   = "/Users/eastonhonaker/Documents/GitHub/BYWsplib_Roman/data/BYWsplib_merged.csv"
SIDECAR     = "/Users/eastonhonaker/Documents/GitHub/BYWsplib_Roman/tmp/astrodb-parse-result.json"

# Load with same reader as parse step
if os.path.exists(SIDECAR):
    meta = json.load(open(SIDECAR))
    reader = meta["reader"]
else:
    reader = "astropy"

if reader == "astropy":
    t = Table.read(DATA_FILE, format="csv")
else:
    import pandas as pd
    t = Table.from_pandas(pd.read_csv(DATA_FILE))

n_rows = len(t)

# Schema non-nullable fields (from schema.yaml)
# Format: {db_table.db_field: nullable}
NON_NULLABLE = {
    "Sources.source":               False,
    "Sources.reference":            False,
    "Names.source":                 False,
    "Names.other_name":             False,
    "Photometry.source":            False,
    "Photometry.reference":         False,
    "Parallaxes.source":            False,
    "Parallaxes.parallax_mas":      False,
    "Parallaxes.reference":         False,
    "ProperMotions.source":         False,
    "ProperMotions.pm_ra":          False,
    "ProperMotions.pm_dec":         False,
    "ProperMotions.reference":      False,
    "SourceTypes.source":           False,
    "SourceTypes.source_type":      False,
    "SourceTypes.reference":        False,
    "ModeledParameters.source":     False,
    "ModeledParameters.parameter":  False,
    "ModeledParameters.value":      False,
    "ModeledParameters.unit":       False,
    "ModeledParameters.reference":  False,
    "Spectra.source":               False,
    "Spectra.reference":            False,
    "Associations.source":          False,
    "Associations.reference":       False,
}

# Schema expected types: {db_table.db_field: felis_type}
SCHEMA_TYPES = {
    "Sources.source":               "string",
    "Sources.ra_deg":               "double",
    "Sources.dec_deg":              "double",
    "Sources.reference":            "string",
    "Sources.other_references":     "string",
    "Sources.comments":             "string",
    "Names.other_name":             "string",
    "Photometry.magnitude":         "double",
    "Photometry.magnitude_error":   "double",
    "Photometry.reference":         "string",
    "Parallaxes.parallax_mas":      "double",
    "Parallaxes.parallax_error":    "double",
    "Parallaxes.reference":         "string",
    "ProperMotions.pm_ra":          "double",
    "ProperMotions.pm_ra_error":    "double",
    "ProperMotions.pm_dec":         "double",
    "ProperMotions.pm_dec_error":   "double",
    "ProperMotions.reference":      "string",
    "SourceTypes.source_type":      "string",
    "SourceTypes.comments":         "string",
    "SourceTypes.reference":        "string",
    "ModeledParameters.value":      "double",
    "ModeledParameters.reference":  "string",
    "Spectra.observation_date":     "string",
    "Spectra.instrument":           "string",
    "Spectra.comments":             "string",
    "Spectra.reference":            "string",
    "Associations.association":     "string",
    "Associations.membership_probability": "double",
}

def count_nulls(col_data):
    """Count nulls/blanks/masked in a column."""
    arr = np.array(col_data)
    if np.ma.is_masked(col_data):
        return int(np.sum(col_data.mask))
    if arr.dtype.kind == 'f':
        return int(np.sum(np.isnan(arr.astype(float))))
    if arr.dtype.kind in ('U', 'S', 'O'):
        return int(np.sum((arr == None) | (arr == '') | (arr == 'nan')))
    return 0

def is_type_compatible(data_dtype, felis_type):
    """Check if numpy dtype is compatible with Felis type."""
    kind = np.dtype(data_dtype).kind
    if felis_type in ("double", "float"):
        return kind in ('f', 'i', 'u')   # float or int (widening OK)
    if felis_type == "string":
        return kind in ('U', 'S', 'O')
    if felis_type == "boolean":
        return kind == 'b'
    return True

# Mapping: input_col -> (db_table_field, note_if_needs_transform)
MAPPINGS = [
    ("shortname",          "Sources.source",               None),
    ("Jname",              "Names.other_name",             None),
    ("FINAL",              "SourceTypes.source_type",      None),
    ("Disc",               "Sources.reference",            "first token only"),
    ("Spec",               "SourceTypes.reference",        None),
    ("Dist_J",             "ModeledParameters.value",      "string→float: strip ' pc'"),
    ("Dist_W2",            "ModeledParameters.value",      "string→float: strip ' pc'"),
    ("Jdesignation",       "Names.other_name",             None),
    ("catWISE RA",         "Sources.ra_deg",               None),
    ("catWISE Dec",        "Sources.dec_deg",              None),
    ("i",                  "Photometry.magnitude",         "cast int64→float64"),
    ("ei",                 "Photometry.magnitude_error",   None),
    ("z",                  "Photometry.magnitude",         None),
    ("ez",                 "Photometry.magnitude_error",   None),
    ("y",                  "Photometry.magnitude",         None),
    ("ey",                 "Photometry.magnitude_error",   None),
    ("opt ref",            "Photometry.reference",         None),
    ("W1",                 "Photometry.magnitude",         None),
    ("eW1",                "Photometry.magnitude_error",   None),
    ("W2",                 "Photometry.magnitude",         None),
    ("eW2",                "Photometry.magnitude_error",   None),
    ("Y",                  "Photometry.magnitude",         None),
    ("eY",                 "Photometry.magnitude_error",   None),
    ("J",                  "Photometry.magnitude",         None),
    ("eJ",                 "Photometry.magnitude_error",   None),
    ("H",                  "Photometry.magnitude",         None),
    ("eH",                 "Photometry.magnitude_error",   None),
    ("K",                  "Photometry.magnitude",         None),
    ("eK",                 "Photometry.magnitude_error",   None),
    ("NIR ref",            "Photometry.reference",         "per-band parse needed"),
    ("plx",                "Parallaxes.parallax_mas",      None),
    ("eplx",               "Parallaxes.parallax_error",    None),
    ("plx_ref",            "Parallaxes.reference",         None),
    ("PMRA",               "ProperMotions.pm_ra",          None),
    ("ePMRA",              "ProperMotions.pm_ra_error",    None),
    ("PMDE",               "ProperMotions.pm_dec",         None),
    ("ePMDE",              "ProperMotions.pm_dec_error",   None),
    ("PM_ref",             "ProperMotions.reference",      None),
    ("PMTot",              "ModeledParameters.value",      None),
    ("Vtan",               "ModeledParameters.value",      None),
    ("Spectral Type",      "SourceTypes.source_type",      None),
    ("SpT_Comments",       "SourceTypes.comments",         None),
    ("Spectrum Date",      "Spectra.observation_date",     "YYMMDD float→ISO string"),
    ("Spectrum Instrument","Spectra.instrument",           None),
    ("Spectrum Observers", "Spectra.comments",             None),
    ("Submitted Name",     "Names.other_name",             None),
    ("BΣ_distance",        "ModeledParameters.value",      None),
    ("BΣ_PROB",            "ModeledParameters.value",      None),
    ("BΣ_YMGs",            "Associations.association",     "parse semicolon-separated"),
    ("Comment",            "Sources.comments",             None),
    ("extra2",             "Sources.comments",             None),
    ("Flags",              "Sources.comments",             None),
    ("Notes",              "Sources.comments",             None),
]

print(f"Rows: {n_rows}")
print(f"Columns in table: {t.colnames}")
print()

nullable_violations = []
type_mismatches = []
clean = []

for col_name, db_field, note in MAPPINGS:
    if col_name not in t.colnames:
        print(f"  WARN: '{col_name}' not in data file (may need transform before ingest)")
        continue

    col = t[col_name]
    null_count = count_nulls(col)
    dtype = str(col.dtype)
    expected_type = SCHEMA_TYPES.get(db_field)
    non_null = not NON_NULLABLE.get(db_field, True)  # True=nullable by default

    type_ok = True
    if expected_type:
        type_ok = is_type_compatible(col.dtype, expected_type)

    # Check nullable violation
    if not NON_NULLABLE.get(db_field, True) and null_count > 0:
        nullable_violations.append((col_name, db_field, null_count, n_rows,
                                    f"{100*null_count/n_rows:.1f}%", note or ""))

    # Check type mismatch
    if expected_type and not type_ok:
        type_mismatches.append((col_name, dtype, db_field, expected_type, "❌ No", note or ""))
    elif expected_type and note and ("string→float" in note or "cast" in note or "→ISO" in note):
        type_mismatches.append((col_name, dtype, db_field, expected_type, "⚠ Needs cast", note))
    elif null_count == 0 and type_ok:
        clean.append(f"{col_name} → {db_field}")
    else:
        clean.append(f"{col_name} → {db_field} ({null_count} nulls, nullable field)")

print("=== NULLABLE VIOLATIONS (non-nullable field has null data) ===")
for v in nullable_violations:
    print(f"  {v[0]} -> {v[1]}: {v[2]}/{v[3]} ({v[4]}) nulls")

print()
print("=== TYPE MISMATCHES / CASTS NEEDED ===")
for m in type_mismatches:
    print(f"  {m[0]} ({m[1]}) -> {m[2]} (expected {m[3]}): {m[4]} | {m[5]}")

print()
print(f"Clean: {len(clean)} columns")
print(f"Nullable violations: {len(nullable_violations)}")
print(f"Type mismatches/casts: {len(type_mismatches)}")
EOF