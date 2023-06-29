import streamlit as st
import folium
from streamlit_folium import st_folium, folium_static
import requests
import pandas as pd
import os


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

# Add map
st.title("Historical 📅 crime data 📜📍")
map = folium.Map(location=[19.4326, -99.1332], zoom_start=11, tiles='Stamen Toner')


col1, col2 = st.columns([1,3])

with col1:
    # Fetch neighborhoods from the backend
    if 'neighborhoods' not in st.session_state:
        response = requests.get(API_HOST + "/neighborhoods")
        neighborhoods = response.json()["neighborhoods"]
        st.session_state.neighborhoods = neighborhoods
    else:
        neighborhoods = st.session_state.neighborhoods

    # Add checkboxes
    checkbox_values = {
        'Neighborhood': neighborhoods,
        'Year': ['ALL', 2019, 2020, 2021, 2022, 2023],
        'Month': ['ALL'] + ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"],
        'Category': ['ALL', 'fraud', 'threats', 'threats', 'burglary', 'homicide',
                    'sexual crime', 'property damage', 'domestic violence', 'danger of well-being',
                    'robbery with violence', 'robbery without violence']
    }

    selected_values = {}
    for checkbox_label, checkbox_options in checkbox_values.items():
        selected_values[checkbox_label] = st.multiselect(checkbox_label, checkbox_options)

    # Initialize the search_executed flag
    if 'search_executed' not in st.session_state:
        st.session_state.search_executed = False
        st.session_state.data = []

    markers_data = []

    if st.button('Search 🔍'):
        # Make API request to the backend to get historical data
        api_url = API_HOST + "/get_historical_data"

        year = selected_values['Year'] if 'ALL' not in selected_values['Year'] else None
        params = {
            'neighborhoods': selected_values['Neighborhood'],
            'years': year,
            'months': selected_values['Month'],
            'categories': selected_values['Category']
        }

        st.write('Searching crimes...')
        response = requests.post(api_url, json=params)
        #print(response.content)
        # Create a Pandas DataFrame from the data
        st.session_state.data = response.json()["data"]
        st.session_state.search_executed = True
    else:
        st.write('No search yet')


with col2:

    if st.session_state.search_executed:
        data = st.session_state.data
        dataframe = pd.DataFrame(data)
        if data:
            for row in data:
                marker = folium.Marker([row['Latitude'], row['Longitude']], tooltip=row['Category'])
                markers_data.append(marker)
                marker.add_to(map)
            # Set the flag to indicate that a search has been executed
            folium_static(map, width=700)
            st.session_state.markers_data = markers_data

        else:
            # Display the message if no crime was committed and a search has been executed
            st.markdown(""" ## NO CRIME WAS COMMITTED """)
