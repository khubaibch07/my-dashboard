"""
charts.py — Plotly chart library for the Spotify Dashboard
Aesthetic: Neon-on-void · Midnight black · Electric pulse
All charts return plotly.graph_objects.Figure (downloadable via Plotly toolbar)
"""
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import scipy.stats as stats

# ── PALETTE ──────────────────────────────────────────────────────────────────
VOID        = "#050508"
VOID2       = "#0D0D14"
VOID3       = "#12121C"
PANEL       = "#0A0A12"
BORDER      = "#1E1E2E"

NEON_GREEN  = "#39FF14"
NEON_PINK   = "#FF2D78"
NEON_CYAN   = "#00F5FF"
NEON_PURPLE = "#BF5FFF"
NEON_AMBER  = "#FFB800"
NEON_CORAL  = "#FF6B35"
NEON_TEAL   = "#00E5A0"

DIM_GREEN   = "#1A7A09"
DIM_PINK    = "#7A1540"
DIM_CYAN    = "#006B7A"
DIM_PURPLE  = "#5A2A7A"

TEXT_PRIMARY   = "#E8E8F0"
TEXT_SECONDARY = "#7070A0"
TEXT_MUTED     = "#3A3A5A"

GENRE_PALETTE = {
    "pop":     NEON_PINK,
    "rap":     NEON_AMBER,
    "rock":    NEON_CORAL,
    "latin":   NEON_TEAL,
    "r&b":     NEON_PURPLE,
    "edm":     NEON_GREEN,
    "other":   NEON_CYAN,
}

FEATURE_COLORS = [
    NEON_GREEN, NEON_PINK, NEON_CYAN,
    NEON_PURPLE, NEON_AMBER, NEON_CORAL, NEON_TEAL
]

GENRE_LIST = ["pop", "rap", "rock", "latin", "r&b", "edm"]


