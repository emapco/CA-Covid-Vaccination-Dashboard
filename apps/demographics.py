import streamlit as st

import app_util
from app_util import DataObject, ChartArgs, DEMOGRAPHICS_CSV
from apps import sidebar


@st.cache(hash_funcs={tuple: hash})
def get_demographic_data(chart_option):
    if chart_option == "cumulative":
        prefix = "cumulative_"
    else:
        prefix = ""

    df = app_util.get_data_from_csv(DEMOGRAPHICS_CSV)
    # select different demographic categories and two other columns to plot
    age_data = df.loc[df["demographic_category"] == "Age Group"] \
        [["demographic_value", f"{prefix}total_doses", "administered_date"]]
    gender_data = df.loc[df["demographic_category"] == "Gender"] \
        [["demographic_value", f"{prefix}total_doses", "administered_date"]]
    race_data = df.loc[df["demographic_category"] == "Race/Ethnicity"] \
        [["demographic_value", f"{prefix}total_doses", "administered_date"]]

    age_data = DataObject(age_data, ChartArgs(f"{prefix}total_doses:Q", f" total doses (x)",
                                              'demographic_value', 'Vaccinations by Age Group'))
    gender_data = DataObject(gender_data, ChartArgs(f"{prefix}total_doses:Q", f" total doses (x)",
                                                    'demographic_value', 'Vaccinations by Gender'))
    race_data = DataObject(race_data, ChartArgs(f"{prefix}total_doses:Q", f" total doses (x)",
                                                'demographic_value', 'Vaccinations by Race/Ethnicity'))
    return (age_data, gender_data, race_data)


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
    if chart_option == "daily":
        demographic_data_objs = get_demographic_data("daily")  # get data
        charts = []
        for obj in demographic_data_objs:  # create chart (chart saved in session state)
            charts.append(app_util.create_chart(obj))
        app_util.plot_chart(*charts)  # plot charts
    else:
        cum_demographic_data_objs = get_demographic_data("cumulative")
        charts = []
        for obj in cum_demographic_data_objs:
            charts.append(app_util.create_chart(obj))
        app_util.plot_chart(*charts)  # plot charts
