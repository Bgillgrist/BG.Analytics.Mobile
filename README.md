# BG.Analytics.Mobile

A one-page Streamlit scoreboard for season SRS rankings.

```sh
python -m pip install -r requirements.txt
streamlit run app.py
```

Without credentials, the app opens with fictional scores. For live results, set
`NEON_DATABASE_URL` in the server environment or Streamlit secrets. Use a
dedicated Neon role with read access to the required `public.game_data` columns
and TLS with certificate verification.

The national calculation uses completed games with scores across all
classifications and includes the postseason. Conference mode recalculates using
games where both teams are listed in the selected conference, excluding games
explicitly marked nonconference when that flag is available. It uses equal
weights and raw margins. SRS fits home rating minus away rating plus one shared
home-field term. Neutral sites and unknown venues contribute zero to that term.
The least-squares ratings are centered within each disconnected group. Teams
from disconnected groups have no head-to-head schedule basis for comparison.
Home-field advantage displays as unavailable when the results cannot identify it.
