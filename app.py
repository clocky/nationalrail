from flask import Flask, render_template, send_from_directory, redirect
from nationalrail import Huxley

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True


@app.route("/")
def default():
    return redirect("/departures/wok", code=302)


@app.route("/departures/<crs>")
def departures(crs: str):
    station = Huxley(crs=crs, rows=10, endpoint="departures")
    return render_template("departures.jinja", station=station)


@app.route("/station/<crs>")
def station(crs: str):
    station = Huxley(crs=crs, rows=5, endpoint="departures", expand=True)
    return render_template("station.jinja", station=station)


@app.route("/fonts/<path:path>")
def send_fonts(path):
    return send_from_directory("fonts", path)


@app.route("/style/<path:path>")
def send_css(path):
    return send_from_directory("style", path)


@app.route("/img/<path:path>")
def send_image(path):
    return send_from_directory("img", path)
