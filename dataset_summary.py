
import duckdb

connection = duckdb.connect()

# Read all five days of gameplay data
file_path = "player_data/February_*/*.nakama-0"

# 1. Overall dataset statistics
summary_query = f"""
SELECT
    COUNT(*) AS total_events,
    COUNT(DISTINCT user_id) AS unique_players_and_bots,
    COUNT(DISTINCT match_id) AS unique_matches,
    COUNT(DISTINCT map_id) AS unique_maps,
    COUNT(DISTINCT CASE
        WHEN regexp_full_match(user_id, '[0-9]+')
        THEN user_id
    END) AS unique_bots,
    COUNT(DISTINCT CASE
        WHEN NOT regexp_full_match(user_id, '[0-9]+')
        THEN user_id
    END) AS unique_humans
FROM read_parquet('{file_path}')
"""

summary = connection.execute(summary_query).fetchone()

print("\n========== DATASET SUMMARY ==========")
print("Total events:", summary[0])
print("Unique players and bots:", summary[1])
print("Unique matches:", summary[2])
print("Unique maps:", summary[3])
print("Unique bots:", summary[4])
print("Unique humans:", summary[5])

# 2. Event type counts
event_query = f"""
SELECT
    CAST(event AS VARCHAR) AS event_type,
    COUNT(*) AS total
FROM read_parquet('{file_path}')
GROUP BY event_type
ORDER BY total DESC
"""

events = connection.execute(event_query).fetchall()

print("\n========== EVENT TYPE COUNTS ==========")

for event_type, total in events:
    print(f"{event_type}: {total:,}")

# 3. Map counts
map_query = f"""
SELECT
    map_id,
    COUNT(*) AS total_events
FROM read_parquet('{file_path}')
GROUP BY map_id
ORDER BY total_events DESC
"""

maps = connection.execute(map_query).fetchall()

print("\n========== MAP COUNTS ==========")

for map_name, total in maps:
    print(f"{map_name}: {total:,}")

connection.close()
