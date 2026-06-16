## Schema Mapping Validation Report
Source: `data/BYWsplib_merged.csv` → `schema.yaml`
Date: 2026-06-15

---

### Nullable Violations  (15 issues)

These columns map to a `nullable: false` field in the schema but contain null/masked values in the
data. Inserting null rows without filtering will raise a database constraint error. The correct
mitigation for all 15 is **row-skipping** — only insert a row when the required field is non-null.
See the Notes column for exceptions.

| Data Column | Maps To | Null Count | Total Rows | % Null | Notes |
|---|---|---|---|---|---|
| `Disc` | Sources.reference | 9 | 258 | 3.5% | The 9 binary components not found in goodstuffcopy219. Discovery reference unknown. **Action required**: look up reference for these 9 objects before ingest, or skip them. |
| `Jdesignation` | Names.other_name | 9 | 258 | 3.5% | Same 9 missing objects. Skip Names row when null. |
| `Submitted Name` | Names.other_name | 9 | 258 | 3.5% | Same 9 missing objects. Skip Names row when null. |
| `opt ref` | Photometry.reference | 257 | 258 | 99.6% | **Genuine data gap**: PS1 optical photometry (i, z, y) is present for only 1/258 objects. i, z, y columns are correspondingly all-null. Optical photometry ingestion is not feasible from this dataset. |
| `NIR ref` | Photometry.reference | 9 | 258 | 3.5% | Same 9 missing objects. Skip NIR Photometry rows when null. |
| `plx` | Parallaxes.parallax_mas | 172 | 258 | 66.7% | Expected — most L/T dwarfs lack a parallax measurement. 86 objects have parallax. Skip Parallaxes row when null. |
| `plx_ref` | Parallaxes.reference | 172 | 258 | 66.7% | Matches plx null pattern exactly. |
| `PMRA` | ProperMotions.pm_ra | 9 | 258 | 3.5% | Same 9 missing objects. Skip ProperMotions row when null. |
| `PMDE` | ProperMotions.pm_dec | 9 | 258 | 3.5% | Same 9 missing objects. |
| `PM_ref` | ProperMotions.reference | 9 | 258 | 3.5% | Same 9 missing objects. |
| `Spec` | SourceTypes.reference | 10 | 258 | 3.9% | 10 objects have no spectroscopy reference. Skip SourceTypes row (and Spectra row) when Spec is null. |
| `Dist_J` | ModeledParameters.value | 15 | 258 | 5.8% | 15 objects missing photometric distance. Also has type mismatch (see below). |
| `Dist_W2` | ModeledParameters.value | 10 | 258 | 3.9% | 10 objects missing W2-based distance. Also has type mismatch. |
| `BΣ_distance` | ModeledParameters.value | 196 | 258 | 76.0% | Expected — Bayesian distance estimates available for only 62 objects. Skip when null. |
| `BΣ_PROB` | ModeledParameters.value | 196 | 258 | 76.0% | Matches BΣ_distance null pattern exactly. |

**Objects with null Disc (Sources.reference cannot be null):**
`0011-0521B`, `0020-1535`, `0146-0508B`, `0643+1950A`, `0809+7417B`, `0904+6106`, `1810-0657A`, `1810-0657B`, `2053+3319B`

These 9 objects are all binary components or co-movers not present in goodstuffcopy219. Their
discovery references must be determined from an external source before they can be ingested into
`Sources`. Until then, skip them and their dependent rows (Names, Photometry, ProperMotions).

---

### Type Mismatches  (4 issues)

| Data Column | Data Type | Maps To | Expected Type | Compatible? | Transform |
|---|---|---|---|---|---|
| `Dist_J` | str (`<U11`) | ModeledParameters.value | double | ⚠ Needs cast | Strip " pc" suffix, parse as float. Filter out '0' values (null placeholder). |
| `Dist_W2` | str (`<U8`) | ModeledParameters.value | double | ⚠ Needs cast | Strip " pc" suffix, parse as float. |
| `i` | int64 | Photometry.magnitude | double | ⚠ Needs cast | Cast to float64. (Moot: all i values are null; optical phot not available.) |
| `Spectrum Date` | float64 | Spectra.observation_date | string | ⚠ Needs cast | Convert YYMMDD integer (e.g. `230629`) → ISO date string `"2023-06-29"`. Prefix 20 for 2000s dates. |

---

