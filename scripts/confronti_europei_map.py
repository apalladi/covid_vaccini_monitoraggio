# -*- coding: utf-8 -*-
import warnings
from datetime import date, datetime
from os import chdir, path
from string import ascii_lowercase

import geopandas as gpd
import mapclassify
import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.collections import PatchCollection
from matplotlib.colors import to_rgb
from matplotlib.offsetbox import AnchoredText
from matplotlib.patches import Path, PathPatch
from matplotlib.patches import Polygon as MpPolygon
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from mpl_toolkits.basemap import Basemap
from shapely.geometry import Polygon as ShapPolygon
from shapely.ops import unary_union

from custom.plots import palette
from custom.plots_confronti import (compute_vaccini_decessi_eu, fit_model,
                                    import_epidem_data, import_vaccines_data,
                                    paesi_abitanti_eu)


def get_map_labels(countries_df, extent_polygon, basemap_map, adm0_a3_it):
    """ Get map labels """

    map_labels = []
    countries_df_clip = gpd.clip(countries_df, extent_polygon)
    for _, row in countries_df_clip.iterrows():
        if row["ADM0_A3_IT"] in adm0_a3_it.values():
            label_ctx = row["geometry"].representative_point()
            label_ctx = basemap_map(label_ctx.x, label_ctx.y)
            labelx, labely = label_ctx[0], label_ctx[1]
            if row["ADM0_A3_IT"] == "LUX":
                labelx, labely = labelx + 100000, labely
            if row["ADM0_A3_IT"] == "CYP":
                labelx, labely = labelx, labely - 110000
            if row["ADM0_A3_IT"] == "MLT":
                labelx, labely = labelx, labely - 55000
            map_labels.append((row["ADM0_A3_IT"], (labelx, labely)))
    return map_labels


def get_eu_patches(eu_countries, basemap_map):
    """ Get EU-27 patches"""
    eu_patches = []
    eu_colors = []
    for _, row in eu_countries.iterrows():
        geom = row["geometry"]
        if geom.geom_type == "MultiPolygon":
            for part in geom:
                coords = np.array([basemap_map(cd[0], cd[1]) for cd in part.exterior.coords[:]])
                eu_patches.append(MpPolygon(coords, True))
                eu_colors.append(row["Biv_color"])
        else:
            coords = np.array([basemap_map(cd[0], cd[1]) for cd in geom.exterior.coords[:]])
            eu_patches.append(MpPolygon(coords, True))
            eu_colors.append(row["Biv_color"])
    return eu_patches, eu_colors


def get_wld_patches(countries_df, eu_countries, basemap_map):
    """ Get world patches"""
    wld_patches = []
    for _, row in countries_df.iterrows():
        if row["ADM0_A3_IT"] not in eu_countries["ADM0_A3_IT"]:
            geom = row["geometry"]
            if geom.geom_type == "MultiPolygon":
                for part in geom:
                    coords = np.array([basemap_map(c[0], c[1]) for c in part.exterior.coords[:]])
                    wld_patches.append(MpPolygon(coords, True))
            else:
                coords = np.array([basemap_map(c[0], c[1]) for c in geom.exterior.coords[:]])
                wld_patches.append(MpPolygon(coords, True))
    return wld_patches


# Source: https://sgillies.net/2010/04/06/painting-punctured-polygons-with-matplotlib.html
def ring_coding(ob):
    # The codes will be all "LINETO" commands, except for "MOVETO"s at the
    # beginning of each subpath
    n = len(ob.coords)
    codes = np.ones(n, dtype=Path.code_type) * Path.LINETO
    codes[0] = Path.MOVETO
    return codes


def pathify(polygon):
    # Convert coordinates to path vertices. Objects produced by Shapely's
    # analytic methods have the proper coordinate order, no need to sort.
    vertices = np.concatenate(
                    [np.asarray(polygon.exterior)]
                    + [np.asarray(r) for r in polygon.interiors])
    codes = np.concatenate(
                [ring_coding(polygon.exterior)]
                + [ring_coding(r) for r in polygon.interiors])
    return Path(vertices, codes)


