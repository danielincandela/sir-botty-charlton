def pick_captains(players):
    # Filter out players with at least one fixture this gameweek
    eligible = [p for p in players if p.get("number_of_fixtures", 0) > 0]

    if not eligible:
        return {
            "captain": {"name": "None", "reason": "No eligible players this gameweek"},
            "vice_captain": {"name": "None", "reason": "No eligible players this gameweek"}
        }

    # Sort by attacking threat, form, and minutes
    sorted_players = sorted(
        eligible,
        key=lambda p: (
            p.get("xG", 0) + p.get("xA", 0),
            p.get("form", 0),
            p.get("expected_minutes", 0)
        ),
        reverse=True
    )

    captain = sorted_players[0]
    vice = next((p for p in sorted_players if p["name"] != captain["name"]), None)

    if not vice:
        return {
            "captain": {
                "name": captain["name"],
                "reason": f"Only eligible player: xG+xA: {captain['xG'] + captain['xA']:.2f}, form {captain['form']}"
            },
            "vice_captain": {
                "name": "None",
                "reason": "No second eligible player available this gameweek"
            }
        }

    return {
        "captain": {
            "name": captain["name"],
            "reason": f"xG+xA: {captain['xG'] + captain['xA']:.2f}, form {captain['form']}"
        },
        "vice_captain": {
            "name": vice["name"],
            "reason": f"xG+xA: {vice['xG'] + vice['xA']:.2f}, form {vice['form']}"
        }
    }