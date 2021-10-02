"""Frameworks for running multiple Streamlit applications as a single app.
"""
import streamlit as st
from apps import sidebar


class MultiApp:
    """Framework for combining multiple streamlit applications.
    Usage:
        import foo
        import bar
        app = MultiApp()
        app.add_app("Foo", foo.app)
        app.add_app("Bar", bar.app)
        app.run()
    """
    def __init__(self):
        self.apps = []

    def add_app(self, title, func):
        """Adds a new application.
        Parameters
        ----------
        func:
            the python function to render this app.
        title:
            title of the app. Appears in the dropdown in the sidebar.
        """
        self.apps.append({
            "title": title,
            "function": func
        })

    def run(self):
        st.set_page_config(layout="wide")  # setting page config to wide mode
        st.title("California Covid-19 Vaccination Dashboard")  # setting page title
        app = st.sidebar.radio(
            'Go To',
            self.apps,
            format_func=lambda returned_app: returned_app['title'])
        sidebar.app()  # adding additional sidebar components
        app['function']()