def _rgba(hex_color: str, alpha: float) -> str:
    """Convert a 6-digit hex color + float alpha (0–1) to 'rgba(r,g,b,a)'.
    Plotly does NOT accept 8-digit hex strings for fillcolor/font color."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


def _base_layout(title: str = "", height: int = 480) -> dict:
    """Shared plotly layout dict — neon-on-void aesthetic."""
    return dict(
        title=dict(
            text=title,
            font=dict(family="'Chakra Petch', monospace", size=15,
                      color=TEXT_PRIMARY),
            x=0.0, xanchor="left", pad=dict(l=4, t=4),
        ),
        paper_bgcolor=VOID2,
        plot_bgcolor=PANEL,
        height=height,
        font=dict(family="'Share Tech Mono', monospace", color=TEXT_SECONDARY),
        margin=dict(l=52, r=24, t=56, b=48),
        xaxis=dict(
            gridcolor=BORDER, gridwidth=1,
            linecolor=BORDER, tickcolor=TEXT_MUTED,
            tickfont=dict(color=TEXT_SECONDARY, size=10),
            showgrid=True,
        ),
        yaxis=dict(
            gridcolor=BORDER, gridwidth=1,
            linecolor=BORDER, tickcolor=TEXT_MUTED,
            tickfont=dict(color=TEXT_SECONDARY, size=10),
            showgrid=True,
        ),
        legend=dict(
            bgcolor=VOID3, bordercolor=BORDER, borderwidth=1,
            font=dict(color=TEXT_SECONDARY, size=10),
        ),
        hoverlabel=dict(
            bgcolor=VOID3, bordercolor=NEON_GREEN,
            font=dict(family="'Share Tech Mono', monospace",
                      color=TEXT_PRIMARY, size=11),
        ),
    )


def _genre_color(genre: str) -> str:
    return GENRE_PALETTE.get(genre.lower(), NEON_CYAN)


# ── 1. POPULARITY BAR — genre ranking ────────────────────────────────────────
def bar_genre_popularity(df: pd.DataFrame, top_n: int = 10) -> go.Figure:
    if df.empty:
        return go.Figure()

    genre_stats = (
        df.groupby("playlist_genre")["track_popularity"]
        .agg(["mean", "count", "median"])
        .reset_index()
        .rename(columns={"mean": "avg_pop", "count": "tracks", "median": "med_pop"})
        .sort_values("avg_pop", ascending=True)
        .tail(top_n)
    )

    colors = [_genre_color(g) for g in genre_stats["playlist_genre"]]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=genre_stats["avg_pop"],
        y=genre_stats["playlist_genre"],
        orientation="h",
        marker=dict(
            color=colors,
            opacity=0.85,
            line=dict(color=[c for c in colors], width=1),
        ),
        customdata=genre_stats[["tracks", "med_pop"]].values,
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Avg Popularity: <b>%{x:.1f}</b><br>"
            "Tracks: <b>%{customdata[0]:,}</b><br>"
            "Median: <b>%{customdata[1]:.1f}</b>"
            "<extra></extra>"
        ),
    ))

    layout = _base_layout("01 · GENRE POPULARITY RANKING", 400)
    layout["xaxis"]["title"] = dict(
        text="Average Track Popularity", font=dict(color=TEXT_SECONDARY, size=11))
    layout["yaxis"]["showgrid"] = False
    layout["plot_bgcolor"] = PANEL
    fig.update_layout(**layout)

    # Neon glow effect on bars via shapes
    for i, row in genre_stats.iterrows():
        pass  # Plotly bars already carry color

    return fig


# ── 2. TRACK VOLUME — stacked subgenre breakdown ─────────────────────────────
def stacked_subgenre(df: pd.DataFrame, top_n: int = 8) -> go.Figure:
    if df.empty:
        return go.Figure()

    top_genres = df["playlist_genre"].value_counts().head(6).index.tolist()
    sub = df[df["playlist_genre"].isin(top_genres)]

    pivot = (
        sub.groupby(["playlist_genre", "playlist_subgenre"])
        .size()
        .reset_index(name="count")
    )
    # Keep top subgenres per genre
    top_subs = (
        pivot.groupby("playlist_subgenre")["count"]
        .sum()
        .nlargest(top_n)
        .index.tolist()
    )
    pivot = pivot[pivot["playlist_subgenre"].isin(top_subs)]
    genre_totals = pivot.groupby("playlist_genre")["count"].sum().sort_values()
    genre_order = genre_totals.index.tolist()

    fig = go.Figure()
    for i, sub_name in enumerate(top_subs):
        sub_data = pivot[pivot["playlist_subgenre"] == sub_name]
        sub_map = dict(zip(sub_data["playlist_genre"], sub_data["count"]))
        vals = [sub_map.get(g, 0) for g in genre_order]
        col = FEATURE_COLORS[i % len(FEATURE_COLORS)]
        fig.add_trace(go.Bar(
            name=sub_name,
            x=genre_order,
            y=vals,
            marker=dict(color=col, opacity=0.8,
                        line=dict(color=VOID, width=0.5)),
            hovertemplate=f"<b>{sub_name}</b><br>%{{x}}: %{{y:,}} tracks<extra></extra>",
        ))

    layout = _base_layout("02 · TRACK VOLUME BY SUBGENRE", 420)
    layout["barmode"] = "stack"
    layout["xaxis"]["title"] = dict(text="Genre", font=dict(color=TEXT_SECONDARY))
    layout["yaxis"]["title"] = dict(text="Track Count", font=dict(color=TEXT_SECONDARY))
    layout["showlegend"] = True
    fig.update_layout(**layout)
    return fig


# ── 3. GENRE RADAR — audio feature fingerprint ───────────────────────────────
def radar_genre_fingerprint(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return go.Figure()

    features = ["danceability", "energy", "valence",
                "acousticness", "instrumentalness", "speechiness", "liveness"]
    genres = df["playlist_genre"].unique()[:6]

    fig = go.Figure()
    for genre in genres:
        sub = df[df["playlist_genre"] == genre]
        means = [sub[f].mean() for f in features]
        means.append(means[0])  # close the polygon

        col = _genre_color(genre)
        fig.add_trace(go.Scatterpolar(
            r=means,
            theta=features + [features[0]],
            name=genre.upper(),
            line=dict(color=col, width=2),
            fill="toself",
            fillcolor=col,
            opacity=0.18,
            hovertemplate=f"<b>{genre.upper()}</b><br>%{{theta}}: %{{r:.3f}}<extra></extra>",
        ))

    layout = _base_layout("03 · GENRE AUDIO FINGERPRINT", 500)
    layout["polar"] = dict(
        bgcolor=PANEL,
        radialaxis=dict(
            visible=True, range=[0, 1],
            gridcolor=BORDER, linecolor=BORDER,
            tickfont=dict(color=TEXT_MUTED, size=8),
        ),
        angularaxis=dict(
            gridcolor=BORDER, linecolor=BORDER,
            tickfont=dict(color=TEXT_SECONDARY, size=10),
        ),
    )
    layout.pop("xaxis", None)
    layout.pop("yaxis", None)
    fig.update_layout(**layout)
    return fig


# ── 4. CORRELATION HEATMAP — audio DNA ───────────────────────────────────────
def heatmap_audio_correlation(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return go.Figure()

    cols = ["danceability", "energy", "loudness", "speechiness",
            "acousticness", "instrumentalness", "liveness", "valence",
            "tempo", "track_popularity"]
    clean = df[cols].dropna()
    corr = clean.corr()

    # Custom neon colorscale: dark void → green
    colorscale = [
        [0.0, NEON_PINK],
        [0.25, DIM_PINK],
        [0.5, VOID3],
        [0.75, DIM_GREEN],
        [1.0, NEON_GREEN],
    ]

    fig = go.Figure(go.Heatmap(
        z=corr.values,
        x=corr.columns.tolist(),
        y=corr.index.tolist(),
        colorscale=colorscale,
        zmid=0,
        text=[[f"{v:.2f}" for v in row] for row in corr.values],
        texttemplate="%{text}",
        textfont=dict(size=9, color=TEXT_PRIMARY),
        hovertemplate="<b>%{x} × %{y}</b><br>r = %{z:.3f}<extra></extra>",
        colorbar=dict(
            tickfont=dict(color=TEXT_SECONDARY, size=9),
            outlinecolor=BORDER, outlinewidth=1,
            bgcolor=VOID2,
        ),
    ))

    layout = _base_layout("04 · AUDIO FEATURE CORRELATION MATRIX", 520)
    layout["xaxis"]["tickangle"] = -40
    layout["xaxis"]["showgrid"] = False
    layout["yaxis"]["showgrid"] = False
    fig.update_layout(**layout)
    return fig


# ── 5. BOX — feature distributions ───────────────────────────────────────────
def box_audio_features(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return go.Figure()

    features = ["danceability", "energy", "valence",
                "acousticness", "speechiness", "liveness", "instrumentalness"]
    fig = go.Figure()
    for i, feat in enumerate(features):
        col = FEATURE_COLORS[i % len(FEATURE_COLORS)]
        vals = df[feat].dropna()
        fig.add_trace(go.Box(
            y=vals,
            name=feat.capitalize(),
            marker=dict(color=col, opacity=0.7, size=3,
                        outliercolor=col),
            line=dict(color=col, width=1.5),
            fillcolor=_rgba(col, 0.13),
            boxmean="sd",
            hovertemplate=f"<b>{feat}</b><br>%{{y:.3f}}<extra></extra>",
        ))

    layout = _base_layout("05 · AUDIO FEATURE DISTRIBUTIONS", 460)
    layout["yaxis"]["title"] = dict(text="Feature Value (0–1)", font=dict(color=TEXT_SECONDARY))
    layout["showlegend"] = False
    fig.update_layout(**layout)
    return fig


# ── 6. SCATTER — danceability vs energy, coloured by genre ───────────────────
def scatter_dance_energy(df: pd.DataFrame, max_pts: int = 3000) -> go.Figure:
    if df.empty:
        return go.Figure()

    sample = df.sample(min(max_pts, len(df)), random_state=42)
    fig = go.Figure()

    for genre in sample["playlist_genre"].unique():
        sub = sample[sample["playlist_genre"] == genre]
        col = _genre_color(genre)
        fig.add_trace(go.Scatter(
            x=sub["danceability"],
            y=sub["energy"],
            mode="markers",
            name=genre.upper(),
            marker=dict(
                color=col, size=5, opacity=0.55,
                line=dict(width=0),
            ),
            customdata=sub[["track_name", "track_artist", "track_popularity"]].values,
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "%{customdata[1]}<br>"
                "Dance: %{x:.2f} · Energy: %{y:.2f}<br>"
                "Pop: %{customdata[2]}"
                "<extra></extra>"
            ),
        ))

    layout = _base_layout("06 · DANCEABILITY × ENERGY", 480)
    layout["xaxis"]["title"] = dict(text="Danceability", font=dict(color=TEXT_SECONDARY))
    layout["yaxis"]["title"] = dict(text="Energy", font=dict(color=TEXT_SECONDARY))
    fig.update_layout(**layout)
    return fig


# ── 7. SCATTER — valence vs danceability · mood quadrants ────────────────────
def scatter_valence_dance(df: pd.DataFrame, max_pts: int = 2500) -> go.Figure:
    if df.empty:
        return go.Figure()

    sample = df.sample(min(max_pts, len(df)), random_state=7)
    fig = go.Figure()

    # Quadrant shading
    quadrant_fills = [
        dict(x0=0, x1=0.5, y0=0.5, y1=1.0, label="Turbulent/Intense", col=NEON_PINK),
        dict(x0=0.5, x1=1.0, y0=0.5, y1=1.0, label="Happy/Euphoric",  col=NEON_GREEN),
        dict(x0=0, x1=0.5, y0=0.0, y1=0.5,   label="Sad/Depressing",  col=NEON_PURPLE),
        dict(x0=0.5, x1=1.0, y0=0.0, y1=0.5, label="Chill/Peaceful",  col=NEON_CYAN),
    ]
    for q in quadrant_fills:
        fig.add_shape(type="rect",
            x0=q["x0"], x1=q["x1"], y0=q["y0"], y1=q["y1"],
            fillcolor=_rgba(q["col"], 0.04), line=dict(width=0))
        fig.add_annotation(
            x=(q["x0"] + q["x1"]) / 2, y=(q["y0"] + q["y1"]) / 2,
            text=q["label"], showarrow=False,
            font=dict(color=_rgba(q["col"], 0.33), size=10,
                      family="'Chakra Petch', monospace"),
        )

    for genre in sample["playlist_genre"].unique():
        sub = sample[sample["playlist_genre"] == genre]
        col = _genre_color(genre)
        fig.add_trace(go.Scatter(
            x=sub["valence"],
            y=sub["danceability"],
            mode="markers",
            name=genre.upper(),
            marker=dict(color=col, size=5, opacity=0.5, line=dict(width=0)),
            customdata=sub[["track_name", "track_artist"]].values,
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "%{customdata[1]}<br>"
                "Valence: %{x:.2f} · Dance: %{y:.2f}"
                "<extra></extra>"
            ),
        ))

    # Quadrant lines
    for v in [0.5]:
        fig.add_hline(y=v, line=dict(color=BORDER, width=1, dash="dot"))
        fig.add_vline(x=v, line=dict(color=BORDER, width=1, dash="dot"))

    layout = _base_layout("07 · MOOD MAP: VALENCE × DANCEABILITY", 500)
    layout["xaxis"]["title"] = dict(text="Valence (Positivity)", font=dict(color=TEXT_SECONDARY))
    layout["yaxis"]["title"] = dict(text="Danceability", font=dict(color=TEXT_SECONDARY))
    fig.update_layout(**layout)
    return fig


# ── 8. HISTOGRAM — tempo distribution by genre ───────────────────────────────
def hist_tempo(df: pd.DataFrame) -> go.Figure:
    if df.empty or "tempo" not in df.columns:
        return go.Figure()

    fig = go.Figure()
    for genre in df["playlist_genre"].unique():
        sub = df[df["playlist_genre"] == genre]["tempo"].dropna()
        col = _genre_color(genre)
        fig.add_trace(go.Histogram(
            x=sub,
            name=genre.upper(),
            nbinsx=50,
            marker=dict(color=col, opacity=0.55, line=dict(color=VOID, width=0.3)),
            hovertemplate=f"<b>{genre.upper()}</b><br>BPM: %{{x}}<br>Count: %{{y}}<extra></extra>",
        ))

    # BPM zone annotations
    for bpm, label in [(60, "Slow"), (120, "Mid"), (150, "Fast")]:
        fig.add_vline(x=bpm, line=dict(color=TEXT_MUTED, width=1, dash="dash"))
        fig.add_annotation(x=bpm + 2, y=0, yref="paper", text=label, showarrow=False,
                           font=dict(color=TEXT_MUTED, size=9), yanchor="bottom")

    layout = _base_layout("08 · TEMPO DISTRIBUTION BY GENRE (BPM)", 440)
    layout["barmode"] = "overlay"
    layout["xaxis"]["title"] = dict(text="Tempo (BPM)", font=dict(color=TEXT_SECONDARY))
    layout["yaxis"]["title"] = dict(text="Track Count", font=dict(color=TEXT_SECONDARY))
    fig.update_layout(**layout)
    return fig


# ── 9. LINE — popularity trend over release years ────────────────────────────
def line_popularity_trend(df: pd.DataFrame) -> go.Figure:
    if df.empty or "release_year" not in df.columns:
        return go.Figure()

    trend = (
        df[df["track_popularity"] > 0]
        .groupby("release_year")["track_popularity"]
        .agg(["mean", "median", "std", "count"])
        .reset_index()
        .query("count >= 10")
        .sort_values("release_year")
    )
    if trend.empty:
        return go.Figure()

    fig = go.Figure()

    # Std dev band
    fig.add_trace(go.Scatter(
        x=pd.concat([trend["release_year"], trend["release_year"][::-1]]),
        y=pd.concat([trend["mean"] + trend["std"],
                     (trend["mean"] - trend["std"])[::-1]]),
        fill="toself",
        fillcolor=_rgba(NEON_GREEN, 0.07),
        line=dict(color="rgba(0,0,0,0)"),
        name="±1 std",
        showlegend=True,
        hoverinfo="skip",
    ))

    # Median line
    fig.add_trace(go.Scatter(
        x=trend["release_year"], y=trend["median"],
        mode="lines",
        line=dict(color=NEON_PURPLE, width=1.5, dash="dot"),
        name="Median",
        hovertemplate="Year: %{x}<br>Median: %{y:.1f}<extra></extra>",
    ))

    # Mean line + markers
    fig.add_trace(go.Scatter(
        x=trend["release_year"], y=trend["mean"],
        mode="lines+markers",
        line=dict(color=NEON_GREEN, width=2.5),
        marker=dict(color=NEON_GREEN, size=6,
                    line=dict(color=VOID, width=1.5)),
        name="Mean",
        hovertemplate="Year: %{x}<br>Mean Pop: %{y:.1f}<extra></extra>",
    ))

    layout = _base_layout("09 · POPULARITY TREND BY RELEASE YEAR", 460)
    layout["xaxis"]["title"] = dict(text="Release Year", font=dict(color=TEXT_SECONDARY))
    layout["yaxis"]["title"] = dict(text="Track Popularity (0–100)", font=dict(color=TEXT_SECONDARY))
    fig.update_layout(**layout)
    return fig


# ── 10. BAR — top artists by avg popularity ──────────────────────────────────
def bar_top_artists(df: pd.DataFrame, top_n: int = 15) -> go.Figure:
    if df.empty or "track_artist" not in df.columns:
        return go.Figure()

    artist_stats = (
        df[df["track_popularity"] > 0]
        .groupby("track_artist")
        .agg(avg_pop=("track_popularity", "mean"),
             track_count=("track_popularity", "count"))
        .query("track_count >= 3")
        .sort_values("avg_pop", ascending=True)
        .tail(top_n)
        .reset_index()
    )

    # Color by avg popularity
    pops = artist_stats["avg_pop"].values
    pmin, pmax = pops.min(), pops.max()

    def pop_color(p):
        t = (p - pmin) / (pmax - pmin + 1e-9)
        r = int(0x3A + t * (0xFF - 0x3A))
        g = int(0xFF * t + 0x14 * (1 - t))
        return f"#{r:02x}{g:02x}14"

    colors = [pop_color(p) for p in pops]

    fig = go.Figure(go.Bar(
        x=artist_stats["avg_pop"],
        y=artist_stats["track_artist"],
        orientation="h",
        marker=dict(color=colors, line=dict(color=VOID, width=0.5)),
        customdata=artist_stats["track_count"].values,
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Avg Popularity: <b>%{x:.1f}</b><br>"
            "Tracks: <b>%{customdata}</b>"
            "<extra></extra>"
        ),
    ))

    layout = _base_layout(f"10 · TOP {top_n} ARTISTS BY POPULARITY", max(380, top_n * 28))
    layout["xaxis"]["title"] = dict(text="Average Popularity", font=dict(color=TEXT_SECONDARY))
    layout["yaxis"]["showgrid"] = False
    layout["yaxis"]["tickfont"] = dict(color=TEXT_SECONDARY, size=9)
    fig.update_layout(**layout)
    return fig


# ── 11. SCATTER — loudness vs popularity ─────────────────────────────────────
def scatter_loud_pop(df: pd.DataFrame, max_pts: int = 3000) -> go.Figure:
    if df.empty:
        return go.Figure()

    sample = df[df["track_popularity"] > 0].sample(
        min(max_pts, len(df)), random_state=42)

    fig = go.Figure()
    for genre in sample["playlist_genre"].unique():
        sub = sample[sample["playlist_genre"] == genre]
        col = _genre_color(genre)
        fig.add_trace(go.Scatter(
            x=sub["loudness"],
            y=sub["track_popularity"],
            mode="markers",
            name=genre.upper(),
            marker=dict(color=col, size=4, opacity=0.45, line=dict(width=0)),
            customdata=sub[["track_name", "track_artist"]].values,
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "%{customdata[1]}<br>"
                "Loudness: %{x:.1f} dB<br>"
                "Popularity: %{y}"
                "<extra></extra>"
            ),
        ))

    layout = _base_layout("11 · LOUDNESS × POPULARITY", 460)
    layout["xaxis"]["title"] = dict(text="Loudness (dB)", font=dict(color=TEXT_SECONDARY))
    layout["yaxis"]["title"] = dict(text="Popularity (0–100)", font=dict(color=TEXT_SECONDARY))
    fig.update_layout(**layout)
    return fig


# ── 12. SCATTER — acousticness vs instrumentalness ───────────────────────────
def scatter_acoustic_instr(df: pd.DataFrame, max_pts: int = 2500) -> go.Figure:
    if df.empty:
        return go.Figure()

    sample = df.sample(min(max_pts, len(df)), random_state=9)
    fig = go.Figure()
    for genre in sample["playlist_genre"].unique():
        sub = sample[sample["playlist_genre"] == genre]
        col = _genre_color(genre)
        fig.add_trace(go.Scatter(
            x=sub["acousticness"],
            y=sub["instrumentalness"],
            mode="markers",
            name=genre.upper(),
            marker=dict(color=col, size=4, opacity=0.45, line=dict(width=0)),
            hovertemplate=(
                "<b>%{text}</b><br>"
                "Acoustic: %{x:.2f}<br>"
                "Instrumental: %{y:.2f}"
                "<extra></extra>"
            ),
            text=sub["track_name"].fillna("Unknown"),
        ))

    layout = _base_layout("12 · ACOUSTICNESS × INSTRUMENTALNESS", 460)
    layout["xaxis"]["title"] = dict(text="Acousticness", font=dict(color=TEXT_SECONDARY))
    layout["yaxis"]["title"] = dict(text="Instrumentalness", font=dict(color=TEXT_SECONDARY))
    fig.update_layout(**layout)
    return fig


# ── 13. BOX — danceability by genre ──────────────────────────────────────────
def box_dance_genre(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return go.Figure()

    genres = df["playlist_genre"].unique()
    fig = go.Figure()
    for genre in genres:
        sub = df[df["playlist_genre"] == genre]["danceability"].dropna()
        col = _genre_color(genre)
        fig.add_trace(go.Box(
            y=sub,
            name=genre.upper(),
            marker=dict(color=col, opacity=0.7, size=3),
            line=dict(color=col, width=2),
            fillcolor=_rgba(col, 0.10),
            boxmean=True,
            hovertemplate=f"<b>{genre.upper()}</b><br>Dance: %{{y:.3f}}<extra></extra>",
        ))

    layout = _base_layout("13 · DANCEABILITY DISTRIBUTION BY GENRE", 440)
    layout["yaxis"]["title"] = dict(text="Danceability", font=dict(color=TEXT_SECONDARY))
    layout["showlegend"] = False
    fig.update_layout(**layout)
    return fig


# ── 14. PIE — key distribution ───────────────────────────────────────────────
def pie_key_distribution(df: pd.DataFrame) -> go.Figure:
    if df.empty or "key" not in df.columns:
        return go.Figure()

    KEY_NAMES = {0: "C", 1: "C♯", 2: "D", 3: "D♯", 4: "E", 5: "F",
                 6: "F♯", 7: "G", 8: "G♯", 9: "A", 10: "A♯", 11: "B"}
    key_counts = df["key"].value_counts().reset_index()
    key_counts.columns = ["key", "count"]
    key_counts["key_name"] = key_counts["key"].map(KEY_NAMES)

    colors = [NEON_GREEN, NEON_PINK, NEON_CYAN, NEON_PURPLE, NEON_AMBER,
              NEON_CORAL, NEON_TEAL, "#FF9B00", "#00B4D8", "#7B2FBE",
              "#E63946", "#4CC9F0"]

    fig = go.Figure(go.Pie(
        labels=key_counts["key_name"],
        values=key_counts["count"],
        marker=dict(colors=colors[:len(key_counts)],
                    line=dict(color=VOID, width=2)),
        hole=0.45,
        textfont=dict(family="'Share Tech Mono', monospace", size=10, color=VOID),
        hovertemplate="<b>Key %{label}</b><br>%{value:,} tracks<br>%{percent}<extra></extra>",
    ))

    layout = _base_layout("14 · MUSICAL KEY DISTRIBUTION", 420)
    layout.pop("xaxis", None)
    layout.pop("yaxis", None)
    layout["annotations"] = [dict(
        text="KEY", x=0.5, y=0.5, font=dict(
            size=14, color=TEXT_SECONDARY, family="'Chakra Petch', monospace"),
        showarrow=False
    )]
    fig.update_layout(**layout)
    return fig


# ── 15. HISTOGRAM — track duration ───────────────────────────────────────────
def hist_duration(df: pd.DataFrame) -> go.Figure:
    if df.empty or "duration_ms" not in df.columns:
        return go.Figure()

    dur_min = df["duration_ms"] / 60_000
    dur_min = dur_min[(dur_min > 0.5) & (dur_min < 10)]

    fig = go.Figure(go.Histogram(
        x=dur_min,
        nbinsx=60,
        marker=dict(
            color=NEON_CYAN,
            opacity=0.7,
            line=dict(color=VOID, width=0.3)
        ),
        hovertemplate="Duration: %{x:.1f} min<br>Count: %{y}<extra></extra>",
    ))

    fig.add_vline(x=dur_min.mean(), line=dict(color=NEON_GREEN, width=2, dash="dash"))
    fig.add_annotation(x=dur_min.mean() + 0.1, y=0, yref="paper",
                       text=f"Avg: {dur_min.mean():.1f} min",
                       showarrow=False,
                       font=dict(color=NEON_GREEN, size=10, family="'Share Tech Mono', monospace"),
                       yanchor="bottom")

    layout = _base_layout("15 · TRACK DURATION DISTRIBUTION", 420)
    layout["xaxis"]["title"] = dict(text="Duration (minutes)", font=dict(color=TEXT_SECONDARY))
    layout["yaxis"]["title"] = dict(text="Track Count", font=dict(color=TEXT_SECONDARY))
    fig.update_layout(**layout)
    return fig


# ── 16. GROUPED BAR — mode (major/minor) by genre ────────────────────────────
def bar_mode_genre(df: pd.DataFrame) -> go.Figure:
    if df.empty or "mode" not in df.columns:
        return go.Figure()

    mode_map = {1: "Major", 0: "Minor"}
    df = df.copy()
    df["mode_label"] = df["mode"].map(mode_map)

    pivot = (
        df.groupby(["playlist_genre", "mode_label"])
        .size()
        .reset_index(name="count")
    )
    genres = pivot["playlist_genre"].unique()

    fig = go.Figure()
    for mode, col in [("Major", NEON_GREEN), ("Minor", NEON_PINK)]:
        sub = pivot[pivot["mode_label"] == mode]
        sub_map = dict(zip(sub["playlist_genre"], sub["count"]))
        fig.add_trace(go.Bar(
            name=mode,
            x=[g for g in genres],
            y=[sub_map.get(g, 0) for g in genres],
            marker=dict(color=col, opacity=0.8, line=dict(color=VOID, width=0.5)),
            hovertemplate=f"<b>{mode}</b><br>%{{x}}: %{{y:,}} tracks<extra></extra>",
        ))

    layout = _base_layout("16 · MAJOR vs MINOR BY GENRE", 420)
    layout["barmode"] = "group"
    layout["xaxis"]["title"] = dict(text="Genre", font=dict(color=TEXT_SECONDARY))
    layout["yaxis"]["title"] = dict(text="Track Count", font=dict(color=TEXT_SECONDARY))
    fig.update_layout(**layout)
    return fig
