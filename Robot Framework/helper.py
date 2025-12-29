import pandas as pd
import pyarrow.parquet as pq
from robot.api.deco import keyword
from selenium.webdriver.common.by import By
from robot.libraries.BuiltIn import BuiltIn
from selenium.webdriver.common.by import By

@keyword
def read_html_table(table_html):
    dfs = pd.read_html(table_html)
    return dfs

@keyword
def read_parquet_dataset(folder_path, filter_date=None, date_column='partition_date'):
    df = pd.read_parquet(folder_path)
    print(f"Total rows in file before filtering: {len(df)}")
    print(f'Example unfiltered df:{df.head(5)}')
    if filter_date:
        if date_column not in df.columns:
            raise KeyError(f"Column '{date_column}' not found in Parquet file. Available columns: {list(df.columns)}")
        df = df[df[date_column] == filter_date]
    print(f'Example filtered df:{df.head(5)}')
    return df

def standardize_columns(df):
    return {col: col.strip().lower().replace(" ", "_") for col in df.columns}

@keyword
def compare_dataframes(df1, df2):
    try:
        df1 = df1.rename(columns=standardize_columns(df1))
        df2 = df2.rename(columns=standardize_columns(df2))
        if 'visit_date' in df1.columns:
            df1['visit_date'] = df1['visit_date'].astype(str)
        if 'visit_date' in df2.columns:
            df2['visit_date'] = df2['visit_date'].astype(str)
        common_cols = list(set(df1.columns) & set(df2.columns))
        if not common_cols:
            raise ValueError("No common columns to compare on after standardizing column names.")
        df1 = df1[common_cols]
        df2 = df2[common_cols]
        pd.testing.assert_frame_equal(df1.sort_index(axis=1), df2.sort_index(axis=1), check_like=True)
        return True, None
    except AssertionError as e:
        diff = {
            "df1_not_in_df2": df1.merge(df2, indicator=True, how='outer').loc[lambda x: x['_merge'] == 'left_only'],
            "df2_not_in_df1": df2.merge(df1, indicator=True, how='outer').loc[lambda x: x['_merge'] == 'left_only'],
        }
        return False, diff

@keyword   
def extract_svg_table_to_csv(file_path, output_csv):
    # Get the SeleniumLibrary driver instance
    seleniumlib = BuiltIn().get_library_instance("SeleniumLibrary")
    driver = seleniumlib.driver

    driver.get(f"file:///{file_path}")
    driver.implicitly_wait(10)

    columns = driver.find_elements(By.CSS_SELECTOR, 'g.column-block[id^="cells"]')
    if not columns:
        print("Could not find columns")
        return
    else:
        print(f"Found {len(columns)} columns")

    # extract text for columns
    col_data = []
    for idx, col in enumerate(columns):
        texts = col.find_elements(By.XPATH, './/*[local-name()="text" and contains(@class, "cell-text")]')
        column_values = [t.text for t in texts]
        col_data.append(column_values)

    print(f"col_data (all columns): {col_data}")

    # find headers
    header_names = []
    header_blocks = driver.find_elements(By.TAG_NAME, 'g')
    for block in header_blocks:
        if block.get_attribute('id') == 'header':
            headers = block.find_elements(By.TAG_NAME, 'text')
            for h in headers:
                if 'cell-text' in h.get_attribute('class'):
                    header_names.append(h.text)
    print(f"Headers: {header_names}")

    n_fields = len(header_names)
    if len(col_data) % n_fields != 0:
        print("Column count does not match header count, cannot proceed.")
        return

    cols_per_field = len(col_data) // n_fields
    grouped_cols = []
    for i in range(n_fields):
        combined = []
        for j in range(cols_per_field):
            combined.extend(col_data[i * cols_per_field + j])
        grouped_cols.append(combined)

    min_len = min(len(col) for col in grouped_cols)
    if min_len == 0:
        print("One of the columns is empty, cannot proceed.")
        return

    truncated_cols = [col[:min_len] for col in grouped_cols]
    rows = list(zip(*truncated_cols))
    df = pd.DataFrame(rows, columns=header_names)
    df.to_csv(output_csv, index=False)
    return output_csv
