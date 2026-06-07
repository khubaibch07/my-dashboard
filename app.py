"""
app.py — Tidy Tuesday Spotify Dashboard
Aesthetic: Neon-on-void · Electric green · Hot magenta · Midnight black
Fonts: Chakra Petch (display) · Share Tech Mono (labels) · DM Sans (body)
"""

import streamlit as st
import pandas as pd
import numpy as np
import os
from io import StringIO
from datetime import datetime
import charts
import filters
import plotly.graph_objects as go

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="🎧 Spotify · Track Analysis",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🎧",
)

# ── GLOBAL CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Chakra+Petch:ital,wght@0,300;0,400;0,600;0,700;1,400&family=Share+Tech+Mono&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,400&display=swap');

/* ─── CSS Variables ─── */
:root {
    --void:         #050508;
    --void2:        #0D0D14;
    --void3:        #12121C;
    --panel:        #0A0A12;
    --border:       #1E1E2E;
    --border2:      #2A2A40;
    --neon-green:   #39FF14;
    --neon-pink:    #FF2D78;
    --neon-cyan:    #00F5FF;
    --neon-purple:  #BF5FFF;
    --neon-amber:   #FFB800;
    --text-primary: #E8E8F0;
    --text-mid:     #9090B8;
    --text-muted:   #4A4A6A;
    --font-display: 'Chakra Petch', monospace;
    --font-mono:    'Share Tech Mono', monospace;
    --font-body:    'DM Sans', sans-serif;
}

/* ─── Base ─── */
html, body, .stApp {
    background: var(--void) !important;
    font-family: var(--font-body);
    color: var(--text-primary);
}
.block-container {
    padding: 1.5rem 2.5rem 5rem;
    max-width: 1540px;
}

/* ─── Scanline overlay ─── */
.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    background: repeating-linear-gradient(
        0deg,
        transparent,
        transparent 2px,
        rgba(0, 245, 255, 0.012) 2px,
        rgba(0, 245, 255, 0.012) 4px
    );
    pointer-events: none;
    z-index: 9999;
}

/* ─── Sidebar ─── */
[data-testid="stSidebar"] {
    background: var(--void2) !important;
    border-right: 1px solid var(--border2) !important;
}
[data-testid="stSidebar"] * {
    color: var(--text-mid) !important;
}
[data-testid="stSidebar"] label {
    font-family: var(--font-mono) !important;
    font-size: 10px !important;
    letter-spacing: 1.8px;
    text-transform: uppercase;
    color: var(--text-muted) !important;
}
[data-testid="stSidebar"] [data-baseweb="select"] > div:first-child {
    background: var(--void3) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 2px !important;
}
[data-testid="stSidebar"] [data-baseweb="select"] span {
    color: var(--neon-green) !important;
    font-family: var(--font-mono) !important;
    font-size: 11px !important;
}
[data-testid="stSidebar"] [data-testid="stSlider"] > div > div > div {
    background: var(--neon-green) !important;
}
[data-testid="stSidebar"] [data-testid="stSlider"] > div > div > div > div {
    background: var(--void) !important;
    border: 2px solid var(--neon-green) !important;
    box-shadow: 0 0 8px var(--neon-green) !important;
}
[data-testid="stSidebar"] hr {
    border-color: var(--border2) !important;
}

/* ─── Section headers ─── */
h1, h2, h3, h4 {
    font-family: var(--font-display) !important;
    font-weight: 600 !important;
}
h1 {
    font-size: 2.2rem !important;
    letter-spacing: 3px;
    color: var(--text-primary) !important;
}
h3 {
    letter-spacing: 2px;
    color: var(--text-mid) !important;
    font-size: 0.75rem !important;
    text-transform: uppercase;
}

