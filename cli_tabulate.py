#!/usr/bin/env python3

"""Show rail departures using the Huxley library."""
import click

from nationalrail import Huxley
from tabulate import tabulate


@click.command()
@click.option("--crs", default="wok", help="CRS code for station.")
def get_departures(crs: str) -> None:
    """Display plain-text table of upcoming departures from a named station."""
    station = Huxley(crs=crs, rows=10, endpoint="departures")

    board: list = []
    headers: list = ["Time", "Destination", "Plat", "Expected"]
    colalign: list = ["left", "left", "right", "right"]

    if station.train_services:
        for train in station.train_services:
            board.append(
                [
                    train.std,
                    route(train.destination, train.via),
                    train.platform,
                    train.etd,
                ]
            )

    elif station.bus_services:
        for bus in station.bus_services:
            board.append([bus.std, route(bus.destination, bus.via), "BUS", bus.etd])

    print(tabulate(board, headers=headers, colalign=colalign))


def route(destination: str, via: str) -> str:
    """Return a route string."""
    route: str = ""
    if via:
        route = f"{destination}\n{via}"
    else:
        route = destination
    return route


if __name__ == "__main__":
    get_departures()  # pylint: disable=no-value-for-parameter
