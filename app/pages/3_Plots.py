import streamlit as st
import folium
from streamlit_folium import st_folium, folium_static
import requests
import pandas as pd
import os
import altair as alt

API_HOST = os.getenv("API_HOST")
st.set_page_config(layout='wide')
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


#Title
st.title("Here you can play with some plots for the historical data")






# Fetch neighborhoods from the backend
if 'neighborhoods' not in st.session_state:
    response = requests.get(API_HOST + "/neighborhoods")
    neighborhoods = response.json()["neighborhoods"]
    st.session_state.neighborhoods = neighborhoods
else:
    neighborhoods = st.session_state.neighborhoods

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
    'Category': ['ALL', 'fraud', 'threats', 'threats', 'burglary', 'homicide',
                  'sexual crime', 'property damage', 'domestic violence', 'danger of well-being',
                  'robbery with violence', 'robbery without violence']
}

selected_values = {}
for checkbox_label, checkbox_options in checkbox_values.items():
    selected_values[checkbox_label] = st.multiselect(checkbox_label, checkbox_options)


# Initialize the plot_search flag
if 'plot_search' not in st.session_state:
    st.session_state.plot_search = False
    st.session_state.data = []



# Check if values were selected
if all(selected_values.values()):
    if st.button('Plot'):
        st.session_state.plot_search = True


        # Make API request to the backend to get_plot_historical_data
        api_url = API_HOST + "/get_plot_historical_data"

        year = selected_values['Year'] if 'ALL' not in selected_values['Year'] else None
        params = {
            'neighborhoods': selected_values['Neighborhood'],
            'years': year,
            'categories': selected_values['Category']
        }

        with st.spinner('Calculating plot...'):
            response = requests.post(api_url, json=params)
            if response.status_code == 200:
                st.session_state.data = response.json()["data"]
                st.session_state.search_executed = True

    else:
        st.write('No plot yet')
        st.empty()

else:
    st.write('Please select values in all dropdown menus to execute the plot.')
    st.session_state.plot_search = False


if st.session_state.plot_search:
        data = st.session_state.data
        dataframe = pd.DataFrame(data)
        dataframe['Month'] = dataframe['Month'].replace(month_mapping_swapped)
        dataframe['datetime'] = pd.to_datetime(dataframe['Year'].astype(int).astype(str) + ' ' + dataframe['Month'], format='%Y %B')

        # Create the Altair chart
        chart = alt.Chart(dataframe).mark_line().encode(
        x='datetime:T',
        y=alt.Y('TotalCrimes', axis=alt.Axis(tickMinStep=1, labelOverlap=True)),
                color='Category'
        ).properties(
            title='Development of Sum of Crimes Over the Years',
            width=2000,
            height=500
        )

        # Display the chart using Streamlit
        st.altair_chart(chart, use_container_width=True)
