import os
import pyodbc
from typing import List, Tuple, Optional

# configuration can come from environment variables or a .env file
_DRIVER = os.getenv("SQL_DRIVER", "ODBC Driver 17 for SQL Server")
_SERVER = os.getenv("SQL_SERVER", "LAPTOP-CVGF86FI\\JSO")
_DATABASE = os.getenv("SQL_DATABASE", "master")
_TRUSTED = os.getenv("SQL_TRUSTED", "yes")


def _get_conn() -> pyodbc.Connection:
    """Return a new connection object using the current configuration."""
    conn_str = (
        f"Driver={{{_DRIVER}}};"
        f"Server={_SERVER};"
        f"Database={_DATABASE};"
        f"Trusted_Connection={_TRUSTED};"
    )
    return pyodbc.connect(conn_str)


def get_sql_health() -> List[Tuple]:
    """Return every row from sys.configurations (instance-level settings).

    The caller can decide how to format or display the results.  If the
    connection fails an exception message is returned as a single-element
    tuple so the caller can still see what went wrong.
    """
    try:
        with _get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("select [configuration_id] \
                , CAST([name] AS varchar(256)) [name]  \
                , CAST([value] AS INT) [value] \
                , CAST([minimum] AS INT) AS [minimum] \
                , CAST([value_in_use] AS INT) AS [value_in_use] \
                , CAST([description] AS varchar(256)) [description] \
                , [is_dynamic] \
                , [is_advanced] \
                from sys.configurations")
            return cursor.fetchall()
    except Exception as e:
        return [(f"Connection failed: {e}",)]


def run_query(sql: str, params: Optional[Tuple] = None) -> List[Tuple]:
    """Execute a read-only query and return the result rows."""
    with _get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, params or ())
        return cursor.fetchall()


def execute_sql(sql: str, params: Optional[Tuple] = None) -> None:
    """Run a statement that modifies data/schema and commit the change."""
    with _get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, params or ())
        conn.commit()


if __name__ == "__main__":
    print(get_sql_health())