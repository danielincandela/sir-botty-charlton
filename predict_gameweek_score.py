# predict_gameweek_score.py

from player_utils import (
    fetch_fixtures,
    get_current_gameweek,
    enrich_players_with_fixtures,
    calculate_predicted_gameweek_score
)

# 🧪 Sample player list (replace this with real data from your FPL team)
players = [
    {
        'name': 'Mo Salah',
        'is_captain': True,
        'is_vice_captain': False,
        'predicted_points_per_fixture': 6.0,
        'team_id': 11  # Liverpool
    },
    {
        'name': 'Bukayo Saka',
        'is_captain': False,
        'is_vice_captain': True,
        'predicted_points_per_fixture': 5.5,
        'team_id': 1  # Arsenal
    },
    {
        'name': 'Erling Haaland',
        'is_captain': False,
        'is_vice_captain': False,
        'predicted_points_per_fixture': 7.2,
        'team_id': 13  # Man City
    }
]

def main():
    try:
        print("🔄 Fetching data...")
        fixtures = fetch_fixtures()
        current_gw = get_current_gameweek()

        print(f"📅 Current Gameweek: {current_gw}")
        enriched_players = enrich_players_with_fixtures(players, fixtures, current_gw)

        print("🔢 Calculating predicted score...")
        score = calculate_predicted_gameweek_score(enriched_players)

        print(f"🎯 Predicted Gameweek Score: {score}")
        print("\n📋 Player Breakdown:")
        for p in enriched_players:
            print(f" - {p['name']}: {p['predicted_points_per_fixture']} pts x {p['number_of_fixtures']} fixture(s)"
                  + (" (C)" if p['is_captain'] else ""))
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()