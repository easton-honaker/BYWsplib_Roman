"""
Tests for the Morphology table.
This table was not part of the astrodb-template-db schema.
As data is added, update n_entries to reflect the expected count.
"""


def test_morphology_table_exists(db):
    """Confirm Morphology was created in the database."""
    assert "Morphology" in db.metadata.tables.keys(), (
        "Morphology table not found — check that schema.yaml includes it"
    )


def test_morphology_count(db):
    """Fresh database should have 0 entries in Morphology."""
    n_entries = db.query(db.Morphology).count()
    assert n_entries == 0, (
        f"Found {n_entries} entries in Morphology, expected 0 (empty database)"
    )
