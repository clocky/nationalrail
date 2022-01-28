from flask import Flask, render_template, send_from_directory
from nationalrail import Huxley

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True


@app.route("/departures/<crs>")
def departures(crs: str):
    station = Huxley(crs=crs, rows=10, endpoint="departures")
    return render_template("departures.html", station=station)


@app.route("/fonts/<path:path>")
def send_fonts(path):
    return send_from_directory("fonts", path)


@app.route("/style/<path:path>")
def send_css(path):
    return send_from_directory("style", path)
