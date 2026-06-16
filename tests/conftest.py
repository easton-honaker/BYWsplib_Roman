import os
import pytest
import logging

import astrodb_utils
from astrodb_utils import build_db_from_json

logger = logging.getLogger(__name__)


@pytest.fixture(scope="session", autouse=True)
def db():
    logger.info(f"Using version {astrodb_utils.__version__} of astrodb_utils")

    db = build_db_from_json()

    assert os.path.exists(
        "BYW_Roman.sqlite"
    ), "Database file 'BYW_Roman.sqlite' was not created."

    logger.info(
        "Loaded BYW_Roman database using build_db_from_json function in conftest.py"
    )

    return db
