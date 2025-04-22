# player_utils.py

import requests
from collections import defaultdict

FPL_FIXTURES_URL = "https://fantasy.premierleague.com/api/fixtures/"
FPL_BOOTSTRAP_URL = "https://fantasy.premierleague.com/api/bootstrap-static/"

def fetch_fixtures():
    response = requests.get(FPL_FIXTURES_URL)
    response.raise_for_status()
    return response.json()

def get_current_gameweek():
    response = requests.get(FPL_BOOTSTRAP_URL)
    response.raise_for_status()
    data = response.json()
    events = data.get("events", [])
    for event in events:
        if event["is_current"]:
            return event["id"]
    return max(e["id"] for e in events if e["is_next"])  # Fallback if no current GW

def enrich_players_with_fixtures(players, fixtures, current_gameweek):
    """
    Adds 'number_of_fixtures' to each player based on their team in the current gameweek.
    Defaults to 1 fixture if fixture data is incomplete (e.g. future gameweeks).
    """
    team_fixtures = defaultdict(int)

    # Guard against missing or empty fixture list for future gameweeks
    if fixtures:
        for fixture in fixtures:
            if fixture.get("event") != current_gameweek:
                continue
            team_h = fixture.get("team_h")
            team_a = fixture.get("team_a")

            if team_h:
                team_fixtures[team_h] += 1
            if team_a:
                team_fixtures[team_a] += 1

    for player in players:
        team_id = player.get("team_id")
        player["number_of_fixtures"] = team_fixtures.get(team_id, 1)  # Default to 1 if team ID not found

    return players

def calculate_predicted_gameweek_score(players):
    """
    Calculates total predicted gameweek score based on captaincy and fixture count.
    Falls back to using xG + xA scaled by expected minutes if no explicit prediction.
    Caps output to prevent unrealistic scores.
    """
    total_score = 0

    for player in players:
        try:
            xG = float(player.get("xG", 0))
            xA = float(player.get("xA", 0))
            minutes = float(player.get("expected_minutes", 60))
        except (ValueError, TypeError):
            xG, xA, minutes = 0.0, 0.0, 60.0

        # Clamp minutes to a realistic range [0, 90]
        minutes = max(0, min(minutes, 90))

        # Predict points per fixture from attacking contribution
        predicted_per_fixture = (xG + xA) * (minutes / 90)

        # Clamp individual prediction to [0, 15] to prevent runaway values
        predicted_per_fixture = max(0, min(predicted_per_fixture, 15))

        # Store on player for debugging/UI
        player["predicted_points_per_fixture"] = predicted_per_fixture

        # Total based on number of fixtures
        num_fixtures = player.get("number_of_fixtures", 1)
        base_points = predicted_per_fixture * num_fixtures

        if player.get("is_captain"):
            total_score += base_points * 2
        else:
            total_score += base_points

    return round(total_score, 2)