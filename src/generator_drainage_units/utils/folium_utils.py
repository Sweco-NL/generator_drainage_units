import folium
import geopandas as gpd
import matplotlib
import numpy as np
import pandas as pd
import random
from folium.plugins import (
    FeatureGroupSubGroup,
    FloatImage,
    MarkerCluster,
    MeasureControl,
)
from shapely.geometry import LineString, Point, Polygon


def check_map_exists_and_feature_group(
    m: folium.Map = None,
    feature_group: folium.FeatureGroup = None,
    layer_name: str = None,
    show: bool = True,
    control: bool = True,
    z_index: int = 1,
):
    """Two things:
        - checks if map (self.m) exists and if not creates it.
        - creates a feature group (layer) and if input includes feature group, it creates a subgroup
    Input:  * feature_group: an existing feature_group (a subgroup will be created)
                or None (a feature_group will be created)
            * layer_name: string representing name of the layer
            * show: True/False - is the layer selected or not
            * control: True/False - is the layer included in the layercontrol legend
            * z_index: z of the layer (does not always work well...)
    """
    if feature_group is not None:
        fgs = FeatureGroupSubGroup(
            feature_group, name=f" - {layer_name}", show=show, control=control
        )
        fgs.add_to(feature_group)
        return feature_group, fgs
    else:
        fg = folium.FeatureGroup(
            name=layer_name, show=show, control=control, z_index=z_index
        )
        m.add_child(fg)
        return fg, None


def check_fields_aliases(
    df: [pd.DataFrame, pd.Series, gpd.GeoDataFrame, gpd.GeoSeries],
    fields: [list[str], str, bool] = False,
    aliases: [list[str], str] = None,
):
    """Does a check on the tooltips (fields and aliases) and the popups (fields and aliases)"""
    ds = df.copy(deep=True)
    if (type(ds) == gpd.GeoSeries or type(ds) == pd.Series) and "geometry" in ds.index:
        ds = ds.drop(index=["geometry"])
    if (
        type(ds) == gpd.GeoDataFrame or type(ds) == pd.DataFrame
    ) and "geometry" in ds.columns:
        ds = ds.drop(columns=["geometry"])

    table_classes = "table table-hover table-condensed table-responsive"

    # def text_wrapper_20(x):
    #     return '<br>'.join(textwrap.wrap(x, 20))
    #
    def text_wrapper_50(x):
        if len(str(x)) > 50:
            return "<br>".join(textwrap.wrap(x, 50))
        else:
            return x

    if fields is False:
        fields_x = None
    elif fields is True:
        if type(ds) == pd.Series or type(ds) == gpd.GeoSeries:
            fields_x = df.to_frame()
            if aliases is not None and len(aliases) == len(fields):
                fields_x.index = aliases
            else:
                aliases = None
            fields_x = fields_x.to_html(
                classes=table_classes,
                header=False,
                border=0,
                justify="left",
                decimal=".",
                max_rows=15,
            )
        else:
            fields_x = [col for col in df.columns if col != "geometry"]
            if aliases is not None and len(aliases) != len(fields_x):
                aliases = None
    elif isinstance(fields, list) or (isinstance(fields, str) and fields in ds):
        if type(ds) == pd.Series or type(ds) == gpd.GeoSeries:
            fields_x = df[fields].to_frame()
            if aliases is not None and len(aliases) == len(fields):
                fields_x.index = aliases
            else:
                aliases = None
            # fields_x.index = fields_x.index.apply(text_wrapper_20)
            # fields_x = fields_x.apply(text_wrapper_50)
            fields_x = fields_x.to_html(
                classes=table_classes,
                header=False,
                border=0,
                justify="left",
                decimal=".",
            )
        else:
            fields_x = [tip for tip in fields if tip in ds.columns if tip != "geometry"]
            if aliases is not None and len(aliases) != len(fields_x):
                aliases = None
    else:
        fields_x = fields.copy()

    return fields_x, aliases


