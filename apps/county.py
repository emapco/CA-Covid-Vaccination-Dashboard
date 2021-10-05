import streamlit as st
import pandas as pd

import app_util
from app_util import DataObject, ChartArgs, STATE_CSV


@st.cache(hash_funcs={DataObject: hash})
def get_county_data():
    print("get_county_data")
    county_demo_data = app_util.get_data_from_csv(STATE_CSV, ["county", "est_population", "administered_date",
                                                              "cumulative_fully_vaccinated"])
    ###########################################################################################
    # vaccine administered by county
    ###########################################################################################

    county_demo_data = county_demo_data[county_demo_data["county"] != "Statewide"]  # remove Statewide data
    county_demo_data = county_demo_data.groupby(
        ["administered_date", "county"]).sum().reset_index()  # group by date and county and then sum the numeric data

    # data for map
    county_demo_data["fully_vaccinated_per_capita"] = \
        county_demo_data["cumulative_fully_vaccinated"] / county_demo_data["est_population"]
    county_demo_data = county_demo_data.round(3)  # round columns to 3 decimal places

    # drop irrelevant columns
    county_demo_data.drop(columns=["cumulative_fully_vaccinated", "est_population"])
    ###########################################################################################
    # vaccine administered by county per capita
    ###########################################################################################
    # Filters out the counties with 50%+ vaccination rate
    counties_above_60_percent_rate = pd.unique(county_demo_data[
                                                   county_demo_data["fully_vaccinated_per_capita"] > .6]["county"])
    counties_below_60_percent_rate = [x for x in pd.unique(county_demo_data["county"])
                                      if x not in counties_above_60_percent_rate]
    counties_below_60_percent_rate = county_demo_data.query("county in @counties_below_60_percent_rate")
    counties_below_60_percent_rate = DataObject(counties_below_60_percent_rate,
                                                ChartArgs("fully_vaccinated_per_capita:Q", "fully vaccinated per capita"
                                                          , "county", "Vaccines Administered by County"))
    return counties_below_60_percent_rate


def app():
    #########################
    # Main content
    #########################
    st.markdown("### Counties with under 60% population vaccination rate")
    county_obj = get_county_data()
    county_chart = app_util.create_chart(county_obj)
    app_util.plot_chart(county_chart)
