import os

import pandas as pd
import altair as alt
import streamlit as st

STATE_CSV = "data/vaccine_progress/statewide-vaccines-administered-by-county-population.csv"
DEMOGRAPHICS_CSV = "data/vaccine_progress/covid-19-vaccines-administered-by-demographics.csv"

@st.cache(hash_funcs={alt.LayerChart: id})
def create_chart(data_obj):
    """
    Plots pandas Dataframe using altair.Chart() function.
    :param data_obj: DataObject object that contains a df and plot arguments
    :return: None
    """
    # filter out dates before start_date
    source = data_obj.df.set_index("administered_date")  # set index for filtering w/ loc method
    source = source.loc[data_obj.args.start_date:"2021-09-30"].reset_index()  # reset index for plotting

    z_no_qualifier = data_obj.args.z.split(":")[0]  # to be able to refer to the column
    y_no_quantifier = data_obj.args.y.split(":")[0]
    # x_axis_ticks = source["administered_date"].tolist()[::10]  # generate a list of dates for x-axis markers

    # init chart base
    base = alt.Chart(source).encode(x=alt.X('administered_date:T',
                                            axis=alt.Axis(format='%m/%d', grid=True),  # values=x_axis_ticks (alt.Axis)
                                            title="administered date (MM/DD)"))
    columns = sorted(source[z_no_qualifier].unique())
    selection = alt.selection_single(fields=['administered_date'], nearest=True, on='mouseover',
                                     empty='none', clear='mouseout')

    # specify type of chart and init lines portion
    if data_obj.args.chart_type == "line":
        lines = base.mark_line()
        lines = lines.encode(y=alt.Y(data_obj.args.y, title=data_obj.args.y_title, stack=False),
                             color=data_obj.args.z, stroke=data_obj.args.z)  # properties(title=chart_title)
    else:  # chart_type == "area"
        lines = base.mark_area(opacity=0.3)
        # area chart includes an additional legend if legend is not set to None
        lines = lines.encode(y=alt.Y(data_obj.args.y, title=data_obj.args.y_title, stack=False),
                             color=alt.Color(data_obj.args.z, legend=None), stroke=data_obj.args.z)
    points = lines.mark_point().transform_filter(selection)

    rule = base.transform_pivot(
        z_no_qualifier, value=y_no_quantifier, groupby=["administered_date"]
    ).mark_rule().encode(
        opacity=alt.condition(selection, alt.value(0.3), alt.value(0)),
        tooltip=[alt.Tooltip(c, type='quantitative') for c in columns]
    ).add_selection(selection)

    return (lines + points + rule).interactive()


def plot_chart(*args):
    for chart in args:
        st.altair_chart(chart, use_container_width=True)


@st.cache(hash_funcs={pd.DataFrame: pd.util.hash_pandas_object})
def get_data_from_csv(file):
    """
    Creates a dataframe using the csv file specified in file.
    It also sets the date column as a datetime data column
    :param file: file path to csv file
    :return: df: dataframe
    """
    if os.name == "nt":
        file = os.path.dirname(__file__) + "\\" + file.replace("/", "\\")
    else:
        file = os.path.dirname(__file__) + "/" + file

    try:
        df = pd.read_csv(file)
        df["administered_date"] = pd.to_datetime(df["administered_date"])
        return df
    except KeyError:
        print("ERROR: administered_date not found")
    except FileNotFoundError:
        print("ERROR: File not found")
    return None


class DataObject:
    def __init__(self, df, args):
        """
        Data object used to return relevant data from get_data functions
        :param df: dataframe
        :param args: ChartArgs object containing the parameters for plotting the data
        """
        self.df = df
        self.args = args
        self.key = args.y_title + args.chart_title


class ChartArgs:
    def __init__(self, y, y_title, z, chart_title, start_date=None, chart_type=None):
        """
        Object to store arguments for plotting DataObject.df
        :param y: y-axis df column name
        :param y_title: y-axis title
        :param z: z-axis df column name
        :param chart_title: chart title
        :param start_date: filter data starting from start_date
        :param chart_type: type of chart: line or area
        """
        if start_date is None:
            start_date = '2020-12-12'
        if chart_type is None:
            chart_type = 'line'
        self.y = y
        self.y_title = y_title
        self.z = z
        self.chart_title = chart_title
        self.start_date = start_date
        self.chart_type = chart_type
