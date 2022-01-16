"""Display plain-text table of upcoming departures from a named station."""
import datetime as dt
from urllib.parse import urljoin
from dataclasses import dataclass

import bleach
import click
import dateutil.parser
import requests
from PIL import Image, ImageDraw, ImageFont

API = "https://huxley2.azurewebsites.net"


@dataclass
class Font:
    """Constants for font names."""

    DOTMATRIX = ImageFont.truetype("./fonts/Dot Matrix Regular.ttf", 30)
    DOTMATRIX_BOLD = ImageFont.truetype("./fonts/Dot Matrix Bold.ttf", 30)
    DOTMATRIX_BOLD_TALL = ImageFont.truetype("./fonts/Dot Matrix Bold Tall.ttf", 30)
    INTER_M = ImageFont.truetype("./fonts/Inter-Bold.otf", 26)
    INTER_L = ImageFont.truetype("./fonts/Inter-Bold.otf", 36)


@dataclass
class Display:
    """Constants relevant to the display."""

    WIDTH: int = 800
    HEIGHT: int = 480
    MARGIN: int = 48
    RIGHT: int = WIDTH - MARGIN
    LEFT: int = MARGIN
    LINES: int = 7
    LINE_HEIGHT: int = 38


@dataclass
class Color:
    """Constants for color names."""

    YELLOW: str = "#e2dc84"


def get_train_services(
    crs: str, endpoint: str = "departures", rows: int = 1, expand: bool = False
) -> dict:
    """Get train services for a given CRS code."""
    train_services: dict = {}
    url: str = urljoin(API, f"/{endpoint}/{crs}/{rows}?expand={expand}")
    try:
        response: requests.models.Response = requests.get(url)
        train_services = response.json()
    except ValueError as error:
        print(f'Error: No listed train services for CRS code "{crs}". ')
        raise SystemExit from error
    return train_services


def draw_headers(draw: ImageDraw.ImageDraw, location: str):
    """Draw headers for departure board."""
    draw.text((Display.MARGIN - 4, 14), "Time", "white", Font.INTER_M, "la")
    draw.text((Display.MARGIN + 96, 14), "Destination", "white", Font.INTER_M, "la")
    draw.text((Display.WIDTH - 224, 14), "Plat", "white", Font.INTER_M, "ra")
    draw.text((Display.WIDTH - 48, 14), "Expected", "white", Font.INTER_M, "ra")
    draw.text((400, 432), location, "white", Font.INTER_L, anchor="ma")


def draw_timestamp(draw: ImageDraw.ImageDraw, generated_at: str) -> None:
    """Draw timestamp at foot of departure board."""
    iso_time: dt.datetime = dateutil.parser.isoparse(generated_at)
    time: str = iso_time.strftime("%H:%M:%S")
    page: str = "Page 1 of 1"
    draw.text((Display.RIGHT, 402), time, Color.YELLOW, Font.DOTMATRIX_BOLD_TALL, "rt")
    draw.text((Display.LEFT, 402), page, Color.YELLOW, Font.DOTMATRIX_BOLD, "lt")


def draw_nrcc_messages(draw: ImageDraw.ImageDraw, nrcc_messages: list) -> None:
    """Draw any National Rail Communication Centre (NRCC) messages."""
    offset: int = 60
    message: str = nrcc_messages[0]["value"]
    sanitized: str = bleach.clean(message, tags=[], strip=True).strip()
    lines = get_multiline_text(
        sanitized, Font.DOTMATRIX, Display.WIDTH - (Display.MARGIN * 4)
    )
    for line in lines:
        offset = offset + Display.LINE_HEIGHT
        draw_led(draw, (Display.WIDTH / 2, offset), line, "mt")


def draw_led_display(draw: ImageDraw.ImageDraw, lines: int = 10):
    """Draw LED display background texture."""
    for i in range(0, lines):
        offset: int = 60 + (i * Display.LINE_HEIGHT)
        for x in range(Display.LEFT, Display.RIGHT, 3):
            for y in range(offset, offset + 26, 3):
                draw.ellipse([(x, y), (x + 2, y + 2)], fill="#231e0c")


