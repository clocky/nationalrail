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

    board = Table(box=box.SIMPLE_HEAVY, style="on black")
    board.add_column("Time", justify="left", style=yellow, no_wrap=True)
    board.add_column("Destination", justify="left", style=yellow, width=32)
    board.add_column("Plat", justify="right", style=yellow, no_wrap=True)
    board.add_column("Expected", justify="right", style=yellow, no_wrap=True)

    if station.train_services:
        for service in station.train_services:
            destination = Table(box=None, show_header=False, pad_edge=False)

            destination.add_row(service.destination)
            if service.via is not None:
                destination.add_row(service.via)
            if service.is_cancelled:
                destination.add_row(service.cancel_reason)

            board.add_row(service.std, destination, service.platform, service.etd)

    console = Console()
    console.print(board)


if __name__ == "__main__":
    get_departures()  # pylint: disable=no-value-for-parameter
