import streamlit as st
import folium
from streamlit_folium import st_folium
import requests
import pandas as pd
import os

API_HOST = os.getenv("API_HOST")

# Add map
st.title("Forecasting Crimes")

# Add checkboxes
checkbox_values = {
    'Year': ['2023'],
    'Month': ['ALL'] + ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"],
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
    # Make API request to the backend to get historical data
    api_url = API_HOST + "/predict"

    year_month = f"{selected_values['Year']}-{selected_values['Month']}-01"
    category = selected_values['Category']

    year_month_search = year_month if 'ALL' not in year_month else None
    params = {
        'year_month': year_month_search,
        'category': category
    }

    print('Searching crimes...', params)
    response = requests.get(api_url, params=params)
    print(response.content)
    # Create a Pandas DataFrame from the data
    st.session_state.data = response.json()["data"]
    st.session_state.search_executed = True
else:
    st.write('No search yet')

if st.session_state.search_executed:
    data = st.session_state.data
    dataframe = pd.DataFrame(data)
    print(f'{dataframe=}')
    if data:
        st.write(dataframe)

    else:
        # Display the message if no crime was committed and a search has been executed
        st.markdown(""" ## NO CRIME WAS COMMITTED """)
