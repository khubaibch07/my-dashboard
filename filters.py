"""
filters.py — Filter logic for the Spotify Dashboard
"""
import pandas as pd


def apply_filters(
    df: pd.DataFrame,
    genres: list,
    subgenres: list,
    year_range: tuple,
    popularity_range: tuple,
    danceability_range: tuple,
    tempo_range: tuple,
) -> pd.DataFrame:
    out = df.copy()

    if genres:
        out = out[out["playlist_genre"].isin(genres)]
    if subgenres:
        out = out[out["playlist_subgenre"].isin(subgenres)]
    if year_range and "release_year" in out.columns:
        out = out[
            (out["release_year"] >= year_range[0]) &
            (out["release_year"] <= year_range[1])
        ]
    if popularity_range:
        out = out[
            (out["track_popularity"] >= popularity_range[0]) &
            (out["track_popularity"] <= popularity_range[1])
        ]
    if danceability_range:
        out = out[
            (out["danceability"] >= danceability_range[0]) &
            (out["danceability"] <= danceability_range[1])
        ]
    if tempo_range:
        out = out[
            (out["tempo"] >= tempo_range[0]) &
            (out["tempo"] <= tempo_range[1])
        ]
    return out