def add_categorized_color_to_gdf(
    gdf,
    color_column=None,
    colormap="RdBu",
    names=None,
    thresholds=None,
    lower_limit=True,
    upper_limit=True,
    colors=None,
    new_name_column=None,
    new_color_column=None,
    label_unit="",
    label_decimals=2,
):
    if color_column is None:
        raise ValueError("no color given via 'color_column'")
    if color_column not in gdf.columns:
        if not matplotlib.colors.is_color_like("red"):
            raise ValueError(
                f"no color given via 'color_column'. '{color_column}' is not a color"
            )
        gdf[new_name_column] = ""
        gdf[new_color_column] = color_column
        return gdf, [], gdf[new_color_column].unique()
    # no colors, but
    if thresholds is None or gdf[color_column].dtype == object:
        if names is None:
            names = [name for name in gdf[color_column].unique() if name is not None]
        if colors is None or len(names) != len(colors):
            if colormap is not None:
                cmap = matplotlib.cm.get_cmap(colormap)
                colors = [
                    matplotlib.colors.rgb2hex(cmap(float(i) / float(len(names) - 1)))
                    for i in range(len(names))
                ]
            else:
                cmap = matplotlib.cm.get_cmap("hsv")
                colors = [
                    matplotlib.colors.rgb2hex(cmap(float(i) / float(len(names) - 1)))
                    for i in range(len(names))
                ]
                random.shuffle(colors)
        gdf[new_name_column] = "-----------"
        gdf[new_color_column] = "rgba(0,0,0,0)"
        for name, color in zip(names, colors):
            gdf.loc[gdf[color_column] == name, new_name_column] = name
            gdf.loc[gdf[color_column] == name, new_color_column] = color
        gdf[new_name_column] = gdf[new_name_column].astype(str)
    else:
        new_thresholds, names = create_categories_based_on_thresholds(
            thresholds=thresholds,
            lower_limit=lower_limit,
            upper_limit=upper_limit,
            unit=label_unit,
            decimals=label_decimals,
        )
        if colors is None or len(names) != len(colors):
            cmap = matplotlib.cm.get_cmap(colormap)
            colors = [
                matplotlib.colors.rgb2hex(cmap(float(i) / float(len(names) - 1)))
                for i in range(len(names))
            ]
        gdf[new_name_column] = "-----------"
        gdf[new_color_column] = "rgba(0,0,0,0)"
        for ii, (name, color) in enumerate(zip(names, colors)):
            gdf.loc[
                gdf[color_column].between(new_thresholds[ii], new_thresholds[ii + 1]),
                new_name_column,
            ] = name
            gdf.loc[
                gdf[color_column].between(new_thresholds[ii], new_thresholds[ii + 1]),
                new_color_column,
            ] = color

    return gdf, names, colors


def add_labels_to_points_lines_polygons(
    gdf: gpd.GeoDataFrame,
    column: str,
    label_fontsize: int = 14,
    label_unit: str = "",
    label_decimals: int = 2,
    show: bool = True,
    center=True,
    fg=None,
    fgs=None,
):
    gdf = gdf.to_crs(4326).copy()

    if column not in gdf.columns:
        return

    for element_id, element in gdf.iterrows():
        if center:
            html_style1 = f'<div style="font-size: {label_fontsize}pt; color: black">'
        else:
            html_style1 = f'<div style="font-size: {label_fontsize}pt; color: black">'
        if isinstance(element.geometry, Polygon):
            point = element.geometry.representative_point()
        elif isinstance(element.geometry, LineString):
            point = element.geometry.interpolate(0.5, normalized=True)
        elif isinstance(element.geometry, Point):
            point = element.geometry
        else:
            raise ValueError(" * GeoDataFrame does not have the right geometry")

        label_value = element[column]
        if isinstance(label_value, float) and np.isnan(label_value):
            return

        if (
            isinstance(label_value, float) or isinstance(label_value, int)
        ) and label_decimals is not None:
            if label_unit == "%":
                label_str = f"{float(label_value):0.{label_decimals}%}"
            else:
                label_str = f"{float(label_value):0.{label_decimals}f}"
        else:
            label_str = f"{label_value}"
        html_style2 = f"<b>{label_str}{label_unit}</b></div>"
        if center:
            icon = folium.DivIcon(
                icon_size=(200, 50),
                icon_anchor=(-10, 15),
                html=html_style1 + html_style2,
            )
        else:
            icon = folium.DivIcon(
                icon_size=(200, 50),
                icon_anchor=(-10, 20),
                html=html_style1 + html_style2,
            )
        _label = folium.Marker(location=[point.y, point.x], icon=icon, show=show)
        if fgs is not None:
            _label.add_to(fgs)
        else:
            _label.add_to(fg)


def add_basemaps_to_folium_map(m: folium.Map, base_map="Light Mode"):
    m.tiles = None
    basemaps = ["ESRI Luchtfoto", "Dark Mode", "Light Mode", "OpenStreetMap"]
    basemap_types = [
        {
            "tiles": "cartodbpositron",
            "name": "Light Mode",
            "attr": None,
            "control": True,
            "maxNativeZoom": 20,
            "maxZoom": 20,
        },
        {
            "tiles": "openstreetmap",
            "name": "OpenStreetMap",
            "attr": None,
            "control": True,
            "maxNativeZoom": 19,
            "maxZoom": 19,
            "show": True,
        },
        {
            "tiles": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
            "attr": "Esri",
            "name": "ESRI Luchtfoto",
            "control": True,
            "maxNativeZoom": 21,
            "maxZoom": 21,
            "show": True,
        },
        {
            "tiles": "cartodbdark_matter",
            "name": "Dark Mode",
            "attr": None,
            "control": True,
            "maxNativeZoom": 20,
            "maxZoom": 20,
            "show": True,
        },
        {
            "tiles": "Stamen Toner",
            "name": "Stamen Toner",
            "attr": None,
            "control": True,
            "maxNativeZoom": 17,
            "maxZoom": 17,
            "show": True,
        },
    ]

    for bm in basemaps:
        basemap = [o for o in basemap_types if o["name"] == bm][0]
        folium.TileLayer(
            tiles=basemap["tiles"],
            name=basemap["name"],
            attr=basemap["attr"],
            control=basemap["control"],
            maxNativeZoom=basemap["maxNativeZoom"],
            maxZoom=basemap["maxZoom"],
            show=True if basemap["name"] == base_map else False,
        ).add_to(m)
    return m


