import streamlit as st
import folium
from streamlit_folium import st_folium
import requests
import pandas as pd
import os

API_HOST = os.getenv("API_HOST")


# Safety Map Front
st.markdown("""
    # Mexico City - Safety Map

    ## Be not part of the statistics

    As much we are loving CDMX we are aware of the fact that it is not the safest place on earth. Therefore we want to provide you
    with a safety map for this amazing city. The intention of our idea is to give you a clear overview of the neighborhoods where you
    eat tacos and trink mezcal tranquilito and where better not to go.

    Our data data includes all registered crimes in Colonias of CDMX from **2019 to 2023**

    To be transparent from the beginning you can find the data for our project public available [here](https://datos.cdmx.gob.mx/dataset/victimas-en-carpetas-de-investigacion-fgj#:~:text=Descargar-,V%C3%ADctimas%20en%20Carpetas%20de%20Investigaci%C3%B3n%20(completa),-CSV)
""")

# Add map
st.title("Historical crime data")
map = folium.Map(location=[19.4326, -99.1332], zoom_start=11, tiles='Stamen Toner')

# Fetch neighborhoods from the backend
response = requests.get(API_HOST + "/neighborhoods")
neighborhood = response.json()["neighborhoods"]




# Add dropdowns
dropdown_values = {
    'Neighborhood': neighborhood,
    'Year': ['ALL', 2019, 2020, 2021, 2022, 2023],
    'Month': ['ALL'] + ["Enero","Febrero" ,"Marzo" ,"Abril" ,"Mayo" ,"Junio" ,"Julio" ,"Agosto" ,"Septiembre" ,"Octubre" ,"Noviembre" ,"Diciembre"],
    'Category': ['ALL', 'fraud', 'threats', 'threats', 'burglary', 'homicide',
                  'sexual crime', 'property damage', 'domestic violence', 'danger of well-being',
                  'robbery with violence', 'robbery without violence']
}


selected_values = {}
for dropdown_label, dropdown_options in dropdown_values.items():
    selected_values[dropdown_label] = st.selectbox(dropdown_label, dropdown_options)


# Initialize the search_executed flag
if 'search_executed' not in st.session_state:
    st.session_state.search_executed = False

markers_data = []

if st.button('Search'):
    # Make API request to the backend to get historical data
    api_url = API_HOST + "/get_historical_data"

    year = selected_values['Year'] if selected_values['Year'] != 'ALL' else None
    params = {
        'neighborhood': selected_values['Neighborhood'],
        'year': year,
        'month': selected_values['Month'],
        'category': selected_values['Category']
    }

    print('Searching crimes...')
    response = requests.get(api_url, params=params)
    # Create a Pandas DataFrame from the data
    st.session_state.data = response.json()["data"]
    st.session_state.search_executed = True
else:

    st.write('No search yet')
if st.session_state.search_executed:
    data = st.session_state.data
    dataframe = pd.DataFrame(data)
    if data:
        for row in data:
            marker = folium.Marker([row['Latitude'], row['Longitude']])
            markers_data.append(marker)
            marker.add_to(map)
        # Set the flag to indicate that a search has been executed
        st.session_state.search_executed = True
        st_folium(map, width=700)
    else:
    #Display the message if no crime was committed and a search has been executed
        st.markdown(""" ## NO CRIME WAS COMMITTED """)

# Store the markers in the session state to persist them
st.session_state.markers_data = markers_data
