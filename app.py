import os

import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text
from streamlit.errors import StreamlitSecretNotFoundError

from srs import rank_teams

st.set_page_config(page_title="Team Rankings", layout="centered")
st.title("Team Rankings")

try:
    url = os.getenv("NEON_DATABASE_URL") or st.secrets.get("NEON_DATABASE_URL")
except StreamlitSecretNotFoundError:
    url = None


@st.cache_resource
def engine(database_url):
    return create_engine(database_url, pool_pre_ping=True)


@st.cache_data(ttl=300)
def load(sql, **params):
    with engine(url).connect() as connection:
        return pd.read_sql(text(sql), connection, params=params)


FBS_GAMES = "completed IS TRUE AND LOWER(TRIM(homeclassification)) = 'fbs' AND LOWER(TRIM(awayclassification)) = 'fbs'"

try:
    if url:
        seasons = load(f"""
            SELECT DISTINCT season FROM public.game_data
            WHERE {FBS_GAMES} AND season IS NOT NULL ORDER BY season DESC
        """).season.tolist()
        if not seasons:
            st.info("No completed seasons available.")
            st.stop()
        season = st.selectbox("Season", seasons)
        columns = load("""
            SELECT column_name FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = 'game_data'
        """).column_name.tolist()
        conference_flag = "COALESCE(conferencegame, TRUE)" if "conferencegame" in columns else "TRUE"
        games = load(f"""
            SELECT DISTINCT id, hometeam, awayteam, homepoints, awaypoints,
                   TRIM(homeconference) AS homeconference, TRIM(awayconference) AS awayconference,
                   {conference_flag} AS conferencegame
            FROM public.game_data AS g
            WHERE season = :season AND {FBS_GAMES}
              AND homepoints IS NOT NULL AND awaypoints IS NOT NULL
              AND hometeam <> awayteam
        """, season=season)
    else:
        st.info("Preview with fictional scores")
        st.selectbox("Season", [2026])
        games = pd.DataFrame([
            ("Georgia", "Alabama", 31, 24, "SEC", "SEC"),
            ("Alabama", "Georgia", 27, 31, "SEC", "SEC"),
            ("Ohio State", "Michigan", 27, 17, "Big Ten", "Big Ten"),
            ("Michigan", "Ohio State", 20, 24, "Big Ten", "Big Ten"),
            ("Georgia", "Ohio State", 31, 30, "SEC", "Big Ten"),
        ], columns="hometeam awayteam homepoints awaypoints homeconference awayconference".split())
except Exception:
    st.error("Could not load game results. Check the server’s Neon connection and read permissions.")
    st.stop()

games = games.loc[~games.id.duplicated(keep=False)] if "id" in games else games
conferences = sorted(set(games.loc[games.homeconference.eq(games.awayconference), "homeconference"].dropna()) - {""})
conference = st.selectbox("Conference", [None, *conferences], format_func=lambda value: value or "All conferences")
if conference:
    intraconference = games.homeconference.eq(conference) & games.awayconference.eq(conference)
    games = games[intraconference & games.get("conferencegame", True)]
if games.empty:
    st.info("No completed games for this selection.")
    st.stop()

sensitivity = st.slider("Loss sensitivity", 0.0, 3.0, 0.75, 0.05)
st.markdown(
    '<div style="display:flex;justify-content:space-between;gap:1rem">'
    '<small>Team strength matters more</small>'
    '<small style="text-align:right">Fewer losses matter more</small></div>',
    unsafe_allow_html=True,
)
rankings = rank_teams(games, sensitivity)
st.caption(f"{len(games):,} completed FBS games · SRS in points")
st.dataframe(rankings, hide_index=True, column_config={"SRS": st.column_config.NumberColumn(format="%.2f")})
