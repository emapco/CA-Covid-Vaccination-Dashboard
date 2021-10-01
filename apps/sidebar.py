import streamlit as st


class Sidebar:
    def __init__(self):
        self._chart_option = st.sidebar.radio('Select graph type for non-rate graphs', ["daily", "cumulative"])

        st.markdown('<style>#vg-tooltip-element{z-index: 1000052}</style>',
                    unsafe_allow_html=True)  # fix for full screen tooltip bug; here since common factor

        st.sidebar.write("")
        st.sidebar.title("Dashboard Data Dictionary")
        st.sidebar.markdown("**Administered Date**: Date on which the vaccine was administered. This is different "
                            "than the report date.")
        st.sidebar.markdown("**Doses**: doses administered on a particular administration date.")
        st.sidebar.markdown("**County**: County of residence for vaccine recipient.")
        st.sidebar.markdown("**Demographic Value**: Classification categories are imported from HL7 codes used in "
                            "vaccination records. "
                            "For purposes of data analysis, 'Other Race' should be viewed as the equivalent of "
                            "“Unknown. For Gender, anything other than 'Male' or 'Female' is mapped to "
                            "'Unknown/Undifferentiated' due to the CDC COVID file specifications")
        st.sidebar.markdown("**Fully Vaccinated**: Total number of people who became fully vaccinated on a "
                            "particular administration date.")
        st.sidebar.markdown("**Cumulative At Least One Dose**: Cumulative number of people with at least one dose on "
                            "that date.")
        st.sidebar.markdown("**Estimated Population**: DOF estimated all ages population for year 2021 "
                            "(January 2021 file version)")
        st.sidebar.markdown("**X per capita**: X/Estimated Population")

        st.sidebar.write("")
        st.sidebar.write("Sources:")
        st.sidebar.write("Vaccine Data: [California Department of Public Health]"
                         "(https://data.chhs.ca.gov/dataset/vaccine-progress-dashboard)")
        st.sidebar.write("Population Data: [California Department of Finance: Demographic Research Unit]"
                         "(https://dof.ca.gov/Forecasting/Demographics/Estimates/e-1/)")

    def get_chart_option(self):
        return self._chart_option
