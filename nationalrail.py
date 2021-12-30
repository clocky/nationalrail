"""Display plain-text table of upcoming departures from a named station."""
import requests
import json
from urllib.parse import urljoin
from tabulate import tabulate

API = "https://huxley2.azurewebsites.net"


def get_train_services(crs: str, endpoint: str, realtime: bool = False) -> dict:
    """Get train services for a given CRS code."""
    train_services = {}
    if realtime:
        url = urljoin(API, f"/{endpoint}/{crs}/")
        response = requests.get(url)
        train_services = response.json()
    else:
        with open(f"./json/{crs.lower()}.json") as f:
            train_services = json.load(f)
    return train_services


def get_departure_board(crs: str, realtime: bool = False) -> list:
    """Get departure board for a given CRS code."""
    departures = []
    services = get_train_services(crs, "departures", realtime)
    train_services = services['trainServices']
    if train_services != None:
        for train in train_services:
            destination = train['destination'][0]['locationName']
            departures.append([train['std'], destination,
                               train['platform'], train['etd']])
    else:
        departures.append(["", "No services found"])
    return departures


if __name__ == "__main__":
    departures = get_departure_board("WOK", True)
    print(tabulate(departures, headers=["Time", "Destination", "Plat", "Expected"],
                   colalign=("left", "left", "right", "right"), tablefmt="simple"))
