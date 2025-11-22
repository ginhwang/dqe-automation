"""
Description: Data Quality checks for facility_name_min_time_spent_per_visit_date
Requirement(s): TICKET-1234
Author(s): Name Surname
"""

import pytest


@pytest.fixture(scope='module')
def source_data(db_connection):
    source_query = """
    SELECT
    f.facility_name,
    v.visit_timestamp::date AS visit_date,
    MIN(v.duration_minutes) AS min_time_spent
FROM
    visits v
JOIN facilities f 
    ON f.id = v.facility_id
GROUP BY
    f.facility_name,
    visit_date
UNION ALL  -- misstake
SELECT
    f.facility_name,
    v.visit_timestamp::date AS visit_date,
    MIN(v.duration_minutes) AS min_time_spent
FROM
    visits v
JOIN facilities f 
    ON f.id = v.facility_id
WHERE
    f.facility_type = 'Clinic' 
GROUP BY
    f.facility_name,
    visit_date;
    """
    source_data = db_connection.get_data_sql(source_query)
    return source_data


@pytest.fixture(scope='module')
def target_data(parquet_reader):
    target_path = '/parquet_data/facility_name_min_time_spent_per_visit_date'
    target_data = parquet_reader.process(target_path, include_subfolders=True)
    return target_data


@pytest.mark.parquet_data
def test_check_dataset_is_not_empty(target_data, data_quality_library):
    data_quality_library.check_dataset_is_not_empty(target_data)


@pytest.mark.parquet_data
def test_check_count(source_data, target_data, data_quality_library):
    data_quality_library.check_count(source_data, target_data)
