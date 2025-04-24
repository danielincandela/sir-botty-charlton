
import requests

FPL_BASE_URL = "https://fantasy.premierleague.com/api"

def get_bootstrap_data():
    res = requests.get(f"{FPL_BASE_URL}/bootstrap-static/")
    res.raise_for_status()
    return res.json()

def get_fixtures():
    res = requests.get(f"{FPL_BASE_URL}/fixtures/")
    res.raise_for_status()
    return res.json()

def get_manager_data(manager_id):
    res = requests.get(f"{FPL_BASE_URL}/entry/{manager_id}/")
    res.raise_for_status()
    return res.json()

def get_manager_picks(manager_id, gameweek):
    url = f"{FPL_BASE_URL}/entry/{manager_id}/event/{gameweek}/picks/"
    res = requests.get(url)
    if res.status_code == 404:
        print(f"⚠️ No picks for GW{gameweek}. Falling back to GW{gameweek - 1}...")
        fallback_url = f"{FPL_BASE_URL}/entry/{manager_id}/event/{gameweek - 1}/picks/"
        fallback_res = requests.get(fallback_url)
        fallback_res.raise_for_status()
        return fallback_res.json()
    res.raise_for_status()
    return res.json()

def suggest_best_transfers_for_manager(manager_id, gameweek=34, max_transfers=3):
    print("🧠 Running universal transfer optimizer...")
    bootstrap = get_bootstrap_data()
    fixtures = get_fixtures()
    picks_data = get_manager_picks(manager_id, gameweek)
    manager_data = get_manager_data(manager_id)

    bank = manager_data.get("bank", 0) / 10.0
    picks = picks_data.get("picks", [])

    elements = bootstrap["elements"]
    teams = {t["id"]: t["name"] for t in bootstrap["teams"]}
    positions = {p["id"]: p["singular_name_short"] for p in bootstrap["element_types"]}
    elements_by_id = {p["id"]: p for p in elements}

    fixtures_by_team = {}
    for f in fixtures:
        if f["event"] == gameweek:
            for team_id, opp_id, diff in [
                (f["team_h"], f["team_a"], f["team_a_difficulty"]),
                (f["team_a"], f["team_h"], f["team_h_difficulty"])
            ]:
                fixtures_by_team.setdefault(team_id, []).append({
                    "opponent": teams.get(opp_id, "Unknown"),
                    "difficulty": diff
                })

    current_players = []
    for p in picks:
        player_id = p["element"]
        player = elements_by_id.get(player_id)
        if not player:
            continue
        team_id = player["team"]
        now_cost = player["now_cost"] / 10.0
        data = {
            "id": player_id,
            "name": f"{player['first_name']} {player['second_name']}",
            "position": positions[player["element_type"]],
            "team": teams[team_id],
            "form": float(player["form"]),
            "price": now_cost,
            "opponent": fixtures_by_team.get(team_id, [{}])[0].get("opponent", "Unknown"),
            "difficulty": fixtures_by_team.get(team_id, [{}])[0].get("difficulty", 3)
        }
        current_players.append(data)

    external_pool = []
    current_ids = set(p["element"] for p in picks)

    for p in elements:
        if p["id"] in current_ids:
            continue
        if p["status"] not in ["a", "d"]:
            continue
        if p["minutes"] < 60:
            continue
        team_id = p["team"]
        fixture_count = len(fixtures_by_team.get(team_id, []))
        if fixture_count == 0:
            continue
        price = p["now_cost"] / 10.0
        opp = fixtures_by_team.get(team_id, [{"opponent": "Unknown", "difficulty": 3}])[0]
        data = {
            "id": p["id"],
            "name": f"{p['first_name']} {p['second_name']}",
            "position": positions[p["element_type"]],
            "team": teams[team_id],
            "form": float(p["form"]),
            "price": price,
            "opponent": opp["opponent"],
            "difficulty": opp["difficulty"]
        }
        external_pool.append(data)

    recommendations = []
    for out_player in sorted(current_players, key=lambda x: (x["form"], -x["difficulty"], x["price"])):
        for in_player in sorted(external_pool, key=lambda x: (-x["form"], x["difficulty"], x["price"])):
            if in_player["position"] != out_player["position"]:
                continue
            if in_player["price"] <= out_player["price"] + bank:
                if in_player["form"] > out_player["form"]:
                    recommendations.append({
                        "out": out_player["name"],
                        "in": in_player["name"],
                        "reason": f"Upgrade {out_player['form']} → {in_player['form']}, vs {in_player['opponent']} (Diff {in_player['difficulty']})"
                    })
                    break
        if len(recommendations) >= max_transfers:
            break

    return recommendations
