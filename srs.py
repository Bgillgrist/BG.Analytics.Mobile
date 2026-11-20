from collections import Counter, deque

import numpy as np
import pandas as pd


def bg_order(rankings):
    groups = {
        losses: deque(group.index)
        for losses, group in rankings.groupby("Losses", sort=True)
    }
    scores = rankings["SRS"]
    threshold = 0.75 * scores.std(ddof=0)
    order = []
    while groups:
        fewest = next(iter(groups))
        pick = fewest
        challenger = groups.get(fewest + 1)
        if challenger and scores.at[challenger[0]] - scores.at[groups[fewest][0]] > threshold:
            pick = fewest + 1
        order.append(groups[pick].popleft())
        if not groups[pick]:
            del groups[pick]
    return order


def apply_head_to_head(order, teams, results):
    spot = 0
    while spot + 1 < len(order):
        upper, lower = teams.at[order[spot]], teams.at[order[spot + 1]]
        if results[lower, upper] > results[upper, lower]:
            order[spot], order[spot + 1] = order[spot + 1], order[spot]
            spot += 2
        else:
            spot += 1
    return order


def rank_teams(games):
    teams = sorted(set(games.hometeam) | set(games.awayteam))
    index = {team: i for i, team in enumerate(teams)}
    matrix = np.zeros((len(games), len(teams)))
    rows = np.arange(len(games))
    matrix[rows, games.hometeam.map(index)] = 1
    matrix[rows, games.awayteam.map(index)] = -1
    margins = games.homepoints - games.awaypoints
    winners = [*games.loc[margins.gt(0), "hometeam"], *games.loc[margins.lt(0), "awayteam"]]
    losers = [*games.loc[margins.gt(0), "awayteam"], *games.loc[margins.lt(0), "hometeam"]]
    margins = np.sign(margins) * margins.abs().clip(7, 24)
    ratings = np.linalg.lstsq(matrix, margins, rcond=None)[0]
    rankings = pd.DataFrame({"Team": teams, "SRS": ratings})
    rankings = rankings.sort_values(["SRS", "Team"], ascending=[False, True]).reset_index(drop=True)
    rankings.insert(0, "SRS Rank", rankings.index + 1)
    rankings["Wins"] = rankings.Team.map(Counter(winners)).fillna(0).astype(int)
    rankings["Losses"] = rankings.Team.map(Counter(losers)).fillna(0).astype(int)
    results = Counter(zip(winners, losers))
    order = apply_head_to_head(bg_order(rankings), rankings.Team, results)
    rankings = rankings.loc[order].reset_index(drop=True)
    rankings.insert(0, "BG.Rank", rankings.index + 1)
    return rankings.round({"SRS": 2})
