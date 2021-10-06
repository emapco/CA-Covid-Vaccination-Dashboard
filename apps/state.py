import streamlit as st
import pandas as pd

import app_util
from app_util import DataObject, ChartArgs, STATE_CSV


@st.cache(hash_funcs={DataObject: hash})
def get_state_data():
    state_data = app_util.get_data_from_csv(STATE_CSV, ["county", "administered_date", "cumulative_fully_vaccinated",
                                                        "cumulative_at_least_one_dose", "est_population"])
    state_data = state_data[state_data["county"] == "All CA Counties"]  # select Statewide data
    state_data = state_data.groupby(
        ["administered_date"]).sum().reset_index()  # group by date and county and then sum the numeric data

    # calculate per capita columns
    state_data["fully_vaccinated_per_capita"] = \
        state_data["cumulative_fully_vaccinated"] / state_data["est_population"]
    state_data["cumulative_at_least_one_dose_per_capita"] = \
        state_data["cumulative_at_least_one_dose"] / state_data["est_population"]
    state_data = state_data.round(3)  # round numeric data to 3 decimal points

    # melt from wide to long form for plotting
    state_vaccination_data = pd.melt(state_data, id_vars='administered_date',
                                     value_vars=["fully_vaccinated_per_capita",
                                                 "cumulative_at_least_one_dose_per_capita"])
    state_vaccination_data = state_vaccination_data.rename(
        columns={"variable": "vaccine_status", "value": "doses"})  # update col. name

    state_vaccination_data = DataObject(state_vaccination_data,
                                        ChartArgs("doses:Q", "Percent of Californians Vaccinated", "vaccine_status",
                                                  "People vaccinated in California", "2021-01-01", "area"))
    return state_vaccination_data


@st.cache(hash_funcs={DataObject: hash})
def get_vaccine_maker_data(chart_option):
    if chart_option == "cumulative":
        prefix = "cumulative_"
    else:
        prefix = ""
    maker_data = app_util.get_data_from_csv(STATE_CSV, [f"{prefix}pfizer_doses", f"{prefix}moderna_doses",
                                                        f"{prefix}jj_doses", "administered_date"])
    # groups data by date and then melts it into long form to plot different vaccine maker data
    maker_data = maker_data.groupby("administered_date").sum().reset_index()  # group and sum vaccines

    maker_data[f"{prefix}total_doses"] = maker_data[f"{prefix}pfizer_doses"] \
                                         + maker_data[f"{prefix}moderna_doses"] + maker_data[f"{prefix}jj_doses"]

    # melt from wide to long form
    maker_data = pd.melt(maker_data, id_vars='administered_date',
                         value_vars=[f"{prefix}pfizer_doses", f"{prefix}moderna_doses",
                                     f"{prefix}jj_doses", f"{prefix}total_doses"])
    maker_data = maker_data.rename(columns={"variable": "maker", "value": "doses"})  # update col. name
    maker_data = DataObject(maker_data, ChartArgs(y="doses:Q", y_title="Vaccine doses (x)", z="maker",
                                                  chart_title="Vaccines Administered by Manufacturer"))
    return maker_data


def app():
    #########################
    # Main content
    #########################
    st.markdown("### Vaccines administered in California by vaccine manufacturer")

    # plot charts depending on radiobutton option
    if st.session_state["graph_type"] == "daily":
        maker_obj = get_vaccine_maker_data("daily")  # get data
        maker_chart = app_util.create_chart(maker_obj)  # create chart
        app_util.plot_chart(maker_chart)  # plot chart
    else:
        cum_maker_obj = get_vaccine_maker_data("cumulative")
        cum_maker_chart = app_util.create_chart(cum_maker_obj)
        app_util.plot_chart(cum_maker_chart)

    st.markdown("### Full and partial vaccination coverage")
    state_obj = get_state_data()
    state_chart = app_util.create_chart(state_obj)
    app_util.plot_chart(state_chart)
