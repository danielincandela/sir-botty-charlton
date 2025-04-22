def evaluate_chip_strategy(players, chips_used, gameweek):
    if not players:
        return {
            "recommended_chip": None,
            "reason": "No valid players to evaluate chip usage."
        }

    # Check if there's already a chip used
    if "wildcard" in chips_used or "freehit" in chips_used:
        return {
            "recommended_chip": None,
            "reason": "You've already used a major chip. Stay the course!"
        }

    # Check for high form + fixture difficulty to trigger chip suggestion
    try:
        top_pick = max(players[:11], key=lambda p: p.get("form", 0))
    except ValueError:
        return {
            "recommended_chip": None,
            "reason": "Not enough players available to assess chip strategy."
        }

    if top_pick["form"] >= 8:
        return {
            "recommended_chip": "Triple Captain",
            "reason": f"{top_pick['name']} is in red-hot form and might haul this week."
        }

    if any(p.get("double_gameweek", False) for p in players):
        return {
            "recommended_chip": "Bench Boost",
            "reason": "Several of your players have a Double Gameweek — boost that bench!"
        }

    return {
        "recommended_chip": None,
        "reason": "No chip needed this week. Keep it in your back pocket."
    }