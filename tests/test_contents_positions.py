"""
Tests for the Positions table.
This table was not part of the astrodb-template-db schema.
As data is added, update n_entries to reflect the expected count.
"""


def test_positions_table_exists(db):
    """Confirm Positions was created in the database."""
    assert "Positions" in db.metadata.tables.keys(), (
        "Positions table not found — check that schema.yaml includes it"
    )


def test_positions_count(db):
    """Fresh database should have 0 entries in Positions."""
    n_entries = db.query(db.Positions).count()
    assert n_entries == 0, (
        f"Found {n_entries} entries in Positions, expected 0 (empty database)"
    )
