"""
Description: Data Quality checks for facility_name_min_time_spent_per_visit_date
Requirement(s): TICKET-1234
Author(s): Regina Khvan
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
@pytest.mark.smoke
@pytest.mark.facility_name_min_time_spent_per_visit_date
def test_check_dataset_is_not_empty(target_data, data_quality_library):
    """Smoke test: Ensure the target dataset is not empty."""
    data_quality_library.check_dataset_is_not_empty(target_data)



@pytest.mark.parquet_data
@pytest.mark.facility_name_min_time_spent_per_visit_date
def test_check_count(source_data, target_data, data_quality_library):
    """Completeness: Ensure row counts match between source and target."""
    data_quality_library.check_count(source_data, target_data)

@pytest.mark.parquet_data
@pytest.mark.facility_name_min_time_spent_per_visit_date
def test_check_data_completeness(source_data, target_data, data_quality_library):
    """Completeness: Ensure all source records are present in the target."""
    # You may want to use a more advanced comparison depending on your needs
    data_quality_library.check_data_full_data_set(source_data, target_data)



@pytest.mark.parquet_data
@pytest.mark.facility_name_min_time_spent_per_visit_date
def test_check_uniqueness(target_data, data_quality_library):
    """Quality: Ensure no duplicate records exist in the target."""
    data_quality_library.check_duplicates(target_data, ['facility_name', 'visit_date'])

@pytest.mark.parquet_data
@pytest.mark.facility_name_min_time_spent_per_visit_date
def test_check_not_null_values(target_data
, data_quality_library):
    """Quality: Ensure key columns do not contain null values."""
    data_quality_library.check_not_null_values(target_data, ['facility_name', 'visit_date', 'min_time_spent'])

@pytest.mark.parquet_data
@pytest.mark.facility_name_min_time_spent_per_visit_date
def test_check_visit_date_format(target_data):
    """Quality: Ensure visit_date is in YYYY-MM format (partitioned by year-month)."""
    assert target_data['visit_date'].str.match(r'^\d{4}-\d{2}$').all(), "visit_date should be in YYYY-MM format"