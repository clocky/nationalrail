from nationalrail import Huxley
from rich.table import Table
from rich.console import Console
from rich.style import Style
from rich import box

import click


@click.command()
@click.option("--crs", default="wok", help="CRS code for station.")
def get_departures(crs: str) -> None:
    """Display plain-text table of upcoming departures from a named station."""
    station = Huxley(crs=crs, rows=10, endpoint="departures")
    yellow = Style(color="#e2dc84")
    console = Console(width=64)

    board = Table(box=box.SIMPLE_HEAVY)
    board.add_column("Time", justify="left", style=yellow, no_wrap=True)
    board.add_column("Destination", justify="left", style=yellow, width=32)
    board.add_column("Plat", justify="right", style=yellow, no_wrap=True)
    board.add_column("Expected", justify="right", style=yellow, no_wrap=True)

    if station.train_services:
        for train in station.train_services:
            destination = Table(box=None, show_header=False, pad_edge=False)

            destination.add_row(train.destination)
            if train.via is not None:
                destination.add_row(train.via)
            if train.is_cancelled and train.cancel_reason:
                destination.add_row(train.cancel_reason_short)

            board.add_row(train.std, destination, train.platform, train.etd)
    elif station.nrcc_messages:
        for message in station.nrcc_messages:
            board.add_row("", message)

    console.print(board)
    if board.row_count == 0:
        no_services: str = "Please check timetable for services"
        console.print(no_services, style=yellow, justify="center")


if __name__ == "__main__":
    get_departures()  # pylint: disable=no-value-for-parameter
