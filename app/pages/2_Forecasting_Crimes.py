import streamlit as st
from streamlit_folium import st_folium, folium_static
import requests
import pandas as pd
import os

### Heat Map libraries in folium
import folium
#from IPython.display import display
#import ipywidgets as widgets
from folium.plugins import HeatMap, HeatMapWithTime
import json

st.set_page_config(layout="wide")

margins_css = """
    <style>
        .main > div {
            padding-left: 2rem;
            padding-right: 2rem;
            padding-top: 2rem;
        }
    </style>
"""

st.markdown(margins_css, unsafe_allow_html=True)

API_HOST = os.getenv("API_HOST")

api_url_download_polygons = API_HOST + "/download_polygons"
response_download_polygons = requests.get(api_url_download_polygons).json()

# Add map
st.title("Forecasting Crimes 🫣 🔫🥸")
st.subheader("July 2023 - December 2023")


col1, col2 = st.columns([1,3])

with col1:
    # Add checkboxes
    checkbox_values = {
        'Month': ["07", "08", "09", "10", "11", "12"],
        'Category': ['fraud', 'threats', 'burglary', 'homicide',
                    'sexual_crime', 'property_damage', 'domestic_violence', 'danger_of_well-being',
                    'robbery_with_violence', 'robbery_without_violence','score']
    }

    selected_values = {}
    for checkbox_label, checkbox_options in checkbox_values.items():
        selected_values[checkbox_label] = st.selectbox(checkbox_label, checkbox_options)

    # Initialize the search_executed flag
    if 'search_executed' not in st.session_state:
        st.session_state.search_executed = False
        st.session_state.data = []

    if st.button('Search 🔍'):
        # Make API request to the backend to get Forecasting data
        api_url = API_HOST + "/get_crimes"

        year_month = f"2023-{selected_values['Month']}-01"
        category = selected_values['Category']

        year_month_search = year_month if 'ALL' not in year_month else None
        params = {
            'year_month': year_month_search,
            'category': category
        }

        response = requests.get(api_url, params=params)
        # Create a Pandas DataFrame from the data
        st.session_state.data = response.json()["data"]
        #st.write(response.json()["data"])
        st.session_state.search_executed = True
    else:
        st.write('')


with col2:

    if st.session_state.search_executed:
        data = st.session_state.data

        dataframe = pd.DataFrame(data)


        category = selected_values['Category']

        if data:


        #test if everything worked and build a map
            #poly_geo = 'local_geo.json'
            #st.write(response_download_polygons.json())

            map = folium.Map(location=[19.4326, -99.1332], zoom_start=11, tiles='Stamen Toner')

            folium.Choropleth(
                geo_data=response_download_polygons,
                name="choropleth",
                data=dataframe,
                columns=["code", category],
                key_on="feature.properties.geo_point_2d.lat",
                fill_color="YlOrRd",
                fill_opacity=0.7,
                line_opacity=0.2,
                legend_name=category,
            ).add_to(map)

            folium.LayerControl().add_to(map)

            folium_static(map, height=500, width=750)

        else:
            # Display the message if no crime was committed and a search has been executed
            st.markdown(""" ## NO CRIME WAS PREDICTED """)
