"""
Tests that the database ORM works as expected.
These tests add and remove rows to verify basic database operations —
they should not need modification as data is added to the database.
"""
from sqlalchemy.ext.automap import automap_base


def test_orm_use(db):
    """Verify adding and removing a source via the ORM works correctly."""
    Base = automap_base(metadata=db.metadata)
    Base.prepare()

    Publications = Base.classes.Publications
    Sources = Base.classes.Sources
    Names = Base.classes.Names

    pub = Publications(reference="TestRef")
    s = Sources(source="Test ORM Source", reference="TestRef")
    n = Names(source="Test ORM Source", other_name="Test Alias")

    with db.session as session:
        session.add(pub)
        session.add(s)
        session.add(n)
        session.commit()

    assert db.query(db.Sources).filter(db.Sources.c.source == "Test ORM Source").count() == 1
    assert db.query(db.Names).filter(db.Names.c.other_name == "Test Alias").count() == 1

    with db.session as session:
        session.delete(n)
        session.delete(s)
        session.delete(pub)
        session.commit()

    assert db.query(db.Sources).filter(db.Sources.c.source == "Test ORM Source").count() == 0
