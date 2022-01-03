"""Display plain-text table of upcoming departures from a named station."""
import json
from zoneinfo import ZoneInfo
from datetime import datetime
from urllib.parse import urljoin
from PIL import Image, ImageFont, ImageDraw

import requests
import click

API = "https://huxley2.azurewebsites.net"
DOTMATRIX = ImageFont.truetype("./fonts/Dot Matrix Regular.ttf", 10)
DOTMATRIX_LG = ImageFont.truetype("./fonts/Dot Matrix Bold.ttf", 10)
DOTMATRIX_XL = ImageFont.truetype("./fonts/Dot Matrix Bold Tall.ttf", 10)


def get_service(service_id: str) -> dict:
    """Get service details for a given service ID."""
    service = {}
    url = urljoin(API, f"/service/{service_id}/")
    try:
        response = requests.get(url)
        service = response.json()
    except ValueError as error:
        print(f'Error: No service found for service ID "{service_id}". ')
        raise SystemExit from error
    return service


def get_calling_points(service_id: str) -> list:
    """Get calling points for a given service ID"""
    calling_points = []
    subsequent_calling_points = get_service(service_id)["subsequentCallingPoints"]
    for calling_point in subsequent_calling_points[0]["callingPoint"]:
        calling_points.append(calling_point["locationName"])

    return calling_points


def get_train_services(
    crs: str, endpoint: str, realtime: bool = True, expand: bool = False, rows: int = 10
) -> dict:
    """Get train services for a given CRS code."""
    train_services = {}
    if realtime:
        url = urljoin(API, f"/{endpoint}/{crs}/{rows}?expand={expand}")
        try:
            response = requests.get(url)
            train_services = response.json()
        except ValueError as error:
            print(f'Error: No listed train services for CRS code "{crs}". ')
            raise SystemExit from error
    else:
        try:
            with open(f"./json/{crs.lower()}.json", encoding="utf-8") as local_json:
                train_services = json.load(local_json)
        except FileNotFoundError as error:
            print(f"Error: No JSON file found for {crs}")
            raise SystemExit from error
    return train_services


def get_service_board(crs: str, realtime: bool = True) -> dict:
    """Retrieve details of a specific service"""
    service = {}
    services = get_train_services(
        crs, endpoint="departures", realtime=realtime, rows=1, expand=True
    )
    if services["trainServices"]:
        train_service = services["trainServices"][0]
        service = {
            "std": train_service["std"],
            "etd": train_service["etd"],
            "destination": train_service["destination"][0]["locationName"],
            "is_cancelled": train_service["isCancelled"],
            "cancel_reason": train_service["cancelReason"],
            "calling_points": train_service["subsequentCallingPoints"][0][
                "callingPoint"
            ],
            "operator": train_service["operator"],
        }
    else:
        # Only shown when no services are running (e.g. during early hours)
        service = {
            "std": services["generatedAt"],
            "etd": "00:00",
            "calling_points": [],
            "operator": "",
            "destination": services["locationName"],
        }

    return service


def get_departure_board(crs: str, realtime=True, rows: int = 3) -> list:
    """Get departure board for a given CRS code."""
    departures = []
    services = get_train_services(
        crs, "departures", realtime=realtime, expand=False, rows=rows
    )
    train_services = services["trainServices"]

    if train_services is not None:
        for service in train_services:
            departures.append(
                {
                    "std": service["std"],
                    "destination": service["destination"][0]["locationName"],
                    "etd": service["etd"],
                    "platform": service["platform"],
                    "cancel_reason": service["cancelReason"],
                }
            )
    else:
        departures = []
    return departures


