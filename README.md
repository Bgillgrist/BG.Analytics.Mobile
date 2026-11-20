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

The national calculation uses completed FBS-vs-FBS games with scores,
including the postseason. Conference mode recalculates using
games where both teams are listed in the selected conference, excluding games
explicitly marked nonconference when that flag is available. It uses equal
weights and limits win margins to 7–24 points, preserving the winner and
keeping ties at zero. SRS fits home rating minus away rating.
The least-squares ratings are centered within each disconnected group. Teams
from disconnected groups have no head-to-head schedule basis for comparison.

Wins and losses use the same games as SRS. Ties count toward neither column.
BG.Rank starts with the fewest losses and uses SRS rank within each loss group.
For each spot, the best remaining team with exactly one more loss moves ahead
if its SRS rank is more than 10 places better.
