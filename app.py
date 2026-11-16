
import streamlit as st
import duckdb
import plotly.graph_objects as go
from PIL import Image
from pathlib import Path
import base64
import io
import zipfile
from datetime import timedelta

# Automatically extract the dataset on Streamlit Cloud
DATA_ZIP = Path("player_data.zip")
DATA_ROOT = Path("player_data")

if not DATA_ROOT.exists():
    if DATA_ZIP.exists():
        with zipfile.ZipFile(DATA_ZIP, "r") as archive:
            archive.extractall(".")
    else:
        st.error("Dataset not found. Please check player_data.zip.")
        st.stop()


# -----------------------------------
# 1. APPLICATION CONFIGURATION
# -----------------------------------

st.set_page_config(
    page_title="Player Journey Visualization",
    page_icon="🎮",
    layout="wide"
)

st.title("🎮 Player Journey Visualization")
st.caption("LILA BLACK | Gameplay Telemetry Explorer")

connection = duckdb.connect()

DATA_PATH = "player_data/February_*/*.nakama-0"
MAP_FOLDER = Path("player_data/minimaps")

MAP_CONFIG = {
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

# -----------------------------------
# 2. SIDEBAR FILTERS
# -----------------------------------

st.sidebar.header("Gameplay Filters")

selected_map = st.sidebar.selectbox(
    "Select Map",
    list(MAP_CONFIG.keys())
)

dates = connection.execute(f"""
    SELECT DISTINCT
        regexp_extract(filename, 'February_[0-9]+', 0) AS game_date
    FROM read_parquet('{DATA_PATH}', filename=true)
    ORDER BY game_date
""").fetchall()

date_options = [row[0] for row in dates]

selected_date = st.sidebar.selectbox(
    "Select Date",
    date_options
)

matches = connection.execute(f"""
    SELECT DISTINCT match_id
    FROM read_parquet('{DATA_PATH}', filename=true)
    WHERE map_id = ?
      AND regexp_extract(filename, 'February_[0-9]+', 0) = ?
    ORDER BY match_id
""", [selected_map, selected_date]).fetchall()

match_options = [row[0] for row in matches]

if not match_options:
    connection.close()
    st.warning("No matches found for this selection.")
    st.stop()

selected_match = st.sidebar.selectbox(
    "Select Match",
    match_options
)

st.sidebar.divider()

show_humans = st.sidebar.checkbox(
    "Show Human Players",
    value=True
)

show_bots = st.sidebar.checkbox(
    "Show Bots",
    value=True
)

show_events = st.sidebar.checkbox(
    "Show Gameplay Events",
    value=True
)

show_heatmap = st.sidebar.checkbox(
    "Show Movement Heatmap",
    value=False,
    help="Shows movement density across all matches for the selected map and date."
)

# -----------------------------------
# 3. LOAD SELECTED MATCH DATA
# -----------------------------------

data = connection.execute(f"""
    SELECT
        user_id,
        match_id,
        map_id,
        x,
        y,
        z,
        ts,
        CAST(event AS VARCHAR) AS event_type
    FROM read_parquet('{DATA_PATH}', filename=true)
    WHERE map_id = ?
      AND match_id = ?
      AND regexp_extract(filename, 'February_[0-9]+', 0) = ?
    ORDER BY ts
""", [selected_map, selected_match, selected_date]).fetchall()

# Movement density is aggregated across ALL matches for the selected map/date.
# This is intentionally separate from the selected-match timeline and paths.
heatmap_data = connection.execute(f"""
    SELECT
        user_id,
        x,
        z
    FROM read_parquet('{DATA_PATH}', filename=true)
    WHERE map_id = ?
      AND regexp_extract(filename, 'February_[0-9]+', 0) = ?
      AND CAST(event AS VARCHAR) IN ('Position', 'BotPosition')
""", [selected_map, selected_date]).fetchall()


# -----------------------------------
# 3A. LOAD DATASET-WIDE ANALYTICS
# -----------------------------------
# These summaries are calculated from the complete dataset, not only
# the currently selected match. DuckDB reads Parquet directly.
dataset_summary = connection.execute(f"""
    SELECT
        COUNT(*) AS total_rows,
        COUNT(DISTINCT match_id) AS total_matches,
        COUNT(DISTINCT user_id) AS unique_ids,
        COUNT(DISTINCT map_id) AS total_maps,
        COUNT(DISTINCT regexp_extract(filename, 'February_[0-9]+', 0)) AS total_dates,
        COUNT(DISTINCT CASE
            WHEN regexp_matches(CAST(user_id AS VARCHAR), '^[0-9]+$')
            THEN user_id END) AS bot_ids,
        COUNT(DISTINCT CASE
            WHEN NOT regexp_matches(CAST(user_id AS VARCHAR), '^[0-9]+$')
            THEN user_id END) AS human_ids
    FROM read_parquet('{DATA_PATH}', filename=true)
""").fetchone()

event_summary = connection.execute(f"""
    SELECT CAST(event AS VARCHAR) AS event_type, COUNT(*) AS event_count
    FROM read_parquet('{DATA_PATH}')
    GROUP BY CAST(event AS VARCHAR)
    ORDER BY event_count DESC
""").fetchall()

map_summary = connection.execute(f"""
    SELECT
        map_id,
        COUNT(*) AS total_records,
        COUNT(DISTINCT match_id) AS matches,
        SUM(CASE WHEN CAST(event AS VARCHAR) = 'Position' THEN 1 ELSE 0 END) AS human_movement,
        SUM(CASE WHEN CAST(event AS VARCHAR) = 'BotPosition' THEN 1 ELSE 0 END) AS bot_movement,
        SUM(CASE WHEN CAST(event AS VARCHAR) = 'Loot' THEN 1 ELSE 0 END) AS loot_records,
        SUM(CASE WHEN CAST(event AS VARCHAR) IN
            ('Kill', 'Killed', 'BotKill', 'BotKilled', 'KilledByStorm')
            THEN 1 ELSE 0 END) AS combat_death_records
    FROM read_parquet('{DATA_PATH}')
    GROUP BY map_id
    ORDER BY total_records DESC
""").fetchall()

hotspot_summary = connection.execute(f"""
    SELECT
        CAST(FLOOR(x / 100.0) AS INTEGER) AS grid_x,
        CAST(FLOOR(z / 100.0) AS INTEGER) AS grid_z,
        COUNT(*) AS movement_samples
    FROM read_parquet('{DATA_PATH}', filename=true)
    WHERE map_id = ?
      AND regexp_extract(filename, 'February_[0-9]+', 0) = ?
      AND CAST(event AS VARCHAR) IN ('Position', 'BotPosition')
    GROUP BY grid_x, grid_z
    ORDER BY movement_samples DESC
    LIMIT 8
""", [selected_map, selected_date]).fetchall()

connection.close()


if not data:
    st.warning("No gameplay records found.")
    st.stop()

# -----------------------------------
# 4. IDENTIFY PLAYERS AND STATISTICS
# -----------------------------------

human_ids = set()
bot_ids = set()

for row in data:
    user_id = str(row[0])

    if user_id.isdigit():
        bot_ids.add(user_id)
    else:
        human_ids.add(user_id)

event_types = set(row[7] for row in data)

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Events", f"{len(data):,}")
col2.metric("Human Players", len(human_ids))
col3.metric("Bots", len(bot_ids))
col4.metric("Event Types", len(event_types))

st.divider()


# -----------------------------------
# 4A. GAMEPLAY ANALYTICS DASHBOARD
# -----------------------------------

st.header("Gameplay Analytics")
st.caption(
    "Dataset-wide statistics use all five dates and all three maps. "
    "Movement hotspots use the selected map and date across all matches."
)

summary_col1, summary_col2, summary_col3, summary_col4, summary_col5 = st.columns(5)
summary_col1.metric("Dataset Records", f"{dataset_summary[0]:,}")
summary_col2.metric("Total Matches", f"{dataset_summary[1]:,}")
summary_col3.metric("Unique IDs", f"{dataset_summary[2]:,}")
summary_col4.metric("Human IDs", f"{dataset_summary[6]:,}")
summary_col5.metric("Bot IDs", f"{dataset_summary[5]:,}")

left_chart, right_chart = st.columns(2)

with left_chart:
    st.subheader("Event Distribution")
    event_names = [str(row[0]) for row in event_summary]
    event_values = [int(row[1]) for row in event_summary]
    event_figure = go.Figure(
        data=[go.Pie(
            labels=event_names,
            values=event_values,
            hole=0.42,
            textinfo="label+percent",
            hovertemplate="%{label}<br>Records: %{value:,}<extra></extra>"
        )]
    )
    event_figure.update_layout(
        height=420,
        margin=dict(l=10, r=10, t=25, b=10),
        showlegend=True
    )
    st.plotly_chart(event_figure, use_container_width=True)

with right_chart:
    st.subheader("Activity by Map")
    map_names = [str(row[0]) for row in map_summary]
    map_values = [int(row[1]) for row in map_summary]
    map_figure = go.Figure(
        data=[go.Bar(
            x=map_names,
            y=map_values,
            text=map_values,
            texttemplate="%{text:,}",
            textposition="outside",
            hovertemplate="%{x}<br>Records: %{y:,}<extra></extra>"
        )]
    )
    map_figure.update_layout(
        height=420,
        yaxis_title="Telemetry records",
        margin=dict(l=10, r=10, t=25, b=10)
    )
    st.plotly_chart(map_figure, use_container_width=True)

st.subheader(f"Movement Hotspots | {selected_map} | {selected_date}")
if hotspot_summary:
    hotspot_labels = [
        f"Grid ({row[0]}, {row[1]})" for row in hotspot_summary
    ]
    hotspot_values = [int(row[2]) for row in hotspot_summary]
    hotspot_figure = go.Figure(
        data=[go.Bar(
            x=hotspot_labels,
            y=hotspot_values,
            text=hotspot_values,
            texttemplate="%{text:,}",
            textposition="outside",
            hovertemplate="%{x}<br>Movement samples: %{y:,}<extra></extra>"
        )]
    )
    hotspot_figure.update_layout(
        height=380,
        yaxis_title="Movement samples",
        margin=dict(l=10, r=10, t=25, b=10)
    )
    st.plotly_chart(hotspot_figure, use_container_width=True)
    st.caption(
        "Each grid cell represents a 100-world-unit by 100-world-unit area. "
        "Counts combine human and bot Position records across all matches "
        "for the selected map and date."
    )
else:
    st.info("No movement records are available for this map and date.")

st.divider()

# -----------------------------------
# 5. LOAD MAP IMAGE
# -----------------------------------

config = MAP_CONFIG[selected_map]
image_path = MAP_FOLDER / config["image"]

if not image_path.exists():
    st.error(f"Map image not found: {image_path}")
    st.stop()

with Image.open(image_path) as original:
    map_width, map_height = original.size
    map_image = original.convert("RGB")
    map_image.thumbnail((1400, 1400))

    buffer = io.BytesIO()
    map_image.save(
        buffer,
        format="JPEG",
        quality=90
    )

image_base64 = base64.b64encode(
    buffer.getvalue()
).decode("utf-8")

image_source = "data:image/jpeg;base64," + image_base64

# -----------------------------------
# 6. CONVERT WORLD COORDINATES
# -----------------------------------

def convert_coordinates(x, z):
    pixel_x = (
        (x - config["origin_x"]) / config["scale"]
    ) * map_width

    pixel_y = (
        1 - (z - config["origin_z"]) / config["scale"]
    ) * map_height

    return pixel_x, pixel_y


# -----------------------------------
# 7. PREPARE TIMELINE
# -----------------------------------

min_ts = min(row[6] for row in data)
max_ts = max(row[6] for row in data)

max_seconds = max(
    1,
    int((max_ts - min_ts).total_seconds())
)

# Reset the timeline when the map, date, or match changes.
timeline_identity = f"{selected_map}|{selected_date}|{selected_match}"

if st.session_state.get("timeline_identity") != timeline_identity:
    st.session_state.timeline_identity = timeline_identity
    st.session_state.timeline_second = 0

# Make sure the saved slider value remains inside the selected match range.
if st.session_state.get("timeline_second", 0) > max_seconds:
    st.session_state.timeline_second = max_seconds

# -----------------------------------
# 8. TIMELINE CONTROLS AND MAP
# -----------------------------------

def display_timeline():

    st.subheader("Match Timeline")

    control_col, slider_col = st.columns([1, 4])

    # Handle button clicks BEFORE creating the slider widget.
    # This avoids changing a widget's state after it has been instantiated.
    with control_col:
        if st.button(
            "Next Second",
            key="timeline_next_second",
            use_container_width=True
        ):
            st.session_state.timeline_second = min(
                st.session_state.get("timeline_second", 0) + 1,
                max_seconds
            )

        if st.button(
            "Restart Timeline",
            key="timeline_restart",
            use_container_width=True
        ):
            st.session_state.timeline_second = 0

    with slider_col:
        current_second = st.slider(
            "Match Timeline (seconds)",
            min_value=0,
            max_value=max_seconds,
            step=1,
            key="timeline_second"
        )

    current_ts = min_ts + timedelta(seconds=current_second)

    visible_data = [
        row for row in data
        if row[6] <= current_ts
    ]

    st.caption(
        f"Elapsed: {current_second} seconds / {max_seconds} seconds"
        f" | Visible records: {len(visible_data):,} / {len(data):,}"
    )

    # -----------------------------------
    # 9. CREATE PLAYER MOVEMENT PATHS
    # -----------------------------------

    player_paths = {}

    for row in visible_data:
        user_id, match_id, map_id, x, y, z, ts, event_type = row

        if event_type == "BotPosition":
            is_bot = True
        elif event_type == "Position":
            is_bot = False
        else:
            continue

        if is_bot and not show_bots:
            continue

        if not is_bot and not show_humans:
            continue

        pixel_x, pixel_y = convert_coordinates(x, z)
        key = (user_id, match_id)

        if key not in player_paths:
            player_paths[key] = {
                "x": [],
                "y": [],
                "timestamps": [],
                "is_bot": is_bot
            }

        player_paths[key]["x"].append(pixel_x)
        player_paths[key]["y"].append(pixel_y)
        player_paths[key]["timestamps"].append(ts)

    # -----------------------------------
    # 10. CREATE PLOTLY FIGURE
    # -----------------------------------

    figure = go.Figure()

    # Keep the working, axis-anchored map background.
    figure.add_layout_image(
        dict(
            source=image_source,
            xref="x",
            yref="y",
            x=0,
            y=0,
            xanchor="left",
            yanchor="top",
            sizex=map_width,
            sizey=map_height,
            sizing="stretch",
            layer="below"
        )
    )

    # -----------------------------------
    # 11. OPTIONAL MOVEMENT HEATMAP
    # -----------------------------------

    if show_heatmap:
        heatmap_x = []
        heatmap_y = []
        heatmap_participants = set()

        for user_id, world_x, world_z in heatmap_data:
            is_bot = str(user_id).isdigit()

            if is_bot and not show_bots:
                continue
            if not is_bot and not show_humans:
                continue

            pixel_x, pixel_y = convert_coordinates(world_x, world_z)
            heatmap_x.append(pixel_x)
            heatmap_y.append(pixel_y)
            heatmap_participants.add(str(user_id))

        if heatmap_x:
            figure.add_trace(
                go.Histogram2d(
                    x=heatmap_x,
                    y=heatmap_y,
                    nbinsx=90,
                    nbinsy=90,
                    colorscale="Hot",
                    opacity=0.55,
                    showscale=True,
                    colorbar=dict(
                        title="Movement<br>samples",
                        thickness=14
                    ),
                    hovertemplate=(
                        "Movement samples: %{z}"
                        "<br>Map X: %{x:.0f}"
                        "<br>Map Y: %{y:.0f}"
                        "<extra></extra>"
                    ),
                    name="Movement density"
                )
            )
            st.caption(
                f"Movement heatmap: {len(heatmap_x):,} position records "
                f"from {len(heatmap_participants):,} participants across "
                f"all {selected_map} matches on {selected_date}. "
                "Brighter areas indicate more recorded movement samples."
            )
        else:
            st.info("No movement records match the current human/bot filters for this map and date.")

    # -----------------------------------
    # 12. DRAW PLAYER AND BOT PATHS
    # -----------------------------------

    for (user_id, match_id), path in player_paths.items():

        if path["is_bot"]:
            line_color = "orange"
            label = "Bot"
        else:
            line_color = "#00FFFF"
            label = "Human"

        figure.add_trace(
            go.Scatter(
                x=path["x"],
                y=path["y"],
                mode="lines+markers",
                name=f"{label} {str(user_id)[:8]}",
                line=dict(
                    color=line_color,
                    width=3
                ),
                marker=dict(
                    color=line_color,
                    size=7
                ),
                opacity=1,
                customdata=path["timestamps"],
                hovertemplate=(
                    f"{label}: {user_id}"
                    "<br>X: %{x:.1f}"
                    "<br>Y: %{y:.1f}"
                    "<br>Time: %{customdata}"
                    "<extra></extra>"
                )
            )
        )

    # -----------------------------------
    # 13. DISPLAY GAMEPLAY EVENT MARKERS
    # -----------------------------------

    if show_events:

        event_styles = {
            "Loot": ("yellow", "diamond"),
            "Kill": ("red", "star"),
            "Killed": ("purple", "x"),
            "BotKill": ("orange", "star"),
            "BotKilled": ("pink", "x"),
            "KilledByStorm": ("cyan", "triangle-up")
        }

        for event_name, (color, symbol) in event_styles.items():

            event_x = []
            event_y = []

            for row in visible_data:
                user_id, match_id, map_id, x, y, z, ts, event_type = row

                if event_type != event_name:
                    continue

                is_bot = str(user_id).isdigit()

                if is_bot and not show_bots:
                    continue

                if not is_bot and not show_humans:
                    continue

                pixel_x, pixel_y = convert_coordinates(x, z)
                event_x.append(pixel_x)
                event_y.append(pixel_y)

            if event_x:
                figure.add_trace(
                    go.Scatter(
                        x=event_x,
                        y=event_y,
                        mode="markers",
                        name=event_name,
                        marker=dict(
                            color=color,
                            symbol=symbol,
                            size=10
                        )
                    )
                )

    # -----------------------------------
    # 14. FINAL CHART LAYOUT
    # -----------------------------------

    figure.update_layout(
        title=f"{selected_map} | {selected_date}",
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis=dict(
            range=[0, map_width],
            visible=False,
            constrain="domain"
        ),
        yaxis=dict(
            range=[map_height, 0],
            visible=False,
            scaleanchor="x",
            scaleratio=1
        ),
        height=750,
        margin=dict(
            l=0,
            r=0,
            t=60,
            b=0
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0
        )
    )

    # -----------------------------------
    # 15. DISPLAY MAP
    # -----------------------------------

    st.subheader("Player Journey Map")

    st.plotly_chart(
        figure,
        use_container_width=True,
        config={
            "displayModeBar": True,
            "scrollZoom": True
        }
    )


display_timeline()
