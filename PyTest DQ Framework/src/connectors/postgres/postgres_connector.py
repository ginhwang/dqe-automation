from typing import Optional
import psycopg2
from psycopg2.extensions import connection
import pandas as pd
from pandas import DataFrame

class PostgresConnectorContextManager:
    """
    PostgreSQL Database Context Manager.

    This class provides a convenient way to manage PostgreSQL database connections
    using a context manager. It handles connection setup and teardown, and provides
    utility methods for interacting with the database.
    """

    def __init__(self, db_user: str, db_password: str, db_host: str, db_name: str, db_port: int, autocommit: bool = False):
        """
        Initialize the database context manager.

        Args:
            db_user (str): Username for authentication.
            db_password (str): Password for authentication.
            db_host (str): Hostname of the PostgreSQL server.
            db_name (str): Name of the database to connect to.
            db_port (int): Port number of the PostgreSQL server.
            autocommit (bool): Enable or disable autocommit mode for the connection.
        """
        self.user = db_user
        self.password = db_password
        self.host = db_host
        self.db = db_name
        self.port = db_port
        self.autocommit = autocommit
        self.connection: Optional[connection] = None

    def __enter__(self):
        self.connection = psycopg2.connect(
            host=self.host,
            port=self.port,
            database=self.db,
            user=self.user,
            password=self.password
        )
        self.connection.autocommit = self.autocommit
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        if self.connection:
            self.connection.close()

    def get_connection(self) -> Optional[connection]:
        return self.connection

    def get_data_sql(self, query: str) -> DataFrame:
        try:
            data_df = pd.read_sql(query, self.connection)
            return data_df
        except Exception as e:
            print(f'Failed to receive data from DB\nError: {e}\n')
            raise