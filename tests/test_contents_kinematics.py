"""
Test kinematic and astrometry tables.
As data is added, update the expected counts.
"""


def test_radial_velocities(db):
    t = db.query(db.RadialVelocities.c.rv_kms).astropy()
    n_radial_velocities = 0
    assert (
        len(t) == n_radial_velocities
    ), f"Found {len(t)} entries in RadialVelocities, expected {n_radial_velocities}"

def test_proper_motions(db):
    t = db.query(db.ProperMotions.c.pm_ra).astropy()
    n_proper_motions = 249
    assert (
        len(t) == n_proper_motions
    ), f"Found {len(t)} entries in ProperMotions, expected {n_proper_motions}"

def test_parallaxes(db):
    t = db.query(db.Parallaxes.c.parallax_mas).astropy()
    n_parallaxes = 86
    assert (
        len(t) == n_parallaxes
    ), f"Found {len(t)} entries in Parallaxes, expected {n_parallaxes}"
