import streamlit as st
import pandas as pd

import app_util
from apps import sidebar


DEMOGRAPHICS_CSV = "data/vaccine_progress/covid-19-vaccines-administered-by-demographics.csv"

@st.cache(hash_funcs={pd.DataFrame: pd.util.hash_pandas_object})
def get_demographic_data(chart_option):
    if chart_option == "cumulative":
        prefix = "cumulative_"
    else:
        prefix = ""

    df = app_util.get_data_from_csv(DEMOGRAPHICS_CSV)

    # select different demographic categories and two other columns to plot
    age_group_data = df.loc[df["demographic_category"] == "Age Group"] \
        [["demographic_value", f"{prefix}total_doses", "administered_date"]]
    gender_data = df.loc[df["demographic_category"] == "Gender"] \
        [["demographic_value", f"{prefix}total_doses", "administered_date"]]
    race_data = df.loc[df["demographic_category"] == "Race/Ethnicity"] \
        [["demographic_value", f"{prefix}total_doses", "administered_date"]]

    plot_arguments = [f"{prefix}total_doses:Q", f" total doses (x)",
                      'demographic_value', 'Vaccinations by Demographic category']
    return age_group_data, gender_data, race_data, plot_arguments


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
    st.markdown("### Vaccine Administered by Demographics")
    # get all data
    age_df, gender_df, race_df, demographic_args = get_demographic_data("daily")
    cum_age_df, cum_gender_df, cum_race_df, cum_demographic_args = get_demographic_data("cumulative")

    # create charts
    age_chart = app_util.create_chart(age_df, *demographic_args)
    gender_chart = app_util.create_chart(gender_df, *demographic_args)
    race_chart = app_util.create_chart(race_df, *demographic_args)
    cum_age_chart = app_util.create_chart(cum_age_df, *cum_demographic_args)
    cum_gender_chart = app_util.create_chart(cum_gender_df, *cum_demographic_args)
    cum_race_chart = app_util.create_chart(cum_race_df, *cum_demographic_args)

    copy_age_chart = age_chart
    copy_gender_chart = gender_chart
    copy_race_chart = race_chart
    copy_cum_age_chart = cum_age_chart
    copy_cum_gender_chart = cum_gender_chart
    copy_cum_race_chart = cum_race_chart

    # plot charts depending on radiobutton option
    if chart_option == "daily":
        app_util.plot_chart(copy_age_chart, copy_gender_chart, copy_race_chart)
    else:
        app_util.plot_chart(copy_cum_age_chart, copy_cum_gender_chart, copy_cum_race_chart)