def add_lines_to_map(
    m: folium.Map,
    lines_gdf: gpd.GeoDataFrame,
    layer_name: str,
    lines: bool = True,
    feature_group: folium.FeatureGroup = None,
    control: bool = True,
    show: bool = True,
    line_color: str = "black",
    line_color_name: str = "XXXXXXXXXXXXXXXX",
    line_weight: int = 2,
    line_opacity: float = 0,
    label: bool = False,
    label_column: str = None,
    label_unit: str = "",
    label_decimals: int = 2,
    label_fontsize: int = 10,
    z_index: int = 1,
    dash_array: str = None,
    tooltip: [list[str], str, bool] = False,
    tooltip_aliases: [list[str], str] = None,
    popup: [list[str], str, bool] = False,
    popup_aliases: [list[str], str] = None,
):
    """
    Voegt lijnen toe aan de kaart
    
    Input:  
            * lines_gdf: Geodataframe with lines
            * layer_name: De naam van de laag zoals deze verschijnt in de lijst met lagen in de kaart
            * feature_group: Vul hier de featuregroup naam in indien je meerdere lagen in één groep plaatst
            * color: Vul hier de kleur van de lijn in. Kies een standaard kleur volgens matplotlib of gebruik een HEX kleurcode
            * weight: de dikte van de lijn
            * line_opacity: Vul een waarde tussen 0.0 (volledig transparant) en 1.0 in (volledig ontransparant)
            * dash_array: geef hier de string met je definitie voor een stippellijn. bijvoorbeeld "10 5" geeft een stippellijn met lijnstukjes lengte 10 en lege stukken met lengte 5
            * label: Kies True als je een label wil weergegeven. label_column vereist
            * label_column: Vul de naam van de kolom in waar de tekst voor je label in staat.
            * label_decimals: Indien je label een getal is, geef hier aan met hoeveel decimalen deze weergegeven moet worden
            * label_fontsize: Kies de fontsize van de label tekst
            * show: Geef met True of False aan of de laag standaard weergegeven moet worden bij openen van de kaart.
            * control: Geef met True of False aan of de laag opgenomen moet worden in de lijst met lagen
            * tooltip: Geef in een list aan welke kolommen weergegeven moeten worden als je met je muis over de feature in de kaart beweegt. Bij True worden alle kolommen weergegeven, bij False geen.
            * tooltip_aliases: Geef een list met alisases op voor de kolomnamen zoals deze verschijnen in de kaart. Het eerste item uit je list is de alias voor het eerste item in de list zoals opgegeven bij tooltip.
            * popup: Geeft de informatie bij klikken op de fetaure in de kaart. Werking; zie tooltip.
            * popup_alisases: Geeft aliases voor de popup. Werking; zie tooltip_aliases
            * z_index: bij meerdere lagen; geef met een waarde aan welke laag op de voorgrond weergegeven wordt
            
    Output
            * feature_group
    """
    fg, fgs = check_map_exists_and_feature_group(
        m=m,
        feature_group=feature_group,
        layer_name=layer_name,
        show=show,
        control=control,
        z_index=z_index,
    )
    lines_gdf_copy = lines_gdf.copy(deep=True)
    lines_columns = [
        c for c in lines_gdf_copy.columns if c not in [line_color, line_color_name]
    ]
    lines_gdf_copy.geometry = lines_gdf.geometry.to_crs(4326)

    if line_color == "line_color":

        def style_function(feature):
            color = feature["properties"]["line_color"]
            return {
                "color": color,
                "weight": line_weight,
                "line_opacity": line_opacity,
                "dashArray": dash_array,
            }

        def highlight_function(feature):
            _line_color = feature["properties"].get(line_color, line_color)
            return {
                "color": "yellow",
                "weight": max(line_weight * 2.0, 1.5),
                "lineOpacity": 1.0,
            }
    else:

        def style_function(feature):
            return {
                "color": line_color,
                "weight": line_weight,
                "line_opacity": line_opacity,
                "dashArray": dash_array,
            }

        def highlight_function(feature):
            _line_color = feature["properties"].get(line_color, line_color)
            return {
                "color": "yellow",
                "weight": max(line_weight * 2.0, 1.5),
                "lineOpacity": 1.0,
            }

    if lines:
        _lines = folium.GeoJson(
            data=lines_gdf_copy.to_json(),
            style_function=style_function,
            highlight_function=highlight_function,
        ).add_to(fg)

        tooltip_fields, tooltip_aliases = check_fields_aliases(
            df=lines_gdf[lines_columns], fields=tooltip, aliases=tooltip_aliases
        )
        popup_fields, popup_aliases = check_fields_aliases(
            df=lines_gdf[lines_columns], fields=popup, aliases=popup_aliases
        )

        if tooltip_fields is not None:
            folium.GeoJsonTooltip(
                fields=tooltip_fields, aliases=tooltip_aliases, labels=True
            ).add_to(_lines)
        if popup_fields is not None:
            folium.GeoJsonPopup(
                fields=popup_fields, aliases=popup_aliases, labels=True
            ).add_to(_lines)

    if label:
        add_labels_to_points_lines_polygons(
            gdf=lines_gdf_copy,
            column=label_column,
            label_fontsize=label_fontsize,
            label_unit=label_unit,
            label_decimals=label_decimals,
            show=show,
            center=True,
            fg=fg,
        )
    if feature_group is None:
        m.add_child(fg)
        return m
    else:
        return fg


