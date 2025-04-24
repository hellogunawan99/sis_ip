import os
from typing import List, Dict, Any
import pyodbc
from fastapi import FastAPI, HTTPException

app = FastAPI(title="Jigsaw Devices API")

# Build the SQL Server connection string from environment variables
def get_connection() -> pyodbc.Connection:
    driver   = os.getenv("MSSQL_DRIVER", "ODBC Driver 18 for SQL Server")
    server   = os.getenv("MSSQL_SERVER", "localhost,1433")
    database = os.getenv("MSSQL_DATABASE", "db")
    user     = os.getenv("MSSQL_USER", "user")
    password = os.getenv("MSSQL_PASSWORD", "pass")

    connection_string = (
        f"DRIVER={{{driver}}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"UID={user};"
        f"PWD={password};"
        "TrustServerCertificate=yes;"
    )
    return pyodbc.connect(connection_string)

QUERY = """
SELECT 
    name, 
    CASE 
        WHEN LEFT(address, 4) = '10.0' 
             THEN '172.16' + SUBSTRING(address, 5, LEN(address))
        ELSE address 
    END AS address
FROM devices
WHERE device_type = 'jigsaw'
  AND name NOT LIKE '%TEST%'
  AND name NOT LIKE '%DIS%'
  AND name NOT LIKE '%DM%'
  AND name NOT LIKE '%MT%'
  AND address IS NOT NULL
	AND address NOT LIKE '127.%'
"""

@app.get("/devices/jigsaw", response_model=List[Dict[str, Any]])
def get_jigsaw_devices():
    """
    Returns all jigsaw devices whose names do not contain
    TEST, DIS, DM or MT and whose address field is not NULL.
    """
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(QUERY)
                columns = [column[0] for column in cur.description]
                rows = cur.fetchall()

        # Convert rows to list of dicts
        results = [dict(zip(columns, row)) for row in rows]
        return results

    except pyodbc.Error as exc:
        raise HTTPException(status_code=500, detail=str(exc))