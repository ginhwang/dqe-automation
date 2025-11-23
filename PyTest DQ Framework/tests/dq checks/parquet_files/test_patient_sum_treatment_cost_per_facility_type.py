"""
Description: Data Quality checks for patient_sum_treatment_cost_per_facility_type
Requirement(s): TICKET-1236
Author(s): Regina Khvan
"""

import pytest


@pytest.fixture(scope='module')
def source_data(db_connection):
    source_query = """
            SELECT
                f.facility_type,
                CASE
                    WHEN p.id <= 15 THEN 
                        NULL  -- misstake
                    ELSE
                        CONCAT(p.first_name, ' ', p.last_name)
                END AS full_name,
                CASE 
                    WHEN f.facility_type = 'Clinic' THEN 
                        -SUM(v.treatment_cost) -- misstake
                    ELSE 
                        SUM(v.treatment_cost)
                END AS sum_treatment_cost
            FROM
                visits v
            JOIN facilities f 
                ON f.id = v.facility_id
            JOIN patients p
                ON p.id = v.patient_id
            GROUP BY
                f.facility_type,
                full_name; 
            """
    source_data = db_connection.get_data_sql(source_query)
    return source_data


@pytest.fixture(scope='module')
def target_data(parquet_reader):
    target_path = '/parquet_data/patient_sum_treatment_cost_per_facility_type'
    target_data = parquet_reader.process(target_path, include_subfolders=True)
    return target_data


@pytest.mark.parquet_data
@pytest.mark.smoke
@pytest.mark.patient_sum_treatment_cost_per_facility_type
def test_check_dataset_is_not_empty(target_data, data_quality_library):
    """Smoke test: Ensure the target dataset is not empty."""
    data_quality_library.check_dataset_is_not_empty(target_data)



@pytest.mark.parquet_data
@pytest.mark.patient_sum_treatment_cost_per_facility_type
def test_check_count(source_data, target_data, data_quality_library):
    """Completeness: Ensure row counts match between source and target."""
    data_quality_library.check_count(source_data, target_data)

@pytest.mark.parquet_data
@pytest.mark.patient_sum_treatment_cost_per_facility_type
def test_check_data_completeness(source_data, target_data, data_quality_library):
    """Completeness: Ensure all source records are present in the target."""
    # You may want to use a more advanced comparison depending on your needs
    data_quality_library.check_data_full_data_set(source_data, target_data)



@pytest.mark.parquet_data
@pytest.mark.patient_sum_treatment_cost_per_facility_type
def test_check_uniqueness(target_data, data_quality_library):
    """Quality: Ensure no duplicate records exist in the target."""
    data_quality_library.check_duplicates(target_data, ['facility_type', 'full_name'])

@pytest.mark.parquet_data
@pytest.mark.patient_sum_treatment_cost_per_facility_type
def test_check_not_null_values(target_data
, data_quality_library):
    """Quality: Ensure key columns do not contain null values."""
    data_quality_library.check_not_null_values(target_data, ['facility_type', 'full_name', 'sum_treatment_cost'])

@pytest.mark.parquet_data
@pytest.mark.patient_sum_treatment_cost_per_facility_type
def test_check_full_name_format(target_data):
    assert target_data['full_name'].str.match(r'^[A-Za-z]+ [A-Za-z]+$').all(), "full_name format invalid"

@pytest.mark.parquet_data
@pytest.mark.patient_sum_treatment_cost_per_facility_type
def test_check_sum_treatment_cost_non_negative(target_data):
    assert (target_data['sum_treatment_cost'] >= 0).all(), "sum_treatment_cost has negative values"