import pyodbc

def get_sql_health():
    """Retrieves basic SQL Server version and top wait types."""
    conn_str = (
        "Driver={ODBC Driver 17 for SQL Server};" # Ensure this driver is installed
        "Server=localhost;" 
        "Database=master;"
        "Trusted_Connection=yes;"
    )
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        # Get Version
        cursor.execute("SELECT @@VERSION")
        version = cursor.fetchone()[0]
        return f"Connected to: {version[:50]}..."
    except Exception as e:
        return f"Connection failed: {e}"