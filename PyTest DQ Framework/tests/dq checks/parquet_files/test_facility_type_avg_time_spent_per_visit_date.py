"""
Description: Data Quality checks for facility_type_avg_time_spent_per_visit_date
Requirement(s): TICKET-1235
Author(s): Regina Khvan
"""

import pytest
import pandas as pd


@pytest.fixture(scope='module')
def source_data(db_connection):
    source_query = """
            SELECT
                f.facility_type,
                v.visit_timestamp::date AS visit_date,
                ROUND(AVG(v.duration_minutes), 2) AS avg_time_spent
            FROM
                visits v
            JOIN
                facilities f 
                ON f.id = v.facility_id
            WHERE
                v.visit_timestamp > '2000-11-01' -- misstake
                AND f.facility_type IN ('Hospital', 'Clinic', 'Specialty Center') -- misstake
            GROUP BY
                f.facility_type,
                visit_date;
            """
    source_data = db_connection.get_data_sql(source_query)
    return source_data


@pytest.fixture(scope='module')
def target_data(parquet_reader):
    target_path = '/parquet_data/facility_type_avg_time_spent_per_visit_date'
    target_data = parquet_reader.process(target_path, include_subfolders=True)
    return target_data


@pytest.mark.parquet_data
@pytest.mark.smoke
@pytest.mark.facility_type_avg_time_spent_per_visit_date
def test_check_dataset_is_not_empty(target_data, data_quality_library):
    """Smoke test: Ensure the target dataset is not empty."""
    data_quality_library.check_dataset_is_not_empty(target_data)



@pytest.mark.parquet_data
@pytest.mark.facility_type_avg_time_spent_per_visit_date
def test_check_count(source_data, target_data, data_quality_library):
    """Completeness: Ensure row counts match between source and target."""
    data_quality_library.check_count(source_data, target_data)

@pytest.mark.parquet_data
@pytest.mark.facility_type_avg_time_spent_per_visit_date
def test_check_data_completeness(source_data, target_data, data_quality_library):
    """Completeness: Ensure all source records are present in the target."""
    # You may want to use a more advanced comparison depending on your needs
    data_quality_library.check_data_full_data_set(source_data, target_data)



@pytest.mark.parquet_data
@pytest.mark.facility_type_avg_time_spent_per_visit_date
def test_check_uniqueness(target_data, data_quality_library):
    """Quality: Ensure no duplicate records exist in the target."""
    data_quality_library.check_duplicates(target_data, ['facility_type', 'visit_date'])

@pytest.mark.parquet_data
@pytest.mark.facility_type_avg_time_spent_per_visit_date
def test_check_not_null_values(target_data
, data_quality_library):
    """Quality: Ensure key columns do not contain null values."""
    data_quality_library.check_not_null_values(target_data, ['facility_type', 'visit_date', 'avg_time_spent'])

@pytest.mark.parquet_data
@pytest.mark.facility_type_avg_time_spent_per_visit_date
def test_check_visit_date_format(target_data):
    if pd.api.types.is_datetime64_any_dtype(target_data['visit_date']):
        visit_date_str = target_data['visit_date'].dt.strftime('%Y-%m')
    else:
        visit_date_str = target_data['visit_date'].astype(str)
    assert visit_date_str.str.match(r'^\d{4}-\d{2}$').all(), "visit_date should be in YYYY-MM format"

@pytest.mark.parquet_data
@pytest.mark.facility_type_avg_time_spent_per_visit_date
def test_check_avg_time_spent_rounding(target_data):
    assert (target_data['avg_time_spent'].apply(lambda x: round(x, 2)) == target_data['avg_time_spent']).all(), "avg_time_spent not rounded to two decimals"