def plot_map_corr_vaccini_decessi(show=False):

    warnings.filterwarnings("ignore")

    # Sequential bivariate color schemes
    # https://www.joshuastevens.net/cartography/make-a-bivariate-choropleth-map/
    map_colors_1 = {"A2": "#6c83b5", "B2": "#567994", "C2": "#2a5a5b",
                    "A1": "#b5c0da", "B1": "#90b2b3", "C1": "#5a9178",
                    "A0": "#e8e8e8", "B0": "#b8d6be", "C0": "#73ae80"}

    texts_fontsize = 12
    admin_fontsize = 12
    title_fontsize = 14
    black_color = "#1A2421"
    ocean_color = '#EBF4FA'

    output_map_colors = map_colors_1

    bivariate_letters = {index: letter.upper() for index, letter in enumerate(ascii_lowercase, start=0)}
    bivariate_legend = np.array([to_rgb(rgb) for rgb in list(output_map_colors.values())]).reshape(3, 3, 3)

    # Europe extent
    lon_min, lat_min, lon_max, lat_max = -15.5, 33, 40, 71

    # Extent polygon
    extent_polygon = ShapPolygon([(lon_min, lat_min),
                                  (lon_max, lat_min),
                                  (lon_max, lat_max),
                                  (lon_min, lat_max),
                                  (lon_min, lat_min)])

    # Map Classifier
    map_classifier = mapclassify.JenksCaspall.make(k=3)

    # Create a dataframe with Vaccinated and deaths
    vacc_dec_2021 = pd.DataFrame(zip(paesi_abitanti_eu.keys(), vacc_res, dec_res),
                                 columns=["Country", "Vax", "Dth"])

    # Add country abbreviation column
    vacc_dec_2021["ADM0_A3_IT"] = vacc_dec_2021.apply(lambda row: adm0_a3_it[row["Country"]], axis=1)

    # Open 50m World Countries from natural earth
    countries_df = gpd.read_file("data/ne_50m_admin_0_countries.shp")

    # Get borders recognized by Italy
    countries_df = countries_df.dissolve(by="ADM0_A3_IT", aggfunc="last").reset_index()

    # Get European countries
    eu_countries = pd.merge(countries_df, vacc_dec_2021, left_on="ADM0_A3_IT",
                            right_on="ADM0_A3_IT")[["ADM0_A3_IT", "Country", "Vax", "Dth", "geometry"]]

    # Create the bivariate classes
    eu_countries["Dth_class"] = eu_countries[["Dth"]].apply(map_classifier).astype(str)
    eu_countries["Vax_class"] = eu_countries[["Vax"]].apply(map_classifier)
    eu_countries["Vax_class_lett"] = eu_countries.apply(lambda row: bivariate_letters[row["Vax_class"]], axis=1)
    eu_countries["Biv_class"] = eu_countries["Vax_class_lett"].str.cat(eu_countries["Dth_class"])
    eu_countries["Biv_color"] = eu_countries.apply(lambda row: output_map_colors[row["Biv_class"]], axis=1)

    fig = plt.figure(figsize=(14, 14))
    ax = plt.subplot(111)

    # Remove white margins
    ax.set_axis_off()
    ax.margins(0)

    # Create a map, set projection to aea
    basemap_map = Basemap(resolution="l", projection="aea", width=5000000, height=4500000,
                          lat_1=45, lat_2=60, lon_0=16, lat_0=53)

    # Draw parallels and meridians
    dashes = [5, 7]
    basemap_map.drawparallels(np.arange(-80., 81., 20.),
                              dashes=dashes,
                              linewidth=0.5,
                              color="grey")
    basemap_map.drawmeridians(np.arange(-180., 181., 20.),
                              dashes=dashes,
                              linewidth=0.5,
                              color="grey")

    # Map boundary
    xx_min, xx_max = ax.get_xbound()
    yy_min, yy_max = ax.get_ybound()
    map_extent_polygon = ShapPolygon([(xx_min, yy_min),
                                      (xx_max, yy_min),
                                      (xx_max, yy_max),
                                      (xx_min, yy_max),
                                      (xx_min, yy_min)])
    # Get EU-Countries patches
    eu_patches, eu_colors = get_eu_patches(eu_countries, basemap_map)

    # Get World-Countries patches
    wld_patches = get_wld_patches(countries_df, eu_countries, basemap_map)

    # Get map labels
    map_labels = get_map_labels(countries_df, extent_polygon, basemap_map, adm0_a3_it)

    # Add World countries
    ax.add_collection(PatchCollection(wld_patches,
                                      facecolor="whitesmoke",
                                      edgecolor=black_color,
                                      linewidths=0.25))

    # Add Bivariate map
    ax.add_collection(PatchCollection(eu_patches,
                                      facecolor=eu_colors,
                                      edgecolor=black_color,
                                      linewidths=0.6))

    # Fade effect
    eu_patches_union = unary_union([ShapPolygon(eu_patch.xy)
                                   for eu_patch in eu_patches])

    fade_path = pathify(map_extent_polygon.buffer(100000).difference(eu_patches_union)[0])
    fade_patch = PathPatch(fade_path, facecolor='white', alpha=0.6)
    ax.add_patch(fade_patch)

    # Add EU-countries labels
    for label in map_labels:
        ax.annotate(label[0], (label[1][0], label[1][1]),
                    color=black_color,
                    fontsize=admin_fontsize,
                    ha="center",
                    va="center",
                    path_effects=[pe.withStroke(linewidth=2,
                                                foreground=ocean_color)])

    # Add map title
    title = "Frazione di vaccinati vs decessi nei 27 Paesi dell'UE dal 22/09/2021"
    map_title = AnchoredText(title,
                             prop=dict(color=black_color,
                                       fontsize=title_fontsize,
                                       weight="bold",
                                       style="italic",
                                       ha="center"),
                             borderpad=0,
                             frameon=False,
                             loc=2)
    ax.add_artist(map_title)

    # Add map credits
    map_sources = AnchoredText("Fonti: John Hopkins University, Our World in Data, Natural Earth",
                               prop=dict(color=black_color,
                                         fontsize=texts_fontsize-2),
                               borderpad=0.,
                               frameon=False,
                               loc=3)
    ax.add_artist(map_sources)

    # Add map author
    map_author = AnchoredText("Autore: Ivan D'Ortenzio\nProiezione: Albers Equal Area",
                              prop=dict(color=black_color,
                                        fontsize=texts_fontsize-2,
                                        ha="right"),
                              borderpad=0.,
                              frameon=False,
                              loc=4)
    ax.add_artist(map_author)

    # Add watermark
    fig.text(0.88, 0.425,
             "github.com/apalladi/covid_vaccini_monitoraggio",
             fontsize=16,
             alpha=0.50,
             color=palette[-1],
             va="center",
             rotation="vertical")

    # Add last update date
    last_update = datetime.today().strftime("%d-%m-%Y %H:%M")
    map_date = AnchoredText(f"Ultimo aggiornamento: {last_update}",
                            prop=dict(color=black_color,
                                      fontsize=texts_fontsize-2),
                            borderpad=0.,
                            frameon=False,
                            loc=1)
    ax.add_artist(map_date)

    # Add bivariate map legend
    map_legend = inset_axes(ax, "25%", "20%",
                            loc="upper left",
                            bbox_to_anchor=(0, 0., 0.98, 0.95),
                            bbox_transform=ax.transAxes)
    map_legend.imshow(bivariate_legend, extent=(0, 1, 0, 1))
    map_legend.set_xticks([0.16, 0.5, 0.83])
    map_legend.set_yticks([0.16, 0.5, 0.83])
    map_legend.tick_params(axis=u"both", which=u"both", length=0)
    map_legend.set_xticklabels(["Basso", "", "Alto"],
                               color=black_color,
                               fontsize=texts_fontsize)
    map_legend.set_yticklabels(["Basso", "", "Alto"],
                               color=black_color,
                               rotation=90,
                               va="center",
                               fontsize=texts_fontsize)
    map_legend.plot(1, 0, ">", color=black_color,
                    transform=map_legend.get_yaxis_transform(),
                    clip_on=False)
    map_legend.plot(0, 1, "^", color=black_color,
                    transform=map_legend.get_xaxis_transform(),
                    clip_on=False)
    map_legend.spines["left"].set_linewidth(1.5)
    map_legend.spines["left"].set_color(black_color)
    map_legend.spines["bottom"].set_linewidth(1.5)
    map_legend.spines["bottom"].set_color(black_color)
    map_legend.spines["top"].set_color(black_color)
    map_legend.spines["right"].set_color(black_color)
    map_legend.set_facecolor((0, 0, 0, 0))

    # Add Vax legend
    vax_array = bivariate_legend[2:, :, :]
    vax_legend = inset_axes(ax, "10%", "5%",
                            loc="upper left",
                            bbox_to_anchor=(0.25, 0, 1.10, 0.96),
                            bbox_transform=ax.transAxes)
    vax_legend.imshow(vax_array, extent=(0, 1, 0, 0.2))
    vax_legend.set_xlabel("% Vaccinati",
                          color=black_color,
                          fontsize=texts_fontsize)
    vax_legend.set_xticks([])
    vax_legend.set_yticks([])
    vax_legend.set_xticklabels([])
    vax_legend.set_yticklabels([])

    # Add Dth legend
    dth_array = np.fliplr(bivariate_legend[:, :1, :].reshape(1, 3, 3))
    dth_legend = inset_axes(ax, "10%", "5%",
                            loc="upper left",
                            bbox_to_anchor=(0.25, 0, 1.10, 0.90),
                            bbox_transform=ax.transAxes)

    dth_legend.imshow(dth_array, extent=(0, 1, 0, 0.2))
    dth_legend.set_xlabel("Decessi per mln",
                          color=black_color,
                          fontsize=texts_fontsize)
    dth_legend.set_xticks([])
    dth_legend.set_yticks([])
    dth_legend.set_xticklabels([])
    dth_legend.set_yticklabels([])

    # Add the scatter plot
    ax_scatter = inset_axes(ax, "25%", "20%",
                            loc="upper right",
                            bbox_to_anchor=(0, 0., 0.98, 0.95),
                            bbox_transform=ax.transAxes)

    ax_scatter.scatter(eu_countries["Vax"],
                       eu_countries["Dth"],
                       color=eu_countries["Biv_color"],
                       marker="h",
                       edgecolor="white",
                       linewidth=0.25)

    # linear fit
    x_grid, y_grid, score = fit_model(vacc_res, dec_res)

    # calcola coefficiente di correlazione (pearson)
    corr_coeff = round(np.corrcoef(vacc_res, dec_res)[0, 1], 2)

    ax_scatter.plot(x_grid, y_grid, linestyle="--", color=palette[1])

    ax_scatter.set_ylabel("Decessi per mln",
                          color=black_color,
                          fontsize=texts_fontsize)
    ax_scatter.set_xlabel("% Vaccinati al 22/09/2021",
                          color=black_color,
                          fontsize=texts_fontsize)
    ax_scatter.set_yticklabels(["-70", "0", "200", "400", "600", "800"],
                               color=black_color,
                               fontsize=texts_fontsize)
    ax_scatter.set_xticklabels(["0%", "20%", "40%", "60%", "80%", "100%"],
                               color=black_color,
                               fontsize=texts_fontsize)
    ax_scatter.spines["top"].set_color(black_color)
    ax_scatter.spines["bottom"].set_color(black_color)
    ax_scatter.spines["left"].set_color(black_color)
    ax_scatter.spines["right"].set_color(black_color)
    ax_scatter.set_ylim(-70, )
    ax_scatter.set_xlim(0, 100)

    # Annotate r and R^2
    ax_scatter_legend = AnchoredText(f"$r={corr_coeff}$\n$R^2={score}$",
                                     prop=dict(color=black_color,
                                               fontsize=texts_fontsize-2,
                                               ha="left"),
                                     borderpad=0,
                                     frameon=False,
                                     loc=1)
    ax_scatter.add_artist(ax_scatter_legend)

    # Save the map
    fig.savefig("../risultati/vaccini_decessi_EU_map.png",
                dpi=300,
                bbox_inches="tight",
                pad_inches=0,
                facecolor=ocean_color)
    if show:
        plt.show()


