import streamlit as st
import folium
from streamlit_folium import folium_static
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
#map = folium.Map(location=[19.4326, -99.1332], zoom_start=11, tiles='Stamen Toner')

col1, col2, col3 = st.columns([1,3,1])

with col1:
    # Fetch neighborhoods from the backend
    if 'neighborhoods' not in st.session_state:
        response = requests.get(API_HOST + "/neighborhoods")
        neighborhoods = response.json()["neighborhoods"]
        st.session_state.neighborhoods = neighborhoods
    else:
        neighborhoods = st.session_state.neighborhoods

    category_colors = {
        'fraud': '#0068fa',
        'domestic violence': '#00eefa',
        'threats': '#00fa71',
        'robbery without violence': '#8afa00',
        'property damage': '#fae500',
        'danger of well-being': '#fa8500',
        'burglary': '#fa9e00',
        'robbery with violence': '#fa5300',
        'sexual crime': '#fa0000',
        'homicide': '#cc0808'
    }

    month_mapping = {
        "January": "Enero",
        "February": "Febrero",
        "March": "Marzo",
        "April": "Abril",
        "May": "Mayo",
        "June": "Junio",
        "July": "Julio",
        "August": "Agosto",
        "September": "Septiembre",
        "October": "Octubre",
        "November": "Noviembre",
        "December": "Diciembre"
    }

    month_mapping_swapped = {value: key for key, value in month_mapping.items()}

    # Add checkboxes
    checkbox_values = {
        'Neighborhood': neighborhoods,
        'Year': ['ALL', 2019, 2020, 2021, 2022, 2023],
        'Month': ['ALL'] + list(month_mapping.keys()),
        'Category': ['ALL', 'fraud', 'threats', 'burglary', 'homicide',
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

    # Check if values were selected
    if all(selected_values.values()):
        if st.button('Search 🔍'):
            # Make API request to the backend to get historical data
            api_url = API_HOST + "/get_historical_data"

            year = selected_values['Year'] if 'ALL' not in selected_values['Year'] else None
            params = {
                'neighborhoods': selected_values['Neighborhood'],
                'years': year,
                'months': [month_mapping.get(month, month) for month in selected_values['Month']],
                'categories': selected_values['Category']
            }

            with st.spinner('Retrieving crimes...'):
                response = requests.post(api_url, json=params)
                if response.status_code == 200:
                    st.session_state.data = response.json()["data"]
                    st.session_state.search_executed = True

        else:
            st.empty()


    else:
        st.write('Please select values in all dropdown menus to execute the search.')
        st.session_state.search_executed = False


with col2:

    if st.session_state.search_executed:
            data = st.session_state.data
            dataframe = pd.DataFrame(data)

            markers_data = []

            if data:
                dataframe['Month'] = dataframe['Month'].replace(month_mapping_swapped)

                south_west_corner = [min(dataframe.Latitude)*0.9999,min(dataframe.Longitude)*1.0001]
                north_east_corner = [max(dataframe.Latitude)*1.0001,max(dataframe.Longitude)*0.9999]
                map = folium.Map(location=[dataframe.Latitude.mean(), dataframe.Longitude.mean()], zoom_start=11, tiles='Stamen Toner')
                for row in data:
                    category = row['Category']
                    color = category_colors.get(category, '#000000')  # Default to black if category not in mapping
                    folium.CircleMarker(
                        location=[row['Latitude'], row['Longitude']],
                        icon=folium.Icon(color=color),  # Pass the color variable
                        radius=5,
                        color=color,
                        fill=True,
                        fill_opacity=0.6,
                        tooltip=row['Category']
                    ).add_to(map)
                map.fit_bounds([south_west_corner, north_east_corner])
                # Set the flag to indicate that a search has been executed
                st.success('Historical map complete')


                folium_static(map, width=750)
                st.session_state.markers_data = markers_data

                with col3:


                    with st.container():
                        legend_html = """
                        <style>
                            .legend-item {{
                                display: inline-block;
                                margin-right: 20px;
                            }}
                        </style>
                        <h3>Legend</h3>
                        <div class="legend-item">
                            {0}
                        </div>
                        """.format("".join([f'<div style="color:{color}"><span style="background-color:{color};">&nbsp;&nbsp;&nbsp;</span> {category.capitalize()}</div>' for category, color in category_colors.items()]))
                        st.markdown(legend_html, unsafe_allow_html=True)

            else:
                # Display the message if no crime was committed and a search has been executed
                st.markdown(""" ## NO CRIME WAS COMMITTED """)
