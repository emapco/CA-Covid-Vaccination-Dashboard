import pydeck as pdk
import pandas as pd
import geopandas as gpd
import streamlit as st


COUNTIES_GPKG = "ca_counties_covid_plot.gpkg"

@st.cache(hash_funcs={gpd.GeoDataFrame: id})
def get_data():
    # Read GPKG and downcast the columns for memory performance
    polygon_gdf = gpd.read_file(COUNTIES_GPKG)
    for col in polygon_gdf.columns:
        dtype = str(polygon_gdf[col].dtype)
        if 'int' in dtype:
            polygon_gdf[col] = pd.to_numeric(polygon_gdf[col], downcast="unsigned")
        if 'float' in dtype:
            polygon_gdf[col] = pd.to_numeric(polygon_gdf[col], downcast="float")

    # produced a simplified polygon object column and overwrite the original
    simplified_polygons = polygon_gdf.simplify(0.0005)
    polygon_gdf['geometry'] = simplified_polygons
    return polygon_gdf

@st.cache(hash_funcs={pdk.Deck: id})
def create_deck(gdf):
    column_scatter_df = pd.DataFrame(gdf.drop(columns=['geometry']))
    # radius cases last 30 days
    # height deaths last 30 days
    # color pop % vaccinated
    layers = [
        pdk.Layer(
            'ColumnLayer',
            data=column_scatter_df,
            get_position=['LON', 'LAT'],
            get_elevation='CASES_PER_CAPITA',
            elevation_scale=10000000,
            radius=2000,
            get_fill_color='[R, G, B]',
            pickable=True,
            auto_highlight=True,
        ),
        pdk.Layer(
            'ScatterplotLayer',
            data=column_scatter_df,
            get_position=['LON', 'LAT'],
            get_radius='DEATHS_PER_CAPITA',
            radius_scale=130000000,
            pickable=True,
            auto_highlight=True,
            get_fill_color='[R, G, B]',
        ),
        pdk.Layer("GeoJsonLayer",
                  gdf,
                  opacity=0.1,
                  extruded=True,
                  wireframe=True,
                  pickable=True,
                  auto_highlight=True,
                  get_line_color=[255, 255, 255],
                  get_fill_color='[R, G, B]'
                  )
    ]
    # create tooltip
    tooltip = {"html": "County: <b>{NAME}</b><br>"
                       "Cases (last 30 days): <b>{CASES_LAST_30}</b><br>"
                       "Deaths (last 30 days): <b>{DEATHS_LAST_30}</b><br>"
                       "Vaccination coverage (10/08/21): <b>{FORMATTED_RATE}</b>"}
    # create init viewport location
    initial_view_state = pdk.ViewState(latitude=37.7749295, longitude=-120.4194155,
                                       zoom=5, bearing=75, pitch=60)
    # create deck
    deck = pdk.Deck(layers=layers, tooltip=tooltip, initial_view_state=initial_view_state, map_style='dark_no_labels')
    return deck


def app():
    gdf = get_data()
    deck = create_deck(gdf)

    #########################
    # Main content
    #########################
    st.markdown("### COVID-19 vaccine coverage and COVID-19 Cases and Deaths (last 30 days)")
    st.pydeck_chart(deck)  # plot deck with streamlit
    st.write("Column height is proportional to the number of COVID-19 cases reported in the last 30 days.")
    st.write("Circle radius is proportional to the number of COVID-19 deaths reported in the last 30 days.")
    st.write("Shorter the wavelength of color (from red to violet) represents larger vaccination coverage.")
