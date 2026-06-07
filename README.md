# 🎧 Tidy Tuesday · Spotify Dashboard

A neon-drenched, club-dark Streamlit dashboard for exploring the **Spotify / TidyTuesday** dataset — audio features, genre landscapes, popularity dynamics, and danceability profiles across 32,000+ tracks.

---

## Folder Structure

```
spotify_dashboard/
├── data/
│   └── spotify_songs.csv     ← dataset goes here (TidyTuesday 2020-01-21)
├── .streamlit/
│   └── config.toml
├── app.py
├── charts.py
├── filters.py
├── requirements.txt
└── README.md
```

---

## Dataset

Download from TidyTuesday:
```
https://raw.githubusercontent.com/rfordatascience/tidytuesday/master/data/2020/2020-01-21/spotify_songs.csv
```
Save to `data/spotify_songs.csv`.

---

## Setup & Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

Opens at `http://localhost:8501`

---

## Dashboard Sections

| Section | What's Inside |
|---------|--------------|
| **01 · Genre Command** | Popularity bar by genre · Track volume breakdown · Genre radar fingerprint |
| **02 · Audio DNA** | Feature correlation heatmap · Box distributions · Danceability vs Energy scatter |
| **03 · Tempo & Mood** | Valence vs Danceability · Tempo histogram · Acousticness vs Instrumentalness |
| **04 · Popularity Engine** | Popularity over release years · Top artists · Loudness vs Popularity |
| **05 · Deep Frequency** | Speechiness vs Loudness · Duration analysis · Key & Mode breakdown |
| **06 · Track Explorer** | Filtered table · Audio profile card · CSV export |

## Sidebar Filters
- **Genre** (multi-select)
- **Sub-genre** (multi-select)
- **Release Year** range
- **Popularity** range
- **Danceability** range
- **Tempo** range
- **Top N** for ranked charts

---

## Design

- **Theme**: Neon-on-void — midnight black, electric green, hot magenta, ultraviolet purple
- **Fonts**: Chakra Petch (display) · Share Tech Mono (mono/labels) · DM Sans (body)
- Completely different from Coffee (parchment/warm), Big Mac (editorial black/gold), COVID (clinical white)

---

*Data: Spotify / TidyTuesday 2020 · Collector: Charlie Thompson*
