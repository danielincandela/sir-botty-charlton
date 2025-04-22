def enrich_player_data(players, understat_data=None, injury_data=None):
    enriched = []

    for p in players:
        player = p.copy()

        # Estimate xG/xA using form as a proxy
        player["xG"] = round(player.get("form", 0) * 0.55, 2)
        player["xA"] = round(player.get("form", 0) * 0.3, 2)
        player["shots"] = round(player.get("form", 0) * 2)

        # Use FPL injury flag as health indicator
        player["injury_status"] = "None" if not player.get("injury_risk") else "Possibly Injured"
        player["return_date"] = "TBD" if player.get("injury_risk") else "-"

        enriched.append(player)

    return enriched

def fetch_understat_data():
    # No longer used — stub to preserve import
    return {}

def fetch_premier_injuries():
    # No longer used — stub to preserve import
    return {}