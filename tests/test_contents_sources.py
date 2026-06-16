"""
Tests for the Sources table.
As data is added, update n_sources to reflect the actual expected count.
"""
from sqlalchemy import or_


def test_sources(db):
    n_sources = db.query(db.Sources).count()
    assert n_sources == 249, f"Found {n_sources} sources, expected 249"


def test_coordinates(db):
    """Verify all sources have valid RA/Dec coordinates."""
    t = (
        db.query(db.Sources.c.source, db.Sources.c.ra_deg, db.Sources.c.dec_deg)
        .filter(
            or_(
                db.Sources.c.ra_deg.is_(None),
                db.Sources.c.ra_deg < 0,
                db.Sources.c.ra_deg > 360,
                db.Sources.c.dec_deg.is_(None),
                db.Sources.c.dec_deg < -90,
                db.Sources.c.dec_deg > 90,
            )
        )
        .astropy()
    )
    assert len(t) == 0, f"{len(t)} Sources failed coordinate checks: {t}"
