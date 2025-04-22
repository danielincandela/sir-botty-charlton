def pick_captains(players):
    if not players:
        return {
            "captain": {"name": "N/A", "reason": "No valid players to choose from."},
            "vice_captain": {"name": "N/A", "reason": "No valid players to choose from."}
        }

    # Sort by a smart captaincy metric: form, xG, expected minutes
    sorted_players = sorted(
        players,
        key=lambda p: (
            p.get("form", 0),
            p.get("xG", 0),
            p.get("expected_minutes", 0)
        ),
        reverse=True
    )

    captain = sorted_players[0]
    vice = sorted_players[1] if len(sorted_players) > 1 else captain

    return {
        "captain": {
            "name": captain["name"],
            "reason": f"Strong form ({captain['form']}), xG {captain['xG']}, minutes {captain['expected_minutes']}."
        },
        "vice_captain": {
            "name": vice["name"],
            "reason": f"Reliable backup with solid performance metrics."
        }
    }