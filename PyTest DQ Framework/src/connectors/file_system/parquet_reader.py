import os
import pandas as pd

class ParquetReader:
    """
    A class to handle reading data from Parquet files.
    """

    def __init__(self):
        pass

    def process(self, target_path, include_subfolders=False):
        """
        Reads Parquet files from the specified path.

        target_path : path to the directory containing Parquet files.

        Returns:
        --------
        DataFrame
            Concatenated DataFrame of all Parquet files found.
        """
        parquet_files = []
        for root, dirs, files in os.walk(target_path):
                for file in files:
                    if file.endswith('.parquet'):
                        parquet_files.append(os.path.join(root, file))

        # Read and concatenate all Parquet files
        dataframes = []
        for f in parquet_files: 
            df = pd.read_parquet(f)
            dataframes.append(df)
        combined_df = pd.concat(dataframes, ignore_index=True)
        return combined_df