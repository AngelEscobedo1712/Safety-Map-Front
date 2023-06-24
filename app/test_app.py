import streamlit as st
import folium
from streamlit_folium import st_folium
import requests

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
response = requests.get("http://localhost:8000/neighborhoods")
neighborhood = response.json()["neighborhoods"]

# Add dropdowns
dropdown_values = {
    'Neighborhood': neighborhood,
    'Year': ['ALL', 2019, 2020, 2021, 2022, 2023],
    'Month': ['ALL'] + list(range(1, 13)),
    'Category': ['ALL', 'fraud', 'threats', 'threats', 'burglary', 'homicide',
                  'sexual crime', 'property damage', 'domestic violence', 'danger of well-being',
                  'robbery with violence', 'robbery without violence']
}

selected_values = {}
for dropdown_label, dropdown_options in dropdown_values.items():
    selected_values[dropdown_label] = st.selectbox(dropdown_label, dropdown_options)

# Make API request to the backend to get crime data
response = requests.get(
    "http://localhost:8000/crime-data",
    params={
        'neighborhood': selected_values['Neighborhood'],
        'year': selected_values['Year'],
        'month': selected_values['Month'],
        'category': selected_values['Category']
    }
)
data = response.json()

# Create a Folium map
if data:
    map_center = [data[0]['Latitude'], data[0]['Longitude']]
else:
    map_center = [19.4326, -99.1332]  # Default center if no data is available

map = folium.Map(location=map_center, zoom_start=11, tiles='Stamen Toner')

# Add markers to the map
if data:
    for row in data:
        folium.Marker([row['Latitude'], row['Longitude']]).add_to(map)
else:
    st.markdown(""" ## NO CRIME WAS COMMITTED """)

# Display the map
st_folium(map, width=700)
