"""
Tests for overall database structure and cross-table sanity checks.
Update n_tables if you add or remove tables from the schema.
"""


def test_table_presence(db):
    """Confirm all expected tables are present."""
    assert len(db.metadata.tables.keys()) == 25, (
        f"Expected 25 tables, found {len(db.metadata.tables.keys())}: "
        f"{sorted(db.metadata.tables.keys())}"
    )
    assert "AssociationList" in db.metadata.tables.keys(), "AssociationList table missing"
    assert "Associations" in db.metadata.tables.keys(), "Associations table missing"
    assert "CompanionList" in db.metadata.tables.keys(), "CompanionList table missing"
    assert "CompanionParameters" in db.metadata.tables.keys(), "CompanionParameters table missing"
    assert "CompanionRelationships" in db.metadata.tables.keys(), "CompanionRelationships table missing"
    assert "Instruments" in db.metadata.tables.keys(), "Instruments table missing"
    assert "ModeledParameters" in db.metadata.tables.keys(), "ModeledParameters table missing"
    assert "Morphology" in db.metadata.tables.keys(), "Morphology table missing"
    assert "Names" in db.metadata.tables.keys(), "Names table missing"
    assert "Parallaxes" in db.metadata.tables.keys(), "Parallaxes table missing"
    assert "ParameterList" in db.metadata.tables.keys(), "ParameterList table missing"
    assert "Photometry" in db.metadata.tables.keys(), "Photometry table missing"
    assert "PhotometryFilters" in db.metadata.tables.keys(), "PhotometryFilters table missing"
    assert "Positions" in db.metadata.tables.keys(), "Positions table missing"
    assert "ProperMotions" in db.metadata.tables.keys(), "ProperMotions table missing"
    assert "Publications" in db.metadata.tables.keys(), "Publications table missing"
    assert "RadialVelocities" in db.metadata.tables.keys(), "RadialVelocities table missing"
    assert "RegimeList" in db.metadata.tables.keys(), "RegimeList table missing"
    assert "RotationalParameters" in db.metadata.tables.keys(), "RotationalParameters table missing"
    assert "SourceTypeList" in db.metadata.tables.keys(), "SourceTypeList table missing"
    assert "SourceTypes" in db.metadata.tables.keys(), "SourceTypes table missing"
    assert "Sources" in db.metadata.tables.keys(), "Sources table missing"
    assert "Spectra" in db.metadata.tables.keys(), "Spectra table missing"
    assert "Telescopes" in db.metadata.tables.keys(), "Telescopes table missing"
    assert "Versions" in db.metadata.tables.keys(), "Versions table missing"


def test_magnitudes(db):
    """Check that all photometry magnitudes are plausible."""
    from sqlalchemy import or_
    t = (
        db.query(db.Photometry.c.magnitude)
        .filter(
            or_(
                db.Photometry.c.magnitude.is_(None),
                db.Photometry.c.magnitude > 100,
                db.Photometry.c.magnitude < -1,
            )
        )
        .astropy()
    )
    assert len(t) == 0, f"{len(t)} Photometry rows failed magnitude checks"
