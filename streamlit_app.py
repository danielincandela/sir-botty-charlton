import streamlit as st
import requests
from PIL import Image
from weekly_report import generate_gameweek_report

FPL_BASE_URL = "https://fantasy.premierleague.com/api"

def get_team_metadata(manager_id):
    try:
        res = requests.get(f"{FPL_BASE_URL}/entry/{manager_id}/")
        if res.status_code == 200:
            data = res.json()
            return data.get("name", "Unknown Team"), data.get("player_first_name", "") + " " + data.get("player_last_name", "")
        return "Unknown Team", ""
    except Exception:
        return "Unknown Team", ""

# Page setup
st.set_page_config(page_title="Sir Botty Charlton", page_icon="🧠")

# Load and display logo
try:
    logo = Image.open("sirbotty-logo.png")
    st.image(logo, width=150)
except FileNotFoundError:
    st.warning("🖼️ Logo not found. Please add 'sirbotty-logo.png' to your app folder.")

st.markdown("""
# 🧠 Sir Botty Charlton

**"On me 'ead, son!"** Welcome to the surreal sanctuary of stats, smirks, and smashing fantasy football insight.  
Sir Botty — tactical tactician, tea connoisseur, and the reincarnation of the 1966 World Cup spirit — is here to guide your Gameweek with wit, wisdom, and a wry grin. 🍵👑

_Enter your Manager ID, and let the dream unfold..._
""", unsafe_allow_html=True)

st.markdown("### 🧾 Enter Your FPL Manager ID")

if "manager_id" not in st.session_state:
    st.session_state.manager_id = ""

manager_id = st.text_input("FPL Manager ID", value=st.session_state.manager_id)

if manager_id:
    st.session_state.manager_id = manager_id
    st.markdown(f"✅ Manager ID set: `{manager_id}`")
else:
    st.warning("Please enter your FPL Manager ID to receive personalized team advice.")

st.markdown("---")
st.subheader("🎩 Sir Botty’s Gameweek Opera 🎭")

gameweek = st.number_input("Which Gameweek do you want to analyze?", min_value=1, max_value=38, value=34)

if st.button("🧠 Summon the Wisdom"):
    with st.spinner("Consulting the footballing ether and boiling the perfect cuppa..."):
        report = generate_gameweek_report(gameweek_number=gameweek, manager_id=st.session_state.manager_id)

        if manager_id:
            team_name, manager_name = get_team_metadata(manager_id)
            squad_value = round(sum([p["form"] for p in report["team_overview"]]) + 85, 1)

            st.markdown(f"### 🔮 Predicted Gameweek Score: **{round(report['predicted_score'], 1)}** points")
            st.markdown(f"### 🏷️ Team: **{team_name}**")
            st.markdown(f"#### 👤 Manager: {manager_name}")
            st.markdown(f"💰 **Estimated Squad Value**: £{squad_value}m")

        if len(report["team_overview"]) == 0:
            st.error("🚫 No player data found. Your team might be private or not set for this gameweek.")
            st.stop()

        st.success(f"Gameweek {gameweek} insights loaded. Let the poetry commence! 🎼")

        st.markdown("## 🧃 Chips Already Used")
        chips_used = report.get("chip_recommendation", {}).get("chips_used", [])
        if chips_used:
            st.markdown(", ".join(f"✅ {chip.title()}" for chip in chips_used))
        else:
            st.info("No chips used yet. A full deck of destiny remains.")

        st.markdown("## 👑 Captain Pick")
        st.markdown(f"**{report['captain']['name']}** — {report['captain']['reason']}")

        st.markdown("## 🎖️ Vice-Captain Pick")
        st.markdown(f"**{report['vice_captain']['name']}** — {report['vice_captain']['reason']}")

        st.markdown("## 💥 Explosive Picks")
        explosive = sorted(report["team_overview"], key=lambda p: p["xG"] + p["shots"], reverse=True)[:3]
        for p in explosive:
            st.markdown(f"**{p['name']}** ({p['position']}, {p['team']}) – xG: {p['xG']}, Shots: {p['shots']}")

        st.markdown("## 🧱 Starting XI")
        position_order = {"GK": 0, "DEF": 1, "MID": 2, "FWD": 3}
        sorted_starting = sorted(report["starting_xi"], key=lambda x: position_order.get(x["position"], 4))

        formation_counts = {"DEF": 0, "MID": 0, "FWD": 0}
        for player in sorted_starting:
            pos = player["position"]
            if pos in formation_counts:
                formation_counts[pos] += 1

        formation_str = f"{formation_counts['DEF']}-{formation_counts['MID']}-{formation_counts['FWD']}"
        st.markdown(f"📐 **Formation:** {formation_str}")

        total_expected_points = sum(
            p.get("points_per_game", 0) for p in report["team_overview"]
            if any(s["name"] == p["name"] for s in sorted_starting)
        )
        st.markdown(f"🎯 **Estimated Points from XI:** {round(total_expected_points, 1)}")

        for player in sorted_starting:
            st.markdown(f"**{player['name']}** ({player['position']}) – {player['reason']}")

        st.markdown("## 🪑 Bench")
        for player in report["bench"]:
            st.markdown(f"**{player['name']}** ({player['position']}) – {player['reason']}")

        if report["alerts"]:
            st.markdown("## 🚨 Alerts")
            for alert in report["alerts"]:
                st.warning(f"**{alert['name']}** – {alert['message']}")

        chip = report.get("chip_recommendation", {})
        st.markdown("## 🧩 Chip Strategy")
        if chip.get("recommended_chip"):
            st.success(f"💡 Suggested Chip: **{chip['recommended_chip']}** — {chip['reason']}")
        else:
            st.info("No chip needed. Save it for a rainy football apocalypse.")

        st.markdown("## 🔁 Substitution Suggestions")
        for t in report["transfer_suggestions"]:
            st.markdown(f"⬅️ **{t['out']}** → ➡️ **{t['in']}**")
            st.caption(t["reason"])

        st.markdown("## 💸 Transfer Recommendations")
        if report["transfer_recommendations"]:
            for t in report["transfer_recommendations"]:
                st.markdown(f"⬅️ **{t['out']}** → ➡️ **{t['in']}**")
                st.caption(t["reason"])
        else:
            st.info("Botty sees no clear upgrades. Hold steady, soldier.")

        st.markdown("## 🧾 Full Squad Overview")
        sorted_squad = sorted(report["team_overview"], key=lambda x: (position_order.get(x["position"], 4), -x["form"]))

        for p in sorted_squad:
            status_tag = ""
            if p.get("double_gameweek"):
                status_tag = "🔥 **Double Gameweek**"
            elif p.get("blank_gameweek"):
                status_tag = "🧊 Blank Gameweek"

            st.markdown(f"**{p['name']}** – {p['position']} for **{p['team']}**")
            if status_tag:
                st.markdown(status_tag)
            st.caption(
                f"Form: {p['form']} | PPG: {p['points_per_game']} | Min: {p['expected_minutes']}  \n"
                f"xG: {p['xG']} | xA: {p['xA']} | Shots: {p['shots']}  \n"
                f"vs {p['opponent_team']} (Diff {p['opponent_difficulty']})"
            )

st.markdown("---")
st.caption("Sir Botty Charlton © — surreal, strategic, and a little bit smug.")