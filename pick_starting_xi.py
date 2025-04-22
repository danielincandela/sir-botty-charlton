def pick_starting_xi(players):
    starting = []
    bench = []
    pos_buckets = {"GK": [], "DEF": [], "MID": [], "FWD": []}

    for player in players:
        pos_buckets[player["position"]].append(player)

    # Sort players in each position by form
    for pos in pos_buckets:
        pos_buckets[pos].sort(key=lambda p: (-p["form"], -p["expected_minutes"]))

    # Core requirements
    gks = pos_buckets["GK"][:1]
    defs = pos_buckets["DEF"][:3]
    mids = pos_buckets["MID"][:2]
    fwds = pos_buckets["FWD"][:1]

    starting_pool = gks + defs + mids + fwds
    used_ids = {p["id"] for p in starting_pool}

    # Fill up to 11 with best remaining players
    remaining = [
        p for pos in ["GK", "DEF", "MID", "FWD"]
        for p in pos_buckets[pos]
        if p["id"] not in used_ids
    ]
    remaining.sort(key=lambda p: (-p["form"], -p["expected_minutes"]))

    while len(starting_pool) < 11 and remaining:
        next_best = remaining.pop(0)
        starting_pool.append(next_best)
        used_ids.add(next_best["id"])

    # Build final output lists
    starting = [{
        "name": p["name"],
        "position": p["position"],
        "reason": f"Form {p['form']}, likely to start vs {p['opponent_team']}"
    } for p in starting_pool]

    bench = [{
        "name": p["name"],
        "position": p["position"],
        "reason": "Lower form or minutes, held in reserve"
    } for p in players if p["id"] not in used_ids]

    return starting, bench