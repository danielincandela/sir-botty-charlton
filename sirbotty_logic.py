import requests

def summarize_team(team_data):
    try:
        picks = team_data["picks"]
        captain_id = next(player["element"] for player in picks if player["is_captain"])
        vice_id = next(player["element"] for player in picks if player["is_vice_captain"])

        starting_ids = [p["element"] for p in picks if p["multiplier"] > 0]
        bench_ids = [p["element"] for p in picks if p["multiplier"] == 0]

        return {
            "starting_player_ids": starting_ids,
            "bench_player_ids": bench_ids,
            "captain_id": captain_id,
            "vice_captain_id": vice_id
        }
    except Exception as e:
        return {"error": str(e)}


def convert_ids_to_names(summary, metadata):
    try:
        # Position lookup
        id_to_position = {
            1: "Goalkeeper",
            2: "Defender",
            3: "Midfielder",
            4: "Forward"
        }

        # Team lookup (1-based index from FPL)
        team_lookup = {
            1: "Arsenal", 2: "Aston Villa", 3: "Bournemouth", 4: "Brentford", 5: "Brighton",
            6: "Burnley", 7: "Chelsea", 8: "Crystal Palace", 9: "Everton", 10: "Fulham",
            11: "Liverpool", 12: "Luton", 13: "Man City", 14: "Man Utd", 15: "Newcastle",
            16: "Nottingham Forest", 17: "Sheffield Utd", 18: "Spurs", 19: "West Ham", 20: "Wolves"
        }

        # Get fixtures data
        fixtures_response = requests.get("https://fantasy.premierleague.com/api/fixtures/")
        fixtures = fixtures_response.json()

        # Build fixture map: team_id → next opponent and home/away
        fixture_map = {}
        for f in fixtures:
            if not f["finished"] and f["event"] is not None:
                home_id = f["team_h"]
                away_id = f["team_a"]
                if home_id not in fixture_map:
                    fixture_map[home_id] = f"{team_lookup.get(away_id)} (H)"
                if away_id not in fixture_map:
                    fixture_map[away_id] = f"{team_lookup.get(home_id)} (A)"

        # Build player ID → info
        id_to_info = {
            p["id"]: {
                "name": f"{p['first_name']} {p['second_name']}",
                "position": id_to_position.get(p["element_type"], "Unknown"),
                "team": team_lookup.get(p["team"], "Unknown"),
                "value": p["now_cost"] / 10,
                "opponent": fixture_map.get(p["team"], "No fixture")
            } for p in metadata
        }

        def map_ids(id_list):
            return [
                {
                    "id": pid,
                    "name": id_to_info[pid]["name"],
                    "position": id_to_info[pid]["position"],
                    "team": id_to_info[pid]["team"],
                    "value": id_to_info[pid]["value"],
                    "opponent": id_to_info[pid]["opponent"]
                }
                for pid in id_list if pid in id_to_info
            ]

        return {
            "starting": map_ids(summary["starting_player_ids"]),
            "bench": map_ids(summary["bench_player_ids"]),
            "captain": id_to_info.get(summary["captain_id"], {}).get("name", "Unknown"),
            "vice_captain": id_to_info.get(summary["vice_captain_id"], {}).get("name", "Unknown")
        }

    except Exception as e:
        return {"error": str(e)}


def recommend_captain(starting_ids, player_lookup):
    try:
        starters = [player_lookup[pid] for pid in starting_ids if pid in player_lookup]
        eligible = [p for p in starters if (p["chance_of_playing_next_round"] or 100) >= 75]
        sorted_candidates = sorted(eligible, key=lambda p: (p["form"], p["total_points"]), reverse=True)

        if not sorted_candidates:
            return {"captain": "No eligible captain found", "vice_captain": None}

        captain = sorted_candidates[0]
        vice = sorted_candidates[1] if len(sorted_candidates) > 1 else None

        return {
            "captain": captain["name"],
            "vice_captain": vice["name"] if vice else None
        }
    except Exception as e:
        return {"error": str(e)}


def recommend_transfers(starting_ids, player_lookup, budget=0, max_transfers=1):
    try:
        transfer_out = []
        for pid in starting_ids:
            p = player_lookup.get(pid)
            if not p:
                continue
            if (p["chance_of_playing_next_round"] or 100) < 50 or p["form"] < 2.0:
                transfer_out.append({"id": pid, "name": p["name"], "form": p["form"], "cost": p["now_cost"]})

        transfer_in = []
        if transfer_out:
            for out_player in transfer_out[:max_transfers]:
                max_price = out_player["cost"] + budget
                candidates = [
                    p for p in player_lookup.values()
                    if (p["form"] > 4.0 and (p["chance_of_playing_next_round"] or 100) >= 75 and p["now_cost"] <= max_price)
                ]
                sorted_in = sorted(candidates, key=lambda x: x["form"], reverse=True)
                best_replacement = sorted_in[0] if sorted_in else None
                if best_replacement:
                    transfer_in.append({
                        "out": out_player["name"],
                        "in": best_replacement["name"],
                        "form": best_replacement["form"],
                        "cost": best_replacement["now_cost"]
                    })

        return {
            "transfers": transfer_in if transfer_in else "No urgent transfers recommended this week."
        }

    except Exception as e:
        return {"error": str(e)}
