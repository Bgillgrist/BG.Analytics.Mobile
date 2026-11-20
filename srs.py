import numpy as np
import pandas as pd


def rank_teams(games):
    teams = sorted(set(games.hometeam) | set(games.awayteam))
    index = {team: i for i, team in enumerate(teams)}
    matrix = np.zeros((len(games), len(teams)))
    rows = np.arange(len(games))
    matrix[rows, games.hometeam.map(index)] = 1
    matrix[rows, games.awayteam.map(index)] = -1
    margins = games.homepoints - games.awaypoints
    margins = np.sign(margins) * margins.abs().clip(7, 24)
    ratings = np.linalg.lstsq(matrix, margins, rcond=None)[0]
    rankings = pd.DataFrame({"Team": teams, "SRS": ratings.round(2)})
    rankings = rankings.sort_values(["SRS", "Team"], ascending=[False, True]).reset_index(drop=True)
    rankings.insert(0, "Rank", rankings.index + 1)
    return rankings
