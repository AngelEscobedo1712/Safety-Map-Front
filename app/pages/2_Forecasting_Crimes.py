import streamlit as st
import folium
from streamlit_folium import st_folium, folium_static
import requests
import pandas as pd
import os
import time

API_HOST = os.getenv("API_HOST")

# Add map
st.title("Forecasting Crimes from July 2023 to December 2023")

if "polygons_layer" not in st.session_state:
    api_url_download_polygons = API_HOST + "/download_polygons"
    response_download_polygons = requests.get(api_url_download_polygons).json()
    st.session_state.polygons_layer = response_download_polygons

# Add checkboxes
checkbox_values = {
    'Month': ["07", "08", "09", "10", "11", "12"],
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

if st.button('Search'):
    # Check if both Month and Category are selected
    st.session_state.search_executed = True
    # Make API request to the backend to get forecasting data
    api_url = API_HOST + "/get_crimes"
    year_month = f"2023-{selected_values['Month']}-01"
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
        folium_static(map, width=700)
    else:
        # Display the message if no crime was predicted and a search has been executed
        st.markdown(""" ## NO CRIME WAS PREDICTED """)