if __name__ == "__main__":
    # Set work directory for the script
    scriptpath = path.dirname(path.realpath(__file__))
    chdir(scriptpath)

    adm0_a3_it = {"Austria": "AUT", "Belgium": "BEL", "Bulgaria": "BGR", "Cyprus": "CYP",
                  "Croatia": "HRV", "Denmark": "DNK", "Estonia": "EST", "Finland": "FIN",
                  "France": "FRA", "Germany": "DEU", "Greece": "GRC", "Ireland":"IRL",
                  "Italy": "ITA", "Latvia": "LVA", "Lithuania": "LTU", "Luxembourg": "LUX",
                  "Malta": "MLT", "Netherlands": "NLD", "Poland": "POL", "Portugal": "PRT",
                  "Czechia": "CZE", "Romania": "ROU", "Slovakia": "SVK", "Slovenia": "SVN",
                  "Spain": "ESP", "Sweden": "SWE", "Hungary": "HUN"}

    # importa dati
    _, df_deaths, _ = import_epidem_data()
    df_vacc = import_vaccines_data()

    # recupera dati vaccini vs. decessi
    # da inizio autunno (22 settembre 2021)
    window = abs((date.today() - date(2021, 9, 22)).days)

    # recupera dati per la finestra temporale selezionata
    vacc_res, dec_res = compute_vaccini_decessi_eu(df_vacc, df_deaths,
                                                   window, fully=False)

    # plot mappa bivariata
    plot_map_corr_vaccini_decessi()
