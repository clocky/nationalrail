"""Display plain-text table of upcoming departures from a named station."""
import textwrap
from urllib.parse import urljoin

import bleach
import click
import dateutil.parser
import requests
from PIL import Image, ImageDraw, ImageFont

API = "https://huxley2.azurewebsites.net"
DOTMATRIX = ImageFont.truetype("./fonts/Dot Matrix Regular.ttf", 10)
DOTMATRIX_LG = ImageFont.truetype("./fonts/Dot Matrix Regular.ttf", 18)
DOTMATRIX_BOLD = ImageFont.truetype("./fonts/Dot Matrix Bold.ttf", 10)


def get_train_services(
    crs: str, endpoint: str, expand: bool = False, rows: int = 1
) -> dict:
    """Get train services for a given CRS code."""
    train_services = {}
    url = urljoin(API, f"/{endpoint}/{crs}/{rows}?expand={expand}")
    try:
        response = requests.get(url)
        train_services = response.json()
    except ValueError as error:
        print(f'Error: No listed train services for CRS code "{crs}". ')
        raise SystemExit from error
    return train_services


def get_service_board(crs: str) -> dict:
    """Retrieve details of a specific service."""
    service = {}
    services = get_train_services(crs, endpoint="departures", rows=1, expand=True)

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
        generated_at = dateutil.parser.isoparse(services["generatedAt"])
        service = {
            "std": generated_at.strftime("%H:%M"),
            "etd": None,
            "calling_points": None,
            "operator": None,
            "nrcc_messages": services["nrccMessages"],
            "destination": services["locationName"],
        }

    return service


def draw_service_board(service: dict):
    """Render train information to PNG using Pillow library."""

    # Create the image
    img = Image.new("RGB", (122, 250))
    draw = ImageDraw.Draw(img)

    # Header
    draw.text((0, 0), service["std"], "yellow", DOTMATRIX)

    # Estimated time of departure
    if service["etd"] is not None:
        color = "white" if service["is_cancelled"] else "yellow"
        draw.text((122, 0), service["etd"], color, DOTMATRIX, "rt")

    # Destination
    if service["destination"] is not None:
        draw.text((0, 14), service["destination"], "yellow", DOTMATRIX_LG)

    # Calling points
    if service["calling_points"] is not None:
        draw.text((0, 36), "Calling at:", "yellow", DOTMATRIX)

        # Loop through available calling points
        for index, calling_point in enumerate(service["calling_points"]):
            offset = 48 + (index * 12)
            if offset <= 226:
                location_name = calling_point["locationName"]
                draw.text((0, offset), location_name, "white", DOTMATRIX)
            else:
                summary = f"{len(service['calling_points']) - index} more stops"
                draw.text((0, offset), summary, "yellow", DOTMATRIX)
                break

    # If there's no calling points, show any NRCC message that were passed

    if service["calling_points"] is None and service["nrcc_messages"] is not None:
        for message in service["nrcc_messages"]:
            sentences = message["value"].split(". ")
            offset = 0
            for sentence in sentences:
                sanitized = bleach.clean(sentence, tags=[], strip=True).strip()
                lines = textwrap.wrap(sanitized, width=26)
                message = "\n".join(lines)

                # Add missing full stops to the end of the message
                if message[-1] != ".":
                    message = message + "."

                draw.multiline_text(
                    (0, 48 + offset), message, "white", DOTMATRIX, spacing=4
                )
                offset = offset + (len(lines) * 12)

    # Operator
    if service["operator"] is not None:
        draw.text((0, 240), service["operator"], "yellow", DOTMATRIX_BOLD)

    # Finally, save the image to disk
    img.save("./signage.png")


@click.command()
@click.option("--crs", default="wok", help="CRS code for station.")
def get_departures(crs: str):
    """Display plain-text table of upcoming departures from a named station."""
    draw_service_board(get_service_board(crs))


if __name__ == "__main__":
    get_departures()  # pylint: disable=no-value-for-parameter
