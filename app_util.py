import os

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
    source = df.set_index("administered_date")  # set index for filtering w/ loc method
    source = source.loc[start_date:"2021-09-30"].reset_index()  # reset index for plotting

    z_no_qualifier = z.split(":")[0]  # to be able to refer to the column
    y_no_quantifier = y.split(":")[0]
    # x_axis_ticks = source["administered_date"].tolist()[::10]  # generate a list of dates for x-axis markers

    # init chart base
    base = alt.Chart(source).encode(x=alt.X('administered_date:T',
                                            axis=alt.Axis(format='%m/%d', grid=True),  # values=x_axis_ticks (alt.Axis)
                                            title="administered date (MM/DD)"))
    columns = sorted(source[z_no_qualifier].unique())
    selection = alt.selection_single(fields=['administered_date'], nearest=True, on='mouseover',
                                     empty='none', clear='mouseout')

    # specify type of chart and init lines portion
    if chart_type == "line":
        lines = base.mark_line()
        lines = lines.encode(y=alt.Y(y, title=y_title, stack=False), color=z, stroke=z)  # properties(title=chart_title)
    else:  # chart_type == "area"
        lines = base.mark_area(opacity=0.3)
        # area chart includes an additional legend if legend is not set to None
        lines = lines.encode(y=alt.Y(y, title=y_title, stack=False), color=alt.Color(z, legend=None), stroke=z)
    points = lines.mark_point().transform_filter(selection)

    rule = base.transform_pivot(
        z_no_qualifier, value=y_no_quantifier, groupby=["administered_date"]
    ).mark_rule().encode(
        opacity=alt.condition(selection, alt.value(0.3), alt.value(0)),
        tooltip=[alt.Tooltip(c, type='quantitative') for c in columns]
    ).add_selection(selection)

    chart = (lines + points + rule).interactive()
    st.altair_chart(chart, use_container_width=True)


@st.cache
def get_data_from_csv(file):
    """
    Creates a dataframe using the csv file specified in file.
    It also sets the date column as a datetime data column
    :param file: file path to csv file
    :return: df: dataframe
    """

    file = os.path.dirname(__file__) + "\\" + file.replace("/", "\\")
    try:
        df = pd.read_csv(file)
        df["administered_date"] = pd.to_datetime(df["administered_date"])
        return df
    except KeyError:
        print("ERROR: administered_date not found")
    except FileNotFoundError:
        print("ERROR: File not found")
    return None
