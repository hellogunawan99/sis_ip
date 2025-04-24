import requests
import mysql.connector

# ----- STEP 1: Fetch Data from the API -----
api_url = "http://localhost:8000/devices/jigsaw"
try:
    response = requests.get(api_url, timeout=10)
    response.raise_for_status()
    devices = response.json()   # Expecting a list of dicts with keys "name", "address", "device_type"
except Exception as e:
    print(f"Error fetching API data: {e}")
    devices = []

# ----- STEP 2: Connect to the MySQL Database -----
# Replace the below variables with your MySQL connection details
mysql_config = {
    'user': 'user',
    'password': 'pass',
    'host': 'localhost',
    'port': 3306,
    'database': 'db',
}
try:
    cnx = mysql.connector.connect(**mysql_config)
    cursor = cnx.cursor()
except mysql.connector.Error as err:
    print(f"Error connecting to MySQL: {err}")
    exit(1)

# ----- STEP 3: Update the MySQL "unit" Table -----
# The query selects only units with status = 0 and device_id = 1. 
update_query = """
    UPDATE unit
    SET ip = %s
    WHERE id = %s  -- id here is assumed to match the device name from the API
      AND `status` = 0
      AND device_id = 1
"""

# Loop through each device from the API and update the corresponding MySQL record
updated_count = 0
for device in devices:
    name = device.get("name")
    address = device.get("address")
    if name and address:
        try:
            cursor.execute(update_query, (address, name))
            updated_count += cursor.rowcount
        except mysql.connector.Error as err:
            print(f"Failed to update record for {name}: {err}")

# Make sure changes are committed.
cnx.commit()

print(f"Updated {updated_count} rows in the MySQL database.")

# Close the MySQL connection
cursor.close()
cnx.close()
