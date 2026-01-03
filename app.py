
import os, requests, time
from flask import Flask, render_template_string
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("ODDS_API_KEY", "")
API_URL = "https://api.the-odds-api.com/v4/sports/soccer_epl/odds"

app = Flask(__name__)
previous = {}

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8"/>
    <title>Odds Monitor Demo</title>
    <meta http-equiv="refresh" content="10">
    <style>
        body { font-family: Arial, sans-serif; background:#f6f7fb; }
        h2 { margin: 10px 0; }
        table { border-collapse: collapse; width:100%; background:#fff; }
        th, td { border:1px solid #ddd; padding:8px; text-align:center; }
        th { background:#333; color:#fff; }
        .green { background:#d4edda; }
        .yellow { background:#fff3cd; }
        .red { background:#f8d7da; }
        .small { color:#666; font-size:12px; }
    </style>
</head>
<body>
<h2>Live Odds Monitor (Demo)</h2>
<div class="small">Auto refresh every 10 seconds • Read-only</div>
<table>
    <tr>
        <th>Match</th>
        <th>Current Odds</th>
        <th>Change</th>
        <th>Status</th>
    </tr>
    {% for m in matches %}
    <tr class="{{m.color}}">
        <td>{{m.name}}</td>
        <td>{{m.current}}</td>
        <td>{{m.change}}</td>
        <td>{{m.status}}</td>
    </tr>
    {% endfor %}
</table>
</body>
</html>
'''

@app.route("/")
def index():
    params = {
        "apiKey": API_KEY,
        "regions": "uk",
        "markets": "h2h",
        "oddsFormat": "decimal"
    }
    try:
        res = requests.get(API_URL, params=params, timeout=10)
        data = res.json()
    except Exception:
        data = []

    matches = []
    for g in data[:15]:
        name = f"{g['home_team']} vs {g['away_team']}"
        odds = g["bookmakers"][0]["markets"][0]["outcomes"][0]["price"]
        last = previous.get(name, odds)
        change_pct = round(((odds - last) / last) * 100, 2) if last else 0.0

        if abs(change_pct) > 15:
            color, status = "red", "ALERT"
        elif abs(change_pct) > 5:
            color, status = "yellow", "WATCH"
        else:
            color, status = "green", "NORMAL"

        previous[name] = odds
        matches.append({
            "name": name,
            "current": odds,
            "change": f"{change_pct}%",
            "status": status,
            "color": color
        })

    return render_template_string(HTML, matches=matches)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
