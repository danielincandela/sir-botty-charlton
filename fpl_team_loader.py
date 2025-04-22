import requests

FPL_BASE_URL = "https://fantasy.premierleague.com/api"

def get_bootstrap_data():
    res = requests.get(f"{FPL_BASE_URL}/bootstrap-static/")
    res.raise_for_status()
    return res.json()

def get_manager_picks(manager_id, gameweek):
    try:
        url = f"{FPL_BASE_URL}/entry/{manager_id}/event/{gameweek}/picks/"
        res = requests.get(url)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print(f"❌ Error fetching picks: {e}")
        return {"picks": []}

def get_manager_chips(manager_id):
    try:
        res = requests.get(f"{FPL_BASE_URL}/entry/{manager_id}/history/")
        res.raise_for_status()
        return [c["name"].lower() for c in res.json().get("chips", [])]
    except:
        return []

def get_fixtures():
    res = requests.get(f"{FPL_BASE_URL}/fixtures/")
    res.raise_for_status()
    return res.json()

def get_team_players(manager_id, gameweek):
    bootstrap = get_bootstrap_data()
    picks_data = get_manager_picks(manager_id, gameweek)
    fixtures = get_fixtures()
    chips_used = get_manager_chips(manager_id)

    players_info = bootstrap["elements"]
    teams_info = {t["id"]: t["name"] for t in bootstrap["teams"]}
    positions_info = {1: "GK", 2: "DEF", 3: "MID", 4: "FWD"}

    player_dict = {p["id"]: p for p in players_info}
    team_fixtures = {}

    for f in fixtures:
        if not f["finished"]:
            for team_id, opponent_id, difficulty in [
                (f["team_h"], f["team_a"], f["team_a_difficulty"]),
                (f["team_a"], f["team_h"], f["team_h_difficulty"])
            ]:
                team_fixtures.setdefault(team_id, []).append({
                    "opponent_id": opponent_id,
                    "difficulty": difficulty,
                    "event": f["event"]
                })

    picks = picks_data.get("picks", [])
    if not picks:
        return [], chips_used, []

    raw_ids = [p["element"] for p in picks]
    team_players = []

    for pick in picks:
        player_id = pick["element"]
        player = player_dict.get(player_id)
        if not player:
            continue

        team_id = player["team"]
        fixtures_list = team_fixtures.get(team_id, [])
        upcoming = [f for f in fixtures_list if f["event"]]
        is_double = len(set(f["event"] for f in upcoming)) > 1
        is_blank = len(upcoming) == 0

        if upcoming:
            opponent = upcoming[0]
            opponent_name = teams_info.get(opponent["opponent_id"], "Unknown")
            difficulty = opponent["difficulty"]
        else:
            opponent_name = "Unknown"
            difficulty = 3

        team_players.append({
            "id": player["id"],
            "photo_id": player["photo"].split(".")[0],
            "team_id": team_id,
            "name": f"{player['first_name']} {player['second_name']}",
            "team": teams_info.get(team_id, "Unknown"),
            "position": positions_info.get(player["element_type"], "UNK"),
            "form": float(player["form"]),
            "points_per_game": float(player["points_per_game"]),
            "expected_minutes": int(player["minutes"]),
            "opponent_team": opponent_name,
            "opponent_difficulty": difficulty,
            "injury_risk": player["news"] != "",
            "injury_status": player["news"] or "None",
            "return_date": player.get("return", ""),
            "double_gameweek": is_double,
            "blank_gameweek": is_blank
        })

    return team_players, chips_used, raw_ids