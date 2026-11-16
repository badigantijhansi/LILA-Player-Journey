# Gameplay Insights and Level Design Recommendations

## LILA BLACK – Player Journey Visualization Tool

## 1. Overview

This document presents three observations derived from the gameplay telemetry dataset covering February 10–14, 2026.

The analysis focuses on map activity, movement behavior, and recurring movement hotspots.

The observations are descriptive. They identify areas worth investigating rather than claiming that a particular map or location has a confirmed gameplay problem.

## 2. Insight 1 – AmbroseValley Has the Highest Telemetry Activity

### Observation

AmbroseValley accounts for the largest share of telemetry records across the three maps.

| Map | Telemetry Records | Share |
|---|---:|---:|
| AmbroseValley | 61,013 | 68.5% |
| Lockdown | 21,238 | 23.8% |
| GrandRift | 6,853 | 7.7% |
| **Total** | **89,104** | **100%** |

AmbroseValley contributes approximately 68.5% of all recorded telemetry activity.

### Interpretation

AmbroseValley has substantially more recorded activity than the other two maps.

However, telemetry volume alone does not prove that players prefer this map. Differences in match counts, active participants, and match duration may influence the result.

### Level Design Recommendation

Investigate whether AmbroseValley's high activity is associated with:

- More active matches.
- Longer match durations.
- More movement opportunities.
- More frequently visited areas.

Compare activity after normalizing by active players, matches, and match duration.

**Suggested metric:** Movement records per active player per match.

## 3. Insight 2 – Movement Is the Dominant Recorded Gameplay Activity

### Observation

Human and bot movement together account for 73,059 records.

| Event Type | Records |
|---|---:|
| Human Position | 51,347 |
| BotPosition | 21,712 |
| Combined Movement | 73,059 |
| Total Dataset Records | 89,104 |

Movement represents approximately 82.0% of all telemetry records.

### Interpretation

The dataset contains a large amount of movement telemetry compared with other recorded event types.

This makes movement analysis particularly useful for investigating player routes, bot activity, and spatial distribution.

The movement-record count does not directly represent the number of unique players or the distance travelled.

### Level Design Recommendation

Use movement paths and heatmaps to investigate:

- Frequently used routes.
- Areas with concentrated movement.
- Differences between human and bot movement.
- Areas that appear to receive comparatively little movement.

Compare human and bot movement separately to understand whether they use similar routes or different parts of the map.

**Suggested metrics:**
- Movement records per active participant.
- Unique participants visiting each grid cell.
- Route diversity.
- Human-to-bot movement distribution.

## 4. Insight 3 – AmbroseValley Has a Recurring Movement Hotspot

### Observation

The grid cell `(0, -1)` appears among the top three movement hotspot cells on all five analyzed dates for AmbroseValley.

| Date | Grid Cell (0, -1) | Movement Records | Share of Map/Date Movement |
|---|---|---:|---:|
| February 10 | (0, -1) | 1,631 | 8.52% |
| February 11 | (0, -1) | 766 | 7.07% |
| February 12 | (0, -1) | 879 | 8.68% |
| February 13 | (0, -1) | 446 | 7.34% |
| February 14 | (0, -1) | 296 | 11.51% |

On February 14, this cell is the second-highest hotspot, with 296 movement records.

### Interpretation

The repeated appearance of this grid cell suggests a consistent concentration of recorded movement in the same world-coordinate region.

This area is worth investigating because recurring movement concentration may be associated with important routes, objectives, loot locations, or map geometry.

The available counts do not establish whether the area is congested or whether its design needs changes.

### Level Design Recommendation

Inspect the corresponding area on the AmbroseValley minimap.

Investigate:

- Whether the area connects important routes.
- Whether nearby loot or objectives attract movement.
- Whether multiple paths converge in this region.
- Whether the area creates meaningful player encounters.

Before changing the map, compare the hotspot with kill events, loot pickups, unique visitors, and route diversity.

**Suggested metrics:**
- Unique players visiting the hotspot.
- Loot pickups per visitor.
- Combat events per visitor.
- Average time spent in the area.
- Number of distinct routes entering and leaving the area.

## 5. Recommended Follow-up Analysis

The following analyses could provide deeper gameplay and level-design insights:

| Analysis | Purpose |
|---|---|
| Player-normalized heatmap | Compare activity fairly across different match sizes |
| Human vs. bot movement comparison | Identify differences in movement patterns |
| Loot and combat hotspot overlay | Understand the relationship between movement and gameplay events |
| Route diversity analysis | Identify whether players have multiple viable paths |
| Match-duration comparison | Understand differences in activity across matches |
| Unique hotspot visitors | Distinguish repeated movement samples from unique player visits |

## 6. Limitations

- The dataset covers five dates only.
- Telemetry record counts are not equivalent to unique player counts.
- Movement density does not automatically indicate congestion.
- Hotspot grid cells are based on 100-world-unit by 100-world-unit areas.
- The analysis does not establish the reasons behind player movement patterns.
- Further gameplay context and additional metrics are required before making map-design changes.

## 7. Conclusion

The telemetry analysis identifies three useful starting points for gameplay investigation:

1. AmbroseValley accounts for the largest share of recorded activity.
2. Movement is the dominant recorded gameplay activity.
3. One AmbroseValley grid cell repeatedly appears among the highest movement hotspots.

The visualization tool makes these patterns easier to explore through interactive maps, movement paths, heatmaps, timelines, and analytics charts.

These observations can help guide further investigation into map engagement, route diversity, player movement, and level-design opportunities.