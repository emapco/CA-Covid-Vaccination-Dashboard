import streamlit as st
import app_util
from apps import sidebar

DEMOGRAPHICS_CSV = "data/vaccine_progress/covid-19-vaccines-administered-by-demographics.csv"

@st.cache
def get_demographic_data(df, chart_option):
    if chart_option == "cumulative":
        prefix = "cumulative_"
    else:
        prefix = ""

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
    st.title("California Covid-19 Vaccines Administered")  # Setting page title

    #########################
    # Sidebar
    #########################
    sb = sidebar.Sidebar()  # add sidebar components
    chart_option = sb.get_chart_option()

    #########################
    # Main content
    #########################
    demographics_csv_df = app_util.get_data_from_csv(DEMOGRAPHICS_CSV)

    st.markdown("### Vaccine Administered by Demographics")
    age_df, gender_df, race_df, demographic_args = get_demographic_data(demographics_csv_df, chart_option)
    app_util.plot_data(age_df, *demographic_args)
    app_util.plot_data(gender_df, *demographic_args)
    app_util.plot_data(race_df, *demographic_args)

