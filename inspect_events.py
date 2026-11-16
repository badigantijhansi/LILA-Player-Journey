
import duckdb

connection = duckdb.connect()

query = """
SELECT
    user_id,
    match_id,
    map_id,
    x,
    y,
    z,
    ts,
    event
FROM read_parquet('player_data/February_10/*.nakama-0')
LIMIT 10
"""

records = connection.execute(query).fetchall()

print("\nFIRST 10 GAMEPLAY RECORDS")
print("=========================")

for index, record in enumerate(records, start=1):
    user_id, match_id, map_id, x, y, z, ts, event = record

    print(f"\nRecord {index}")
    print("Player ID:", user_id)
    print("Map:", map_id)
    print("Position:", x, y, z)
    print("Timestamp:", ts)

    event_bytes = bytes(event)

    print("Event bytes (hex):", event_bytes.hex()[:150])

    try:
        print("Event decoded:", event_bytes.decode("utf-8"))
    except UnicodeDecodeError:
        print("Event decoded: Not plain UTF-8 text")

connection.close()
