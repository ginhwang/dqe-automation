import pytest
import pandas as pd
import logging
import sys

import pytest

from reportportal_client import RPLogger

#Fixture for ReportPortal logging
@pytest.fixture(scope="session")
def rp_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logging.setLoggerClass(RPLogger)
    return logger

# Fixture to read the CSV file
@pytest.fixture(scope="session")
def extract_csv():
    path_to_file = "C:/Users/Regina_Khvan/Desktop/dq_auto/dqe-automation/PyTest Introduction/src/data/data.csv"
    try:
        df = pd.read_csv(path_to_file)
    except Exception as e: 
        raise("Unable to read CSV file: {e}")
    return df

# Fixture to validate the schema of the file
@pytest.fixture(scope="session")
def validate_csv_schema():
    def _validate(actual_schema, expected_schema):
        assert list(actual_schema.columns) == expected_schema, (
            f"Schema mismatch. Expected columns: {expected_schema}; Actual columns: {list(actual_schema.columns)}."
        )
    return _validate

# Pytest hook to mark unmarked tests with a custom mark
def pytest_collection_modifyitems(config, items):
    for item in items:
        if not any(item.iter_markers()):
            item.add_marker("unmarked")