import streamlit as st
import folium
from streamlit_folium import folium_static
import requests
import pandas as pd
import os

API_HOST = os.getenv("API_HOST")

st.set_page_config(layout="wide")

margins_css = """
    <style>
        .main > div {
            padding-left: 2rem;
            padding-right: 2rem;
            padding-top: 0.5rem;
        }
    </style>
"""

st.markdown(margins_css, unsafe_allow_html=True)

month_mapping = {
    "July": '07',
    "August": '08',
    "September": '09',
    "October": '10',
    "November": '11',
    "December": '12'
}

month_mapping_swapped = {value: key for key, value in month_mapping.items()}


# Add map
st.title("Forecasting Crimes 🫣 🔫🥸")
st.subheader("July 2023 - December 2023")

col1, col2 = st.columns([1,3])

with col1:
    if "polygons_layer" not in st.session_state:
        api_url_download_polygons = API_HOST + "/download_polygons"
        response_download_polygons = requests.get(api_url_download_polygons).json()
        st.session_state.polygons_layer = response_download_polygons

    # Add checkboxes
    checkbox_values = {
        'Month': list(month_mapping.keys()),
        'Category': ['fraud', 'threats', 'burglary', 'homicide',
                    'sexual_crime', 'property_damage', 'domestic_violence', 'danger_of_well_being',
                    'robbery_with_violence', 'robbery_without_violence', 'score']
    }
    selected_values = {}
    for checkbox_label, checkbox_options in checkbox_values.items():
        selected_values[checkbox_label] = st.selectbox(checkbox_label, checkbox_options)

  # Initialize the search_executed flag
    if 'search_executed' not in st.session_state:
        st.session_state.search_executed = False
        st.session_state.data = []

    button = st.button('Search 🔍')
with col2:
    if button:
        # Check if both Month and Category are selected
        st.session_state.search_executed = True
        # Make API request to the backend to get forecasting data
        api_url = API_HOST + "/get_crimes"
        year_month = f"2023-{month_mapping[selected_values['Month']]}-01"
        category = selected_values['Category']
        year_month_search = year_month if 'ALL' not in year_month else None
        params = {
            'year_month': year_month_search,
            'category': category
        }
        with st.spinner('Predicting crimes...'):
            response = requests.get(api_url, params=params)
            if response.status_code == 200:
                data = response.json()["data"]
        if data:
            dataframe = pd.DataFrame(data)
            category = selected_values['Category']
            # Build the map
            map = folium.Map(location=[19.4326, -99.1332], zoom_start=11, tiles='Stamen Toner')
            st.success('Prediction complete')
            folium.Choropleth(
                geo_data=st.session_state.polygons_layer,
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
            # Display the message if no crime was predicted and a search has been executed
            st.markdown(""" ## NO CRIME WAS PREDICTED """)
