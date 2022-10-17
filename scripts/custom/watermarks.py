from datetime import datetime
from itertools import takewhile

import numpy as np
from matplotlib.font_manager import FontProperties, findfont
from PIL import ImageFont

from custom.plots import palette

url = "github.com/apalladi/covid_vaccini_monitoraggio"


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


def add_watermark(figure):
    # Get the scaled watermark fontsize and angle
    fontsize, angle = watermark_specs(figure, url)
    figure.text(0.5,
                0.5,
                url,
                fontsize=fontsize,
                color=palette[-1],
                alpha=0.50,
                ha="center",
                va="center",
                rotation=angle,
                zorder=0)


def add_last_updated(fig, ax, dati="ISS", y=-0.050):
    last_update = datetime.today().strftime("%d-%m-%Y alle %H:%M")
    src = r"$\bf{Fonti:}$ "
    src += f"{dati}, {url}\n"
    src += f"Ultimo aggiornamento: {last_update}"
    fig.text(0.50,
             y,
             s=src,
             ha="center",
             fontsize=ax.xaxis.label.get_fontsize())
