from flask import Flask, request, jsonify
from personality import get_random_line
from player_utils import get_manager_team, get_player_metadata, build_player_lookup
from sirbotty_logic import (
    summarize_team,
    convert_ids_to_names,
    recommend_captain,
    recommend_transfers
)
from weekly_report import generate_gameweek_report  # NEW

app = Flask(__name__)

# ========== Basic Routes with Personality ==========

@app.route("/")
def home():
    return get_random_line("greeting")

@app.route("/farewell")
def goodbye():
    return get_random_line("farewell")

@app.route("/error-test")
def error_test():
    return get_random_line("error")

# ========== Legacy Botty Lite Analyzer ==========

@app.route("/analyze", methods=["GET"])
def analyze_team():
    manager_id = request.args.get("id")
    if not manager_id:
        return jsonify({"error": "Missing Manager ID"}), 400

    team_data = get_manager_team(manager_id)
    metadata = get_player_metadata()
    player_lookup = build_player_lookup()

    if "error" in team_data:
        return jsonify({
            "error": team_data["error"],
            "note": get_random_line("error")
        }), 500

    summary = summarize_team(team_data)
    named_team = convert_ids_to_names(summary, metadata)
    captain_pick = recommend_captain(summary["starting_player_ids"], player_lookup)
    transfer_suggestions = recommend_transfers(summary["starting_player_ids"], player_lookup)

    return jsonify({
        "message": f"Sir Botty is analyzing team {manager_id}...",
        "team": named_team,
        "captain_recommendation": captain_pick,
        "transfers": transfer_suggestions,
        "tip": f"Sir Botty says to trust in {captain_pick['captain']} — unless he’s mysteriously benched.",
        "signoff": get_random_line("farewell")
    })

# ========== NEW Full Weekly Report API ==========

@app.route("/api/report", methods=["GET"])
def full_report():
    manager_id = request.args.get("manager_id")
    gameweek = request.args.get("gw", default=34, type=int)

    if not manager_id:
        return jsonify({"error": "Missing Manager ID"}), 400

    try:
        report = generate_gameweek_report(gameweek_number=gameweek, manager_id=manager_id)
        return jsonify(report)
    except Exception as e:
        return jsonify({
            "error": f"Failed to generate report: {str(e)}",
            "note": get_random_line("error")
        }), 500

# ========== Run Server ==========

if __name__ == "__main__":
    app.run(debug=True, port=5151)