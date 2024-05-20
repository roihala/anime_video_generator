# conftest.py
import os

import pytest

from config import logger


@pytest.fixture(scope="session", autouse=True)
def setup_session():
    # Code to run before any debug starts
    # logger.set_id(_id='45KmQwtF5qecbixQNe')
    # os.environ['DEBUG'] = 'True'
    yield
    # Code to run after all tests are done
    print("Session teardown")
