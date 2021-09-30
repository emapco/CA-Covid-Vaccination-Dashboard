import streamlit as st
import pandas as pd
import altair as alt


def plot_data(df, y, y_title, z, chart_title, start_date=None, chart_type=None):
    """
    Plots pandas Dataframe using altair.Chart() function.
    :param df: dataframe
    :param y: y-axis df column name and altair's data type symbol (e.g. 'axis:Q')
    :param y_title: y-axis title
    :param z: z-axis df column name
    :param chart_title: the charts title
    :param start_date: plot data at start_date; 'YYYY-MM-DD' format
    :param chart_type: type of altair chart
    :return: None
    """
    if start_date is None:
        start_date = "2020-12-12"
    if chart_type is None:
        chart_type = "line"

    # filter out dates before start_date
    filtered_data = df.set_index("administered_date")  # set index for filtering w/ loc method
    filtered_data = filtered_data.loc[start_date:"2021-09-24"].reset_index()  # reset index for plotting
    x_axis_ticks = filtered_data["administered_date"].tolist()[::]  # generate a list of dates for x-axis markers

    chart = alt.Chart(filtered_data)  # init chart
    if chart_type == "line":  # specify type of chart
        chart = chart.mark_line()
    elif chart_type == "area":
        chart = chart.mark_area(opacity=0.9)
    # finish building chart
    chart = chart.encode(x=alt.X('administered_date:T', axis=alt.Axis(values=x_axis_ticks, format='%m/%d', grid=True),
                                 title="administered date (MM/DD)"),
                         y=alt.Y(y, title=y_title, stack=False),
                         color=z,
                         strokeDash=z,
                         tooltip=[*filtered_data.columns]
                         ).properties(title=chart_title
                                      ).add_selection(
        alt.selection_interval(bind='scales'))  # adds scaling interactivity
    st.altair_chart(chart, use_container_width=True)


@st.cache
def get_demographic_data(chart_option):
    df = pd.read_csv("data/vaccine_progress/covid-19-vaccines-administered-by-demographics.csv")
    df["administered_date"] = pd.to_datetime(df['administered_date'])  # change date string column to datetime objects

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


@st.cache
def get_county_data():
    ###########################################################################################
    # vaccine administered by county
    ###########################################################################################
    df = pd.read_csv("data/vaccine_progress/covid-19-vaccines-administered-by-demographics-by-county.csv")
    df["administered_date"] = pd.to_datetime(df['administered_date'])

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
    county_demo_data = county_demo_data[["county", "administered_date", "fully_vaccinated_per_capita",
                                         "suppress_data"]]

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


@st.cache
def get_state_data():
    df = pd.read_csv("data/vaccine_progress/covid-19-vaccines-administered-by-demographics-by-county.csv")
    df["administered_date"] = pd.to_datetime(df['administered_date'])

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
def get_vaccine_maker_data(chart_option):
    ###########################################################################################
    # vaccine maker data
    ###########################################################################################
    df = pd.read_csv("data/vaccine_progress/covid-19-vaccines-administered-by-demographics.csv")
    df["administered_date"] = pd.to_datetime(df['administered_date'])  # change date string column to datetime objects

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


def main():
    st.set_page_config(layout="wide")  # Setting page config to wide mode
    st.title("California Covid-19 Vaccines Administered")  # Setting page title

    #########################
    # Sidebar
    #########################
    chart_option = st.sidebar.radio('Select data type for non-rate graphs', ["daily", "cumulative"])
    # TODO: Add a legend/dictionary description for each variable for each type of graph to side bar
    st.sidebar.write("")
    st.sidebar.title("Dashboard Data Dictionary")
    st.sidebar.markdown("**suppress_data**: Is data suppressed according to CHHS Agency Data "
                        "De-Identification Guidelines? (True or False)")

    #########################
    # Main content
    #########################
    st.markdown("### Vaccine Administered by Demographics")
    age_df, gender_df, race_df, demographic_args = get_demographic_data(chart_option)
    plot_data(age_df, *demographic_args)
    plot_data(gender_df, *demographic_args)
    plot_data(race_df, *demographic_args)

    st.markdown("### Vaccine Administered in California by Vaccine Maker")
    maker_df, maker_args = get_vaccine_maker_data(chart_option)
    plot_data(maker_df, *maker_args)

    st.markdown("### Counties with under 50% population vaccination rate")
    county_df, county_args = get_county_data()
    plot_data(county_df, *county_args)

    st.markdown("### State partial and fully vaccinated rate")
    state_df, state_args = get_state_data()
    plot_data(state_df, *state_args)

    st.write("Source: [California Department of Public Health]"
             "(https://data.chhs.ca.gov/dataset/vaccine-progress-dashboard)")


if __name__ == '__main__':
    main()