/* ─── Metric cards ─── */
[data-testid="stMetric"] {
    background: var(--void2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 3px !important;
    padding: 1rem 1.2rem !important;
    position: relative;
    overflow: hidden;
    transition: border-color 0.25s ease;
}
[data-testid="stMetric"]:hover {
    border-color: var(--neon-green) !important;
    box-shadow: 0 0 12px rgba(57, 255, 20, 0.12) !important;
}
[data-testid="stMetric"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--neon-green), transparent);
}
[data-testid="stMetricLabel"] {
    font-family: var(--font-mono) !important;
    font-size: 9px !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    color: var(--text-muted) !important;
}
[data-testid="stMetricValue"] {
    font-family: var(--font-display) !important;
    font-size: 1.9rem !important;
    font-weight: 700 !important;
    color: var(--neon-green) !important;
    letter-spacing: 1px;
}
[data-testid="stMetricDelta"] {
    font-family: var(--font-mono) !important;
    font-size: 10px !important;
}

/* ─── Section dividers ─── */
.section-head {
    display: flex;
    align-items: center;
    gap: 14px;
    margin: 2rem 0 1.2rem;
}
.section-head .num {
    font-family: var(--font-mono);
    font-size: 0.7rem;
    color: var(--neon-green);
    letter-spacing: 2px;
    opacity: 0.6;
    padding: 3px 7px;
    border: 1px solid var(--neon-green);
    border-radius: 2px;
    line-height: 1;
}
.section-head .title {
    font-family: var(--font-display);
    font-size: 0.85rem;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: var(--text-mid);
    font-weight: 600;
}
.section-head .line {
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, var(--border2), transparent);
}

/* ─── Chart containers ─── */
.chart-wrap {
    background: var(--void2);
    border: 1px solid var(--border);
    border-radius: 3px;
    padding: 0.25rem 0.25rem 0;
    margin-bottom: 1rem;
    transition: border-color 0.3s ease;
    position: relative;
}
.chart-wrap:hover {
    border-color: var(--border2);
}

/* ─── Tabs ─── */
[data-testid="stTabs"] [role="tablist"] {
    background: var(--void2) !important;
    border-bottom: 1px solid var(--border) !important;
    gap: 0 !important;
}
[data-testid="stTabs"] button[role="tab"] {
    font-family: var(--font-mono) !important;
    font-size: 10px !important;
    letter-spacing: 1.8px !important;
    text-transform: uppercase !important;
    color: var(--text-muted) !important;
    background: transparent !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    padding: 10px 18px !important;
    border-radius: 0 !important;
    transition: all 0.2s ease !important;
}
[data-testid="stTabs"] button[role="tab"]:hover {
    color: var(--neon-green) !important;
    border-bottom-color: var(--neon-green) !important;
}
[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    color: var(--neon-green) !important;
    border-bottom: 2px solid var(--neon-green) !important;
    background: transparent !important;
}

/* ─── Buttons ─── */
.stDownloadButton > button, .stButton > button {
    font-family: var(--font-mono) !important;
    font-size: 10px !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    background: transparent !important;
    color: var(--neon-green) !important;
    border: 1px solid var(--neon-green) !important;
    border-radius: 2px !important;
    padding: 6px 16px !important;
    transition: all 0.2s ease !important;
    box-shadow: none !important;
}
.stDownloadButton > button:hover, .stButton > button:hover {
    background: var(--neon-green) !important;
    color: var(--void) !important;
    box-shadow: 0 0 16px rgba(57, 255, 20, 0.35) !important;
}

/* ─── Dataframe ─── */
[data-testid="stDataFrame"] {
    border: 1px solid var(--border) !important;
    border-radius: 3px !important;
}
[data-testid="stDataFrame"] * {
    font-family: var(--font-mono) !important;
    font-size: 11px !important;
}

