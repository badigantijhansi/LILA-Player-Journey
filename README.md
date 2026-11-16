# LILA BLACK – Player Journey Visualization Tool

## Project Overview

The Player Journey Visualization Tool is an interactive gameplay telemetry analysis application developed to explore and visualize player and bot behavior in LILA BLACK.

The application processes gameplay telemetry stored in Parquet files and presents player movement, gameplay events, match timelines, movement heatmaps, and dataset-level analytics through an interactive dashboard.

The goal is to make gameplay data easier to understand and help identify movement patterns, activity hotspots, and gameplay behavior that can support level-design analysis.

## Key Features

### 1. Gameplay Filters
- Select a map.
- Select a gameplay date.
- Select an individual match.
- Toggle human player movement.
- Toggle bot movement.
- Toggle gameplay event markers.
- Toggle the movement heatmap.

### 2. Player Journey Map
- Displays player movement paths on the original minimap.
- Separates human and bot movement using different colors.
- Displays gameplay events at their corresponding map locations.
- Supports interactive zooming and panning.

### 3. Match Timeline
- Displays gameplay activity over elapsed match time.
- Provides manual timeline controls.
- Allows users to advance through gameplay records one second at a time.
- Includes a restart control.

### 4. Movement Heatmap
- Visualizes movement concentration across the selected map and date.
- Combines human and bot movement records across matches.
- Uses color intensity to highlight areas with higher movement activity.

### 5. Gameplay Analytics
Provides dataset-wide statistics and visual reports:

- Total telemetry records.
- Total matches.
- Unique player and bot IDs.
- Event distribution.
- Activity by map.
- Movement hotspot analysis.

## Dataset Overview

The analyzed dataset contains:

| Metric | Value |
|---|---:|
| Total Records | 89,104 |
| Total Matches | 796 |
| Unique IDs | 339 |
| Human IDs | 245 |
| Bot IDs | 94 |
| Maps | 3 |
| Dates | 5 |

### Maps

- AmbroseValley
- Lockdown
- GrandRift

### Gameplay Events

The application processes the following event types:

| Event | Description |
|---|---|
| Position | Human player movement |
| BotPosition | Bot movement |
| Loot | Item pickup |
| Kill | Human killed human |
| Killed | Human was killed by human |
| BotKill | Human killed bot |
| BotKilled | Human was killed by bot |
| KilledByStorm | Player eliminated by storm |

## Technology Stack

- **Python** – Application logic and data processing.
- **Streamlit** – Interactive web dashboard.
- **DuckDB** – Querying and processing Parquet telemetry files.
- **Plotly** – Interactive charts and gameplay visualizations.
- **Pillow (PIL)** – Loading and processing minimap images.

## Project Structure

```text
LILA-Player-Journey/
│
├── app.py
├── analytics_report.py
├── inspect_data.py
├── inspect_events.py
├── dataset_summary.py
├── validate_map_coordinates.py
├── check_bots.py
│
├── player_data/
│   ├── February_10/
│   ├── February_11/
│   ├── February_12/
│   ├── February_13/
│   ├── February_14/
│   │
│   └── minimaps/
│       ├── AmbroseValley_Minimap.png
│       ├── GrandRift_Minimap.png
│       └── Lockdown_Minimap.jpg
│
├── .venv/
│
└── README.md
```

## Installation and Setup

### Requirements

- Python 3.13 or a compatible Python version.
- Windows, macOS, or Linux.
- Gameplay telemetry Parquet files.
- Corresponding minimap images.

### 1. Clone the Repository

```bash
git clone YOUR_REPOSITORY_URL
cd LILA-Player-Journey
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

### 3. Activate the Environment

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 4. Install Dependencies

```bash
pip install streamlit duckdb plotly pillow
```

### 5. Add the Dataset

Place the authorized gameplay telemetry files inside the `player_data` folder, preserving the date-folder structure and minimap directory.

### 6. Run the Application

```bash
python -m streamlit run app.py
```

Open the local URL displayed in the terminal, normally:

```text
http://localhost:8501
```

## Data Processing and Visualization

The application reads Parquet telemetry files using DuckDB.

Gameplay movement records are grouped by player and match to construct individual movement paths.

The map visualization uses the world coordinates `x` and `z` to position movement records on the corresponding minimap.

Map-specific coordinate configurations are used to convert world coordinates into minimap pixel positions.

Movement heatmaps aggregate position records into grid cells to identify areas with higher movement activity.

## Analytical Observations

Initial dataset-level observations:

1. AmbroseValley contributes approximately 68.5% of all telemetry records.
2. Human and bot movement records together account for approximately 82% of the dataset.
3. An AmbroseValley movement hotspot appears among the top three hotspot cells on all five analyzed dates.

These observations can help guide further investigation of movement distribution, route diversity, player activity, and map engagement.

A high-activity hotspot does not automatically indicate congestion or a level-design problem; additional gameplay metrics and context are needed.

## Assumptions and Limitations

- The dataset covers February 10–14, 2026.
- The `ts` field is treated as elapsed match time rather than calendar time.
- Map visualization uses `x` and `z` world coordinates.
- Heatmap counts represent movement records, not necessarily unique players.
- Timeline controls currently support manual stepping rather than automatic playback.
- Analytical observations are descriptive and should not be treated as proof of player behavior or design issues.

## Data Privacy

Gameplay telemetry may contain proprietary assessment data.

Do not publish the original dataset, player identifiers, or other restricted files in a public repository without explicit authorization.

## Running the Application

```bash
python -m streamlit run app.py
```

---

**Project:** LILA BLACK – Player Journey Visualization Tool  
**Purpose:** Gameplay Telemetry Analysis and Player Movement Visualization