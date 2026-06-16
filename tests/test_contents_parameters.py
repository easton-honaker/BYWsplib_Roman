"""
Tests for parameter tables.
As data is added, update the expected counts.
"""


def test_companion_parameters(db):
    t = db.query(db.CompanionParameters.c.source).astropy()
    n_companion_parameters = 0
    assert (
        len(t) == n_companion_parameters
    ), f"Found {len(t)} entries in CompanionParameters, expected {n_companion_parameters}"

def test_modeled_parameters(db):
    t = db.query(db.ModeledParameters.c.parameter).astropy()
    n_parameters = 611
    assert (
        len(t) == n_parameters
    ), f"Found {len(t)} entries in ModeledParameters, expected {n_parameters}"

def test_rotational_parameters(db):
    t = db.query(db.RotationalParameters.c.source).astropy()
    n_rotational_parameters = 0
    assert (
        len(t) == n_rotational_parameters
    ), f"Found {len(t)} entries in RotationalParameters, expected {n_rotational_parameters}"
