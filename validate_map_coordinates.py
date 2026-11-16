
import duckdb
from PIL import Image
from pathlib import Path

connection = duckdb.connect()

# Map coordinate configurations from the assessment README
map_config = {
    "AmbroseValley": {
        "scale": 900,
        "origin_x": -370,
        "origin_z": -473,
        "image": "AmbroseValley_Minimap.png"
    },
    "GrandRift": {
        "scale": 581,
        "origin_x": -290,
        "origin_z": -290,
        "image": "GrandRift_Minimap.png"
    },
    "Lockdown": {
        "scale": 1000,
        "origin_x": -500,
        "origin_z": -500,
        "image": "Lockdown_Minimap.jpg"
    }
}

query = """
SELECT map_id, x, z
FROM read_parquet('player_data/February_*/*.nakama-0')
"""

records = connection.execute(query).fetchall()

print("\n========== MAP COORDINATE VALIDATION ==========")

for map_name, config in map_config.items():

    image_path = Path("player_data/minimaps") / config["image"]

    with Image.open(image_path) as image:
        width, height = image.size

    total = 0
    inside = 0

    for record_map, x, z in records:

        if record_map != map_name:
            continue

        total += 1

        u = (x - config["origin_x"]) / config["scale"]
        v = (z - config["origin_z"]) / config["scale"]

        pixel_x = u * width
        pixel_y = (1 - v) * height

        if 0 <= pixel_x < width and 0 <= pixel_y < height:
            inside += 1

    percentage = (inside / total * 100) if total else 0

    print(f"\nMap: {map_name}")
    print(f"Image size: {width} x {height}")
    print(f"Total records: {total:,}")
    print(f"Inside map bounds: {inside:,}")
    print(f"Outside map bounds: {total - inside:,}")
    print(f"Inside percentage: {percentage:.2f}%")

connection.close()
