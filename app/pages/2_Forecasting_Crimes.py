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
#from datetime import datetime, timedelta


API_HOST = os.getenv("API_HOST")

api_url_download_polygons = API_HOST + "/download_polygons"
response_download_polygons = requests.get(api_url_download_polygons).json()
# Add map
st.title("Forecasting Crimes")


# Add checkboxes
checkbox_values = {
    'Year': ['2023'],
    'Month': ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"],
    'Category': ['fraud', 'threats', 'burglary', 'homicide',
                  'sexual crime', 'property damage', 'domestic violence', 'danger of well-being',
                  'robbery with violence', 'robbery without violence','score']
}

selected_values = {}
for checkbox_label, checkbox_options in checkbox_values.items():
    selected_values[checkbox_label] = st.selectbox(checkbox_label, checkbox_options)



# Initialize the search_executed flag
if 'search_executed' not in st.session_state:
    st.session_state.search_executed = False
    st.session_state.data = []

markers_data = []

if st.button('Search'):
    # Make API request to the backend to get Forecasting data
    api_url = API_HOST + "/get_crimes"

    year_month = f"{selected_values['Year']}-{selected_values['Month']}-01"
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
    st.write('No search yet')

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
            fill_color="YlGn",
            fill_opacity=0.7,
            line_opacity=0.2,
            legend_name="Unemployment Rate (%)",
        ).add_to(map)

        folium.LayerControl().add_to(map)

        folium_static(map, width=700)

    else:
        # Display the message if no crime was committed and a search has been executed
        st.markdown(""" ## NO CRIME WAS COMMITTED """)
