import streamlit as st
from multiapp import MultiApp
from apps import demographics, state, county  # import your app modules here

app = MultiApp()

# Adding applications
app.add_app("Demographic Data", demographics.app)
app.add_app("State Data", state.app)
app.add_app("County Data", county.app)

# The main app
app.run()
