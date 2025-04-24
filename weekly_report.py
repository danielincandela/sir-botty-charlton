import json
from form_trend import analyze_form_trends, load_players as load_mock_players
from captain_picker import pick_captains
from transfer_engine import suggest_transfers
from chip_strategy import evaluate_chip_strategy
from data_enrichment import (
    fetch_understat_data,
    fetch_premier_injuries,
    enrich_player_data
)
from transfer_optimizer import suggest_best_transfers_for_manager

from player_utils import (
    fetch_fixtures,
    enrich_players_with_fixtures,
    calculate_predicted_gameweek_score
)

from fpl_team_loader import fetch_team_for_gameweek, get_team_players


def pick_starting_xi(players):
    starting = []
    bench = []
    pos_buckets = {"GK": [], "DEF": [], "MID": [], "FWD": []}

    for player in players:
        pos_buckets[player["position"]].append(player)

    for pos in pos_buckets:
        pos_buckets[pos].sort(key=lambda p: (-p["form"], -p["expected_minutes"]))

    gks = pos_buckets["GK"][:1]
    defs = pos_buckets["DEF"][:3]
    mids = pos_buckets["MID"][:2]
    fwds = pos_buckets["FWD"][:1]

    starting_pool = gks + defs + mids + fwds
    used_ids = {p["id"] for p in starting_pool}

    remaining = []
    for pos in ["DEF", "MID", "FWD"]:
        for p in pos_buckets[pos]:
            if p["id"] not in used_ids:
                remaining.append(p)

    remaining.sort(key=lambda p: (-p["form"], -p["expected_minutes"]))
    while len(starting_pool) < 11 and remaining:
        next_best = remaining.pop(0)
        starting_pool.append(next_best)
        used_ids.add(next_best["id"])

    starting = [{
        "name": p["name"],
        "position": p["position"],
        "reason": f"Form {p['form']}, likely to start vs {p['opponent_team']}"
    } for p in starting_pool]

    bench = []
    for p in players:
        if p["id"] in used_ids:
            continue
        if p.get("number_of_fixtures", 1) == 0:
            continue
        bench.append({
            "name": p["name"],
            "position": p["position"],
            "reason": "Lower form or minutes, held in reserve"
        })

    return starting, bench

def detect_alerts(players):
    alerts = []
    for p in players:
        if p["injury_risk"]:
            alerts.append({
                "name": p["name"],
                "type": "injury",
                "message": f"{p['injury_status']} – Return: {p['return_date']}"
            })
        elif p["form"] < 2.5:
            alerts.append({
                "name": p["name"],
                "type": "form",
                "message": "Poor form – consider benching or transferring"
            })
        elif p["opponent_difficulty"] >= 4:
            alerts.append({
                "name": p["name"],
                "type": "fixture",
                "message": f"Tough opponent: {p['opponent_team']}"
            })
    return alerts

def generate_gameweek_report(gameweek_number=33, manager_id=None):
    is_projected = False
    gw_used = gameweek_number
    players, chips_used, current_team_ids = [], [], []

    if manager_id:
        try:
            gw_used, _, is_projected = fetch_team_for_gameweek(manager_id, gameweek_number)
            players, chips_used, current_team_ids = get_team_players(manager_id, gw_used)
            print(f"✅ Loaded FPL team for Manager ID {manager_id} (GW{gw_used})")
        except Exception as e:
            print(f"⚠️ Falling back to mock data: {e}")
            players = load_mock_players()
            chips_used = ["wildcard"]
            current_team_ids = [p["id"] for p in players]
    else:
        print("🧪 Using mock data fallback.")
        players = load_mock_players()
        chips_used = ["wildcard"]
        current_team_ids = [p["id"] for p in players]

    understat = fetch_understat_data()
    injuries = fetch_premier_injuries()
    players = enrich_player_data(players, understat, injuries)

    players_with_trends = analyze_form_trends(players)
    fixtures = fetch_fixtures()
    enriched_players = enrich_players_with_fixtures(players_with_trends, fixtures, gameweek_number)

    # Recalculate suggestions and output using the target gameweek context
    captains = pick_captains(enriched_players)
    transfers = suggest_transfers(enriched_players)
    starting_xi, bench = pick_starting_xi(enriched_players)
    alerts = detect_alerts(enriched_players)
    chip_recommendation = evaluate_chip_strategy(enriched_players, chips_used, gameweek_number)
    chip_recommendation["chips_used"] = chips_used

    # 🧠 Use the upgraded manager-based optimizer
    transfer_recommendations = suggest_best_transfers_for_manager(
        manager_id, gameweek=gameweek_number, max_transfers=3
    )

    predicted_score = calculate_predicted_gameweek_score(enriched_players)

    report = {
        "gameweek": gameweek_number,
        "original_gw": gw_used if is_projected else gameweek_number,
        "is_projected": is_projected,
        "team_overview": [
            {
                "id": p["id"],
                "team_id": p.get("team_id", 1),
                "photo_id": p.get("photo_id", "0000001"),
                "name": p["name"],
                "team": p["team"],
                "position": p["position"],
                "form": p["form"],
                "points_per_game": p["points_per_game"],
                "form_trend": p["form_trend"],
                "expected_minutes": p["expected_minutes"],
                "opponent_team": p["opponent_team"],
                "opponent_difficulty": p["opponent_difficulty"],
                "injury_risk": p["injury_risk"],
                "injury_status": p["injury_status"],
                "return_date": p["return_date"],
                "double_gameweek": p.get("double_gameweek", False),
                "blank_gameweek": p.get("blank_gameweek", False),
                "xG": p["xG"],
                "xA": p["xA"],
                "shots": p["shots"],
                "number_of_fixtures": p.get("number_of_fixtures", 1),
                "is_captain": p.get("is_captain", False),
                "is_vice_captain": p.get("is_vice_captain", False),
                "predicted_points_per_fixture": p.get("predicted_points_per_fixture", 0)
            }
            for p in enriched_players
        ],
        "captain": captains["captain"],
        "vice_captain": captains["vice_captain"],
        "transfer_suggestions": transfers,
        "transfer_recommendations": transfer_recommendations,
        "starting_xi": starting_xi,
        "bench": bench,
        "alerts": alerts,
        "chip_recommendation": chip_recommendation,
        "predicted_score": predicted_score
    }

    return report

if __name__ == "__main__":
    test_report = generate_gameweek_report(gameweek_number=34, manager_id="5421259")
    with open("sir_botty_weekly_report.json", "w") as f:
        json.dump(test_report, f, indent=4)
    print("✅ Weekly report saved as sir_botty_weekly_report.json")