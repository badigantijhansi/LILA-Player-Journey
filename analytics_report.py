import duckdb

DATA_PATH = "player_data/February_*/*.nakama-0"
con = duckdb.connect()

# Read the supplied Parquet files directly. No pandas or PyArrow required.
base = f"read_parquet('{DATA_PATH}', filename=true)"

print("\n========== DATASET OVERVIEW ==========")
rows = con.execute(f"""
    SELECT
        COUNT(*) AS total_rows,
        COUNT(DISTINCT match_id) AS unique_matches,
        COUNT(DISTINCT user_id) AS unique_ids,
        COUNT(DISTINCT map_id) AS maps,
        COUNT(DISTINCT regexp_extract(filename, 'February_[0-9]+', 0)) AS dates,
        COUNT(DISTINCT CASE WHEN regexp_matches(CAST(user_id AS VARCHAR), '^[0-9]+$') THEN user_id END) AS bot_ids,
        COUNT(DISTINCT CASE WHEN NOT regexp_matches(CAST(user_id AS VARCHAR), '^[0-9]+$') THEN user_id END) AS human_ids
    FROM {base}
""").fetchone()
print("Rows | Matches | Unique IDs | Maps | Dates | Bot IDs | Human IDs")
print(" | ".join(str(v) for v in rows))

print("\n========== EVENT COUNTS ==========")
for event_type, count in con.execute(f"""
    SELECT CAST(event AS VARCHAR) AS event_type, COUNT(*) AS event_count
    FROM {base}
    GROUP BY 1 ORDER BY event_count DESC
""").fetchall():
    print(f"{event_type}: {count:,}")

print("\n========== MAP AND DATE SUMMARY ==========")
print("Map | Date | Records | Matches | Human IDs | Bot IDs | Human movement | Bot movement | Loot | Combat/death events")
for r in con.execute(f"""
    SELECT
        map_id,
        regexp_extract(filename, 'February_[0-9]+', 0) AS game_date,
        COUNT(*) AS records,
        COUNT(DISTINCT match_id) AS matches,
        COUNT(DISTINCT CASE WHEN NOT regexp_matches(CAST(user_id AS VARCHAR), '^[0-9]+$') THEN user_id END) AS human_ids,
        COUNT(DISTINCT CASE WHEN regexp_matches(CAST(user_id AS VARCHAR), '^[0-9]+$') THEN user_id END) AS bot_ids,
        COUNT(*) FILTER (WHERE CAST(event AS VARCHAR) = 'Position') AS human_movement,
        COUNT(*) FILTER (WHERE CAST(event AS VARCHAR) = 'BotPosition') AS bot_movement,
        COUNT(*) FILTER (WHERE CAST(event AS VARCHAR) = 'Loot') AS loot,
        COUNT(*) FILTER (WHERE CAST(event AS VARCHAR) IN ('Kill','Killed','BotKill','BotKilled','KilledByStorm')) AS combat_death
    FROM {base}
    GROUP BY 1, 2 ORDER BY 1, 2
""").fetchall():
    print(" | ".join(str(v) for v in r))

print("\n========== TOP 12 MATCHES BY TOTAL MOVEMENT RECORDS ==========")
print("Map | Date | Match ID | Human IDs | Bot IDs | Human movement | Bot movement | Loot | Combat/death")
for r in con.execute(f"""
    SELECT
        map_id,
        regexp_extract(filename, 'February_[0-9]+', 0) AS game_date,
        match_id,
        COUNT(DISTINCT CASE WHEN NOT regexp_matches(CAST(user_id AS VARCHAR), '^[0-9]+$') THEN user_id END) AS human_ids,
        COUNT(DISTINCT CASE WHEN regexp_matches(CAST(user_id AS VARCHAR), '^[0-9]+$') THEN user_id END) AS bot_ids,
        COUNT(*) FILTER (WHERE CAST(event AS VARCHAR) = 'Position') AS human_movement,
        COUNT(*) FILTER (WHERE CAST(event AS VARCHAR) = 'BotPosition') AS bot_movement,
        COUNT(*) FILTER (WHERE CAST(event AS VARCHAR) = 'Loot') AS loot,
        COUNT(*) FILTER (WHERE CAST(event AS VARCHAR) IN ('Kill','Killed','BotKill','BotKilled','KilledByStorm')) AS combat_death
    FROM {base}
    GROUP BY 1, 2, 3
    ORDER BY (human_movement + bot_movement) DESC
    LIMIT 12
""").fetchall():
    print(" | ".join(str(v) for v in r))

print("\n========== MOVEMENT HOTSPOT CELLS (100-WORLD-UNIT GRID) ==========")
print("Map | Date | Grid X | Grid Z | Movement samples | Share of that map/date movement")
for r in con.execute(f"""
    WITH movement AS (
        SELECT
            map_id,
            regexp_extract(filename, 'February_[0-9]+', 0) AS game_date,
            CAST(floor(x / 100.0) AS INTEGER) AS grid_x,
            CAST(floor(z / 100.0) AS INTEGER) AS grid_z,
            COUNT(*) AS samples
        FROM {base}
        WHERE CAST(event AS VARCHAR) IN ('Position','BotPosition')
        GROUP BY 1, 2, 3, 4
    ), ranked AS (
        SELECT *,
            SUM(samples) OVER (PARTITION BY map_id, game_date) AS total_samples,
            ROW_NUMBER() OVER (PARTITION BY map_id, game_date ORDER BY samples DESC) AS rn
        FROM movement
    )
    SELECT map_id, game_date, grid_x, grid_z, samples,
           ROUND(100.0 * samples / total_samples, 2) AS share_percent
    FROM ranked WHERE rn <= 3
    ORDER BY map_id, game_date, rn
""").fetchall():
    print(" | ".join(str(v) for v in r))

con.close()
print("\nReport complete.")
