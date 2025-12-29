*** Settings ***
Library    BuiltIn
Library    Collections
Library    SeleniumLibrary
Library    DatabaseLibrary
Library    helper.py

Suite Setup       Open Report In Chrome
Suite Teardown    Close Browser

*** Variables ***
${REPORT_FILE}      C:/Users/Regina_Khvan/Desktop/dq_auto/dqe-automation/Robot Framework/report.html
${PARQUET_FOLDER}   C:/Users/Regina_Khvan/Desktop/dq_auto/dqe-automation/Robot Framework/parquet_data/facility_type_avg_time_spent_per_visit_date
${FILTER_DATE}      2025-11
${CSV_FILE}         C:/Users/Regina_Khvan/Desktop/dq_auto/dqe-automation/Robot Framework/table.csv

*** Test Cases ***
Compare HTML Table With Parquet Dataset
    [Documentation]    Extract SVG table, read parquet, compare.
    Extract SVG Table To Csv    ${REPORT_FILE}    ${CSV_FILE}
    ${df_html}=    Read Csv As Dataframe    ${CSV_FILE}
    ${df_parquet}=    Read Parquet Dataset    ${PARQUET_FOLDER}    ${FILTER_DATE}
    ${result}    ${diff}=    Compare Dataframes    ${df_html}    ${df_parquet}
    Run Keyword If    not ${result}    Fail    DataFrames do not match. Differences: ${diff}

*** Keywords ***
Open Report In Chrome
    Open Browser    file://${REPORT_FILE}    chrome
    Maximize Browser Window

Read Csv As Dataframe
    [Arguments]    ${csv_file}
    ${df}=    Evaluate    __import__('pandas').read_csv(r'''${csv_file}''')
    RETURN    ${df}