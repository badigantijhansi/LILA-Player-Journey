# Architecture – LILA BLACK Player Journey Visualization Tool

## 1. System Overview

The Player Journey Visualization Tool is built using Python, Streamlit, DuckDB, Plotly, and Pillow.

The application reads gameplay telemetry stored in Parquet files, processes player movement and gameplay events, converts world coordinates into minimap positions, and presents the results through an interactive dashboard.

## 2. Technology Architecture

| Component | Technology | Responsibility |
|---|---|---|
| Application | Python | Core application logic |
| User Interface | Streamlit | Filters, controls, dashboard layout |
| Data Processing | DuckDB | Querying Parquet telemetry |
| Visualization | Plotly | Movement paths, charts, heatmaps |
| Image Processing | Pillow | Loading minimap images |
| Data Storage | Parquet | Gameplay telemetry storage |

## 3. Data Flow

The application follows this processing flow:

1. Read gameplay telemetry from date-based Parquet folders.
2. Use DuckDB to query the telemetry records.
3. Apply map, date, and match filters.
4. Decode event values stored as BLOB data into readable event names.
5. Separate human and bot movement records.
6. Convert world coordinates into minimap pixel coordinates.
7. Group movement records by player and match to construct movement paths.
8. Aggregate movement records into grid cells for heatmap analysis.
9. Generate dataset analytics and interactive charts.
10. Display the results through the Streamlit dashboard.

### Data Flow Diagram

```text
Gameplay Telemetry (Parquet)
             |
             v
       DuckDB Queries
             |
             v
     Data Filtering
   (Map / Date / Match)
             |
             v
      Event Processing
             |
       +-----+------+
       |            |
       v            v
 Human Movement   Bot Movement
       |            |
       +------+-----+
              |
              v
    Coordinate Conversion
              |
              v
       Minimap Mapping
              |
       +------+------+
       |             |
       v             v
 Movement Paths   Heatmap
       |             |
       +------+------+
              |
              v
       Plotly Charts
              |
              v
       Streamlit UI
```

## 4. Coordinate Mapping

Gameplay telemetry provides world coordinates using `x`, `y`, and `z`.

For the two-dimensional minimap visualization, the application uses `x` and `z`.

The `y` coordinate represents vertical position and is not used for the minimap's horizontal and vertical axes.

The coordinate conversion is based on the map configuration provided in the dataset README.

### Map Configuration

| Map | Scale | Origin X | Origin Z |
|---|---:|---:|---:|
| AmbroseValley | 900 | -370 | -473 |
| GrandRift | 581 | -290 | -290 |
| Lockdown | 1000 | -500 | -500 |

The reference coordinate resolution is 1024 × 1024.

### Conversion Formula

First, calculate normalized coordinates:

```python
u = (x - origin_x) / scale
v = (z - origin_z) / scale
```

Then convert them into minimap pixel coordinates:

```python
pixel_x = u * image_width
pixel_y = (1 - v) * image_height
```

The actual minimap image dimensions are used for the final pixel conversion.

### Coordinate Validation

A validation script checked all 89,104 telemetry records against their corresponding minimap image bounds.

- Records inside map bounds: 89,104
- Records outside map bounds: 0
- Coordinate bounds validation: 100%

This confirms that all records fall within the calculated image bounds. It does not independently prove exact visual alignment for every point.

## 5. Player Movement Visualization

Movement records are grouped by:

- `user_id`
- `match_id`

The application uses separate visual colors for human and bot movement paths.

Plotly Scatter traces display movement paths using lines and markers.

The original minimap is placed behind the movement visualization using a Plotly layout image.

The map and movement traces share the same coordinate axes, allowing them to zoom and pan together.

## 6. Gameplay Event Visualization

The application identifies gameplay events by decoding the event BLOB values as UTF-8 text.

Supported events include:

| Event | Meaning |
|---|---|
| Position | Human player movement |
| BotPosition | Bot movement |
| Loot | Item pickup |
| Kill | Human killed human |
| Killed | Human was killed by human |
| BotKill | Human killed bot |
| BotKilled | Human was killed by bot |
| KilledByStorm | Player eliminated by storm |

Different marker symbols and colors distinguish event types on the player journey map.

## 7. Movement Heatmap

The movement heatmap aggregates Position and BotPosition records across all matches for the selected map and date.

Movement records are grouped into 100-world-unit by 100-world-unit grid cells.

The resulting counts are visualized using Plotly's two-dimensional histogram.

Higher-intensity regions represent areas containing more recorded movement samples.

These counts represent movement records, not unique players or confirmed congestion.

## 8. Gameplay Analytics

The analytics module uses DuckDB queries to calculate:

- Total telemetry records.
- Total matches.
- Unique IDs.
- Human IDs and bot IDs.
- Event distribution.
- Activity by map.
- Movement hotspot counts.

Dataset-wide metrics use all five dates and all three maps.

Movement hotspot analytics are calculated for the currently selected map and date across all matches.

## 9. Match Timeline

The timeline uses the `ts` field to represent elapsed match time.

Users can inspect gameplay records using the timeline slider and manual Next Second and Restart Timeline controls.

The current implementation uses manual stepping rather than automatic playback.

The timestamp is treated as match-relative elapsed time, not as the calendar date of the gameplay session.

## 10. Design Decisions and Trade-offs

### DuckDB for Parquet Processing

DuckDB queries Parquet files directly, avoiding the need to load the complete dataset into memory using a DataFrame-based workflow.

### Streamlit for the Dashboard

Streamlit provides a simple interactive interface with filters, controls, metrics, and visualizations.

### Plotly for Visualization

Plotly supports interactive movement paths, event markers, charts, zooming, and panning.

### Static Minimap Background

The original map image is used as the background so player movement can be interpreted in the context of the game environment.

### Manual Timeline Controls

Manual stepping provides a simple and predictable way to inspect elapsed match activity without requiring automatic playback.

## 11. Current Limitations

- Timeline playback is manual rather than automatic.
- Heatmap intensity represents movement-record counts and is not normalized by active players or match duration.
- Hotspot counts alone do not establish whether an area is balanced, congested, or problematic.
- Coordinate bounds validation does not guarantee exact alignment with every in-game location.
- The current analytics are descriptive and do not establish causal gameplay conclusions.

## 12. Conclusion

The architecture provides an interactive workflow for exploring gameplay telemetry, understanding player and bot movement, examining gameplay events, and identifying areas of concentrated activity.

The system is designed to support further gameplay analysis and level-design investigation.