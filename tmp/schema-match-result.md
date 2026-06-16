# AstroDB Schema Match — BYWsplib_merged.csv
**Date:** 2026-06-15

| # | Input Column | Description | Units | Type | AstroDB Table | AstroDB Field | Confidence | Notes |
|---|---|---|---|---|---|---|---|---|
| 1 | shortname | Coordinate-based short identifier | — | str | Sources | source | High | Primary key; unique per object |
| 2 | Jname | J-band designation from Reconcile coords | — | str | Names | other_name | High | Alternate name from discovery coords |
| 3 | FINALNUM | Numerical spectral type (e.g. 27=T7) | — | float64 | SKIP | — | — | Redundant with FINAL; internal use only |
| 4 | FINAL | Final adopted spectral type string | — | str | SourceTypes | source_type | High | adopted=True; reference=Spec |
| 5 | Spt_unc | Spectral type uncertainty flag (int code) | — | int64 | SourceTypes | comments | Medium | Encode as "spt_unc=N" in SourceTypes comments |
| 6 | TAGS | Object category: d/sd/y/b | — | str | SourceTypes | source_type | Medium | Map d→"dwarf", sd→"subdwarf", y→"young", b→"binary"; add as separate SourceTypes rows |
| 7 | Code | Reconciliation code (filter already applied) | — | str | SKIP | — | — | Already filtered to non-skip |
| 8 | Comment | Free-form reconciliation comment | — | str | Sources | comments | Medium | Append to source comments if non-empty |
| 9 | USEVERSION | Spectral version flag | — | int64 | SKIP | — | — | Internal processing flag |
| 10 | USECOLOR | Color usage flag | — | int64 | SKIP | — | — | Internal processing flag |
| 11 | Keep/Skip/maintain | Disposition | — | str | SKIP | — | — | Filter already applied |
| 12 | extra1 | Auxiliary reconciliation flag | — | str | SKIP | — | — | Values: "r" (review) — internal |
| 13 | extra2 | Auxiliary reconciliation notes | — | str | Sources | comments | Low | Append to comments if non-empty; contains useful binary/co-mover notes |
| 14 | Disc | Discovery reference shortname | — | str | Sources | reference | High | FK→Publications; 31 unique refs |
| 15 | Spec | Spectroscopy reference shortname | — | str | SourceTypes | reference | High | FK→Publications; also Sources.other_references; 14 unique refs |
| 16 | ID | Internal catalog integer ID | — | float64 | SKIP | — | — | Internal ID not needed in DB |
| 17 | Priority | Processing priority flag | — | str | SKIP | — | — | Internal flag (A/B/C/D/DONE) |
| 18 | Type | Photometric SpT estimate (parenthetical) | — | str | SKIP | — | — | Less precise than FINAL; redundant |
| 19 | Dist_J | Distance from J-band photometry | pc | str→float64 | ModeledParameters | value | High | parameter="distance_J"; parse numeric from "32.9 pc" string; ref=Disc |
| 20 | Dist_W2 | Distance from W2-band photometry | pc | str→float64 | ModeledParameters | value | High | parameter="distance_W2"; parse numeric from "34.8 pc" string; ref=Disc |
| 21 | RA SXG | Right ascension (sexagesimal) | — | str | SKIP | — | — | Redundant with catWISE RA |
| 22 | DE SXG | Declination (sexagesimal) | — | str | SKIP | — | — | Redundant with catWISE Dec |
| 23 | Jdesignation | catWISE-coordinate J-designation | — | str | Names | other_name | High | Alternate name from catWISE coords |
| 24 | catWISE RA | Right ascension from catWISE (decimal deg) | deg | float64 | Sources | ra_deg | High | Primary coordinate column |
| 25 | catWISE Dec | Declination from catWISE (decimal deg) | deg | float64 | Sources | dec_deg | High | Primary coordinate column |
| 26 | i | i-band magnitude (PS1 DR2) | mag | float64 | Photometry | magnitude | High | band=PAN-STARRS/PS1.i; ref=opt ref; regime=optical; cast from int64 |
| 27 | ei | Uncertainty on i | mag | float64 | Photometry | magnitude_error | High | Paired with i |
| 28 | z | z-band magnitude (PS1 DR2) | mag | float64 | Photometry | magnitude | High | band=PAN-STARRS/PS1.z; ref=opt ref; regime=optical |
| 29 | ez | Uncertainty on z | mag | float64 | Photometry | magnitude_error | High | Paired with z |
| 30 | y | y-band magnitude (PS1 DR2) | mag | float64 | Photometry | magnitude | High | band=PAN-STARRS/PS1.y; ref=opt ref; regime=optical |
| 31 | ey | Uncertainty on y | mag | float64 | Photometry | magnitude_error | High | Paired with y |
| 32 | opt ref | Optical photometry reference | — | str | Photometry | reference | High | Always "PS1 DR2"; shared ref for i, z, y; FK→Publications |
| 33 | W1 | WISE W1 magnitude (3.4 µm) | mag | float64 | Photometry | magnitude | High | band=WISE/WISE.W1; ref=NIR ref; regime=mir |
| 34 | eW1 | Uncertainty on W1 | mag | float64 | Photometry | magnitude_error | High | Paired with W1 |
| 35 | W2 | WISE W2 magnitude (4.6 µm) | mag | float64 | Photometry | magnitude | High | band=WISE/WISE.W2; ref=NIR ref; regime=mir |
| 36 | eW2 | Uncertainty on W2 | mag | float64 | Photometry | magnitude_error | High | Paired with W2 |
| 37 | Y | Y-band magnitude (NIR) | mag | float64 | Photometry | magnitude | High | band depends on NIR ref (VHS→Paranal/VIRCAM.Y, VIKING→same) ⚠ |
| 38 | eY | Uncertainty on Y | mag | float64 | Photometry | magnitude_error | High | Paired with Y |
| 39 | J | J-band magnitude (NIR) | mag | float64 | Photometry | magnitude | High | band depends on NIR ref (VHS→Paranal/VIRCAM.J, UHS→UKIRT/WFCAM.J, 2MASS→2MASS/2MASS.J) ⚠ |
| 40 | eJ | Uncertainty on J | mag | float64 | Photometry | magnitude_error | High | Paired with J |
| 41 | H | H-band magnitude (NIR) | mag | float64 | Photometry | magnitude | High | band depends on NIR ref (VHS→Paranal/VIRCAM.H, 2MASS→2MASS/2MASS.H) ⚠ |
| 42 | eH | Uncertainty on H | mag | float64 | Photometry | magnitude_error | High | Paired with H |
| 43 | K | K-band magnitude (NIR) | mag | float64 | Photometry | magnitude | High | band depends on NIR ref (VHS→Paranal/VIRCAM.Ks, UHS→UKIRT/WFCAM.K, 2MASS→2MASS/2MASS.Ks) ⚠ |
| 44 | eK | Uncertainty on K | mag | float64 | Photometry | magnitude_error | High | Paired with K |
| 45 | NIR ref | NIR photometry reference string | — | str | Photometry | reference | Medium | Per-band ref encoded in string (e.g. "UHS DR3, 2MASS (H)"); must be parsed per-band at ingest ⚠ |
| 46 | plx | Parallax measurement | mas | float64 | Parallaxes | parallax_mas | High | |
| 47 | eplx | Uncertainty on parallax | mas | float64 | Parallaxes | parallax_error | High | |
| 48 | plx_ref | Parallax reference | — | str | Parallaxes | reference | High | Values: GaiaDR3, Best20, Kirk21; FK→Publications |
| 49 | PMRA | Proper motion in RA*cos(Dec) | mas/yr | float64 | ProperMotions | pm_ra | High | |
| 50 | ePMRA | Uncertainty on PMRA | mas/yr | float64 | ProperMotions | pm_ra_error | High | |
| 51 | PMDE | Proper motion in Dec | mas/yr | float64 | ProperMotions | pm_dec | High | |
| 52 | ePMDE | Uncertainty on PMDE | mas/yr | float64 | ProperMotions | pm_dec_error | High | |
| 53 | PM_ref | Proper motion reference | — | str | ProperMotions | reference | High | 21 unique values; FK→Publications |
| 54 | PMTot | Total proper motion magnitude | mas/yr | float64 | ModeledParameters | value | Medium | parameter="pm_total"; derived from PMRA+PMDE |
| 55 | Vtan | Tangential velocity | km/s | float64 | ModeledParameters | value | High | parameter="v_tan"; unit="km/s" |
| 56 | Phototype | Photometric SpT (numerical, Goodstuff) | — | float64 | SKIP | — | — | Redundant with FINALNUM/FINAL |
| 57 | Spectral Type | Spectral type from spectrum (Goodstuff) | — | str | SourceTypes | source_type | High | adopted=False (FINAL is adopted); reference=Spec |
| 58 | SpT_Comments | Notes on spectral type determination | — | str | SourceTypes | comments | High | Append to the SourceTypes row for FINAL |
| 59 | Spectrum Date | Observation date (YYMMDD float) | — | float64 | Spectra | observation_date | Medium | Convert YYMMDD→ISO date string (e.g. 230629→2023-06-29) |
| 60 | Spectrum Instrument | Spectroscopy instrument name | — | str | Spectra | instrument | High | FK→Instruments; 7 unique instruments |
| 61 | Spectrum Observers | Observer names string | — | str | Spectra | comments | Medium | No direct Spectra field; store as "observers: <value>" in comments |
| 62 | Submitted Name | Name submitted by discoverer | — | str | Names | other_name | High | Alternate name |
| 63 | SIMBAD | SIMBAD link label | — | str | SKIP | — | — | URL label, not data |
| 64 | Vizier | VizieR link label | — | str | SKIP | — | — | URL label, not data |
| 65 | IRSA_Finder | IRSA finder chart label | — | str | SKIP | — | — | URL label, not data |
| 66 | GSA | GSA link label | — | str | SKIP | — | — | URL label, not data |
| 67 | wiseview | WISEView link label | — | str | SKIP | — | — | URL label, not data |
| 68 | BΣ_distance_Checkup | Bayesian distance check flag | — | str | SKIP | — | — | Quality flag |
| 69 | BΣ_distance | Bayesian sigma distance estimate | pc | float64 | ModeledParameters | value | Medium | parameter="bayes_distance"; unit="pc" |
| 70 | BΣ_PROB | Bayesian distance probability | — | float64 | ModeledParameters | value | Medium | parameter="bayes_distance_prob"; unit="dimensionless" |
| 71 | BΣ_YMGs | YMG membership with probabilities | — | str | Associations | association | Medium | Format: "ABDMG(88);OCTN(11)" — parse to separate rows with membership_probability |
| 72 | BΣ_Hyp | Bayesian hypothesis string | — | str | SKIP | — | — | Internal flag |
| 73 | Date Added | Date added to catalog (YYMMDD) | — | float64 | SKIP | — | — | Catalog metadata |
| 74 | NumType | Numerical SpT from Goodstuff | — | float64 | SKIP | — | — | Redundant with FINALNUM |
| 75 | In BASS UltraCool | BASS UltraCool catalog membership | — | str | SKIP | — | — | Catalog flag |
| 76 | Flags | Special processing flags | — | str | Sources | comments | Low | Append "flags: <value>" to comments if non-empty (e.g. "COMOVER") |
| 77 | Notes | Free-form notes | — | str | Sources | comments | Low | Append to source comments if non-empty |

## Summary

- **High confidence:** 50 columns
- **Medium confidence:** 11 columns
- **Low confidence:** 3 columns
- **SKIP (not ingested):** 26 columns (flags, internal IDs, URL labels, redundant columns)
- **Unmatched (need decision):** 0 — all columns resolved

## Key ingestion complexities

1. **NIR band SVO IDs are per-source**: The `NIR ref` column encodes a complex string (e.g. "UHS DR3, 2MASS (H)") indicating which survey provided each band. Ingestion script must parse this per row and per band to determine the correct SVO filter ID.
2. **BΣ_YMGs** contains semicolon-separated associations with probabilities in parentheses — must be split into one Associations row per moving group per source.
3. **Spectral type duplication**: Both `FINAL` (adopted) and `Spectral Type` (from Goodstuff) map to SourceTypes. Ingest FINAL as adopted=True; skip Spectral Type if it duplicates FINAL.
4. **Spectrum Date** is stored as YYMMDD float — convert to ISO format (e.g. 230629 → 2023-06-29).
5. **Dist_J / Dist_W2** stored as strings ("32.9 pc") — strip " pc" and convert to float.
