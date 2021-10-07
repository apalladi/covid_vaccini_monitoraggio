from matplotlib.font_manager import findfont, FontProperties
from itertools import takewhile
from PIL import ImageFont
import numpy as np
from datetime import datetime


def watermark_specs(figure, watermark):
    # Get the default Matplotlib font
    default_font = findfont(FontProperties(family=["sans-serif"]))

    # Fraction of the image where the Watermark is placed
    figure_fraction = 0.6

    # Get Figure width, height (Pixels)
    figure_wd = figure.get_figwidth() * figure.dpi
    figure_ht = figure.get_figheight() * figure.dpi

    # Get Watermark width (Pixels)
    watermark_wd = int(figure_fraction * figure_wd)

    # Calculate the scaled fontsize - iterate until the text size is
    # larger than the text width and take the max value
    fontsize = max(takewhile(lambda i: ImageFont.truetype(default_font, i)
                   .getsize(watermark)[0] < watermark_wd,
                   range(1, watermark_wd))) - 1
    # Calculate appropriate rotation and convert to degree (r * 180°/pi)
    angle = np.arctan(figure_ht/figure_wd)*(180/np.pi)

    # Multiply by -1 to flip text horizontally
    angle *= -1

    print(f"watermark fontsize: {fontsize}, angle:{round(angle, 2)}")
    return fontsize, angle


def add_watermark(figure, axis_font_size):
    watermark = "github.com/apalladi/covid_vaccini_monitoraggio"
    # Get the scaled watermark fontsize and angle
    fontsize, angle = watermark_specs(figure, watermark)
    figure.text(0.5,
                0.5,
                watermark,
                fontsize=fontsize,
                color="gray",
                alpha=0.25,
                ha="center",
                va="center",
                rotation=angle,
                zorder=0
                )

    # explicit link and last update date at the bottom
    last_update = datetime.today().strftime("%d-%m-%Y %H:%M")
    watermark_btm = r"$\bf{Fonte:}$ "
    watermark_btm += "https://github.com/apalladi/covid_vaccini_monitoraggio"
    watermark_btm += f"\n Ultimo aggiornamento: {last_update}"
    figure.text(0.5,
                -0.06,
                watermark_btm,
                fontsize=axis_font_size,
                color="darkslategray",
                ha="center",
                va="bottom"
                )
