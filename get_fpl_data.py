import requests
import json
import pandas as pd

BASE_URL = "https://fantasy.premierleague.com/api/"

def load_player_names(filename="/Users/jsimpson/Projects/personal/python_scripts/fpl_api_data_pred/players.json"):
    with open(filename, "r") as f:
        return json.load(f)

def get_bootstrap_static():
    return requests.get(BASE_URL + "bootstrap-static/").json()

def get_fixtures():
    return requests.get(BASE_URL + "fixtures/").json()

def map_names_to_ids_and_form(player_names, elements):
    name_to_info = {}
    for player in elements:
        full_name = f"{player['first_name']} {player['second_name']}"
        if full_name in player_names:
            name_to_info[full_name] = {
                "id": player["id"],
                "team_id": player["team"],
                "form_by_round": player["form"],
                "full_data": player
            }
    return name_to_info

def get_team_mapping(teams):
    return {team["id"]: team["name"] for team in teams}

def build_fixture_lookup(fixtures):
    lookup = {}
    for fixture in fixtures:
        kickoff = fixture["kickoff_time"]
        if kickoff is None:
            continue
        kickoff = pd.to_datetime(kickoff)
        lookup[(fixture["team_h"], fixture["team_a"], kickoff, True)] = fixture["team_h_difficulty"]
        lookup[(fixture["team_a"], fixture["team_h"], kickoff, False)] = fixture["team_a_difficulty"]
    return lookup

def get_form_by_round(elements):
    form_by_player_id = {}
    for player in elements:
        player_id = player["id"]
        history_past = player.get("ep_next")
        form_by_player_id[player_id] = player["form"]
    return form_by_player_id

def get_player_match_data(player_id, player_team_id, team_mapping, fixture_lookup):
    url = BASE_URL + f"element-summary/{player_id}/"
    data = requests.get(url).json()
    history = data["history"]

    matches = []
    for match in history:
        kickoff_time = match["kickoff_time"]
        if kickoff_time is None:
            continue
        kickoff = pd.to_datetime(kickoff_time)
        opponent_id = match["opponent_team"]
        was_home = match["was_home"]
        round_number = match["round"]

        fdr = fixture_lookup.get((player_team_id, opponent_id, kickoff, was_home), None)

        matches.append({
            "kickoff_time": kickoff,
            "gameweek": round_number,
            "opponent_team": team_mapping.get(opponent_id, f"Team {opponent_id}"),
            "was_home": was_home,
            "team_difficulty": fdr,
            "points": match["total_points"],
            "minutes": match["minutes"],
            "goals_scored": match["goals_scored"],
            "assists": match["assists"],
            "bps": match["bps"],
            "bonus": match["bonus"],
            "clean_sheets": match["clean_sheets"],
            "yellow_cards": match["yellow_cards"],
            "red_cards": match["red_cards"],
            "expected_goals": match.get("expected_goals"),
            "expected_assists": match.get("expected_assists"),
            "expected_goal_involvements": match.get("expected_goal_involvements"),
            "influence": match["influence"],
            "creativity": match["creativity"],
            "threat": match["threat"],
            "ict_index": match["ict_index"]
        })

    df = pd.DataFrame(matches)
    df.set_index("kickoff_time", inplace=True)
    df.sort_index(inplace=True)

    # Compute 30-day rolling average of total points as form
    df["form"] = df["points"].rolling("30D").mean().fillna(0)
    df.team_name = team_mapping.get(player_team_id, f"Team {player_team_id}")
    return df

def main():
    player_names = load_player_names()
    bootstrap = get_bootstrap_static()
    fixtures = get_fixtures()

    elements = bootstrap["elements"]
    teams = bootstrap["teams"]

    team_mapping = get_team_mapping(teams)
    fixture_lookup = build_fixture_lookup(fixtures)
    name_to_info = map_names_to_ids_and_form(player_names, elements)

    player_dataframes = {}

    for name, info in name_to_info.items():
        df = get_player_match_data(info["id"], info["team_id"], team_mapping, fixture_lookup)
        player_dataframes[name] = df
        print(f"\n{name} ({df.team_name}):\n{df[['gameweek', 'opponent_team', 'points', 'form']].head()}")

    return player_dataframes

if __name__ == "__main__":
    player_dfs = main()
