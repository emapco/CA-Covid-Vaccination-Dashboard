import pandas as pd
import altair as alt
import streamlit as st


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
    x_axis_ticks = filtered_data["administered_date"].tolist()[::20]  # generate a list of dates for x-axis markers

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
def get_data_from_csv(file):
    """
    Creates a dataframe using the csv file specified in file.
    It also sets the date column as a datetime data column
    :param file: file path to csv file
    :return: df: dataframe
    """
    df = pd.read_csv(file)
    df["administered_date"] = pd.to_datetime(df['administered_date'])
    return df
