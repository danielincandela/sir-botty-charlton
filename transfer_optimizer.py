import requests

FPL_BASE_URL = "https://fantasy.premierleague.com/api"

def get_bootstrap_data():
    res = requests.get(f"{FPL_BASE_URL}/bootstrap-static/")
    res.raise_for_status()
    return res.json()

def suggest_best_transfers(current_team_ids, budget=2.0, max_transfers=3):
    bootstrap = get_bootstrap_data()
    all_players = bootstrap["elements"]
    teams = {t["id"]: t["name"] for t in bootstrap["teams"]}
    positions = {p["id"]: p["singular_name_short"] for p in bootstrap["element_types"]}

    current_ids = set(current_team_ids)

    # Build full external candidate pool
    external_pool = []
    for p in all_players:
        if p["id"] in current_ids:
            continue
        if p["status"] not in ["a", "d"]:
            continue
        if p["minutes"] < 90:
            continue
        external_pool.append({
            "id": p["id"],
            "name": f"{p['first_name']} {p['second_name']}",
            "team": teams[p["team"]],
            "position": positions[p["element_type"]],
            "price": p["now_cost"] / 10,
            "form": float(p["form"]),
            "ppg": float(p["points_per_game"]),
            "score": float(p["form"]) + float(p["points_per_game"]) + (float(p["form"]) * 0.55),
        })

    # Sort by smart score
    external_pool.sort(key=lambda p: p["score"], reverse=True)

    # Get current squad by position
    current_players = [p for p in all_players if p["id"] in current_ids]
    current_by_position = {}
    for p in current_players:
        pos = positions[p["element_type"]]
        current_by_position.setdefault(pos, []).append({
            "id": p["id"],
            "name": f"{p['first_name']} {p['second_name']}",
            "form": float(p["form"]),
            "price": p["now_cost"] / 10,
            "position": pos
        })

    # Recommend up to 3 upgrades
    recommendations = []
    used_out_ids = set()

    for new_player in external_pool:
        if len(recommendations) >= max_transfers:
            break

        pos = new_player["position"]
        candidates = current_by_position.get(pos, [])

        # Try replacing the weakest option in this position
        for old_player in sorted(candidates, key=lambda p: p["form"]):
            if old_player["id"] in used_out_ids:
                continue

            price_diff = new_player["price"] - old_player["price"]
            if price_diff <= budget and new_player["form"] > old_player["form"] + 1:
                recommendations.append({
                    "out": old_player["name"],
                    "in": new_player["name"],
                    "reason": f"{pos} upgrade: Form {old_player['form']} → {new_player['form']}, price +£{price_diff:.1f}"
                })
                budget -= max(0, price_diff)
                used_out_ids.add(old_player["id"])
                break

    return recommendations