/* ─── Select/input widgets ─── */
[data-baseweb="select"] > div:first-child {
    background: var(--void3) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 2px !important;
}
.stSelectbox label, .stMultiSelect label, .stSlider label,
.stNumberInput label, .stTextInput label {
    font-family: var(--font-mono) !important;
    font-size: 10px !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
    color: var(--text-muted) !important;
}
[data-testid="stExpander"] {
    background: var(--void2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 3px !important;
}
[data-testid="stExpander"] summary {
    font-family: var(--font-mono) !important;
    font-size: 10px !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
    color: var(--text-muted) !important;
}

/* ─── Info/warning boxes ─── */
.stAlert {
    background: var(--void3) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 2px !important;
    font-family: var(--font-mono) !important;
    font-size: 11px !important;
    color: var(--text-mid) !important;
}

/* ─── Scrollbar ─── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: var(--void); }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: var(--neon-green); }

/* ─── Sidebar logo ─── */
.sidebar-brand {
    font-family: var(--font-display);
    font-size: 1.1rem;
    font-weight: 700;
    letter-spacing: 3px;
    color: #E8E8F0;
    margin-bottom: 4px;
}
.sidebar-sub {
    font-family: var(--font-mono);
    font-size: 9px;
    letter-spacing: 2px;
    color: #3A3A5A;
    text-transform: uppercase;
    margin-bottom: 20px;
}
.neon-dot {
    display: inline-block;
    width: 7px; height: 7px;
    border-radius: 50%;
    background: var(--neon-green);
    box-shadow: 0 0 8px var(--neon-green);
    margin-right: 8px;
}
</style>
""", unsafe_allow_html=True)


# ── DATA LOADING ──────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    path = os.path.join(os.path.dirname(__file__), "data", "spotify_songs.csv")
    if not os.path.exists(path):
        return pd.DataFrame()
    df = pd.read_csv(path)

    # Parse release year
    if "track_album_release_date" in df.columns:
        df["release_year"] = pd.to_datetime(
            df["track_album_release_date"], errors="coerce"
        ).dt.year

    # Normalise column names (TidyTuesday dataset)
    rename_map = {
        "track_name": "track_name",
        "track_artist": "track_artist",
        "track_popularity": "track_popularity",
        "playlist_genre": "playlist_genre",
        "playlist_subgenre": "playlist_subgenre",
    }
    return df


def _section(num: str, title: str):
    st.markdown(
        f'<div class="section-head">'
        f'<span class="num">{num}</span>'
        f'<span class="title">{title}</span>'
        f'<span class="line"></span>'
        f'</div>',
        unsafe_allow_html=True,
    )


def _chart(fig, key: str = ""):
    """Render a Plotly chart inside a styled wrapper."""
    st.plotly_chart(fig, use_container_width=True, key=key,
                    config={
                        "displaylogo": False,
                        "modeBarButtonsToRemove": ["select2d", "lasso2d"],
                        "toImageButtonOptions": {
                            "format": "png",
                            "filename": f"spotify_{key}",
                            "height": 600,
                            "width": 1200,
                            "scale": 2,
                        },
                    })


# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        '<div class="sidebar-brand">'
        '<span class="neon-dot"></span>SPOTIFY</div>'
        '<div class="sidebar-sub">TRACK ANALYSIS · TIDY TUESDAY</div>',
        unsafe_allow_html=True,
    )

    df_raw = load_data()

    if df_raw.empty:
        st.warning(
            "No dataset found.\n\n"
            "Place `spotify_songs.csv` inside the `data/` folder.\n\n"
            "Download:\n"
            "https://raw.githubusercontent.com/rfordatascience/tidytuesday/"
            "master/data/2020/2020-01-21/spotify_songs.csv"
        )
        st.stop()

    st.markdown("---")
    st.markdown("##### FILTERS")

    # Genre
    all_genres = sorted(df_raw["playlist_genre"].dropna().unique().tolist())
    sel_genres = st.multiselect(
        "Genre", options=all_genres, default=[],
        placeholder="All genres"
    )

    # Subgenre (reactive to genre)
    genre_pool = df_raw[df_raw["playlist_genre"].isin(sel_genres)] if sel_genres else df_raw
    all_subgenres = sorted(genre_pool["playlist_subgenre"].dropna().unique().tolist())
    sel_subgenres = st.multiselect(
        "Subgenre", options=all_subgenres, default=[],
        placeholder="All subgenres"
    )

    st.markdown("---")

    # Year range
    if "release_year" in df_raw.columns:
        years = df_raw["release_year"].dropna()
        yr_min, yr_max = int(years.min()), int(years.max())
        sel_years = st.slider(
            "Release Year", min_value=yr_min, max_value=yr_max,
            value=(yr_min, yr_max)
        )
    else:
        sel_years = (1900, 2025)

    # Popularity
    sel_pop = st.slider(
        "Popularity", min_value=0, max_value=100, value=(0, 100)
    )

    # Danceability
    sel_dance = st.slider(
        "Danceability", min_value=0.0, max_value=1.0,
        value=(0.0, 1.0), step=0.01
    )

    # Tempo
    tempo_vals = df_raw["tempo"].dropna()
    t_min, t_max = float(tempo_vals.min()), float(tempo_vals.max())
    sel_tempo = st.slider(
        "Tempo (BPM)", min_value=t_min, max_value=t_max,
        value=(t_min, t_max), step=1.0,
        format="%.0f"
    )

    st.markdown("---")

    # Top N
    top_n = st.selectbox("Top N (ranked charts)", options=[5, 10, 15, 20, 25], index=1)

    st.markdown("---")
    st.markdown(
        '<div style="font-family:\'Share Tech Mono\',monospace;font-size:9px;'
        'color:#3A3A5A;letter-spacing:1px;line-height:1.8">'
        'DATA: Spotify / TidyTuesday<br>'
        'WEEK: 2020-01-21<br>'
        'COLLECTOR: Charlie Thompson<br>'
        'RECORDS: ~32,000 tracks'
        '</div>',
        unsafe_allow_html=True,
    )


# ── APPLY FILTERS ─────────────────────────────────────────────────────────────
df = filters.apply_filters(
    df_raw,
    genres=sel_genres,
    subgenres=sel_subgenres,
    year_range=sel_years,
    popularity_range=sel_pop,
    danceability_range=sel_dance,
    tempo_range=sel_tempo,
)

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown(
    '<h1>🎧 SPOTIFY TRACK ANALYSIS</h1>'
    '<p style="font-family:\'Share Tech Mono\',monospace;font-size:11px;'
    'color:#4A4A6A;letter-spacing:2px;margin-top:-8px;margin-bottom:24px">'
    'TIDY TUESDAY · 2020 · AUDIO FEATURES & POPULARITY DYNAMICS'
    '</p>',
    unsafe_allow_html=True,
)

# ── KPI STRIP ─────────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5, k6 = st.columns(6)
total_tracks   = len(df)
total_artists  = df["track_artist"].nunique() if "track_artist" in df.columns else 0
genres_count   = df["playlist_genre"].nunique() if "playlist_genre" in df.columns else 0
avg_pop        = df["track_popularity"].mean() if "track_popularity" in df.columns else 0
avg_dance      = df["danceability"].mean() if "danceability" in df.columns else 0
avg_energy     = df["energy"].mean() if "energy" in df.columns else 0

k1.metric("TRACKS",     f"{total_tracks:,}")
k2.metric("ARTISTS",    f"{total_artists:,}")
k3.metric("GENRES",     f"{genres_count}")
k4.metric("AVG POP",    f"{avg_pop:.1f}")
k5.metric("AVG DANCE",  f"{avg_dance:.3f}")
k6.metric("AVG ENERGY", f"{avg_energy:.3f}")


# ── TABS ──────────────────────────────────────────────────────────────────────
tabs = st.tabs([
    "⬡ GENRE COMMAND",
    "⬡ AUDIO DNA",
    "⬡ TEMPO & MOOD",
    "⬡ POPULARITY",
    "⬡ DEEP FREQUENCY",
    "⬡ TRACK EXPLORER",
])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — GENRE COMMAND
# ══════════════════════════════════════════════════════════════════════════════
with tabs[0]:
    _section("01", "GENRE COMMAND")

    c1, c2 = st.columns([1, 1])
    with c1:
        fig = charts.bar_genre_popularity(df, top_n=top_n)
        _chart(fig, "genre_pop")
    with c2:
        fig = charts.stacked_subgenre(df, top_n=top_n)
        _chart(fig, "stacked_sub")

    st.markdown("---")

    fig = charts.radar_genre_fingerprint(df)
    _chart(fig, "radar_genre")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — AUDIO DNA
# ══════════════════════════════════════════════════════════════════════════════
with tabs[1]:
    _section("02", "AUDIO DNA")

    fig = charts.heatmap_audio_correlation(df)
    _chart(fig, "heatmap_corr")

    c1, c2 = st.columns([1, 1])
    with c1:
        fig = charts.box_audio_features(df)
        _chart(fig, "box_feat")
    with c2:
        fig = charts.scatter_dance_energy(df)
        _chart(fig, "scatter_de")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — TEMPO & MOOD
# ══════════════════════════════════════════════════════════════════════════════
with tabs[2]:
    _section("03", "TEMPO & MOOD")

    fig = charts.scatter_valence_dance(df)
    _chart(fig, "valence_dance")

    c1, c2 = st.columns([1, 1])
    with c1:
        fig = charts.hist_tempo(df)
        _chart(fig, "tempo_hist")
    with c2:
        fig = charts.scatter_acoustic_instr(df)
        _chart(fig, "acoustic_instr")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — POPULARITY ENGINE
# ══════════════════════════════════════════════════════════════════════════════
with tabs[3]:
    _section("04", "POPULARITY ENGINE")

    fig = charts.line_popularity_trend(df)
    _chart(fig, "pop_trend")

    c1, c2 = st.columns([1, 1])
    with c1:
        fig = charts.bar_top_artists(df, top_n=top_n)
        _chart(fig, "top_artists")
    with c2:
        fig = charts.scatter_loud_pop(df)
        _chart(fig, "loud_pop")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — DEEP FREQUENCY
# ══════════════════════════════════════════════════════════════════════════════
with tabs[4]:
    _section("05", "DEEP FREQUENCY")

    c1, c2 = st.columns([1, 1])
    with c1:
        fig = charts.box_dance_genre(df)
        _chart(fig, "dance_genre")
    with c2:
        fig = charts.pie_key_distribution(df)
        _chart(fig, "key_dist")

    c1, c2 = st.columns([1, 1])
    with c1:
        fig = charts.hist_duration(df)
        _chart(fig, "duration_hist")
    with c2:
        fig = charts.bar_mode_genre(df)
        _chart(fig, "mode_genre")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 6 — TRACK EXPLORER
# ══════════════════════════════════════════════════════════════════════════════
with tabs[5]:
    _section("06", "TRACK EXPLORER")

    # ── Summary table ─────────────────────────────────────────────────────────
    with st.expander("GENRE SUMMARY", expanded=True):
        if not df.empty and "playlist_genre" in df.columns:
            audio_cols = ["danceability", "energy", "valence",
                          "acousticness", "speechiness", "tempo",
                          "track_popularity"]
            available = [c for c in audio_cols if c in df.columns]
            summary = (
                df.groupby("playlist_genre")[available]
                .agg(["mean", "median", "std"])
                .round(3)
            )
            summary.columns = [f"{c}_{a}" for c, a in summary.columns]
            summary = summary.reset_index()
            st.dataframe(summary, use_container_width=True)

            csv_sum = summary.to_csv(index=False)
            st.download_button(
                "EXPORT GENRE SUMMARY →",
                data=csv_sum,
                file_name=f"spotify_genre_summary_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
            )

    # ── Track detail table ─────────────────────────────────────────────────────
    st.markdown("---")

    search_cols = ["track_name", "track_artist", "playlist_genre", "playlist_subgenre",
                   "track_popularity", "danceability", "energy", "valence",
                   "tempo", "release_year"]
    available_search = [c for c in search_cols if c in df.columns]

    c1, c2 = st.columns([3, 1])
    with c1:
        search_query = st.text_input("SEARCH TRACKS / ARTISTS", placeholder="type to filter...")
    with c2:
        sort_col = st.selectbox("SORT BY", options=available_search,
                                index=available_search.index("track_popularity")
                                if "track_popularity" in available_search else 0)

    display_df = df[available_search].copy()
    if search_query:
        mask = display_df.apply(
            lambda col: col.astype(str).str.contains(search_query, case=False, na=False)
        ).any(axis=1)
        display_df = display_df[mask]

    display_df = display_df.sort_values(sort_col, ascending=False).head(500)

    st.dataframe(
        display_df.reset_index(drop=True),
        use_container_width=True,
        height=380,
    )

    csv_tracks = display_df.to_csv(index=False)
    st.download_button(
        "EXPORT FILTERED TRACKS →",
        data=csv_tracks,
        file_name=f"spotify_filtered_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv",
    )

    # ── Audio feature spotlight ────────────────────────────────────────────────
    st.markdown("---")
    _section("06b", "AUDIO FEATURE SPOTLIGHT")

    if not df.empty and "track_name" in df.columns:
        track_options = df.sort_values("track_popularity", ascending=False)[
            "track_name"
        ].dropna().unique()[:200].tolist()
        chosen_track = st.selectbox("SELECT A TRACK", options=track_options)

        track_row = df[df["track_name"] == chosen_track].iloc[0] if any(df["track_name"] == chosen_track) else None

        if track_row is not None:
            feat_cols_radar = ["danceability", "energy", "valence",
                               "acousticness", "speechiness", "liveness",
                               "instrumentalness"]
            avail_feats = [f for f in feat_cols_radar if f in track_row.index]
            feat_vals = [float(track_row.get(f, 0)) for f in avail_feats]

            fig_track = go.Figure()
            feat_vals_closed = feat_vals + [feat_vals[0]]
            avail_feats_closed = avail_feats + [avail_feats[0]]

            fig_track.add_trace(go.Scatterpolar(
                r=feat_vals_closed,
                theta=avail_feats_closed,
                name=chosen_track,
                line=dict(color="#39FF14", width=2.5),
                fill="toself",
                fillcolor="rgba(57, 255, 20, 0.13)",
            ))

            fig_track.update_layout(
                polar=dict(
                    bgcolor="#0A0A12",
                    radialaxis=dict(
                        visible=True, range=[0, 1],
                        gridcolor="#1E1E2E", linecolor="#1E1E2E",
                        tickfont=dict(color="#4A4A6A", size=8),
                    ),
                    angularaxis=dict(
                        gridcolor="#1E1E2E", linecolor="#1E1E2E",
                        tickfont=dict(color="#9090B8", size=10),
                    ),
                ),
                paper_bgcolor="#0D0D14",
                title=dict(
                    text=f"AUDIO PROFILE · {chosen_track[:50].upper()}",
                    font=dict(family="'Chakra Petch', monospace",
                              size=13, color="#E8E8F0"),
                    x=0,
                ),
                height=400,
                font=dict(family="'Share Tech Mono', monospace", color="#9090B8"),
                hoverlabel=dict(
                    bgcolor="#12121C", bordercolor="#39FF14",
                    font=dict(family="'Share Tech Mono', monospace",
                              color="#E8E8F0", size=11),
                ),
            )

            c1, c2 = st.columns([1, 1])
            with c1:
                _chart(fig_track, "track_radar")
            with c2:
                meta_fields = ["track_artist", "playlist_genre", "playlist_subgenre",
                               "track_popularity", "tempo", "loudness",
                               "duration_ms", "release_year", "key", "mode"]
                avail_meta = [f for f in meta_fields if f in track_row.index]
                st.markdown(
                    '<div style="background:#0A0A12;border:1px solid #1E1E2E;'
                    'border-radius:3px;padding:1.2rem;font-family:\'Share Tech Mono\','
                    'monospace;font-size:11px;line-height:2.2;color:#9090B8">',
                    unsafe_allow_html=True,
                )
                for field in avail_meta:
                    val = track_row.get(field, "–")
                    if field == "duration_ms" and pd.notna(val):
                        val = f"{val / 60_000:.2f} min"
                    if field == "key":
                        KEY_NAMES = {0: "C", 1: "C♯", 2: "D", 3: "D♯", 4: "E",
                                     5: "F", 6: "F♯", 7: "G", 8: "G♯", 9: "A",
                                     10: "A♯", 11: "B"}
                        val = KEY_NAMES.get(int(val), val) if pd.notna(val) else "–"
                    if field == "mode":
                        val = "Major" if val == 1 else "Minor" if val == 0 else "–"
                    disp_label = field.upper().replace("_", " ")
                    st.markdown(
                        f'<span style="color:#3A3A5A">{disp_label}</span>'
                        f'<span style="float:right;color:#E8E8F0">{val}</span><br>',
                        unsafe_allow_html=True,
                    )
                st.markdown("</div>", unsafe_allow_html=True)