def draw_led(
    draw: ImageDraw.ImageDraw,
    xy: tuple[float, float],
    text: str,
    align: str = "lt",
    font=Font.DOTMATRIX,
):
    draw.text(xy=xy, text=text, fill=Color.YELLOW, font=font, anchor=align)


def draw_services(draw: ImageDraw.ImageDraw, services: list):
    line: int = 0
    for service in services:
        offset = 60 + (line * Display.LINE_HEIGHT)

        # Draw the scheduled time of departure
        if service["std"] is not None:
            draw_led(draw, (Display.LEFT, offset), service["std"])

        # Draw the destination
        if service["destination"] is not None:
            destination: str = service["destination"][0]["locationName"]
            via: str = service["destination"][0]["via"]

            draw_led(draw, (Display.LEFT + 100, offset), destination)
            if via is not None and line < Display.LINES:
                draw_led(draw, (Display.LEFT + 100, offset + Display.LINE_HEIGHT), via)
                line = line + 1

        # Draw the platform
        if service["platform"] is not None:
            draw_led(draw, (Display.WIDTH - 224, offset), service["platform"], "rt")

        # Draw the estimated time of departure
        if service["etd"] is not None:
            etd: str = service["etd"]
            draw_led(draw, (Display.WIDTH - Display.MARGIN, offset), etd, "rt")

            offset = 60 + (line * Display.LINE_HEIGHT)
            if etd == "Delayed" and service["delayReason"] is not None:
                delay_reason = service["delayReason"].partition("delayed by")
                reason = f"Service delayed due to {delay_reason[2].strip()}"
                draw.text(
                    xy=(Display.LEFT + 100, offset + Display.LINE_HEIGHT),
                    text=reason,
                    fill=Color.YELLOW,
                    font=Font.DOTMATRIX,
                )
                line = line + 1
            elif etd == "Cancelled" and service["cancelReason"] is not None:
                cancel_reason = service["cancelReason"].partition("because of")
                reason = f"Service cancelled due to {cancel_reason[2].strip()}"

                lines = get_multiline_text(reason, Font.DOTMATRIX, 480)
                for number, line in enumerate(lines):
                    y = offset + Display.LINE_HEIGHT + (number * Display.LINE_HEIGHT)
                    draw.text(
                        xy=(Display.LEFT + 100, y),
                        text=line.strip(),
                        fill=Color.YELLOW,
                        font=Font.DOTMATRIX,
                    )
                    line = line + 1

        line = line + 1
        if line > Display.LINES:
            break


def draw_station_board(services: dict) -> None:
    """Render station information to PNG using Pillow library."""
    img = Image.new("RGB", (Display.WIDTH, Display.HEIGHT))
    draw = ImageDraw.Draw(img)

    draw_headers(draw, services["locationName"])
    draw_led_display(draw, lines=10)

    if services["trainServices"] is not None:
        draw_services(draw, services["trainServices"])
    elif services["busServices"] is not None:
        draw_services(draw, services["busServices"])
    elif services["nrccMessages"] is not None:
        draw_nrcc_messages(draw, services["nrccMessages"])
    else:
        message = "Please Check Timetable for Services"
        draw_led(draw, (400, 174), message, "mt")

    draw_timestamp(draw, services["generatedAt"])
    img.save("./signage.png")


def get_multiline_text(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list:
    """Split text into lines of a maximum Display.WIDTH."""
    img = Image.new("RGB", (122, 250))
    draw = ImageDraw.Draw(img)

    words: list = text.split(" ")
    lines: list = []
    line: str = ""

    for word in words:
        if draw.textsize(line + " " + word, font)[0] < max_width:
            line = line + " " + word
        else:
            lines.append(line)
            line = word

    lines.append(line)

    return lines


@click.command()
@click.option("--crs", default="wok", help="CRS code for station.")
def get_departures(crs: str) -> None:
    """Display plain-text table of upcoming departures from a named station."""
    services = get_train_services(crs=crs, rows=10, expand=False)
    draw_station_board(services)


if __name__ == "__main__":
    get_departures()  # pylint: disable=no-value-for-parameter
