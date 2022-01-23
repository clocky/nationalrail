from dataclasses import dataclass
from PIL import ImageFont


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
    BACKLIGHT: str = "#231e0c"
    WHITE: str = "#ffffff"
