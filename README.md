# NBA Player Analyzer

A Python-based data analysis tool that ranks NBA players using min-max normalization and weighted scoring across multiple situational categories.

## Overview

Takes 2024-2025 NBA season data and generates custom rankings based on different in-game scenarios. Players are filtered, normalized, and scored using configurable stat weights — letting you find the best clutch scorer, best defender, best playmaker, and more.

## Features

- **Situational rankings** — rank players across 5 preset scenarios (overall, clutch, defensive, playmaker, three-point scorer)
- **Custom weights** — build your own scenario with user-defined stat weights between -1 and 1
- **Player comparison** — detailed side-by-side breakdown of two players' normalized and weighted stats
- **Data export** — generates ranked CSVs (top 20 and full list) for any scenario
- **Visualizations** via Plotly:
  - Bar chart — top N players per situation
  - Radar chart — head-to-head player comparison across all stats
  - Scatter plot — relationship between any two stats across players

## Tech Stack

- Python
- Pandas
- Plotly (express + graph objects)
- CSV (stdlib)

## Setup

```bash
pip install pandas plotly
```

Place `CS final project starter csv - Sheet1.csv` in the same directory as `Final_project.py`, then run:

```bash
python Final_project.py
```

## How It Works

1. **Filtering** — removes players with fewer than 20 games played or under 15 minutes per game
2. **Normalization** — applies min-max normalization across all stats for the filtered player pool
3. **Weighting** — multiplies each normalized stat by its situational weight to produce a score
4. **Ranking** — sorts players by score descending for the chosen scenario

## Preset Scenarios

| Scenario | Key Stats |
|---|---|
| Overall | PTS, AST, TRB, STL, BLK, TOV(-) |
| Clutch | PTS, FG%, eFG%, FT, TOV(-) |
| Defensive | DRB, STL, BLK |
| Playmaker | AST, TOV(-), ORB, PF(-), eFG% |
| Three-point scorer | 3P, 3P%, 3PA |

## Project Structure

```
├── Final_project.py
├── CS final project starter csv - Sheet1.csv
└── exported CSVs (generated on run)
```

## Author

Kevin Hennet — [GitHub](https://github.com/Kevin-Hennet) · [LinkedIn](https://www.linkedin.com/in/kevin-hennet-b1b33829b/)
