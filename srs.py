import numpy as np
import pandas as pd


def rank_teams(games):
    teams = sorted(set(games.hometeam) | set(games.awayteam))
    index = {team: i for i, team in enumerate(teams)}
    matrix = np.zeros((len(games), len(teams) + 1))
    rows = np.arange(len(games))
    matrix[rows, games.hometeam.map(index)] = 1
    matrix[rows, games.awayteam.map(index)] = -1
    matrix[:, -1] = (~games.neutralsite.fillna(True)).astype(int)
    margins = games.homepoints - games.awaypoints
    margins = np.sign(margins) * margins.abs().clip(7, 24)
    solution, _, rank, _ = np.linalg.lstsq(matrix, margins, rcond=None)
    identifiable = rank > np.linalg.matrix_rank(matrix[:, :-1])
    ratings = solution[:-1] if identifiable else np.linalg.lstsq(matrix[:, :-1], margins, rcond=None)[0]
    rankings = pd.DataFrame({"Team": teams, "SRS": ratings.round(2)})
    rankings = rankings.sort_values(["SRS", "Team"], ascending=[False, True]).reset_index(drop=True)
    rankings.insert(0, "Rank", rankings.index + 1)
    return rankings, float(solution[-1]) if identifiable else None