def draw_service_board(service: dict):
    """Render train information to PNG using Pillow library"""
    dotmatrix = ImageFont.truetype("./fonts/Dot Matrix Regular.ttf", 10)
    dotmatrix_lg = ImageFont.truetype("./fonts/Dot Matrix Regular.ttf", 18)
    dotmatrix_xl = ImageFont.truetype("./fonts/Dot Matrix Bold Tall.ttf", 10)
    img = Image.new("RGB", (122, 250))
    draw = ImageDraw.Draw(img)
    draw.text((4, 4), text=service["std"], fill="yellow", font=dotmatrix)
    draw.text((119, 4), text=service["etd"], fill="yellow", font=dotmatrix, anchor="rt")
    draw.text((4, 18), text=service["destination"], fill="yellow", font=dotmatrix_lg)
    draw.text((4, 38), text="Calling at:", fill="yellow", font=dotmatrix)
    for index, calling_point in enumerate(service["calling_points"]):
        draw.text(
            (4, 51 + (index * 12)),
            text=calling_point["locationName"],
            fill="white",
            font=dotmatrix,
        )
    draw.text((4, 240), text=service["operator"], fill="yellow", font=dotmatrix_xl)
    img.save("./signage.png")
    return True


def get_reason(cancel_reason: str) -> str:
    """Create a concise string describing the reason for a cancellation."""
    parse = cancel_reason.partition("because of a")
    reason = parse[2].lstrip().capitalize()
    return reason


def draw_departure_board(departures: list):
    """Render train information to PNG using Pillow library"""
    img = Image.new("RGB", (250, 122))
    draw = ImageDraw.Draw(img)

    # Headers
    draw.text((4, 4), "Time", "white", font=DOTMATRIX)
    draw.text((32, 4), "Destination", "white", font=DOTMATRIX)
    draw.text((175, 4), "Plat", "white", font=DOTMATRIX)
    draw.text((204, 4), "Expected", "white", font=DOTMATRIX)

    baseline: int = 19
    if departures is not None:
        for i, service in enumerate(departures):
            offset = baseline + (i * 15)

            # Only render upt 6 lines of text (to fit on the sign)
            if offset < 103:
                # Scheduled Departure Time
                draw.text(
                    (4, offset), text=service["std"], fill="yellow", font=DOTMATRIX
                )

                # Destination
                draw.text(
                    (32, offset),
                    text=service["destination"],
                    fill="yellow",
                    font=DOTMATRIX,
                )

                # Cancellation reason
                if service["cancel_reason"] is not None:
                    cancel_reason = get_reason(service["cancel_reason"])
                    if (offset + 15) < 103:
                        draw.text(
                            (32, offset + 15),
                            text=cancel_reason,
                            fill="white",
                            font=DOTMATRIX,
                        )
                    baseline = baseline + 15

                # Platform
                if service["platform"] is not None:
                    draw.text(
                        (192, offset),
                        text=service["platform"],
                        fill="yellow",
                        font=DOTMATRIX,
                        anchor="rt",
                    )

                # Estimated Time of Departure
                if service["etd"] not in ["On time", "Cancelled", "Delayed"]:
                    etd = f"Exp {service['etd']}"
                else:
                    etd = service["etd"]

                draw.text(
                    (246, offset),
                    text=etd,
                    fill="yellow",
                    font=DOTMATRIX,
                    anchor="rt",
                )

    time = datetime.now(ZoneInfo("Europe/London")).strftime("%H:%M")

    width, height = draw.textsize(time, DOTMATRIX_XL)
    draw.text(
        ((img.width - width) / 2, img.height - height - 4),
        text=time,
        fill="white",
        font=DOTMATRIX_XL,
    )
    img.save("./signage.png")


@click.command()
@click.option("--crs", default="wok", help="CRS code for station.")
@click.option("--realtime", default=True, help="Use realtime data.")
def get_departures(crs: str, realtime: bool = True):
    """Display plain-text table of upcoming departures from a named station."""
    departures = get_departure_board(crs, realtime=realtime, rows=7)
    draw_departure_board(departures)


if __name__ == "__main__":
    get_departures()  # pylint: disable=no-value-for-parameter
