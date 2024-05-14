# conftest.py
import os

import pytest

from config import set_logger


@pytest.fixture(scope="session", autouse=True)
def setup_session():
    # Code to run before any debug starts
    set_logger(_id='45KmQwtF5qecbixQNe')
    yield
    # Code to run after all tests are done
    print("Session teardown")
