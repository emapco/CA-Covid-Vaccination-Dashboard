import streamlit as st
import pandas as pd

import app_util
from apps import sidebar

COUNTY_CSV = "data/vaccine_progress/covid-19-vaccines-administered-by-demographics-by-county.csv"


@st.cache
def get_county_data(df):
    ###########################################################################################
    # vaccine administered by county
    ###########################################################################################
    county_demo_data = df[["county", "est_population", "administered_date",
                           "cumulative_fully_vaccinated", "suppress_data"]]
    county_demo_data = county_demo_data[county_demo_data["county"] != "Statewide"]  # remove Statewide data
    county_demo_data = county_demo_data.groupby(
        ["administered_date", "county"]).sum().reset_index()  # group by date and county and then sum the numeric data

    # data for map
    county_demo_data["fully_vaccinated_per_capita"] = \
        county_demo_data["cumulative_fully_vaccinated"] / county_demo_data["est_population"]
    county_demo_data = county_demo_data.round(3)  # round columns to 3 decimal places

    # select relevant columns for plotting
    county_demo_data = county_demo_data[["county", "administered_date", "fully_vaccinated_per_capita"]]

    ###########################################################################################
    # vaccine administered by county per capita
    ###########################################################################################
    # Filters out the counties with 50%+ vaccination rate
    counties_above_50_percent_rate = pd.unique(county_demo_data[
                                                   county_demo_data["fully_vaccinated_per_capita"] > .5]["county"])
    counties_below_50_percent_rate = [x for x in pd.unique(county_demo_data["county"])
                                      if x not in counties_above_50_percent_rate]
    counties_below_50_percent_rate = county_demo_data.query("county in @counties_below_50_percent_rate")

    plot_arguments = ["fully_vaccinated_per_capita:Q", "fully vaccinated per capita",
                      "county", "Vaccines Administered by County"]

    return counties_below_50_percent_rate, plot_arguments


def app():
    st.title("California Covid-19 Vaccination Dashboard")  # setting page title

    #########################
    # Sidebar
    #########################
    sb = sidebar.Sidebar()  # add sidebar components
    chart_option = sb.get_chart_option()

    #########################
    # Main content
    #########################
    county_csv_df = app_util.get_data_from_csv(COUNTY_CSV)

    st.markdown("### Counties with under 50% population vaccination rate")
    county_df, county_args = get_county_data(county_csv_df)
    app_util.plot_data(county_df, *county_args)