
import duckdb

# Connect to DuckDB
connection = duckdb.connect()

# Read the February 10 gameplay files
query = """
DESCRIBE
SELECT *
FROM read_parquet('player_data/February_10/*.nakama-0')
"""

# Get column names and data types
result = connection.execute(query).fetchall()

print("\nGAMEPLAY DATA COLUMNS")
print("---------------------")

for column in result:
    print(column)

connection.close()
