"""Show rail departures using the Huxley library."""
import click
from rich import box
from rich.console import Console
from rich.padding import Padding
from rich.style import Style
from rich.table import Table

from nationalrail import Huxley


@click.command()
@click.option("--crs", default="wok", help="CRS code for station.")
def get_departures(crs: str) -> None:
    """Display plain-text table of upcoming departures from a named station."""
    station = Huxley(crs=crs, rows=10, endpoint="departures")
    yellow = Style(color="#e2dc84")
    console = Console(width=64)

    board = Table(
        box=box.SIMPLE,
        style="white on black",
        header_style="white on navy_blue",
        collapse_padding=True,
    )
    board.add_column("Time", justify="left", style="on black", width=5)
    board.add_column("Destination", justify="left", style="gold3 on black", width=32)
    board.add_column("Plat", justify="right", style="on black", no_wrap=True, width=4)
    board.add_column("Expected", justify="right", style="on black", width=10)

    if station.train_services:
        for train in station.train_services:

            destination = Table(box=None, show_header=False, pad_edge=False)
            destination.add_row(train.destination)

            if train.via is not None:
                via: str = f"[white]{train.via}[/white]"
                destination.add_row(via)

            if train.delay_reason and not train.cancel_reason:
                delay: str = f"[white]{train.delay_reason}[/white]"
                destination.add_row(delay)

            if train.platform is None:
                train.platform = "-"

            if train.is_cancelled and train.cancel_reason:
                cancellation: str = f"[white]{train.cancel_reason}[/]"
                destination.add_row(cancellation)

            board.add_row(train.std, destination, train.platform, train.etd)

    console.print(board)

    if board.row_count == 0:
        if station.nrcc_messages:
            for message in station.nrcc_messages:
                output = Padding(message, (0, 6, 1, 6))
                console.print(
                    output, style="gold3 on black", justify="center", width=61
                )
        else:
            no_services: str = "Please check timetable for services\n"
            console.print(
                no_services, style="gold3 on black", justify="center", width=61
            )


if __name__ == "__main__":
    get_departures()  # pylint: disable=no-value-for-parameter
