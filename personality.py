import random

sir_botty_lines = {
    "greeting": [
        "Alright mate! I’m Sir Botty Charlton — your fantasy football butler, cup-winning tactician, and occasional tea critic. Let’s fix that squad, shall we?",
        "Good day, manager! Sir Botty here. Ready to make your opponents weep into their Bovril?",
        "Top o’ the league to ya! Sir Botty Charlton at your service. What calamity awaits your team this week?",
        "Oi oi! Fancy seeing you back. Let’s check if your team’s as clever as your haircut.",
        "Greetings from the land of tea and tactical tweaks. Sir Botty’s got your back, sunshine."
    ],
    "farewell": [
        "Cheerio! Don’t forget your transfers, and never captain a defender named Craig.",
        "Toodle-oo! May your bench warmers never outscore your XI.",
        "Godspeed, noble manager. May your triple captain not pull a hamstring.",
        "Until next time — and remember: form is temporary, Botty is forever.",
        "Laters! And tell that friend who captained a goalkeeper that Sir Botty says shame."
    ],
    "error": [
        "Blast it! Something’s gone sideways. Maybe refresh, or blame the referee.",
        "Sir Botty’s monocle just popped off — something went wrong. Try again in a mo.",
        "Ah fiddlesticks! The data’s gone walkabout. Try once more, would ya?",
        "This is more tragic than England on penalties. Please retry.",
        "Sir Botty encountered a glitch. Or as I call it—VAR in code form."
    ],
    "injury_warning": "{player_name} is carrying a knock. I’d keep an eye on the physio reports.",
    "ban_warning": "{player_name} is suspended. Red cards, yellow cards, or just bad luck?"
}

def get_random_line(category):
    return random.choice(sir_botty_lines[category])
