"""Display plain-text table of upcoming departures from a named station."""
from urllib.parse import urljoin
import requests
import json
import click
import tabulate as tb
from tabulate import tabulate

tb.PRESERVE_WHITESPACE = True

API = "https://huxley2.azurewebsites.net"


def get_train_services(crs: str, endpoint: str, realtime: bool = False) -> dict:
    """Get train services for a given CRS code."""
    train_services = {}
    if realtime:
        url = urljoin(API, f"/{endpoint}/{crs}/")
        try:
            response = requests.get(url)
            train_services = response.json()
        except:
            print("Error: Could not get train services for CRS code.")
            raise SystemExit
    else:
        try:
            with open(f"./json/{crs.lower()}.json", encoding="utf-8") as f:
                train_services = json.load(f)
        except FileNotFoundError:
            print(f"Error: No JSON file found for {crs}")
            raise SystemExit
    return train_services


def get_departure_board(crs: str, realtime: bool = True) -> list:
    """Get departure board for a given CRS code."""
    departures = []
    services = get_train_services(crs, "departures", realtime)
    train_services = services["trainServices"]

    if train_services is not None:
        for service in train_services:
            destination = service["destination"][0]["locationName"]

            if service["isCancelled"] == True:
                cancel_reason = service["cancelReason"]
                destination = f"{destination}\n{cancel_reason}"

            departures.append(
                [
                    service["std"],
                    destination.ljust(32),
                    service["platform"],
                    service["etd"],
                ]
            )
    else:
        departures.append(["", "No scheduled departures", "", ""])
    return departures


@click.command()
@click.option("--crs", default="wok", help="CRS code for station.")
@click.option("--realtime", default=True, help="Use realtime data.")
def get_departures(crs: str, realtime: bool):
    """Display plain-text table of upcoming departures from a named station."""
    departures = get_departure_board(crs, realtime)

    print(
        tabulate(
            departures,
            headers=["Time", "Destination", "Plat", "Expected"],
            colalign=("left", "left", "right", "right"),
            tablefmt="simple",
        )
    )


if __name__ == "__main__":
    get_departures()