def add_categorized_lines_to_map(
    m: folium.Map,
    lines_gdf: gpd.GeoDataFrame,
    feature_group: folium.FeatureGroup = None,
    control: bool = True,
    layer_name: str = "categorized lines",
    lines: bool = True,
    line_color_column: str = "black",
    line_color_category_names: list[str] = None,
    line_color_category_thresholds: list[float] = None,
    line_color_category_lower_limit: bool = True,
    line_color_category_upper_limit: bool = True,
    line_color_category_colors: list[str] = None,
    line_color_cmap: str = None,
    line_weight: int = 2,
    label: bool = False,
    label_column: str = None,
    label_unit: str = "",
    label_decimals: int = 2,
    label_fontsize: int = 10,
    z_index: int = 1,
    dash_array: str = None,
    legend: bool = False,
    legend_name: str = None,
    legend_location: str = "top",
    show: bool = True,
    tooltip: [list[str], str, bool] = False,
    tooltip_aliases: [list[str], str] = None,
    popup: [list[str], str, bool] = False,
    popup_aliases: [list[str], str] = None,
):
    """Voegt lijnen toe aan de kaart met kleuren zoals gedefinieerd in de categorieen. Input zoals in add_lines_to_map met als toevoeging:
    * color_column: de kolomnaam waar de kleur van de lijn op gebaseerd wordt
    * color_category_names: lijst met de categorieën in woorden.
    * color_category_thresholds: lijst met de waarden van de grenzen voor de categorieen
    * color_category_lower_limit: True voor een extra categorie voor alle waarden lager dan je laagste categorie
    * color_category_upper_limit: True voor een extra categorie voor alle waarden hoger dan je hoogste categorie
    * color_category_colors: lijst met kleuren behorend bij de categorieen
    * legend: bool = False voor weergeven van legenda, False voor geen legenda
    * legend_name: Naam die boven de legenda wordt weergegeven,
    * legend_location: locatie van de legenda, bottom of top
    """
    lines_gdf = lines_gdf.copy(deep=True).to_crs(4326)
    # add symbol_color to lines_gdf
    lines_gdf, line_names, line_colors = add_categorized_color_to_gdf(
        gdf=lines_gdf,
        color_column=line_color_column,
        colormap=line_color_cmap,
        names=line_color_category_names,
        thresholds=line_color_category_thresholds,
        lower_limit=line_color_category_lower_limit,
        upper_limit=line_color_category_upper_limit,
        colors=line_color_category_colors,
        new_name_column="line_color_name",
        new_color_column="line_color",
        label_unit=label_unit,
        label_decimals=label_decimals,
    )
    fg = add_lines_to_map(
        m=m,
        lines_gdf=lines_gdf,
        lines=lines,
        layer_name=layer_name,
        feature_group=feature_group,
        control=control,
        show=show,
        line_color="line_color",
        line_color_name="line_color_name",
        line_weight=line_weight,
        label=label,
        label_column=label_column,
        label_unit=label_unit,
        label_decimals=label_decimals,
        label_fontsize=label_fontsize,
        z_index=z_index,
        dash_array=dash_array,
        tooltip=tooltip,
        tooltip_aliases=tooltip_aliases,
        popup=popup,
        popup_aliases=popup_aliases,
    )
    return fg
