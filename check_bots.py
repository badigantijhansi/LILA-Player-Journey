
import duckdb

connection = duckdb.connect()

DATA_PATH = "player_data/February_*/*.nakama-0"

results = connection.execute(f"""
    SELECT
        map_id,
        regexp_extract(filename, 'February_[0-9]+', 0) AS game_date,
        match_id,
        COUNT(*) AS bot_records,
        COUNT(DISTINCT user_id) AS bot_ids
    FROM read_parquet('{DATA_PATH}', filename=true)
    WHERE CAST(event AS VARCHAR) = 'BotPosition'
    GROUP BY map_id, game_date, match_id
    ORDER BY bot_records DESC
    LIMIT 20
""").fetchall()

print("\n========== MATCHES CONTAINING BOTS ==========")

for map_name, game_date, match_id, records, ids in results:
    print(f"\nMap: {map_name}")
    print(f"Date: {game_date}")
    print(f"Match: {match_id}")
    print(f"Bot movement records: {records}")
    print(f"Unique bot IDs: {ids}")

connection.close()
