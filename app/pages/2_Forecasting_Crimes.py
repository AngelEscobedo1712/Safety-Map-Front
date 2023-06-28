import streamlit as st
from streamlit_folium import st_folium
import requests
import pandas as pd
import os

### Heat Map libraries in folium
import folium
#from IPython.display import display
#import ipywidgets as widgets
from folium.plugins import HeatMap, HeatMapWithTime
#from datetime import datetime, timedelta


API_HOST = os.getenv("API_HOST")

# Add map
st.title("Forecasting Crimes")


# Add checkboxes
checkbox_values = {
    'Year': ['2023'],
    'Month': ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"],
    'Category': ['ALL', 'fraud', 'threats', 'threats', 'burglary', 'homicide',
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
    api_url = API_HOST + "/predict"

    year_month = f"{selected_values['Year']}-{selected_values['Month']}-01"
    category = selected_values['Category']

    year_month_search = year_month if 'ALL' not in year_month else None
    params = {
        'year_month': year_month_search,
        'category': category
    }

    response = requests.get(api_url, params=params)
    print(response.content)
    # Create a Pandas DataFrame from the data
    st.session_state.data = response.json()["data"]
    st.session_state.search_executed = True


########################

    # Make API request to the backend to get coordinates
    api_url_coords = API_HOST + "/coordinates"
    response_coords = requests.get(api_url_coords)
    print(response_coords.content)
    # Create a Pandas DataFrame from the data
    st.session_state.data_coords = response_coords.json()["data"]
    st.session_state.search_executed = True

########################

else:
    st.write('No search yet')

if st.session_state.search_executed:
    data = st.session_state.data
    data_coords = st.session_state.data_coords
    dataframe = pd.DataFrame(data)
    dataframe_coords = pd.DataFrame(data_coords)

    category = selected_values['Category']

    merged_neighborhood_location = pd.merge(dataframe, dataframe_coords, on="Neighborhood")
    columns_order_for_map = ['latitud','longitud',str(category)]
    merged_neighborhood_location_display = merged_neighborhood_location[columns_order_for_map]

    if data:

        #st.write(dataframe)
        #st.write(merged_neighborhood_location_display)

# Define the map variable to use it in display map
        heatmap = folium.Map(location=[19.4326, -99.1332], #Center of cdmx
                    tiles='stamentoner',
                    zoom_start=11)


# Display the lat and long of the predictions in a map
        bins=[0,20,40,60,80,100,120,140,160,180,200]
        HeatMap(merged_neighborhood_location_display,
                bins=bins,
                min_opacity=0.4,
                blur = 18
                    ).add_to(folium.FeatureGroup(name='Heat Map').add_to(heatmap))
        folium.LayerControl().add_to(heatmap)
        st_folium(heatmap, width=700)

    else:
        # Display the message if no crime was committed and a search has been executed
        st.markdown(""" ## NO CRIME WAS COMMITTED """)
