import pandas as pd


class DataQualityLibrary:
    """
    A library of static methods for performing data quality checks on pandas DataFrames.

    This class is intended to be used in a PyTest-based testing framework to validate
    the quality of data in DataFrames. Each method performs a specific data quality
    check and uses assertions to ensure that the data meets the expected conditions.
    """

    @staticmethod
    def check_duplicates(df, column_names=None):
        if column_names:
            duplicates = df.duplicated(column_names)
        else:
            duplicates = df.duplicated()
        num_duplicates = duplicates.sum()
        assert num_duplicates == 0, f"There are {num_duplicates} duplicate rows in DataFrame."

    @staticmethod
    def check_count(df1, df2):
        assert df1.count == df2.count, f"Row count mismatch: {count1} != {count2}"

    @staticmethod
    def check_data_full_data_set(df1, df2):
        assert df1 == df2, "Datasets are not equal."

    @staticmethod
    def check_dataset_is_not_empty(df):
        assert not df.empty, "Dataset has no rows"

    @staticmethod
    def check_not_null_values(df, column_names=None):
        if column_names:
            columns_to_check = column_names 
        else:
           columns_to_check = df.columns
        for col in columns_to_check:
            num_nulls = df[col].isnull().sum()
            assert num_nulls == 0, f"Column '{col}' has {num_nulls} NULL values"

