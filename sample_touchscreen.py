"""Display plain-text table of upcoming departures from a named station."""
import click
import dateutil
from PIL import Image, ImageDraw, ImageFont

from nationalrail import Color, Display, Font, Huxley


def draw_headers(draw: ImageDraw.ImageDraw, location: str):
    """Draw headers for departure board."""
    draw.text((Display.MARGIN - 4, 14), "Time", Color.WHITE, Font.INTER_M, "la")
    draw.text((Display.MARGIN + 96, 14), "Destination", Color.WHITE, Font.INTER_M, "la")
    draw.text((Display.WIDTH - 224, 14), "Plat", Color.WHITE, Font.INTER_M, "ra")
    draw.text((Display.WIDTH - 48, 14), "Expected", Color.WHITE, Font.INTER_M, "ra")
    draw.text((400, 432), location, Color.WHITE, Font.INTER_L, anchor="ma")


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
    message: str = nrcc_messages[0]
    lines = get_multiline_text(
        message, Font.DOTMATRIX, Display.WIDTH - (Display.MARGIN * 4)
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
                draw.ellipse([(x, y), (x + 2, y + 2)], fill=Color.BACKLIGHT)


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
        if service.std:
            draw_led(draw, (Display.LEFT, offset), service.std)

        # Draw the destination
        if service.destination:
            destination: str = service.destination
            via: str = service.via

            draw_led(draw, (Display.LEFT + 100, offset), destination)
            if via is not None and line < Display.LINES:
                draw_led(draw, (Display.LEFT + 100, offset + Display.LINE_HEIGHT), via)
                line = line + 1

        # Draw the platform
        if service.platform:
            draw_led(draw, (Display.WIDTH - 224, offset), service.platform, "rt")

        # Draw the estimated time of departure
        if service.etd:
            etd: str = service.etd
            draw_led(draw, (Display.WIDTH - Display.MARGIN, offset), etd, "rt")

            offset = 60 + (line * Display.LINE_HEIGHT)
            if service.delay_reason:
                delay_reason = service.delay_reason.partition("delayed by")
                reason = f"Service delayed due to {delay_reason[2].strip()}"
                lines = get_multiline_text(reason, Font.DOTMATRIX, 432)
                for number, text in enumerate(lines):
                    y = offset + Display.LINE_HEIGHT + (number * Display.LINE_HEIGHT)
                    draw.text(
                        xy=(Display.LEFT + 100, y),
                        text=text.strip(),
                        fill=Color.YELLOW,
                        font=Font.DOTMATRIX,
                    )
                    line = line + 1

            elif etd == "Cancelled" and service.cancel_reason:
                cancel_reason = service.cancel_reason.partition("because of")
                reason = f"Service cancelled due to {cancel_reason[2].strip()}"

                if line < Display.LINES:
                    lines = get_multiline_text(reason, Font.DOTMATRIX, 432)
                    for number, text in enumerate(lines):
                        y = (
                            offset
                            + Display.LINE_HEIGHT
                            + (number * Display.LINE_HEIGHT)
                        )
                        draw.text(
                            xy=(Display.LEFT + 100, y),
                            text=text.strip(),
                            fill=Color.YELLOW,
                            font=Font.DOTMATRIX,
                        )
                        line = line + 1

        line = line + 1
        if line > Display.LINES:
            break


def draw_station_board(services) -> None:
    """Render station information to PNG using Pillow library."""
    img = Image.new("RGB", (Display.WIDTH, Display.HEIGHT))
    draw = ImageDraw.Draw(img)

    draw_headers(draw, services.location_name)
    draw_led_display(draw, lines=10)

    if services.train_services:
        draw_services(draw, services.train_services)
    elif services.bus_services:
        draw_services(draw, services.bus_services)
    elif services.nrcc_messages:
        draw_nrcc_messages(draw, services.nrcc_messages)
    else:
        message = "Please Check Timetable for Services"
        draw_led(draw, (400, 174), message, "mt")

    draw_timestamp(draw, services.generated_at)
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
    services = Huxley(crs=crs, rows=10, expand=False)
    draw_station_board(services)


if __name__ == "__main__":
    get_departures()  # pylint: disable=no-value-for-parameter
