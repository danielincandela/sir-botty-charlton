import json

def load_players(filepath="mock_fpl_players.json"):
    with open(filepath, "r") as f:
        return json.load(f)

def suggest_transfers(players, limit=3):
    # Sort players by worst form, high difficulty, and low expected minutes
    underperformers = sorted(
        [p for p in players if not p["injury_risk"]],
        key=lambda p: (p["form"], -p["opponent_difficulty"], p["expected_minutes"])
    )

    # Sort players by best form and good fixtures
    top_performers = sorted(
        [p for p in players if not p["injury_risk"] and p["expected_minutes"] >= 60],
        key=lambda p: (-p["form"], p["opponent_difficulty"])
    )

    suggestions = []

    for i in range(limit):
        if i >= len(underperformers) or i >= len(top_performers):
            break

        out_player = underperformers[i]
        in_player = top_performers[i]

        if out_player["id"] == in_player["id"]:
            continue  # Skip silly transfers

        reason = (
            f"{out_player['name']} has low form ({out_player['form']}) and a tough opponent "
            f"({out_player['opponent_team']}). Meanwhile, {in_player['name']} is in great form "
            f"({in_player['form']}) and has a more favorable fixture."
        )

        suggestions.append({
            "out": out_player["name"],
            "in": in_player["name"],
            "reason": reason
        })

    return suggestions

if __name__ == "__main__":
    players = load_players()
    transfers = suggest_transfers(players)

    for i, t in enumerate(transfers, 1):
        print(f"🔁 Transfer #{i}")
        print(f"⬅️ Out: {t['out']}")
        print(f"➡️ In: {t['in']}")
        print(f"💬 Reason: {t['reason']}")
        print()
        