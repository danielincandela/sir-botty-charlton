import json

def load_players(filepath="mock_fpl_players.json"):
    with open(filepath, "r") as f:
        return json.load(f)

def analyze_form_trends(players):
    for player in players:
        form = player["form"]
        avg_points = player["points_per_game"]
        
        if form > avg_points + 0.5:
            trend = "⬆️ trending up"
        elif form < avg_points - 0.5:
            trend = "⬇️ trending down"
        else:
            trend = "↔️ stable"
        
        player["form_trend"] = trend

    return players

if __name__ == "__main__":
    players = load_players()
    players_with_trends = analyze_form_trends(players)
    
    for player in players_with_trends:
        print(f"{player['name']} – Form: {player['form']} | PPG: {player['points_per_game']} → {player['form_trend']}")