### Clean Mappings  (36 columns OK)

All columns below pass both the nullable constraint check and the type compatibility check.

```
shortname       → Sources.source
Jname           → Names.other_name
FINAL           → SourceTypes.source_type
catWISE RA      → Sources.ra_deg
catWISE Dec     → Sources.dec_deg
ei              → Photometry.magnitude_error
z               → Photometry.magnitude
ez              → Photometry.magnitude_error
y               → Photometry.magnitude
ey              → Photometry.magnitude_error
W1              → Photometry.magnitude
eW1             → Photometry.magnitude_error
W2              → Photometry.magnitude
eW2             → Photometry.magnitude_error
Y               → Photometry.magnitude
eY              → Photometry.magnitude_error
J               → Photometry.magnitude
eJ              → Photometry.magnitude_error
H               → Photometry.magnitude
eH              → Photometry.magnitude_error
K               → Photometry.magnitude
eK              → Photometry.magnitude_error
eplx            → Parallaxes.parallax_error
ePMRA           → ProperMotions.pm_ra_error
ePMDE           → ProperMotions.pm_dec_error
PMTot           → ModeledParameters.value
Vtan            → ModeledParameters.value
Spectral Type   → SourceTypes.source_type
SpT_Comments    → SourceTypes.comments
Spectrum Instrument → Spectra.instrument
Spectrum Observers  → Spectra.comments
TAGS            → SourceTypes.source_type
Spt_unc         → SourceTypes.comments
BΣ_YMGs        → Associations.association
Comment         → Sources.comments
extra2          → Sources.comments
Flags           → Sources.comments
Notes           → Sources.comments
```

---

### Coverage Summary

| Table | Expected Rows | Estimated Ingestible |
|---|---|---|
| Sources | 258 | 249 (9 missing Disc/reference) |
| Names | ~774 (3 names × 258) | ~747 (skip 9 objects × 3) |
| Photometry (W1/W2) | 249 each | 249 |
| Photometry (J/H/K/Y) | 248/214/~240/~120 | varies by NIR ref |
| Photometry (i/z/y) | ~1 | 1 (optical data absent) |
| Parallaxes | 86 | 86 |
| ProperMotions | 249 | 249 |
| SourceTypes (FINAL) | 258 | 248 (10 lack Spec reference) |
| SourceTypes (TAGS) | ~258 | ~258 |
| ModeledParameters (Dist_J) | 243 | 243 |
| ModeledParameters (Dist_W2) | 248 | 248 |
| ModeledParameters (BΣ_distance) | 62 | 62 |
| ModeledParameters (Vtan/PMTot) | 249 | 249 |
| Spectra | 248 | 248 |
| Associations (BΣ_YMGs) | ~62 × avg_ymgs | ~62 |

---

### Summary

- **15 nullable violations** found — all mitigated by row-skipping in the ingestion script, except the 9 objects with null `Disc` (Sources.reference), which require their discovery references before they can be ingested.
- **4 type mismatches** found — all require explicit transforms (string parsing, int→float cast, date conversion).
- **36 columns** passed validation cleanly.

**Resolution for null Disc**: The 9 objects with null `Disc` will use `EastonH` as their `Sources.reference` (user-confirmed 2026-06-15).
Objects affected: `0011-0521B`, `0020-1535`, `0146-0508B`, `0643+1950A`, `0809+7417B`, `0904+6106`, `1810-0657A`, `1810-0657B`, `2053+3319B`

**Next steps:**

1. **For nullable violations**: Add null-filter guard at the start of each ingestion loop:
   ```python
   if pd.isna(row["Disc"]) or row["Disc"] == "": continue  # Sources
   if pd.isna(row["plx"]) or row["plx"] == "": continue  # Parallaxes
   # etc.
   ```
2. **For type mismatches**: Add explicit cast steps in ingestion scripts:
   ```python
   dist_j = float(row["Dist_J"].replace(" pc", ""))  # strip " pc"
   obs_date = f"20{int(row['Spectrum Date']):06d}"[:4] + "-" + ...  # YYMMDD→ISO
   ```
3. **For opt ref (optical photometry)**: De-prioritize i/z/y photometry ingestion — data is present for only 1/258 objects. The primary photometry will be WISE W1/W2 and NIR Y/J/H/K.
4. **Next skill**: Run `astrodb-generate-schema` to update `schema.yaml` name and validate with felis.
