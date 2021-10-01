import streamlit as st
import pandas as pd

import app_util
from apps import sidebar

STATE_CSV = "data/vaccine_progress/statewide-covid-19-vaccines-administered-by-county.csv"
DEMOGRAPHICS_CSV = "data/vaccine_progress/covid-19-vaccines-administered-by-demographics.csv"


@st.cache
def get_state_data(df):
    state_data = df[["county", "administered_date", "cumulative_fully_vaccinated",
                     "cumulative_at_least_one_dose", "est_population"]]  # select relevant columns
    state_data = state_data[
        state_data["county"] == "Statewide"]  # select Statewide data
    state_data = state_data.groupby(
        ["administered_date"]).sum().reset_index()  # group by date and county and then sum the numeric data

    # calculate per capita columns
    state_data["fully_vaccinated_per_capita"] = \
        state_data["cumulative_fully_vaccinated"] / state_data["est_population"]
    state_data["cumulative_at_least_one_dose_per_capita"] = \
        state_data["cumulative_at_least_one_dose"] / state_data["est_population"]
    state_data = state_data.round(3)  # round numeric data to 3 decimal points

    # melt from wide to long form for plotting
    state_vaccine_status = pd.melt(state_data, id_vars='administered_date',
                                   value_vars=["fully_vaccinated_per_capita",
                                               "cumulative_at_least_one_dose_per_capita"])
    state_vaccine_status = state_vaccine_status.rename(
        columns={"variable": "vaccine_status", "value": "doses"})  # update col. name
    plot_arguments = ["doses:Q", "Percent of Californians Vaccinated", "vaccine_status",
                      "People vaccinated in California", "2021-01-01", "area"]

    return state_vaccine_status, plot_arguments


@st.cache
def get_vaccine_maker_data(df, chart_option):
    if chart_option == "cumulative":
        prefix = "cumulative_"
    else:
        prefix = ""

    # groups data by date and then melts it into long form to plot different vaccine maker data
    maker_data = df[[f"{prefix}pfizer_doses", f"{prefix}moderna_doses",
                     f"{prefix}jj_doses", "administered_date"]]  # select columns
    maker_data = maker_data.groupby("administered_date").sum().reset_index()  # group and sum vaccines

    maker_data[f"{prefix}total_doses"] = maker_data[f"{prefix}pfizer_doses"] \
                                         + maker_data[f"{prefix}moderna_doses"] + maker_data[f"{prefix}jj_doses"]

    # melt from wide to long form
    maker_data = pd.melt(maker_data, id_vars='administered_date',
                         value_vars=[f"{prefix}pfizer_doses", f"{prefix}moderna_doses",
                                     f"{prefix}jj_doses", f"{prefix}total_doses"])
    maker_data = maker_data.rename(columns={"variable": "maker", "value": "doses"})  # update col. name
    plot_arguments = ["doses:Q", "Vaccine doses (x)", "maker", "Vaccines Administered by Maker"]

    return maker_data, plot_arguments


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
    county_csv_df = app_util.get_data_from_csv(STATE_CSV)
    demographics_csv_df = app_util.get_data_from_csv(DEMOGRAPHICS_CSV)

    st.markdown("### Vaccines administered in California by vaccine maker")
    maker_df, maker_args = get_vaccine_maker_data(demographics_csv_df, chart_option)
    app_util.plot_data(maker_df, *maker_args)

    st.markdown("### State partial and fully vaccination rate")
    state_df, state_args = get_state_data(county_csv_df)
    app_util.plot_data(state_df, *state_args)
