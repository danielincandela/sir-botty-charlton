def generate_gameweek_report(gameweek_number=33, manager_id=None):
    players = []
    chips_used = []
    current_team_ids = []

    if manager_id and get_team_players:
        try:
            players, chips_used, current_team_ids = get_team_players(manager_id, gameweek_number)
            if not players:
                raise ValueError("No players returned. Falling back to mock data.")
            print(f"✅ Loaded real FPL team for Manager ID {manager_id}")
        except Exception as e:
            print(f"⚠️ Falling back to mock data: {e}")
            from form_trend import load_players as load_mock_players
            players = load_mock_players()
            chips_used = ["wildcard"]
            current_team_ids = [p["id"] for p in players]
    else:
        print("🧪 Using mock data fallback.")
        from form_trend import load_players as load_mock_players
        players = load_mock_players()
        chips_used = ["wildcard"]
        current_team_ids = [p["id"] for p in players]

    from form_trend import analyze_form_trends
    from captain_picker import pick_captains
    from transfer_engine import suggest_transfers
    from chip_strategy import evaluate_chip_strategy
    from data_enrichment import (
        fetch_understat_data,
        fetch_premier_injuries,
        enrich_player_data
    )
    from transfer_optimizer import suggest_best_transfers

    understat = fetch_understat_data()
    injuries = fetch_premier_injuries()
    players = enrich_player_data(players, understat, injuries)

    players_with_trends = analyze_form_trends(players)
    captains = pick_captains(players_with_trends)
    transfers = suggest_transfers(players_with_trends)
    starting_xi, bench = pick_starting_xi(players_with_trends)
    alerts = detect_alerts(players_with_trends)
    chip_recommendation = evaluate_chip_strategy(players_with_trends, chips_used, gameweek_number)
    chip_recommendation["chips_used"] = chips_used

    transfer_recommendations = suggest_best_transfers(current_team_ids, budget=2.0, max_transfers=3)

    report = {
        "gameweek": gameweek_number,
        "team_overview": [
            {
                "id": p["id"],
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
                "shots": p["shots"]
            }
            for p in players_with_trends
        ],
        "captain": captains["captain"],
        "vice_captain": captains["vice_captain"],
        "transfer_suggestions": transfers,
        "transfer_recommendations": transfer_recommendations,
        "starting_xi": starting_xi,
        "bench": bench,
        "alerts": alerts,
        "chip_recommendation": chip_recommendation
    }

    return report