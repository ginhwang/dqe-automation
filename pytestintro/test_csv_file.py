import pytest
import re


def test_file_not_empty(extract_csv):
    df = extract_csv
    df_count = df.count()
    assert  len(df) > 0, "The file has no data"

@pytest.mark.validate_csv
@pytest.mark.xfail
def test_duplicates(extract_csv):
    df = extract_csv
    assert not df.duplicated().any(), f"Duplicates are present. Rows: {df[df.duplicated()]}"

@pytest.mark.validate_csv
def test_validate_schema(extract_csv, validate_csv_schema):
    df = extract_csv
    expected_schema = ['id', 'name', 'age', 'email']
    result = validate_csv_schema(df, expected_schema)
    assert result

@pytest.mark.validate_csv
@pytest.mark.skip
def test_age_column_valid(extract_csv):
    df = extract_csv
    assert df['age'].between(0,100, inclusive='both').all(), "Some ages are outside the valid range of 0-100."

@pytest.mark.validate_csv
def test_email_column_valid(extract_csv):
    df = extract_csv
    email_pattern = r".+@.+\..+"
    invalid_emails = df[~df['email'].astype(str).str.match(email_pattern)]['email']
    assert invalid_emails.empty, f"Invalid email addresses: {invalid_emails.tolist()}"
    
@pytest.mark.parametrize("id, is_active", [(1, False), (2, True)])
def test_active_players(extract_csv, id, is_active):
    df = extract_csv
    row = df[df['id'] == id]
    row_is_active = row.iloc[0]['is_active']
    assert row_is_active == is_active, f"The is_active flag for id {id} is {row_is_active}. Expected value: {is_active}"


def test_active_player(extract_csv):
    df = extract_csv
    row = df[df['id'] == 2]
    row_is_active = row.iloc[0]['is_active']
    assert row_is_active is True, "The is_active flag is incorrect for id=2."
